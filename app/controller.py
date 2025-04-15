import base64
import uuid
import os
import json
import requests
from datetime import datetime
from models import get_db
from imagekitio import ImageKit

# Leemos las credenciales desde un fichero JSON (que NO se sube a GitHub)
with open("credentials.json", "r") as f:
    creds = json.load(f)

# Configuración de ImageKit
imagekit = ImageKit(
    public_key=creds["imagekit"]["public_key"],
    private_key=creds["imagekit"]["private_key"],
    url_endpoint=creds["imagekit"]["url_endpoint"]
)

# Configuración de Imagga (autenticación básica)
imagga_auth = (
    creds["imagga"]["api_key"],
    creds["imagga"]["api_secret"]
)

# Carpeta donde guardaremos localmente las imágenes
IMAGES_DIR = "images"

def process_image(base64_str, min_conf=80):
    """
    Recibe una imagen en base64 (string), la procesa y devuelve info.
    """

    # Convertimos el string base64 recibido a bytes
    base64_data = base64_str.encode("utf-8")

    # Generamos un UUID para la imagen
    image_id = str(uuid.uuid4())
    filename = f"{image_id}.jpg"

    # 1. Subir a ImageKit
    upload_info = imagekit.upload(
        file=base64_data,
        file_name=filename
    )

    public_url = upload_info.url
    file_id_ik = upload_info.file_id

    # 2. Obtener tags de Imagga
    response = requests.get(
        f"https://api.imagga.com/v2/tags?image_url={public_url}",
        auth=imagga_auth
    )
    response_json = response.json()

    if "result" not in response_json or "tags" not in response_json["result"]:
        raise Exception("No se han recibido tags desde Imagga.")

    raw_tags = response_json["result"]["tags"]
    filtered_tags = [
        {
            "tag": t["tag"]["en"],
            "confidence": t["confidence"]
        }
        for t in raw_tags
        if t["confidence"] >= min_conf
    ]

    # 3. Borrar la imagen de ImageKit
    imagekit.delete_file(file_id=file_id_ik)

    # 4. Guardar localmente
    os.makedirs(IMAGES_DIR, exist_ok=True)
    local_path = os.path.join(IMAGES_DIR, filename)
    with open(local_path, "wb") as f:
        f.write(base64.b64decode(base64_data))

    # 5. Guardar en base de datos
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO pictures (id, path, date) VALUES (%s, %s, %s)",
        (image_id, local_path, now)
    )
    for tag_obj in filtered_tags:
        cursor.execute(
            "INSERT INTO tags (tag, picture_id, confidence, date) VALUES (%s, %s, %s, %s)",
            (tag_obj["tag"], image_id, tag_obj["confidence"], now)
        )
    db.commit()

    # 6. Respuesta
    size_kb = round(os.path.getsize(local_path) / 1024, 2)

    return {
        "tags": filtered_tags,
        "size": size_kb,
        "date": now,
        "data": base64_str,
        "id": image_id,  # usamos el string original, no los bytes
    }

def get_image_by_id(image_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Buscar imagen en la tabla pictures
    cursor.execute("SELECT * FROM pictures WHERE id = %s", (image_id,))
    pic = cursor.fetchone()
    if not pic:
        raise Exception("Imagen no encontrada")

    # Buscar tags asociadas
    cursor.execute("SELECT tag, confidence FROM tags WHERE picture_id = %s", (image_id,))
    tags = cursor.fetchall()

    # Leer imagen local
    with open(pic["path"], "rb") as f:
        img_data = f.read()
    base64_img = base64.b64encode(img_data).decode("utf-8")

    size_kb = round(os.path.getsize(pic["path"]) / 1024, 2)

    return {
        "tags": tags,
        "size": size_kb,
        "date": pic["date"].strftime('%Y-%m-%d %H:%M:%S')
    }

