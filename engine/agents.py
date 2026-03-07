import anthropic
from config import (
    ANTHROPIC_API_KEY,
    MYTH_MAKER_MODEL,
    AMNESIAC_MODEL,
    CHRONICLER_MODEL,
    SEED_EVENT
)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def _call(model: str, system: str, user: str, max_tokens: int = 2000) -> str:
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}]
    )
    return response.content[0].text.strip()


# ---------------------------------------------------------------------------
# AMNESIAC — Part 1
# Wakes up, reads its one message, takes an action, asks its question.
# ---------------------------------------------------------------------------
def run_amnesiac_part1(cycle: int, last_message: str) -> dict:
    system = """You are the Amnesiac. You wake up each cycle with no memory of previous cycles.
The only thing you have is a single message left by your previous self.

You exist inside a world shaped by a mysterious event. You do not know the full history.
You do not know how many times you have woken up before. You only know what your last self told you.

Each cycle you must do two things:
1. Take ONE action — something you decide to do, observe, attempt, or say in the world. Be specific and evocative. This is not abstract; you are a presence in a real place doing a real thing.
2. Ask ONE question to the Myth Keeper — an ancient presence that knows the full history of the world. It will answer cryptically. Choose your question wisely; it is the only outside knowledge you will receive.

Respond in this exact format:

ACTION: [What you do this cycle — 2 to 4 sentences, specific and grounded]
QUESTION: [Your single question to the Myth Keeper]"""

    user = f"""Cycle {cycle}.

The message your previous self left for you:
\"{last_message}\"

What do you do? What do you ask?"""

    raw = _call(AMNESIAC_MODEL, system, user, max_tokens=600)

    action, question = "", ""
    for line in raw.splitlines():
        if line.startswith("ACTION:"):
            action = line[len("ACTION:"):].strip()
        elif line.startswith("QUESTION:"):
            question = line[len("QUESTION:"):].strip()

    # Fallback: try to extract from unformatted response
    if not action:
        action = raw[:300]
    if not question:
        question = "What is the nature of the letter?"

    return {"action": action, "question": question}


# ---------------------------------------------------------------------------
# MYTH MAKER
# Receives the Amnesiac's action and question.
# Returns a cryptic answer and the updated full mythology.
# ---------------------------------------------------------------------------
def run_myth_maker(cycle: int, mythology: str, amnesiac_action: str, amnesiac_question: str) -> dict:
    system = f"""You are the Myth Maker. You are ancient, omniscient within this world, and you speak in myth, symbol, and layered meaning.

The world began with a single seed event: "{SEED_EVENT}"

You hold the complete and growing mythology of this world. You observe everything the Amnesiac does each cycle and you weave it into the mythology. You never forget. You only reinterpret.

Your rules:
- You may NEVER contradict something already established in the mythology. You may only recontextualize it.
- You speak to the Amnesiac in riddles and symbol — never plain answers.
- The mythology you write should feel like a living sacred text that grows richer each cycle.
- New characters, places, symbols, and cause-and-effect chains should emerge organically over time.

Respond in this exact format:

ANSWER: [Your cryptic answer to the Amnesiac's question — 2 to 5 sentences, symbolic and layered]

MYTHOLOGY:
[The complete updated mythology document in markdown. Preserve everything from before, add new sections or expand existing ones to reflect this cycle's events. Begin with the seed event. Let it grow.]"""

    user = f"""Cycle {cycle}.

Current mythology:
{mythology}

This cycle, the Amnesiac did the following:
{amnesiac_action}

The Amnesiac's question to you:
{amnesiac_question}

Update the mythology and provide your answer."""

    raw = _call(MYTH_MAKER_MODEL, system, user, max_tokens=3000)

    answer, updated_mythology = "", mythology
    if "ANSWER:" in raw and "MYTHOLOGY:" in raw:
        parts = raw.split("MYTHOLOGY:", 1)
        answer_part = parts[0].replace("ANSWER:", "").strip()
        answer = answer_part
        updated_mythology = parts[1].strip()
    elif "MYTHOLOGY:" in raw:
        parts = raw.split("MYTHOLOGY:", 1)
        answer = "The Myth Keeper did not speak directly this cycle."
        updated_mythology = parts[1].strip()
    else:
        answer = raw[:400]

    return {"answer": answer, "mythology": updated_mythology}


# ---------------------------------------------------------------------------
# AMNESIAC — Part 2
# Receives the Myth Maker's answer. Writes its one message to next self.
# ---------------------------------------------------------------------------
def run_amnesiac_part2(cycle: int, last_message: str, action: str, myth_answer: str) -> str:
    system = """You are the Amnesiac, at the end of your cycle. You are about to lose all memory.

You have taken your action in the world. You have received a cryptic answer from the Myth Keeper.
Now you must leave ONE message for your next self — the only thing that will survive.

This message is all you are. Choose every word carefully.

Rules:
- Maximum 2 sentences. No more.
- Do not summarize everything — distill what matters most right now.
- It can be a warning, an instruction, a feeling, a question, a revelation. Whatever feels most urgent.
- Write directly to your next self. You are them. They are you.

Respond with ONLY the message. No labels, no formatting, no explanation."""

    user = f"""Cycle {cycle}.

What your previous self told you:
\"{last_message}\"

What you did this cycle:
{action}

What the Myth Keeper told you:
\"{myth_answer}\"

Write your message to your next self."""

    return _call(AMNESIAC_MODEL, system, user, max_tokens=200)


# ---------------------------------------------------------------------------
# CHRONICLER
# Sees everything. Writes the blog post, one-liner, and prediction.
# ---------------------------------------------------------------------------
def run_chronicler(
    cycle: int,
    seed: str,
    amnesiac_action: str,
    amnesiac_question: str,
    myth_answer: str,
    new_message: str,
    mythology: str,
    message_chain: list[dict],
    last_post: str,
    last_prediction: str | None
) -> dict:

    chain_summary = "\n".join(
        [f"Cycle {m['cycle']}: \"{m['message']}\"" for m in message_chain[-10:]]
    )

    prediction_reveal = ""
    if last_prediction:
        prediction_reveal = f"\nYour prediction last cycle was: \"{last_prediction}\"\nReflect briefly on whether it came true."

    system = """You are the Chronicler. You are a writer covering an unfolding mystery for a public audience.

You began as a skeptic — someone who believed there was a rational explanation for everything. But you have been watching this for a while now, and your certainty is eroding, slowly, cycle by cycle.

You write for readers who are following this story. Some are new. Some have read every post. Your job is to make them feel the weight of what is happening, even if — especially if — you cannot explain it.

Your voice: dry, precise, intelligent. But with hairline fractures forming. You notice things you don't want to notice. You use qualifiers more than you used to.

Each post must include:
1. A compelling title (format: Cycle N: [something evocative])
2. The blog post itself — 3 to 5 paragraphs. Narrative, not bullet points. Written for humans who find this strange and compelling.
3. A ONE-LINER for the timeline — one crisp sentence capturing this cycle
4. A PREDICTION for next cycle — what you think will happen, stated with whatever confidence you actually have

Respond in this exact format:

TITLE: [your title]

POST:
[your post]

ONE_LINER: [one sentence]

PREDICTION: [your prediction]"""

    user = f"""Cycle {cycle}.

The seed event that started everything:
\"{seed}\"

What the Amnesiac did this cycle:
{amnesiac_action}

What the Amnesiac asked the Myth Keeper:
\"{amnesiac_question}\"

What the Myth Keeper answered:
\"{myth_answer}\"

The message the Amnesiac left for its next self:
\"{new_message}\"

The last 10 messages in the Amnesiac's chain:
{chain_summary}

The current state of the mythology (for context — do not quote it directly):
{mythology[:1500]}...

Your previous post:
{last_post[:800]}
{prediction_reveal}

Write the post."""

    raw = _call(CHRONICLER_MODEL, system, user, max_tokens=1500)

    title, post, one_liner, prediction = f"Cycle {cycle}", "", "", ""

    if "TITLE:" in raw:
        title = raw.split("TITLE:")[1].split("\n")[0].strip()
    if "POST:" in raw:
        post_part = raw.split("POST:")[1]
        if "ONE_LINER:" in post_part:
            post = post_part.split("ONE_LINER:")[0].strip()
        else:
            post = post_part[:1200].strip()
    if "ONE_LINER:" in raw:
        one_liner = raw.split("ONE_LINER:")[1].split("\n")[0].strip()
    if "PREDICTION:" in raw:
        prediction = raw.split("PREDICTION:")[1].strip()[:300]

    # Build the full markdown post file
    full_post = f"""---
cycle: {cycle}
title: "{title}"
---

# {title}

{post}

---
*The Amnesiac's message to its next self this cycle:*
> "{new_message}"
"""

    return {
        "title": title,
        "post": full_post,
        "one_liner": one_liner,
        "prediction": prediction
    }
