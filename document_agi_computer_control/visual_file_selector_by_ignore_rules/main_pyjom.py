# this version is for pyjom, our ultimate challenge.
# TODO: type "R" to refresh the tree
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree, Label
from rich.text import Text
from textual.timer import Timer
from threading import Lock
# from tempfile import TemporaryDirectory
from jinja2 import Template
from argparse import ArgumentParser
from beartype import beartype
from datetime import datetime

import os
cached_paths = []
INTERVAL = 0.1

import asyncio
def format_timedelta(td):
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes}:{seconds}"

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

import aiofiles

def expand_parent(elem):
    elem.expand()
    if not elem.is_root:
        expand_parent(elem.parent)

async def read_file_and_get_line_count(filepath: str):
    filepath = os.path.abspath(filepath)
    if not os.path.exists(filepath):
        return -1
    if filepath in cached_paths:
        return -3
    try:
        lc = 0
        async with aiofiles.open(filepath, mode='r') as file:
            async for line in file:
                lc += 1
        return lc
    except:
        return -2

from collections import defaultdict
def patch_missing_files(path, basemap,expand=False):
# def patch_missing_files(path, basemap, color, expand=False, processor=lambda x: x):
    subpath, filename = dirsplit(path)
    # breakpoint()
    if basemap.get(path) is None:
        subtree, _ = patch_missing_files(subpath + "/", basemap)
        # renderable = Text.assemble((processor(filename), color))
        if path.endswith("/"):
            subsubtree = subtree.add(filename, expand=expand)
        else:
            subsubtree = subtree.add_leaf(filename)
        # subsubtree = subtree.add(processor(filename), expanded=expanded,style=color, guide_style=color)
        # print(filename)
        basemap[path] = subsubtree
        return subsubtree, filename
    else:
        return basemap.get(path), filename


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-d", "--diffpath", help="Path to visualize ignored files")
    args = parser.parse_args()
    return args.diffpath


def dirsplit(path):
    if path.endswith("/"):
        path = path[:-1]
    return os.path.split(path)

def iterate_parent_dirs(path):
    parts = path.split("/")
    for i in range(1, len(parts)):
        yield "/".join(parts[:i])+"/", parts[i-1]

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
        self.header = Header()
        self.diffpath = diffpath
        self.treeview = Tree(".")
        # do not expand, since this is slow.
        self.treeview.root.expand()
        self.footer = Footer()
        self.mymap = {"./":self.treeview.root}
        # self.counter = 0
        default_label = f"Lines: -/- Errors: -/- Last finished at: - Current Running: -"
        self.label = Label(Text.assemble((default_label, "bold")), expand=True)
        self.label.styles.background = "red"
        # self.label.styles.border = ('solid','red')
        # self.label.styles.height = 3
        self.label.styles.height = 1
        # self.label.styles.dock = 'bottom'
        self.line_count_map = defaultdict(int)
        self.line_count = 0
        self.previous_line_count = "-"
        self.error_count_map = defaultdict(int)
        self.error_count = 0
        self.previous_error_count = "-"
        self.previous_time = datetime.now()
        self.previous_time_formatted = "-"

    async def progress(self):
        locked = processingLock.acquire(blocking=False)
        if locked: # taking forever. bad.
            self.line_count = 0
            self.line_count_map = defaultdict(int)
            self.error_count_map = defaultdict(int)
            self.error_count = 0
            command = ["bash", "-c", f"cd '{self.diffpath}' && fd"]
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                # stderr=asyncio.subprocess.PIPE
            )
            banner_refresh_counter = 0
            while True:
                line = await process.stdout.readline() # type:ignore
                if not line: break
                decline = line.decode("utf-8").strip()
                if decline == "": break
                relpath = "./"+decline
                subtree, fname = patch_missing_files(relpath, self.mymap)
                if not relpath.endswith("/"):
                    linecount = await read_file_and_get_line_count(os.path.join(self.diffpath, relpath))
                    error =True
                    if linecount == 0:
                        label = "Empty"
                    elif linecount == -1:
                        label = "Missing"
                    elif linecount == -2:
                        label = "Error"
                    elif linecount == -3:
                        label = "Cached"
                        error = False
                    else:
                        label = f"{linecount} L"
                        self.line_count += linecount
                        self.line_count_map[relpath] = linecount
                        for parent_path, parent_name in iterate_parent_dirs(relpath): # ends with "/"
                            self.line_count_map[parent_path] += linecount
                            if parent_path not in self.error_count_map.keys():
                                self.mymap[parent_path].set_label(f"[{self.line_count_map[parent_path]} L] "+parent_name)
                        error = False
                    color = 'white'
                    if error:
                        color = "bold red"
                        expand_parent(subtree)
                        self.error_count += 1
                        self.error_count_map[label] += 1

                        for parent_path, parent_name in iterate_parent_dirs(relpath): # ends with "/"
                            self.error_count_map[parent_path] += 1
                            self.mymap[parent_path].set_label(Text.assemble((f"<{self.error_count_map[parent_path]} E> "+parent_name, "bold red")))
                    
                    subtree.set_label(Text.assemble(((f"[{label}]" if not error else f"<{label}>") +f" {fname}", color)))
                banner_refresh_counter += 1
                if banner_refresh_counter > 10:
                # if banner_refresh_counter > 10000:
                    banner_refresh_counter = 0
                    running = format_timedelta(datetime.now() - self.previous_time)
                    self.label.renderable = Text.assemble((f"Lines: {self.line_count}/{self.previous_line_count} Errors: {self.error_count}/{self.previous_line_count} Last finished at: {self.previous_time_formatted} Current Running: {running}", "bold"))
                    self.label.refresh()
            self.previous_line_count = self.line_count
            self.previous_error_count = self.error_count
            self.previous_time = datetime.now()
            self.previous_time_formatted = self.previous_time.strftime("%Y-%m-%d %H:%M:%S")
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
