import csv
import datetime
import pytz
import requests
import urllib
import uuid
import requests

from flask import redirect, render_template, request, session
from functools import wraps
from cs50 import SQL


# Consider excluding this module!
def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


# Need to modify this with other APIs as well!
def stock_lookup(symbol):
    """Look up quote for symbol."""

    # Prepare API request
    symbol = symbol.upper()
    end = datetime.datetime.now(pytz.timezone("US/Eastern"))
    start = end - datetime.timedelta(days=7)

    # Yahoo Finance API
    url = (
        f"https://query1.finance.yahoo.com/v7/finance/download/{urllib.parse.quote_plus(symbol)}"
        f"?period1={int(start.timestamp())}"
        f"&period2={int(end.timestamp())}"
        f"&interval=1d&events=history&includeAdjustedClose=true"
    )

    # Query API
    try:
        response = requests.get(
            url,
            cookies={"session": str(uuid.uuid4())},
            headers={"Accept": "*/*", "User-Agent": request.headers.get("User-Agent")},
        )
        response.raise_for_status()

        # CSV header: Date,Open,High,Low,Close,Adj Close,Volume
        quotes = list(csv.DictReader(response.content.decode("utf-8").splitlines()))
        price = round(float(quotes[-1]["Adj Close"]), 4)
        return {"price": price, "symbol": symbol}
    
    except (KeyError, IndexError, requests.RequestException, ValueError):
        return 0
    

# Get crypto symbol from Binance API symbol price ticker (GET https://api.binance.com/api/v3/ticker/price?symbol={BTC}USDT)
""" Response is [
  {
    "symbol": "LTCBTC",
    "price": "4.00000200"
  },
  {
    "symbol": "ETHBTC",
    "price": "0.07946600"
  }
] """
def crypto_lookup(symbol):
    symbol = symbol.upper()

    # Binance API
    url = (
        f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        price = round(float(data['price']), 4)
        return {"symbol": symbol, "price": price}

    except (KeyError, IndexError, requests.RequestException, ValueError):
        return 1
    

# Get foreign exchange rates based in USD using Frankfurter API.
""" 
    GET https://api.frankfurter.app/latest?from=USD&to={SGD}
    Response {"amount":1.0,"base":"USD","date":"2024-06-28","rates":{"SGD":1.3557}}
"""
def forex_rate(symbol):
    symbol = symbol.upper()

    #Frankfurter API
    url = (
        f"https://api.frankfurter.app/latest?from=USD&to={symbol}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        rate = round(float(data['rates'][symbol]), 4)
        return {"symbol": symbol, "rate": rate}

    except (KeyError, IndexError, requests.RequestException, ValueError):
        return 2


# Convert other currency values into usd   
def amount_in_usd(currency, value):
    if currency.upper() == 'USD':
        return round(float(value), 2)

    elif currency.upper() == 'MMK':
        exchange_rate = 4970
        amount_in_usd = (1 / exchange_rate) * float(value)
        return round(float(amount_in_usd), 2)

    else:
        exchange_rate = forex_rate(currency)["rate"]
        amount_in_usd = (1 / exchange_rate) * float(value)
        return round(float(amount_in_usd), 2)

        
# function to show in homepage stock profits and debts
def profit(value):
    """ Format currency value to be used in homepage """
    if value > 0:
        return f"+{value:,.2f}"
    
    if value == 0:
        return f"+0.00"
    
    if value < 0:
        return f"{value:,.2f}"
    

# function to show the amount of currency in comma separated financial terms
def currency(value):
    return f"{value:,.2f}"


# function to get days difference for calculating interest rate
def days_difference(past_date_str, date_format='%Y-%m-%d'):
    # Parse the sqlite return string to datetime object.
    past_date = datetime.datetime.strptime(past_date_str, date_format)

    # Get today's date
    today = datetime.datetime.today()

    difference = today - past_date
    return difference.days


# function to check if the repayment is made to user or made by user
def repay_check(debtor_or_creditor):
    # Configure CS50 Library to use SQLite database
    db = SQL("sqlite:///budgetary.db")

    user_id = session.get("user_id")

    # check the first id of debtor_or_creditor in database
    debt_category = db.execute(
        "SELECT debt_category FROM debt WHERE debtor_or_creditor = ? and user_id = ? ORDER BY id LIMIT 1",
        debtor_or_creditor, user_id
    )

    return debt_category
