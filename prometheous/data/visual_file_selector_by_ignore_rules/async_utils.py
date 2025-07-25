import asyncio

async def read_lines(stream:asyncio.StreamReader):
    while True:
        line = await stream.readline()
        # print("line")
        if not line:
            break
        else: 
            yield line

async def run_command(command:list[str]):
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        # stderr=asyncio.subprocess.PIPE
    )
    f = [it for it in read_lines(process.stdout)]
    # stderr_reader = asyncio.StreamReader()

    # Read lines from stdout and stderr concurrently
    # await asyncio.gather(
    #     read_lines(stdout_reader),
    #     read_lines(stderr_reader)
    # )
    # Wait for the process to complete
    await process.wait()

async def main():
    command = ["ls", "-l"]

    # Run the command asynchronously
    await run_command(command)

if __name__ == "__main__":
    # Run the event loop
    asyncio.run(main())
