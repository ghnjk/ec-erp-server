#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: trainning_web
@author: jkguo
@create: 2022/7/9
"""
from flask import Flask
from ec_erp_api.app_config import get_app_config


app_config = get_app_config()


def create_app():
    from ec_erp_api.apis.system import system_apis
    app = Flask(app_config["application"])
    app.register_blueprint(system_apis, url_prefix="/erp_api/system")
    return app


def main():
    app = create_app()
    app.secret_key = app_config["session_secret_key"]
    listen_port = app_config["listen_port"]
    app.run(debug=True, port=listen_port)


if __name__ == '__main__':
    main()
