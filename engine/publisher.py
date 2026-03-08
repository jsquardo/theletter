import subprocess
import logging
import os
from config import BASE_DIR

logger = logging.getLogger(__name__)

REPO_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
SITE_DIR = os.path.join(REPO_ROOT, "site")


def commit_content(cycle: int):
    """
    Stages all content/ changes and commits them with a cycle-stamped message.
    This gives you a full git history of every cycle's output.
    """
    try:
        # Stage everything in content/
        subprocess.run(
            ["git", "add", "content/"], cwd=REPO_ROOT, check=True, capture_output=True
        )

        # Check if there's actually anything to commit
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_ROOT)

        if result.returncode == 0:
            logger.info(f"Cycle {cycle}: nothing new to commit in content/.")
            return

        subprocess.run(
            ["git", "commit", "-m", f"cycle {cycle}: mythology, messages, post"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
        logger.info(f"Cycle {cycle}: content committed to git.")

    except subprocess.CalledProcessError as e:
        logger.warning(f"Git commit failed: {e}")


def push_to_remote():
    """
    Pushes committed content to the remote (optional).
    Useful if you want the git history mirrored to GitHub as a backup.
    Safe to skip if you only care about local history on the VPS.
    """
    try:
        subprocess.run(
            ["git", "push"], cwd=REPO_ROOT, check=True, capture_output=True, timeout=30
        )
        logger.info("Pushed to remote.")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Git push failed (remote may not be configured): {e}")
    except subprocess.TimeoutExpired:
        logger.warning("Git push timed out — skipping.")


def rebuild_astro_site():
    """
    Triggers an Astro build on the VPS.
    Nginx serves the resulting dist/ folder.
    """
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=SITE_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            logger.info("Astro site rebuilt successfully.")
        else:
            logger.error(f"Astro build failed:\n{result.stderr}")
    except Exception as e:
        logger.error(f"Astro rebuild error: {e}")
