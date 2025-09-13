from fastapi import FastAPI
import uvicorn

from app.routes import marketplace_router

app = FastAPI(title='FREELANCER MARKETPLACE',description='welcome to FREELANCER MARKETPLACE')

app.include_router(marketplace_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=9126, reload=True)