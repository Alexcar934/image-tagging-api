from flask import Blueprint, jsonify, request
from controller import process_image, get_image_by_id

bp = Blueprint("api", __name__) 

@bp.route("/")
def index():
    """
    Endpoint raíz para comprobar que la API funciona.
    """
    return jsonify({"message": "API funcionando correctamente 🔥"})

@bp.route("/image", methods=["POST"])
def upload_image():
    """
    POST /image
    - Recibe JSON con 'data' (imagen en base64).
    - Parámetro opcional 'min_confidence' en query (?min_confidence=80).
    - Llama a process_image() en el controller, que hace:
        1) Subida a ImageKit
        2) Tags con Imagga
        3) Borrado remoto
        4) Guardado local
        5) Inserción en DB
        6) Retorno del JSON final
    """
    body = request.get_json()
    if not body or "data" not in body:
        return jsonify({"error": "Missing 'data' in body"}), 400

    # Valor por defecto 80 si no se pasa ?min_confidence= en la ruta 
    min_conf = request.args.get("min_confidence", default=80, type=int)

    try:
        # process_image es la función que hará toda la magia
        result = process_image(body["data"], min_conf)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@bp.route("/image/<image_id>", methods=["GET"])
def get_image(image_id):
    try:
        result = get_image_by_id(image_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 404


