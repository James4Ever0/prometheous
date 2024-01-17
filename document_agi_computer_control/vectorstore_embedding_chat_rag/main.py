import sys, os

sys.path.append(os.path.dirname(__file__))
import prompts as P
import vectorindex as V

from llm import llm_context
from pydantic import BaseModel


class ReaderQuestions(BaseModel):
    questions: list[str]


class ContextQueries(BaseModel):
    queries: list[str]


prompt = P.generateFileSummaryContextQueriesPrompt(
    schema, contentType, projectName, filePath, summary
)
res = ...
contextQueries = ContextQueries.parse_raw(res)
contextQAPairs = []
for q in contextQueries:
    context = ...
    contextQAPairs.append((q, context))

prompt = P.generateFileSummaryPrompt(
    contentType, projectName, filePath, summary, contextQAPairs
)

documentSummary = ...  # file summary

prompt = P.generateFileQuestionsPrompt(
    schema, contentType, projectName, filePath, summary
)
res = ...
questions = ReaderQuestions.parse_raw(res)
print(questions)

QAPairs = []
for q in questions:
    context = ...
    prompt = P.generateFileAnswerPrompt(
        contentType,
        projectNAme,
        filePath,
        summary,
        q,
        context,
    )
    res = ...
    # assemble questions and answers.
    QAPairs.append(q, res)


# assemble document
documentQA = ["## Questions:\n"] + [
    f"{i+1}. {q}\n\n{a}\n" for i, (q, a) in enumerate(QAPairs)
]
documentQA = "\n".join(documentQA)

document = f"{documentSummary}\n---\n{documentQA}"

################################

prompt = P.generateFolderSummaryContextQueriesPrompt(
    schema,
    contextType,
    projectName,
    folderPath,
    summary,
)
res = ...
queries = ContextQueries.parse_raw(res)

contextQAPairs = []
for q in queries:
    context = ...
    contextQAPairs.append((q, context))


prompt = P.generateFolderSummaryPrompt(
    contentType, projectName, filePath, summary, contextQAPairs
)
document = ...

################################
last_chat_history = None
context = ...  # generate from first question
prompt = P.generateQAPrompt(contentType, projectName, question, context)
res = ...

prompt = P.generateRecentChatHistorySummaryPrompts(question, res)
recent_chat_history = ...

if last_chat_history is None:
    chat_history = recent_chat_history
else:
    prompt = P.generateChatHistorySummaryPrompt(last_chat_history, recent_chat_history)
    chat_history = ...
last_chat_history = chat_history

question = ...  # new question from user

prompt = P.generateCondensePrompt(chat_history, question)
standalone_question = ...
context = ...
