import numpy as np
import boto3
import requests
import re
import json
import base64
from flask import Flask, request
from flask_cors import CORS
from PIL import Image, ImageOps
from io import BytesIO

import os
from dotenv import load_dotenv
load_dotenv()

# ENV consts
AWS=os.getenv("AWSKEY")
AWS_SECRET=os.getenv("AWSSECRET")
API_KEY=os.getenv("APIKEY")
APP_ID=os.getenv("APPID")
bucket_name = os.getenv("bucket")

s3 = boto3.client('s3', aws_access_key_id=AWS, aws_secret_access_key=AWS_SECRET)

app = Flask(__name__)

CORS(app, origins=["*"])

lol = []

def crop_image(img, x1, y1, x2, y2):
    print(x1,y1,x2,y2)
    croppedImg = img.crop((x1, y2, x2, y1))
    return croppedImg

def base64_img(base64_string):
    img_data = base64.b64decode(base64_string)
    img_bytes = BytesIO(img_data)
    img = Image.open(img_bytes)
    return img


@app.route("/add", methods=['POST'])
def add():
    try:
        s3.delete_object(Bucket=bucket_name, Key="dinosaur.jpeg")
    except:
        pass

    data = request.get_data()
    if not data:
        return {"success": False}

    data = json.loads(data.decode("utf-8"))
    print(len(data['body']))

    x1 = int(request.headers["left"])
    y1 = int(request.headers["top"])
    width = int(request.headers["width"])*2.45
    height = int(request.headers["height"])*2.5

    img = base64_img(data['body'])
    img.save("lol2.png", "png")
    pim = img
    im = np.array(pim)

    # NUMPY Colors
    red_channel = im[:, :, 0]
    green_channel = im[:, :, 1]
    blue_channel = im[:, :, 2]

    blue_majority_mask = (blue_channel > red_channel) & (blue_channel > green_channel)
    max_blue_majority = np.amax(blue_channel[blue_majority_mask])
    indices = np.argwhere((blue_channel == max_blue_majority) & blue_majority_mask)
    leftmost_index = indices[np.argsort(indices[:, 1])][0]

    print(leftmost_index)
    print(indices[0], indices[-1])

    print(indices[0][1] + width)
    print(img.width, img.height)
    x1 = min(indices[0][1], indices[0][1] + width)
    y1 = min(indices[0][0], indices[0][0]+height)
    x2 = max(indices[0][1], indices[0][1] + width)
    y2 = max(indices[0][0], indices[0][0]+height)

    img = crop_image(img, x1, y2, x2, y1)
    img = ImageOps.grayscale(img)
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img.save("lol3.png", "png")

    s3.put_object(Bucket="yousefwantstodie", Key="dinosaur.jpeg", Body=buffered.getvalue(), ContentType='image/jpeg', ACL='public-read')
    public_url = f"https://{bucket_name}.s3.amazonaws.com/dinosaur.jpeg"
    print(f"Public URL: {public_url}")

    response = requests.post("https://api.mathpix.com/v3/text", 
        json={
            "src": public_url,
            "formats": ["latex_styled"],
            "data_options": {
            "include_asciimath": True
            }
        },
        headers={
        "app_id": APP_ID,
        "app_key": API_KEY,
        "Content-type": "application/json"
        }
    )

    data = response.json()

    print(img.width, img.height)

    print(data)

    if not "latex_styled" in data:
        return {"success": False}

    s: str = data["latex_styled"]
    
    lol.append(re.sub(r'\\\\', r'\\', s))
    
    return {"success": True}


@app.route("/get", methods=['GET'])
def get():
    if not len(lol):
        return {"success": False}
    l = lol.pop()
    return {"success": True, "string": l}


if __name__ == "__main__":
    app.run(debug=True, port=5000)