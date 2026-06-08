from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.middleware.auth import JWTAuthMiddleware
from app.api.v1 import auth, products, orders, clients, webhooks, admin

app = FastAPI(
    title="Más Pizzas API",
    description="API para la gestión de la pizzería y bot de WhatsApp",
    version="1.0.0"
)

# CORS configuration
origins = [
    settings.frontend_url,
    "http://localhost:5173", # Local dev frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Añadir middleware estricto de JWT Auth
app.add_middleware(JWTAuthMiddleware)

@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.app_env}

# Register Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(clients.router, prefix="/api/v1/clients", tags=["Clients"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
