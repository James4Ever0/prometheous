from tempfile import TemporaryDirectory
from jinja2 import Template
from argparse import ArgumentParser
from beartype import beartype
import os
import subprocess

script_template_str = """
cd "{{diffpath}}"
fd --no-ignore --hidden | tree --fromfile -J > "{{tempdir}}/all_tree.json"
fd | tree --fromfile -J > "{{tempdir}}/selected_tree.json"
"""

# tree output in json
# load tree json, set selected & unselected properties
# count file size
# render tree json

script_template = Template(script_template_str)

RELATIVE_TEMP_DIR_SCRIPT_PATH = "script.sh"


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-d", "--diffpath", help="Path to visualize ignored files")
    args = parser.parse_args()
    return args.diffpath


@beartype
def render_script_template(diffpath: str, tempdir: str) -> str:
    return script_template.render(diffpath=diffpath, tempdir=tempdir)


with TemporaryDirectory() as tempdir:
    diffpath = parse_args()
    script_str = render_script_template(diffpath, tempdir)
    with open(os.path.join(tempdir, RELATIVE_TEMP_DIR_SCRIPT_PATH), "w") as f:
        f.write(script_str)
    subprocess.run(["bash", os.path.join(tempdir, RELATIVE_TEMP_DIR_SCRIPT_PATH)])
    full = f"{tempdir}/all_tree.json"
    selected = f"{tempdir}/selected_tree.json"
    basepath = os.path.abspath(diffpath)
    subprocess.run(
        [
            "python3.9",
            "display_tree_structure.py",
            "--full",
            full,
            "--selected",
            selected,
            "--basepath",
            basepath,
        ]
    )
