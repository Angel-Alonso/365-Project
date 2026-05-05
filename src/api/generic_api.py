from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List

import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    tags=["portfolio", "stocks", "accounts"],
    dependencies=[Depends(auth.get_api_key)],
)


class Stock(BaseModel):
    name: str
    price: int = Field(ge=0, description="Price must be non-negative")


class StockOrder(BaseModel):
    name: str
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")

class PortfolioHolding(BaseModel):
    stock_id: int
    stock_name: str
    quantity: int
    price: int


class PortfolioResponse(BaseModel):
    portfolio_id: int
    user_id: int
    portfolio_name: str
    holdings: List[PortfolioHolding]

class BuyConfirmRequest(BaseModel):
    portfolio_id: int = Field(gt=0)
    stock_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


def get_portfolio(connection: sqlalchemy.Connection, portfolio_id: int) -> dict:
    portfolio_row = connection.execute(
        sqlalchemy.text(
            """
            SELECT portfolio_id, user_id, portfolio_name
            FROM portfolio_table
            WHERE portfolio_id = :portfolio_id
            """
        ),
        {"portfolio_id": portfolio_id},
    ).mappings().one_or_none()

    if portfolio_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"portfolio_id {portfolio_id} not found",
        )

    holdings_rows = connection.execute(
        sqlalchemy.text(
            """
            SELECT
                h.stock_id,
                a.stock_name,
                h.quantity,
                a.price
            FROM holdings_table h
            JOIN asset_table a ON a.stock_id = h.stock_id
            WHERE h.portfolio_id = :portfolio_id
            ORDER BY a.stock_name ASC
            """
        ),
        {"portfolio_id": portfolio_id},
    ).mappings().all()

    return {
        "portfolio_id": int(portfolio_row["portfolio_id"]),
        "user_id": int(portfolio_row["user_id"]),
        "portfolio_name": str(portfolio_row["portfolio_name"]),
        "holdings": [
            {
                "stock_id": int(r["stock_id"]),
                "stock_name": str(r["stock_name"]),
                "quantity": int(r["quantity"]),
                "price": int(r["price"]),
            }
            for r in holdings_rows
        ],
    }


@router.post("/orders/buy/confirm", response_model=PortfolioResponse, tags=["portfolio"])
def post_orders_buy_confirm(req: BuyConfirmRequest):
    """
    V1 "write" endpoint: adds shares to a portfolio and records a transaction.
    """
    with db.engine.begin() as connection:
        stock_row = connection.execute(
            sqlalchemy.text(
                """
                SELECT stock_id, stock_name
                FROM asset_table
                WHERE stock_id = :stock_id
                """
            ),
            {"stock_id": req.stock_id},
        ).mappings().one_or_none()

        if stock_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"stock_id {req.stock_id} not found",
            )

        portfolio_row = connection.execute(
            sqlalchemy.text(
                """
                SELECT portfolio_id, portfolio_name
                FROM portfolio_table
                WHERE portfolio_id = :portfolio_id
                """
            ),
            {"portfolio_id": req.portfolio_id},
        ).mappings().one_or_none()

        if portfolio_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"portfolio_id {req.portfolio_id} not found",
            )

        existing_holding = connection.execute(
            sqlalchemy.text(
                """
                SELECT holdings_id, quantity
                FROM holdings_table
                WHERE portfolio_id = :portfolio_id AND stock_id = :stock_id
                """
            ),
            {"portfolio_id": req.portfolio_id, "stock_id": req.stock_id},
        ).mappings().one_or_none()

        if existing_holding is None:
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO holdings_table (stock_id, portfolio_id, quantity)
                    VALUES (:stock_id, :portfolio_id, :quantity)
                    """
                ),
                {
                    "stock_id": req.stock_id,
                    "portfolio_id": req.portfolio_id,
                    "quantity": req.quantity,
                },
            )
        else:
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE holdings_table
                    SET quantity = quantity + :quantity
                    WHERE holdings_id = :holdings_id
                    """
                ),
                {"quantity": req.quantity, "holdings_id": existing_holding["holdings_id"]},
            )

        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO transaction_table (portfolio_id, stock_id, quantity, portfolio_name)
                VALUES (:portfolio_id, :stock_id, :quantity, :portfolio_name)
                """
            ),
            {
                "portfolio_id": req.portfolio_id,
                "stock_id": req.stock_id,
                "quantity": req.quantity,
                "portfolio_name": portfolio_row["portfolio_name"],
            },
        )

        return get_portfolio(connection, portfolio_id=req.portfolio_id)


@router.get("/portfolio", response_model=PortfolioResponse)
def get_portfolio_endpoint(portfolio_id: int = 1):
    """
    Return a single portfolio and its holdings.

    V1 simplification: defaults to portfolio_id=1 unless a different id is provided.
    """
    with db.engine.begin() as connection:
        return get_portfolio(connection, portfolio_id=portfolio_id)


@router.post("/stocks/deliver/{order_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["stocks"])
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

def create_account(
    name: str,
    email: str,
    ):
    # Check if account with email already exists in the database
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text("""
                SELECT * FROM user_table WHERE email = :email      
                """),
            
                {
                    "email": email
                }
            ,
        )
    print(
        f"Creating account with name: {name} and email: {email}"
    )

    # return true if account creation is successful, false otherwise
    return True


@router.post("/stocks/plan", response_model=List[StockOrder], tags=["stocks"])
def get_wholesale_purchase_plan(wholesale_catalog: List[Stock]):
    """
    Gets the plan for purchasing wholesale Stocks. The call passes in a catalog of available Stocks
    and the shop returns back which Stocks they'd like to purchase and how many.
    """
    print(f"Stock catalog: {wholesale_catalog}")

    return create_Stock_plan(
        wholesale_catalog=wholesale_catalog,
    )
