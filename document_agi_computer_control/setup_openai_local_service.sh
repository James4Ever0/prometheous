# use fastchat. (pip3 install fschat)
# run `pip3 install setuptools-scm` first.
# python3 -m fastchat.serve.cli --model-path /media/root/Prima/WD2000_Backup/Llama-7b-chat
# python3 -m fastchat.serve.cli --model-path /media/root/Prima/WD2000_Backup/Llama-7b-chat
export BETTER_EXCEPTIONS=1
litellm --model ollama/openhermes2.5-mistral --drop_params
# litellm --model ollama/openhermes2.5-mistral --debug --drop_params
