User Stories 
1. As a practicing trader, I want to see the prediction value on Meta stocks 10 months from now to see if it is worth investing in it now.  
2. As someone interested in cryptocurrencies, I want to see how much lower Ethereum is going to be in order for me to buy it at its lowest price.  
3. As a trader, I want to see transaction history of when I bought apple stocks to see if the value increased or decreased from then.  
4. As someone who doesn’t have much knowledge, I want a list of the biggest movements on the market so I can spend less time researching. 
5. As a trader, I want the database to update with real-time stock information so I can make up to date purchases. 
6. As an experienced trader, I want to automatically test my strategy by putting buy and sell indicators to paper trade. 
7. As a new user, I want to create an account so that I can track my own stock portfolio. 
8. As a mobile user, I want fast responses so that I can quickly execute trades and view updates on the go. 
9. As a beginner investor, I want to start with a fixed virtual balance so that I can practice trading in a realistic environment. 
10. As a beginner investor, I want full control over my simulated portfolio so that I can try different strategies and fail without consequence.  
11. As a trader, I want to be able to compare stocks side-by-side so that I can make more informed decisions when trading. 
12. As a learner, I want to be able to see what other trading strategies are so that I can make better decisions when trading. 

Exceptions  
Unknown User – If a user’s credentials aren’t in the system, then they should be alerted to that fact, and then should be directed to the login/signup page. 
Selling more shares than owned - If a user attempts to sell more shares than they own, the system will reject the request and notify the user. 
Insufficient funds - If the user tries to buy stock without enough balance, the system should prompt the user to choose between returning to the previous menu, or to override their simulation wallet and get the stock anyways. 
Database joins – The database should pull stock data for the data at regular intervals and join it into the existing table. If the stock doesn’t exist in the database, it should be added to the table. 
Unknown purchase – If you are trying to get information of stock you never bought an error would pop out saying “stock not found” 
Non-existent Simulated Stock – if a user tries to experiment with a stock that isn’t supported in the playground environment, they should be aware of the scope of the simulation through an error. 
Price-change Error – If a user spends enough time on a stock buying decision, and the price of that stock updates, then the user should be alerted to that information as part of a mandatory pop-up. 
Weekends/Holidays - On days the market is closed, the database should not try to update as there is no new information. 
Invalid Indicators – If the user inputs invalid flags (i.e “purchase AAPL if price < 0), the proper error will be caught and displayed for the user. 
Invalid ticker - If a user enters a stock symbol that does not exist, the system will return an error and prompt the user to enter a valid symbol. 
Inactive session – if a user is inactive for a long enough period of time, then the app should log the user out in order to keep their account private.  
Predictions go wrong - Before giving out prediction we send a message saying “Outside variables may affect our predictions in a real-world situation” 
