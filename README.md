# Prometheous

As before, our past is complete chaos because of inadequate knowledge and time for us to learn and develop.

Find tools for searching our code, build a semantic chatbot to serve us, for hacking, earning and creating.

## Environments and Models

[Pyenv](), [virtualenv]() and [conda]()/[mamba]() are used for environment management. To store model cache other than default `$HOME` (*nix) or `%USERPROFILE%` (Windows) you may need to change the home directory of current user. Complex solutions such as [overlayfs]() may apply but not preferred.

## Libraries

To install "compiled" packages like [hnswlib](https://github.com/nmslib/hnswlib/issues/479) on windows you may need mingw2 (follow the installation guide of privateGPT) or conda:

```
conda install -c conda-forge -n prometheous hnswlib
```

```
conda install libpython m2w64-toolchain -c msys2
```

---

You may want to use other models. There are currently [a lot models](https://github.com/eugeneyan/open-llms).

[Baichuan-13B](https://modelscope.cn/models/baichuan-inc/Baichuan-13B-Base)

[ChatGLM2-6B](https://github.com/THUDM/ChatGLM2-6B)

[VisCPM](https://github.com/OpenBMB/VisCPM)

[MPT-6B](https://huggingface.co/mosaicml/mpt-7b-instruct)

[WizardLM](https://github.com/nlpxucan/WizardLM): for coding

[Awesome-LLM-for-RecSys](https://github.com/CHIANGEL/Awesome-LLM-for-RecSys): for recommendation, may assist our "pyjom" project or help models to explore more

more ai related news/info can be found on [kuxai](https://www.kuxai.com/)

---

serve custom models with openai api compatible server:

[openai_server](https://github.com/shawwn/openai-server)

[llama-api-server](https://github.com/iaalm/llama-api-server)

---

[langchain](https://docs.langchain.com/docs/): the mother of all agent gpts

[autogpt](https://github.com/Significant-Gravitas/Auto-GPT): making gpt into agi

[promptify](https://github.com/promptslab/Promptify): structural gpt output

---

when using these retrieval based models, we need to provide more context. we need to know what the content is (more than filename), how it was retrieved (more than timestamp) and some brief. though these can be achieved by some genetic prompt generation algorithm.

[quivr](https://github.com/StanGirard/quivr)

[privateGPT](https://github.com/imartinez/privateGPT)

[localGPT](https://github.com/PromtEngineer/localGPT): inspired by privateGPT

[h2ogpt](https://github.com/h2oai/h2ogpt) with [alternatives](https://github.com/h2oai/h2ogpt/blob/main/docs/README_LangChain.md#what-is-h2ogpts-langchain-integration-like)

---

[haystack](https://github.com/deepset-ai/haystack): information retrieval toolkit

---

[autodoc](https://github.com/context-labs/autodoc): generate documentation in codebase

## Data sources

Bookmarks, important code repositories, text files within given suffix and sizes, notes, weblinks, even our actions and clipboards. The bot's actions need to be recorded by its demand.

## Objectives

Assist us by chatting, executing commands in sandboxes and receiving feedback from us and the internet (we may predefine some rewards)

The bot needs to learn and modify itself.

## Requirements

You might want a bigger SSD for storing all these data. It is simply overwhelming. Also for faster searching and training, you may want bigger RAM.
