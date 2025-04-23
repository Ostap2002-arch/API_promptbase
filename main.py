from fastapi import FastAPI

import routers

app = FastAPI()

app.include_router(routers.router, prefix="/api")