import random
import time

from bson import ObjectId
from flask import Flask, jsonify, request
from keras.models import load_model
import numpy as np
from PIL import Image, ImageOps
import tensorflow as tf
from flask import Flask
from flask_cors import CORS

import db.user as user

app = Flask(__name__)
print(app)
CORS(app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# @app.route("/classify_cancer", methods=['POST'])
# def classify_cancer():
#     try:
#         image_file = request.files['image']
#         # get the image from request and preprocess the image
#         image = Image.open(image_file)
#         image = image.resize((64, 64))  # Resize the image to 64 x 64 pixels
#         image = np.array(image)  # Convert image to NumPy array
#         image = image / 255.0  # Normalize the pixel values to 0-1
#         image = np.expand_dims(image, axis=0)
#
#         # load the model
#         print("Up")
#         # model = tf.keras.models.load_model("models/keras/model")
#         model = tf.keras.models.load_model("models/h5/model.h5")
#         print("Down")
#         # model = tf.saved_model.load('models/h5/model.h5')
#
#         # run model on the image and return results as the response
#         c = 0
#         results = {}
#         for i in model.predict(image)[0]:
#             label = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc'][c]
#             print(label, np.around(i * 100, decimals=2), "%")
#             c = c + 1
#             results[label] = (np.around(i * 100, decimals=2))
#         return jsonify(results)
#     except:
#         return jsonify("Error!"), 500


@app.route("/classify_cancer", methods=['POST'])
def classify_cancer():
    try:
        # image_file = request.files['image']
        # # get the image from request and preprocess the image
        # image = Image.open(image_file)
        # image = image.resize((64, 64))  # Resize the image to 64 x 64 pixels
        # image = np.array(image)  # Convert image to NumPy array
        # image = image / 255.0  # Normalize the pixel values to 0-1
        # image = np.expand_dims(image, axis=0)

        # Load the binary classification model first
        print("Image coming to the model")
        binary_model = load_model("models/h5/keras_model.h5", compile=False)
        print("Image left the model")

        # Load the labels
        class_names = open("models/h5/labels.txt", "r").readlines()
        print(class_names)

        # Process the image
        image_file = request.files['image']
        image = Image.open(image_file).convert("RGB")

        # Resize the image to 224x224
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        image_array = np.asarray(image)
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = normalized_image_array

        # Run binary classification on the image
        binary_result = binary_model.predict(data)
        print(binary_result)
        binary_confidence = binary_result[0][0]

        # Check if the image is "SkinRelatedImages" or "RandomImages"
        if binary_confidence > 0.75:  # SkinRelatedImages
            # Load the skin cancer classification model
            print("Inside the condition")
            skin_cancer_model = tf.keras.models.load_model("models/h5/model.h5")
            print("Model loaded")

            image_file = request.files['image']
            # get the image from request and preprocess the image
            image = Image.open(image_file)
            image = image.resize((64, 64))  # Resize the image to 64 x 64 pixels
            image = np.array(image)  # Convert image to NumPy array
            image = image / 255.0  # Normalize the pixel values to 0-1
            image = np.expand_dims(image, axis=0)

            # Run the skin cancer classification model on the image and return results
            c = 0
            results = {}
            print("results loaded")
            print(skin_cancer_model.predict(image))
            for i in skin_cancer_model.predict(image)[0]:
                label = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc'][c]
                print(label, np.around(i * 100, decimals=2), "%")
                c = c + 1
                results[label] = (np.around(i * 100, decimals=2))
            return jsonify(results)
        else:  # RandomImages
            print("Random Image")
            return jsonify("The image is not skin related")

    except Exception as e:
        print("Error", str(e))
        return jsonify("Error!"), 500


@app.route("/check_severity", methods=['POST'])
def check_severity():
    try:
        image_file = request.files['image']
        # get the image from request and preprocess the image
        image = Image.open(image_file)
        image = image.resize((128, 128))  # Resize the image to 64 x 64 pixels
        image = np.array(image)  # Convert image to NumPy array
        image = image / 255.0  # Normalize the pixel values to 0-1
        image = np.expand_dims(image, axis=0)

        # load the model
        model = tf.keras.models.load_model("models/severity/new/model")

        # run model on the image and return results as the response
        c = 0
        results = {}
        print(model.predict(image))
        for i in model.predict(image)[0]:
            label = ["low", "medium", "high"][c]
            print(label, np.around(i * 100, decimals=2), "%")
            c = c + 1
            results[label] = (np.around(i * 100, decimals=2))
        return jsonify(results)
    except:
        return jsonify("Error!"), 500


@app.route("/login_user", methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        res = user.login_user(data['email'], data['password'])
        usr = {
            '_id': str(res['_id']),
            'name': res['name'],
            'mobile_number': res['mobile_number'],
            'email': res['email'],
            'success': True,
        }
        return usr
    except Exception as e:
        print(str(e))
        return jsonify(str(e)), 500


@app.route("/register_user", methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        res = user.register_user(data['email'], data['name'], data['mobile_number'], data['password'])
        return {
            '_id': str(res['_id']),
            'name': res['name'],
            'mobile_number': res['mobile_number'],
            'email': res['email'],
            'success': True,
        }
    except Exception as e:
        return jsonify(str(e)),500