#!/bin/bash

pwd
python3 --version
echo $1
python3 main.py --benchmark $1
