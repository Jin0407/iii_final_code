import flask
from flask import Flask
from flask import send_file
from flask_cors import CORS
import io
import os
import imageio
import numpy as np
import json
import base64
from PIL import Image

from PIL import Image

import style_pic

from google_images_download import google_images_download


app = Flask(__name__)
CORS(app)



# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

string_style = './style/bango.jpg'


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

#json_dump = json.dumps({'image': generated}, cls=NumpyEncoder)


@app.route('/')
def hello():
    """Renders a sample page."""
    return "Hello World!"


@app.route('/style_transfer',methods=['POST'])
def style():
    image = flask.request.files["image"].read()
    #image = Image.open(io.BytesIO(image))
    print(imageio.imread(image))
    content_image = imageio.imread(image)
    style_image = imageio.imread(string_style)
    generated = style_pic.style_transfer(content_image,style_image)
    print(generated)
    imageio.imwrite("generated_image.jpg",generated)

    #return send_file("generated_image.jpg", mimetype='image/jpg')
    #img=send_file("generated_image.jpg", mimetype='image/jpg', as_attachment=True)
    with open("generated_image.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string
    
    #im = Image.open("generated_image.jpg")
    #return im

@app.route('/style_transfer_line',methods=['POST'])
def style_line():
    image = flask.request.files["image"].read()
    #image = Image.open(io.BytesIO(image))
    print(imageio.imread(image))
    content_image = imageio.imread(image)
    style_image = imageio.imread(string_style)
    generated = style_pic.style_transfer(content_image,style_image)
    print(generated)

    return json.dumps({'image': generated}, cls=NumpyEncoder)
       
@app.route('/google_image',methods=['POST'])
def image_search():
    word = flask.request.form.get("word")
    print(word)
    response = google_images_download.googleimagesdownload()  
    
    arguments = {"keywords":word,"limit":10,"print_urls":True} #keywords 打要搜尋的關鍵字   # limit 就是設定最多抓幾張  print_urls 只是要不要記錄圖檔路徑而已

    paths = response.download(arguments) 
    return paths

if __name__ == '__main__':
    app.run(port=5555)


        