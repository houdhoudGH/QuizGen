import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv


from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import SystemMessage
from langchain_classic.chains import LLMChain, SequentialChain
from langchain_core.prompts import PromptTemplate

load_dotenv()
KEY = os.getenv("HUGGING_FACE_API_KEY")


llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.3-70B-Instruct",  # newer, well-supported
    task="conversational",
    provider="auto",
    max_new_tokens=512,
)
chat = ChatHuggingFace(llm=llm, verbose=True)

system_msg = SystemMessage(
    content="/no_think Answer very briefly and do not explain your reasoning."
)

TEMPLATE_QUIZ_NEW = """\
{system_msg}
Context: {text}
Your task is to write exactly {number} multiple-choice questions based on the above content. The questions should be appropriate for {subject} students and written in a {difficulty} difficulty.
Return ONLY a JSON object matching the format shown in RESPONSE_JSON below. Do not include any extra explanation.
### RESPONSE_JSON
{response_json}
"""

quiz_prompt_new = PromptTemplate(
    input_variables=[
        "system_msg",
        "text",
        "number",
        "subject",
        "difficulty",
        "response_json",
    ],
    template=TEMPLATE_QUIZ_NEW,
)

quiz_chain = LLMChain(llm=chat, prompt=quiz_prompt_new, output_key="quiz")

TEMPLATE_REVIEW_NEW = """\
{system_msg}
Below is a quiz for {subject} students. Review its difficulty in no more than 50 words. If any question is not suitable, rewrite only the problem parts in a suitable difficulty.
Quiz:
{quiz}
"""

review_prompt_new = PromptTemplate(
    input_variables=["system_msg", "subject", "quiz"],
    template=TEMPLATE_REVIEW_NEW,
)

review_chain = LLMChain(llm=chat, prompt=review_prompt_new, output_key="review")

combined_chain = SequentialChain(
    chains=[quiz_chain, review_chain],
    input_variables=[
        "system_msg",
        "text",
        "number",
        "subject",
        "difficulty",
        "response_json",
    ],
    output_variables=["quiz", "review"],
    verbose=True,
)
