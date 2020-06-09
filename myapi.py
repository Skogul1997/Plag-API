import moss
import os
import hashlib
import shutil
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename
import base64
from flask_swagger_ui import get_swaggerui_blueprint
from functools import wraps
from flask_pymongo import PyMongo
from flask_httpauth import HTTPBasicAuth
import threading
import sys

auth = HTTPBasicAuth()
app = Flask(__name__)
api = Api(app)

app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
mongo = PyMongo(app)

SWAGGER_URL = ''
API_URL = '/static/swagger.yaml'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL
)

app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


@auth.verify_password
def verify_password(username, password):
    try:
        users = mongo.db.users
        user = users.find_one({'username': username})
        password = (hashlib.md5(password.encode())).hexdigest()
        if user['password'] == password:
            return username
    except:
        return None


class getResult(Resource):

    @auth.login_required
    def get(self):

        return {'status': "Success", 'info': 'This is a plagiarism checking API. Submit to the same endpoint with fields lang and files. Lang specifies the source code language and files specifies the files. The result would have a detailed report and a list of the results.'}, 200

    @auth.login_required
    def post(self):

        data = request.get_json()

        if 'lang' in data.keys():

            with open('config.txt', 'r') as f:
                counter = int(f.read())
            with open('config.txt', 'w') as f:
                f.write(str(counter+1))

            while True:
                try:
                    os.mkdir(str(counter))
                except:
                    with open('config.txt', 'r') as f:
                        counter = int(f.read())
                    with open('config.txt', 'w') as f:
                        f.write(str(counter+1))
                else:
                    break

            lang = data['lang']

            try:
                app.config['UPLOAD_FOLDER'] = str(counter) + '/'

                for key in data['files'].keys():
                    base64_bytes = data['files'][key].encode('ascii')
                    message_bytes = base64.b64decode(base64_bytes)
                    message = message_bytes.decode('ascii')
                    with open(os.path.join(app.config['UPLOAD_FOLDER'], (str(key)+'.txt')), "w", newline="") as f:
                        f.write(message)

                path = str(counter)
                return_json = moss.getURL(path, lang)

                if request.get_json():
                    return return_json
            except:
                return {"status": "Fail"}, 500
            finally:
                os.chdir('..')
                shutil.rmtree(path)

        else:

            return {'status': 'Fail', 'error': 'language not specified'}, 422


api.add_resource(getResult, '/result')

if __name__ == '__main__':
    app.run(debug=True)
