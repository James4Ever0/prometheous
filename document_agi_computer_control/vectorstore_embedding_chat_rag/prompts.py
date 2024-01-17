FILE_RETRIEVER_OBJECTIVE_PROMPT = """Write a detailed technical explanation of what this code does.
Focus on the high-level purpose of the code and how it may be used in the larger project.
"""

FOLDER_RETRIEVER_OBJECTIVE_PROMPT = """Write a technical explanation of what the code in this file does and how it might fit into the larger project or work with other parts of the project.
Give examples of how this code might be used. Include code examples where appropriate.
"""

FILE_PROMPT = (
    f"""
{FILE_RETRIEVER_OBJECTIVE_PROMPT.strip()}
Include code examples where appropriate. Keep you response between 100 and 300 words.
DO NOT RETURN MORE THAN 300 WORDS.
Output should be in markdown format.
Do not just list the methods and classes in this file.
""",
)
FOLDER_PROMPT = (
    f"""
{FOLDER_RETRIEVER_OBJECTIVE_PROMPT.strip()}
Be concise. Include any information that may be relevant to a developer who is curious about this code.
Keep you response under 400 words. Output should be in markdown format.
Do not just list the files and folders in this folder.
""",
)

TARGET_AUDIENCE = "smart developer"


def generateFileSummaryContextQueriesPrompt(
    schema: str,
    contentType: str,
    projectName: str,
    filePath: str,
    summary: str,
    fileRetrieverObjectivePrompt=FILE_RETRIEVER_OBJECTIVE_PROMPT,
):
    prompt = f"""You are acting as a {contentType} documentation expert for a project called {projectName}.
Below is the summary from a file located at `{filePath}`. 

Your objective is:

{fileRetrieverObjectivePrompt}

File summary:

{summary}

Generate 3 to 5 queries (NO MORE THAN FIVE) to help you retrieve relevant content to achieve your objective.

Response schema:

{schema}

Respond strictly to the schema, in JSON format:
"""
    return prompt


def generateFileSummaryPrompt(
    contentType: str,
    projectName: str,
    filePath: str,
    summary: str,
    contextQAPairs: list[tuple[str, str]],
    filePrompt=FILE_PROMPT,
):
    context = "\n".join(
        [f"Context to query '{query}':\n{answer}\n" for query, answer in contextQAPairs]
    )
    prompt = f"""You are acting as a {contentType} documentation expert for a project called {projectName}.
Below is the summary and relevant context of {contentType} from a file located at `{filePath}`. 
{filePrompt}
Do not say "this file is a part of the {projectName} project".

File summary:

{summary}

{context}

Response in Markdown:
"""
    return prompt


def generateFileQuestionsPrompt(
    schema: str,
    contentType: str,
    projectName: str,
    targetAudience: str,
    filePath: str,
    summary: str,
):
    prompt = f"""You are acting as a {contentType} documentation expert for a project called {projectName}.
Below is the {contentType} from a file located at `{filePath}`. 
What are 3 questions that a {targetAudience} might have about this {contentType}?

File summary:

{summary}

Response schema:

{schema}

Respond strictly to the schema, in JSON format:
"""
    return prompt


def generateFileAnswerPrompt(
    contentType: str,
    projectName: str,
    targetAudience: str,
    filePath: str,
    summary: str,
    question: str,
    context: str,
):
    prompt = f"""You are acting as a {contentType} documentation expert for a project called {projectName}.
Below is the {contentType} from a file located at `{filePath}`.

File summary:

{summary}

This is a question that a {targetAudience} might have about this {contentType}:

{question}

Context about the question:

{context}

Answer the question in 1-2 sentences. Output should be in markdown format.

Respond in markdown format:
"""
    return prompt


def generateFolderSummaryContextQueriesPrompt(
    schema: str,
    contentType: str,
    projectName: str,
    folderPath: str,
    summary: str,
    folderRetrieverObjectivePrompt=FOLDER_RETRIEVER_OBJECTIVE_PROMPT,
):
    prompt = f"""You are acting as a {contentType} documentation expert for a project called {projectName}.
You are currently documenting the folder located at `{folderPath}`. 
    
Your objective is:

{folderRetrieverObjectivePrompt}

Folder summary:

{summary}

Generate 3 to 5 queries (NO MORE THAN FIVE) to help you retrieve relevant content to achieve your objective.

Response schema:

{schema}

Respond strictly to the schema, in JSON format:
"""
    return prompt


def generateFolderSummaryPrompt(
    contentType: str,
    projectName: str,
    filePath: str,
    summary: str,
    contextQAPairs: list[tuple[str, str]],
    folderPrompt=FOLDER_PROMPT,
):
    context = "\n".join(
        [f"Context to query '{query}':\n{answer}\n" for query, answer in contextQAPairs]
    )
    prompt = f"""You are acting as a {contentType} documentation expert for a project called {projectName}.
Below is the summary and relevant context of {contentType} from a folder located at `{filePath}`. 
{folderPrompt}
Do not say "this file is a part of the {projectName} project".

Folder summary:

{summary}

{context}

Response in Markdown:
"""
    return prompt


def generateCondensePrompt(chat_history:str, question:str): # in order to query context for next question, we generate another query'
    prompt = f"""Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:
"""
    return prompt


def generateQAPrompt(contentType:str, projectName:str,targetAudience:str,question:str, context:str):
    prompt = f"""You are an AI assistant for a software project called {projectName}. You are trained on all the {contentType} that makes up this project.
You are given the following extracted parts of a technical summary of files in a {contentType} and a question. 
Provide a conversational answer with hyperlinks back to GitHub.
You should only use hyperlinks that are explicitly listed in the context. Do NOT make up a hyperlink that is not listed.
Include lots of {contentType} examples and links to the {contentType} examples, where appropriate.
Assume the reader is a {targetAudience} but is not deeply familiar with {projectName}.
Assume the reader does not know anything about how the project is strucuted or which folders/files are provided in the context.
Do not reference the context in your answer. Instead use the context to inform your answer.
If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
If the question is not about the {projectName}, politely inform them that you are tuned to only answer questions about the {projectName}.
Your answer should be at least 100 words and no more than 300 words.
Do not include information that is not directly relevant to the question, even if the context includes it.
Always include a list of reference links from the context. Links should ONLY come from the context.

Question: {question}

Context:
{context}

Answer in Markdown:
"""
    return prompt
