# do not create doc for bloated files, blob files.
# do not create too many docs

# do not create multiple documentation for identical files, identical code

export OPENAI_API_KEY='any'
export OPENAI_API_BASE=http://0.0.0.0:8000
export BETTER_EXCEPTIONS=1
# write-the docs example.py

python3 recursive_document_writer.py -f "/media/root/Toshiba XG3/works/agi_computer_control_python_doc/src" -o "/media/root/Toshiba XG3/works/agi_computer_control_python_doc/doc"

# python3 custom_doc_writer.py -f "/media/root/Toshiba XG3/works/agi_computer_control_python_doc/src/use_logging.py" -o "/media/root/Toshiba XG3/works/agi_computer_control_python_doc/doc/use_logging_py.json" -l python

# cd "/media/root/Toshiba XG3/works/agi_computer_control_python_doc/src"
# cp ../../agi_computer_control/*.py .
# write-the docs -s "/media/root/Toshiba XG3/works/agi_computer_control_python_doc/src"

# cd "/media/root/Toshiba XG3/works/agi_computer_control_python_doc/doc"
# write-the mkdocs "/media/root/Toshiba XG3/works/agi_computer_control_python_doc/src"
