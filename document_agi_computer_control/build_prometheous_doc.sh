export OPENAI_API_KEY='any'
export OPENAI_API_BASE=http://0.0.0.0:8000
export BETTER_EXCEPTIONS=1

PROJECT_ROOT="/media/root/Toshiba XG3/works/prometheous"
PROJECT_URL="https://github.com/james4ever0/prometheous"
DOC_ROOT="/media/root/Toshiba XG3/works/prometheous_doc"

python3 visual_file_selector_by_ignore_rules/main_pyjom.py -d "$PROJECT_ROOT"

echo "removing: $DOC_ROOT/src"

read -p "Are you sure you want to remove? (y/n): " answer

if [ "$answer" = "y" ]; then
    echo "Removing..."
    # Place your program execution command here
    rm -rf "$DOC_ROOT/src"
else
    echo "Exiting..."
    exit 1
fi

python3 visual_file_selector_by_ignore_rules/file_copy_by_fd.py -b "$PROJECT_ROOT" -t "$DOC_ROOT/src"

ntfy_error python3 stdout_redirect_progress/main_once.py -- python3 -u recursive_document_writer.py -d "$DOC_ROOT" -u "$PROJECT_URL"

cd "$DOC_ROOT"
python3 -m http.server 8001