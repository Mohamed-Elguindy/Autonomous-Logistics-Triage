from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import health
# Placeholder for your router imports
# from routers import my_router 

# 1. Create the FastAPI app instance
app = FastAPI(title="Logistics AI API")
app.include_router(health.router)  

# 2. Add CORS middleware (allowing all origins for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # Allows all origins 
    allow_credentials=True,
    allow_methods=["*"],     # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],     # Allows all headers
)

# 3. Register your routers
# app.include_router(my_router.router, prefix="/api")

# 4. Add a root / endpoint to prevent 404s on the base URL
@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Logistics AI API is up and running!"
    }