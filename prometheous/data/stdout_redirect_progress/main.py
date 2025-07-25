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


class VisualIgnoreApp(App):
    """A Textual app to visualize"""

    def __init__(self, error_container: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mylog = Log()
        self.prog = ProgressBar()
        self.error_container = error_container
        # self.prog.styles.width="100%"
        self.prog.styles.align_horizontal = "center"
        self.prog.update(total=100, progress=0)

    async def progress(self):
        locked = lock.acquire(blocking=False)
        if locked:
            self.mylog.clear()
            await main(self.mylog, self.prog, self.error_container)
            await asyncio.sleep(2)
            lock.release()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        return [self.mylog, self.prog]

    def on_mount(self) -> None:
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

line_format = "PROCESSING PROGRESS: {progress:d}%"


def parse_line(line: str):
    parsed = parse.parse(line_format, line)
    if parsed:
        return parsed["progress"]
    return None


async def read_stderr(proc, error_container):
    while True:
        mbyte = await proc.stderr.readline()  # type:ignore
        # mbyte = await proc.stderr.read(1)  # type:ignore
        error_container.append(mbyte.decode())
        if mbyte == b"":
            break


async def read_stdout(proc, mylog, prog):
    # line_position = 0
    # line_content = ""
    # mtime = []
    while True:
        mbyte = await proc.stdout.readline()  # type:ignore
        # mbyte = await proc.stdout.read(20)  # type:ignore
        # mbyte = await proc.stdout.read(1)  # type:ignore
        if mbyte == b"":
            break
        else:
            line_content = mbyte.decode("utf-8").rstrip()
            # print(content)
            mylog.write_line(line_content)
            # mylog.refresh()
            # continue
            # if mbyte == b"\n":
            #     line_position = 0
            #     # try to parse line content.
            #     mylog.write("\n")
            # mylog.write_line(line_content)
            if line_content.startswith(">>>> "):
                #     mtime.append(datetime.datetime.now())
                mline = line_content[5:]
                ret = parse_line(mline)
                if ret is not None:
                    steps = ret - prog.progress
                    if steps > 0:
                        prog.advance(steps)
                mylog.write_line("parsed progress? " + str(ret))


async def main(mylog, prog, error_container):
    proc = await asyncio.create_subprocess_shell(
        # proc = await asyncio.create_subprocess_exec(
        # *cmd, stdout=asyncio.subprocess.PIPE
        # UNBUFFERED FLAG: -u
        "bash -c 'python3.9 -u test_no_patch.py 2>&1'",
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


if __name__ == "__main__":
    error_container = []
    app = VisualIgnoreApp(error_container)
    app.run()
    # breakpoint()
    retcode = error_container[0]
    if retcode != 0:
        raise Exception(
            "\n".join(
                ["Error: subprocess returned", str(retcode)] + error_container[1:]
            )
        )
