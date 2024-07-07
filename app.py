import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, stock_lookup, amount_in_usd, crypto_lookup


# Configure application
app = Flask(__name__)
#cache = Cache(app, config={'CACHE_TYPE': 'redis'})

# Custom filter
# app.jinja_env.filters["usd"] = usd

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


@app.route("/")
@login_required
def index():
    # Create homepage routes
    return apology("TO DO", 400)


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
                    user_id, transaction_id, investment_type, other_investment, stock_symbol, buy_sell, quantity
                )
                flash('Success!', 'alert-success')
                return redirect(url_for('budgetary'))

            # If cryptocurrency is chosen for investment_type...
            elif investment_type == 'cryptocurrency': 
                # Update investment table
                db.execute(
                    "INSERT INTO investment (user_id, transaction_id, investment_type, investment_comment, symbol_real_estate_type, buy_or_sell, quantity) \
                    VALUES (?, ?, ?, ?, ?, ?, ?)",
                    user_id, transaction_id, investment_type, other_investment, crypto_symbol, buy_sell, quantity
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
    # Create analysis routes
    return apology("TO DO", 400)


@app.route("/history")
@login_required
def history():
    # Create budgetary logs
    return apology("TO DO", 400)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # Get registered user data via POST
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure re-type password field was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Ensure password and re-typed password match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # Register username and hashed password in the database
        try:
            rows = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get(
                    "username"), generate_password_hash(request.form.get("password"))
            )
            # Redirect user to home page
            return redirect("/login")

        except ValueError:
            return apology("username already exists", 400)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")