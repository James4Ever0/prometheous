# from langchain.prompts import Prompt
# from langchain.chains import LLMChain
from contextlib import contextmanager

#from langchain.llms import OpenAI # TODO: use openlm
#from langchain_community.llms import OpenLLM as OpenAI

# TODO: use litellm instead of langchain openai
import litellm

import tiktoken

import os


def print_center(banner: str):
    print(banner.center(50, "="))


class LLM:
    """
    A class for running a Language Model Chain.
    """

    def __init__(self, prompt: str, temperature=0, gpt_4=False):
        """
        Initializes the LLM class.
        Args:
            prompt (PromptTemplate): The prompt template to use.
            temperature (int): The temperature to use for the model.
            gpt_4 (bool): Whether to use GPT-4 or Text-Davinci-003.
        Side Effects:
            Sets the class attributes.
        """
        self.prompt = prompt
        self.prompt_size = self.number_of_tokens(prompt)
        self.temperature = temperature
        self.gpt_4 = gpt_4
        self.model_name = os.environ.get(
            "PROMETHEOUS_MODEL_NAME", "gpt-4" if self.gpt_4 else "text-davinci-003"
        )
        self.max_tokens = int(
            os.environ.get("PROMETHEOUS_MAX_TOKENS", 4097 * 2 if self.gpt_4 else 4097)
        )
        self.show_init_config()

    def show_init_config(self):
        print_center("init params")
        print(f"Model: {self.model_name}")
        print(f"Max Tokens: {self.max_tokens}")
        print(f"Prompt Size: {self.prompt_size}")
        print(f"Temperature: {self.temperature}")
        print_center("init config")
        print(self.prompt)

    def run(self, query):
        """
        Runs the Language Model Chain.
        Args:
            code (str): The code to use for the chain.
            **kwargs (dict): Additional keyword arguments.
        Returns:
            str: The generated text.
        """
        messages = [
            dict(role="system", 
                content=self.prompt),
            dict(role="user",
                content=query)
            ]
        llm = litellm.completion(
            temperature=self.temperature,
            stream=True,
            model="openai/%s" % self.model_name,
            messages = messages
        )
        chunk_list = []
        print_center("query")
        print(query)
        print_center("response")
        for it in llm:
            delta= it['choices'][0]['delta']
            if hasattr(delta, "content"):
                chunk = getattr(delta, 'content')
                if chunk:
                    print(chunk, end="", flush=True)
                    chunk_list.append(chunk)
        print()

        result = "".join(chunk_list)
        return result

    def number_of_tokens(self, text):
        """
        Counts the number of tokens in a given text.
        Args:
            text (str): The text to count tokens for.
        Returns:
            int: The number of tokens in the text.
        """
        encoding = tiktoken.encoding_for_model("gpt-4")
        return len(encoding.encode(text, disallowed_special=()))


@contextmanager
def llm_context(prompt: str, temperature=0, gpt_4=False):
    model = LLM(prompt, temperature=temperature, gpt_4=gpt_4)
    try:
        yield model
    finally:
        del model
