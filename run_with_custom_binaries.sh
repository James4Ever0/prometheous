# let us not to use alias.
# let us use heredoc and export these binaries to PATH

TMP_BINARY_PATH=/tmp/binaries
rm -rf $TMP_BINARY_PATH
mkdir -p $TMP_BINARY_PATH

PYTHON_BINARY=$(which python3)

echo "Using Python binary: $PYTHON_BINARY"

cat <<EOF > $TMP_BINARY_PATH/ntfy_error
#!/bin/bash
echo "Dummy ntfy_error"
echo "Args: \$@"
\$@
EOF

chmod +x $TMP_BINARY_PATH/ntfy_error

cat <<EOF > $TMP_BINARY_PATH/python3.9
#!/bin/bash
echo "Dummy python3.9"
echo "Args: \$@"
$PYTHON_BINARY \$@
EOF

chmod +x $TMP_BINARY_PATH/python3.9

export PATH=$TMP_BINARY_PATH:$PATH

export PROMETHEOUS_MAX_TOKENS=13468
export PROMETHEOUS_MODEL_NAME=gemma3:27b
export OPENAI_API_KEY=any
export OPENAI_API_BASE=http://10.10.11.178:11434/v1

export PROJECT_ROOT="/home/jamesbrown/Desktop/meilin_java/txt_files_source"
export PROJECT_URL="https://dummy_project_url.local"
export DOC_ROOT="/home/jamesbrown/Desktop/meilin_java/txt_controller_java_doc"
export HEADLESS=false

cd document_agi_computer_control

bash build_doc_custom_scriptable.sh
