import logging
import argparse
from pprint import pprint

from agent import build_agent
from config import CONFIG

# === CLI Setup ===
parser = argparse.ArgumentParser(description="Frage einen RAG Agent.")
parser.add_argument("question", type=str, help="Die Frage an den Wissensgraphen")
parser.add_argument("--debug", action="store_true", help="Zeige Debug-Logs")
args = parser.parse_args()

# === Logging Setup ===
logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    format="%(levelname)s: %(message)s",
)

# === Agent Ausführung ===
agent = build_agent()
initial_state = {"question": args.question, "attempt": 1}


def invoke_with_retries(state):
    for i in range(CONFIG["max_retries"]):
        state["attempt"] = i + 1
        result = agent.invoke(state)
        if result.get("score", 0) >= CONFIG["judge_threshold"]:
            return result
    return result


final_result = invoke_with_retries(initial_state)
print("\nFinale Antwort:\n")
pprint(final_result.get("answer", "(keine Antwort)"))
