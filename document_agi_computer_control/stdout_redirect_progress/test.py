import builtins
import copy

myprint = copy.copy(builtins.print)


def custom_print(*args, **kwargs):
    if "flush" not in kwargs:
        kwargs["flush"] = True
    myprint(*args, **kwargs)


# Override the built-in print function with the custom function
builtins.print = custom_print

# Now, when you use print, it will default to flush=True

import time

# for _ in range(200):
#     print(">>>> PROCESSING PROGRESS: 30%")

print("Hello, world")

SLEEP = 0.2
# time.sleep(SLEEP)
for i in range(10000):
    print(
        f">>>> PROCESSING PROGRESS: {i}%"
    )  # problem is here. how to set flush=True this as default?
    print("hello world")
    time.sleep(SLEEP)
