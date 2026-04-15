import logging
import time

from sqlalchemy import text
from sqlmodel import Session

from app.core.db import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


def init() -> None:
    tries = 0
    while tries < max_tries:
        try:
            with Session(engine) as session:
                # Try to create session to check if DB is awake
                session.exec(text("SELECT 1"))
                return
        except Exception as e:
            logger.error(f"Attempt {tries + 1} failed: {e}")
            tries += 1
            time.sleep(wait_seconds)

    raise RuntimeError("Could not connect to database after maximum retries.")


def main() -> None:
    logger.info("Initializing service (waiting for DB)")
    init()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
