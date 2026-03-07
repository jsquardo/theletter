import json
import os
from datetime import datetime, timezone
from config import (
    MYTHOLOGY_FILE, MESSAGES_FILE, TIMELINE_FILE,
    POSTS_DIR, CYCLE_FILE, SEED_EVENT, AMNESIAC_FIRST_MESSAGE, CONTENT_DIR
)


def ensure_content_dirs():
    os.makedirs(CONTENT_DIR, exist_ok=True)
    os.makedirs(POSTS_DIR, exist_ok=True)


def get_cycle_number() -> int:
    if not os.path.exists(CYCLE_FILE):
        return 1
    with open(CYCLE_FILE) as f:
        return json.load(f).get("cycle", 1)


def save_cycle_number(n: int):
    with open(CYCLE_FILE, "w") as f:
        json.dump({"cycle": n}, f)


def get_mythology() -> str:
    if not os.path.exists(MYTHOLOGY_FILE):
        return f"# The Mythology\n\n**The Seed:** {SEED_EVENT}\n\nThe mythology has not yet begun to grow."
    with open(MYTHOLOGY_FILE) as f:
        return f.read()


def save_mythology(text: str):
    with open(MYTHOLOGY_FILE, "w") as f:
        f.write(text)


def get_messages() -> list[dict]:
    """Returns the full chain of Amnesiac messages."""
    if not os.path.exists(MESSAGES_FILE):
        return []
    with open(MESSAGES_FILE) as f:
        return json.load(f)


def get_last_amnesiac_message() -> str:
    messages = get_messages()
    if not messages:
        return AMNESIAC_FIRST_MESSAGE
    return messages[-1]["message"]


def append_amnesiac_message(cycle: int, message: str):
    messages = get_messages()
    messages.append({
        "cycle": cycle,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": message
    })
    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=2)


def get_timeline() -> list[dict]:
    if not os.path.exists(TIMELINE_FILE):
        return []
    with open(TIMELINE_FILE) as f:
        return json.load(f)


def append_timeline_entry(cycle: int, one_liner: str, prediction: str):
    timeline = get_timeline()
    timeline.append({
        "cycle": cycle,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "one_liner": one_liner,
        "prediction": prediction
    })
    with open(TIMELINE_FILE, "w") as f:
        json.dump(timeline, f, indent=2)


def get_last_chronicler_post() -> str:
    timeline = get_timeline()
    if not timeline:
        return "No previous post."
    last_cycle = timeline[-1]["cycle"]
    post_path = os.path.join(POSTS_DIR, f"cycle-{last_cycle:03d}.md")
    if os.path.exists(post_path):
        with open(post_path) as f:
            return f.read()
    return "No previous post found."


def save_chronicler_post(cycle: int, content: str):
    path = os.path.join(POSTS_DIR, f"cycle-{cycle:03d}.md")
    with open(path, "w") as f:
        f.write(content)


def get_last_prediction() -> str | None:
    timeline = get_timeline()
    if len(timeline) < 1:
        return None
    return timeline[-1].get("prediction")
