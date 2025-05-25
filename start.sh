#!bin/bash
set -e


# Start the llm async and record pid for future shutdown
(./Llama-3.2-1B-Instruct.Q6_K.llamafile --server --port 8081 --nobrowser -c 2048)&
(llm_pid=$!; echo "llm_pid: $llm_pid")


# Start the embedding model async and record pid for future shutdown
(./llamafiler -m ./mxbai-embed-large-v1-f16.gguf -l localhost:8082 -c 2048)&
(embedding_model_pid=$!; echo "embedding_model_pid: $embedding_model_pid")
    

# Start Python virtual environment. If successful, start app
source ./.venv/bin/activate 
if [[ "$VIRTUAL_ENV" != "" ]]
then 
    python ./src/main.py
fi

# Kill the LLM and embedding model on script termination
trap 'kill $llm_pid; kill $embedding_model_pid' SIGINT SIGTERM