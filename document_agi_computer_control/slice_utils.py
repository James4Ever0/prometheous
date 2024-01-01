from itertools import islice
from beartype import beartype

@beartype
def split_dict_into_chunks(dictionary:dict, chunk_size:int):
    """
    Split a dictionary into chunks of specified size using itertools and a generator function.
    Args:
    - dictionary: The input dictionary to be split.
    - chunk_size: The size of each chunk.
    Returns:
    - A generator that yields dictionaries, each containing at most `chunk_size` items.
    """
    it = iter(dictionary.items())
    while True:
        chunk = dict(islice(it, chunk_size))
        if not chunk:
            break
        yield chunk

def test():
    # Example usage
    input_dict = {str(i): i for i in range(1000)}  # Example input dictionary
    chunked_dicts_generator = split_dict_into_chunks(input_dict, 100)  # Use the generator function to split the dictionary

    # Iterate through the generator to get the chunks
    for chunk in chunked_dicts_generator:
        print(str(chunk)[:10]+"...}")

if __name__ == "__main__":
    test()