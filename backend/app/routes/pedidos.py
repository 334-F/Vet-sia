"""
Rutas de pedidos.

Este es el endpoint central del e-commerce. Cuando un cliente hace
checkout, este endpoint:
  1. Valida que todos los productos existen y tienen stock
  2. Calcula precios con CalculadoraPrecios (escalado + promociones + tipo cliente)
  3. Crea el pedido y sus líneas en una transacción
  4. Resta el stock
  5. Si el método de pago es tarjeta, crea el PaymentIntent en Stripe
  6. Genera la factura PDF
  7. Envía email de confirmación al cliente

GET /api/pedidos             - historial del usuario autenticado
GET /api/pedidos/:id         - detalle de un pedido propio
POST /api/pedidos            - crear pedido (checkout)
PATCH /api/pedidos/:id/cancelar - cancelar pedido propio (si estado lo permite)
GET /api/pedidos/:id/factura - descargar PDF de factura
"""
import os
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
from ..models import (
    Pedido, LineaPedido, Producto, DireccionEnvio,
    MetodoPago, ZonaEnvio, TipoServicio, Usuario,
)
from ..services.precios import CalculadoraPrecios, calcular_totales_pedido
from ..services.facturas import generar_factura_pdf
from ..services.emails import enviar_email_confirmacion_pedido, enviar_email_cambio_estado
from ..services.pagos import crear_payment_intent
from ..utils.decorators import admin_required

pedidos_bp = Blueprint("pedidos", __name__)


@pedidos_bp.route("", methods=["GET"])
@jwt_required()
def listar_pedidos_usuario():
    """Historial de pedidos del usuario autenticado."""
    usuario_id = int(get_jwt_identity())
    pedidos = (Pedido.query.filter_by(usuario_id=usuario_id)
                           .order_by(Pedido.fecha.desc()).all())
    return jsonify([p.to_dict(incluir_lineas=False) for p in pedidos])


@pedidos_bp.route("/<int:pedido_id>", methods=["GET"])
@jwt_required()
def get_pedido(pedido_id):
    """Detalle de un pedido (solo si es propio o el usuario es admin)."""
    usuario_id = int(get_jwt_identity())
    claims = get_jwt()
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404
    if pedido.usuario_id != usuario_id and claims.get("rol") != "admin":
        return jsonify({"error": "No tienes acceso a este pedido"}), 403
    return jsonify(pedido.to_dict(incluir_lineas=True))


@pedidos_bp.route("", methods=["POST"])
@jwt_required()
def crear_pedido():
    """
    Crear un pedido nuevo (endpoint del checkout).

    Espera un JSON con:
    {
      "direccion_envio_id": 1,
      "metodo_pago_id": 1,
      "zona_envio_id": 1,
      "notas": "...",
      "lineas": [
        { "producto_id": 1, "cantidad": 2, "tipo_servicio_id": null,
          "personalizacion": null, "archivo_diseno_url": null }
      ]
    }
    """
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get(usuario_id)
    datos = request.get_json() or {}

    # --- 1. Validar entrada básica ---
    requeridos = ["direccion_envio_id", "metodo_pago_id", "zona_envio_id", "lineas"]
    faltantes = [c for c in requeridos if datos.get(c) is None]
    if faltantes:
        return jsonify({"error": "Faltan campos", "campos": faltantes}), 400

    lineas_datos = datos["lineas"]
    if not isinstance(lineas_datos, list) or len(lineas_datos) == 0:
        return jsonify({"error": "El pedido debe tener al menos una línea"}), 400

    # --- 2. Validar dirección, método de pago y zona ---
    direccion = DireccionEnvio.query.filter_by(
        id=datos["direccion_envio_id"], usuario_id=usuario_id
    ).first()
    if not direccion:
        return jsonify({"error": "Dirección de envío no válida"}), 400

    metodo_pago = MetodoPago.query.filter_by(id=datos["metodo_pago_id"], activo=True).first()
    if not metodo_pago:
        return jsonify({"error": "Método de pago no disponible"}), 400

    zona = ZonaEnvio.query.filter_by(id=datos["zona_envio_id"], activa=True).first()
    if not zona:
        return jsonify({"error": "Zona de envío no válida"}), 400

    # --- 3. Crear pedido (transacción completa) ---
    try:
        pedido = Pedido(
            usuario_id=usuario_id,
            direccion_envio_id=direccion.id,
            metodo_pago_id=metodo_pago.id,
            zona_envio_id=zona.id,
            estado="pendiente_pago",
            coste_envio=zona.coste_envio,
            notas=datos.get("notas"),
        )
        db.session.add(pedido)
        db.session.flush()  # asignamos id sin commit

        # Crear cada línea aplicando precios
        for linea_datos in lineas_datos:
            producto = Producto.query.get(linea_datos.get("producto_id"))
            if not producto or not producto.activo:
                db.session.rollback()
                return jsonify({"error": f"Producto {linea_datos.get('producto_id')} no disponible"}), 400

            cantidad = int(linea_datos.get("cantidad", 1))
            if cantidad <= 0:
                db.session.rollback()
                return jsonify({"error": "Cantidad inválida"}), 400

            if not producto.verificar_stock(cantidad):
                db.session.rollback()
                return jsonify({
                    "error": f"Stock insuficiente para {producto.nombre}",
                    "stock_disponible": producto.stock
                }), 400

            tipo_servicio = None
            if linea_datos.get("tipo_servicio_id"):
                tipo_servicio = TipoServicio.query.get(linea_datos["tipo_servicio_id"])

            # Calcular precio con la calculadora
            calc = CalculadoraPrecios(producto, cantidad, tipo_servicio, usuario)
            subtotal = calc.calcular()
            precio_unitario = calc.detalle["precio_unitario_final"]

            linea = LineaPedido(
                pedido_id=pedido.id,
                producto_id=producto.id,
                tipo_servicio_id=tipo_servicio.id if tipo_servicio else None,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                personalizacion=linea_datos.get("personalizacion"),
                archivo_diseno_url=linea_datos.get("archivo_diseno_url"),
                subtotal=subtotal,
            )
            db.session.add(linea)

            # Restar stock
            producto.actualizar_stock(-cantidad)

        db.session.flush()  # refrescar relaciones
        db.session.refresh(pedido)

        # Recalcular totales del pedido
        pedido.calcular_total()

        db.session.commit()
    except (SQLAlchemyError, ValueError) as e:
        db.session.rollback()
        current_app.logger.error(f"Error al crear pedido: {e}")
        return jsonify({"error": "Error al crear el pedido", "detalle": str(e)}), 500

    # --- 4. Si el método requiere pasarela, crear PaymentIntent en Stripe ---
    respuesta = {"pedido": pedido.to_dict(incluir_lineas=True)}
    if metodo_pago.requiere_pasarela:
        try:
            datos_pago = crear_payment_intent(pedido)
            respuesta["pago"] = datos_pago
        except Exception as e:
            current_app.logger.error(f"Error con Stripe: {e}")
            respuesta["pago_error"] = "No se pudo iniciar el pago. Inténtalo de nuevo."
    else:
        # Para transferencia/contrareembolso, el pedido queda pendiente hasta confirmación manual
        respuesta["mensaje_pago"] = (
            "Pedido registrado. Se confirmará cuando recibamos tu pago."
        )

    # --- 5. La factura se genera bajo demanda cuando el usuario la descarga,
    # para no consumir memoria del worker en plan Free de Render.
    # El endpoint /api/pedidos/<id>/factura se encarga de generarla si no existe.

    return jsonify(respuesta), 201


@pedidos_bp.route("/<int:pedido_id>/cancelar", methods=["PATCH"])
@jwt_required()
def cancelar_pedido(pedido_id):
    """Cancelar un pedido propio (solo si el estado lo permite)."""
    usuario_id = int(get_jwt_identity())
    pedido = Pedido.query.filter_by(id=pedido_id, usuario_id=usuario_id).first()
    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404
    if not pedido.puede_cancelarse():
        return jsonify({"error": f"No se puede cancelar un pedido en estado {pedido.estado}"}), 400

    pedido.cambiar_estado("cancelado")

    # Devolver el stock de cada producto
    for linea in pedido.lineas:
        if linea.producto:
            linea.producto.actualizar_stock(linea.cantidad)

    db.session.commit()
    enviar_email_cambio_estado(pedido)
    return jsonify({"mensaje": "Pedido cancelado", "pedido": pedido.to_dict()})


@pedidos_bp.route("/<int:pedido_id>/factura", methods=["GET"])
@jwt_required()
def descargar_factura(pedido_id):
    """Descarga el PDF de la factura. Solo el dueño o un admin."""
    usuario_id = int(get_jwt_identity())
    claims = get_jwt()
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404
    if pedido.usuario_id != usuario_id and claims.get("rol") != "admin":
        return jsonify({"error": "No tienes acceso a este pedido"}), 403
    if not pedido.factura_url or not os.path.exists(pedido.factura_url):
        # Regenerar si no existe
        try:
            ruta = os.path.join(
                current_app.config["INVOICE_FOLDER"], f"factura_{pedido.id:06d}.pdf"
            )
            generar_factura_pdf(pedido, ruta)
            pedido.factura_url = ruta
            db.session.commit()
        except Exception as e:
            return jsonify({"error": f"No se pudo generar la factura: {e}"}), 500

    return send_file(pedido.factura_url, as_attachment=True,
                     download_name=f"factura_VE-{pedido.id:06d}.pdf",
                     mimetype="application/pdf")


# --- Endpoints auxiliares para el checkout ---

@pedidos_bp.route("/metodos-pago", methods=["GET"])
def listar_metodos_pago():
    metodos = MetodoPago.query.filter_by(activo=True).all()
    return jsonify([m.to_dict() for m in metodos])


@pedidos_bp.route("/zonas-envio", methods=["GET"])
def listar_zonas_envio():
    zonas = ZonaEnvio.query.filter_by(activa=True).all()
    return jsonify([z.to_dict() for z in zonas])


@pedidos_bp.route("/tipos-servicio", methods=["GET"])
def listar_tipos_servicio():
    """Tipos de servicio de personalización para uniformidad."""
    tipos = TipoServicio.query.filter_by(activo=True).all()
    return jsonify([t.to_dict() for t in tipos])
