# from fastapi import FastAPI
# from app.database import get_connection
 
# app = FastAPI()
 
 
# @app.get("/")
# def test_db_connection():
#     try:
#         conn = get_connection()
#         conn.close()
#         return {"message": "Database connected successfully!"}
#     except Exception as e:
#         return {"error": str(e)}


from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.routes import router

app = FastAPI()

app.include_router(router)


# Handle HTTPException globally

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        },
    )



# Handle unexpected exceptions


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "status_code": 500
        },
    )



