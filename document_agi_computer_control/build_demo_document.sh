
# pass the repository url as parameter of document builder 

export OPENAI_API_KEY='any'
export OPENAI_API_BASE=http://0.0.0.0:8000
export BETTER_EXCEPTIONS=1



# python3 stdout_redirect_progress/main_once.py -- python3 -u recursive_document_writer.py -d "/media/root/Toshiba XG3/works/prometheous/document_agi_computer_control/demo_document_repository" -u "https://github.com/james4ever0/agi_computer_control"
python3 recursive_document_writer.py -d "/media/root/Toshiba XG3/works/prometheous/document_agi_computer_control/demo_document_repository" -u "https://github.com/james4ever0/agi_computer_control"

cd demo_document_repository
python3 -m http.server 8001