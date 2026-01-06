import logging

## Configure logging
file_handler = logging.FileHandler("app.log")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s : [MON] : %(message)s @ %(msecs)d mSec",
)

file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter("%(levelname)s : [MON] : %(message)s @ %(msecs)d mSec")
)
logging.getLogger().addHandler(file_handler)

"""
Logging Levels:
notset: 0
debug: 10
info: 20
warning: 30
error: 40
critical: 50
default level: warning
"""

logging.warning("This is a warning message")
logging.info("This is an info message")
logging.critical("This is a critical message")

a = 5
b = 2
y = 7

logging.info('Values of a: %s, b: %s, y: %s', bin(a), bin(b), bin(y))