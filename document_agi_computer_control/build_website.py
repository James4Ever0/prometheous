import os
import argparse
import json
from beartype import beartype
from bs4 import BeautifulSoup
from jinja2 import Template

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        help=f"directory of code to process",
    )
    parser.add_argument(
        "-d",
        "--document",
        help=f"directory of document json to read",
    )
    parser.add_argument("-o", "--output", help="document output path", default="")
    args = parser.parse_args()

    code_dir_path = args.file
    json_path = args.json
    output_path = args.document

    assert os.path.isabs(code_dir_path)
    assert os.path.isabs(json_path)

    assert os.path.isdir(code_dir_path)
    assert os.path.isdir(json_path)

    return output_path, code_dir_path, json_path


@beartype
def generate_html_document(template:Template, data: dict):
    html = template.render(**data)
    return html

@beartype
def load_template(template_path:str):
    with open(template_path, "r") as f:
        content = f.read()
    template = Template(content)
    return template
    

@beartype
def generate_and_write_document(template:Template, data: dict, html_output_path: str):
    content = generate_html_document(template, data)
    with open(html_output_path, "w+") as f:
        f.write(content)


if __name__ == "__main__":
    output_path, code_dir_path, json_path = parse_arguments()

    template_path = "website_template.html.j2"
    template = load_template(template_path)

    for fpath in os.listdir(json_path):
        json_abspath = os.path.join(json_path, fpath)
        html_output_path = os.path.join(
            output_path,
            "index.html"
        )
        with open(json_abspath, "r") as f:
            data = json.load(
                f
            )  # {"summary": summary, "details": [{"comment": comment, "location": location, "content": content}, ...]}
            generate_and_write_document(template, data, html_output_path)
