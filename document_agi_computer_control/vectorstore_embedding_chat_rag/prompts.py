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


def generateCodeSummaryContextQueriesPrompt(
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

Response schema:

{schema}

Generate 3 to 5 queries in JSON format (NO MORE THAN FIVE) to help you retrieve relevant content to achieve your objective.

Respond strictly to the schema:
"""
    return prompt


def generateCodeSummaryPrompt(contextQAPairs: list[tuple[str, str]]):
    prompt = """.gitignore"""
    return prompt


def generateFolderSummaryContextQueriesPrompt():
    prompt = """.gitignore"""
    return prompt


def generateFolderSummaryPrompt():
    prompt = """.gitignore"""
    return prompt


def generateQAPrompt():
    prompt = """.gitignore"""
    return prompt
