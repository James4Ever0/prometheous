# will implement the doc writer myself.
# first thing: visualize the progress.

# TODO: specify location like: module -> filename -> block name (class/method) -> lineno

# usually the line is not so long. but if it does, we cut it.
from typing import Callable

import argparse, os
import json
from beartype import beartype
from beartype.door import is_bearable
from beartype.vale import Is
from typing import Annotated, Optional  # <--------------- if Python ≥ 3.9.0
from llm import LLM
import copy
from codepiece_summarizer import comment_summarizer


NonEmptyString = Annotated[str, Is[lambda str_obj: len(str_obj.strip()) > 0]]


class DocumentProcessingException(Exception):
    ...  # placeholder


class UnableToCutByLineLimit(Exception):
    ...


class ZeroCutIndex(Exception):
    def __init__(self):
        super().__init__("Unable to cut with zero cut index.")


@beartype
def commentProcessMethodFactory(model: LLM, prompt_generator: Callable):
    # better not to
    @beartype
    def commentProcessMethod(
        content: NonEmptyString,
        location: NonEmptyString,
        response_token_limit: int = 60,
        previous_comment: str = "",
    ) -> tuple[bool, str]:
        success = False
        prompt = prompt_generator(content, location, previous_comment=previous_comment)
        result = model.run(prompt)
        success = True
        return success, result

    return commentProcessMethod


@beartype
class DocProcessQueue:
    def __init__(
        self, process_method: Callable, filepath: str, char_limit=1000, line_limit=15
    ):
        self.init_limits_and_counters(char_limit, line_limit)
        self.init_storage()
        self.process_method = process_method
        self.filepath = filepath

    def init_storage(self):
        self.queue = []
        self.locations = []
        self.result_all = []
        self.previous_comment = ""

    def init_limits_and_counters(self, char_limit: int, line_limit: int):
        self.char_limit = char_limit
        self.line_limit = line_limit

        self.char_count = 0
        self.line_count = 0

    def char_limit_exceeded(self):
        return self.char_count > self.char_limit

    def line_limit_exceeded(self):
        return self.line_count > self.line_limit

    def strip_storage_by_cut_index(self, cut_index: int):
        self.queue = self.queue[cut_index:]
        self.locations = self.locations[cut_index:]

    def prepare_content_and_location(
        self, cut_index: int, cut_content: Optional[str] = None
    ):
        from_lineno, to_lineno = self.locations[0], self.locations[cut_index - 1]

        lines = self.queue[:cut_index]
        if cut_content is not None:
            lines[-1] = cut_content
        content = "\n".join(lines)
        location = f'"{self.filepath}":{from_lineno}-{to_lineno}'
        return content, location

    def get_cut_and_remained_params_by_char_limit(self):
        char_count = 0
        remained_content = None
        cut_content = None
        remained_location = None
        cut_index = None
        for index, line in enumerate(self.queue):
            char_count += len(line)
            if char_count > self.char_limit:
                reverse_cut_point = char_count - self.char_limit
                cut_point = len(line) - reverse_cut_point
                cut_content = line[:cut_point]
                remained_content = line[cut_point:]
                remained_location = self.locations[index]
                cut_index = index + 1
                break
        return cut_index, cut_content, remained_content, remained_location

    def process_by_char_limit(self):
        (
            cut_index,
            cut_content,
            remained_content,
            remained_location,
        ) = self.get_cut_and_remained_params_by_char_limit()
        content, location = self.prepare_content_and_location(cut_index, cut_content)
        self.strip_storage_by_cut_index(cut_index)

        if remained_content:
            self.queue.insert(0, remained_content)
            self.locations.insert(0, remained_location)
        return content, location

    def update_counters(self):
        self.char_count = len("".join(self.queue))
        self.line_count = len(self.queue)

    def get_cut_params_by_line_limit(self, final: bool):
        if self.line_count > self.line_limit:
            cut_index = self.line_limit
        elif final:
            cut_index = self.line_count
        else:
            raise UnableToCutByLineLimit(
                f"Current line count {self.line_count} below limit {self.line_limit}"
            )
        if cut_index == 0:
            raise ZeroCutIndex()
        cut_content = None
        return cut_index, cut_content

    def process_by_line_limit(self, final=False):
        cut_index, cut_content = self.get_cut_params_by_line_limit(final)
        content, location = self.prepare_content_and_location(cut_index, cut_content)
        self.strip_storage_by_cut_index(cut_index)
        return content, location

    def process_by_limit(self, final=False):
        processed = True
        content = ""
        location = ""
        if self.char_limit_exceeded():
            content, location = self.process_by_char_limit()
        elif self.line_limit_exceeded() or final:
            content, location = self.process_by_line_limit(final=final)
        else:
            processed = False

        if processed:
            self.update_counters()
        return processed, content, location

    def process(self, final=True):
        processed, content, location = self.process_by_limit(final=final)
        if processed:
            if is_bearable(content, NonEmptyString):
                success, result = self.process_method(
                    content, location, self.previous_comment
                )
                if not success:
                    raise DocumentProcessingException(
                        "Failed to process code at:", location
                    )
                self.previous_comment = result
                yield dict(comment=result, location=location, content=content)
        if final:
            if len(self.queue) != 0:
                yield from self.process(final=True)

    def process_and_collect_all(self, final=True):
        ret = list(self.process(final=final))
        self.result_all.extend(ret)
        return ret

    def update_counter_after_push(self, content: str):
        self.char_count += len(content)
        self.line_count += 1

    def push(self, content: str, lineno: int):
        self.queue.append(content)
        self.locations.append(lineno)
        self.update_counter_after_push(content)

    def push_and_process(self, content: str, lineno: int):
        self.push(content, lineno)
        return self.process_and_collect_all(final=False)  # final


@beartype
def process_code_and_get_result(process_queue: DocProcessQueue, filepath: str):
    with open(filepath, "r") as f:
        content = f.read()
        lines = content.split("\n")

        for lineno, line in enumerate(lines):
            if is_bearable(line, NonEmptyString):
                process_queue.push_and_process(line, lineno)

    process_queue.process_and_collect_all()
    result_all = copy.copy(process_queue.result_all)
    return result_all


@beartype
def assert_exists_as_absolute_directory(basepath: str):
    assert os.path.isabs(basepath)
    assert os.path.isdir(basepath)


@beartype
def join_and_assert_exists_as_absolute_directory(basepath: str, name: str):
    joined_path = os.path.join(basepath, name)
    assert_exists_as_absolute_directory(joined_path)
    return joined_path


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--document_dir",
        help=f"document directory, contains 'src' as source code directory, 'doc' as comment json directory",
    )
    args = parser.parse_args()

    document_dir = args.document_dir
    assert_exists_as_absolute_directory(document_dir)
    join_and_assert_exists_as_absolute_directory(document_dir, "src")
    join_and_assert_exists_as_absolute_directory(document_dir, "doc")

    return document_dir


@beartype
def summary_code_comment_return_value(ret: list[dict]):
    comment_list = [elem["comment"] for elem in ret]
    summary = comment_summarizer(comment_list)
    return summary


@beartype
def process_code_and_write_result(
    model: LLM,
    prompt_generator: Callable,
    code_file_path: str,
    output_path: str,
):
    commentProcessMethod = commentProcessMethodFactory(model, prompt_generator)
    process_queue = DocProcessQueue(commentProcessMethod, code_file_path)
    result_all = process_code_and_get_result(process_queue, code_file_path)

    summary = summary_code_comment_return_value(result_all)

    data = {"summary": summary, "details": result_all}

    serialized = json.dumps(data, ensure_ascii=False, indent=4)

    with open(output_path, "w+") as f:
        f.write(serialized)
    del process_queue
    return result_all


@beartype
def filter_empty_elements(mlist: list):
    return [elem for elem in mlist if elem]


@beartype
def generate_location_component(location: str):
    return f"""Storage location: {location}"""


@beartype
def generate_previous_comment_component(previous_comment: str):
    return (
        f"""Previous code comment:
{previous_comment}"""
        if previous_comment
        else ""
    )


@beartype
def generate_code_component(programming_language: str, code: str):
    return f"""Code:
```{programming_language}
{code}
```"""


def generate_comment_coponent():
    return """Comment for code:
"""


@beartype
def generate_prompt_components(
    code: str, location: str, programming_language: str, previous_comment: str
):
    location_component = generate_location_component(location)
    previous_comment_component = generate_previous_comment_component(previous_comment)
    code_component = generate_code_component(programming_language, code)
    comment_component = generate_comment_coponent()
    components = [
        location_component,
        previous_comment_component,
        code_component,
        comment_component,
    ]
    return components


@beartype
def assemble_prompt_components(components: list[str]):
    components = filter_empty_elements(components)
    ret = "\n".join(components)
    return ret


@beartype
def generate_prompt_generator(programming_language: str):
    @beartype
    def prompt_generator(code: str, location: str, previous_comment: str = ""):
        components = generate_prompt_components(
            code, location, programming_language, previous_comment
        )
        ret = assemble_prompt_components(components)
        return ret

    return prompt_generator


@beartype
def generate_prompt_base(word_limit: int):
    return f"""You are reading code from codebase in chunks. You would understand what the code is doing and return brief comments (under {word_limit} words)."""


@beartype
def construct_llm_and_write_code_comment(
    code_file_path: str,
    output_path: str,
    programming_language: str = "",
    word_limit: int = 15,
):
    prompt_base = generate_prompt_base(word_limit)

    prompt_generator = generate_prompt_generator(programming_language)

    model = LLM(prompt_base)

    ret = process_code_and_write_result(
        model, prompt_generator, code_file_path, output_path
    )

    del model
    return ret


if __name__ == "__main__":
    programming_language, code_file_path, output_path = parse_arguments()
    construct_llm_and_write_code_comment(
        code_file_path, output_path, programming_language=programming_language
    )
