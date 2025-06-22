#!/usr/bin/env bash

conda activate ec_erp_env

mkdir -p logs

listen_port=`grep listen_port conf/application.json | awk -F ":" '{print $2;}' | tr -d ","`
procs=`netstat -nlpt | grep $listen_port | awk '{print $7;}'  | awk -F"/" '{print $1;}' `

if [[ "$procs" != "" ]]
then
  echo "stopping process $procs"
  echo "$procs" | xargs kill -9
else
  echo "No process found. not need stop."
fi

nohup python ec_erp_app.py 2>&1 1>>std.log &
