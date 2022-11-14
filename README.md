# Finance :moneybag: :dollar:
### CS50's Famous Finance Project

## Project Overview:
#### Languages/Frameworks Used: Flask (Python), SQL(Sqlite3), HTML, CSS
* Used Flask to develop a web application that simulates a financial stock portfolio/exchange platform that you can buy and sell stocks from.
* Built up the process of regestering on the platform, buying and selling stocks, viewing your portfolio and viewing your complete history of exchange activity.
* Flask's main file distribution comprise of a conroller app.py file, templates folder for HTML files, styles folder for CSS and a database of some sort.
* In order to access real time stock valuation data, I utilized IEX's API platform which gives you stock quotes, names etc...
* For my database, I used a Sqlite3 to implement CRUD activities, store and manage user data.

In order to run this web application, you must create an account with IEX to obtain a unique token key. Once you obtain that, run export API_KEY= (token key) in the terminal, at the directory where your storing all your files. 

Here are sample images from the web applications.
### The Index Page
![alt text](/img1.png)

### The Sell Page
![alt text](/img2.png)
