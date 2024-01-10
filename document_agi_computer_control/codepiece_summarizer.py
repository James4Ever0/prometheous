from beartype import beartype
from llm import LLM


@beartype
def comment_summarizer(comments: list[str], word_limit: int = 30) -> str:
    summary_prompt = """You are a professional summarizer. You will be given a pair of comments and produce a concise summary.
"""
    summary_model = LLM(summary_prompt)

    def combine_comments(comment1: str, comment2: str):
        summary_query = f"""

{comment1}

{comment2}

Summary in {word_limit} words (do not be verbose, just summarize):
"""
        ret = summary_model.run(summary_query)
        return ret

    def recursive_combine(comments_list: list[str]):
        if len(comments_list) == 0:
            raise Exception("No comments to combine")
        elif len(comments_list) == 1:
            return comments_list[0]
        elif len(comments_list) % 2 == 0:
            combined = [
                combine_comments(comments_list[i], comments_list[i + 1])
                for i in range(0, len(comments_list), 2)
            ]
        else:
            combined = [
                combine_comments(comments_list[i], comments_list[i + 1])
                for i in range(0, len(comments_list) - 1, 2)
            ]
            combined += [comments_list[-1]]
        return recursive_combine(combined)

    summary = recursive_combine(comments)
    del summary_model
    return summary
