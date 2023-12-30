# os.environ["OPENAI_API_KEY"] = "any"
# os.environ["OPENAI_API_BASE"] = "http://0.0.0.0:8000"
# os.environ["BETTER_EXCEPTIONS"] = "1"
import os
from typing import Literal, Optional, Union
import uuid
import json

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

    def insert_code_and_comment(self, code: str, comment: str):
        self.insert(
            content=code,
            type="code",
        )
        self.insert(
            content=comment,
            type="comment",
        )

    def insert(
        self,
        content: str,
        type: Literal["filepath", "summary", "comment", "code"],
    ):
        assert isinstance(self.file_id, int)
        self[self.counter] = dict(file_id=self.file_id, content=content, type=type)
        self.counter += 1


@beartype
def render_document_webpage(
    document_dir_path: str,
    param: SourceIteratorAndTargetGeneratorParam,
    repository_url: str,
    template_dir: str = ".",
    template_filename: str = "website_template.html.j2",
    output_filename: str = "index.html",
    url_prefix: str = "https://github.com/",
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
                )

        @beartype
        def update_data_and_file_mapping(
            manager: CacheManager, record: dict, file_id: int, source_relative_path: str
        ):
            file_mapping[file_id] = dict(
                filepath=source_relative_path, entry_id=data.counter
            )
            target_path, _ = manager.get_record_target_path_and_hash(record)
            target_data = json.loads(read_file(target_path))
            update_data_by_target_data(target_data, file_id, source_relative_path)

        def assemble_render_params():
            partial_repository_url = repository_url.replace(url_prefix, "")
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
                for file_id, (_, source_path) in enumerate(
                    dirpath_and_fpath_walker(param.source_dir_path)
                ):
                    source_relative_path = source_path[len(param.source_dir_path) :]
                    record, _ = manager.get_record_by_computing_source_hash(source_path)
                    if record:
                        update_data_and_file_mapping(
                            manager, record, file_id, source_relative_path
                        )

            return assemble_render_params()

        return iterate_source_dir_and_assemble_render_params()

    @beartype
    def render_template(template: Template):
        render_params = get_template_render_params()
        ret = template.render(**render_params)
        return ret

    def render_to_output_path():
        template = load_template()
        content = render_template(template)
        write_to_output_path(content)

    render_to_output_path()


def main():
    (document_dir_path, repository_url) = parse_arguments()
    param = scan_code_dir_and_write_to_comment_dir(document_dir_path)
    # not done yet. we have to create the webpage.
    render_document_webpage(document_dir_path, param, repository_url)


if __name__ == "__main__":
    main()
