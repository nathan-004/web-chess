# ---------------------------------------------------------------------
# Affichage d'éléments en couleurs
# ---------------------------------------------------------------------

from functools import wraps
from collections import defaultdict
from time import time, sleep
from datetime import datetime

DEBUG = "debug"
INFO = "info"
WARNING = "warning"
ERROR = "error"

colors = {
    DEBUG: "BLUE",
    INFO: "GREEN",
    WARNING: "YELLOW",
    ERROR: "RED"
}

class bcolors:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    INVERT = '\033[7m'
    HIDDEN = '\033[8m'

def display(level):
    """Prépare l'affichage du message en initiant les variables current time"""
    def decorator(function):
        doc_template = f"""
        Affiche un élément dans le niveau {level.upper()}

        Parameters
        ----------
        time_counter:bool
            Si True, commence un timer qui s'affichera au prochain {level.upper()}
        """

        @wraps(function)
        def wrapper(cls, *args, time_counter=False):
            cls.messages_count[level] += 1

            if hasattr(cls, f"timer_{level}"):
                current_time = round(time() - getattr(cls, f"timer_{level}"), 4)
                delattr(cls, f"timer_{level}")
            else:
                current_time = datetime.today().strftime('%H:%M:%S')

            color = getattr(bcolors, colors[level]) if hasattr(bcolors, colors[level]) else bcolors.WHITE

            print(f"{color}{bcolors.BOLD}{current_time} | {bcolors.UNDERLINE}{level.upper()}{bcolors.RESET} {color}-", *args, bcolors.RESET)

            if time_counter:
                setattr(cls, f"timer_{level}", time())

            return None
        wrapper.__doc__ = doc_template.strip()
        return wrapper
    return decorator

class Logger:
    def __init__(self, min_level=DEBUG):
        """
        Parameters
        ----------
        min_level:str
            Configure le niveau minimal d'affichage
        """
        self.LEVELS = [DEBUG, INFO, WARNING, ERROR]

        try:
            self.min_level = self.LEVELS.index(min_level)
        except ValueError:
            self.min_level = 0

        self.messages_count = defaultdict(lambda : 0)

    @display(DEBUG)
    def debug(self, *arg, time_counter=False):
        pass

    @display(INFO)
    def info(self, *arg, time_counter=False):
        pass

    @display(WARNING)
    def warning(self, *arg, time_counter=False):
        pass

    @display(ERROR)
    def error(self, *arg, time_counter=False):
        pass

if __name__ == "__main__":
    a = Logger()
    a.error("test", time_counter=True)
    a.debug("test", time_counter=True)
    sleep(1.5)
    a.debug("Message 2")

    a.info("test", time_counter=True)
    sleep(1.5)
    a.info("Message 2")

    a.warning("test", time_counter=True)
    sleep(1.5)
    a.warning("Message 2")

    a.error("test", time_counter=False)
    sleep(1.5)
    a.error("Message 2", time_counter=True)