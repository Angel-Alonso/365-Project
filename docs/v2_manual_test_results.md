# Example workflow
Purchasing Stock Example Flow

1. Call GET /market to see all stocks on the market and simple data.
2. Call GET /stocks/AAPL to view AAPL stock to view specific data on Apple.
3. Call GET /account to check available funds.
4. Call POST /orders/buy/request to attempt to buy stock based on funds and quantity.
5. Call POST /orders/buy/confirm to complete the purchase and add stock to inventory.
6. Call GET /portfolio to see the stocks added to his portfolio along with its value.

Selling Stock Example Flow

1. Call GET /portfolio to double check Microsoft shares in his portfolio and their value.
2. Call GET /stocks/MSFT to pull up Microsoft stock page with more details.
3. Call POST /orders/sell/request to attempt to sell stock based on quantity.
4. Call POST /orders/sell/confirm to complete the purchase, removing stock from inventory and adding funds to account.
5. Call GET /account to see updated funds.
6. Call GET /orders to see the transaction details.

Viewing and Researching a Stock Example Flow

1. Call GET /market to see data on the market today.
2. Call GET /stocks/TSLA to open Tesla and see specific details.
3. Call GET /account to review his funds.
4. Call GET /portfolio to compare with his other stocks.

# Testing results
## Purchasing Stock Example Flow
### 1. GET /market

Curl called:

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/market' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject'
```

Response:

```json
[
  {
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "price": 100
  },
  {
    "ticker": "MSFT",
    "company_name": "Microsoft Corporation",
    "price": 200
  },
  {
    "ticker": "TSLA",
    "company_name": "Tesla Inc.",
    "price": 250
  }
]
```

### 2. GET /stocks/AAPL

Curl called:

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/stocks/AAPL' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject'
```

Response:

```json
{
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "price": 100
}
```

### 3. GET /account

Curl called:

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/account' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject'
```

Response:

```json
{
  "user_id": 1,
  "name": "admin",
  "email": "admin@admin.com",
  "cash_balance": 10000
}
```

### 4. POST /orders/buy/request

Curl called:

```bash
curl -X 'POST' \
  'http://127.0.0.1:3000/orders/buy/request' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject' \
  -H 'Content-Type: application/json' \
  -d '{
  "portfolio_id": 1,
  "ticker": "AAPL",
  "quantity": 10
}'
```

Response:

```json
{
  "portfolio_id": 1,
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "quantity": 10,
  "price": 100,
  "estimated_total": 1000,
  "can_purchase": true
}
```

### 5. POST /orders/buy/confirm

Curl called:

```bash
curl -X 'POST' \
  'http://127.0.0.1:3000/orders/buy/confirm' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject' \
  -H 'Content-Type: application/json' \
  -d '{
  "portfolio_id": 1,
  "stock_id": 1,
  "quantity": 10
}'
```

Response:

```json
{
  "portfolio_id": 1,
  "user_id": 1,
  "portfolio_name": "Default Portfolio",
  "holdings": [
    {
      "stock_id": 1,
      "stock_name": "AAPL",
      "quantity": 20,
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
```

### 6. GET /portfolio

Curl called:

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/portfolio?portfolio_id=1' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject'
```

Response:

```json
{
  "portfolio_id": 1,
  "user_id": 1,
  "portfolio_name": "Default Portfolio",
  "holdings": [
    {
      "stock_id": 1,
      "stock_name": "AAPL",
      "quantity": 20,
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
```

## Selling Stock Example Flow

### 1. GET /portfolio

Curl called:

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/portfolio?portfolio_id=1' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject'
```

Response:

```json
{
  "portfolio_id": 1,
  "user_id": 1,
  "portfolio_name": "Default Portfolio",
  "holdings": [
    {
      "stock_id": 1,
      "stock_name": "AAPL",
      "quantity": 20,
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
```

### 2. GET /stocks/MSFT

Curl called:

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/stocks/MSFT' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject'
```

Response:

```json
{
  "ticker": "MSFT",
  "company_name": "Microsoft Corporation",
  "price": 200
}
```

### 3. POST /orders/sell/request

Curl called:

```bash
curl -X 'POST' \
  'http://127.0.0.1:3000/orders/sell/request' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject' \
  -H 'Content-Type: application/json' \
  -d '{
  "portfolio_id": 1,
  "ticker": "MSFT",
  "quantity": 5
}'
```

Response:

```json
{
  "portfolio_id": 1,
  "ticker": "MSFT",
  "company_name": "Microsoft Corporation",
  "quantity": 5,
  "price": 200,
  "estimated_total": 1000,
  "can_sell": true
}
```

### 4. POST /orders/sell/confirm

Curl called:

```bash
curl -X 'POST' \
  'http://127.0.0.1:3000/orders/sell/confirm' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject' \
  -H 'Content-Type: application/json' \
  -d '{
  "portfolio_id": 1,
  "stock_id": 2,
  "quantity": 5
}'
```

Response:

```json
{
  "portfolio_id": 1,
  "user_id": 1,
  "portfolio_name": "Default Portfolio",
  "holdings": [
    {
      "stock_id": 1,
      "stock_name": "AAPL",
      "quantity": 20,
      "price": 100
    }
  ]
}
```

### 5. GET /account

Curl called:

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/account' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject'
```

Response:

```json
{
  "user_id": 1,
  "name": "admin",
  "email": "admin@admin.com",
  "cash_balance": 10000
}
```

### 6. GET /orders

Curl called:

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/orders?portfolio_id=1' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject'
```

Response:

```json
[
  {
    "transaction_id": 1,
    "portfolio_id": 1,
    "stock_id": 1,
    "ticker": "AAPL",
    "transaction_type": "BUY",
    "quantity": 10,
    "price": 100,
    "total": 1000
  },
  {
    "transaction_id": 2,
    "portfolio_id": 1,
    "stock_id": 2,
    "ticker": "MSFT",
    "transaction_type": "SELL",
    "quantity": 5,
    "price": 200,
    "total": 1000
  }
]
```

## Viewing and Researching a Stock Example Flow

### 1. GET /market

Curl called:

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/market' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject'
```

Response:

```json
[
  {
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "price": 100
  },
  {
    "ticker": "MSFT",
    "company_name": "Microsoft Corporation",
    "price": 200
  },
  {
    "ticker": "TSLA",
    "company_name": "Tesla Inc.",
    "price": 250
  }
]
```

### 2. GET /stocks/TSLA

Curl called:

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/stocks/TSLA' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject'
```

Response:

```json
{
  "ticker": "TSLA",
  "company_name": "Tesla Inc.",
  "price": 250
}
```

### 3. GET /account

Curl called:

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/account' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject'
```

Response:

```json
{
  "user_id": 1,
  "name": "admin",
  "email": "admin@admin.com",
  "cash_balance": 10000
}
```

### 4. GET /portfolio

Curl called:

```bash
curl -X 'GET' \
  'http://127.0.0.1:3000/portfolio?portfolio_id=1' \
  -H 'accept: application/json' \
  -H 'access_token: groupproject'
```

Response:

```json
{
  "portfolio_id": 1,
  "user_id": 1,
  "portfolio_name": "Default Portfolio",
  "holdings": [
    {
      "stock_id": 1,
      "stock_name": "AAPL",
      "quantity": 20,
      "price": 100
    }
  ]
}
```
