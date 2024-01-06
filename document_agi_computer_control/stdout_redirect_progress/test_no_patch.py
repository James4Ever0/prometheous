import time

# for _ in range(200):
#     print(">>>> PROCESSING PROGRESS: 30%")

print("Hello, world")

SLEEP = 0.2
# time.sleep(SLEEP)
for i in range(100):
    print(
        f">>>> PROCESSING PROGRESS: {i}%"
    )  # problem is here. how to set flush=True this as default?
    print("hello world")
    time.sleep(SLEEP)
