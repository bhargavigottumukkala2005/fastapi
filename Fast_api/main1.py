from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
from blogs import router as blogs_router
from authentication import router as auth_router
from users import router as users_router

app = FastAPI()

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    logging.error(f"Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

app.include_router(blogs_router, prefix="/blog", tags=["Blogs"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/users", tags=["Users"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
