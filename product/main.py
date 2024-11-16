from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from routers import product
from logger import logger
import os
from prometheus_client import Counter, Histogram

app = FastAPI() 

APP_VERSION = os.getenv("APP_VERSION", "default")
HTTP_REQUEST_TOTAL = Counter("http_requests_total", "Total number of HTTP requests made", ["endpoint", "method", "app_version"])
HTTP_REQUEST_DURATION = Histogram("http_requests_duration_seconds", "Total Processing time of a HTTP request", ["endpoint", "method", "app_version"])
HTTP_REQUEST_STATUS_CODE_TOTAL = Counter("http_requests_status_code_total", "Total count of all http requests status code", ["endpoint", "method", "status", "app_version"])

@app.middleware("http")
async def prometheus_metrics_generator(request: Request, call_next):
    endpoint = request.url.path 
    method = request.method 
    HTTP_REQUEST_TOTAL.labels(endpoint=endpoint, method=method, app_version=APP_VERSION).inc()

    with HTTP_REQUEST_DURATION.labels(endpoint=endpoint, method=method, app_version=APP_VERSION).time():
        response = await call_next(request)

    HTTP_REQUEST_STATUS_CODE_TOTAL.labels(endpoint=endpoint, method=method, status=response.status_code, app_version=APP_VERSION).inc()
    return response 

@app.exception_handler(HTTPException) 
async def exception_handler(request: Request, exc: HTTPException):
    status_codes = ["401", "400", "403"]
    db_conn_error = ["408"]
    if str(exc.status_code) in status_codes: 
        logger.warning(f"{exc.detail} (status: {exc.status_code})")
    elif str(exc.status_code) in db_conn_error: 
        logger.error(f"{exc}", exc_info=True)
    else: 
        logger.info(f"{exc.detail} (status: {exc.status_code})")
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail}) 

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"{exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred"}
    )

app.include_router(product.router)