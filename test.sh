#!/bin/bash

# Report this process's PID (so that it can be killed) by a third party command later
echo getpgid $$

# Define function to kill subshells
function kill_llm_and_embedding_model {
    echo "Closing all subshells."
    kill ${PIDs[0]}
    kill ${PIDs[1]}
}
# Call function when third party command sends signal "USR1".
trap kill_llm_and_embedding_model USR1

# Launch first async process
(
    while true
    do {
        sleep 1
        echo 2
    } done
)&
# Record PID
PIDs[0]=$!

# Launch second async process
(
    while true
    do {
        sleep 1
        echo 3
    } done
)&
# Record PID
PIDs[1]=$!

# (
#     sleep 5
#     kill_llm_and_embedding_model
# )&
# clean_up_PID=$!
# wait $clean_up_PID
