import logging
import os
import socket
from logging.handlers import RotatingFileHandler

"""
    game data
"""
# determines whether the power of the character is used before
# or after moving
permanents = {"pink"}
before = {"purple", "brown"}
after = {"black", "white", "red", "blue", "grey"}

# reunion of sets
colors = {"pink",
          "blue",
          "purple",
          "grey",
          "white",
          "black",
          "red",
          "brown"}

# ways between rooms
# rooms are numbered
# from right to left
# from bottom to top
# 0 ---> 9
passages = [{1, 4}, {0, 2}, {1, 3}, {2, 7}, {0, 5, 8},
            {4, 6}, {5, 7}, {3, 6, 9}, {4, 9}, {7, 8}]
# ways for the pink character
pink_passages = [{1, 4}, {0, 2, 5, 7}, {1, 3, 6}, {2, 7}, {0, 5, 8, 9},
                 {4, 6, 1, 8}, {5, 7, 2, 9}, {3, 6, 9, 1}, {4, 9, 5},
                 {7, 8, 4, 6}]

mandatory_powers = ["red", "blue", "grey"]

"""
    logging setup
    you can set the appropriate importance level of the data
    that are written to your logfiles.
"""
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")

# logger to file
def logger_to_file(filename, retry):
    filename_ext = filename + ".log"
    try:
        if os.path.exists(filename_ext):
            os.remove(filename_ext)
        file_handler = RotatingFileHandler(filename_ext, 'a', 1000000, 1)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except:
        if (retry):
            logger_to_file(filename + "_1", False)
        else:
            print("[ERROR] Failed to log to " + filename_ext + ".")

logger_to_file("./logs/game", True)