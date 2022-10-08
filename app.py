import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    #we will have the LOGGED IN users symbols, total amount of shares for each symbol
    data = db.execute("SELECT symbol, SUM(amount), SUM(amount_sold) FROM purchases WHERE user_id = ? GROUP BY symbol", session["user_id"])

    #create an empty list
    lookup_master = []

    #we will have the name, symbol, price for each symbol a user has.
    for sym in data:
        lookup_master.append(lookup(sym["symbol"]))

    #we will add to lookup master list the items from the data list, i.e amount of stock the user has from each symbol. I know that lookup master and data have symbol names stored in SAME ORDER.
    for i in range(len(lookup_master)):
        lookup_master[i].update(data[i])

    #get the users updated cash value
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

    #add the cash plus equity to get the TOTAL value
    total = 0
    for tot in lookup_master:
        total = total + tot['SUM(amount)']*tot['price']- tot['SUM(amount_sold)']*tot['price']

    total = total + cash[0]['cash']

    return render_template("index.html", data=lookup_master, data2=data, total=total, cash=cash[0]['cash'])


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    #Reach this route via POST
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Must provide a Stock Symbol", 400)

        sym = request.form.get("symbol")
        if not lookup(sym):
            return apology("Invalid Stock Symbol", 400)

        num_shares = int(request.form.get("shares"))

        if num_shares < 1 or not int(request.form.get("shares")):
            return apology("Must select a postive number of shares", 400)

        #get the stock price
        stock_price = lookup(sym)["price"]

        #get the users current balance
        user_current_balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        user_current_balance = float(user_current_balance[0]["cash"])

        #get the total amount user wants to pay: shares*price
        total_amount = stock_price*float(request.form.get("shares"))

        #if total amount more than what user can afford, return an erro
        if total_amount > user_current_balance:
            return apology("You Broke", 400)

        new_user_balance = user_current_balance - total_amount

        #if we pass the condition above, lets execute this purchase and update our tables!
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_user_balance, session["user_id"])
        db.execute("INSERT INTO purchases (symbol, price_of_trans, amount, total_price, user_id, amount_sold) VALUES (?,?,?,?,?,?)", sym,stock_price,int(request.form.get("shares")),total_amount,session["user_id"],0)

        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    transactions = db.execute("SELECT * FROM purchases WHERE user_id = ?", session["user_id"])
    return render_template("history.html",trans=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        #look up the symbol
        symbol_resp = lookup(request.form.get("symbol"))

        #if success, render a text with symbols info
        if not symbol_resp:
            return apology("Invalid Symbol",400)

        return render_template("quoted.html", symbol=symbol_resp)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        #Confirm username (check if it is a text field and its name is "username", essentially check if successfully grabbed via request.form.get)
        if not request.form.get("username"):
            return apology("Invalid username", 400)

        #confirm password
        if not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Invalid password", 400)

        #make sure confirmation of password matches password
        if request.form.get("confirmation") != request.form.get("password"):
            return apology("Password confirmation does not match", 400)

        #Check if the username exists in our database
        user_check = db.execute("SELECT * FROM users WHERE username = ?",request.form.get("username"))
        if len(user_check) != 0:
            return apology("Username already exists", 400)

        #Once pass all checks, successfully inster user into our database. Important columns are username and hash, the rest are auto
        rows = db.execute("INSERT INTO users (username, hash) VALUES (?,?)", request.form.get("username"), generate_password_hash(request.form.get("password")))

        #After we are done, redirect us to home page /
        return redirect("/")

    #If we go to /register via GET, simply render the same register.html page
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    #get the user's current symbols, and total amount bought, total amount sold
    data = db.execute("SELECT symbol, SUM(amount), SUM(amount_sold) FROM purchases WHERE user_id = ? GROUP BY symbol", session["user_id"])

    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Please Choose a symbol", 400)
        for da in data:
            if da['symbol'] == request.form.get("symbol") and (da['SUM(amount)']-da['SUM(amount_sold)']) < int(request.form.get("shares")):
                return apology("Not enough shares", 400)

        sym = request.form.get("symbol")
        stock_price = lookup(sym)["price"]

        #get the users current balance
        user_current_balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        user_current_balance = float(user_current_balance[0]["cash"])

        #get the total amount user wants to pay: shares*price
        total_amount_sold = stock_price*float(request.form.get("shares"))

        new_user_balance = user_current_balance + total_amount_sold

        #if we pass the condition above, lets execute this purchase and update our tables!
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_user_balance, session["user_id"])
        db.execute("INSERT INTO purchases (symbol, price_of_trans, amount, total_price, user_id, amount_sold) VALUES (?,?,?,?,?,?)", sym,stock_price,0,total_amount_sold,session["user_id"],int(request.form.get("shares")))

        return redirect("/")
    else:
        return render_template("sell.html", data=data)

