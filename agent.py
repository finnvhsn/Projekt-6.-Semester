import logging
import traceback
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains import LLMChain, RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langgraph.graph import StateGraph, END

from config import CONFIG

# === Logging ===
logger = logging.getLogger(__name__)

# === LLM & Embeddings ===
llm = ChatOpenAI(
    model=CONFIG["llm_model"],
    temperature=0.1,
    api_key=CONFIG["openai_api_key"],
    base_url=CONFIG["openai_api_base"],
)

embedding_model = OpenAIEmbeddings(
    model=CONFIG["openai_embedding_model"],
    api_key=CONFIG["openai_api_key"],
    base_url=CONFIG["openai_api_base"],
)

# === Vectorstore / FAISS ===
FAISS_INDEX_PATH = "appdata/faiss_index"
vectorstore = FAISS.load_local(
    FAISS_INDEX_PATH, embedding_model, allow_dangerous_deserialization=True
)

# === QA Chain ===
retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

qa_chain = RetrievalQA.from_chain_type(
    llm=llm, retriever=retriever, return_source_documents=True
)

# === Antwortformatierung (Output Prompt) ===
response_formatting_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Du bist ein hilfreicher Chatbot und gibst strukturierte Informationen im Markdown-Format aus.
""",
        ),
        ("human", "Frage: {question}\nKontext: {context}"),
    ]
)
response_formatting_chain = LLMChain(llm=llm, prompt=response_formatting_prompt)

# === Bewertung ===
judge_prompt = PromptTemplate.from_template(
    """
Bewerte die folgende Antwort auf die gegebene Frage auf einer Skala von 0 bis 10.
Gib nur die Zahl als Antwort zurück.

Frage: {question}
Antwort: {answer}
"""
)
judge_chain = LLMChain(llm=llm, prompt=judge_prompt)


# === Graph QA Node ===
def run_vector_qa(state: dict) -> dict:
    question = state.get("question", "").strip()
    if not question:
        raise ValueError("Fehlende Frage im State.")

    logger.info(f"[VectorQA] Frage: {question}")
    try:
        result = qa_chain(question)
        answer = result["result"]
        context = "\n\n".join(doc.page_content for doc in result["source_documents"])

        formatted_answer = response_formatting_chain.run(
            question=question, context=context
        )
    except Exception as e:
        traceback.print_exc()
        logger.error(f"[VectorQA] Fehler: {e}")
        formatted_answer = "Entschuldigung, ich konnte deine Frage nicht beantworten."

    return {**state, "answer": formatted_answer}


# === Bewertung ===
def evaluate_answer(state: dict) -> dict:
    answer = state.get("answer", "").strip()
    question = state.get("question", "").strip()
    attempt = state.get("attempt", 1)

    score_str = judge_chain.run(question=question, answer=answer)
    try:
        score = max(0, min(int(score_str.strip()), 10))
    except ValueError:
        score = 0

    return {**state, "score": score, "attempt": attempt + 1}


def check_score(state: dict) -> str:
    attempt = state.get("attempt", 1)
    if state.get("score", 0) >= CONFIG["judge_threshold"]:
        return "end"
    elif attempt >= CONFIG["max_retries"]:
        return "end"
    return "retry"


# === Build Agent ===
def build_agent():
    builder = StateGraph(dict)
    builder.add_node("vector_qa", run_vector_qa)
    builder.add_node("judge", evaluate_answer)

    builder.set_entry_point("vector_qa")
    builder.add_edge("vector_qa", "judge")
    builder.add_conditional_edges(
        "judge", check_score, {"end": END, "retry": "vector_qa"}
    )

    return builder.compile()
