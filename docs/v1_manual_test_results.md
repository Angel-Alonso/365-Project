# Example workflow
Buy Stock + View Portfolio (V1 Minimal Workflow)

1. Call POST /orders/buy/confirm with a portfolio_id, stock_id, and quantity to add shares to a portfolio.
2. Call GET /portfolio?portfolio_id=<id> to verify the holdings updated.

# Testing results
1. POST /orders/buy/confirm

Curl called :

curl -X 'POST' \
  'http://127.0.0.1:3000/orders/buy/confirm' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject' \
  -H 'Content-Type: application/json' \
  -d '{
  "portfolio_id": 1,
  "stock_id": 1,
  "quantity": 1
}'

Response:

{
  "portfolio_id": 1,
  "user_id": 1,
  "portfolio_name": "Default Portfolio",
  "holdings": [
    {
      "stock_id": 1,
      "stock_name": "AAPL",
      "quantity": 11,
      "price": 100
    },
    {
      "stock_id": 2,
      "stock_name": "MSFT",
      "quantity": 5,
      "price": 200
    }
  ]
}
2. GET /portfolio

Curl called :

curl -X 'GET' \
  'http://127.0.0.1:3000/portfolio?portfolio_id=1' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject'

Response:

{
  "portfolio_id": 1,
  "user_id": 1,
  "portfolio_name": "Default Portfolio",
  "holdings": [
    {
      "stock_id": 1,
      "stock_name": "AAPL",
      "quantity": 11,
      "price": 100
    },
    {
      "stock_id": 2,
      "stock_name": "MSFT",
      "quantity": 5,
      "price": 200
    }
  ]
}
