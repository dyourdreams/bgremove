import os
from flask import Flask, request, render_template,Response,make_response
from PIL import Image
from conversions import remove_bg
import io
import time
import base64


from pymongo import MongoClient

# client = MongoClient("mongodb://localhost:27017")
client = MongoClient("mongodb+srv://prabin:bprabin@cluster0.2phmxej.mongodb.net/test")

db = client["imageLab"]
image_collection = db['Images']

app = Flask(__name__, template_folder='templates', static_folder='static',)


@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route('/bgremove', methods=['POST']) 
def background_remove():
    return remove_bg()

@app.route('/download/<user_id>')
def download(user_id):
    image_collection_data=image_collection.find_one({'user_id': user_id})
    if image_collection_data:
        binary_image_data = image_collection_data['image_data']
    else:
        return render_template("error.html",  error_msg='No file found on Database')
    image = Image.open(io.BytesIO(binary_image_data))
    image_format = image.format
    response = make_response(binary_image_data)
    response.headers.set('Content-Type', 'image/'+ image_format)
    response.headers.set('Content-Disposition', 'attachment', filename=f'img{int(time.time())}.{image_format}')
    return response

if  __name__ == "__main__":
    app.run()