# from rich.tree import Tree
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label, Tree
from rich.text import Text
from textual.timer import Timer
from threading import Lock
import subprocess
# from tempfile import TemporaryDirectory
from jinja2 import Template
from argparse import ArgumentParser
from beartype import beartype

INTERVAL = 3

import asyncio

async def run_command(command:str):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode().strip(), stderr.decode().strip()

script_template_str = """
cd "{{diffpath}}"
fd --no-ignore --hidden | tree --fromfile > "{{tempdir}}/all_tree.txt"
fd | tree --fromfile > "{{tempdir}}/selected_tree.txt"
diff -y "{{tempdir}}/all_tree.txt" "{{tempdir}}/selected_tree.txt" > "{{tempdir}}/diff_tree.txt"
cat "{{tempdir}}/diff_tree.txt"
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


processingLock = Lock()


class VisualIgnoreApp(App):
    """A Textual app to visualize ignore files."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("e", "exit", "Exit")]
    timer: Timer

    def __init__(self, diffpath, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.i = 0
        self.header = Header()
        self.diffpath = diffpath
        self.treeview = Tree(".")
        self.treeview.root.expand()
        # self.treeview = RichLog(auto_scroll=False)
        self.footer = Footer()
        # self.mytree = Tree(".")
        self.label = Label(Text.assemble(("ETA:", "bold")), expand=True)
        self.label.styles.background = "red"
        # self.label.styles.border = ('solid','red')
        # self.label.styles.height = 3
        self.label.styles.height = 1
        # self.label.styles.dock = 'bottom'

    async def progress(self):
        locked = processingLock.acquire(blocking=False)
        if locked: # taking forever. bad.
            self.treeview.root.set_label(str(self.i))
            self.i+=1
            self.treeview.root.add("item", expand=True)
            # self.treeview.refresh()
            processingLock.release()


        # self.counter += 1

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        return [self.header, self.treeview, self.label, self.footer]

    def on_mount(self) -> None:
        self.timer = self.set_interval(INTERVAL, self.progress)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_exit(self):
        """An action to exit the app."""
        self.exit()


def main():
    diffpath = parse_args()
    app = VisualIgnoreApp(diffpath)
    app.run()


if __name__ == "__main__":
    main()
