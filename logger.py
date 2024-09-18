import logging 

logger = logging.getLogger(name="ecom")
logger.setLevel(logging.INFO)  # Set the logger level to INFO

file_handler = logging.FileHandler(filename="app.log", mode="a", encoding="utf-8")

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M"
) 
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)