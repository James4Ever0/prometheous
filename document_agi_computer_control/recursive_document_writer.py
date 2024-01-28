# os.environ["OPENAI_API_KEY"] = "any"
# os.environ["OPENAI_API_BASE"] = "http://0.0.0.0:8000"
# os.environ["BETTER_EXCEPTIONS"] = "1"

# TODO: add shared context while spliting code into chunks

import os
from typing import Literal, Optional, Union #, OrderedDict
import uuid
import json
from slice_utils import split_dict_into_chunks
import parse
import shutil
import custom_doc_writer

CODE_LOCATION_FORMAT = '"{code_path}":{line_start:d}-{line_end:d}'
DATA_SLICE_LENGTH = 100
from beartype import beartype

from cache_db_context import (
    CacheContextManager,
    CacheManager,
    SourceIteratorAndTargetGeneratorParam,  # type:ignore
    TargetGeneratorParameter,
    iterate_source_dir_and_generate_to_target_dir,
    read_file,
    write_file,
)
from custom_doc_writer import (
    construct_llm_and_write_code_comment,  # type:ignore
    parse_arguments,
)
from identify_utils import get_language_id_from_filename


@beartype
def file_empty(fpath: str):
    assert os.path.exists(fpath), "File %s does not exist" % fpath
    with open(fpath, "r") as f:
        content = f.read().strip()
        if content == "":
            return True
    return False


@beartype
def dirpath_and_fpath_walker(dir_path: str):
    for dirpath, _, filenames in os.walk(dir_path):
        for filename in filenames:
            fpath = os.path.join(dirpath, filename)
            if not file_empty(fpath):
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
    param = get_source_iterator_and_target_generator_param_from_document_dir(
        document_dir
    )
    iterate_source_dir_and_generate_to_target_dir(
        param,
        dirpath_and_fpath_walker,
        generate_comment_path,
        construct_llm_and_write_code_comment,
    )
    return param


from jinja2 import Environment, FileSystemLoader, Template


@beartype
class SearchIndexData(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0
        self.file_id: Optional[int] = None

    def insert_filepath_and_summary(self, file_id: int, filepath: str, summary: str):
        self.file_id = file_id
        self.insert(
            content=filepath,
            type="filepath",
        )
        self.insert(
            content=summary,
            type="summary",
        )

    def insert_code_and_comment(self, code: str, comment: str, location: str):
        self.insert(content=code, type="code", location=location)
        self.insert(
            content=comment,
            type="comment",
        )

    def insert(
        self,
        content: str,
        type: Literal["filepath", "summary", "comment", "code"],
        location: Optional[str] = None,
    ):
        assert isinstance(self.file_id, int)
        self[self.counter] = dict(
            file_id=self.file_id,
            content=content,
            type=type,
            **(dict(location=location) if location else {}),
        )
        self.counter += 1


@beartype
def render_document_webpage(
    document_dir_path: str,
    param: SourceIteratorAndTargetGeneratorParam,
    repository_url: str,
    template_dir: str = ".",
    template_filename: str = "website_template.html.j2",
    output_filename: str = "index.html",
    url_prefixs: list[str] = ["https://github.com/", "https://gitee.com/"],
    # url_prefix: str = "https://github.com/",
):
    @beartype
    def load_template() -> Template:
        # Load the template from file
        file_loader = FileSystemLoader(
            template_dir
        )  # Replace 'path_to_templates_directory' with the actual path
        env = Environment(loader=file_loader)
        template = env.get_template(
            template_filename
        )  # Replace 'sitemap_template.html' with the actual template file name
        return template

    @beartype
    def write_to_output_path(content: str):
        output_path = os.path.join(document_dir_path, output_filename)
        write_file(output_path, content)

    @beartype
    def get_template_render_params() -> dict[str, Union[dict, str]]:
        data = SearchIndexData()
        file_mapping: dict[int, dict[str, Union[str, int]]] = {}

        @beartype
        def strip_path_prefix(path: str):
            return path[len(param.source_dir_path) :]

        @beartype
        def strip_location(location: str):
            result = parse.parse(CODE_LOCATION_FORMAT, location)
            assert isinstance(result, parse.Result)
            stripped_path = strip_path_prefix(result["code_path"])
            return f"{stripped_path}:{result['line_start']+1}-{result['line_end']+1}"

        @beartype
        def update_data_by_target_data(
            target_data: dict, file_id: int, source_relative_path: str
        ):
            data.insert_filepath_and_summary(
                file_id=file_id,
                filepath=source_relative_path,
                summary=target_data["summary"],
            )
            for detail in target_data["details"]:
                data.insert_code_and_comment(
                    code=detail["content"],
                    comment=detail["comment"],
                    location=strip_location(detail["location"]),
                )

        @beartype
        def update_data_and_file_mapping(
            manager: CacheManager, record: dict, file_id: int, source_relative_path: str
        ):
            file_mapping[file_id] = dict(
                filepath=source_relative_path,
                entry_id=data.counter,
                language_id=get_language_id_from_filename(source_relative_path),
            )
            target_path, _ = manager.get_record_target_path_and_hash(record)
            target_data = json.loads(read_file(target_path))
            update_data_by_target_data(target_data, file_id, source_relative_path)

        def assemble_render_params():
            partial_repository_url = repository_url
            for it in url_prefixs:
                partial_repository_url = partial_repository_url.replace(it, "").strip(
                    "/"
                )
            render_params = dict(
                datadict=data,
                repository_url=repository_url,
                file_mapping=file_mapping,
                partial_repository_url=partial_repository_url,
            )
            return render_params

        def iterate_source_dir_and_assemble_render_params():
            # if only have one file, we should return one
            with CacheContextManager(param.db_path) as manager:
                source_path_list = [
                    sp for _, sp in dirpath_and_fpath_walker(param.source_dir_path)
                ]
                source_path_list.sort()  # to reduce git folder size
                
                for file_id, source_path in enumerate(source_path_list):
                    source_relative_path = strip_path_prefix(source_path)
                    record, _ = manager.get_record_by_computing_source_hash(source_path)
                    if record:
                        update_data_and_file_mapping(
                            manager, record, file_id, source_relative_path
                        )

            return assemble_render_params()

        return iterate_source_dir_and_assemble_render_params()

    def strip_quote(s: str):
        s = s.strip()
        if s[0] == s[-1]:
            if s[0] in ['"', "'"]:
                return s[1:-1].strip()
        return s.strip()

    @beartype
    def write_render_params(render_params: dict):
        # TODO: mapping source file path to documentation json
        # TODO: add mode of index to hide search bar and render single file left-right comparison only
        datadict = render_params["datadict"]
        metadata = dict()
        metadata["url"] = dict(
            full=render_params["repository_url"],
            partial=render_params["partial_repository_url"],
        )
        metadata["file_mapping"] = render_params["file_mapping"]
        metadata["project_name"] = render_params["partial_repository_url"].split("/")[
            -1
        ]
        split_count = 0
        # datadict_split = {}
        datadict = {
            k: v
            if (v["type"] not in ["comment", "summary"])
            else {
                "file_id": v["file_id"],
                "content": strip_quote(v["content"]),
                "type": v["type"],
            }
            for k, v in datadict.items()
        }

        data_dir = os.path.join(document_dir_path, "data")
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)

        for chunk in split_dict_into_chunks(datadict, DATA_SLICE_LENGTH):
            write_file(
                os.path.join(data_dir, f"{split_count}.json"),
                json.dumps(chunk, indent=4, ensure_ascii=False),
            )
            split_count += 1
        metadata["split_count"] = split_count
        write_file(
            os.path.join(document_dir_path, "metadata.json"),
            json.dumps(metadata, indent=4, ensure_ascii=False),
        )

    @beartype
    def render_template(template: Template):
        render_params = get_template_render_params()
        write_render_params(render_params)
        # do something else, like writing to files.
        # ret = template.render(**render_params)
        # return ret

    def copy_static_pages():
        script_base_dir = os.path.split(__file__)[0]
        static_pages_dir = os.path.join(script_base_dir, "static_pages")
        for fname in ["index.html", "codeview.html"]:
            # for fname in os.listdir(static_pages_dir):
            shutil.copy(os.path.join(static_pages_dir, fname), document_dir_path)

    def write_gitignore():
        with open(os.path.join(document_dir_path, ".gitignore"), "w+") as f:
            f.write(
                "!.gitignore\n!*\n!*/*\ncache_db.json\ncache_tree.json\nvector_cache\n"
            )
            # f.write("!.gitignore\n!*\n!*/*\ncache_db.json\n")

    def render_to_output_path():
        template = load_template()
        render_template(template)
        copy_static_pages()
        write_gitignore()
        # content = render_template(template)
        # write_to_output_path(content)

    render_to_output_path()


import subprocess


def run_subprocess(cli: str):
    print("running:", cli)
    excode = subprocess.check_call(cli, shell=True)
    if excode != 0:
        exit(excode)


def main():
    (document_dir_path, repository_url) = parse_arguments()
    project_name = repository_url.split("/")[-1]
    custom_doc_writer.CUSTOM_DOC_WRITER_PARAMS["location_prefix"] = document_dir_path
    custom_doc_writer.CUSTOM_DOC_WRITER_PARAMS["project_name"] = project_name
    param = scan_code_dir_and_write_to_comment_dir(document_dir_path)
    # not done yet. we have to create the webpage.
    render_document_webpage(document_dir_path, param, repository_url)
    run_subprocess(
        f"python3.9 -u tree_markdown_view_folder_hierarchy/main_recursive.py -s '{document_dir_path}'"
    )
    run_subprocess(f"python3.9 -u title_generator/main.py -s '{document_dir_path}'")
    run_subprocess(f"python3.9 -u sitemap_generator/main.py -s '{document_dir_path}'")


if __name__ == "__main__":
    main()
