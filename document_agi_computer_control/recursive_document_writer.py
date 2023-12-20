import os
import json
import tinydb
import uuid

# os.environ["OPENAI_API_KEY"] = "any"
# os.environ["OPENAI_API_BASE"] = "http://0.0.0.0:8000"
# os.environ["BETTER_EXCEPTIONS"] = "1"

from custom_doc_writer import construct_llm_and_write_code_comment, parse_arguments
from beartype import beartype


@beartype
def scan_code_dir_and_write_to_comment_dir(document_dir: str):
    code_dir_path = os.path.join(document_dir, "src")
    output_dir_path = os.path.join(document_dir, "doc")
    db_path = os.path.join(document_dir, "cache_db.json")

    db = tinydb.TinyDB(db_path)
    for fpath in os.listdir(code_dir_path):
        print("processing:", fpath)

        code_path = os.path.join(code_dir_path, fpath)
        comment_rel_path = str(uuid.uuid4()) + ".json"
        comment_path = os.path.join(output_dir_path, comment_rel_path)

        query = tinydb.Query()
        code_hash = ...
        record = db.get(query.code.hash == code_hash) # what if empty file?

        if record:
            record_comment_hash = record['comment']['hash']
            if code_hash == record_code_hash:
                if os.path.exists(comment_path):
                    old_comment_hash = ...
                    if old_comment_hash == record_comment_hash:
                        print("comment exists for code:", code_path)
                        continue
        ret = construct_llm_and_write_code_comment(code_path, comment_path)
        db.upsert(
            {
                "code": {"path": code_path, "hash": code_hash},
                "comment": {"path": comment_path},
            }
        )


if __name__ == "__main__":
    (
        document_dir_path
    ) = parse_arguments(assert_file=False)
    scan_code_dir_and_write_to_comment_dir(
        code_dir_path,
        output_dir_path,  # summary_dir_path
    )