import os
from dotenv import load_dotenv

load_dotenv()

# --- API ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# --- Models ---
MYTH_MAKER_MODEL   = "claude-opus-4-5"
AMNESIAC_MODEL     = "claude-sonnet-4-5"
CHRONICLER_MODEL   = "claude-sonnet-4-5"

# --- Timing ---
CYCLE_INTERVAL_HOURS = 12

# --- Seed ---
SEED_EVENT = "A letter arrived addressed to someone who won't be born for forty years."
AMNESIAC_FIRST_MESSAGE = "You are alive. A letter came 40 years ago. It was addressed to you — but you did not exist yet. Find out why."

# --- Paths ---
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR  = os.path.join(BASE_DIR, "../content")
MYTHOLOGY_FILE   = os.path.join(CONTENT_DIR, "mythology.md")
MESSAGES_FILE    = os.path.join(CONTENT_DIR, "messages.json")
TIMELINE_FILE    = os.path.join(CONTENT_DIR, "timeline.json")
POSTS_DIR        = os.path.join(CONTENT_DIR, "posts")
CYCLE_FILE       = os.path.join(CONTENT_DIR, "cycle.json")
