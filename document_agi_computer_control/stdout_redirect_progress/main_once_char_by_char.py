# redirect stdout to some buffered output window, and show a progress bar below.

# differentiate between "cached" file and "processed" file
# you may retrieve "cached" file processing time from somewhere else.
# if failed to retrieve stored processing time, use average one instead.

# TODO: add this to recursive document generator.
# TODO: before that, just use a simple timer for producing total processing time and count files, in size, count and lines.

import asyncio
import parse
from textual.app import App, ComposeResult
from textual.widgets import Log, ProgressBar

# import textual
from threading import Lock

lock = Lock()

INTERVAL = 0.1


import shutil
import textwrap


def wrap_text(text):
    # Get the terminal width
    terminal_width, _ = shutil.get_terminal_size()
    tw = terminal_width - 8
    if tw < 8:
        tw = terminal_width

    wrapped_text = textwrap.fill(text, width=tw)
    return wrapped_text.rstrip()


class VisualIgnoreApp(App):
    """A Textual app to visualize"""

    def __init__(self, error_container: list, program_args: list[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mylog = Log(max_lines=10000)
        self.prog = ProgressBar()
        self.program_args = program_args
        self.error_container = error_container
        # self.prog.styles.width="100%"
        self.prog.styles.align_horizontal = "center"
        # self.prog.update(total=100, progress=0)

    async def progress(self):
        locked = lock.acquire(blocking=False)
        if locked:
            self.mylog.clear()
            await main(self.mylog, self.prog, self.error_container, self.program_args)
            self.exit()
            # lock.release()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        return [self.mylog, self.prog]

    def on_mount(self) -> None:
        # await self.progress()
        # self.exit()
        self.timer = self.set_interval(INTERVAL, self.progress)


# mylog = textual.widgets.Log(max_lines = ...)
# mybar = textual.widgets.ProgressBar(total=100, show_eta=...)
# mylog.write()

# TODO: run the document processor in a separate process.
# TODO: parse the data received from the separate process, line by line.
# TODO: if the data starts with something special, we would read and parse the whole line and update progress
# this is sick.
# cmd = ["python3.9", "test.py"]
# cmd = ["stdbuf", "-o0", "-e0", "bash", "-c", "python3.9 test.py 2>&1"]
cmd = ["stdbuf", "-o0", "-e0", "python3.9", "test.py"]
# cmd = ["bash", "-c", "python3.9 test.py 2>&1"]

line_format = "PROCESSING PROGRESS: {progress:d}/{total:d}"


def parse_line(line: str):
    parsed = parse.parse(line_format, line)
    if parsed:
        return parsed["progress"], parsed["total"]
    return None


async def read_stderr(proc, error_container):
    while True:
        # mbyte = await proc.stderr.readline()  # type:ignore
        mbyte = await proc.stderr.read(100)  # type:ignore
        error_container.append(mbyte)
        if mbyte == b"":
            break


async def read_stdout(proc, mylog, prog):
    line_position = 0
    line_content = ""
    # mtime = []
    init = False
    while True:
        # mbyte = await proc.stdout.readline()  # type:ignore
        # mbyte = await proc.stdout.read(20)  # type:ignore
        mbyte = await proc.stdout.read(1)  # type:ignore
        if mbyte == b"":
            break
        else:
            # line_content = mbyte.decode("utf-8").rstrip()
            # # print(content)
            # mylog.write_line(wrap_text(line_content))
            # mylog.refresh()
            # continue
            if mbyte == b"\n":
                line_position = 0
                mylog.write("\n")
                # try to parse line content.
                if line_content.startswith(">>>> "):
                    #     mtime.append(datetime.datetime.now())
                    mline = line_content[5:]
                    ret = parse_line(mline)
                    if ret is not None:
                        if not init:
                            prog.update(total=ret[1], progress=0)
                            init = True
                        steps = ret[0] - prog.progress
                        if steps > 0:
                            prog.advance(steps)
                    mylog.write("parsed progress? " + str(ret)+"\n")
                line_content = ""
            else:
                line_position +=1
                line_content += mbyte.decode("utf-8")
                mylog.write( mbyte.decode("utf-8"))
            # mylog.write_line(line_content)


async def main(mylog, prog, error_container, program_args):
    # proc = await asyncio.create_subprocess_shell(
    proc = await asyncio.create_subprocess_exec(
        *program_args,  # stdout=asyncio.subprocess.PIPE
        # UNBUFFERED FLAG: -u
        # "bash -c 'python3.9 -u test_no_patch.py 2>&1'",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
        # "python3.9 -u test_no_patch.py", stdout=asyncio.subprocess.PIPE
        # "python3.9 test.py", stdout=asyncio.subprocess.PIPE
    )  # how to handle the stderr now? we may merge the altogether.
    t1 = asyncio.create_task(read_stdout(proc, mylog, prog))
    t2 = asyncio.create_task(read_stderr(proc, error_container))
    # task1 = asyncio.create_task(read_stdout(proc, mylog))
    # task2 = asyncio.create_task(read_stderr(proc))
    await asyncio.gather(t1, t2)
    # await asyncio.gather(task1, task2)

    retcode = await proc.wait()
    error_container.insert(0, retcode)
    if retcode != 0:
        print(f"Error: subprocess returned {retcode}")
    else:
        print(f"Success: subprocess returned {retcode}")


import sys
import time
import humanize

if __name__ == "__main__":
    split_ind = sys.argv.index("--")
    args = sys.argv[split_ind + 1 :]
    if "python" in args or "python3.9" in args:
        assert "-u" in args, "Python script must be run with -u flag (unbuffered)"
    error_container = []
    app = VisualIgnoreApp(error_container, args)
    start_time = time.time()
    app.run()
    end_time = time.time()
    total_time = end_time - start_time
    # breakpoint()
    retcode = error_container[0]
    if retcode != 0:
        error_info = b"\n".join(error_container[1:])
        sys.stderr.buffer.write(error_info)
        raise Exception(
            "\n".join(
                ["Error: subprocess returned", str(retcode)]
                + ["total time:", humanize.naturaltime(total_time).split(" ago")[0]]
            )
        )
    else:
        print("exit successfully")
        print("total time:", humanize.naturaltime(total_time).split(" ago")[0])
