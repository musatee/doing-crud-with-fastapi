import logging 
from fastapi import Request
logger = logging.getLogger(name="ecom")
logger.setLevel(logging.INFO)  # Set the logger level to INFO

file_handler = logging.FileHandler(filename="/app/log/product.log", mode="a", encoding="utf-8")

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M"
) 
file_handler.setFormatter(formatter)
logger.addHandler(file_handler) 

async def request_without_payload(request: Request): 
    if request.query_params: 
        logger.info(f"{request.method} {request.url.path}?{request.query_params}")
    else: 
        logger.info(f"{request.method} {request.url.path}") 

async def request_with_payload(request: Request):
    body = await request.body()
    logger.info(f"{request.method} {request.url.path}\n{body.decode('utf-8')}")
