from fastapi import FastAPI
import uvicorn

from app.routes.auth import auth_router
from app.routes.customer.orders import orders_router
from app.routes.provider.orders import provider_orders_router
from app.routes.provider.earnings import provider_earnings_router
from app.routes import marketplace_router

app = FastAPI(title='FREELANCER MARKETPLACE', description='welcome to FREELANCER MARKETPLACE')

app.include_router(marketplace_router)
app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(provider_orders_router)
app.include_router(provider_earnings_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)