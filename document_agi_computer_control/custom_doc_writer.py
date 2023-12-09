# will implement the doc writer myself.
# first thing: visualize the progress.

code_file_path = (
    "/media/root/Toshiba XG3/works/agi_computer_control_python_doc/src/use_logging.py"
)

prompt_template = """
You are reading code from codebase in chunks. You would understand what the code is doing and return brief comments.
Code:
{code}
Comment for code at {location}:
"""

import langchain

from langchain.prompts import PromptTemplate

write_docstings_for_code_prompt = PromptTemplate(
    input_variables=["code", "location"], template=prompt_template
)

# usually the line is not so long. but if it does, we cut it.


class DocProcessQueue:
    def __init__(self, char_limit=1000, line_limit=15):
        self.char_limit = char_limit
        self.line_limit = line_limit
    
    def 


process_queue = DocProcessQueue()

with open(code_file_path, "r") as f:
    content = f.read()
    lines = content.split("\n")

    for lineno, line in enumerate(lines):
        line = line.strip()
        if line:
            process_queue.push(line, lineno)
