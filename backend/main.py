from fastapi import FastAPI
from routers import user, upload_image


app = FastAPI()

# app.include_router(common_routes.router)
app.include_router(user.app, prefix="", tags=["users"])
# app.include_router(upload_image.app, prefix="", tags=["upload"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=80)