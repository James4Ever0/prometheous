export PROMETHEOUS_MAX_TOKENS=13468
export OPENAI_API_KEY=any

#export OPENAI_API_BASE=http://localhost:11434/v1
#export PROMETHEOUS_MODEL_NAME=gemma:2b-instruct

#export OLLAMA_BASE_URL=http://localhost:11434
#export PROMETHEOUS_EMBEDDING_MODEL=gemma:2b-instruct

export OPENAI_API_BASE=http://10.10.11.178:11434/v1
export PROMETHEOUS_MODEL_NAME=gemma3:27b

export OLLAMA_BASE_URL=http://10.10.11.178:11434
export PROMETHEOUS_EMBEDDING_MODEL=qwen3:32b
#export PROMETHEOUS_EMBEDDING_MODEL=gemma3:27b

export EMBEDDING_DIMENSION=5120 # qwen3:32b
#export EMBEDDING_DIMENSION=2048 # gemma:2b-instruct

#export DOC_PATH=$(realpath ../../../test_doc/doc/)

export DOC_PATH=/home/jamesbrown/Desktop/meilin_java/txt_controller_java_doc

python3 vectorindex_universal.py -s $DOC_PATH
