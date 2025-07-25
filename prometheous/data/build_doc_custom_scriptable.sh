# export OPENAI_API_KEY='any'
# export OPENAI_API_BASE=http://0.0.0.0:8000
export BETTER_EXCEPTIONS=1

# PROJECT_NAME="Video-Pre-Training"
# AUTHOR="openai"

# Check if PROJECT_ROOT environment variable is set
if [ -z "$PROJECT_ROOT" ]; then
    echo "ERROR: PROJECT_ROOT environment variable is not set" >&2
    exit 1
else
    echo "PROJECT_ROOT environment variable is set to: $PROJECT_ROOT"
fi

# Check if DOC_ROOT environment variable is set
if [ -z "$DOC_ROOT" ]; then
    echo "ERROR: DOC_ROOT environment variable is not set" >&2
    exit 1
else
    echo "DOC_ROOT environment variable is set to: $DOC_ROOT"
fi

# Check if PROJECT_URL environment variable is set
if [ -z "$PROJECT_URL" ]; then
    echo "ERROR: PROJECT_URL environment variable is not set" >&2
    exit 1
else
    echo "PROJECT_URL environment variable is set to: $PROJECT_URL"
fi

# provided
# PROJECT_ROOT="/media/root/Prima/works/$PROJECT_NAME"
# PROJECT_URL="https://github.com/$AUTHOR/$PROJECT_NAME"
# DOC_ROOT="/media/root/Prima/works/$PROJECT_NAME/docs"

if [ ! -d "$PROJECT_ROOT" ]; then
    echo "The directory '$PROJECT_ROOT' does not exist."
    exit 1  # Exit the script with a non-zero status code
fi

echo "Evaluating ignore rules"

python3.9 visual_file_selector_by_ignore_rules/main_pyjom.py -d "$PROJECT_ROOT" $@

echo "Removing: $DOC_ROOT/src"

echo "Headless: $HEADLESS"
if [ "$HEADLESS" = "true" ]; then
    answer="y"
else
    read -p "Are you sure you want to remove and generate? (y/n): " answer
fi


if [ "$answer" = "y" ]; then
    echo "Removing..."
    # Place your program execution command here
    rm -rf "$DOC_ROOT/src"
    mkdir -p "$DOC_ROOT/doc"
    mkdir -p "$DOC_ROOT/src"
    mkdir -p "$DOC_ROOT/data"
else
    echo "Exiting..."
    exit 1
fi

python3.9 ensure_fdignore_with_doc.py -b "$PROJECT_ROOT"

python3.9 visual_file_selector_by_ignore_rules/file_copy_by_fd.py -b "$PROJECT_ROOT" -t "$DOC_ROOT/src"

# char by char is infeasible since utf-8 has two byte chars. anyway, skip it for now.
ntfy_error python3.9 stdout_redirect_progress/main_once.py -- python3.9 -u recursive_document_writer.py -d "$DOC_ROOT" -u "$PROJECT_URL"

# cd "$PROJECT_ROOT"

cd "$DOC_ROOT"
# git add .
# git commit -m "update"
# git push origin master
# git push origin main
# git push origin develop

if [ "$HEADLESS" = "true" ]; then
    echo "Exiting"
else
    python3.9 -m http.server 8001
fi
