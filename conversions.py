import io
import threading
from flask import request, render_template
from PIL import Image
from rembg import remove
from pymongo import MongoClient
import base64
import threading
from time import sleep
from utils4 import generate_unique_id

# Connect to MongoDB
client = MongoClient("mongodb+srv://prabin:bprabin@cluster0.2phmxej.mongodb.net/test")
# client = MongoClient("mongodb://localhost:27017")
db = client["imageLab"]
image_collection = db['Images']

def delete_image_collection(user_id):
    sleep(140) # wait for 2 minutes
    image_collection.delete_one({'user_id': user_id})

def image_processing(image, user_id, image_type,img_format,quality):
    img_io = io.BytesIO()
    image.save(img_io, format=img_format, quality=quality)
    img_io.seek(0)
    image_data = img_io.read()
    image_collection.insert_one({'user_id': user_id, 'image_data': image_data, 'type': image_type})
    threading.Thread(target=delete_image_collection, args=(user_id,)).start()
    image_data = image_collection.find_one({'user_id': user_id})['image_data']
    image = Image.open(io.BytesIO(image_data))
    img_io = io.BytesIO()
    image.save(img_io, format= img_format,quality=quality)
    img_io.seek(0)
    img_str = base64.b64encode(img_io.getvalue()).decode()
    return img_str

def handle_error(error_msg):
    return render_template("error.html", error_msg='Upload a valid image file.')

def view_result_Page(message,user_id,image_data,format):
    return render_template('result.html',message=message,user_id=user_id ,image_data=image_data,format=format)

def remove_bg():
    file = request.files.get('bfile')
    try:
        if file is None or file.filename == '':
            return 'No file was submitted or the file is empty'
        image = Image.open(file)
        user_id = generate_unique_id()
        image = remove(image)
        img_str = image_processing(image, user_id, 'bg_remove','PNG',100)
        return view_result_Page("Background removed Successfully",user_id ,img_str,'PNG')
    except OSError:
        return render_template("error.html",error_msg='Upload a valid image file.')