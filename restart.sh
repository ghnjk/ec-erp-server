#!/usr/bin/env bash

conda activate ec_erp_env

ps aux | grep ec_erp_app.py | grep -v grep| grep python | awk '{print $2;}' | xargs kill -9

nohup python ec_erp_app.py 2>&1 1>>std.log &
