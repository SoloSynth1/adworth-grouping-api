#!/usr/bin/env bash

port=8000
scriptDir=$(dirname "$0")
cd $scriptDir
nohup ./venv/bin/python3 ./src/main.py -p $port > nohup.log &
