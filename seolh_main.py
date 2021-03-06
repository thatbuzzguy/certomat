from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from flask import Flask, request, jsonify, Response, render_template, redirect, url_for
import json
import os.path
import datetime
import sys

import seolh_config
import seolh_crypto
import seolh_requests


class config():

    def __init__(self):
        self.app_version = 'b3'
        self.data = {}
        self.data['service_config'] = {}
        self.data['client_cert_config'] = {}
        self.data['root_cert_config'] = {}


class certificate_request():

    def __init__(self):
        self.serial_number = int
        self.self_signed = bool
        self.csr = str


def set_backend(config_data):
    backend = config_data['service_config']['backend']
    if backend == 'default_backend':
        backend_obj = default_backend()
    else:
        backend_obj = default_backend()
    return backend_obj

if not os.path.exists("certificates"):
    os.makedirs("certificates")

if not os.path.exists("ca"):
    os.makedirs("ca")


def file_exists(file_name):
    exists = os.path.isfile(file_name)
    return exists

config_obj = config()
config_obj = seolh_config.load(config_obj)
backend_obj = set_backend(config_obj.data)

if file_exists(config_obj.data['service_config']['private_key_file']):
    with open(config_obj.data['service_config']['private_key_file'], "rb") as key_file:
        private_key_obj = serialization.load_pem_private_key(
            key_file.read(), password=None, backend=backend_obj)
else:
    seolh_requests.initalize(config_obj, backend_obj)

with open("ca/seolh.log", "a") as log:
    log.write('seolh ' + config_obj.app_version + ' startup ' +
              datetime.datetime.now().__str__() + '\n')

app = Flask(__name__)


@app.route('/')
def root():
    return redirect(url_for('help'))


@app.route('/help')
def help():
    resp = Response(response='<html><a href=\"/version\">version</a><p>' +
                    '<a href=\"/initalize\">initalize</a><p>' +
                    '<a href=\"/generate-random-csr\">generate-random-csr</a><p>' +
                    '<a href=\"/get-csr\">get-csr</a><p>' +
                    '<a href=\"/config-save\">config-save</a><p>' +
                    '<a href=\"/config-load\">config-load</a><p>' +
                    '<a href=\"/config-default\">config-default</a>', status=200)
    return(resp)


@app.route('/version')
def version():
    version = config_obj.app_version
    return version


@app.route('/initalize')
def initalize():
    seolh_requests.initalize(config_obj, backend_obj)
    resp = Response(response='ok', status=200, mimetype="application/json")
    return(resp)


@app.route('/config-save')
def config_save():
    seolh_config.save(config_obj)
    resp = Response(response='ok', status=200, mimetype="application/json")
    return(resp)


@app.route('/config-load')
def config_load():
    seolh_config.load(config_obj)
    resp = Response(response='ok', status=200, mimetype="application/json")
    return(resp)


@app.route('/config-default')
def config_default():
    seolh_config.default(config_obj)
    resp = Response(response='ok', status=200, mimetype="application/json")
    return(resp)


@app.route('/generate-random-csr')
def generate_random_csr():
    csr_text = seolh_requests.generate_random_csr(config_obj, backend_obj)
    resp = Response(response=csr_text, status=200, mimetype="application/json")
    return(resp)


@app.route('/get-csr')
def get_csr():
    return render_template("csr_input.html")


@app.route('/process-csr', methods=['GET', 'POST'])
def process_csr():
    csr_text = request.form['csr']
    resp = seolh_requests.process_csr(csr_text, config_obj, backend_obj)
    return(resp)

if __name__ == '__main__':
    app.run(host=config_obj.data['service_config']['ip_address'],
            port=config_obj.data['service_config']['port_number'])
