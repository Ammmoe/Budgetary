import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, stock_lookup, amount_in_usd, crypto_lookup, profit, currency, days_difference, forex_rate, repay_check


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

# Set MMK exchange rate here
MMK_EXCHANGE_RATE = 5480
    

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
    total_cash_usd = 0
    total_bank_usd = 0

    # Retrieve the list of currencies
    # Convert to lowercase because in transactions database, currencies are in lowercase
    currencies_q = db.execute(
        "SELECT currency_code FROM user_currencies WHERE user_id = ?", user_id
    )

    # original_currencies will be passed to index.html
    original_currencies = [row['currency_code'].lower() for row in currencies_q]

    # create a copy of original_currencies to be used in the loop
    currencies = original_currencies.copy()

    # Get a list of currencies previously used by the user, which is not included in the user_currencies that they chose
    used_currencies_q = db.execute(
        "SELECT DISTINCT currency FROM transactions WHERE user_id = ?", user_id
    )

    used_currencies = [row['currency'].lower() for row in used_currencies_q]

    # Find currencies in used_currencies that are not in currencies
    not_included_currencies = list(set(used_currencies) - set(currencies))

    # Add not_included_currencies to the currencies list
    currencies.extend(not_included_currencies)

    # Create homepage routes
    if request.method == "GET":
        
        # Initialize dictionaries to store the results
        income_cash = {}
        income_bank = {}
        spending_cash = {}
        spending_bank = {}
        investment_cash_buy = {}
        investment_bank_buy = {}
        investment_cash_sell = {}
        investment_bank_sell = {}
        debt_cash_borrow = {}
        debt_cash_lend = {}
        debt_cash_brepay = {}
        debt_cash_lrepay = {}
        debt_bank_borrow = {}
        debt_bank_lend = {}
        debt_bank_brepay = {}
        debt_bank_lrepay = {}
        cash = {}
        bank = {}
        cash_str = {}
        bank_str = {}
        cash_in_usd = {}
        bank_in_usd = {}
        
        for currency_v in currencies:
            # Get income-related cash values
            income_cash_q = db.execute(
                "SELECT SUM(amount) AS income_cash FROM transactions WHERE payment_method = 'cash' and currency = ? and id IN \
                    (SELECT transaction_id FROM income WHERE user_id = ?)", currency_v, user_id 
            )

            income_cash[currency_v] = income_cash_q[0]['income_cash'] if income_cash_q[0]['income_cash'] is not None else 0

            # Get income-related bank deposit values
            income_bank_q = db.execute(
                "SELECT SUM(amount) AS income_bank FROM transactions WHERE payment_method = 'banking' and currency = ? and id IN \
                    (SELECT transaction_id FROM income WHERE user_id = ?)", currency_v, user_id 
            )

            income_bank[currency_v] = income_bank_q[0]['income_bank'] if income_bank_q[0]['income_bank'] is not None else 0

            # Get spending-related cash values
            spending_cash_q = db.execute(
                "SELECT SUM(amount) AS spending_cash FROM transactions WHERE payment_method = 'cash' and currency = ? and id IN \
                    (SELECT transaction_id FROM spending WHERE user_id = ?)", currency_v, user_id
            )

            spending_cash[currency_v] = spending_cash_q[0]['spending_cash'] if spending_cash_q[0]['spending_cash'] is not None else 0

            # Get spending-related bank deposit values
            spending_bank_q = db.execute(
                "SELECT SUM(amount) AS spending_bank FROM transactions WHERE payment_method = 'banking' and currency = ? and id IN \
                    (SELECT transaction_id FROM spending WHERE user_id = ?)", currency_v, user_id
            )

            spending_bank[currency_v] = spending_bank_q[0]['spending_bank'] if spending_bank_q[0]['spending_bank'] is not None else 0

            # Get investment-related cash values for buy
            investment_cash_buy_q = db.execute (
                "SELECT SUM(amount) AS investment_cash_buy FROM transactions WHERE payment_method = 'cash' and currency = ? and id IN \
                    (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'buy')", currency_v, user_id
            )

            investment_cash_buy[currency_v] = investment_cash_buy_q[0]['investment_cash_buy'] if investment_cash_buy_q[0]['investment_cash_buy'] is not None else 0

            # Get investment-related bank deposit values for buy
            investment_bank_buy_q = db.execute (
                "SELECT SUM(amount) AS investment_bank_buy FROM transactions WHERE payment_method = 'banking' and currency = ? and id IN \
                    (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'buy')", currency_v, user_id
            )

            investment_bank_buy[currency_v] = investment_bank_buy_q[0]['investment_bank_buy'] if investment_bank_buy_q[0]['investment_bank_buy'] is not None else 0

            # Get investment-related cash values for sell
            investment_cash_sell_q = db.execute (
                "SELECT SUM(amount) AS investment_cash_sell FROM transactions WHERE payment_method = 'cash' and currency = ? and id IN \
                    (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'sell')", currency_v, user_id
            )

            investment_cash_sell[currency_v] = investment_cash_sell_q[0]['investment_cash_sell'] if investment_cash_sell_q[0]['investment_cash_sell'] is not None else 0

            # Get investment-related bank deposit values for sell
            investment_bank_sell_q = db.execute (
                "SELECT SUM(amount) AS investment_bank_sell FROM transactions WHERE payment_method = 'banking' and currency = ? and id IN \
                    (SELECT transaction_id FROM investment WHERE user_id = ? and buy_or_sell = 'sell')", currency_v, user_id
            )

            investment_bank_sell[currency_v] = investment_bank_sell_q[0]['investment_bank_sell'] if investment_bank_sell_q[0]['investment_bank_sell'] is not None else 0

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
                    debt.user_id = ? and transactions.currency = ?) \
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
                ASC", user_id, currency_v)

            # Initialize debt cash values
            debt_cash_borrow[currency_v] = 0
            debt_cash_lend[currency_v] = 0
            debt_cash_brepay[currency_v] = 0
            debt_cash_lrepay[currency_v] = 0

            # Initialize debt bank values
            debt_bank_borrow[currency_v] = 0
            debt_bank_lend[currency_v] = 0
            debt_bank_brepay[currency_v] = 0 
            debt_bank_lrepay[currency_v] = 0
            
            for row in debt_rows:
                # debt_cash_borrow variables
                if row['category'] == 'borrow' and row['payment_method'] == 'cash':
                    debt_cash_borrow[currency_v] = debt_cash_borrow[currency_v] + round(float(row['amount']), 2)

                # debt_bank_borrow variables
                if row['category'] == 'borrow' and row['payment_method'] == 'banking':
                    debt_bank_borrow[currency_v] = debt_bank_borrow[currency_v] + round(float(row['amount']), 2)

                # debt_cash_lend variables
                if row['category'] == 'lend' and row['payment_method'] == 'cash':
                    debt_cash_lend[currency_v] = debt_cash_lend[currency_v] + round(float(row['amount']), 2)

                # debt_bank_lend variables
                if row['category'] == 'lend' and row['payment_method'] == 'banking':
                    debt_bank_lend[currency_v] = debt_bank_lend[currency_v] + round(float(row['amount']), 2)

                # debt repay variables
                if row['category'] == 'repay':
                    # debt cash lrepay variables
                    if repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'lend' and row['payment_method'] == 'cash':
                        debt_cash_lrepay[currency_v] = debt_cash_lrepay[currency_v] + round(float(row['amount']), 2)

                    # debt bank lrepay variables
                    if repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'lend' and row['payment_method'] == 'banking':
                        debt_bank_lrepay[currency_v] = debt_bank_lrepay[currency_v] + round(float(row['amount']), 2)

                    # debt cash brepay variables
                    if repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'borrow' and row['payment_method'] == 'cash':
                        debt_cash_brepay[currency_v] = debt_cash_brepay[currency_v] + round(float(row['amount']), 2)

                    # debt bank brepay variables
                    if repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'borrow' and row['payment_method'] == 'banking':
                        debt_bank_brepay[currency_v] = debt_bank_brepay[currency_v] + round(float(row['amount']), 2)

            # Calculate cash and bank values
            cash[currency_v] = income_cash[currency_v] - spending_cash[currency_v] + investment_cash_sell[currency_v] - investment_cash_buy[currency_v] \
                + debt_cash_borrow[currency_v] - debt_cash_lend[currency_v] - debt_cash_brepay[currency_v] + debt_cash_lrepay[currency_v]
        
            bank[currency_v] = income_bank[currency_v] - spending_bank[currency_v] + investment_bank_sell[currency_v] - investment_bank_buy[currency_v] \
                + debt_bank_borrow[currency_v] - debt_bank_lend[currency_v] - debt_bank_brepay[currency_v] + debt_bank_lrepay[currency_v]
        
            cash[currency_v] = round(cash[currency_v], 2)
            bank[currency_v] = round(bank[currency_v], 2)

            cash_str[currency_v] = f"{cash[currency_v]:,.2f}"
            bank_str[currency_v] = f"{bank[currency_v]:,.2f}"

            # Change the currency in cash and bank to usd for total amount calculation
            if cash[currency_v] == 0:
                cash_in_usd[currency_v] = 0

            else:
                cash_in_usd[currency_v] = amount_in_usd(currency_v, cash[currency_v])

            if bank[currency_v] == 0:
                bank_in_usd[currency_v] = 0

            else:
                bank_in_usd[currency_v] = amount_in_usd(currency_v, bank[currency_v])

            # Get the total cash in usd
            total_cash_usd = total_cash_usd + round(cash_in_usd[currency_v] , 2)

            # Get total bank in usd
            total_bank_usd = total_bank_usd + round(bank_in_usd[currency_v], 2)

            # If the currency is in the not_included_currencies and total_cash_usd != 0 or total_bank_usd != 0, add this currency to user_currencies
            if currency_v in not_included_currencies and (cash_in_usd[currency_v] != 0 or bank_in_usd[currency_v] != 0):
                db.execute(
                "INSERT INTO user_currencies (user_id, currency_code) VALUES (?, ?)", user_id, currency_v.upper()
                )

                # Add the currency to the original_currencies which will be passed to index.html
                original_currencies.append(currency_v)

        # Get total assets in usd
        total_assets = total_assets + total_cash_usd + total_bank_usd

        # Write database code for homepage investments table
        investment_rows = db.execute (
            "SELECT \
                investment.investment_type, \
                CASE \
                    WHEN investment.investment_type IN ('other-investment', 'real-estate') THEN investment.comment \
                    ELSE investment.symbol \
                END AS symbol, \
                SUM(CASE WHEN investment.buy_or_sell = 'buy' THEN investment.quantity ELSE -investment.quantity END) AS quantity, \
                SUM(CASE WHEN investment.buy_or_sell = 'buy' THEN transactions.amount_in_usd ELSE -transactions.amount_in_usd END) AS original_value \
            FROM investment JOIN transactions \
            ON investment.transaction_id = transactions.id \
            WHERE investment.user_id = ? \
            GROUP BY \
                investment.investment_type, \
                CASE \
                    WHEN investment.investment_type IN ('other-investment', 'real-estate') THEN investment.comment \
                    ELSE investment.symbol \
                END", user_id
        )

        # Initialize a list for new investment rows which includes original value and profits by today's market rate
        new_investment_rows = []
        investment_total = 0
        profit_loss_total = 0

        for row in investment_rows:
            # Get quantity of investment
            quantity = round(float(row['quantity']), 4)

            # Get stock today's stock market value and append new_investment_rows
            if row['investment_type'] == 'stock':
                # Get stock price from Yahoo API
                stock_quote = stock_lookup(row['symbol'])
                stock_price = stock_quote['price']

                # Calculate market value of existing stock
                market_value = round(stock_price * quantity, 2)

                # Calculate profit / loss of the existing stock
                profit_loss = round(market_value - float(row['original_value']), 2)

                # Swap the original values with market values for appending new_investment_rows
                row['original_value'] = market_value
                row['profit_loss'] = profit_loss
                row['quantity'] = quantity

                # Update investment_total and profit_loss_total
                investment_total = investment_total + market_value
                profit_loss_total = profit_loss_total + profit_loss

                # Append to new_investment_rows
                new_investment_rows.append(row)

            # Get stock today's crypto market value and append new_investment_rows
            elif row['investment_type'] == 'cryptocurrency':
                # Get crypto price from Binance API
                crypto_quote = crypto_lookup(row['symbol'])
                crypto_price = crypto_quote['price']

                # Calculate market value of existing cryptocurrency
                market_value = round(crypto_price * quantity, 2)

                # Calcualte profit / loss of existing cryptocurrency
                profit_loss = round(market_value - float(row['original_value']), 2)

                # Swap the original values with market values for appending new_investment_rows
                row['original_value'] = market_value
                row['profit_loss'] = profit_loss
                row['quantity'] = quantity

                # Update investment_total and profit_loss_total
                investment_total = investment_total + market_value
                profit_loss_total = profit_loss_total + profit_loss

                # Append to new_investment_rows
                new_investment_rows.append(row)

            # For other types of investments...
            else:
                # if quantity == 1, market_value is original_value and profit / loss is 0
                if quantity == 1:
                    market_value = round(float(row['original_value']), 2)
                    profit_loss = 0

                    row['original_value'] = market_value
                    row['profit_loss'] = profit_loss

                    # Update investment_total and profit_loss_total
                    investment_total = investment_total + market_value
                    profit_loss_total = profit_loss_total + profit_loss

                    # Append to new_investment_rows
                    new_investment_rows.append(row)

                # if quantity == 0, market_value is 0 and profit / loss is row['original_value']
                elif quantity == 0:
                    profit_loss = (-1) * round(float(row['original_value']), 2)

                    row['original_value'] = 0
                    row['profit_loss'] = profit_loss

                    # Update investment_total and profit_loss_total
                    investment_total = investment_total + row['original_value']
                    profit_loss_total = profit_loss_total + profit_loss

                    # Append to new_investment_rows
                    new_investment_rows.append(row)

        # Update total_assets
        total_assets = total_assets + investment_total

        # Write database code for Debts & Receivables table
        debt_rows = db.execute (
            "SELECT \
            debt.debt_category, debt.debtor_or_creditor, transactions.transaction_date, debt.interest_rate, transactions.currency, \
            transactions.amount \
            FROM debt JOIN transactions \
            ON debt.transaction_id = transactions.id \
            WHERE debt.id IN (SELECT MAX(debt.id) FROM debt WHERE debt.user_id = ? GROUP BY debtor_or_creditor)", user_id
        )

        # Initialize the list for new_debt_rows which will be displayed in homepage
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
        
            # Update total debt and interest values for new_debt_rows
            row['amount'] = total_debt
            row['interest'] = interest

            if row['debt_category'] == 'borrow':
                debt_total = debt_total - total_debt_usd
                interest_total = interest_total - interest_in_usd

            elif row['debt_category'] == 'lend':
                debt_total = debt_total + total_debt_usd
                interest_total = interest_total + interest_in_usd

            # Append new_debt_rows
            new_debt_rows.append(row)

        # Update total_assets
        total_assets = total_assets + debt_total

        return render_template("index.html", cash=cash_str, bank=bank_str, investment_rows=new_investment_rows, profit=profit, \
            currencies=original_currencies, currency=currency, debt_rows=new_debt_rows, total_cash_usd=total_cash_usd, total_bank_usd=total_bank_usd, \
            investment_total=investment_total, profit_loss_total=profit_loss_total, debt_total=debt_total, interest_total=interest_total, \
            total_assets=total_assets)


@app.route("/budgetary", methods=["GET", "POST"])
@login_required
def budgetary():
    # Get the user id
    user_id = session.get("user_id")

    # Retrieve the list of currencies
    # Convert to lowercase because in transactions database, currencies are in lowercase
    currencies_q = db.execute(
        "SELECT currency_code FROM user_currencies WHERE user_id = ?", user_id
    )

    # user selected currencies will be valid currencies
    valid_currencies = [row['currency_code'].lower() for row in currencies_q]

    if request.method == "POST":

        # Retrieve the specified text of real estate with a status of 'buy'.
        specified_real_estates_q = db.execute(
            "SELECT comment FROM investment WHERE investment_type = 'real-estate' and buy_or_sell = 'buy' and user_id = ?", user_id
        )

        # Extract a list of valid_specified_real_estates
        valid_specified_real_estates = [row['comment'] for row in specified_real_estates_q]

        # Retrieve the specified text of other investments with a status of 'buy'.
        specified_other_investments_q = db.execute(
            "SELECT comment FROM investment WHERE investment_type = 'other-investment' and buy_or_sell = 'buy' and user_id = ?", user_id
        )

        # Extract a list of valid_specified_other_investments
        valid_specified_other_investments = [row['comment'] for row in specified_other_investments_q]

        # Valid options for server side error handling
        valid_budgetary_types = ['income', 'spending', 'investment', 'debt']
        valid_income_types = ['salary', 'bank-interest', 'other-income']
        valid_spending_types = ['food', 'transportation', 'clothing', 'rent', 'other-spending']
        valid_investment_types = ['stock', 'cryptocurrency', 'real-estate', 'other-investment']
        valid_buy_sell_types = ['buy', 'sell']
        valid_debt_categories = ['borrow', 'lend', 'repay']
        valid_payment_methods = ['cash', 'banking']

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
            flash('Please choose budgetary type!', 'alert-danger')
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
        
        if budgetary_type == 'investment' and investment_type == 'real-estate' and other_investment == '':
            flash('Please specify real estate!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'investment' and investment_type == 'real-estate' and float(quantity) != 1:
            flash("Only a quantity of 1 can be chosen for this type of investment!", 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'investment' and investment_type == 'real-estate' and buy_sell == 'sell' and other_investment not in valid_specified_real_estates:
            flash('Please choose a previously bought real estate!', 'alert-danger')
            return(redirect(url_for('budgetary')))
        
        if budgetary_type == 'investment' and investment_type == 'real-estate' and buy_sell == 'buy' and other_investment in valid_specified_real_estates:
            flash('Please choose a different name from previously specified real estates!', 'alert-danger')
            return(redirect(url_for('budgetary')))
        
        if budgetary_type == 'investment' and investment_type == 'other-investment' and other_investment == '':
            flash('Please specify other investment!', 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'investment' and investment_type == 'other-investment' and float(quantity) != 1:
            flash("Only a quantity of 1 can be chosen for this type of investment!", 'alert-danger')
            return redirect(url_for('budgetary'))
        
        if budgetary_type == 'investment' and investment_type == 'other-investment' and buy_sell == 'sell' and other_investment not in valid_specified_other_investments:
            flash('Please choose a previously bought other investment!', 'alert-danger')
            return(redirect(url_for('budgetary')))
        
        if budgetary_type == 'investment' and investment_type == 'other-investment' and buy_sell == 'buy' and other_investment in valid_specified_other_investments:
            flash('Please choose a different name from previously specified other investments!', 'alert-danger')
            return(redirect(url_for('budgetary')))
        
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

        # Update database for income category
        if budgetary_type == 'income':         

            # Update transactions table
            db.execute(
                "INSERT INTO transactions (user_id, payment_method, currency, amount, amount_in_usd, transaction_date) VALUES (?, ?, ?, ?, ?, ?)",
                user_id, payment_method, currency, amount, usd_amount, date
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
                "INSERT INTO transactions (user_id, payment_method, currency, amount, amount_in_usd, transaction_date) VALUES (?, ?, ?, ?, ?, ?)",
                user_id, payment_method, currency, amount, usd_amount, date
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
                "INSERT INTO transactions (user_id, payment_method, currency, amount, amount_in_usd, transaction_date) VALUES (?, ?, ?, ?, ?, ?)",
                user_id, payment_method, currency, amount, usd_amount, date
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
                    "INSERT INTO investment (user_id, transaction_id, investment_type, comment, symbol, buy_or_sell, quantity) \
                    VALUES (?, ?, ?, ?, ?, ?, ?)",
                    user_id, transaction_id, investment_type, other_investment, stock_symbol.upper(), buy_sell, quantity
                )
                flash('Success!', 'alert-success')
                return redirect(url_for('budgetary'))

            # If cryptocurrency is chosen for investment_type...
            elif investment_type == 'cryptocurrency': 
                # Update investment table
                db.execute(
                    "INSERT INTO investment (user_id, transaction_id, investment_type, comment, symbol, buy_or_sell, quantity) \
                    VALUES (?, ?, ?, ?, ?, ?, ?)",
                    user_id, transaction_id, investment_type, other_investment, crypto_symbol.upper(), buy_sell, quantity
                )
                flash('Success!', 'alert-success')
                return redirect(url_for('budgetary'))

            # If real-estate is chosen for investment_type...
            elif investment_type == 'real-estate':
                # Update investment table
                db.execute(
                    "INSERT INTO investment (user_id, transaction_id, investment_type, comment, buy_or_sell, quantity) \
                    VALUES (?, ?, ?, ?, ?, ?)",
                    user_id, transaction_id, investment_type, other_investment, buy_sell, quantity
                )
                flash('Success!', 'alert-success')
                return redirect(url_for('budgetary'))

            # If other-investment is chosen for investment_type...
            elif investment_type == 'other-investment':
                # Update investment table
                db.execute(
                    "INSERT INTO investment (user_id, transaction_id, investment_type, comment, buy_or_sell, quantity) \
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
                    "INSERT INTO transactions (user_id, payment_method, currency, amount, amount_in_usd, transaction_date) VALUES (?, ?, ?, ?, ?, ?)",
                    user_id, payment_method, currency, amount, usd_amount, date
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
                    AS day_diff FROM transactions WHERE user_id = ? and id = ( \
                    SELECT transaction_id FROM debt WHERE debtor_or_creditor = ? ORDER BY id DESC)",
                    user_id, debtor_creditor
                )

                original_interest = db.execute(
                    "SELECT interest_rate FROM debt WHERE user_id = ? and debtor_or_creditor = ? ORDER BY id DESC",
                    user_id, debtor_creditor
                )

                original_debt = db.execute(
                    "SELECT payment_method, currency, amount FROM transactions WHERE user_id = ? and id = ( \
                    SELECT transaction_id FROM debt WHERE debtor_or_creditor = ? ORDER BY id DESC)",
                    user_id, debtor_creditor
                )

                original_category = db.execute(
                    "SELECT debt_category FROM debt WHERE user_id = ? and debtor_or_creditor = ? ORDER BY id DESC",
                    user_id, debtor_creditor
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
                    "INSERT INTO transactions (user_id, payment_method, currency, amount, amount_in_usd, transaction_date) VALUES (?, ?, ?, ?, ?, ?)",
                    user_id, payment_method, currency, amount, usd_amount, date
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
                "INSERT INTO transactions (user_id, payment_method, currency, amount, amount_in_usd, transaction_date) VALUES (?, ?, ?, ?, ?, ?)",
                user_id, original_payment_method, currency, remaining_debt_amount, remaining_usd_amount, date
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
                
    return render_template("budgetary.html", currencies=valid_currencies)


@app.route("/analysis", methods=["GET", "POST"])
@login_required
def analysis():
    user_id = session.get("user_id")
    total_assets = 0

    # Retrieve the list of currencies
    # Convert to lowercase because in transactions database, currencies are in lowercase
    currencies_q = db.execute(
        "SELECT currency_code FROM user_currencies WHERE user_id = ?", user_id
    )

    # original_currencies will be passed to index.html
    original_currencies = [row['currency_code'].lower() for row in currencies_q]

    # create a copy of original_currencies to be used in the loop
    currencies = original_currencies.copy()

    # Get a list of currencies previously used by the user, which is not included in the user_currencies that they chose
    used_currencies_q = db.execute(
        "SELECT DISTINCT currency FROM transactions WHERE user_id = ?", user_id
    )

    used_currencies = [row['currency'].lower() for row in used_currencies_q]

    # Find currencies in used_currencies that are not in currencies
    not_included_currencies = list(set(used_currencies) - set(currencies))

    # Add not_included_currencies to the currencies list
    currencies.extend(not_included_currencies)
    
    # Create analysis routes
    if request.method == "GET":

        # Write database code for homepage investments table
        investment_rows = db.execute (
            "SELECT \
                investment.investment_type, \
                CASE \
                    WHEN investment.investment_type IN ('other-investment', 'real-estate') THEN investment.comment \
                    ELSE investment.symbol \
                END AS symbol, \
                SUM(CASE WHEN investment.buy_or_sell = 'buy' THEN investment.quantity ELSE -investment.quantity END) AS quantity, \
                SUM(CASE WHEN investment.buy_or_sell = 'buy' THEN transactions.amount_in_usd ELSE -transactions.amount_in_usd END) AS original_value \
            FROM investment JOIN transactions \
            ON investment.transaction_id = transactions.id \
            WHERE investment.user_id = ? \
            GROUP BY \
                investment.investment_type, \
                CASE \
                    WHEN investment.investment_type IN ('other-investment', 'real-estate') THEN investment.comment \
                    ELSE investment.symbol \
                END", user_id
        )

        # Initialize a list for new investment rows which includes original value and profits by today's market rate
        new_investment_rows = []
        investment_total = 0
        profit_loss_total = 0

        for row in investment_rows:
            # Get quantity of investment
            quantity = round(float(row['quantity']), 4)

            # Get stock today's stock market value and append new_investment_rows
            if row['investment_type'] == 'stock':
                # Get stock price from Yahoo API
                stock_quote = stock_lookup(row['symbol'])
                stock_price = stock_quote['price']

                # Calculate market value of existing stock
                market_value = round(stock_price * quantity, 2)

                # Calculate profit / loss of the existing stock
                profit_loss = round(market_value - float(row['original_value']), 2)

                # Swap the original values with market values for appending new_investment_rows
                row['original_value'] = market_value
                row['profit_loss'] = profit_loss
                row['quantity'] = quantity

                # Update investment_total and profit_loss_total
                investment_total = investment_total + market_value
                profit_loss_total = profit_loss_total + profit_loss

                # Append to new_investment_rows
                new_investment_rows.append(row)

            # Get stock today's crypto market value and append new_investment_rows
            elif row['investment_type'] == 'cryptocurrency':
                # Get crypto price from Binance API
                crypto_quote = crypto_lookup(row['symbol'])
                crypto_price = crypto_quote['price']

                # Calculate market value of existing cryptocurrency
                market_value = round(crypto_price * quantity, 2)

                # Calcualte profit / loss of existing cryptocurrency
                profit_loss = round(market_value - float(row['original_value']), 2)

                # Swap the original values with market values for appending new_investment_rows
                row['original_value'] = market_value
                row['profit_loss'] = profit_loss
                row['quantity'] = quantity

                # Update investment_total and profit_loss_total
                investment_total = investment_total + market_value
                profit_loss_total = profit_loss_total + profit_loss

                # Append to new_investment_rows
                new_investment_rows.append(row)

            # For other types of investments...
            else:
                # if quantity == 1, market_value is original_value and profit / loss is 0
                if quantity == 1:
                    market_value = round(float(row['original_value']), 2)
                    profit_loss = 0

                    row['original_value'] = market_value
                    row['profit_loss'] = profit_loss

                    # Update investment_total and profit_loss_total
                    investment_total = investment_total + market_value
                    profit_loss_total = profit_loss_total + profit_loss

                    # Append to new_investment_rows
                    new_investment_rows.append(row)

                # if quantity == 0, market_value is 0 and profit / loss is row['original_value']
                elif quantity == 0:
                    profit_loss = (-1) * round(float(row['original_value']), 2)

                    row['original_value'] = 0
                    row['profit_loss'] = profit_loss

                    # Update investment_total and profit_loss_total
                    investment_total = investment_total + row['original_value']
                    profit_loss_total = profit_loss_total + profit_loss

                    # Append to new_investment_rows
                    new_investment_rows.append(row)

        total_assets = total_assets + investment_total
   
        # Write database code for Debts & Receivables table
        debt_rows = db.execute (
            "SELECT \
            debt.debt_category, debt.debtor_or_creditor, transactions.transaction_date, debt.interest_rate, transactions.currency, \
            transactions.amount \
            FROM debt JOIN transactions \
            ON debt.transaction_id = transactions.id \
            WHERE debt.id IN (SELECT MAX(debt.id) FROM debt WHERE debt.user_id = ? GROUP BY debtor_or_creditor)", user_id
        )

        # Initialize the list for new_debt_rows which will be displayed in homepage
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
        
            # Update total debt and interest values for new_debt_rows
            row['amount'] = total_debt
            row['interest'] = interest

            if row['debt_category'] == 'borrow':
                debt_total = debt_total - total_debt_usd
                interest_total = interest_total - interest_in_usd

            elif row['debt_category'] == 'lend':
                debt_total = debt_total + total_debt_usd
                interest_total = interest_total + interest_in_usd

            # Append new_debt_rows
            new_debt_rows.append(row)

        total_assets = total_assets + debt_total
        
        # Initialize the dictionary variables to be used inside the loop
        salary = {}
        bank_interest = {}
        other_income = {}

        food = {}
        transportation = {}
        clothing = {}
        rent = {}
        other_expense = {}

        stock_sell = {}
        crypto_sell = {}
        real_estate_sell = {}
        other_investment_sell = {}

        stock_buy = {}
        crypto_buy = {}
        real_estate_buy = {}
        other_investment_buy = {}

        borrow = {}
        receivable_repay = {}

        lend = {}
        debt_repay = {}

        usd_var = {
            "salary_in_usd": 0,
            "bank_interest_in_usd": 0,
            "other_income_in_usd": 0,
            "food_in_usd": 0,
            "transportation_in_usd": 0,
            "clothing_in_usd": 0,
            "rent_in_usd": 0,
            "other_expense_in_usd": 0,
            "stock_sell_in_usd": 0,
            "crypto_sell_in_usd": 0,
            "real_estate_sell_in_usd": 0,
            "other_investment_sell_in_usd": 0,
            "stock_buy_in_usd": 0,
            "crypto_buy_in_usd": 0,
            "real_estate_buy_in_usd": 0,
            "other_investment_buy_in_usd": 0,
            "borrow_in_usd": 0,
            "receivable_repay_in_usd": 0,
            "lend_in_usd": 0,
            "debt_repay_in_usd": 0
        }
            
        for currency_v in currencies:
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
                    income.user_id = ? and transactions.currency = ?", user_id, currency_v)
            
            # Get amount of each income category in usd
            salary[currency_v] = 0
            bank_interest[currency_v] = 0
            other_income[currency_v] = 0

            for row in inflow_income_rows:
                # Salary-related rows
                if row['category'] == 'salary':
                    salary[currency_v] = salary[currency_v] + round(float(row['amount']), 2)

                # Bank-interest-related rows
                if row['category'] == 'bank-interest':
                    bank_interest[currency_v] = bank_interest[currency_v] + round(float(row['amount']), 2)

                # Other-income-related rows
                if row['category'] == 'other-income':
                    other_income[currency_v] = other_income[currency_v] + round(float(row['amount']), 2)

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
                    spending.user_id = ? and transactions.currency = ?", user_id, currency_v)

            # Get amount of each expense category in usd
            food[currency_v] = 0
            transportation[currency_v] = 0
            clothing[currency_v] = 0
            rent[currency_v] = 0
            other_expense[currency_v] = 0

            for row in outflow_expense_rows:
                # Food-related rows
                if row['category'] == 'food':
                    food[currency_v] = food[currency_v] + round(float(row['amount']), 2)

                # Transportation-related rows
                if row['category'] == 'transportation':
                    transportation[currency_v] = transportation[currency_v] + round(float(row['amount']), 2)

                # Clothing-related rows
                if row['category'] == 'clothing':
                    clothing[currency_v] = clothing[currency_v] + round(float(row['amount']), 2)

                # Rent-related rows
                if row['category'] == 'rent':
                    rent[currency_v] = rent[currency_v] + round(float(row['amount']), 2)

                # Other-expense-related rows
                if row['category'] == 'other-spending':
                    other_expense[currency_v] = other_expense[currency_v] + round(float(row['amount']), 2)
            
            # Write database query for investment breakdown
            inflow_outflow_investment_rows = db.execute(
                "SELECT \
                    transactions.transaction_date AS date, \
                    investment.investment_type AS type, \
                CASE \
                    WHEN investment.investment_type IN ('other-investment', 'real-estate') THEN investment.comment \
                    ELSE investment.symbol\
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
                    investment.user_id = ? and transactions.currency = ?", user_id, currency_v
            )

            # Get amount of each inflow investment category in usd
            stock_sell[currency_v] = 0
            crypto_sell[currency_v] = 0
            real_estate_sell[currency_v] = 0
            other_investment_sell[currency_v] = 0

            # Get amount of each outflow investment category in usd
            stock_buy[currency_v] = 0
            crypto_buy[currency_v] = 0
            real_estate_buy[currency_v] = 0
            other_investment_buy[currency_v] = 0

            for row in inflow_outflow_investment_rows:
                # Inflow variables for selling investments
                if row['type'] == 'stock' and row['buy_sell'] == 'sell':
                    stock_sell[currency_v] = stock_sell[currency_v] + round(float(row['amount']), 2)

                if row['type'] == 'cryptocurrency' and row['buy_sell'] == 'sell':
                    crypto_sell[currency_v] = crypto_sell[currency_v] + round(float(row['amount']), 2)
                
                if row['type'] == 'real-estate' and row['buy_sell'] == 'sell':
                    real_estate_sell[currency_v] = real_estate_sell[currency_v] + round(float(row['amount']), 2)

                if row['type'] == 'other-investment' and row['buy_sell'] == 'sell':
                    other_investment_sell[currency_v] = other_investment_sell[currency_v] + round(float(row['amount']), 2)

                # Outflow variables for buying investments
                if row['type'] == 'stock' and row['buy_sell'] == 'buy':
                    stock_buy[currency_v] = stock_buy[currency_v] + round(float(row['amount']), 2)

                if row['type'] == 'cryptocurrency' and row['buy_sell'] == 'buy':
                    crypto_buy[currency_v] = crypto_buy[currency_v] + round(float(row['amount']), 2)
                
                if row['type'] == 'real-estate' and row['buy_sell'] == 'buy':
                    real_estate_buy[currency_v] = real_estate_buy[currency_v] + round(float(row['amount']), 2)

                if row['type'] == 'other-investment' and row['buy_sell'] == 'buy':
                    other_investment_buy[currency_v] = other_investment_buy[currency_v] + round(float(row['amount']), 2)

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
                    debt.user_id = ? and transactions.currency = ?) \
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
                ASC", user_id, currency_v)

            # Get amount of each inflow debt category in usd
            borrow[currency_v] = 0
            receivable_repay[currency_v] = 0

            # Get amount of each outflow debt category in usd
            lend[currency_v] = 0
            debt_repay[currency_v] = 0

            for row in inflow_outflow_debt_rows:
                # Inflow variables for debts
                if row['category'] == 'borrow':
                    borrow[currency_v] = borrow[currency_v] + round(float(row['amount']), 2)

                if row['category'] == 'repay':
                    if repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'lend':
                        receivable_repay[currency_v] = receivable_repay[currency_v] + round(float(row['amount']), 2)

                    elif repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'borrow':
                        debt_repay[currency_v] = debt_repay[currency_v] + round(float(row['amount']), 2)

                if row['category'] == 'lend':
                    lend[currency_v] = lend[currency_v] + round(float(row['amount']), 2)

            currency_var = {
                "salary_in_usd": salary[currency_v],
                "bank_interest_in_usd": bank_interest[currency_v],
                "other_income_in_usd": other_income[currency_v],
                "food_in_usd": food[currency_v],
                "transportation_in_usd": transportation[currency_v],
                "clothing_in_usd": clothing[currency_v],
                "rent_in_usd": rent[currency_v],
                "other_expense_in_usd": other_expense[currency_v],
                "stock_sell_in_usd": stock_sell[currency_v],
                "crypto_sell_in_usd": crypto_sell[currency_v],
                "real_estate_sell_in_usd": real_estate_sell[currency_v],
                "other_investment_sell_in_usd": other_investment_sell[currency_v],
                "stock_buy_in_usd": stock_buy[currency_v],
                "crypto_buy_in_usd": crypto_buy[currency_v],
                "real_estate_buy_in_usd": real_estate_buy[currency_v],
                "other_investment_buy_in_usd": other_investment_buy[currency_v],
                "borrow_in_usd": borrow[currency_v],
                "receivable_repay_in_usd": receivable_repay[currency_v],
                "lend_in_usd": lend[currency_v],
                "debt_repay_in_usd": debt_repay[currency_v]
            }

            currency_var_sum = sum(currency_var.values())

            if currency_var_sum != 0:
                if currency_v == 'usd':
                    for key in currency_var:
                        usd_var[key] = usd_var[key] + currency_var[key]

                elif currency_v == 'mmk':
                    for key in currency_var:
                        usd_var[key] = usd_var[key] + round((1/MMK_EXCHANGE_RATE) * currency_var[key], 2)

                else:
                    exchange_rate = forex_rate(currency_v)["rate"]
                    for key in currency_var:
                        usd_var[key] = usd_var[key] + round((1/exchange_rate) * currency_var[key], 2)

        # Update inflow income
        inflow_income = round((usd_var["salary_in_usd"] + usd_var["bank_interest_in_usd"] + usd_var["other_income_in_usd"]), 2)

        # Update outflow expense
        outflow_expense = round((usd_var["food_in_usd"] + usd_var["transportation_in_usd"] + usd_var["clothing_in_usd"] + usd_var["rent_in_usd"] \
            + usd_var["other_expense_in_usd"]), 2)

        # Update inflow investment
        inflow_investment = round((usd_var["stock_sell_in_usd"] + usd_var["crypto_sell_in_usd"] + usd_var["real_estate_sell_in_usd"] \
            + usd_var["other_investment_sell_in_usd"]), 2)

        # Update outflow investment
        outflow_investment = round((usd_var["stock_buy_in_usd"] + usd_var["crypto_buy_in_usd"] + usd_var["real_estate_buy_in_usd"] \
            + usd_var["other_investment_buy_in_usd"]), 2)

        # Update inflow debt
        inflow_debt = round((usd_var["borrow_in_usd"] + usd_var["receivable_repay_in_usd"]), 2)

        # Update outflow debt
        outflow_debt = round((usd_var["lend_in_usd"] + usd_var["debt_repay_in_usd"]), 2)

        # Update inflows and outflows
        inflows = inflow_income + inflow_investment + inflow_debt
        outflows = outflow_expense + outflow_investment + outflow_debt

        # Update net balance
        net_balance = inflows - outflows

        # Update total assets
        total_assets = total_assets + net_balance

        return render_template("analysis.html", currencies=original_currencies, total_assets=total_assets, investment_total=investment_total, \
            debt_total=debt_total, inflow_income=inflow_income, inflow_investment=inflow_investment, inflow_debt=inflow_debt, outflow_expense=outflow_expense, \
            outflow_investment=outflow_investment, outflow_debt=outflow_debt, inflows=inflows, outflows=outflows, net_balance=net_balance, \
            salary=usd_var["salary_in_usd"], bank_interest=usd_var["bank_interest_in_usd"], other_income=usd_var["other_income_in_usd"], food=usd_var["food_in_usd"], \
            transportation=usd_var["transportation_in_usd"], clothing=usd_var["clothing_in_usd"], rent=usd_var["rent_in_usd"], other_expense=usd_var["other_expense_in_usd"], \
            stock_sell=usd_var["stock_sell_in_usd"], crypto_sell=usd_var["crypto_sell_in_usd"], real_estate_sell=usd_var["real_estate_sell_in_usd"], \
            other_investment_sell=usd_var["other_investment_sell_in_usd"], stock_buy=usd_var["stock_buy_in_usd"], crypto_buy=usd_var["crypto_buy_in_usd"], \
            real_estate_buy=usd_var["real_estate_buy_in_usd"], other_investment_buy=usd_var["other_investment_buy_in_usd"], borrow=usd_var["borrow_in_usd"], \
            receivable_repay=usd_var["receivable_repay_in_usd"], lend=usd_var["lend_in_usd"], debt_repay=usd_var["debt_repay_in_usd"])


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
            WHEN investment.investment_type IN ('other-investment', 'real-estate') THEN investment.comment
            ELSE investment.symbol
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

        # Check if the user already has set up currencies to use
        preferred_currencies = db.execute(
            "SELECT * FROM user_currencies WHERE user_id = ?", session["user_id"]
        )

        if not preferred_currencies:
            return redirect(url_for('choose_currency'))

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
    return redirect("/login")


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
@login_required
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
@login_required
def convert_currency():
    final_currency = request.args.get('final_currency')
    final_currency = final_currency.upper()
    value_in_usd = float(request.args.get('value_in_usd'))

    if final_currency == 'USD':
        converted_amount = round(float(value_in_usd), 2)
        return jsonify({'converted_amount': currency(converted_amount)})
    
    elif final_currency == 'MMK':
        converted_amount = round(MMK_EXCHANGE_RATE * float(value_in_usd), 2)
        return jsonify({'converted_amount': currency(converted_amount)})
    
    else:
        exchange_rate = forex_rate(final_currency)["rate"]
        converted_amount = round(exchange_rate * float(value_in_usd), 2)
        return jsonify({'converted_amount': currency(converted_amount)})
    

# Convert usd values for profits or interests into other currencies
@app.route("/convert_profit_currency")
@login_required
def convert_profit_currency():
    final_currency = request.args.get('final_currency')
    value_in_usd = float(request.args.get('value_in_usd'))

    if final_currency.upper() == 'USD':
        converted_amount = round(float(value_in_usd), 2)
        return jsonify({'converted_amount': profit(converted_amount)})
    
    elif final_currency.upper() == 'MMK':
        converted_amount = round(MMK_EXCHANGE_RATE * float(value_in_usd), 2)
        return jsonify({'converted_amount': profit(converted_amount)})
    
    else:
        exchange_rate = forex_rate(final_currency)["rate"]
        converted_amount = round(exchange_rate * float(value_in_usd), 2)
        return jsonify({'converted_amount': profit(converted_amount)})
    

# Date filter in analysis page
@app.route("/analysis_filter")
@login_required
def analysis_filter():
    user_id = session.get("user_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    selected_currency = request.args.get("selected_currency")
    total_assets = request.args.get("total_assets")
    investment_total = request.args.get("investment_total")
    debt_total = request.args.get("debt_total")
    total_cash_bank_usd = round(float(request.args.get("total_cash_bank")), 2)
    total_cash_bank = total_cash_bank_usd

    # Retrieve the list of currencies
    # Convert to lowercase because in transactions database, currencies are in lowercase
    currencies_q = db.execute(
        "SELECT currency_code FROM user_currencies WHERE user_id = ?", user_id
    )

    # original_currencies will be passed to index.html
    original_currencies = [row['currency_code'].lower() for row in currencies_q]

    # create a copy of original_currencies to be used in the loop
    currencies = original_currencies.copy()

    # Get a list of currencies previously used by the user, which is not included in the user_currencies that they chose
    used_currencies_q = db.execute(
        "SELECT DISTINCT currency FROM transactions WHERE user_id = ?", user_id
    )

    used_currencies = [row['currency'].lower() for row in used_currencies_q]

    # Find currencies in used_currencies that are not in currencies
    not_included_currencies = list(set(used_currencies) - set(currencies))

    # Add not_included_currencies to the currencies list
    currencies.extend(not_included_currencies)

    # Initialize query lists
    inflow_income_rows = []
    outflow_expense_rows = []
    inflow_outflow_investment_rows = []
    inflow_outflow_debt_rows = []

    # Initialize the dictionary variables to be used inside the loop
    salary = {}
    bank_interest = {}
    other_income = {}

    food = {}
    transportation = {}
    clothing = {}
    rent = {}
    other_expense = {}

    stock_sell = {}
    crypto_sell = {}
    real_estate_sell = {}
    other_investment_sell = {}

    stock_buy = {}
    crypto_buy = {}
    real_estate_buy = {}
    other_investment_buy = {}

    borrow = {}
    receivable_repay = {}

    lend = {}
    debt_repay = {}

    usd_var = {
        "salary_in_usd": 0,
        "bank_interest_in_usd": 0,
        "other_income_in_usd": 0,
        "food_in_usd": 0,
        "transportation_in_usd": 0,
        "clothing_in_usd": 0,
        "rent_in_usd": 0,
        "other_expense_in_usd": 0,
        "stock_sell_in_usd": 0,
        "crypto_sell_in_usd": 0,
        "real_estate_sell_in_usd": 0,
        "other_investment_sell_in_usd": 0,
        "stock_buy_in_usd": 0,
        "crypto_buy_in_usd": 0,
        "real_estate_buy_in_usd": 0,
        "other_investment_buy_in_usd": 0,
        "borrow_in_usd": 0,
        "receivable_repay_in_usd": 0,
        "lend_in_usd": 0,
        "debt_repay_in_usd": 0
    }

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
            income.user_id = ? and transactions.currency = ? {where_clause} """
    
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
            spending.user_id = ? and transactions.currency = ? {where_clause} """

    # Write database query for investment breakdown
    inflow_outflow_investment_rows_query = """
        SELECT \
            transactions.transaction_date AS date, \
            investment.investment_type AS type, \
        CASE \
            WHEN investment.investment_type IN ('other-investment', 'real-estate') THEN investment.comment \
            ELSE investment.symbol \
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
            investment.user_id = ? and transactions.currency = ? {where_clause} """
    
    
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
            debt.user_id = ? and transactions.currency = ? {where_clause}) \
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
    
    for currency_v in currencies:
        if start_date and end_date:
            # Format where clause for query
            where_clause = "and transactions.transaction_date BETWEEN ? AND ?"

            inflow_income_rows_query = inflow_income_rows_query.format(where_clause=where_clause)
            inflow_income_rows = db.execute(
                inflow_income_rows_query, user_id, currency_v, start_date, end_date
            )

            outflow_expense_rows_query = outflow_expense_rows_query.format(where_clause=where_clause)
            outflow_expense_rows = db.execute(
                outflow_expense_rows_query, user_id, currency_v, start_date, end_date
            )

            inflow_outflow_investment_rows_query = inflow_outflow_investment_rows_query.format(where_clause=where_clause)
            inflow_outflow_investment_rows = db.execute(
                inflow_outflow_investment_rows_query, user_id, currency_v, start_date, end_date
            )

            inflow_outflow_debt_rows_query = inflow_outflow_debt_rows_query.format(where_clause=where_clause)
            inflow_outflow_debt_rows = db.execute(
                inflow_outflow_debt_rows_query, user_id, currency_v, start_date, end_date
            )

        else:
            # Format where clause for query
            where_clause = ""

            inflow_income_rows_query = inflow_income_rows_query.format(where_clause=where_clause)
            inflow_income_rows = db.execute(
                inflow_income_rows_query, user_id, currency_v
            )

            outflow_expense_rows_query = outflow_expense_rows_query.format(where_clause=where_clause)
            outflow_expense_rows = db.execute(
                outflow_expense_rows_query, user_id, currency_v
            )

            inflow_outflow_investment_rows_query = inflow_outflow_investment_rows_query.format(where_clause=where_clause)
            inflow_outflow_investment_rows = db.execute(
                inflow_outflow_investment_rows_query, user_id, currency_v
            )

            inflow_outflow_debt_rows_query = inflow_outflow_debt_rows_query.format(where_clause=where_clause)
            inflow_outflow_debt_rows = db.execute(
                inflow_outflow_debt_rows_query, user_id, currency_v
            )

        # Get amount of each income category in usd
        salary[currency_v] = 0
        bank_interest[currency_v] = 0
        other_income[currency_v] = 0

        for row in inflow_income_rows:
            # Salary-related rows
            if row['category'] == 'salary':
                salary[currency_v] = salary[currency_v] + round(float(row['amount']), 2)

            # Bank-interest-related rows
            if row['category'] == 'bank-interest':
                bank_interest[currency_v] = bank_interest[currency_v] + round(float(row['amount']), 2)

            # Other-income-related rows
            if row['category'] == 'other-income':
                other_income[currency_v] = other_income[currency_v] + round(float(row['amount']), 2)

        # Get amount of each expense category in usd
        food[currency_v] = 0
        transportation[currency_v] = 0
        clothing[currency_v] = 0
        rent[currency_v] = 0
        other_expense[currency_v] = 0

        for row in outflow_expense_rows:
            # Food-related rows
            if row['category'] == 'food':
                food[currency_v] = food[currency_v] + round(float(row['amount']), 2)

            # Transportation-related rows
            if row['category'] == 'transportation':
                transportation[currency_v] = transportation[currency_v] + round(float(row['amount']), 2)

            # Clothing-related rows
            if row['category'] == 'clothing':
                clothing[currency_v] = clothing[currency_v] + round(float(row['amount']), 2)

            # Rent-related rows
            if row['category'] == 'rent':
                rent[currency_v] = rent[currency_v] + round(float(row['amount']), 2)

            # Other-expense-related rows
            if row['category'] == 'other-spending':
                other_expense[currency_v] = other_expense[currency_v] + round(float(row['amount']), 2)

        # Get amount of each inflow investment category in usd
        stock_sell[currency_v] = 0
        crypto_sell[currency_v] = 0
        real_estate_sell[currency_v] = 0
        other_investment_sell[currency_v] = 0

        # Get amount of each outflow investment category in usd
        stock_buy[currency_v] = 0
        crypto_buy[currency_v] = 0
        real_estate_buy[currency_v] = 0
        other_investment_buy[currency_v] = 0

        for row in inflow_outflow_investment_rows:
            # Inflow variables for selling investments
            if row['type'] == 'stock' and row['buy_sell'] == 'sell':
                stock_sell[currency_v] = stock_sell[currency_v] + round(float(row['amount']), 2)

            if row['type'] == 'cryptocurrency' and row['buy_sell'] == 'sell':
                crypto_sell[currency_v] = crypto_sell[currency_v] + round(float(row['amount']), 2)
            
            if row['type'] == 'real-estate' and row['buy_sell'] == 'sell':
                real_estate_sell[currency_v] = real_estate_sell[currency_v] + round(float(row['amount']), 2)

            if row['type'] == 'other-investment' and row['buy_sell'] == 'sell':
                other_investment_sell[currency_v] = other_investment_sell[currency_v] + round(float(row['amount']), 2)

            # Outflow variables for buying investments
            if row['type'] == 'stock' and row['buy_sell'] == 'buy':
                stock_buy[currency_v] = stock_buy[currency_v] + round(float(row['amount']), 2)

            if row['type'] == 'cryptocurrency' and row['buy_sell'] == 'buy':
                crypto_buy[currency_v] = crypto_buy[currency_v] + round(float(row['amount']), 2)
            
            if row['type'] == 'real-estate' and row['buy_sell'] == 'buy':
                real_estate_buy[currency_v] = real_estate_buy[currency_v] + round(float(row['amount']), 2)

            if row['type'] == 'other-investment' and row['buy_sell'] == 'buy':
                other_investment_buy[currency_v] = other_investment_buy[currency_v] + round(float(row['amount']), 2)

        # Get amount of each inflow debt category in usd
        borrow[currency_v] = 0
        receivable_repay[currency_v] = 0

        # Get amount of each outflow debt category in usd
        lend[currency_v] = 0
        debt_repay[currency_v] = 0

        for row in inflow_outflow_debt_rows:
            # Inflow variables for debts
            if row['category'] == 'borrow':
                borrow[currency_v] = borrow[currency_v] + round(float(row['amount']), 2)

            if row['category'] == 'repay':
                if repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'lend':
                    receivable_repay[currency_v] = receivable_repay[currency_v] + round(float(row['amount']), 2)

                elif repay_check(row['debtor_or_creditor'])[0]['debt_category'] == 'borrow':
                    debt_repay[currency_v] = debt_repay[currency_v] + round(float(row['amount']), 2)

            if row['category'] == 'lend':
                lend[currency_v] = lend[currency_v] + round(float(row['amount']), 2)

        currency_var = {
            "salary_in_usd": salary[currency_v],
            "bank_interest_in_usd": bank_interest[currency_v],
            "other_income_in_usd": other_income[currency_v],
            "food_in_usd": food[currency_v],
            "transportation_in_usd": transportation[currency_v],
            "clothing_in_usd": clothing[currency_v],
            "rent_in_usd": rent[currency_v],
            "other_expense_in_usd": other_expense[currency_v],
            "stock_sell_in_usd": stock_sell[currency_v],
            "crypto_sell_in_usd": crypto_sell[currency_v],
            "real_estate_sell_in_usd": real_estate_sell[currency_v],
            "other_investment_sell_in_usd": other_investment_sell[currency_v],
            "stock_buy_in_usd": stock_buy[currency_v],
            "crypto_buy_in_usd": crypto_buy[currency_v],
            "real_estate_buy_in_usd": real_estate_buy[currency_v],
            "other_investment_buy_in_usd": other_investment_buy[currency_v],
            "borrow_in_usd": borrow[currency_v],
            "receivable_repay_in_usd": receivable_repay[currency_v],
            "lend_in_usd": lend[currency_v],
            "debt_repay_in_usd": debt_repay[currency_v]
        }

        currency_var_sum = sum(currency_var.values())

        if currency_var_sum != 0:
            if currency_v == 'usd':
                for key in currency_var:
                    usd_var[key] = usd_var[key] + currency_var[key]

            elif currency_v == 'mmk':
                for key in currency_var:
                    usd_var[key] = usd_var[key] + round((1/MMK_EXCHANGE_RATE) * currency_var[key], 2)

            else:
                exchange_rate = forex_rate(currency_v)["rate"]
                for key in currency_var:
                    usd_var[key] = usd_var[key] + round((1/exchange_rate) * currency_var[key], 2)
        
    # Update inflow income
    inflow_income = round((usd_var["salary_in_usd"] + usd_var["bank_interest_in_usd"] + usd_var["other_income_in_usd"]), 2)

    # Update outflow expense
    outflow_expense = round((usd_var["food_in_usd"] + usd_var["transportation_in_usd"] + usd_var["clothing_in_usd"] + usd_var["rent_in_usd"] \
        + usd_var["other_expense_in_usd"]), 2)

    # Update inflow investment
    inflow_investment = round((usd_var["stock_sell_in_usd"] + usd_var["crypto_sell_in_usd"] + usd_var["real_estate_sell_in_usd"] \
        + usd_var["other_investment_sell_in_usd"]), 2)

    # Update outflow investment
    outflow_investment = round((usd_var["stock_buy_in_usd"] + usd_var["crypto_buy_in_usd"] + usd_var["real_estate_buy_in_usd"] \
        + usd_var["other_investment_buy_in_usd"]), 2)

    # Update inflow debt
    inflow_debt = round((usd_var["borrow_in_usd"] + usd_var["receivable_repay_in_usd"]), 2)

    # Update outflow debt
    outflow_debt = round((usd_var["lend_in_usd"] + usd_var["debt_repay_in_usd"]), 2)

    # Update inflows and outflows
    inflows = inflow_income + inflow_investment + inflow_debt
    outflows = outflow_expense + outflow_investment + outflow_debt

    # Update net balance
    net_balance = inflows - outflows

    if selected_currency == 'usd':
        total_assets = round(float(total_assets), 2)
        investment_total = round(float(investment_total), 2)
        debt_total = round(float(debt_total), 2)
        total_cash_bank = total_cash_bank

        salary = round(float(usd_var["salary_in_usd"]), 2)
        bank_interest = round(float(usd_var["bank_interest_in_usd"]), 2)
        other_income = round(float(usd_var["other_income_in_usd"]), 2)
        food = round(float(usd_var["food_in_usd"]), 2)
        transportation = round(float(usd_var["transportation_in_usd"]), 2)
        clothing = round(float(usd_var["clothing_in_usd"]), 2)
        rent = round(float(usd_var["rent_in_usd"]), 2)
        other_expense = round(float(usd_var["other_expense_in_usd"]), 2)
        stock_sell = round(float(usd_var["stock_sell_in_usd"]), 2)
        crypto_sell = round(float(usd_var["crypto_sell_in_usd"]), 2)
        real_estate_sell = round(float(usd_var["real_estate_sell_in_usd"]), 2)
        other_investment_sell = round(float(usd_var["other_investment_sell_in_usd"]), 2)
        stock_buy = round(float(usd_var["stock_buy_in_usd"]), 2)
        crypto_buy = round(float(usd_var["crypto_buy_in_usd"]), 2)
        real_estate_buy = round(float(usd_var["real_estate_buy_in_usd"]), 2)
        other_investment_buy = round(float(usd_var["other_investment_buy_in_usd"]), 2)
        borrow = round(float(usd_var["borrow_in_usd"]), 2)
        receivable_repay = round(float(usd_var["receivable_repay_in_usd"]), 2)
        lend = round(float(usd_var["lend_in_usd"]), 2)
        debt_repay = round(float(usd_var["debt_repay_in_usd"]), 2)   
    
    elif selected_currency == 'mmk':
        total_assets = round(MMK_EXCHANGE_RATE * float(total_assets), 2)
        investment_total = round(MMK_EXCHANGE_RATE * float(investment_total), 2)
        debt_total = round(MMK_EXCHANGE_RATE * float(debt_total), 2)
        total_cash_bank = round(MMK_EXCHANGE_RATE * total_cash_bank)

        inflow_income = round(MMK_EXCHANGE_RATE * float(inflow_income), 2)
        inflow_investment = round(MMK_EXCHANGE_RATE * float(inflow_investment), 2)
        inflow_debt = round(MMK_EXCHANGE_RATE * float(inflow_debt), 2)
        outflow_expense = round(MMK_EXCHANGE_RATE * float(outflow_expense), 2)
        outflow_investment = round(MMK_EXCHANGE_RATE * float(outflow_investment), 2)
        outflow_debt = round(MMK_EXCHANGE_RATE * float(outflow_debt), 2)
        inflows = round(MMK_EXCHANGE_RATE * float(inflows), 2)
        outflows = round(MMK_EXCHANGE_RATE * float(outflows), 2)
        net_balance = round(MMK_EXCHANGE_RATE * float(net_balance), 2)

        salary = round(MMK_EXCHANGE_RATE * float(usd_var["salary_in_usd"]), 2)
        bank_interest = round(MMK_EXCHANGE_RATE * float(usd_var["bank_interest_in_usd"]), 2)
        other_income = round(MMK_EXCHANGE_RATE * float(usd_var["other_income_in_usd"]), 2)
        food = round(MMK_EXCHANGE_RATE * float(usd_var["food_in_usd"]), 2)
        transportation = round(MMK_EXCHANGE_RATE * float(usd_var["transportation_in_usd"]), 2)
        clothing = round(MMK_EXCHANGE_RATE * float(usd_var["clothing_in_usd"]), 2)
        rent = round(MMK_EXCHANGE_RATE * float(usd_var["rent_in_usd"]), 2)
        other_expense = round(MMK_EXCHANGE_RATE * float(usd_var["other_expense_in_usd"]), 2)
        stock_sell = round(MMK_EXCHANGE_RATE * float(usd_var["stock_sell_in_usd"]), 2)
        crypto_sell = round(MMK_EXCHANGE_RATE * float(usd_var["crypto_sell_in_usd"]), 2)
        real_estate_sell = round(MMK_EXCHANGE_RATE * float(usd_var["real_estate_sell_in_usd"]), 2)
        other_investment_sell = round(MMK_EXCHANGE_RATE * float(usd_var["other_investment_sell_in_usd"]), 2)
        stock_buy = round(MMK_EXCHANGE_RATE * float(usd_var["stock_buy_in_usd"]), 2)
        crypto_buy = round(MMK_EXCHANGE_RATE * float(usd_var["crypto_buy_in_usd"]), 2)
        real_estate_buy = round(MMK_EXCHANGE_RATE * float(usd_var["real_estate_buy_in_usd"]), 2)
        other_investment_buy = round(MMK_EXCHANGE_RATE * float(usd_var["other_investment_buy_in_usd"]), 2)
        borrow = round(MMK_EXCHANGE_RATE * float(usd_var["borrow_in_usd"]), 2)
        receivable_repay = round(MMK_EXCHANGE_RATE * float(usd_var["receivable_repay_in_usd"]), 2)
        lend = round(MMK_EXCHANGE_RATE * float(usd_var["lend_in_usd"]), 2)
        debt_repay = round(MMK_EXCHANGE_RATE * float(usd_var["debt_repay_in_usd"]), 2)        
    
    else:
        exchange_rate = forex_rate(selected_currency)["rate"]

        total_assets = round(exchange_rate * float(total_assets), 2)
        investment_total = round(exchange_rate * float(investment_total), 2)
        debt_total = round(exchange_rate * float(debt_total), 2)
        total_cash_bank = round(exchange_rate * float(total_cash_bank), 2)

        inflow_income = round(exchange_rate * float(inflow_income), 2)
        inflow_investment = round(exchange_rate * float(inflow_investment), 2)
        inflow_debt = round(exchange_rate * float(inflow_debt), 2)
        outflow_expense = round(exchange_rate * float(outflow_expense), 2)
        outflow_investment = round(exchange_rate * float(outflow_investment), 2)
        outflow_debt = round(exchange_rate * float(outflow_debt), 2)
        inflows = round(exchange_rate * float(inflows), 2)
        outflows = round(exchange_rate * float(outflows), 2)
        net_balance = round(exchange_rate * float(net_balance), 2)

        salary = round(exchange_rate * float(usd_var["salary_in_usd"]), 2)
        bank_interest = round(exchange_rate * float(usd_var["bank_interest_in_usd"]), 2)
        other_income = round(exchange_rate * float(usd_var["other_income_in_usd"]), 2)
        food = round(exchange_rate * float(usd_var["food_in_usd"]), 2)
        transportation = round(exchange_rate * float(usd_var["transportation_in_usd"]), 2)
        clothing = round(exchange_rate * float(usd_var["clothing_in_usd"]), 2)
        rent = round(exchange_rate * float(usd_var["rent_in_usd"]), 2)
        other_expense = round(exchange_rate * float(usd_var["other_expense_in_usd"]), 2)
        stock_sell = round(exchange_rate * float(usd_var["stock_sell_in_usd"]), 2)
        crypto_sell = round(exchange_rate * float(usd_var["crypto_sell_in_usd"]), 2)
        real_estate_sell = round(exchange_rate * float(usd_var["real_estate_sell_in_usd"]), 2)
        other_investment_sell = round(exchange_rate * float(usd_var["other_investment_sell_in_usd"]), 2)
        stock_buy = round(exchange_rate * float(usd_var["stock_buy_in_usd"]), 2)
        crypto_buy = round(exchange_rate * float(usd_var["crypto_buy_in_usd"]), 2)
        real_estate_buy = round(exchange_rate * float(usd_var["real_estate_buy_in_usd"]), 2)
        other_investment_buy = round(exchange_rate * float(usd_var["other_investment_buy_in_usd"]), 2)
        borrow = round(exchange_rate * float(usd_var["borrow_in_usd"]), 2)
        receivable_repay = round(exchange_rate * float(usd_var["receivable_repay_in_usd"]), 2)
        lend = round(exchange_rate * float(usd_var["lend_in_usd"]), 2)
        debt_repay = round(exchange_rate * float(usd_var["debt_repay_in_usd"]), 2)

    return jsonify({'inflow_income': inflow_income, 'inflow_investment': inflow_investment, 'inflow_debt': inflow_debt, 'outflow_expense': outflow_expense, \
        'outflow_investment': outflow_investment, 'outflow_debt': outflow_debt, 'inflows': inflows, 'outflows': outflows, 'net_balance': net_balance, \
        'salary': salary, 'bank_interest': bank_interest, 'other_income': other_income, 'food': food, 'transportation': transportation, 'clothing': clothing, \
        'rent': rent, 'other_expense': other_expense, 'stock_sell': stock_sell, 'crypto_sell': crypto_sell, 'real_estate_sell': real_estate_sell, \
        'other_investment_sell': other_investment_sell, 'stock_buy': stock_buy, 'crypto_buy': crypto_buy, 'real_estate_buy': real_estate_buy, \
        'other_investment_buy': other_investment_buy, 'borrow': borrow, 'receivable_repay': receivable_repay, 'lend': lend, 'debt_repay': debt_repay, \
        'total_assets': total_assets, 'investment_total': investment_total, 'debt_total': debt_total, 'total_cash_bank': total_cash_bank, \
        'total_cash_bank_usd': total_cash_bank_usd})


# delete repaid debts from database
@app.route("/delete_debt", methods=["POST"])
@login_required
def delete_debt():
    user_id = session.get("user_id")
    data = request.get_json()
    debtor_or_creditor = data.get('debtor_or_creditor')

    # Get the transition_ids for the specific debtor_or_creditor
    transaction_ids = db.execute(
        "SELECT transaction_id, debt_category FROM debt WHERE user_id = ? and debtor_or_creditor = ?", user_id, debtor_or_creditor
    )

    # Get the debt_category and transaction_id of the first transaction of the specific debtor_or_creditor
    main_transaction_id = repay_check(debtor_or_creditor)[0]['transaction_id']
    main_debt_category = repay_check(debtor_or_creditor)[0]['debt_category']

    # Delete the debt rows from debt table for the specific debtor_or_creditor
    db.execute(
        "DELETE FROM debt WHERE user_id = ? and debtor_or_creditor = ?", user_id, debtor_or_creditor
    )

    for transaction_id in transaction_ids:
        # if the debt_category is borrow and transaction_id is main_transaction_id, relocate the values into other-income category
        if transaction_id['debt_category'] == 'borrow' and transaction_id['transaction_id'] == main_transaction_id:
            comment = f"borrow - {debtor_or_creditor}"
            db.execute(
                "INSERT INTO income (user_id, transaction_id, income_type, comment) VALUES (?, ?, ?, ?)",
                user_id, transaction_id['transaction_id'], 'other-income', comment
            )

        # if the debt_category is borrow and transaction_id is not main_transaction_id, delete the transaction to avoid repetitive counting
        elif transaction_id['debt_category'] == 'borrow' and transaction_id['transaction_id'] != main_transaction_id:
            db.execute(
                "DELETE FROM transactions WHERE id = ?", transaction_id['transaction_id']
            )

        # if the debt_category is lend and transaction_id is main_transaction_id, relocate the values into other-epense category
        if transaction_id['debt_category'] == 'lend' and transaction_id['transaction_id'] == main_transaction_id:
            comment = f"lend - {debtor_or_creditor}"
            db.execute(
                "INSERT INTO spending (user_id, transaction_id, spending_type, comment) VALUES (?, ?, ?, ?)",
                user_id, transaction_id['transaction_id'], 'other-spending', comment
            )

        # if the debt_category is lend and transaction_id is not main_transaction_id, delete the transaction to avoid repetitive counting
        elif transaction_id['debt_category'] == 'lend' and transaction_id['transaction_id'] != main_transaction_id:
            db.execute(
                "DELETE FROM transactions WHERE id = ?", transaction_id['transaction_id']
            )

        # if debt_category is repay, check the main_debt_category
        if transaction_id['debt_category'] == 'repay':
            # if main_debt_category is lend, relocate the values into other-income category for lend-repay
            if main_debt_category == 'lend':
                comment = f"lend repayment - {debtor_or_creditor}"
                db.execute(
                "INSERT INTO income (user_id, transaction_id, income_type, comment) VALUES (?, ?, ?, ?)",
                user_id, transaction_id['transaction_id'], 'other-income', comment
                )

            # if main_debt_category is borrow, relocate the values into other-expense category for borrow-repay
            if main_debt_category == 'borrow':
                comment = f"borrow repayment - {debtor_or_creditor}"
                db.execute(
                "INSERT INTO spending (user_id, transaction_id, spending_type, comment) VALUES (?, ?, ?, ?)",
                user_id, transaction_id['transaction_id'], 'other-spending', comment
                )

    return jsonify({'status': 'success'})


# delete investments with zero quantity from database
@app.route("/delete_investment", methods=["POST"])
@login_required
def delete_investment():
    user_id = session.get("user_id")
    data = request.get_json()
    symbol_comment = data.get('symbol_comment')

    # Get the transaction_ids, investment_type, buy_or_sell, and quantity for the specific symbol_comment
    transaction_ids = db.execute(
        "SELECT \
            transaction_id, \
            investment_type, \
            buy_or_sell, \
            quantity \
        FROM \
            investment \
        WHERE \
            user_id = ? \
        AND \
            (CASE \
                WHEN investment_type IN ('other-investment', 'real-estate') THEN comment \
                ELSE symbol \
            END) = ?", user_id, symbol_comment
    )

    # Delete the rows from the investment table for the specific symbol_comment
    db.execute(
        "DELETE FROM investment \
        WHERE \
            user_id = ? \
        AND \
            (CASE \
                WHEN investment_type IN ('other-investment', 'real-estate') THEN comment \
                ELSE symbol \
            END) = ?", user_id, symbol_comment
    )

    # Loop throught the transaction_ids
    for transaction_id in transaction_ids:
        quantity = transaction_id['quantity']

        # if the investment_type is stock
        if transaction_id['investment_type'] == 'stock':
            buy_comment = f"stock buy - {quantity} {symbol_comment}"
            sell_comment = f"stock sell - {quantity} {symbol_comment}"

            # if buy_or_sell is buy, relocate the values into other-expense category with comment "Stock Buy - {quantity} {symbol_comment}"
            if transaction_id['buy_or_sell'] == 'buy':
                db.execute(
                "INSERT INTO spending (user_id, transaction_id, spending_type, comment) VALUES (?, ?, ?, ?)",
                user_id, transaction_id['transaction_id'], 'other-spending', buy_comment
                )

            # elif buy_or_sell is sell, relocate the values into other-income category with comment "Stock Sell - {quantity} {symbol_comment}"
            elif transaction_id['buy_or_sell'] == 'sell':
                db.execute(
                "INSERT INTO income (user_id, transaction_id, income_type, comment) VALUES (?, ?, ?, ?)",
                user_id, transaction_id['transaction_id'], 'other-income', sell_comment
                )

        # elif the investment_category is cryptocurrency
        elif transaction_id['investment_type'] == 'cryptocurrency':
            buy_comment = f"crypto buy - {quantity} {symbol_comment}"
            sell_comment = f"crypto sell - {quantity} {symbol_comment}"

            # if buy_or_sell is buy, relocate the values into other-expense category with comment "Crypto Buy - {quantity} {symbol_comment}"
            if transaction_id['buy_or_sell'] == 'buy':
                db.execute(
                "INSERT INTO spending (user_id, transaction_id, spending_type, comment) VALUES (?, ?, ?, ?)",
                user_id, transaction_id['transaction_id'], 'other-spending', buy_comment
                )

            # elif buy_or_sell is sell, relocate the values into other-income category with comment "Crypto Sell - {quantity} {symbol_comment}"
            elif transaction_id['buy_or_sell'] == 'sell':
                db.execute(
                "INSERT INTO income (user_id, transaction_id, income_type, comment) VALUES (?, ?, ?, ?)",
                user_id, transaction_id['transaction_id'], 'other-income', sell_comment
                )

        # elif the investment_category is real-estate
        elif transaction_id['investment_type'] == 'real-estate':
            buy_comment = f"real estate buy - {symbol_comment}"
            sell_comment = f"real estate sell - {symbol_comment}"

            # if buy_or_sell is buy, relocate the values into other-expense category with comment "Real Estate Buy - {symbol_comment}"
            if transaction_id['buy_or_sell'] == 'buy':
                db.execute(
                "INSERT INTO spending (user_id, transaction_id, spending_type, comment) VALUES (?, ?, ?, ?)",
                user_id, transaction_id['transaction_id'], 'other-spending', buy_comment
                )

            # elif buy_or_sell is sell, relocate the values into other-income category with comment "Real Estate Sell - {symbol_comment}"
            elif transaction_id['buy_or_sell'] == 'sell':
                db.execute(
                "INSERT INTO income (user_id, transaction_id, income_type, comment) VALUES (?, ?, ?, ?)",
                user_id, transaction_id['transaction_id'], 'other-income', sell_comment
                )

        # else (other-investment)
        else:
            buy_comment = f"investment Buy - {symbol_comment}"
            sell_comment = f"investment Sell - {symbol_comment}"

            # if buy_or_sell is buy, relocate the values into other-expense category with comment "Investment Buy - {symbol_comment}"
            if transaction_id['buy_or_sell'] == 'buy':
                db.execute(
                "INSERT INTO spending (user_id, transaction_id, spending_type, comment) VALUES (?, ?, ?, ?)",
                user_id, transaction_id['transaction_id'], 'other-spending', buy_comment
                )

            # elif buy_or_sell is sell, relocate the values into other-income category with comment "Investment Sell - {symbol_comment}"
            elif transaction_id['buy_or_sell'] == 'sell':
                db.execute(
                "INSERT INTO income (user_id, transaction_id, income_type, comment) VALUES (?, ?, ?, ?)",
                user_id, transaction_id['transaction_id'], 'other-income', sell_comment
                )

    return jsonify({'status': 'success'})


# Currency route
@app.route("/currency", methods=["GET", "POST"])
@login_required
def choose_currency():
    user_id = session.get("user_id")

    # Get available currencies from the database
    currencies = db.execute(
        "SELECT * FROM currencies"
    )

    # Get a list of previously selected currencies
    previous_currencies = db.execute(
        "SELECT currency_code FROM user_currencies WHERE user_id = ?", user_id
    )
    
    # Change the previously selected currencies into a list
    previous_currencies_list = [row['currency_code'] for row in previous_currencies]

    # Get a list of user selected currencies
    selected_currencies = request.form.getlist('currency')

    if request.method == 'POST':    
        # Update selected currencies to database user_currencies
        # Delete previously selected currencies
        db.execute(
            "DELETE FROM user_currencies WHERE user_id = ?", user_id
        )

        # Add selected currencies
        for currency in selected_currencies:
            db.execute(
                "INSERT INTO user_currencies (user_id, currency_code) VALUES (?, ?)", user_id, currency
            )

        flash('Preferred currencies successfully updated!', 'alert-success')

        return render_template("currency.html", currencies=currencies, previous_currencies=selected_currencies)
    
    return render_template("currency.html", currencies=currencies, previous_currencies=previous_currencies_list)