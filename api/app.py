import base64
from flask import Flask, request
from flask_cors import CORS
from PIL import Image
from io import BytesIO

app = Flask(__name__)

CORS(app, origins=["*"])

lol = []

def crop_image(imgPath, x1, y1, x2, y2):
    img = Image.open(imgPath)
    croppedImg = img.crop((x1, y1, x2, y2))
    return croppedImg


def base64_img(base64_string):
    img_data = base64.b64decode(base64_string)
    img_bytes = BytesIO(img_data)
    img = Image.open(img_bytes)
    return img


@app.route("/add", methods=['POST'])
def add():
    latex = request.headers.get("string", None)
    if not latex:
        return {"success": False}
    
    lol.append(latex)
    return {"success": True}


@app.route("/get", methods=['GET'])
def get():
    if not len(lol):
        return {"success": False}
    l = lol.pop()
    return {"success": True, "string": l}


if __name__ == "__main__":
    app.run(debug=True, port=5000)