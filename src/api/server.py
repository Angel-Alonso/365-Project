from fastapi import FastAPI
from src.api import generic_api
from starlette.middleware.cors import CORSMiddleware

description = """
Stock Portfolio API for paper-trading and portfolio tracking.
"""
tags_metadata = [
    {"name": "portfolio", "description": "View and manage a portfolio."},
    {"name": "accounts", "description": "Create and view user accounts."},
    {"name": "stocks", "description": "Market/stock lookup and holdings."},
]

app = FastAPI(
    title="Stock Portfolio Service",
    description=description,
    version="0.1.0",
    contact={
        "name": "CS365 Group Project",
    },
    openapi_tags=tags_metadata,
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generic_api.router)


@app.get("/")
async def root():
    return {"message": "Stock portfolio service is running."}
