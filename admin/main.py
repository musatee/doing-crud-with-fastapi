from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from routers import admin
from logger import logger

app = FastAPI() 

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

app.include_router(admin.router)