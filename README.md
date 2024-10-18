# BUDGETARY
#### Video Demo:  [Budgetary](https://www.youtube.com/watch?v=MQWdp7ki3fs)

## Description
**Budgetary** is a web application for managing personal finances across multiple currencies. Users can track their daily budgets in categories like incomes, expenses, investments, and debts, with real-time insights on net worth, financial trends, and detailed logs.

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

## Features

1. User Registration

2. Login

3. Customized Currency Selection

4. Daily Budget Entry

5. Multi-currency Budget Monitoring

6. Budget Analysis and Visualization

7. Budget History Review

8. Changing Password

9. Logout
 
### 1. User Registration

- **Route:** 
`@app.route("/register", methods=["GET", "POST"])` in `app.py`

- **Templates:** `register.html` and `layout.html` in `templates`

- **Database:** `users` table in `budgetary.db`

- **GET Request:** 
    
    - Renders the `register.html` template. When rendering, any flash message from the previous session is stored in a variable before clearing session data to ensure the flash message is displayed. 
    
    - As the `layout.html` uses the Jinja condition `{% if session["user_id"] %}`, only the `login` and `register` tabs are displayed in the `nav bar` since the `user_id` has not been established yet in the logged-out state.

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

- **Templates:** `login.html` and `layout.html` in `templates`

- **Database:** `users` and `user_currencies` tables in `budgetary.db`

- **GET Request:** 

    - Renders the `login.html` template. When rendering, any flash message from the previous session is stored in a variable before clearing session data to ensure the flash message is displayed.

    - As the `layout.html` uses the Jinja condition `{% if session["user_id"] %}`, only the `login` and `register` tabs are displayed in the `nav bar` since the `user_id` has not been established yet in the logged-out state.

- **POST Request:** 
    1. Server-side Validation
    
        - Checks if the `username` and `password` fields are submitted.

        - Checks if the `username` and `password` matches with the values stored in the `users` table using the `check_password_hash` function from the `werkzeus.security` module.

    2. If Validation Passes
        
        - `user_id` is stored in `session`. Then, `user_currencies` table is checked to know if the user has selected any `preferred currencies` previously. 

        - If the user has not selected any `preferred currencies`, the user is redirected to `/currency` route (`currency.html`). 

        - If the user has already selected `preferred currencies`, then the user will be redirected to `/` route (`index.html`). 

        - Since `session["user_id"]` is established in the logged-in state, all the nav bar items except the `login` and `register` tabs are displayed by the Jinja condition `{% if session["user_id"] %}` in `layout.html`.
        
    3. If Validation Fails
        
        - The user is redirected to `/login` route (`login.html`) and a flash message is displayed.

### 3. Customized Currency Selection

- **Route:** `@app.route("/currency", methods=["GET", "POST"])` in `app.py`

- **Templates:** `currency.html` and `layout.html` in `templates`

- **Server-Side Login Validation:** `login_required` decorator from `helpers.py`

- **Database:** `currencies` and `user_currencies` tables in `budgetary.db`

- **Author's Note:** The `available currencies` from the `currencies` table are obtained from the `Frankfurter API`. Additionally, `MMK (Myanmar Kyat)` was manually added to the list to include my home currency.

- **GET Request:** Gets the `available currencies` from the `currencies` table and the previously-selected `preferred currencies` from the `user_currencies` table. Renders the `currency.html` template, showing `available currencies` in a `option select` format, with the previously selected `preferred currencies` in the selected state.

- **POST Request:** Gets the newly-selected currencies via `request.form.getlist('currency')`. Delete the previously-selected currencies from the `user_currencies` table and insert the newly-selected currencies to the `user_currencies` table for that `user_id`.

### 4. Daily Budget Entry

- **Route:** `@app.route("/budgetary", methods=["GET", "POST"])`

- **Templates:** `budgetary.html` and `layout.html` in `templates`

- **Server-Side Login Validation:** `login_required` decorator from `helpers.py`

- **Database:** `user_currencies`, `transactions`, `income`, `spending`, `investment`, and `debt` tables

- **`budgetary.html` Template:** 
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

- **Routes in `app.py`:** 
    
    - `@app.route("/", methods=["GET", "POST"])`

    - `@app.route("/convert_currency")`

    - `@app.route("/convert_profit_currency")`

    - `@app.route("/delete_investment", methods=["POST"])`

    - `@app.route("/delete_debt", methods=["POST"])`

- **Templates:** `index.html` and `layout.html` in `templates`

- **Server-Side Login Validation:** `login_required` decorator from `helpers.py`

- **Database:** `user_currencies`, `transactions`, `income`, `spending`, `investment`, and `debt` tables

- **`index.html` Template:** 
    
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

        - To work with the extracted data, we start by looping each of the `debt_rows`. For each row, we can get the `original debt amount` and the `monthly interest rate` from the relevant columns. Then, we calculate how many days have passed between `today` and the `transaction date` using the function `days_difference(past_date_str)` from `helper.py`. Then, the `original debt amount`, `monthly interest rate` and the number of `months: days_diff / 30` is used to calculate the `interest` in its `original currency`. For `total_interest` calculation, the `interest` is also converted to `USD`. Finally, the `final debt amount` is calculated by the equation `final debt = original debt amount + interest`. The `final_debt` is also converted to `USD` for `total_debt` calculation. 

        - Then, each of the `debt_rows` with the `interest` and `final debt` are rendered in the `debts & receivables` information card along with the values of `total_interest` and `total_debt`.

### 6. Budget Analysis and Visualization

- **Routes in `app.py`:** 
    
    - `@app.route("/analysis", methods=["GET", "POST"])`

    - `@app.route("/analysis_filter")`

- **Templates:** `analysis.html` and `layout.html` in `templates`

- **Server-Side Login Validation:** `login_required` decorator from `helpers.py`

- **Database:** `user_currencies`, `transactions`, `income`, `spending`, `investment`, and `debt` tables

- **`analysis.html` Template:** 
    
    1. Layout

        - There are `4` cards, namely, `total net worth breakdown`, `inflows vs outflows analysis`, `inflows breakdown`, and `outflows breakdown`, each containing a canvas to dynamically draw a chart upon.

    2. Creating Charts Using Chart.js Library

        - The source file link for the Chart.js library `<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>` is included at the start of the JavaScript.

        - The required `datasets` for the chart are acquired from the `HTML` page and are changed from `string` to `numeric` values using the script `Number(document.getElementById('#id-name').innerText)`. The `labels` and the `backgroundColor` are then hard-coded for each chart.

        - To specify the type of chart, we can use the syntax `new Chart(#canvas-id, { type: 'doughnut', ...` for `doughnut chart`, and `type: 'bar'` for `bar chart`. In order to create a `stacked bar chart`, we can use the syntax `x: { stacked: true, ... }, y: { stacked: true, ... }`. For a `horizontal bar chart`, the syntax is `options: { indexAxis: 'y', ... `. 

    3. Hiding Data Labels with `0` Value

        - There are numerous `data labels` that can be `0` value in the charts `inflows vs outflows analysis`, `inflows breakdown`, and `outflows breakdown`. Therefore, we need to hide the `data labels` with the `0` value so that the user can view the chart with minimal nuances.

        - In order to do that, the JavaScript function `hideElementByClass('checkZero')` is used. In each of the `<div>` tag of `label` items, there is a class of `parentElement`, and in each `data value`, there is a class of `checkZero`. 

        - The `hideElementByClass('checkZero')` function effectively loops through the `checkZero` classes if each have any `0` value by using the script function `parseFloat(element.textContent.trim());`. If a `0` value is found, then the closest `parentElement` is set to be hidden by the script function `parentElement.style.display = 'none';`.

    4. Updating Charts by Filtering with Date and Currency Values (AJAX request using GET)

        - In the `inflows vs outflows analysis` card, there is a filter input, that accepts the values of `start date`, `end date`, and `currency`. When the `filter` button is clicked, the AJAX function `analysisFilter()` is called.

        - Then, the function sends the filter inputs (`start date`, `end date`, `currency`), and the `data` from the `total net worth breakdown` table to the server via the route `/analysis_filter` using GET request.

        - The server then responds with a `JSON` file containing the `data` for all charts in the page. The `analysisFilter()` function then parse the `JSON` file and replace the `label data values` in the `HTML` page with the updated values.

        - After updating the `label data values`, all the charts are updated by replacing the `existing chart datasets` with the updated ones and calling the function `chartName.update();`.

        - After updating the charts, the `labels` with `0` values are set to be hidden by calling the function `hideElementByClass('checkZero');`. 
        
        - Then the `CSS` class of the id `#formatted-net-balance` is updated based on its value to show a `greenish` background if positive, a `reddish` background if negative, and a `greyish` background if equals to `0` by call the script function `updateNetBalanceDisplay(data.net_balance, selectedCurrency);`. 

        - Finally, all `data` values are formatted to show `2` decimal places in a comma-separated string with the `currency` the user selected using the script function `updateCurrencyDisplay(selectedCurrency);`. 

- **GET Request:** 

    1. `/analysis` Route

        - Note: This route is used to calculate necessary values to be used in the charts of the analysis page.

        - Investments Calculation
            
            Investment values are calculated using the same codes as explained at `5. Multi-Currency Budget Monitoring > GET Request > 3. Investments Calculation` in this document.

        - Debts & Receivables Calculation

            Debts & Receivables are calculated using the same codes as explained at `5. Multi-Currency Budget Monitoring > GET Request > 4. Debts & Receivables Calculation` in this document.

        - Inflows & Outflows Calculation

            The calculation procedure used here is a bit different from the one used in the `/` route (`index.html`). The reason is that in the `/` route, we want to focus on `cash` and `bank deposits` information of each `currency` separately for accurate budget monitoring. 
            
            However, for the `/analysis` route, we focus on the `type` of each `budget category` in our `SQLite` queries since the `type - amount` relations are crucial for budget analysis.

            First, we loop through each currency using the method explained in the `5. Multi-Currency Budget Monitoring > GET Request > 1. Getting User Currencies` in this document.

            Then, we query the `amount` in the `looping currency` associated with each `type` of the `income`, `spending`, `investment`, and `debt` tables. For difficulty understanding the `database queries`, it is advised to read through the session `5. Multi-Currency Budget Monitoring > GET Request > ..`. 

            After that, all the calculated values are assigned inside a newly-created `dictionary` variable called `currency_var`. This variable is specially created with the sole purpose of `reducing the number of API calls` in the `/analysis` route. In the next line of code, we can see the new variable `currency_var_sum = sum(currency_var.values())` that calculates the sum of all calculated values for the `looping currency`. If that `currency_var_sum` is equal to `0`, we will not call API to know the foreign exchange rate of this `looping currency`, effectively reducing the loading time if the user selected so many currencies with `0` used values.

            Next, all the calculated values are converted into `USD` since we require the same unit of currency to be displayed together in one chart. If the `looping currency` is `MMK`, then the manual foreign exchange rate of `MMK_EXCHANGE_RATE` is used. If it is a currency other than `USD` or `MMK`, then the function `forex_rate(currency_v)["rate"]` that uses `Yahoo API` is used to know the exchange rate.

            Then, all the necessary components of financial `inflows` and `outflows` are calculated, thereby, allowing to calculate the `net_balance = inflows - outflows` and the `total_assets` aka `total net worth` as well. 

            Finally, the page is rendered by providing all necessary data of components to be used in creating the `charts` and `label data`. 

    2. `/analysis_filter` route

        - The route is used to process the fetch request from the `AJAX` function `analysisFilter()` when the user enters the `start date`, `end date`, and `currency` information and then click the `filter` button. We can get the information sent from the client side using the function `request.args.get("key")`.

        - Calculations

            All the calculation steps are almost the same as the ones used in the `/analysis` route. However, we will not re-calculate the `total net worth` as it has already been calculated with the `GET request`. For updating the `total net worth breakdown` chart, we will reuse the data for this chart sent from the client side, skipping the calculations steps of `6. Budget Analysis and Visualization > GET Request > 1. Analysis Route > Investments Calculations` and `... > 1. Analysis Route > Debts & Receivables Calculations`.
            
            The other difference is that since we are filtering data by `date`, an additional `WHERE clause` is added to each database query.

            If there is user input for `start date` and `end date`, the `WHERE clause` is updated to `transactions.transaction_date BETWEEN ? AND ?`, effectively filtering data in the requested period. Else, the `WHERE clause` is just set as an `empty string` so all the existing data for that `user_id` will be extracted.

            Since the `filter` also includes `currency` as an input, at the end of the calculations, all calculated values in `USD` will required to be converted to the `user-selected currency` using the exchange rate `MMK_EXCHANGE_RATE` for `MMK`, and the `forex_rate(selected_currency)["rate"]` function that uses `Yahoo API` for currencies other than `USD`. 

            Finally, all the filtered and currency-converted values are returned as a `JSON` file to the client side, where the browser effectively renders the updated `charts` and `label data` for the user's specific request.

### 7. Budget History Review

- **Route:** `@app.route("/history", methods=["GET", "POST"])` in `app.py`

- **Templates:** `history.html` and `layout.html` in `templates`

- **Server-Side Login Validation:** `login_required` decorator from `helpers.py`

- **Database:** `transactions`, `income`, `spending`, `investment`, and `debt` tables

- **`history.html` Template:** 

    1. Layout

        - There are `3 information cards` in `history.html`, which shows all the historical logs of `incomes & expenses`, `investments`, and `debts & receivables`.

        - The `incomes & expenses`, `investments` and `debts & receivables` cards are only shown if there is any relevant information for these sessions using the Jinja code `{% if income_spending_rows %}`, `{% if investment_rows %}` and `{% if debt_rows %}`. 

    2. Searching and Highlighting Keywords Using Mark.js Library

        - The source file link for the Mark.js library `<script src="https://cdn.jsdelivr.net/npm/mark.js/dist/mark.min.js"></script>` is included at the head session of `layout.html`.

        - Each individual input to the id `searchKeyword` is listened using the script syntax `document.getElementById('searchKeyword').addEventListener('input', function() { ...`. Then, the input letters are converted to lowercase in order to search without case sensitivity. 

        - Each table row is looped through and the text content of each row is also converted to lowercase using the script function `row.textContent.toLowerCase();`. Then, a `mark instance` is added to the `looping row` to get ready for highlighting using the `Mark.js` syntax `new Mark(row);`. 

        - Note: It is important to `unmark` any previous highlight before `highlighting` new letters.

        - If the row contains the `Keyword`, the row is displayed using the syntax `row.style.display = '';`. The letters in the table row that matches with the `Keyword` are also highlighted using the syntax `instance.mark(filter, ...`. 

        - If the row does not contain the `Keyword`, then the row is hidden using the syntax `row.style.display = 'none';`.

- **GET Request:** 

    - The data from the `income` and `spending` tables are both extracted using the same `SQLite` query named `income_spending_query`. Then, the data from the `investment` and `debt` tables are extracted separately using the `investment_query` and `debt_query`. All information of the user is extracted from the database except for the `investment_query`, which left out the `comment` category for `stock` and `cryptocurrency` types, for which the `symbol` column is extracted instead of `comment` column.

    - In the `debt_query` rows, if the debt category is `repay`, then the category is processed to explicitly mention if it is `borrow repay` or `lend repay` using the function `repay_check(debtor_or_creditor)` from `helpers.py`. The idea behind this clarification is change the color of the text content to `green` if it is `lend repay` and to `red` if it is `borrow repay` when being displayed in `HTML` page.

    - All the extracted rows are fed to the `history.html`, where all the rows are rendered in `3` separate information cards.

- **POST Request:**

    - This request is processed when the user wants to filter `history` data by date by inputting `start date` and `end date` information and submitting to server.

    - The data query process is the same as that of `GET Request` with the exception that the `WHERE clause` of the queries contains the date filtering part `WHERE transactions.transaction_date BETWEEN ? AND ?`. However, if the user does not fully provide `start date` and `end date`, the `WHERE clause` will not contain date filtering part, causing the query to `return unfiltered information` of that user.

    - Then the debt category of `repay` is further processed as mentioned in the `GET Request`. 

    - All the extracted rows are fed to the `history.html`, rendering all information in `3` separate information cards.

### 8. Changing Password

- **Route:** `@app.route("/change-password", methods=["GET", "POST"])` in `app.py`

- **Templates:** `change-password.html` and `layout.html` in `templates`

- **Server-Side Login Validation:** `login_required` decorator from `helpers.py`

- **Database:** `users` table in `budgetary.db`

- **GET Request:** 

    - Renders the `change-password.html` template.

- **POST Request:** 

    1. Server-side Validation
    
        - Checks if the `old password`, `new password`, and `confirmation` fields are submitted.

        - Checks if the `new password` and `confirmation` inputs are the same.

        - Checks if the hash value of the `old password` using the `check_password_hash` function from the `werkzeus.security` module matches with the hash stored in the `users` table.

    2. If Validation Passes
        
        - The `hash` value in `users` table for that `user_id` is changed to the `hash` value of the `new password` using the `generate_password_hash` function from the `werkzeus.security` module.

        - Then, the user is redirected to the `/change-password` route and a flash message is displayed to notify the user of the successful password change.
        
    3. If Validation Fails
        
        - The user is redirected to the `/change-password` route and a flash message mentioning the error message is displayed.

### 9. Logout

- **Route:** `@app.route("/logout")` in `app.py`

- **Templates:** `layout.html` in `templates`

- **GET Request:** 

    - Logs the user out by clearing the session and redirecting the user to the `/login` page.

## Copyrights and Credits

- Web Application Name: **BUDGETARY** suggested by [ChatGPT](https://www.openai.com/chatgpt).

- [Background Image](https://th.pngtree.com/freebackground/cartoon-internet-business-finance-poster-background_1071853.html?sol=downref&id=bef) created by `588ku - pngtree`.

- [Budget Icon](https://www.flaticon.com/free-icons/budget) created by `Freepik - Flaticon`.
