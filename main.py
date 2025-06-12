import logging
import os
import requests
from pprint import pprint
from dotenv import load_dotenv
from agent import build_agent
from config import CONFIG

# === Load .env ===
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("OPENAI_API_BASE")

# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

# === Step 1: Fetch Available Models from IONOS ===
def fetch_available_models():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    try:
        res = requests.get(f"{API_BASE}/models", headers=headers)
        res.raise_for_status()
        models = res.json().get("data", [])
        return [m["id"] for m in models if "Instruct" in m["id"]]
    except Exception as e:
        print("❌ Fehler beim Laden der Modelle:", e)
        return []

# === Step 2: Select a Model ===
def choose_model():
    models = fetch_available_models()
    if not models:
        print("Keine Modelle verfügbar.")
        exit(1)

    print("\n🧠 Verfügbare Modelle:")
    for idx, model_id in enumerate(models, 1):
        print(f"{idx}. {model_id}")
    try:
        choice = int(input("\nWähle ein Modell (1–{}): ".format(len(models))))
        return models[choice - 1]
    except (ValueError, IndexError):
        print("Ungültige Auswahl.")
        exit(1)

# === Step 3: Ask Questions in a Loop ===
def chat_loop(agent):
    while True:
        question = input("\n💬 Deine Frage (oder 'exit'): ").strip()
        if question.lower() in {"exit", "quit"}:
            print("👋 Auf Wiedersehen!")
            break

        state = {"question": question, "attempt": 1}
        result = invoke_with_retries(agent, state)
        print("\n✅ Antwort:\n")
        pprint(result.get("answer", "(keine Antwort)"))

# === Step 4: Retry logic from original code ===
def invoke_with_retries(agent, state):
    for i in range(CONFIG["max_retries"]):
        state["attempt"] = i + 1
        result = agent.invoke(state)
        if result.get("score", 0) >= CONFIG["judge_threshold"]:
            return result
    return result

# === MAIN ===
if __name__ == "__main__":
    selected_model = choose_model()
    CONFIG["llm_model"] = selected_model  # override model dynamically
    print(f"\n🔧 Modell '{selected_model}' wird verwendet.\n")
    agent = build_agent()
    chat_loop(agent)
