#!/bin/bash

if command -v python3 &>/dev/null; then
    python3 run.py
elif command -v python &>/dev/null; then
    python run.py
else
    echo "Python is not installed. Please install Python 3 to run this application."
    exit 1
fi 