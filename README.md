# BUDGETARY
#### Video Demo:  <URL HERE>

## Description
**Budgetary** is a web app for managing personal finances across multiple currencies. Users can track their daily budgets in categories like incomes, expenses, investments, and debts, with real-time insights on net worth, financial trends, and detailed logs.

## Technologies

### Frontend
- HTML, CSS, Bootstrap, JavaScript
- Chart.js
- Mark.js
- AJAX

### Backend 
- Flask framework
- Jinja
- AJAX

### APIs
- [Frankfurter API](https://www.frankfurter.app/) to get the foreign currency exchange rate in real time.
- [Binance API](https://www.binance.com/) to get the cryptocurrency quotes in real time.
- [Yahoo Finance API](https://finance.yahoo.com/) to get the stock quotes in real time.

## Copyrights and Credits
- [Background Image](https://th.pngtree.com/freebackground/cartoon-internet-business-finance-poster-background_1071853.html?sol=downref&id=bef) created by `588ku - pngtree`.
- [Budget Icon](https://www.flaticon.com/free-icons/budget) created by `Freepik - Flaticon`.

## Features
1. **User Registration**
2. **Login**
3. **Customized Currency Selection**
4. **Daily Budget Entry**
5. **Multi-currency Budget Monitoring**
6. **Budget Analysis and Visualization**
7. **Budget History Review**
8. **Changing Password**
9. **Logout**
 
### 1. User Registration
- **Route:** 
`@app.route("/register", methods=["GET", "POST"])` in `app.py`

- **Template:** `register.html` in `templates`

- **Database:** `users` table in `budgetary.db`

- **GET Request:** Renders the `register.html` template. When rendering, any flash message from the previous session is stored in a variable before clearing session data to ensure the flash message is displayed.

- **POST Request:** 
    1. Server-Side Validation
    
        - Checks if the `username`, `password`, and `password confirmation` fields are submitted.
        - Checks if the `password` and `password confirmation` matches.

    2. If Validation Passes
        
        - The `username` and `hash value of password` (obtained using `generate_password_hash` from the `werkzeug.security` module) are inserted into the `users` table, completing the registration process. 
        - Then, the user is redirected to the `/login` route (`login.html`).

    3. If Validation Fails
        
        - The user is redirected to the `/register` route (`register.html`) and a flash message is displayed.

### 2. Login
- **Route:** `@app.route("/login", methods=["GET", "POST"])` in `app.py`

- **Template:** `login.html` in `templates`

- **Database:** `users` and `user_currencies` tables in `budgetary.db`

- **GET Request:** Renders the `login.html` template. When rendering, any flash message from the previous session is stored in a variable before clearing session data to ensure the flash message is displayed.

- **POST Request:** 
    1. Server-side Validation
    
        - Checks if the `username` and `password` fields are submitted.
        - Checks if the `username` and `password` matches with the values stored in the `users` table using the `check_password_hash` function from the `werkzeus.security` module.

    2. If Validation Passes
        
        - `user_id` is stored in `session`. Then, `user_currencies` table is checked to know if the user has selected any `preferred currencies` previously. 
        - If the user has not selected any `preferred currencies`, the user is redirected to `/currency` route (`currency.html`). 
        - If the user has already selected `preferred currencies`, then the user will be redirected to `/` route (`index.html`). 
        
    3. If Validation Fails
        
        - The user is redirected to `/login` route (`login.html`) and a flash message is displayed.

### 3. Customized Currency Selection
- **Route:** `@app.route("/currency", methods=["GET", "POST"])` in `app.py`

- **Template:** `currency.html` in `templates`

- **Database:** `currencies` and `user_currencies` tables in `budgetary.db`

- **Author's Note:** The `available currencies` from the `currencies` table are obtained from the `Frankfurter API`. Additionally, `MMK (Myanmar Kyat)` was manually added to the list to include my home currency.

- **GET Request:** Gets the `available currencies` from the `currencies` table and the previously-selected `preferred currencies` from the `user_currencies` table. Renders the `currency.html` template, showing `available currencies` in a `option select` format, with the previously selected `preferred currencies` in the selected state.

- **POST Request:** Gets the newly-selected currencies via `request.form.getlist('currency')`. Delete the previously-selected currencies from the `user_currencies` table and insert the newly-selected currencies to the `user_currencies` table for that `user_id`.

### 4. Daily Budget Entry
- **Route:** `@app.route("/budgetary", methods=["GET", "POST"])`

- **Template:** `budgetary.html` in `templates`

- **Database:** `user_currencies`, `transactions`, `income`, `spending`, `investment`, and `debt` tables

- **HTML Template:** 
    1. Form Fields Visibility
    
        Initially, form fields related to the budget categories `income`, `expense`, `investment`, and `debt & receivable` are hidden using the CSS property `style="display: none;"`. When the user selects a budget category via the selection-menu id `#budgetary-type`, the JavaScript function `onchange="displayForm(this.value)"` is triggered, revealing the hidden blocks of the selected category in the process using the `document.getElementById(type).style.display = "block";` property.
        
    2. Date Input Field
    
         `The date of the computer's operating system` is obtained using the JavaScript functions `getDate()`, `getMonth()`, and `getFullYear()` to automatically fill the `date` input field.
         
    3. Client-Side Validations
        - Debt & Receivable Category
        
            The JavaScript function `enableInterestRate()` disables the `interest rate` field when the user selects `repayment` in `debt & receivable` category to prevent conflict in the database which could occur when the `borrow / lend interest rate` and the `repayment interest rate` are not equal.
            
        - Investment Category

            The JavaScript function `setInvestmentQuantity()` automatically sets the `quantity` field to `1` and disables user input if the investment types `real-estate` or `other-investment` are chosen. This is necessary to keep the investment data monitoring correct in the homepage.

- **GET Request:** Renders the `budgetary.html` template. During rendering, the `user-selected currencies` are extracted from the `user_currencies` table and they are rendered in the `currency selection menu` on this page.

- **POST Request:** 
    1. Server-Side Validations

        - General Validations

            Check if the `date` field is submitted. Check if the submitted values of the dropdown lists are among the valid options. 
            
            If the `other-income`, `other-spending`, and `other-investment` values are selected, `comment` field must be submitted. Otherwise, all relevant input fields for the chosen budget category except the `comment` field must be submitted. 
            
            For validations which expect numerical values such as `quantity`, `interest rate`, and `amount` fields, the `isinstance()` function is used to ensure if the user actually inputs a numerical value. Moreover, they must also be `non-zero positive values`. 
        
        - Investment Category
        
            If the user inputs the `stock symbol` or `cryptocurrency symbol`, the server checks the `stock symbol` with the `Yahoo Finance API` and the `cryptocurrency symbol` with the `Binance API` to ensure the symbol actually exists using the `stock_lookup(symbol)` and `crypto_lookup(symbol)` functions from `helpers.py`. 
            
        - Debt & Receivable Category

            Only one unique string is accepted as `debtor_or_creditor` for each borrow or lend process. This is necessary to keep track of each `debt` or `receivable` without any further complication. If `repayment` is chosen, the `debtor_or_creditor` must already exists in the database. 

            For `repayment`, the `payment amount` must be equal to or lower than the `total debt amount`, which is equal to `original amount + interest rate`.      

    2. Updating Database
    
        If the validation passes, the submitted data in each `budget category` is inserted into its respective tables in the `budgetary.db` database. Generally, a `category` table (income, spending, investment, or debt) and the `transactions` table are updated one time each for one POST request.

        However, for `repayment` in `debt & receivable` category, there are two times the `debt` and `transactions` tables are required to be updated each for one POST request. The `first time` is for inserting the `repaid amount` into the database and the `second time` is for inserting the `remaining amount` into the database. This step is necessary to ensure the `repayment` process works for `less than 100% repayment amounts`.

### 5. Multi-currency Budget Monitoring
- **Route in `app.py`:** 
    
    - `@app.route("/", methods=["GET", "POST"])`

    - `@app.route("/convert_currency")`

    - `@app.route("/convert_profit_currency")`

    - `@app.route("/delete_investment", methods=["POST"])`

    - `@app.route("/delete_debt", methods=["POST"])`

- **Template:** `index.html` in `templates`
- **Database:** `user_currencies` table, `transactions` table, `income` table, `spending` table, `investment` table, and `debt` table

- **HTML Template:** 
    
    1. Layout

        - There are `4 information cards` in `homepage`, which shows `total net worth`, `cash & bank deposits`, `investments`, and `debts & receivables`.

        - The `investments` and `debts & receivables` cards are only shown if there is any relevant information for these sessions using the Jinja code `{% if investment_rows %}` and `{% if debt_rows %}`. 

    2. Convert Currency Functions (AJAX request using GET)

        - There are `4 Asynchronous JavaScript (AJAX) functions` for converting currency, which are `convertCashCurrency()`, `convertInvestmentCurrency()`, `convertDebtCurrency()`, and `convertAssetCurrency()`. 

        - Each function sends the `currency` and `amount` to server side using `AJAX fetch request using GET` through the routes `@app.route("/convert_currency")` and `@app.route("/convert_profit_currency")`.
        
        - Both routes convert the currencies using the `forex_rate()` function from helpers.py and then returns the formatted string values in `JSON` format back to the client side, which then successfully converts the currency without having to refresh the page.

    3. Deleting Investment Rows (AJAX request using POST)

        - It is beneficial in having a delete button for investment records with `0` quantity, which have less value in existing than to be deleted.

        - For investments, if the `quantity` of an investment is already `0`, a `delete button` appears on the specific row of the `investments card` using Jinja condition `{% if row['quantity'] == 0 %}`. If the `delete button` is clicked, the JavaScript function is triggered using `onclick=deleteInvestment(event)` property.

        - Then, the `deleteInvestment()` function sends the `symbol` (if `stock` and `cryptocurrency` types) and `comment` (if `real-estate` and `other-investment` types) to the server side using `AJAX fetch request using POST` throught the route `@app.route("/delete_investment", methods=["POST"])`.

        - Note: POST method is used here because the request includes data deletion from the server, which is not displayed in the front end of the web app.

        - At the server side, the `delete_investment()` function then stores the relevant rows from the `investment` table in a variable.

        - The relevant rows in the `investment` table are deleted. If the deleted row is about `selling investment`, then the replacement row is inserted to the `income` table, and if it is about `buying investment`, then replacement row is inserted to the `spending` table, re-assigning the `transaction_ids` of the deleted rows.

        - Upon successful deletion and re-assignment, a `JSON` file with the `status: success` is returned to the client side. Upon receiving the `status: success`, the JavaScript function reloads the page using the code `window.location.reload();`.

    4. Deleting Debt Rows (AJAX request using POST)
    
        - It is beneficial in having a delete button for fully-repaid debt records, which have less value in existing than to be deleted.

        - For debts & receivables, if the specific debt is `fully repaid`, a `delete button` appears on the specific row of the `debts & receivables card` using Jinja condition `{% if row['amount'] == 0 %}`. If the `delete button` is clicked, the JavaScript function is triggered using `onclick=deleteDebt(event)` property.

        - Then, the `deleteDebt()` function sends the string information of the `debtor_or_creditor` to the server side using `AJAX fetch request using POST` through the route `@app.route("/delete_debt", methods=["POST"])`.

        - Note 1: POST method is used here because the request includes data deletion from the server, which is not displayed in the front end of the web app.

        - At the server side, the `delete_debt()` function then stores the relevant rows from the `debt` table in a variable. Also, using the `repay_check(debtor_or_creditor)` function of `helpers.py`, the `very first debt_category` and the `very first transaction_id` are obtained and stored inside a variable each.

        - Note 2: Remember that the database was updated two times for `repayment` in `/budgetary` route, one time for the `paid amount` and one time for the `remaining amount`. If the `very first debt_category` is `borrow` and there is a `partial repayment`, the `remaining amount` will be inserted to the table with the same `debt_category: borrow`. Therefore, if we were to re-assign all `transaction_ids` from the `deleted rows` into the `income` table, the data will be inflated because of this `repaid amount`. Therefore, for all `debt_categories` other than `repayment`, only the `very first transaction_id` will be re-assigned to the `income` or `spending` table.

        - The relevant rows in the `debt` table are deleted. If the deleted row's `debt_category` is `borrow` or `lend` and the `transaction_id` is not equal to the `very first transaction_id`, the row from `transactions` table with the same `transactions.id` is deleted. If the deleted row's `debt_category` is `borrow` and the `transaction_id` is equal to the `very first transaction_id`, the replacement row is inserted to the `income` table, and else if is the case for `lend`, the replacement row is inserted to the `spending` table. If the deleted row's `debt_category` is `repayment` and the `very first debt_category` is `lend`, the replacement row is inserted to the `income` table, and else if the `very first debt_category` is `borrow`, then the replacement row is inserted to the `spending` table.

        - Upon successful deletion and re-assignment, a `JSON` file with the `status: success` is returned to the client side. Upon receiving the `status: success`, the JavaScript function reloads the page using the code `window.location.reload();`.

- **GET Request:** 

    1. Getting User Currencies
    
        - Note: When calculating the budgets, we cannot just use the `user-selected currencies` in the `user_currencies` table. If the user has used another currency before and then they change their `user_currencies`, the data for that another currency will be sitting around with the same `user_id`, waiting for a potential error to emerge when calculating a large sum of data. Therefore, we cannot ignore the `previously-used currencies` for that `user_id`. 

        - Get the `user-selected currencies` from the `user_currencies` table in a variable, and also get the `previously-used currencies` from the `transactions` table for the same `user_id` in another variable. Then, add the `previously-used currencies` to the `user-selected currencies` so that we can start the calculation with no accuracy error.

        - Later in the `/` route, if each `previously-used currency` has an existing amount of `cash` or `bank deposit`, then this currency is added to the `user_currencies` table.

    2. Cash & Bank Deposits Calculation

        - Loop through each currency in `user-selected currencies`.

        - For each currency, get the total amount for `cash` and `bank transfer` categories separately from `income`, `spending`, and `transactions` tables.

        - Also get the total amount for `cash` and `bank transfer` categories separately for `investment: buy` and `investment: sell` types from `investment` and `transactions` tables.

        - Finally, the `debt_rows` database query extracts rows from the `debt` table with the `first row` and all `repayment rows` of `each debtor_or_creditor` for accurate data calculation as explained in the `Note 2` of the sub-title `4. Deleting Debt Rows`. Then the total amount for `cash` and `bank transfer` categories are obtained separately for `borrow`, `lend`, `borrow repay`, and `lend repay` types from `debt` and `transactions` tables.

        - Then the existing `cash` and `bank deposits` for the `looping currency` are obtained by adding `income`, `investment: sell`, `borrow`, and `lend repay` categories, and subtracting `spending`, `investment: buy`, `lend`, and `borrow repay` categories.

        - After that, the `cash` and `bank deposits` values for the `looping currency` is converted to `USD` for total amount calculation.

        - When all `user-selected currencies` are looped through, the total `cash` and `bank deposits` of the user is stored accurately in the `USD` format.

        - The `cash` and `bank deposits` information of `each currency` and the `total amount in USD` are rendered in the `cash & bank deposits` information card of the homepage.

    3. Investments Calculation

        - Note: We calculated `cash & bank deposits` previously. If we want to calculate the `total net worth`, however, the existing amount of `cash & bank deposits` is not the correct answer because the `investments` that you possess also worth a value and it should be added in order to get the `total net worth`. 

        - Firstly, we get the `investment_rows` of the `user_id` with their quantities and amounts already summed up for each investment item. Then we loop through each row (each investment item). 

        - If the `investment_type` is `stock`, the `original value` of the stock that the user bought is obtained from the `amount_in_usd` column of the `looping row`. Then, we get `current stock price` of that specific stock symbol from the `Yahoo API` using the function `stock_lookup(symbol)`. Subsequently, we can get the `market value` of the user's stock by multiplying `current stock price` with the `quantity`. For profit / loss, the value is calculated by subtracting `amount_in_usd` from the `market value`.

        - If the `investment_type` is `cryptocurrency`, the `original value` of the cryptocurrency that the user bought is obtained from the `amount_in_usd` column of the `looping row`. Then, we get `current cryptocurrency price` of that specific crypto symbol from the `Binance API` using the function `crypto_lookup(symbol)`. Subsequently, we can get the `market value` of the user's cryptocurrency by multiplying `current cryptocurrency price` with the `quantity`. For `profit / loss`, the value is calculated by subtracting `amount_in_usd` from the `market value`.

        - If the `investment_type` is `real-estate` or `other-investment`, we cannot know the `market value` of each investment item. Therefore, if the investment item is not sold yet (`quantity: 1`), then the `market value` is set as the `original value` and the `profit / loss` is `0`. If the investment item is sold, (`quantity: 0`), then the `market value` is set as `0` and the `profit / loss` is `sold value - buy value`, which is already calculated in the database query (`investment_rows`).

        - Then, each `investment_row` with `market value` and `profit / loss` values are rendered in the `investments` information card of the homepage. Note that the investment values that we work with in this session are all in `USD` so we can just add them directly for `total_investment` calculation.

    4. Debts & Receivables Calculation

        - Note 1: So far, we have already calculated `cash & bank deposits` and `investments`. However, in order to get the user's `total net worth` accurately, we need to add `receivables` and subtract `debts` into our equations.

        - Firstly, `debt_rows` are extracted from the `debt` table. These `debt_rows` only contain the `last-inserted rows` for each `debtor_or_creditor`. 

        - Note 2: If there are no `repayment rows` for a unique `debtor_or_creditor`, then `the very first row` is used for calculating `interest` so the result is correct. Even if there are `repayment rows`, since we only extract the `last-inserted row`, the `interest` calculation would still be correct because the `last-inserted row` is the row with the information of `remaining debt amount` (Remember we have to insert twice for `repayment` category - see `Note 2` of the sub-title `4. Deleting Debt Rows`).

        - To work with the extracted data, we start by looping each of the `debt_rows`. For each row, we can get the `original debt amount` and the `monthly interest rate` from the relevant columns. Then, we calculate how many days have passed between `today` and the `transaction date` using the function `days_difference(past_date_str)`. Then, the `original debt amount`, `monthly interest rate` and the number of `months: days_diff / 30` is used to calculate the `interest` in its `original currency`. For `total_interest` calculation, the `interest` is also converted to `USD`. Finally, the `final debt amount` is calculated by the equation `final debt = original debt amount + interest`. The `final_debt` is also converted to `USD` for `total_debt` calculation. 

        - Then, each of the `debt_rows` with the `interest` and `final debt` are rendered in the `debts & receivables` information card along with the values of `total_interest` and `total_debt`.

        
