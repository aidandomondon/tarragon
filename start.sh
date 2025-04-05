#!bin/bash

source ./.venv/bin/activate 

if [[ "$VIRTUAL_ENV" != "" ]]
then 
    python ./src/main.py
fi