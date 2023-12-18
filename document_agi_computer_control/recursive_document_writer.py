import os
import json

# os.environ["OPENAI_API_KEY"] = "any"
# os.environ["OPENAI_API_BASE"] = "http://0.0.0.0:8000"
# os.environ["BETTER_EXCEPTIONS"] = "1"

from custom_doc_writer import construct_llm_and_write_code_comment, parse_arguments
from beartype import beartype

@beartype
def scan_code_dir_and_write_to_comment_dir(
    code_dir_path: str, output_dir_path: str #, summary_dir_path: str
):
    for fpath in os.listdir(code_dir_path):
        print("processing:", fpath)
        code_path = os.path.join(code_dir_path, fpath)
        comment_rel_path = fpath.replace(".", "_") + ".json"
        comment_path = os.path.join(output_dir_path, comment_rel_path)
        # summary_path = os.path.join(summary_dir_path, comment_rel_path)

        ret = construct_llm_and_write_code_comment(code_path, comment_path)
        # summary_code_comment_return_value_and_write_to_path(summary_path, ret)


if __name__ == "__main__":
    (
        programming_language,
        code_dir_path,
        output_dir_path,
        # summary_dir_path,
    ) = parse_arguments(assert_file=False)
    scan_code_dir_and_write_to_comment_dir(
        code_dir_path, output_dir_path,  # summary_dir_path
    )
