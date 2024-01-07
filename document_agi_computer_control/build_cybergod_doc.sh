export OPENAI_API_KEY='any'
export OPENAI_API_BASE=http://0.0.0.0:8000
export BETTER_EXCEPTIONS=1

# python3 visual_file_selector_by_ignore_rules/file_copy_by_fd.py -b "/media/root/Toshiba XG3/works/agi_computer_control" -t "/media/root/Toshiba XG3/works/cybergod_doc/src"

ntfy_error python3 stdout_redirect_progress/main_once.py -- python3 -u recursive_document_writer.py -d "/media/root/Toshiba XG3/works/cybergod_doc" -u "https://github.com/james4ever0/agi_computer_control"

cd "/media/root/Toshiba XG3/works/cybergod_doc"
python3 -m http.server 8001