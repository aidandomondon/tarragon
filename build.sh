#!/bin/bash
set -e

# Make LLM llamafile executable
chmod +x ./Llama-3.2-1B-Instruct.Q6_K.llamafile

# Make llamafiler executable
chmod +x ./llamafiler

# Create and start virtual environment and install python package dependencies into it
python3 -m venv ./.venv
source ./.venv/bin/activate
if [[ "$VIRTUAL_ENV" != "" ]]
then 
    pip3 install -r ./requirements.txt
fi