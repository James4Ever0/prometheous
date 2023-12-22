
# os.environ["OPENAI_API_KEY"] = "any"
# os.environ["OPENAI_API_BASE"] = "http://0.0.0.0:8000"
# os.environ["BETTER_EXCEPTIONS"] = "1"
import os
import uuid

from beartype import beartype

from cache_db_context import (SourceIteratorAndTargetGeneratorParam,
                              TargetGeneratorParameter,
                              iterate_source_dir_and_generate_to_target_dir)
from custom_doc_writer import (construct_llm_and_write_code_comment,
                               parse_arguments)


@beartype
def dirpath_and_fpath_walker(dir_path: str):
    for dirpath, _, filenames in os.walk(dir_path):
        for filename in filenames:
            fpath = os.path.join(dirpath, filename)
            yield dirpath, fpath


@beartype
def get_source_iterator_and_target_generator_param_from_document_dir(
    document_dir: str,
    code_relpath: str = "src",
    output_relpath: str = "doc",
    db_relpath: str = "cache_db.json",
):
    source_dir_path = os.path.join(document_dir, code_relpath)
    target_dir_path = os.path.join(document_dir, output_relpath)
    db_path = os.path.join(document_dir, db_relpath)

    param = SourceIteratorAndTargetGeneratorParam(
        source_dir_path=source_dir_path,
        target_dir_path=target_dir_path,
        db_path=db_path,
    )
    return param


@beartype
def generate_comment_path(param: TargetGeneratorParameter):
    comment_rel_path = str(uuid.uuid4()) + ".json"
    comment_path = os.path.join(param.target_dir_path, comment_rel_path)
    return comment_path

@beartype
def scan_code_dir_and_write_to_comment_dir(document_dir: str):
    param = get_source_iterator_and_target_generator_param_from_document_dir(document_dir)
    iterate_source_dir_and_generate_to_target_dir(
        param,
        dirpath_and_fpath_walker,
        generate_comment_path,
        construct_llm_and_write_code_comment,
    )

if __name__ == "__main__":
    (document_dir_path) = parse_arguments()
    scan_code_dir_and_write_to_comment_dir(
        document_dir_path
    )
