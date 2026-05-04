from dataclasses import dataclass
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List

import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/Stocks",
    tags=["Stocks"],
    dependencies=[Depends(auth.get_api_key)],
)


class Stock(BaseModel):
    name: str
    ml_per_Stock: int = Field(gt=0, description="Must be greater than 0")
    price: int = Field(ge=0, description="Price must be non-negative")
    quantity: int = Field(ge=0, description="Quantity must be non-negative")


class StockOrder(BaseModel):
    name: str
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")


@router.post("/deliver/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_deliver_stocks(stocks_delivered: List[Stock], order_id: int):
    """
    Processes Stocks delivered based on the provided order_id. order_id is a unique value representing
    a single delivery; the call is idempotent based on the order_id.
    """
    print(f"Stocks delivered: {stocks_delivered} order_id: {order_id}")

    pass


def create_Stock_plan(
    wholesale_catalog: List[Stock],
) -> List[StockOrder]:
    print(
        f"wholesale_catalog: {wholesale_catalog}"
    )

    # return an empty list
    return []


@router.post("/plan", response_model=List[StockOrder])
def get_wholesale_purchase_plan(wholesale_catalog: List[Stock]):
    """
    Gets the plan for purchasing wholesale Stocks. The call passes in a catalog of available Stocks
    and the shop returns back which Stocks they'd like to purchase and how many.
    """
    print(f"Stock catalog: {wholesale_catalog}")

    return create_Stock_plan(
        wholesale_catalog=wholesale_catalog,
    )
