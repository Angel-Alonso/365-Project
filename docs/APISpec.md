API Endpoints: 

Buy 

The user requests to make a purchase (POST /orders/buy/request) 

There also is an affirmation of that purchase (POST /order/buy/confirm) 

Sell 

User requests to sell a stock (POST /orders/sell/request) 

User confirms sale of stock (POST /orders/sell/confirm) 

View Portfolio 

There should be a call where users can see what inventory of stocks that they have (GET /portfolio) 

View a Single Stock 

Users can look at an individual simulated stock (company or index fund) (GET /stock/{id}) 

Market / Stocks 

Users can view all available stocks (GET /market) 

Orders 

View all orders (GET /orders) 

Account 

View account details (GET /account) 

complex end points

Get/portfolio/{portfolio_id}/performance - 
It calculates the average price paid for each stock using past trasactions, compares it to the current price and computes how much money was gain or lost per stock. 
GET/leaderboard-
It looks at every portfolio calculates how much each user has invested and what their current worth is. 