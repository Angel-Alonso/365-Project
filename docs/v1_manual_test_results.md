# Example workflow
Buy Stock + View Portfolio (V1 Minimal Workflow)

1. Call POST /orders/buy/confirm with a portfolio_id, stock_id, and quantity to add shares to a portfolio.
2. Call GET /portfolio?portfolio_id=<id> to verify the holdings updated.

# Testing results
1. POST /orders/buy/confirm

Curl called (copy from your deployed `/docs`):

<paste curl here>

Response:

<paste response here>

2. GET /portfolio

Curl called (copy from your deployed `/docs`):

<paste curl here>

Response:

<paste response here>

