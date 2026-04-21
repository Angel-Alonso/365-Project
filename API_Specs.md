Deliverables: 

8 API endpoints that we can connect to 

3 Example Flows of how our software works (basically – user stories translated to API calls) 

 

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

 

Example Flow: 

 

Purchasing Stock Example Flow 

Dave has come to our application because he wants to get into stocks and after a little bit of looking around at the available stocks decides to purchase 10 Apple stocks. To do this: 

Call GET /market to see all stocks on the market and simple data 

Call GET /stocks/AAPL to view AAPL stock to view specific data on Apple 

Call GET /account to check available funds 

Call POST /orders/buy/request to attempt to buy stock based on funds and quantity 

Call POST /orders/buy/confirm to complete the purchase and add stock to inventory 

Call GET /portfolio to see the stocks added to his portfolio along with its value 

 

Selling Stock Example Flow 

Dave2 is not a great trader. After buying 100 shares of Microsoft, he sold the next day because they went down $10. To do this: 

Call GET /portfolio to double check Microsoft shares in his portfolio and their value 

Call GET /stocks/MSFT to pull up Microsoft stock page with more details 

Call POST /orders/sell/request to attempt to sell stock based on quantity 

Call POST /orders/sell/confirm to complete the purchase, removing stock from inventory and adding funds to account 

Call GET /account to see updated funds 

Call GET /orders to see the transaction details 

 

Viewing and Researching a Stock Example Flow 

DaveCubed is a smart guy who does his research before making any decisions. He saw some news about Elon Musk and his plans for Tesla, and wants to see if now might be a good time to add shares to his profile. 

Call GET /market to see data on the market today 

Call GET /stocks/TSLA to open Tesla and see specific details 

Call GET /account to review his funds 

Call GET /portfolio to compare with his other stocks 

