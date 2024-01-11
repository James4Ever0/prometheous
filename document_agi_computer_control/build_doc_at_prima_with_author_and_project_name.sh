export OPENAI_API_KEY='any'
export OPENAI_API_BASE=http://0.0.0.0:8000
export BETTER_EXCEPTIONS=1

# PROJECT_NAME="Video-Pre-Training"
# AUTHOR="openai"

PROJECT_ROOT="/media/root/Prima/works/$PROJECT_NAME"
PROJECT_URL="https://github.com/$AUTHOR/$PROJECT_NAME"
DOC_ROOT="/media/root/Prima/works/$PROJECT_NAME/docs"

if [ ! -d "$PROJECT_ROOT" ]; then
    echo "The directory '$PROJECT_ROOT' does not exist."
    exit 1  # Exit the script with a non-zero status code
fi

python3 visual_file_selector_by_ignore_rules/main_pyjom.py -d "$PROJECT_ROOT" $@

echo "removing: $DOC_ROOT/src"


echo "headless: $HEADLESS"
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

python3 ensure_fdignore_with_doc.py -b "$PROJECT_ROOT"

python3 visual_file_selector_by_ignore_rules/file_copy_by_fd.py -b "$PROJECT_ROOT" -t "$DOC_ROOT/src"

# char by char is infeasible since utf-8 has two byte chars. anyway, skip it for now.
ntfy_error python3 stdout_redirect_progress/main_once.py -- python3 -u recursive_document_writer.py -d "$DOC_ROOT" -u "$PROJECT_URL"
cd "$PROJECT_ROOT"

git add .
git commit -m "update"
git push origin master
git push origin main
cd "$DOC_ROOT"
if [ "$HEADLESS" = "true" ]; then
    echo "Exiting"
else
    python3 -m http.server 8001
fi