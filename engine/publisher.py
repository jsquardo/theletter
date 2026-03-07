import subprocess
import logging
from config import BASE_DIR

logger = logging.getLogger(__name__)


def trigger_site_rebuild():
    """
    Commits and pushes new content to git, which triggers a site rebuild.
    On DigitalOcean you can set this up as a git post-receive hook or
    a simple deploy script that Nginx serves after Astro builds.
    """
    try:
        repo_root = BASE_DIR + "/.."
        subprocess.run(["git", "add", "content/"], cwd=repo_root, check=True)
        subprocess.run(
            ["git", "commit", "-m", "chore: new cycle content"],
            cwd=repo_root, check=True
        )
        subprocess.run(["git", "push"], cwd=repo_root, check=True)
        logger.info("Content committed and pushed.")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Git push failed (may be nothing to commit): {e}")


def rebuild_astro_site():
    """
    Triggers an Astro build on the VPS.
    This runs `npm run build` inside the /site directory,
    then Nginx serves the dist/ folder.
    Call this after pushing content if you're doing local builds.
    """
    import os
    site_dir = os.path.join(BASE_DIR, "../site")
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=site_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            logger.info("Astro site rebuilt successfully.")
        else:
            logger.error(f"Astro build failed:\n{result.stderr}")
    except Exception as e:
        logger.error(f"Astro rebuild error: {e}")
