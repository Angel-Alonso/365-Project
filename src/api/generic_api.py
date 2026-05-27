from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List

import sqlalchemy
from src.api import auth
from src import database as db
from sqlalchemy.exc import SQLAlchemyError
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


class StockResponse(BaseModel):
    ticker: str
    company_name: str
    price: int = Field(ge=0, description="Price must be non-negative")


class AccountResponse(BaseModel):
    user_id: int
    name: str
    email: str
    cash_balance: int


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


class TradeRequest(BaseModel):
    portfolio_id: int = Field(gt=0)
    ticker: str
    quantity: int = Field(gt=0)

class HoldingPerformance(BaseModel):
    ticker: str
    quantity: int
    average_cost: float
    current_price: int
    potential_gains_or_losses: float 
    return_percentage: float

class PortfolioPerformance(BaseModel):
    portfolio_id: int
    total_invested: float
    current_value: float
    total_return_percentage: float
    holdings_performance: List[HoldingPerformance]

class CreateAccountRequest(BaseModel):
    name: str
    email: str



STARTING_CASH_BALANCE = 10000
DEFAULT_MARKET_DATA = {
    "AAPL": {"stock_id": 1, "company_name": "Apple Inc.", "price": 100},
    "MSFT": {"stock_id": 2, "company_name": "Microsoft Corporation", "price": 200},
    "TSLA": {"stock_id": 3, "company_name": "Tesla Inc.", "price": 250},
}

@router.post("/accounts/create", tags=["accounts"])
def post_create_account(req: CreateAccountRequest):
    """
    Create a new user account with the provided name and email.
    """
    with db.engine.begin() as connection:
        existing_account = connection.execute(
            sqlalchemy.text(
                """
                SELECT id
                FROM user_table
                WHERE email = :email
                """ ),
            {"email": req.email},
        ).mappings().one_or_none()
        if existing_account is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Account with email {req.email} already exists",
            )
        user_row = connection.execute(
            sqlalchemy.text(  
                """
                INSERT INTO user_table (name, email)
                VALUES (:name, :email)
                RETURNING id
                """            ),
            {"name": req.name, "email": req.email},
        ).mappings().one()
        protfolio_row = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO portfolio_table (user_id, portfolio_name)
                VALUES (:user_id, :portfolio_name)
                RETURNING portfolio_id
                """
            ),
            {"user_id": user_row["id"], "portfolio_name": f"{req.name}'s Portfolio"},
        ).mappings().one()
    return {
        "message": "Account created successfully",
        "user_id": int(user_row["id"]),
        "portfolio_id": int(protfolio_row["portfolio_id"])
    }

def normalize_ticker(ticker: str) -> str:
    return ticker.strip().upper()


def get_company_name(ticker: str) -> str:
    return DEFAULT_MARKET_DATA.get(ticker, {}).get("company_name", ticker)


def table_exists(connection: sqlalchemy.Connection, table_name: str) -> bool:
    row = connection.execute(
        sqlalchemy.text("SELECT to_regclass(:table_name) IS NOT NULL AS exists"),
        {"table_name": table_name},
    ).mappings().one()

    return bool(row["exists"])


def get_stock_from_asset_table(connection: sqlalchemy.Connection, ticker: str) -> dict | None:
    row = connection.execute(
        sqlalchemy.text(
            """
            SELECT stock_id, stock_name, price
            FROM asset_table
            WHERE UPPER(stock_name) = :ticker
            """
        ),
        {"ticker": ticker},
    ).mappings().one_or_none()

    if row is None:
        return None

    return {
        "stock_id": int(row["stock_id"]),
        "ticker": str(row["stock_name"]).upper(),
        "company_name": get_company_name(str(row["stock_name"]).upper()),
        "price": int(row["price"]),
    }


def get_stock_from_price_tables(connection: sqlalchemy.Connection, ticker: str) -> dict | None:
    if not table_exists(connection, "stocks") or not table_exists(connection, "stock_prices"):
        return None

    row = connection.execute(
        sqlalchemy.text(
            """
            SELECT s.stock_id, s.ticker, s.company_name, sp.price
            FROM stocks s
            JOIN stock_prices sp ON s.ticker = sp.ticker
            WHERE UPPER(s.ticker) = :ticker
            ORDER BY sp.recorded_at DESC
            LIMIT 1
            """
        ),
        {"ticker": ticker},
    ).mappings().one_or_none()

    if row is None:
        return None

    return {
        "stock_id": int(row["stock_id"]),
        "ticker": str(row["ticker"]).upper(),
        "company_name": str(row["company_name"]),
        "price": int(row["price"]),
    }


def get_stock_by_ticker(connection: sqlalchemy.Connection, ticker: str) -> dict:
    normalized_ticker = normalize_ticker(ticker)
    stock = get_stock_from_asset_table(connection, normalized_ticker)

    if stock is None:
        stock = get_stock_from_price_tables(connection, normalized_ticker)

    if stock is None and normalized_ticker in DEFAULT_MARKET_DATA:
        default_stock = DEFAULT_MARKET_DATA[normalized_ticker]
        stock = {
            "stock_id": int(default_stock["stock_id"]),
            "ticker": normalized_ticker,
            "company_name": str(default_stock["company_name"]),
            "price": int(default_stock["price"]),
        }

    if stock is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ticker {normalized_ticker} not found",
        )

    return stock


def get_stock_by_id(connection: sqlalchemy.Connection, stock_id: int) -> dict:
    row = connection.execute(
        sqlalchemy.text(
            """
            SELECT stock_id, stock_name, price
            FROM asset_table
            WHERE stock_id = :stock_id
            """
        ),
        {"stock_id": stock_id},
    ).mappings().one_or_none()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"stock_id {stock_id} not found",
        )

    ticker = str(row["stock_name"]).upper()
    return {
        "stock_id": int(row["stock_id"]),
        "ticker": ticker,
        "company_name": get_company_name(ticker),
        "price": int(row["price"]),
    }


def get_cash_balance(connection: sqlalchemy.Connection, portfolio_id: int) -> int:
    row = connection.execute(
        sqlalchemy.text(
            """
            SELECT COALESCE(SUM(t.quantity * a.price), 0) AS total_spent
            FROM transaction_table t
            JOIN asset_table a ON a.stock_id = t.stock_id
            WHERE t.portfolio_id = :portfolio_id
            """
        ),
        {"portfolio_id": portfolio_id},
    ).mappings().one()

    return STARTING_CASH_BALANCE - int(row["total_spent"])


def ensure_portfolio_exists(connection: sqlalchemy.Connection, portfolio_id: int) -> dict:
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

    return dict(portfolio_row)


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


@router.get("/market", response_model=List[StockResponse], tags=["stocks"])
def get_market():
    """
    Return the current stock market list used by the sample workflows.
    """
    try:
        with db.engine.begin() as connection:
            market_by_ticker = {}

            asset_rows = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT stock_id, stock_name, price
                    FROM asset_table
                    ORDER BY stock_id ASC
                    """
                )
            ).mappings().all()

            for row in asset_rows:
                ticker = str(row["stock_name"]).upper()
                market_by_ticker[ticker] = {
                    "ticker": ticker,
                    "company_name": get_company_name(ticker),
                    "price": int(row["price"]),
                }

            if table_exists(connection, "stocks") and table_exists(connection, "stock_prices"):
                stock_rows = connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT DISTINCT ON (s.ticker)
                            s.ticker,
                            s.company_name,
                            sp.price
                        FROM stocks s
                        JOIN stock_prices sp ON s.ticker = sp.ticker
                        ORDER BY s.ticker, sp.recorded_at DESC
                        """
                    )
                ).mappings().all()

                for row in stock_rows:
                    ticker = str(row["ticker"]).upper()
                    market_by_ticker[ticker] = {
                        "ticker": ticker,
                        "company_name": str(row["company_name"]),
                        "price": int(row["price"]),
                    }

            for ticker, default_stock in DEFAULT_MARKET_DATA.items():
                market_by_ticker.setdefault(
                    ticker,
                    {
                        "ticker": ticker,
                        "company_name": str(default_stock["company_name"]),
                        "price": int(default_stock["price"]),
                    },
                )

    except SQLAlchemyError as e:
        raise HTTPException(status_code=503, detail="Database unavailable") from e

    return [market_by_ticker[ticker] for ticker in sorted(market_by_ticker)]


@router.get("/stocks/{ticker}", response_model=StockResponse, tags=["stocks"])
def get_stock(ticker: str):
    """
    Return the latest known price for one stock ticker.
    """
    with db.engine.begin() as connection:
        stock = get_stock_by_ticker(connection, ticker)

    return {
        "ticker": stock["ticker"],
        "company_name": stock["company_name"],
        "price": stock["price"],
    }


@router.get("/account", response_model=AccountResponse, tags=["accounts"])
def get_account(user_id: int = 1):
    """
    Return account information and computed cash balance.
    """
    with db.engine.begin() as connection:
        account_row = connection.execute(
            sqlalchemy.text(
                """
                SELECT u.id, u.name, u.email, p.portfolio_id
                FROM user_table u
                LEFT JOIN portfolio_table p ON p.user_id = u.id
                WHERE u.id = :user_id
                ORDER BY p.portfolio_id ASC
                LIMIT 1
                """
            ),
            {"user_id": user_id},
        ).mappings().one_or_none()

        if account_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id {user_id} not found",
            )

        portfolio_id = account_row["portfolio_id"]
        cash_balance = (
            get_cash_balance(connection, int(portfolio_id))
            if portfolio_id is not None
            else STARTING_CASH_BALANCE
        )

        return {
            "user_id": int(account_row["id"]),
            "name": str(account_row["name"]),
            "email": str(account_row["email"]),
            "cash_balance": cash_balance,
        }


@router.post("/orders/buy/request", tags=["portfolio"])
def post_orders_buy_request(req: TradeRequest):
    """
    Preview whether a buy order can be placed.
    """
    with db.engine.begin() as connection:
        ensure_portfolio_exists(connection, req.portfolio_id)
        stock = get_stock_by_ticker(connection, req.ticker)
        estimated_total = stock["price"] * req.quantity
        cash_balance = get_cash_balance(connection, req.portfolio_id)

        return {
            "portfolio_id": req.portfolio_id,
            "ticker": stock["ticker"],
            "company_name": stock["company_name"],
            "quantity": req.quantity,
            "price": stock["price"],
            "estimated_total": estimated_total,
            "can_purchase": cash_balance >= estimated_total,
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
                SELECT stock_id, stock_name, price
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
                INSERT INTO transaction_table (portfolio_id, stock_id, quantity, portfolio_name,price_at_purchase)
                VALUES (:portfolio_id, :stock_id, :quantity, :portfolio_name, :price_at_purchase)
                """
            ),
            {
                "portfolio_id": req.portfolio_id,
                "stock_id": req.stock_id,
                "quantity": req.quantity,
                "portfolio_name": portfolio_row["portfolio_name"],
                "price_at_purchase": stock_row["price"],
            },
        )

        return get_portfolio(connection, portfolio_id=req.portfolio_id)


@router.post("/orders/sell/request", tags=["portfolio"])
def post_orders_sell_request(req: TradeRequest):
    """
    Preview whether a sell order can be placed.
    """
    with db.engine.begin() as connection:
        ensure_portfolio_exists(connection, req.portfolio_id)
        stock = get_stock_by_ticker(connection, req.ticker)
        holding_row = connection.execute(
            sqlalchemy.text(
                """
                SELECT quantity
                FROM holdings_table
                WHERE portfolio_id = :portfolio_id AND stock_id = :stock_id
                """
            ),
            {"portfolio_id": req.portfolio_id, "stock_id": stock["stock_id"]},
        ).mappings().one_or_none()

        current_quantity = int(holding_row["quantity"]) if holding_row is not None else 0
        estimated_total = stock["price"] * req.quantity

        return {
            "portfolio_id": req.portfolio_id,
            "ticker": stock["ticker"],
            "company_name": stock["company_name"],
            "quantity": req.quantity,
            "price": stock["price"],
            "estimated_total": estimated_total,
            "can_sell": current_quantity >= req.quantity,
        }


@router.post("/orders/sell/confirm", response_model=PortfolioResponse, tags=["portfolio"])
def post_orders_sell_confirm(req: BuyConfirmRequest):
    """
    Remove shares from a portfolio and record the sell transaction.
    """
    with db.engine.begin() as connection:
        portfolio_row = ensure_portfolio_exists(connection, req.portfolio_id)
        get_stock_by_id(connection, req.stock_id)

        holding_row = connection.execute(
            sqlalchemy.text(
                """
                SELECT holdings_id, quantity
                FROM holdings_table
                WHERE portfolio_id = :portfolio_id AND stock_id = :stock_id
                """
            ),
            {"portfolio_id": req.portfolio_id, "stock_id": req.stock_id},
        ).mappings().one_or_none()

        if holding_row is None or int(holding_row["quantity"]) < req.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough shares to sell",
            )

        remaining_quantity = int(holding_row["quantity"]) - req.quantity

        if remaining_quantity == 0:
            connection.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM holdings_table
                    WHERE holdings_id = :holdings_id
                    """
                ),
                {"holdings_id": holding_row["holdings_id"]},
            )
        else:
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE holdings_table
                    SET quantity = :quantity
                    WHERE holdings_id = :holdings_id
                    """
                ),
                {
                    "quantity": remaining_quantity,
                    "holdings_id": holding_row["holdings_id"],
                },
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
                "quantity": -req.quantity,
                "portfolio_name": portfolio_row["portfolio_name"],
            },
        )

        return get_portfolio(connection, portfolio_id=req.portfolio_id)


@router.get("/orders", tags=["portfolio"])
def get_orders(portfolio_id: int = 1):
    """
    Return transaction history for a portfolio.
    """
    with db.engine.begin() as connection:
        ensure_portfolio_exists(connection, portfolio_id)
        order_rows = connection.execute(
            sqlalchemy.text(
                """
                SELECT
                    t.transaction_id,
                    t.portfolio_id,
                    t.stock_id,
                    a.stock_name,
                    t.quantity,
                    a.price
                FROM transaction_table t
                JOIN asset_table a ON a.stock_id = t.stock_id
                WHERE t.portfolio_id = :portfolio_id
                ORDER BY t.transaction_id ASC
                """
            ),
            {"portfolio_id": portfolio_id},
        ).mappings().all()

        return [
            {
                "transaction_id": int(row["transaction_id"]),
                "portfolio_id": int(row["portfolio_id"]),
                "stock_id": int(row["stock_id"]),
                "ticker": str(row["stock_name"]).upper(),
                "transaction_type": "SELL" if int(row["quantity"]) < 0 else "BUY",
                "quantity": abs(int(row["quantity"])),
                "price": int(row["price"]),
                "total": abs(int(row["quantity"])) * int(row["price"]),
            }
            for row in order_rows
        ]


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




@router.get("/portfolio/{portfolio_id}/performance", response_model=PortfolioPerformance, tags=["portfolio"])
def get_portfolio_performance(portfolio_id: int):
    """Return the performance of a portfolio including total invested, current value, total return percentage, and performance of each holding.
    """
    with db.engine.begin() as connection:
        ensure_portfolio_exists(connection, portfolio_id)
        

        history = connection.execute(sqlalchemy.text(
            """
            SELECT 
            t.stock_id,
            sum(t.quantity *t.price_at_purchase) as total_invested,
            sum(t.quantity) as total_shares
            FROM transaction_table t
            JOIN asset_table a ON a.stock_id = t.stock_id
            WHERE t.portfolio_id = :portfolio_id
            and t.quantity > 0
            GROUP BY t.stock_id
            """),
            {"portfolio_id": portfolio_id},
        ).mappings().all()

        current_holdings = connection.execute(sqlalchemy.text(
            """
            SELECT 
            h.stock_id,
            a.stock_name,
            h.quantity,
            a.price
            FROM holdings_table h
            JOIN asset_table a ON a.stock_id = h.stock_id
            WHERE h.portfolio_id = :portfolio_id
            """),
            {"portfolio_id": portfolio_id},
        ).mappings().all()

        history_by_stock_id = {row["stock_id"]: row for row in history}
        holding_list = []
        current_value = 0.0
        total_invested = 0.0

        for row in current_holdings:
            stock_id = row["stock_id"]
            hist = history_by_stock_id.get(stock_id)
            if hist is None:
                continue
            avg_cost = hist["total_invested"] / hist["total_shares"]
            potential_gain_or_loss = (row["price"] - avg_cost) * row["quantity"]
            return_percentage = (potential_gain_or_loss / hist["total_invested"]) * 100 if hist["total_invested"] > 0 else 0
            total_invested += hist["total_invested"]
            current_value += row["price"] * row["quantity"]
            

            holding_list.append({
                
                "ticker": str(row["stock_name"]).upper(),
                "quantity": int(row["quantity"]),
                "average_cost": avg_cost,
                "current_price": int(row["price"]),
                "potential_gains_or_losses": round(potential_gain_or_loss, 2),
                "return_percentage": round(return_percentage, 2),
                })
        
        total_return_percentage = ((current_value - total_invested) / total_invested) * 100 if total_invested > 0 else 0
        
        return {
            "portfolio_id": portfolio_id,
            "total_invested": round(total_invested, 2),
            "current_value": round(current_value, 2),
            "total_return_percentage": round(total_return_percentage, 2),
            "holdings_performance": holding_list,
            }


      
       


