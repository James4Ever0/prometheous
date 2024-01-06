import time

# for _ in range(200):
#     print(">>>> PROCESSING PROGRESS: 30%")

print("Hello, world")

SLEEP = 0.1
# SLEEP = 0.01
# SLEEP = 1
# time.sleep(SLEEP)
total = 100
for i in range(total):
    print(
        f">>>> PROCESSING PROGRESS: {i+1}/{total}"
    )  # problem is here. how to set flush=True this as default?
    print("hello world")
    time.sleep(SLEEP)
