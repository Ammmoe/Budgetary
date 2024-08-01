import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify, g
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, stock_lookup, amount_in_usd, crypto_lookup, profit, currency, days_difference, forex_rate, repay_check


# Configure application
app = Flask(__name__)
#cache = Cache(app, config={'CACHE_TYPE': 'redis'})

# Custom filter
app.jinja_env.filters["profit"] = profit
app.jinja_env.filters["currency"] = currency

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///budgetary.db")
    

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session.get("user_id")
    total_assets = 0

    # Create homepage routes
    if request.method == "GET":
        # Get income-related cash values
        income_cash_usd_q = db.execute (
            "SELECT SUM(amount) AS income_cash_usd FROM transactions WHERE payment_method = 'cash' and currency = 'usd' and id IN \
                (SELECT transaction_id FROM income WHERE user_id = ?)", user_id 
        )
        income_cash_usd = income_cash_usd_q[0]["income_cash_usd"]
        if income_cash_usd == None:
            income_cash_usd = 0

        income_cash_sgd_q = db.execute (
            "SELECT SUM(amount) AS income_cash_sgd FROM transactions WHERE payment_method = 'cash' and currency = 'sgd' and id IN \
                (SELECT transaction_id FROM income WHERE user_id = ?)", user_id 
        )
        income_cash_sgd = income_cash_sgd_q[0]["income_cash_sgd"]
        if income_cash_sgd == None:
            income_cash_sgd = 0

        income_cash_thb_q = db.execute (
            "SELECT SUM(amount) AS income_cash_thb FROM transactions WHERE payment_method = 'cash' and currency = 'thb' and id IN \
                (SELECT transaction_id FROM income WHERE user_id = ?)", user_id 
        )
        income_cash_thb = income_cash_thb_q[0]["income_cash_thb"]
        if income_cash_thb == None:
            income_cash_thb = 0

        income_cash_mmk_q = db.execute (
            "SELECT SUM(amount) AS income_cash_mmk FROM transactions WHERE payment_method = 'cash' and currency = 'mmk' and id IN \
                (SELECT transaction_id FROM income WHERE user_id = ?)", user_id 
        )
        income_cash_mmk = income_cash_mmk_q[0]["income_cash_mmk"]
        if income_cash_mmk == None:
            income_cash_mmk = 0

        # Get income-related bank_deposit values
        income_bank_usd_q = db.execute (
            "SELECT SUM(amount) AS income_bank_usd FROM transactions WHERE payment_method = 'banking' and currency = 'usd' and id IN \
                (SELECT transaction_id FROM income WHERE user_id = ?)", user_id 
        )
        income_bank_usd = income_bank_usd_q[0]["income_bank_usd"]
        if income_bank_usd == None:
            income_bank_usd = 0

        income_bank_sgd_q = db.execute (
            "SELECT SUM(amount) AS income_bank_sgd FROM transactions WHERE payment_method = 'banking' and currency = 'sgd' and id IN \
                (SELECT transaction_id FROM income WHERE user_id = ?)", user_id 
        )
        income_bank_sgd = income_bank_sgd_q[0]["income_bank_sgd"]
        if income_bank_sgd == None:
            income_bank_sgd = 0

        income_bank_thb_q = db.execute (
            "SELECT SUM(amount) AS income_bank_thb FROM transactions WHERE payment_method = 'banking' and currency = 'thb' and id IN \
                (SELECT transaction_id FROM income WHERE user_id = ?)", user_id 
        )
        income_bank_thb = income_bank_thb_q[0]["income_bank_thb"]
        if income_bank_thb == None:
            income_bank_thb = 0

        income_bank_mmk_q = db.execute (
            "SELECT SUM(amount) AS income_bank_mmk FROM transactions WHERE payment_method = 'banking' and currency = 'mmk' and id IN \
                (SELECT transaction_id FROM income WHERE user_id = ?)", user_id 
        )
        income_bank_mmk = income_bank_mmk_q[0]["income_bank_mmk"]
        if income_bank_mmk == None:
            income_bank_mmk = 0

        # Get spending-related cash values
        spending_cash_usd_q = db.execute (
            "SELECT SUM(amount) AS spending_cash_usd FROM transactions WHERE payment_method = 'cash' and currency = 'usd' and id IN \
                (SELECT transaction_id FROM spending WHERE user_id = ?)", user_id 
        )
        spending_cash_usd = spending_cash_usd_q[0]["spending_cash_usd"]
        if spending_cash_usd == None:
            spending_cash_usd = 0

        spending_cash_sgd_q = db.execute (
            "SELECT SUM(amount) AS spending_cash_sgd FROM transactions WHERE payment_method = 'cash' and currency = 'sgd' and id IN \
                (SELECT transaction_id FROM spending WHERE user_id = ?)", user_id 
        )
        spending_cash_sgd = spending_cash_sgd_q[0]["spending_cash_sgd"]
        if spending_cash_sgd == None:
            spending_cash_sgd = 0

        spending_cash_thb_q = db.execute (
            "SELECT SUM(amount) AS spending_cash_thb FROM transactions WHERE payment_method = 'cash' and currency = 'thb' and id IN \
                (SELECT transaction_id FROM spending WHERE user_id = ?)", user_id 
        )
        spending_cash_thb = spending_cash_thb_q[0]["spending_cash_thb"]
        if spending_cash_thb == None:
            spending_cash_thb = 0

        spending_cash_mmk_q = db.execute (
            "SELECT SUM(amount) AS spending_cash_mmk FROM transactions WHERE payment_method = 'cash' and currency = 'mmk' and id IN \
                (SELECT transaction_id FROM spending WHERE user_id = ?)", user_id 
        )
        spending_cash_mmk = spending_cash_mmk_q[0]["spending_cash_mmk"]
        if spending_cash_mmk == None:
            spending_cash_mmk = 0

        # Get spending-related bank_deposit values
        spending_bank_usd_q = db.execute (
            "SELECT SUM(amount) AS spending_bank_usd FROM transactions WHERE payment_method = 'banking' and currency = 'usd' and id IN \
                (SELECT transaction_id FROM spending WHERE user_id = ?)", user_id 
        )
        spending_bank_usd = spending_bank_usd_q[0]["spending_bank_usd"]
        if spending_bank_usd == None:
            spending_bank_usd = 0

        spending_bank_sgd_q = db.execute (
            "SELECT SUM(amount) AS spending_bank_sgd FROM transactions WHERE payment_method = 'banking' and currency = 'sgd' and id IN \
                (SELECT transaction_id FROM spending WHERE user_id = ?)", user_id 
        )
        spending_bank_sgd = spending_bank_sgd_q[0]["spending_bank_sgd"]
        if spending_bank_sgd == None:
            spending_bank_sgd = 0

        spending_bank_thb_q = db.execute (
            "SELECT SUM(amount) AS spending_bank_thb FROM transactions WHERE payment_method = 'banking' and currency = 'thb' and id IN \
                (SELECT transaction_id FROM spending WHERE user_id = ?)", user_id 
        )
        spending_bank_thb = spending_bank_thb_q[0]["spending_bank_thb"]
        if spending_bank_thb == None:
            spending_bank_thb = 0

        spending_bank_mmk_q = db.execute (
            "SELECT SUM(amount) AS spending_bank_mmk FROM transactions WHERE payment_method = 'banking' and currency = 'mmk' and id IN \
                (SELECT transaction_id FROM spending WHERE user_id = ?)", user_id 
        )
        spending_bank_mmk = spending_bank_mmk_q[0]["spending_bank_mmk"]
        if spending_bank_mmk == None:
            spending_bank_mmk = 0

        # Get investment-related cash values for buy
        investment_cash_buy_usd_q = db.execute (
            "SELECT SUM(amount) AS investment_cash_buy_usd FROM transactions WHERE payment_method = 'cash' and currency = 'usd' and id IN \
                (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'buy')", user_id
        )
        investment_cash_buy_usd = investment_cash_buy_usd_q[0]["investment_cash_buy_usd"]
        if investment_cash_buy_usd == None:
            investment_cash_buy_usd = 0

        investment_cash_buy_sgd_q = db.execute (
            "SELECT SUM(amount) AS investment_cash_buy_sgd FROM transactions WHERE payment_method = 'cash' and currency = 'sgd' and id IN \
                (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'buy')", user_id
        )
        investment_cash_buy_sgd = investment_cash_buy_sgd_q[0]["investment_cash_buy_sgd"]
        if investment_cash_buy_sgd == None:
            investment_cash_buy_sgd = 0

        investment_cash_buy_thb_q = db.execute (
            "SELECT SUM(amount) AS investment_cash_buy_thb FROM transactions WHERE payment_method = 'cash' and currency = 'thb' and id IN \
                (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'buy')", user_id
        )
        investment_cash_buy_thb = investment_cash_buy_thb_q[0]["investment_cash_buy_thb"]
        if investment_cash_buy_thb == None:
            investment_cash_buy_thb = 0

        investment_cash_buy_mmk_q = db.execute (
            "SELECT SUM(amount) AS investment_cash_buy_mmk FROM transactions WHERE payment_method = 'cash' and currency = 'mmk' and id IN \
                (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'buy')", user_id
        )
        investment_cash_buy_mmk = investment_cash_buy_mmk_q[0]["investment_cash_buy_mmk"]
        if investment_cash_buy_mmk == None:
            investment_cash_buy_mmk = 0

        # Get investment-related bank values for buy
        investment_bank_buy_usd_q = db.execute (
            "SELECT SUM(amount) AS investment_bank_buy_usd FROM transactions WHERE payment_method = 'banking' and currency = 'usd' and id IN \
                (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'buy')", user_id
        )
        investment_bank_buy_usd = investment_bank_buy_usd_q[0]["investment_bank_buy_usd"]
        if investment_bank_buy_usd == None:
            investment_bank_buy_usd = 0

        investment_bank_buy_sgd_q = db.execute (
            "SELECT SUM(amount) AS investment_bank_buy_sgd FROM transactions WHERE payment_method = 'banking' and currency = 'sgd' and id IN \
                (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'buy')", user_id
        )
        investment_bank_buy_sgd = investment_bank_buy_sgd_q[0]["investment_bank_buy_sgd"]
        if investment_bank_buy_sgd == None:
            investment_bank_buy_sgd = 0

        investment_bank_buy_thb_q = db.execute (
            "SELECT SUM(amount) AS investment_bank_buy_thb FROM transactions WHERE payment_method = 'banking' and currency = 'thb' and id IN \
                (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'buy')", user_id
        )
        investment_bank_buy_thb = investment_bank_buy_thb_q[0]["investment_bank_buy_thb"]
        if investment_bank_buy_thb == None:
            investment_bank_buy_thb = 0

        investment_bank_buy_mmk_q = db.execute (
            "SELECT SUM(amount) AS investment_bank_buy_mmk FROM transactions WHERE payment_method = 'banking' and currency = 'mmk' and id IN \
                (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'buy')", user_id
        )
        investment_bank_buy_mmk = investment_bank_buy_mmk_q[0]["investment_bank_buy_mmk"]
        if investment_bank_buy_mmk == None:
            investment_bank_buy_mmk = 0

        # Get investment-related cash values for sell
        investment_cash_sell_usd_q = db.execute (
            "SELECT SUM(amount) AS investment_cash_sell_usd FROM transactions WHERE payment_method = 'cash' and currency = 'usd' and id IN \
                (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'sell')", user_id
        )
        investment_cash_sell_usd = investment_cash_sell_usd_q[0]["investment_cash_sell_usd"]
        if investment_cash_sell_usd == None:
            investment_cash_sell_usd = 0

        investment_cash_sell_sgd_q = db.execute (
            "SELECT SUM(amount) AS investment_cash_sell_sgd FROM transactions WHERE payment_method = 'cash' and currency = 'sgd' and id IN \
                (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'sell')", user_id
        )
        investment_cash_sell_sgd = investment_cash_sell_sgd_q[0]["investment_cash_sell_sgd"]
        if investment_cash_sell_sgd == None:
            investment_cash_sell_sgd = 0

        investment_cash_sell_thb_q = db.execute (
            "SELECT SUM(amount) AS investment_cash_sell_thb FROM transactions WHERE payment_method = 'cash' and currency = 'thb' and id IN \
                (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'sell')", user_id
        )
        investment_cash_sell_thb = investment_cash_sell_thb_q[0]["investment_cash_sell_thb"]
        if investment_cash_sell_thb == None:
            investment_cash_sell_thb = 0

        investment_cash_sell_mmk_q = db.execute (
            "SELECT SUM(amount) AS investment_cash_sell_mmk FROM transactions WHERE payment_method = 'cash' and currency = 'mmk' and id IN \
                (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'sell')", user_id
        )
        investment_cash_sell_mmk = investment_cash_sell_mmk_q[0]["investment_cash_sell_mmk"]
        if investment_cash_sell_mmk == None:
            investment_cash_sell_mmk = 0

        # Get investment-related bank values for sell
        investment_bank_sell_usd_q = db.execute (
            "SELECT SUM(amount) AS investment_bank_sell_usd FROM transactions WHERE payment_method = 'banking' and currency = 'usd' and id IN \
                (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'sell')", user_id
        )
        investment_bank_sell_usd = investment_bank_sell_usd_q[0]["investment_bank_sell_usd"]
        if investment_bank_sell_usd == None:
            investment_bank_sell_usd = 0

        investment_bank_sell_sgd_q = db.execute (
            "SELECT SUM(amount) AS investment_bank_sell_sgd FROM transactions WHERE payment_method = 'banking' and currency = 'sgd' and id IN \
                (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'sell')", user_id
        )
        investment_bank_sell_sgd = investment_bank_sell_sgd_q[0]["investment_bank_sell_sgd"]
        if investment_bank_sell_sgd == None:
            investment_bank_sell_sgd = 0

        investment_bank_sell_thb_q = db.execute (
            "SELECT SUM(amount) AS investment_bank_sell_thb FROM transactions WHERE payment_method = 'banking' and currency = 'thb' and id IN \
                (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'sell')", user_id
        )
        investment_bank_sell_thb = investment_bank_sell_thb_q[0]["investment_bank_sell_thb"]
        if investment_bank_sell_thb == None:
            investment_bank_sell_thb = 0

        investment_bank_sell_mmk_q = db.execute (
            "SELECT SUM(amount) AS investment_bank_sell_mmk FROM transactions WHERE payment_method = 'banking' and currency = 'mmk' and id IN \
                (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'sell')", user_id
        )
        investment_bank_sell_mmk = investment_bank_sell_mmk_q[0]["investment_bank_sell_mmk"]
        if investment_bank_sell_mmk == None:
            investment_bank_sell_mmk = 0

        # Get debt rows that are not repetitive after each repay process
        debt_rows = db.execute(
            "WITH ranked AS ( \
            SELECT \
                transactions.transaction_date AS date, \
                debt.id AS debt_id, \
                debt.user_id AS user_id, \
                debt.debt_category AS category, \
                debt.debtor_or_creditor AS debtor_or_creditor, \
                debt.interest_rate AS interest_rate, \
                transactions.payment_method AS payment_method, \
                transactions.currency AS currency, \
                transactions.amount AS amount, \
                transactions.amount_in_usd AS amount_in_usd, \
                ROW_NUMBER() OVER ( \
                    PARTITION BY \
                    CASE \
                        WHEN debt.debt_category IN ('borrow', 'lend') THEN debt.debtor_or_creditor \
                        WHEN debt.debt_category = 'repay' THEN debt.id \
                        ELSE NULL \
                    END \
                    ORDER BY debt.id ASC) AS row \
            FROM \
                debt JOIN transactions ON debt.transaction_id = transactions.id \
            WHERE \
                debt.user_id = ?) \
            SELECT \
                date, \
                category, \
                debtor_or_creditor, \
                interest_rate, \
                payment_method, \
                currency, \
                amount, \
                amount_in_usd \
            FROM \
                ranked \
            WHERE \
                (row = 1 AND category IN ('borrow', 'lend')) \
                OR category = 'repay' \
            ORDER BY \
                debt_id \
            ASC", user_id)

        # Debt cash usd values
        debt_cash_borrow_usd = 0
        debt_cash_lend_usd = 0
        debt_cash_brepay_usd = 0
        debt_cash_lrepay_usd = 0

        # Debt bank usd values
        debt_bank_borrow_usd = 0
        debt_bank_lend_usd = 0
        debt_bank_brepay_usd = 0
        debt_bank_lrepay_usd = 0
        
        # Debt cash sgd values
        debt_cash_borrow_sgd = 0
        debt_cash_lend_sgd = 0
        debt_cash_brepay_sgd = 0
        debt_cash_lrepay_sgd = 0

        # Debt bank sgd values
        debt_bank_borrow_sgd = 0
        debt_bank_lend_sgd = 0
        debt_bank_brepay_sgd = 0
        debt_bank_lrepay_sgd = 0

        # Debt cash thb values
        debt_cash_borrow_thb = 0
        debt_cash_lend_thb = 0
        debt_cash_brepay_thb = 0
        debt_cash_lrepay_thb = 0

        # Debt bank thb values
        debt_bank_borrow_thb = 0
        debt_bank_lend_thb = 0
        debt_bank_brepay_thb = 0
        debt_bank_lrepay_thb = 0
        
        # Debt cash mmk values
        debt_cash_borrow_mmk = 0
        debt_cash_lend_mmk = 0
        debt_cash_brepay_mmk = 0
        debt_cash_lrepay_mmk = 0

        # Debt bank mmk values
        debt_bank_borrow_mmk = 0
        debt_bank_lend_mmk = 0
        debt_bank_brepay_mmk = 0
        debt_bank_lrepay_mmk = 0

        for row in debt_rows:
            # debt_cash_borrow variables
            if row['category'] == 'borrow' and row['payment_method'] == 'cash':
                if row['currency'] == 'usd':
                    debt_cash_borrow_usd = debt_cash_borrow_usd + round(float(row['amount']), 2)

                elif row['currency'] == 'sgd':
                    debt_cash_borrow_sgd = debt_cash_borrow_sgd + round(float(row['amount']), 2)

                elif row['currency'] == 'thb':
                    debt_cash_borrow_thb = debt_cash_borrow_thb + round(float(row['amount']), 2)

                elif row['currency'] == 'mmk':
                    debt_cash_borrow_mmk = debt_cash_borrow_mmk + round(float(row['amount']), 2)

            # debt_bank_borrow variables
            if row['category'] == 'borrow' and row['payment_method'] == 'banking':
                if row['currency'] == 'usd':
                    debt_bank_borrow_usd = debt_bank_borrow_usd + round(float(row['amount']), 2)

                elif row['currency'] == 'sgd':
                    debt_bank_borrow_sgd = debt_bank_borrow_sgd + round(float(row['amount']), 2)

                elif row['currency'] == 'thb':
                    debt_bank_borrow_thb = debt_bank_borrow_thb + round(float(row['amount']), 2)

                elif row['currency'] == 'mmk':
                    debt_bank_borrow_mmk = debt_bank_borrow_mmk + round(float(row['amount']), 2)

            # debt_cash_lend variables
            if row['category'] == 'lend' and row['payment_method'] == 'cash':
                if row['currency'] == 'usd':
                    debt_cash_lend_usd = debt_cash_lend_usd + round(float(row['amount']), 2)

                elif row['currency'] == 'sgd':
                    debt_cash_lend_sgd = debt_cash_lend_sgd + round(float(row['amount']), 2)

                elif row['currency'] == 'thb':
                    debt_cash_lend_thb = debt_cash_lend_thb + round(float(row['amount']), 2)

                elif row['currency'] == 'mmk':
                    debt_cash_lend_mmk = debt_cash_lend_mmk + round(float(row['amount']), 2)

            # debt_bank_lend variables
            if row['category'] == 'lend' and row['payment_method'] == 'banking':
                if row['currency'] == 'usd':
                    debt_bank_lend_usd = debt_bank_lend_usd + round(float(row['amount']), 2)

                elif row['currency'] == 'sgd':
                    debt_bank_lend_sgd = debt_bank_lend_sgd + round(float(row['amount']), 2)

                elif row['currency'] == 'thb':
                    debt_bank_lend_thb = debt_bank_lend_thb + round(float(row['amount']), 2)

                elif row['currency'] == 'mmk':
                    debt_bank_lend_mmk = debt_bank_lend_mmk + round(float(row['amount']), 2)

            # debt repay variables
            if row['category'] == 'repay':
                # debt cash lrepay variables
                if repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'lend' and row['payment_method'] == 'cash':
                    if row['currency'] == 'usd':
                        debt_cash_lrepay_usd = debt_cash_lrepay_usd + round(float(row['amount']), 2)

                    elif row['currency'] == 'sgd':
                        debt_cash_lrepay_sgd = debt_cash_lrepay_sgd + round(float(row['amount']), 2)

                    elif row['currency'] == 'thb':
                        debt_cash_lrepay_thb = debt_cash_lrepay_thb + round(float(row['amount']), 2)

                    elif row['currency'] == 'mmk':
                        debt_cash_lrepay_mmk = debt_cash_lrepay_mmk + round(float(row['amount']), 2)

                # debt bank lrepay variables
                if repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'lend' and row['payment_method'] == 'banking':
                    if row['currency'] == 'usd':
                        debt_bank_lrepay_usd = debt_bank_lrepay_usd + round(float(row['amount']), 2)

                    elif row['currency'] == 'sgd':
                        debt_bank_lrepay_sgd = debt_bank_lrepay_sgd + round(float(row['amount']), 2)

                    elif row['currency'] == 'thb':
                        debt_bank_lrepay_thb = debt_bank_lrepay_thb + round(float(row['amount']), 2)

                    elif row['currency'] == 'mmk':
                        debt_bank_lrepay_mmk = debt_bank_lrepay_mmk + round(float(row['amount']), 2)

                # debt cash brepay variables
                if repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'borrow' and row['payment_method'] == 'cash':
                    if row['currency'] == 'usd':
                        debt_cash_brepay_usd = debt_cash_brepay_usd + round(float(row['amount']), 2)

                    elif row['currency'] == 'sgd':
                        debt_cash_brepay_sgd = debt_cash_brepay_sgd + round(float(row['amount']), 2)

                    elif row['currency'] == 'thb':
                        debt_cash_brepay_thb = debt_cash_brepay_thb + round(float(row['amount']), 2)

                    elif row['currency'] == 'mmk':
                        debt_cash_brepay_mmk = debt_cash_brepay_mmk + round(float(row['amount']), 2)

                # debt bank brepay variables
                if repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'borrow' and row['payment_method'] == 'banking':
                    if row['currency'] == 'usd':
                        debt_bank_brepay_usd = debt_bank_brepay_usd + round(float(row['amount']), 2)

                    elif row['currency'] == 'sgd':
                        debt_bank_brepay_sgd = debt_bank_brepay_sgd + round(float(row['amount']), 2)

                    elif row['currency'] == 'thb':
                        debt_bank_brepay_thb = debt_bank_brepay_thb + round(float(row['amount']), 2)

                    elif row['currency'] == 'mmk':
                        debt_bank_brepay_mmk = debt_bank_brepay_mmk + round(float(row['amount']), 2)

        cash_usd = income_cash_usd - spending_cash_usd + investment_cash_sell_usd - investment_cash_buy_usd \
            + debt_cash_borrow_usd - debt_cash_lend_usd - debt_cash_brepay_usd + debt_cash_lrepay_usd
        
        cash_sgd = income_cash_sgd - spending_cash_sgd + investment_cash_sell_sgd - investment_cash_buy_sgd \
            + debt_cash_borrow_sgd - debt_cash_lend_sgd - debt_cash_brepay_sgd + debt_cash_lrepay_sgd
        
        cash_thb = income_cash_thb - spending_cash_thb + investment_cash_sell_thb - investment_cash_buy_thb \
            + debt_cash_borrow_thb - debt_cash_lend_thb - debt_cash_brepay_thb + debt_cash_lrepay_thb
        
        cash_mmk = income_cash_mmk - spending_cash_mmk + investment_cash_sell_mmk - investment_cash_buy_mmk \
            + debt_cash_borrow_mmk - debt_cash_lend_mmk - debt_cash_brepay_mmk + debt_cash_lrepay_mmk
        
        bank_usd = income_bank_usd - spending_bank_usd + investment_bank_sell_usd - investment_bank_buy_usd \
            + debt_bank_borrow_usd - debt_bank_lend_usd - debt_bank_brepay_usd + debt_bank_lrepay_usd
        
        bank_sgd = income_bank_sgd - spending_bank_sgd + investment_bank_sell_sgd - investment_bank_buy_sgd \
            + debt_bank_borrow_sgd - debt_bank_lend_sgd - debt_bank_brepay_sgd + debt_bank_lrepay_sgd
        
        bank_thb = income_bank_thb - spending_bank_thb + investment_bank_sell_thb - investment_bank_buy_thb \
            + debt_bank_borrow_thb - debt_bank_lend_thb - debt_bank_brepay_thb + debt_bank_lrepay_thb
        
        bank_mmk = income_bank_mmk - spending_bank_mmk + investment_bank_sell_mmk - investment_bank_buy_mmk \
            + debt_bank_borrow_mmk - debt_bank_lend_mmk - debt_bank_brepay_mmk + debt_bank_lrepay_mmk
        
        cash_usd = round(cash_usd, 2)
        cash_sgd = round(cash_sgd, 2)
        cash_thb = round(cash_thb, 2)
        cash_mmk = round(cash_mmk, 2)

        bank_usd = round(bank_usd, 2)
        bank_sgd = round(bank_sgd, 2)
        bank_thb = round(bank_thb, 2)
        bank_mmk = round(bank_mmk, 2)

        cash_usd_str = f"{cash_usd:,.2f}"
        cash_sgd_str = f"{cash_sgd:,.2f}"
        cash_thb_str = f"{cash_thb:,.2f}"
        cash_mmk_str = f"{cash_mmk:,.2f}"

        bank_usd_str = f"{bank_usd:,.2f}"
        bank_sgd_str = f"{bank_sgd:,.2f}"
        bank_thb_str = f"{bank_thb:,.2f}"
        bank_mmk_str = f"{bank_mmk:,.2f}"

        # Change the currency in cash to usd for total amount calculation
        cash_sgd_in_usd = amount_in_usd('sgd', cash_sgd)
        cash_thb_in_usd = amount_in_usd('thb', cash_thb)
        cash_mmk_in_usd = amount_in_usd('mmk', cash_mmk)

        # Change the currency in banking to usd for total amount calculation
        bank_sgd_in_usd = amount_in_usd('sgd', bank_sgd)
        bank_thb_in_usd = amount_in_usd('thb', bank_thb)
        bank_mmk_in_usd = amount_in_usd('mmk', bank_mmk)

        # Get the total cash in usd
        total_cash_usd = round((cash_usd + cash_sgd_in_usd + cash_thb_in_usd + cash_mmk_in_usd), 2)

        # Get total bank in usd
        total_bank_usd = round((bank_usd + bank_sgd_in_usd + bank_thb_in_usd + bank_mmk_in_usd), 2)

        total_assets = total_assets + total_cash_usd + total_bank_usd

        # Write database code for homepage investments table
        investment_rows = db.execute (
            "SELECT \
                investment.investment_type, \
                CASE \
                    WHEN investment.investment_type = 'other-investment' THEN investment.investment_comment \
                    WHEN investment.symbol_real_estate_type = 'otherRealEstate' THEN investment.real_estate_comment \
                    ELSE investment.symbol_real_estate_type \
                END AS symbol, \
                SUM(CASE WHEN investment.buy_or_sell = 'buy' THEN investment.quantity ELSE -investment.quantity END) AS quantity, \
                SUM(CASE WHEN investment.buy_or_sell = 'buy' THEN transactions.amount_in_usd ELSE -transactions.amount_in_usd END) AS original_value \
            FROM investment JOIN transactions \
            ON investment.transaction_id = transactions.id \
            WHERE investment.user_id = ? \
            GROUP BY \
                investment.investment_type, \
                CASE \
                    WHEN investment.investment_type = 'other-investment' THEN investment.investment_comment \
                    WHEN investment.symbol_real_estate_type = 'otherRealEstate' THEN investment.real_estate_comment \
                    ELSE investment.symbol_real_estate_type \
                END", user_id
        )

        new_investment_rows = []
        investment_total = 0
        profit_loss_total = 0
        for row in investment_rows:
            quantity = round(float(row['quantity']), 2)

            if row['investment_type'] == 'stock':
                stock_quote = stock_lookup(row['symbol'])
                stock_price = stock_quote['price']
                market_value = round(stock_price * quantity, 2)
                profit_loss = round(market_value - float(row['original_value']), 2)
                row['original_value'] = market_value
                row['profit_loss'] = profit_loss
                row['quantity'] = quantity
                investment_total = investment_total + market_value
                profit_loss_total = profit_loss_total + profit_loss

                new_investment_rows.append(row)

            elif row['investment_type'] == 'cryptocurrency':
                crypto_quote = crypto_lookup(row['symbol'])
                crypto_price = crypto_quote['price']
                market_value = round(crypto_price * quantity, 2)
                profit_loss = round(market_value - float(row['original_value']), 2)
                row['original_value'] = market_value
                row['profit_loss'] = profit_loss
                row['quantity'] = quantity
                investment_total = investment_total + market_value
                profit_loss_total = profit_loss_total + profit_loss

                new_investment_rows.append(row)

            else:
                row['profit_loss'] = 0
                row['quantity'] = quantity
                investment_total = investment_total + row['original_value']

                new_investment_rows.append(row)

        total_assets = total_assets + investment_total
   
        # Write database code for Debts & Receivables table
        debt_rows = db.execute (
            "SELECT \
            debt.debt_category, debt.debtor_or_creditor, transactions.transaction_date, debt.interest_rate, transactions.currency, \
            transactions.amount \
            FROM debt JOIN transactions \
            ON debt.transaction_id = transactions.id \
            WHERE debt.user_id = ? and debt.id IN (SELECT MAX(debt.id) FROM debt GROUP BY debtor_or_creditor)", user_id
        )

        new_debt_rows = []
        debt_total = 0
        interest_total = 0
        for row in debt_rows:
            original_debt_amount = float(row['amount'])
            interest_rate = float(row['interest_rate'])
            days_diff = days_difference(row['transaction_date'])
            
            # Find out the number of months
            months = days_diff / 30

            # Calculate interest
            interest = round((original_debt_amount * interest_rate * months / 100), 2)
            interest_in_usd = amount_in_usd(row['currency'], interest)

            # Find out the total amount to be repaid
            total_debt = round(original_debt_amount + interest, 2)
            total_debt_usd = amount_in_usd(row['currency'], total_debt)
        
            row['amount'] = total_debt
            row['interest'] = interest

            if row['debt_category'] == 'borrow':
                debt_total = debt_total - total_debt_usd
                interest_total = interest_total - interest_in_usd

            elif row['debt_category'] == 'lend':
                debt_total = debt_total + total_debt_usd
                interest_total = interest_total + interest_in_usd

            new_debt_rows.append(row)

        total_assets = total_assets + debt_total

        return render_template("index.html", cash_usd=cash_usd_str, cash_sgd=cash_sgd_str, cash_thb=cash_thb_str, cash_mmk=cash_mmk_str, \
            bank_usd=bank_usd_str, bank_sgd=bank_sgd_str, bank_thb=bank_thb_str, bank_mmk=bank_mmk_str, investment_rows=new_investment_rows, \
            profit=profit, currency=currency, debt_rows=new_debt_rows, total_cash_usd=total_cash_usd, total_bank_usd=total_bank_usd, \
            investment_total=investment_total, profit_loss_total=profit_loss_total, debt_total=debt_total, interest_total=interest_total, \
            total_assets=total_assets)


@app.route("/budgetary", methods=["GET", "POST"])
@login_required
def budgetary():
    if request.method == "POST":

        # Valid options for server side error handling
        valid_budgetary_types = ['income', 'spending', 'investment', 'debt']
        valid_income_types = ['salary', 'bank-interest', 'other-income']
        valid_spending_types = ['food', 'transportation', 'clothing', 'rent', 'other-spending']
        valid_investment_types = ['stock', 'cryptocurrency', 'real-estate', 'other-investment']
        valid_real_estates = ['residential', 'land', 'industrial', 'otherRealEstate']
        valid_buy_sell_types = ['buy', 'sell']
        valid_debt_categories = ['borrow', 'lend', 'repay']
        valid_payment_methods = ['cash', 'banking']
        valid_currencies = ['usd', 'sgd', 'thb', 'mmk']

        # Get user input elements
        date = request.form.get('date')
        budgetary_type = request.form.get('budgetary-type')
        income_type = request.form.get('income-type')
        other_income = request.form.get('incomeOther')
        spending_type = request.form.get('spending-type')
        other_spending = request.form.get('spendingOther')
        investment_type = request.form.get('investment-type')
        other_investment = request.form.get('investmentOther')
        stock_symbol = request.form.get('stockSymbol')
        crypto_symbol = request.form.get('cryptoSymbol')
        real_estate = request.form.get('realEstate')
        other_real_estate = request.form.get('realEstateOther')
        buy_sell = request.form.get('buyOrSell')
        quantity = request.form.get('quantityOfItems')
        debtor_creditor = request.form.get('debtor')
        debt_category = request.form.get('debt-category')
        interest_rate = request.form.get('interestRate')
        payment_method = request.form.get('payment-method')
        currency = request.form.get('currency')
        amount = request.form.get('amount')

        # Error handling at server side
        if date == '':
            flash('Please input date!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type not in valid_budgetary_types:
            msg = flash('Please choose budgetary type!', 'alert-danger')
            print(f"Flash message: {msg}")
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'income' and income_type not in valid_income_types:
            flash('Please choose income type!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'income' and income_type == 'other-income' and other_income == '':
            flash('Please specify other income!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'spending' and spending_type not in valid_spending_types:
            flash('Please choose expense type!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'spending' and spending_type == 'other-spending' and other_spending == '':
            flash('Please specify other expense!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'investment' and investment_type not in valid_investment_types:
            flash('Please choose investment type!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'investment' and investment_type == 'stock' and stock_lookup(stock_symbol) == 0:
            flash('Invalid stock symbol!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'investment' and investment_type == 'cryptocurrency' and crypto_lookup(crypto_symbol) == 1:
            flash('Invalid cryptocurrency symbol!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'investment' and investment_type == 'real-estate' and real_estate not in valid_real_estates:
            flash('Please choose real estate!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'investment' and investment_type == 'real-estate' and real_estate == 'otherRealEstate' and other_real_estate == '':
            flash('Please specify other real estate!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'investment' and investment_type == 'other-investment' and other_investment == '':
            flash('Please specify other investment!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'investment' and investment_type in valid_investment_types and buy_sell not in valid_buy_sell_types:
            flash('Please select buy or sell!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'investment' and (quantity == '' or not isinstance(float(quantity), float) or float(quantity) <= 0):
            flash('Please input positive quantity!', 'alert-danger') 
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'debt' and debtor_creditor == '':
            flash('Please input debtor or creditor!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        # Handle unique value error of debtor_creditor inside function

        if budgetary_type == 'debt' and debt_category not in valid_debt_categories:
            flash('Please choose debt category!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'debt' and (debt_category == 'borrow' or debt_category == 'lend') and (interest_rate == '' or not isinstance(float(interest_rate), float) or float(interest_rate) < 0):
            flash('Please input positive interest rate!', 'alert-danger')   
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'debt' and debt_category == 'repay' and interest_rate is not None:
            flash('Please do not input interest rate in debt repay category!', 'alert-danger') 
            return redirect(url_for('budgetary'))

        if payment_method not in valid_payment_methods:
            flash('Please choose payment method!', 'alert-danger')
            return redirect(url_for('budgetary'))
               
        if currency not in valid_currencies:
            flash('Please choose currency!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if amount == '' or not isinstance(float(amount), float) or float(amount) <= 0:
            flash('Please input positive amount!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        # Convert the transaction amount to usd
        usd_amount = amount_in_usd(currency, amount)

        # Get the user id
        user_id = session.get("user_id")

        # Update database for income category
        if budgetary_type == 'income':         

            # Update transactions table
            db.execute(
                "INSERT INTO transactions (payment_method, currency, amount, amount_in_usd, transaction_date) VALUES (?, ?, ?, ?, ?)",
                payment_method, currency, amount, usd_amount, date
            )
            
            # Get the last row of transactions table (to get transaction id)
            row = db.execute(
                "SELECT * FROM transactions ORDER BY id DESC LIMIT 1"
            )
            transaction_id = row[0]["id"]

            # Update income table
            db.execute(
                "INSERT INTO income (user_id, transaction_id, income_type, comment) VALUES (?, ?, ?, ?)",
                user_id, transaction_id, income_type, other_income
            )
            flash('Success!', 'alert-success')
            return redirect(url_for('budgetary'))

        # If spending is chosen...    
        elif budgetary_type == 'spending':

            # Update transactions table
            db.execute(
                "INSERT INTO transactions (payment_method, currency, amount, amount_in_usd, transaction_date) VALUES (?, ?, ?, ?, ?)",
                payment_method, currency, amount, usd_amount, date
            )
            
            # Get the last row of transactions table (to get transaction id)
            row = db.execute(
                "SELECT * FROM transactions ORDER BY id DESC LIMIT 1"
            )
            transaction_id = row[0]["id"]

            # Update spending table
            db.execute(
                "INSERT INTO spending (user_id, transaction_id, spending_type, comment) VALUES (?, ?, ?, ?)",
                user_id, transaction_id, spending_type, other_spending
            )
            flash('Success!', 'alert-success')
            return redirect(url_for('budgetary'))

        elif budgetary_type == 'investment':

            # Update transactions table
            db.execute(
                "INSERT INTO transactions (payment_method, currency, amount, amount_in_usd, transaction_date) VALUES (?, ?, ?, ?, ?)",
                payment_method, currency, amount, usd_amount, date
            )
            
            # Get the last row of transactions table (to get transaction id)
            row = db.execute(
                "SELECT * FROM transactions ORDER BY id DESC LIMIT 1"
            )
            transaction_id = row[0]["id"]

            # If stock is chosen for investment_type...
            if investment_type == 'stock':
                # Update investment table
                db.execute(
                    "INSERT INTO investment (user_id, transaction_id, investment_type, investment_comment, symbol_real_estate_type, buy_or_sell, quantity) \
                    VALUES (?, ?, ?, ?, ?, ?, ?)",
                    user_id, transaction_id, investment_type, other_investment, stock_symbol.upper(), buy_sell, quantity
                )
                flash('Success!', 'alert-success')
                return redirect(url_for('budgetary'))

            # If cryptocurrency is chosen for investment_type...
            elif investment_type == 'cryptocurrency': 
                # Update investment table
                db.execute(
                    "INSERT INTO investment (user_id, transaction_id, investment_type, investment_comment, symbol_real_estate_type, buy_or_sell, quantity) \
                    VALUES (?, ?, ?, ?, ?, ?, ?)",
                    user_id, transaction_id, investment_type, other_investment, crypto_symbol.upper(), buy_sell, quantity
                )
                flash('Success!', 'alert-success')
                return redirect(url_for('budgetary'))

            # If real-estate is chosen for investment_type...
            elif investment_type == 'real-estate':
                # Update investment table
                db.execute(
                    "INSERT INTO investment (user_id, transaction_id, investment_type, investment_comment, symbol_real_estate_type, real_estate_comment, buy_or_sell, quantity) \
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    user_id, transaction_id, investment_type, other_investment, real_estate, other_real_estate, buy_sell, quantity
                )
                flash('Success!', 'alert-success')
                return redirect(url_for('budgetary'))

            # If other-investment is chosen for investment_type...
            elif investment_type == 'other-investment':
                # Update investment table
                db.execute(
                    "INSERT INTO investment (user_id, transaction_id, investment_type, investment_comment, buy_or_sell, quantity) \
                    VALUES (?, ?, ?, ?, ?, ?)",
                    user_id, transaction_id, investment_type, other_investment, buy_sell, quantity
                )
                flash('Success!', 'alert-success')
                return redirect(url_for('budgetary'))
        
        elif budgetary_type == 'debt':
            # Get existing debtor_or_creditor in a list
            existing_debtors = db.execute (
                "SELECT debtor_or_creditor FROM debt WHERE user_id = ?", user_id
            )
            existing_debtors_list = [row['debtor_or_creditor'] for row in existing_debtors]

            # If user chooses borrow or lend as debt_category...
            if debt_category == 'borrow' or debt_category == 'lend':
                # Ensure user does not input same debtor_creditor names
                if debtor_creditor in existing_debtors_list:
                    flash('Debtor or creditor already exists!', 'alert-danger')
                    return redirect(url_for('budgetary'))
                
                # Update transactions table
                db.execute(
                    "INSERT INTO transactions (payment_method, currency, amount, amount_in_usd, transaction_date) VALUES (?, ?, ?, ?, ?)",
                    payment_method, currency, amount, usd_amount, date
                )
            
                # Get the last row of transactions table (to get transaction id)
                row = db.execute(
                    "SELECT * FROM transactions ORDER BY id DESC LIMIT 1"
                )
                transaction_id = row[0]["id"]

                # Update debt table
                db.execute(
                    "INSERT INTO debt (user_id, transaction_id, debtor_or_creditor, debt_category, interest_rate) \
                    VALUES (?, ?, ?, ?, ?)",
                    user_id, transaction_id, debtor_creditor, debt_category, interest_rate
                )
                flash('Success!', 'alert-success')
                return redirect(url_for('budgetary'))
            
            # If user chooses repay as debt_category...
            elif debt_category == 'repay':
                # Return error if the user selects repay and chooses someone who's not in the borrow or lend list
                if debtor_creditor not in existing_debtors_list:
                    flash('Choose someone from the existing debtors or creditors!', 'alert-danger')
                    return redirect(url_for('budgetary'))

                # Day difference between today and the day where debt is first borrowed.
                day_diff = db.execute(
                    "SELECT ROUND (julianday('now') - julianday(transaction_date)) \
                    AS day_diff FROM transactions WHERE id = ( \
                    SELECT transaction_id FROM debt WHERE debtor_or_creditor = ? ORDER BY id DESC)",
                    debtor_creditor
                )

                original_interest = db.execute(
                    "SELECT interest_rate FROM debt WHERE debtor_or_creditor = ? ORDER BY id DESC",
                    debtor_creditor
                )

                original_debt = db.execute(
                    "SELECT payment_method, currency, amount FROM transactions WHERE id = ( \
                    SELECT transaction_id FROM debt WHERE debtor_or_creditor = ? ORDER BY id DESC)",
                    debtor_creditor
                )

                original_category = db.execute(
                    "SELECT debt_category FROM debt WHERE debtor_or_creditor = ? ORDER BY id DESC",
                    debtor_creditor
                )
                
                day_diff_value = day_diff[0]['day_diff']
                original_interest_rate = original_interest[0]['interest_rate']
                original_payment_method = original_debt[0]['payment_method']
                original_debt_currency = original_debt[0]['currency']
                original_debt_amount = original_debt[0]['amount']
                original_debt_category = original_category[0]['debt_category']

                # Find out the number of months
                months = day_diff_value / 30

                # Find out the total amount to be repaid
                total_debt = round(original_debt_amount * (1 + (original_interest_rate * months / 100)), 2)

                if currency != original_debt_currency:
                    flash(f'Original debt currency is in {original_debt_currency.upper()}!', 'alert-danger')
                    return redirect(url_for('budgetary'))

                if float(amount) > total_debt:
                    flash(f'You only need to pay/receive {original_debt_currency.upper()} {total_debt}!', 'alert-danger')
                    return redirect(url_for('budgetary'))

                # Update transactions table
                db.execute(
                    "INSERT INTO transactions (payment_method, currency, amount, amount_in_usd, transaction_date) VALUES (?, ?, ?, ?, ?)",
                    payment_method, currency, amount, usd_amount, date
                )
            
                # Get the last row of transactions table (to get transaction id)
                row = db.execute(
                    "SELECT * FROM transactions ORDER BY id DESC LIMIT 1"
                )
                transaction_id = row[0]["id"]
                
                # Update debt table for repaid debt amount
                db.execute(
                    "INSERT INTO debt (user_id, transaction_id, debtor_or_creditor, debt_category) \
                    VALUES (?, ?, ?, ?)",
                    user_id, transaction_id, debtor_creditor, debt_category
                )

                # Get the value of remaining debt amount
                remaining_debt_amount = total_debt - float(amount)

                # Convert the remaining amount to usd
                remaining_usd_amount = amount_in_usd(currency, remaining_debt_amount)

                # Update transactions table for remaining debt amount
                db.execute(
                "INSERT INTO transactions (payment_method, currency, amount, amount_in_usd, transaction_date) VALUES (?, ?, ?, ?, ?)",
                original_payment_method, currency, remaining_debt_amount, remaining_usd_amount, date
                )

                # Get the last row of transactions table (to get transaction id)
                row = db.execute(
                "SELECT * FROM transactions ORDER BY id DESC LIMIT 1"
                )
                new_transaction_id = row[0]["id"]

                # Update the debt table for remaining debt amount
                db.execute(
                    "INSERT INTO debt (user_id, transaction_id, debtor_or_creditor, debt_category, interest_rate) \
                    VALUES (?, ?, ?, ?, ?)",
                    user_id, new_transaction_id, debtor_creditor, original_debt_category, original_interest_rate
                )

                flash('Success!', 'alert-success')
                return redirect(url_for('budgetary'))
                
    return render_template("budgetary.html")


@app.route("/analysis", methods=["GET", "POST"])
@login_required
def analysis():
    user_id = session.get("user_id")
    total_assets = 0
    total_cash_bank = 0
    inflow_income = 0
    inflow_investment = 0
    inflow_debt = 0
    outflow_expense = 0
    outflow_investment = 0
    outflow_debt = 0
    
    # Create analysis routes
    if request.method == "GET":

        # Write database code for homepage investments table
        investment_rows = db.execute (
            "SELECT \
                investment.investment_type, \
                CASE \
                    WHEN investment.investment_type = 'other-investment' THEN investment.investment_comment \
                    WHEN investment.symbol_real_estate_type = 'otherRealEstate' THEN investment.real_estate_comment \
                    ELSE investment.symbol_real_estate_type \
                END AS symbol, \
                SUM(CASE WHEN investment.buy_or_sell = 'buy' THEN investment.quantity ELSE -investment.quantity END) AS quantity, \
                SUM(CASE WHEN investment.buy_or_sell = 'buy' THEN transactions.amount_in_usd ELSE -transactions.amount_in_usd END) AS original_value \
            FROM investment JOIN transactions \
            ON investment.transaction_id = transactions.id \
            WHERE investment.user_id = ? \
            GROUP BY \
                investment.investment_type, \
                CASE \
                    WHEN investment.investment_type = 'other-investment' THEN investment.investment_comment \
                    WHEN investment.symbol_real_estate_type = 'otherRealEstate' THEN investment.real_estate_comment \
                    ELSE investment.symbol_real_estate_type \
                END", user_id
        )

        new_investment_rows = []
        investment_total = 0
        profit_loss_total = 0
        for row in investment_rows:
            quantity = round(float(row['quantity']), 2)

            if row['investment_type'] == 'stock':
                stock_quote = stock_lookup(row['symbol'])
                stock_price = stock_quote['price']
                market_value = round(stock_price * quantity, 2)
                profit_loss = round(market_value - float(row['original_value']), 2)
                row['original_value'] = market_value
                row['profit_loss'] = profit_loss
                row['quantity'] = quantity
                investment_total = investment_total + market_value
                profit_loss_total = profit_loss_total + profit_loss

                new_investment_rows.append(row)

            elif row['investment_type'] == 'cryptocurrency':
                crypto_quote = crypto_lookup(row['symbol'])
                crypto_price = crypto_quote['price']
                market_value = round(crypto_price * quantity, 2)
                profit_loss = round(market_value - float(row['original_value']), 2)
                row['original_value'] = market_value
                row['profit_loss'] = profit_loss
                row['quantity'] = quantity
                investment_total = investment_total + market_value
                profit_loss_total = profit_loss_total + profit_loss

                new_investment_rows.append(row)

            else:
                row['profit_loss'] = 0
                row['quantity'] = quantity
                investment_total = investment_total + row['original_value']

                new_investment_rows.append(row)

        total_assets = total_assets + investment_total
   
        # Write database code for Debts & Receivables table
        debt_rows = db.execute (
            "SELECT \
            debt.debt_category, debt.debtor_or_creditor, transactions.transaction_date, debt.interest_rate, transactions.currency, \
            transactions.amount \
            FROM debt JOIN transactions \
            ON debt.transaction_id = transactions.id \
            WHERE debt.user_id = ? and debt.id IN (SELECT MAX(debt.id) FROM debt GROUP BY debtor_or_creditor)", user_id
        )

        new_debt_rows = []
        debt_total = 0
        interest_total = 0
        for row in debt_rows:
            original_debt_amount = float(row['amount'])
            interest_rate = float(row['interest_rate'])
            days_diff = days_difference(row['transaction_date'])
            
            # Find out the number of months
            months = days_diff / 30

            # Calculate interest
            interest = round((original_debt_amount * interest_rate * months / 100), 2)
            interest_in_usd = amount_in_usd(row['currency'], interest)

            # Find out the total amount to be repaid
            total_debt = round(original_debt_amount + interest, 2)
            total_debt_usd = amount_in_usd(row['currency'], total_debt)
        
            row['amount'] = total_debt
            row['interest'] = interest

            if row['debt_category'] == 'borrow':
                debt_total = debt_total - total_debt_usd
                interest_total = interest_total - interest_in_usd

            elif row['debt_category'] == 'lend':
                debt_total = debt_total + total_debt_usd
                interest_total = interest_total + interest_in_usd

            new_debt_rows.append(row)

        total_assets = total_assets + debt_total

        # Write database code for inflows breakdown
        # First, get inflow-income data from history
        inflow_income_rows = db.execute(
            "SELECT \
                transactions.transaction_date AS date, \
                'income' AS type, \
                income.income_type AS category, \
                income.comment AS comment, \
                transactions.payment_method AS payment_method, \
                transactions.currency AS currency, \
                transactions.amount AS amount, \
                transactions.amount_in_usd AS amount_in_usd \
            FROM \
                income JOIN transactions ON income.transaction_id = transactions.id \
            WHERE \
                income.user_id = ?", user_id)
        
        # Get amount of each income category in usd
        salary = 0
        bank_interest = 0
        other_income = 0

        for row in inflow_income_rows:
            # Salary-related rows
            if row['category'] == 'salary':
                salary = salary + round(float(row['amount_in_usd']), 2)

            # Bank-interest-related rows
            if row['category'] == 'bank-interest':
                bank_interest = bank_interest + round(float(row['amount_in_usd']), 2)

            # Other-income-related rows
            if row['category'] == 'other-income':
                other_income = other_income + round(float(row['amount_in_usd']), 2)

            # Update inflow income
            inflow_income = inflow_income + round(float(row['amount_in_usd']), 2)

        # Write database code for expenses breakdown
        outflow_expense_rows = db.execute(
            "SELECT \
                transactions.transaction_date AS date, \
                'expense' AS type, \
                spending.spending_type AS category, \
                spending.comment AS comment, \
                transactions.payment_method AS payment_method, \
                transactions.currency AS currency, \
                transactions.amount AS amount, \
                transactions.amount_in_usd AS amount_in_usd \
            FROM \
                spending JOIN transactions ON spending.transaction_id = transactions.id \
            WHERE \
                spending.user_id = ?", user_id)
        

        # Get amount of each expense category in usd
        food = 0
        transportation = 0
        clothing = 0
        rent = 0
        other_expense = 0

        for row in outflow_expense_rows:
            # Food-related rows
            if row['category'] == 'food':
                food = food + round(float(row['amount_in_usd']), 2)

            # Transportation-related rows
            if row['category'] == 'transportation':
                transportation = transportation + round(float(row['amount_in_usd']), 2)

            # Clothing-related rows
            if row['category'] == 'clothing':
                clothing = clothing + round(float(row['amount_in_usd']), 2)

            # Rent-related rows
            if row['category'] == 'rent':
                rent = rent + round(float(row['amount_in_usd']), 2)

            # Other-expense-related rows
            if row['category'] == 'other-spending':
                other_expense = other_expense + round(float(row['amount_in_usd']), 2)

            # Update outflow expense
            outflow_expense = outflow_expense + round(float(row['amount_in_usd']), 2)

        # Write database query for investment breakdown
        inflow_outflow_investment_rows = db.execute(
            "SELECT \
                transactions.transaction_date AS date, \
                investment.investment_type AS type, \
            CASE \
                WHEN investment.investment_type = 'other-investment' THEN investment.investment_comment \
                WHEN investment.symbol_real_estate_type = 'otherRealEstate' THEN investment.real_estate_comment \
                ELSE investment.symbol_real_estate_type \
            END AS symbol_comment, \
                investment.buy_or_sell AS buy_sell, \
                investment.quantity, \
                transactions.payment_method, \
                transactions.currency, \
                transactions.amount, \
                transactions.amount_in_usd \
            FROM \
                investment JOIN transactions ON investment.transaction_id = transactions.id \
            WHERE \
                investment.user_id = ?", user_id
        )
        
        # Get amount of each inflow investment category in usd
        stock_sell = 0
        crypto_sell = 0
        real_estate_sell = 0
        other_investment_sell = 0

        # Get amount of each outflow investment category in usd
        stock_buy = 0
        crypto_buy = 0
        real_estate_buy = 0
        other_investment_buy = 0

        for row in inflow_outflow_investment_rows:
            # Inflow variables for selling investments
            if row['type'] == 'stock' and row['buy_sell'] == 'sell':
                stock_sell = stock_sell + round(float(row['amount_in_usd']), 2)

            if row['type'] == 'cryptocurrency' and row['buy_sell'] == 'sell':
                crypto_sell = crypto_sell + round(float(row['amount_in_usd']), 2)
            
            if row['type'] == 'real-estate' and row['buy_sell'] == 'sell':
                real_estate_sell = real_estate_sell + round(float(row['amount_in_usd']), 2)

            if row['type'] == 'other-investment' and row['buy_sell'] == 'sell':
                other_investment_sell = other_investment_sell + round(float(row['amount_in_usd']), 2)

            # Outflow variables for buying investments
            if row['type'] == 'stock' and row['buy_sell'] == 'buy':
                stock_buy = stock_buy + round(float(row['amount_in_usd']), 2)

            if row['type'] == 'cryptocurrency' and row['buy_sell'] == 'buy':
                crypto_buy = crypto_buy + round(float(row['amount_in_usd']), 2)
            
            if row['type'] == 'real-estate' and row['buy_sell'] == 'buy':
                real_estate_buy = real_estate_buy + round(float(row['amount_in_usd']), 2)

            if row['type'] == 'other-investment' and row['buy_sell'] == 'buy':
                other_investment_buy = other_investment_buy + round(float(row['amount_in_usd']), 2)

        # Update inflow investment
        inflow_investment = stock_sell + crypto_sell + real_estate_sell + other_investment_sell

        # Update outflow investment
        outflow_investment = stock_buy + crypto_buy + real_estate_buy + other_investment_buy

        # Write database query for debt breakdown
        inflow_outflow_debt_rows = db.execute(
            "WITH ranked AS ( \
            SELECT \
                transactions.transaction_date AS date, \
                debt.id AS debt_id, \
                debt.user_id AS user_id, \
                debt.debt_category AS category, \
                debt.debtor_or_creditor AS debtor_or_creditor, \
                debt.interest_rate AS interest_rate, \
                transactions.payment_method AS payment_method, \
                transactions.currency AS currency, \
                transactions.amount AS amount, \
                transactions.amount_in_usd AS amount_in_usd, \
                ROW_NUMBER() OVER ( \
                    PARTITION BY \
                    CASE \
                        WHEN debt.debt_category IN ('borrow', 'lend') THEN debt.debtor_or_creditor \
                        WHEN debt.debt_category = 'repay' THEN debt.id \
                        ELSE NULL \
                    END \
                    ORDER BY debt.id ASC) AS row \
            FROM \
                debt JOIN transactions ON debt.transaction_id = transactions.id \
            WHERE \
                debt.user_id = ?) \
            SELECT \
                date, \
                category, \
                debtor_or_creditor, \
                interest_rate, \
                payment_method, \
                currency, \
                amount, \
                amount_in_usd \
            FROM \
                ranked \
            WHERE \
                (row = 1 AND category IN ('borrow', 'lend')) \
                OR category = 'repay' \
            ORDER BY \
                debt_id \
            ASC", user_id)

        # Get amount of each inflow debt category in usd
        borrow = 0
        receivable_repay = 0

        # Get amount of each outflow debt category in usd
        lend = 0
        debt_repay = 0

        for row in inflow_outflow_debt_rows:
            # Inflow variables for debts
            if row['category'] == 'borrow':
                borrow = borrow + round(float(row['amount_in_usd']), 2)

            if row['category'] == 'repay':
                if repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'lend':
                    receivable_repay = receivable_repay + round(float(row['amount_in_usd']), 2)

                elif repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'borrow':
                    debt_repay = debt_repay + round(float(row['amount_in_usd']), 2)

            if row['category'] == 'lend':
                lend = lend + round(float(row['amount_in_usd']), 2)

        # Update inflow debt
        inflow_debt = borrow + receivable_repay

        # Update outflow debt
        outflow_debt = lend + debt_repay

        # Update inflows and outflows
        inflows = inflow_income + inflow_investment + inflow_debt
        outflows = outflow_expense + outflow_investment + outflow_debt

        # Update net balance
        net_balance = inflows - outflows

        # Update total assets
        total_assets = total_assets + net_balance

        return render_template("analysis.html", total_assets=total_assets, total_cash_bank=total_cash_bank, investment_total=investment_total, \
            debt_total=debt_total, inflow_income=inflow_income, inflow_investment=inflow_investment, inflow_debt=inflow_debt, outflow_expense=outflow_expense, \
            outflow_investment=outflow_investment, outflow_debt=outflow_debt, inflows=inflows, outflows=outflows, net_balance=net_balance, \
            salary=salary, bank_interest=bank_interest, other_income=other_income, food=food, transportation=transportation, clothing=clothing, \
            rent=rent, other_expense=other_expense, stock_sell=stock_sell, crypto_sell=crypto_sell, real_estate_sell=real_estate_sell, \
            other_investment_sell=other_investment_sell, stock_buy=stock_buy, crypto_buy=crypto_buy, real_estate_buy=real_estate_buy, \
            other_investment_buy=other_investment_buy, borrow=borrow, receivable_repay=receivable_repay, lend=lend, debt_repay=debt_repay)


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    user_id = session.get("user_id")
    # Create budgetary logs
    income_spending_query = """
        SELECT
            transactions.transaction_date AS date,
            'income' AS type,
            income.income_type AS category,
            income.comment AS comment,
            transactions.payment_method AS payment_method,
            transactions.currency AS currency,
            transactions.amount AS amount
        FROM
            income JOIN transactions ON income.transaction_id = transactions.id
        {income_where_clause}
        UNION ALL
        SELECT
            transactions.transaction_date AS date,
            'expense' AS type,
            spending.spending_type AS category,
            spending.comment AS comment,
            transactions.payment_method AS payment_method,
            transactions.currency AS currency,
            transactions.amount AS amount
        FROM
            spending JOIN transactions ON spending.transaction_id = transactions.id
        {spending_where_clause}
        ORDER BY transactions.transaction_date
        """
    
    investment_query = """
        SELECT
            transactions.transaction_date AS date,
            investment.investment_type AS type,
        CASE
            WHEN investment.investment_type = 'other-investment' THEN investment.investment_comment
            WHEN investment.symbol_real_estate_type = 'otherRealEstate' THEN investment.real_estate_comment
            ELSE investment.symbol_real_estate_type
        END AS symbol_comment,
            investment.buy_or_sell AS buy_sell,
            investment.quantity,
            transactions.payment_method,
            transactions.currency,
            transactions.amount
        FROM
            investment JOIN transactions ON investment.transaction_id = transactions.id
        {investment_where_clause}
        ORDER BY transactions.transaction_date
        """
    
    debt_query = """
        SELECT
            transactions.transaction_date AS date,
            debt.debt_category AS category,
            debt.debtor_or_creditor,
            debt.interest_rate,
            transactions.payment_method,
            transactions.currency,
            transactions.amount
        FROM
            debt JOIN transactions ON debt.transaction_id = transactions.id
        {debt_where_clause}
        ORDER BY debt.debtor_or_creditor, transactions.transaction_date
        """
    
    income_where_clause = "WHERE income.user_id = ?"
    spending_where_clause = "WHERE spending.user_id = ?"
    investment_where_clause = "WHERE investment.user_id = ?"
    debt_where_clause = "WHERE debt.user_id = ?"

    if request.method == "GET":
        income_spending_query = income_spending_query.format(income_where_clause=income_where_clause, spending_where_clause=spending_where_clause)
        income_spending_rows = db.execute(
            income_spending_query, user_id, user_id
        )
        
        investment_query = investment_query.format(investment_where_clause=investment_where_clause)
        investment_rows = db.execute(
            investment_query, user_id
        )

        debt_query = debt_query.format(debt_where_clause=debt_where_clause)
        debt_rows = db.execute(
            debt_query, user_id
        )

        for row in debt_rows:
                if row['category'] == 'repay':
                    if repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'lend':
                        row['category'] = 'lrepay'

                    elif repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'borrow':
                        row['category'] = 'brepay'

        return render_template("history.html", income_spending_rows=income_spending_rows, investment_rows=investment_rows, \
            debt_rows=debt_rows, currency=currency)

    else:
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
    
        if start_date and end_date:
            income_where_clause = "WHERE income.user_id = ? and transactions.transaction_date BETWEEN ? AND ?"
            spending_where_clause = "WHERE spending.user_id = ? and transactions.transaction_date BETWEEN ? AND ?"
            investment_where_clause = "WHERE investment.user_id = ? and transactions.transaction_date BETWEEN ? AND ?"
            debt_where_clause = "WHERE debt.user_id = ? and transactions.transaction_date BETWEEN ? AND ?"

            income_spending_query = income_spending_query.format(income_where_clause=income_where_clause, spending_where_clause=spending_where_clause)
            income_spending_rows = db.execute(
                income_spending_query, user_id, start_date, end_date, user_id, start_date, end_date
            )

            investment_query = investment_query.format(investment_where_clause=investment_where_clause)
            investment_rows = db.execute(
                investment_query, user_id, start_date, end_date
            )

            debt_query = debt_query.format(debt_where_clause=debt_where_clause)
            debt_rows = db.execute(
                debt_query, user_id, start_date, end_date
            )

            for row in debt_rows:
                if row['category'] == 'repay':
                    if repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'lend':
                        row['category'] = 'lrepay'

                    elif repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'borrow':
                        row['category'] = 'brepay'

            return render_template("history.html", income_spending_rows=income_spending_rows, investment_rows=investment_rows, \
                debt_rows=debt_rows, currency=currency, start_date=start_date, end_date=end_date)

        else:
            income_spending_query = income_spending_query.format(income_where_clause=income_where_clause, spending_where_clause=spending_where_clause)
            income_spending_rows = db.execute(
                income_spending_query, user_id, user_id
            )

            investment_query = investment_query.format(investment_where_clause=investment_where_clause)
            investment_rows = db.execute(
                investment_query, user_id
            )

            debt_query = debt_query.format(debt_where_clause=debt_where_clause)
            debt_rows = db.execute(
                debt_query, user_id
            )

            for row in debt_rows:
                if row['category'] == 'repay':
                    if repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'lend':
                        row['category'] = 'lrepay'

                    elif repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'borrow':
                        row['category'] = 'brepay'
        
            return render_template("history.html", income_spending_rows=income_spending_rows, investment_rows=investment_rows, \
                debt_rows=debt_rows, currency=currency)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    flash_messages = session.get('_flashes', [])

    # Forget any user_id
    session.clear()

    # Restore flash messages after clearing session
    if flash_messages:
        session['_flashes'] = flash_messages

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash('Please provide username!', 'alert-danger')
            return redirect(url_for('login'))

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash('Please provide password!', 'alert-danger')
            return redirect(url_for('login'))

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash('Invalid username or password!', 'alert-danger')
            # Clear the session but keep flash messages
            return redirect(url_for('login'))

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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    flash_messages = session.get('_flashes', [])

    # Forget any user_id
    session.clear()

    # Restore flash messages after clearing session
    if flash_messages:
        session['_flashes'] = flash_messages

    # Get registered user data via POST
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash('Please provide username!', 'alert-danger')
            return redirect(url_for('register'))

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash('Please provide password!', 'alert-danger')
            return redirect(url_for('register'))

        # Ensure re-type password field was submitted
        elif not request.form.get("confirmation"):
            flash('Please confirm password!', 'alert-danger')
            return redirect(url_for('register'))

        # Ensure password and re-typed password match
        elif request.form.get("password") != request.form.get("confirmation"):
            flash('Passwords do not match!', 'alert-danger')
            return redirect(url_for('register'))

        # Register username and hashed password in the database
        try:
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get(
                    "username"), generate_password_hash(request.form.get("password"))
            )
            # Redirect user to home page
            return redirect("/login")

        except:
            flash('Username already exists!', 'alert-danger')
            return redirect(url_for('register'))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    

@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    # Get registered user data via POST
    if request.method == "POST":
        user_id = session.get("user_id")
        old_password = request.form.get("old-password")
        new_password = request.form.get("new-password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not old_password:
            flash('Please input old password!', 'alert-danger')
            return redirect(url_for('change_password'))

        # Ensure password was submitted
        if not new_password:
            flash('Please input new password!', 'alert-danger')
            return redirect(url_for('change_password'))

        # Ensure re-type password field was submitted
        if not confirmation:
            flash('Please confirm new password!', 'alert-danger')
            return redirect(url_for('change_password'))

        # Ensure password and re-typed password match
        if new_password != confirmation:
            flash('New passwords do not match!', 'alert-danger')
            return redirect(url_for('change_password'))
        
        old_password_hash = db.execute("SELECT hash FROM users WHERE id = ?", user_id)
        print(f"old_password_hash: {old_password_hash}")

        # Check if old password is correct
        if not check_password_hash(old_password_hash[0]['hash'], old_password):
            flash('Wrong old password!', 'alert-danger')
            return redirect(url_for('change_password'))
        
        elif check_password_hash(old_password_hash[0]['hash'], old_password):
            db.execute(
                "UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(new_password), user_id
            )
            flash('Password changed successfully!', 'alert-success')
            return redirect(url_for('change_password'))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change-password.html")
    

# Convert usd values into other currencies
@app.route("/convert_currency")
def convert_currency():
    final_currency = request.args.get('final_currency')
    value_in_usd = float(request.args.get('value_in_usd'))

    if final_currency.upper() == 'USD':
        converted_amount = round(float(value_in_usd), 2)
        return jsonify({'converted_amount': currency(converted_amount)})
    
    elif final_currency.upper() == 'MMK':
        exchange_rate = 4970
        converted_amount = round(exchange_rate * float(value_in_usd), 2)
        return jsonify({'converted_amount': currency(converted_amount)})
    
    else:
        exchange_rate = forex_rate(final_currency)["rate"]
        converted_amount = round(exchange_rate * float(value_in_usd), 2)
        return jsonify({'converted_amount': currency(converted_amount)})
    

# Convert usd values for profits or interests into other currencies
@app.route("/convert_profit_currency")
def convert_profit_currency():
    final_currency = request.args.get('final_currency')
    value_in_usd = float(request.args.get('value_in_usd'))

    if final_currency.upper() == 'USD':
        converted_amount = round(float(value_in_usd), 2)
        return jsonify({'converted_amount': profit(converted_amount)})
    
    elif final_currency.upper() == 'MMK':
        exchange_rate = 4970
        converted_amount = round(exchange_rate * float(value_in_usd), 2)
        return jsonify({'converted_amount': profit(converted_amount)})
    
    else:
        exchange_rate = forex_rate(final_currency)["rate"]
        converted_amount = round(exchange_rate * float(value_in_usd), 2)
        return jsonify({'converted_amount': profit(converted_amount)})
    

# Date filter in analysis page
@app.route("/analysis_filter")
def analysis_filter():
    user_id = session.get("user_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Initialize query lists
    inflow_income_rows = []
    outflow_expense_rows = []
    inflow_outflow_investment_rows = []
    inflow_outflow_debt_rows = []

    # Write database code for inflows breakdown
    # First, get inflow-income data from history
    inflow_income_rows_query = """
        SELECT \
            transactions.transaction_date AS date, \
            'income' AS type, \
            income.income_type AS category, \
            income.comment AS comment, \
            transactions.payment_method AS payment_method, \
            transactions.currency AS currency, \
            transactions.amount AS amount, \
            transactions.amount_in_usd AS amount_in_usd \
        FROM \
            income JOIN transactions ON income.transaction_id = transactions.id \
        WHERE \
            income.user_id = ? {where_clause} """
    
    # Write database code for expenses breakdown
    outflow_expense_rows_query = """
        SELECT \
            transactions.transaction_date AS date, \
            'expense' AS type, \
            spending.spending_type AS category, \
            spending.comment AS comment, \
            transactions.payment_method AS payment_method, \
            transactions.currency AS currency, \
            transactions.amount AS amount, \
            transactions.amount_in_usd AS amount_in_usd \
        FROM \
            spending JOIN transactions ON spending.transaction_id = transactions.id \
        WHERE \
            spending.user_id = ? {where_clause} """

    # Write database query for investment breakdown
    inflow_outflow_investment_rows_query = """
        SELECT \
            transactions.transaction_date AS date, \
            investment.investment_type AS type, \
        CASE \
            WHEN investment.investment_type = 'other-investment' THEN investment.investment_comment \
            WHEN investment.symbol_real_estate_type = 'otherRealEstate' THEN investment.real_estate_comment \
            ELSE investment.symbol_real_estate_type \
        END AS symbol_comment, \
            investment.buy_or_sell AS buy_sell, \
            investment.quantity, \
            transactions.payment_method, \
            transactions.currency, \
            transactions.amount, \
            transactions.amount_in_usd \
        FROM \
            investment JOIN transactions ON investment.transaction_id = transactions.id \
        WHERE \
            investment.user_id = ? {where_clause} """
    
    
    # Write database query for debt breakdown
    inflow_outflow_debt_rows_query = """
        WITH ranked AS ( \
        SELECT \
            transactions.transaction_date AS date, \
            debt.id AS debt_id, \
            debt.user_id AS user_id, \
            debt.debt_category AS category, \
            debt.debtor_or_creditor AS debtor_or_creditor, \
            debt.interest_rate AS interest_rate, \
            transactions.payment_method AS payment_method, \
            transactions.currency AS currency, \
            transactions.amount AS amount, \
            transactions.amount_in_usd AS amount_in_usd, \
            ROW_NUMBER() OVER ( \
                PARTITION BY \
                CASE \
                    WHEN debt.debt_category IN ('borrow', 'lend') THEN debt.debtor_or_creditor \
                    WHEN debt.debt_category = 'repay' THEN debt.id \
                    ELSE NULL \
                END \
                ORDER BY debt.id ASC) AS row \
        FROM \
            debt JOIN transactions ON debt.transaction_id = transactions.id \
        WHERE \
            debt.user_id = ? {where_clause}) \
        SELECT \
            date, \
            category, \
            debtor_or_creditor, \
            interest_rate, \
            payment_method, \
            currency, \
            amount, \
            amount_in_usd \
        FROM \
            ranked \
        WHERE \
            (row = 1 AND category IN ('borrow', 'lend')) \
            OR category = 'repay' \
        ORDER BY \
            debt_id \
        ASC """

    if start_date and end_date:
        # Format where clause for query
        where_clause = "and transactions.transaction_date BETWEEN ? AND ?"

        inflow_income_rows_query = inflow_income_rows_query.format(where_clause=where_clause)
        inflow_income_rows = db.execute(
            inflow_income_rows_query, user_id, start_date, end_date
        )

        outflow_expense_rows_query = outflow_expense_rows_query.format(where_clause=where_clause)
        outflow_expense_rows = db.execute(
            outflow_expense_rows_query, user_id, start_date, end_date
        )

        inflow_outflow_investment_rows_query = inflow_outflow_investment_rows_query.format(where_clause=where_clause)
        inflow_outflow_investment_rows = db.execute(
            inflow_outflow_investment_rows_query, user_id, start_date, end_date
        )

        inflow_outflow_debt_rows_query = inflow_outflow_debt_rows_query.format(where_clause=where_clause)
        inflow_outflow_debt_rows = db.execute(
            inflow_outflow_debt_rows_query, user_id, start_date, end_date
        )

    else:
        # Format where clause for query
        where_clause = ""

        inflow_income_rows_query = inflow_income_rows_query.format(where_clause=where_clause)
        inflow_income_rows = db.execute(
            inflow_income_rows_query, user_id
        )

        outflow_expense_rows_query = outflow_expense_rows_query.format(where_clause=where_clause)
        outflow_expense_rows = db.execute(
            outflow_expense_rows_query, user_id
        )

        inflow_outflow_investment_rows_query = inflow_outflow_investment_rows_query.format(where_clause=where_clause)
        inflow_outflow_investment_rows = db.execute(
            inflow_outflow_investment_rows_query, user_id
        )

        inflow_outflow_debt_rows_query = inflow_outflow_debt_rows_query.format(where_clause=where_clause)
        inflow_outflow_debt_rows = db.execute(
            inflow_outflow_debt_rows_query, user_id
        )

    # initialize variables
    inflow_income = 0
    outflow_expense = 0
    
    # Get amount of each income category in usd
    salary = 0
    bank_interest = 0
    other_income = 0

    for row in inflow_income_rows:
        # Salary-related rows
        if row['category'] == 'salary':
            salary = salary + round(float(row['amount_in_usd']), 2)

        # Bank-interest-related rows
        if row['category'] == 'bank-interest':
            bank_interest = bank_interest + round(float(row['amount_in_usd']), 2)

        # Other-income-related rows
        if row['category'] == 'other-income':
            other_income = other_income + round(float(row['amount_in_usd']), 2)

        # Update inflow income
        inflow_income = inflow_income + round(float(row['amount_in_usd']), 2)  

    # Get amount of each expense category in usd
    food = 0
    transportation = 0
    clothing = 0
    rent = 0
    other_expense = 0

    for row in outflow_expense_rows:
        # Food-related rows
        if row['category'] == 'food':
            food = food + round(float(row['amount_in_usd']), 2)

        # Transportation-related rows
        if row['category'] == 'transportation':
            transportation = transportation + round(float(row['amount_in_usd']), 2)

        # Clothing-related rows
        if row['category'] == 'clothing':
            clothing = clothing + round(float(row['amount_in_usd']), 2)

        # Rent-related rows
        if row['category'] == 'rent':
            rent = rent + round(float(row['amount_in_usd']), 2)

        # Other-expense-related rows
        if row['category'] == 'other-spending':
            other_expense = other_expense + round(float(row['amount_in_usd']), 2)

        # Update outflow expense
        outflow_expense = outflow_expense + round(float(row['amount_in_usd']), 2)
    
    # Get amount of each inflow investment category in usd
    stock_sell = 0
    crypto_sell = 0
    real_estate_sell = 0
    other_investment_sell = 0

    # Get amount of each outflow investment category in usd
    stock_buy = 0
    crypto_buy = 0
    real_estate_buy = 0
    other_investment_buy = 0

    for row in inflow_outflow_investment_rows:
        # Inflow variables for selling investments
        if row['type'] == 'stock' and row['buy_sell'] == 'sell':
            stock_sell = stock_sell + round(float(row['amount_in_usd']), 2)

        if row['type'] == 'cryptocurrency' and row['buy_sell'] == 'sell':
            crypto_sell = crypto_sell + round(float(row['amount_in_usd']), 2)
        
        if row['type'] == 'real-estate' and row['buy_sell'] == 'sell':
            real_estate_sell = real_estate_sell + round(float(row['amount_in_usd']), 2)

        if row['type'] == 'other-investment' and row['buy_sell'] == 'sell':
            other_investment_sell = other_investment_sell + round(float(row['amount_in_usd']), 2)

        # Outflow variables for buying investments
        if row['type'] == 'stock' and row['buy_sell'] == 'buy':
            stock_buy = stock_buy + round(float(row['amount_in_usd']), 2)

        if row['type'] == 'cryptocurrency' and row['buy_sell'] == 'buy':
            crypto_buy = crypto_buy + round(float(row['amount_in_usd']), 2)
        
        if row['type'] == 'real-estate' and row['buy_sell'] == 'buy':
            real_estate_buy = real_estate_buy + round(float(row['amount_in_usd']), 2)

        if row['type'] == 'other-investment' and row['buy_sell'] == 'buy':
            other_investment_buy = other_investment_buy + round(float(row['amount_in_usd']), 2)

    # Update inflow investment
    inflow_investment = stock_sell + crypto_sell + real_estate_sell + other_investment_sell

    # Update outflow investment
    outflow_investment = stock_buy + crypto_buy + real_estate_buy + other_investment_buy

    # Get amount of each inflow debt category in usd
    borrow = 0
    receivable_repay = 0

    # Get amount of each outflow debt category in usd
    lend = 0
    debt_repay = 0

    for row in inflow_outflow_debt_rows:
        # Inflow variables for debts
        if row['category'] == 'borrow':
            borrow = borrow + round(float(row['amount_in_usd']), 2)

        if row['category'] == 'repay':
            if repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'lend':
                receivable_repay = receivable_repay + round(float(row['amount_in_usd']), 2)

            elif repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'borrow':
                debt_repay = debt_repay + round(float(row['amount_in_usd']), 2)

        if row['category'] == 'lend':
            lend = lend + round(float(row['amount_in_usd']), 2)

    # Update inflow debt
    inflow_debt = borrow + receivable_repay

    # Update outflow debt
    outflow_debt = lend + debt_repay

    # Update inflows and outflows
    inflows = inflow_income + inflow_investment + inflow_debt
    outflows = outflow_expense + outflow_investment + outflow_debt

    # Update net balance
    net_balance = inflows - outflows

    return jsonify({'inflow_income': inflow_income, 'inflow_investment': inflow_investment, 'inflow_debt': inflow_debt, 'outflow_expense': outflow_expense, \
        'outflow_investment': outflow_investment, 'outflow_debt': outflow_debt, 'inflows': inflows, 'outflows': outflows, 'net_balance': net_balance, \
        'salary': salary, 'bank_interest': bank_interest, 'other_income': other_income, 'food': food, 'transportation': transportation, 'clothing': clothing, \
        'rent': rent, 'other_expense': other_expense, 'stock_sell': stock_sell, 'crypto_sell': crypto_sell, 'real_estate_sell': real_estate_sell, \
        'other_investment_sell': other_investment_sell, 'stock_buy': stock_buy, 'crypto_buy': crypto_buy, 'real_estate_buy': real_estate_buy, \
        'other_investment_buy': other_investment_buy, 'borrow': borrow, 'receivable_repay': receivable_repay, 'lend': lend, 'debt_repay': debt_repay})