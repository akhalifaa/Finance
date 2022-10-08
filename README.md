# Finance
### CS50's Famous Finance Project

For this project, I used Flask to develop a web application that simulates a financial stock portfolio/exchange platform that you can buy and sell stocks from. I built up the process of regestering on the platform, buying and selling stocks, viewing your portfolio and viewing your complete history of exchange activity. This project was all about learning and exploring Flask, which is a backend framework running with Python. It was a fantastic learning opportunity to understand what happens underneath the hood of many web applications. Flask's main file distribution comrise of a conroller app.py file, templates folder for HTML files, styles folder for CSS and a database of some sort.

In order to access real time stock valuation data, I utilized IEX's API platform which gives you stock quotes, names etc...

For my database, I used a Sqlite3 to implement CRUD activities, store and manage user data.

In order to run this web application, you must create an account with IEX to obtain a unique token key. Once you obtain that, run export API_KEY= (token key) in the terminal, at the directory where your storing all your files. 

Here are sample images from the web applications.
