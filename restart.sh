#!/usr/bin/env bash


ps aux | grep ec_erp_app.py | grep -v | grep python | awk '{print $2;}' | xargs kill -9

nohup python ec_erp_app.py 2>&1 1>>std.log &
