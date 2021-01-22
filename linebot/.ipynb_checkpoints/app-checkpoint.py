from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage , ImageSendMessage

import logging
import requests
import configparser

import random

import json
import base64
import tempfile
import pyimgur
import imageio
import numpy as np
app = Flask(__name__)


# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

def glucose_graph():
    CLIENT_ID = "5f8eec870063bd9"
    PATH = "final_generated_image.jpg"
    im = pyimgur.Imgur(CLIENT_ID)
    uploaded_image = im.upload_image(PATH, title="Uploaded with PyImgur")
    return uploaded_image.link


# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        print(body, signature)
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 學你說話
# @handler.add(MessageEvent, message=TextMessage)
# def pretty_echo(event):
    
#     # if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        
#     #     # Phoebe 愛唱歌
#     #     pretty_note = '♫♪♬'
#     #     pretty_text = ''
        
#     #     for i in event.message.text:
        
#     #         pretty_text += i
#     #         pretty_text += random.choice(pretty_note)
    
#     #     line_bot_api.reply_message(
#     #         event.reply_token,
#     #         TextSendMessage(text=pretty_text)
#     #     )

#     if event.message.text == '/風格轉移':
#         line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text='請上傳圖片、選擇風格')
#         )
    
@handler.add(MessageEvent, message=ImageMessage)
def get_image(event):
    message_content = line_bot_api.get_message_content(event.message.id)

    tempfile_path = os.path.join("/tmp", "tempfile")
    with open(tempfile_path, 'wb') as fd:
        for chunk in message_content.iter_content():
                fd.write(chunk)
    
    print(imageio.imread(tempfile_path))

    files = {'image': open(tempfile_path ,'rb')}
    server_endpoint = 'http://127.0.0.1:5555/style_transfer_line'
    r = requests.post(server_endpoint, files=files).json()
    # print(r)
    image_restored = np.asarray(r["image"])
    # json_load = json.loads(r)
    # image_restored = np.asarray(json_load["image"])
    imageio.imwrite('final_generated_image.jpg', image_restored)

    img_url = glucose_graph()
    print(img_url)
    line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(original_content_url = img_url + '.jpg',
    preview_image_url = img_url + '.jpg'))

if __name__ == "__main__":
    app.run()