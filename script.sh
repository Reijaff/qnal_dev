echo Starting tts server ... 
python tts_server.py &
# exec $1 &

bash

trap 'pkill -f tts_server.py && echo "Exiting the shell"' EXIT