#!/usr/bin/env python3
# -*- coding:utf-8 _*-
"""
@file: trainning_web
@author: jkguo
@create: 2022/7/9
"""
from flask import Flask
from ec_erp_api.app_config import get_app_config
import logging
from ec_erp_api.common.api_core import set_file_logger

app_config = get_app_config()


def create_app():
    from ec_erp_api.apis.system import system_apis
    from ec_erp_api.apis.supplier import supplier_apis
    from ec_erp_api.apis.warehouse import warehouse_apis
    from ec_erp_api.apis.sale import sale_apis
    set_file_logger("logs/acc.log", logger=logging.getLogger("ACC"))
    set_file_logger("logs/async_task.log", logger=logging.getLogger("ASYNC_TASK"))
    set_file_logger("logs/invoker.log", logger=logging.getLogger("INVOKER"))
    set_file_logger("logs/sql.log", logger=logging.getLogger("sqlalchemy.engine"))

    app = Flask(app_config["application"], static_url_path='')
    app.static_folder = "./static"
    app.register_blueprint(system_apis, url_prefix="/erp_api/system")
    app.register_blueprint(supplier_apis, url_prefix="/erp_api/supplier")
    app.register_blueprint(warehouse_apis, url_prefix="/erp_api/warehouse")
    app.register_blueprint(sale_apis, url_prefix="/erp_api/sale")
    return app


def main():
    app = create_app()
    app.secret_key = app_config["session_secret_key"]
    listen_ip = app_config.get("listen_host", "127.0.0.1")
    listen_port = app_config["listen_port"]
    app.run(debug=False, threaded=True, host=listen_ip, port=listen_port)


if __name__ == '__main__':
    main()
