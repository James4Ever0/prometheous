import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source_dir", type=str, required=True)
args = parser.parse_args()

# the only parameter.
source_dir = args.source_dir

assert os.path.exists(source_dir)
assert os.path.isdir(source_dir)
assert os.path.isabs(source_dir)

repo_name = os.path.split(source_dir)[1]
if repo_name == "docs":
    repo_name = os.path.split(os.path.dirname(source_dir))[1]

template_path = os.path.join(os.path.dirname(__file__), "sitemap.xml.j2")
# template_path = "sitemap_template.html.j2"
output_file_path = os.path.join(source_dir,"sitemap.xml")
base_url = f"https://james4ever0.github.io/{repo_name}"
from jinja2 import Template

template = Template(open(template_path, "r").read())
import json
metadata = json.loads(open(os.path.join(source_dir, "metadata.json"), "r").read())

file_mapping = metadata["file_mapping"]
# split_count = metadata["split_count"]
# project_name = metadata["project_name"]

import urllib.parse
lines = [
    f"{base_url}?q={urllib.parse.quote(comp['filepath'])}" for comp in file_mapping.values()
]
# Data to be rendered
datalist = [(item, "2023-12-28T09:21:02+00:00", "1.00") for item in lines]

# Render the template with the data
rendered_template = template.render(datalist=datalist)

# Write the rendered output to a file
with open(output_file_path, "w") as output_file:
    output_file.write(rendered_template)

print("Template rendered and written to file successfully.")
