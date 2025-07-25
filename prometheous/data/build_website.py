import argparse
import json
import os

from beartype import beartype
from jinja2 import Template

# it is better structured like:

# db: shared, unified mapping between filename, document json name (uuid) and document summary

# search results again in selected documents, from entry level
# search results in selected folder (you may click different part of the filepath to jump)
# search results in detail of each document file (if clicked in)

# or, just build a unified search index out of the entire repo.

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        help="directory of code to process",
    )
    parser.add_argument(
        "-d",
        "--document",
        help="directory of document json to read",
    )
    parser.add_argument("-o", "--output", help="document output path", default="")
    args = parser.parse_args()

    code_dir_path = args.file
    json_path = args.document
    output_path = args.output

    assert os.path.isabs(code_dir_path)
    assert os.path.isabs(json_path)

    assert os.path.isdir(code_dir_path)
    assert os.path.isdir(json_path)

    return output_path, code_dir_path, json_path


@beartype
def generate_html_document(template: Template, data: dict):
    html = template.render(**data)
    return html


@beartype
def load_template(template_path: str):
    with open(template_path, "r") as f:
        content = f.read()
    template = Template(content)
    return template


@beartype
def generate_and_write_document(template: Template, data: dict, html_output_path: str):
    content = generate_html_document(template, data)
    with open(html_output_path, "w+") as f:
        f.write(content)


if __name__ == "__main__":
    output_path, code_dir_path, json_path = parse_arguments()

    template_path = "website_template.html.j2"
    template = load_template(template_path)
    datalist = []
    html_output_path = os.path.join(output_path, "index.html")

    for fpath in os.listdir(json_path):
        json_abspath = os.path.join(json_path, fpath)

        with open(json_abspath, "r") as f:
            data = json.load(
                f
            )  # {"summary": summary, "details": [{"comment": comment, "location": location, "content": content}, ...]}
            summary = data["summary"]
            datalist.append(dict(title=summary))
    datadict = {index: content for index, content in enumerate(datalist)}
    template_data = dict(datadict=datadict)
    generate_and_write_document(template, template_data, html_output_path)
