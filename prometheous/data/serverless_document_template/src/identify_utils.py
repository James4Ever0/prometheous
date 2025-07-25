from identify import identify
from beartype import beartype
import random  # this is magic

TEXT = "text"


@beartype
def get_language_id_from_filename(filename: str) -> str:
    language_id = ""
    tags = identify.tags_from_filename(filename)
    if TEXT in tags:
        candidates = [it for it in tags if it != TEXT]
        if candidates:
            language_id = random.choice(candidates)
    return language_id


def test():
    names = ["test.bash", "test.py", "test.js"]
    for name in names:
        language_id = get_language_id_from_filename(name)
        print(f"{name} -> {language_id}")


if __name__ == "__main__":
    test()
