from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)

CORS(app, origins=["*"])

lol = []

@app.route("/add", methods=['POST'])
def add():
    print(request.headers)
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
    app.run(debug=True, port=5001)