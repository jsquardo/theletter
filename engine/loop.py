import logging
import time
from datetime import datetime, timezone

import state
import agents
import publisher
from config import CYCLE_INTERVAL_HOURS, SEED_EVENT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("../content/engine.log")
    ]
)
logger = logging.getLogger(__name__)


def run_cycle():
    state.ensure_content_dirs()
    cycle = state.get_cycle_number()
    logger.info(f"=== CYCLE {cycle} STARTING at {datetime.now(timezone.utc).isoformat()} ===")

    # --- Load current state ---
    mythology       = state.get_mythology()
    last_message    = state.get_last_amnesiac_message()
    message_chain   = state.get_messages()
    last_post       = state.get_last_chronicler_post()
    last_prediction = state.get_last_prediction()

    logger.info(f"Amnesiac wakes with message: \"{last_message}\"")

    # --- Step 1: Amnesiac wakes and acts ---
    amnesiac_p1 = agents.run_amnesiac_part1(cycle, last_message)
    logger.info(f"Amnesiac action: {amnesiac_p1['action']}")
    logger.info(f"Amnesiac question: {amnesiac_p1['question']}")

    # --- Step 2: Myth Maker observes and responds ---
    myth_result = agents.run_myth_maker(
        cycle,
        mythology,
        amnesiac_p1["action"],
        amnesiac_p1["question"]
    )
    logger.info(f"Myth Maker answer: {myth_result['answer'][:100]}...")

    # --- Step 3: Amnesiac writes its farewell message ---
    new_message = agents.run_amnesiac_part2(
        cycle,
        last_message,
        amnesiac_p1["action"],
        myth_result["answer"]
    )
    logger.info(f"Amnesiac's message to next self: \"{new_message}\"")

    # --- Step 4: Save updated state ---
    state.save_mythology(myth_result["mythology"])
    state.append_amnesiac_message(cycle, new_message)

    # --- Step 5: Chronicler writes and publishes ---
    chronicle = agents.run_chronicler(
        cycle=cycle,
        seed=SEED_EVENT,
        amnesiac_action=amnesiac_p1["action"],
        amnesiac_question=amnesiac_p1["question"],
        myth_answer=myth_result["answer"],
        new_message=new_message,
        mythology=myth_result["mythology"],
        message_chain=state.get_messages(),
        last_post=last_post,
        last_prediction=last_prediction
    )

    state.save_chronicler_post(cycle, chronicle["post"])
    state.append_timeline_entry(cycle, chronicle["one_liner"], chronicle["prediction"])

    logger.info(f"Chronicler post saved: {chronicle['title']}")
    logger.info(f"One-liner: {chronicle['one_liner']}")
    logger.info(f"Prediction: {chronicle['prediction']}")

    # --- Step 6: Publish ---
    publisher.rebuild_astro_site()

    # --- Step 7: Advance cycle ---
    state.save_cycle_number(cycle + 1)
    logger.info(f"=== CYCLE {cycle} COMPLETE ===\n")


def main():
    logger.info("Engine starting up...")
    logger.info(f"Seed event: \"{SEED_EVENT}\"")
    logger.info(f"Cycle interval: {CYCLE_INTERVAL_HOURS} hours")

    while True:
        try:
            run_cycle()
        except Exception as e:
            logger.error(f"Cycle failed with error: {e}", exc_info=True)
            logger.info("Will retry next cycle.")

        sleep_seconds = CYCLE_INTERVAL_HOURS * 3600
        logger.info(f"Sleeping for {CYCLE_INTERVAL_HOURS} hours...")
        time.sleep(sleep_seconds)


if __name__ == "__main__":
    main()
