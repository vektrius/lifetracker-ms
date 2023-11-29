from fastapi import FastAPI
from endpoints.auth import router as auth_routers

app = FastAPI()
app.include_router(auth_routers)
