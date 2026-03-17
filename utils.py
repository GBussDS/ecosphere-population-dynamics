import logging
import os

def get_logger(name: str = "ecosphere", log_file: str = "logs/app.log", *, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if logger.handlers:
        logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    logger.propagate = False
    return logger