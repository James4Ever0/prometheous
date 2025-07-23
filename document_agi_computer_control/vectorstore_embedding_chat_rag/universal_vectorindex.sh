export PROMETHEOUS_MAX_TOKENS=13468
export OPENAI_API_KEY=any

export OPENAI_API_BASE=http://localhost:11434/v1
export PROMETHEOUS_MODEL_NAME=gemma:2b-instruct

export OLLAMA_BASE_URL=http://localhost:11434
export PROMETHEOUS_EMBEDDING_MODEL=gemma:2b-instruct

export EMBEDDING_DIMENSION=2048

export DOC_PATH=$(realpath ../../../test_doc/doc/)
python3 vectorindex_universal.py -s $DOC_PATH
