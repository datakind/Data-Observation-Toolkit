import logging
import argparse
import uuid
from utils.run_management import run_dot_tests
from utils.utils import setup_custom_logger


class DOTRunException(Exception):
    """Catch exceptions from an DOT run"""


logger = setup_custom_logger("./logs/run_everything.log", logging.INFO)

logger.info("Starting DOT test run")

# Set up arguments for parsing files
parser = argparse.ArgumentParser(description="Specify arguments")
parser.add_argument(
    "--project_id",
    action="store",
    required=True,
    help="DOT project name, eg Muso or Brac",
)
project_id = parser.parse_args().project_id

# Generate the run_id
run_id = run_id = uuid.uuid4()

# noinspection PyBroadException
try:
    run_dot_tests(project_id, logger, run_id)
    logger.info("Completed DOT run. Your results should in DB table dot.test_results.")
except DOTRunException:
    logging.exception("Fatal Error in Main Loop", exc_info=True)
