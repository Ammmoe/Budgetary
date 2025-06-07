# Budgetary

**Video Demo**: [Watch on YouTube](https://www.youtube.com/watch?v=MQWdp7ki3fs)  
**GitHub Repository**: [Project Code](https://github.com/Ammmoe/Budgetary.git)

---

## 🧾 Description

**Budgetary** is a web application for managing personal finances across multiple currencies. It allows users to track their daily budgets in categories such as income, expenses, investments, and debts. The app provides real-time insights into total net worth, financial trends, and transaction history with interactive visualizations.

---

## 🛠️ Technologies

### 🔸 Frontend
- HTML, CSS, Bootstrap, JavaScript
- [Chart.js](https://www.chartjs.org/) – for interactive data visualizations
- [Mark.js](https://markjs.io/) – for highlighting search keywords
- AJAX – for asynchronous UI updates

### 🔹 Backend
- Python (Flask framework)
- SQLite (relational database)
- Jinja (templating engine)
- AJAX (for dynamic server interactions)

### 🔗 APIs
- [Frankfurter API](https://www.frankfurter.app/) – real-time foreign exchange rates
- [Binance API](https://www.binance.com/) – cryptocurrency quotes
- [Yahoo Finance API](https://finance.yahoo.com/) – stock quotes

---

## ✨ Features

1. **User Registration**
2. **Login**
3. **Customized Currency Selection**
4. **Daily Budget Entry**
5. **Multi-Currency Budget Monitoring**
6. **Budget Analysis and Visualization**
7. **Budget History Review**
8. **Change Password**
9. **Logout**

---
 
### 1. User Registration

- **Route:**  
  `@app.route("/register", methods=["GET", "POST"])` in `app.py`

- **Templates:**  
  `register.html`, `layout.html` in the `templates/` directory

- **Database:**  
  `users` table in `budgetary.db`

#### GET Request

- Renders the `register.html` template.
- Any flash message from the previous session is stored in a variable before clearing session data to ensure it's displayed correctly.
- Since `session["user_id"]` is not set (user is logged out), only the **Login** and **Register** tabs are shown in the navigation bar, as determined by the condition `{% if session["user_id"] %}` in `layout.html`.

#### POST Request

1. **Server-Side Validation**
   - Ensures the `username`, `password`, and `password confirmation` fields are submitted.
   - Verifies that `password` and `password confirmation` match.

2. **If Validation Passes**
   - Inserts the `username` and the hashed password (using `generate_password_hash` from `werkzeug.security`) into the `users` table.
   - Redirects the user to the `/login` route (`login.html`).

3. **If Validation Fails**
   - Redirects the user back to the `/register` route (`register.html`).
   - A flash message is displayed to indicate the error.

---

### 2. User Login

- **Route:**  
  `@app.route("/login", methods=["GET", "POST"])` in `app.py`

- **Templates:**  
  `login.html`, `layout.html` in the `templates/` directory

- **Database:**  
  `users`, `user_currencies` tables in `budgetary.db`

#### GET Request

- Renders the `login.html` template.
- Any flash message from the previous session is stored in a variable before clearing session data to ensure it's displayed correctly.
- Since `session["user_id"]` is not set (user is logged out), only the **Login** and **Register** tabs are shown in the navigation bar.

#### POST Request

1. **Server-Side Validation**
   - Ensures the `username` and `password` fields are submitted.
   - Validates the credentials using `check_password_hash` from `werkzeug.security`.

2. **If Validation Passes**
   - Stores the user's ID in `session["user_id"]`.
   - Checks the `user_currencies` table to determine if the user has selected preferred currencies.
     - If not, redirects to `/currency` (`currency.html`).
     - If yes, redirects to `/` (`index.html`).
   - With `session["user_id"]` set (logged-in state), all nav bar items except **Login** and **Register** are shown via the condition `{% if session["user_id"] %}` in `layout.html`.

3. **If Validation Fails**
   - Redirects the user back to the `/login` route (`login.html`).
   - A flash message is displayed to indicate the error.

---

### 3. Customized Currency Selection

- **Route:** `@app.route("/currency", methods=["GET", "POST"])` in `app.py`
- **Templates:** `currency.html`, `layout.html` (in `templates` folder)
- **Authentication:** Protected with the `login_required` decorator from `helpers.py`
- **Database Tables:** `currencies`, `user_currencies` (in `budgetary.db`)

- **Author's Note:**  
  The available currencies are sourced from the [Frankfurter API](https://www.frankfurter.app/), with `MMK (Myanmar Kyat)` manually added to include support for my home currency.

#### GET Request
- Retrieves the list of available currencies from the `currencies` table.
- Fetches the user's previously selected currencies from the `user_currencies` table.
- Renders the `currency.html` template, displaying all available currencies in a `<select>` menu with the previously selected ones preselected.

#### POST Request
- Receives the updated currency selection via `request.form.getlist('currency')`.
- Deletes the user's previously selected currencies from the `user_currencies` table.
- Inserts the new currency selections for that user into the `user_currencies` table.

---

### 4. Daily Budget Entry

- **Route:** `@app.route("/budgetary", methods=["GET", "POST"])`
- **Templates:** `budgetary.html`, `layout.html`
- **Authentication:** Protected with the `login_required` decorator from `helpers.py`
- **Database Tables:** `user_currencies`, `transactions`, `income`, `spending`, `investment`, `debt`

#### `budgetary.html` Template

1. **Form Fields Visibility**
   - All budget category sections (`income`, `expense`, `investment`, `debt & receivable`) are initially hidden using `style="display: none;"`.
   - When a user selects a category from the dropdown (`#budgetary-type`), the JavaScript function `displayForm(this.value)` is triggered.
   - This function reveals the corresponding section using:  
     `document.getElementById(type).style.display = "block";`.

2. **Date Input Autofill**
   - The current date is automatically filled using JavaScript functions: `getDate()`, `getMonth()`, and `getFullYear()`.

3. **Client-Side Validations**
   - **Debt & Receivable Category:**  
     The `enableInterestRate()` function disables the interest rate field when `repayment` is selected, preventing logical conflicts in the database.
   
   - **Investment Category:**  
     The `setInvestmentQuantity()` function sets the `quantity` field to `1` and disables it if `real-estate` or `other-investment` is selected, ensuring accurate data tracking.

#### GET Request
- Renders the `budgetary.html` template.
- Fetches and displays user-selected currencies in the currency selection menu.

#### POST Request

1. **Server-Side Validations**
   - **General Validations:**
     - Ensures the `date` field is provided.
     - Validates dropdown values against allowed options.
     - If `other-income`, `other-spending`, or `other-investment` is selected, the `comment` field is required.
     - Otherwise, all required fields for the selected category must be submitted (except `comment`).
     - Fields like `quantity`, `interest rate`, and `amount` are validated using `isinstance()` and must be non-zero positive values.

   - **Investment Category:**
     - If a `stock symbol` or `cryptocurrency symbol` is entered, it is validated using:
       - `stock_lookup(symbol)` for stocks via Yahoo Finance API
       - `crypto_lookup(symbol)` for crypto via Binance API

   - **Debt & Receivable Category:**
     - Each `borrow` or `lend` entry must use a unique `debtor_or_creditor` string to track individual debts.
     - For `repayment`, the name must already exist in the database.
     - The `repayment amount` must be equal to or less than the total debt (`original amount + interest`).

2. **Database Updates**
   - Valid data is inserted into both the relevant category table (`income`, `spending`, `investment`, or `debt`) and the `transactions` table.
   - Normally, each POST inserts one record into each table.
   - **Special Case — Repayment:**
     - Two updates each are made to the `debt` and `transactions` tables:
       1. Record the repaid amount.
       2. Record the remaining debt (if the repayment is partial).
     - This ensures accurate tracking for repayments less than 100%.

---

### 5. Multi-currency Budget Monitoring

- **Routes in `app.py`:**  
  - `@app.route("/", methods=["GET", "POST"])`  
  - `@app.route("/convert_currency")`  
  - `@app.route("/convert_profit_currency")`  
  - `@app.route("/delete_investment", methods=["POST"])`  
  - `@app.route("/delete_debt", methods=["POST"])`  

- **Templates:**  
  - `index.html`  
  - `layout.html` (in `templates` folder)  

- **Server-Side Login Validation:**  
  - `login_required` decorator from `helpers.py`  

- **Database Tables:**  
  - `user_currencies`  
  - `transactions`  
  - `income`  
  - `spending`  
  - `investment`  
  - `debt`  

---

#### `index.html` Template Overview

1. **Layout:**  
   - The homepage features **4 information cards** displaying:  
     - Total net worth  
     - Cash & bank deposits  
     - Investments  
     - Debts & receivables  
   - The **Investments** and **Debts & Receivables** cards are conditionally rendered only if relevant data exists, using Jinja conditions:  
     ```jinja
     {% if investment_rows %} ... {% endif %}
     {% if debt_rows %} ... {% endif %}
     ```  

2. **Currency Conversion Functions (AJAX - GET requests):**  
   - There are **4 AJAX functions** for currency conversion:  
     - `convertCashCurrency()`  
     - `convertInvestmentCurrency()`  
     - `convertDebtCurrency()`  
     - `convertAssetCurrency()`  
   - Each function sends `currency` and `amount` parameters to server-side routes:  
     - `/convert_currency`  
     - `/convert_profit_currency`  
   - Server uses the `forex_rate()` function (from `helpers.py`) to perform conversion and returns formatted values as JSON.  
   - This enables seamless client-side currency conversion **without page refresh**.  

3. **Deleting Investment Rows (AJAX - POST request):**  
   - Investments with `quantity == 0` display a **delete button** on their row, controlled by Jinja:  
     ```jinja
     {% if row['quantity'] == 0 %} ... {% endif %}
     ```  
   - Clicking the delete button triggers the JavaScript function `deleteInvestment(event)`.  
   - This function sends either the `symbol` (for stock and cryptocurrency investments) or `comment` (for real estate and other investment types) to the server via a POST request to `/delete_investment`.  
   - **POST method** is used because this action modifies data on the server (deletion).  
   - On the server:  
     - Relevant rows in the `investment` table are fetched and deleted.  
     - If the deleted record corresponds to a **selling investment**, a replacement record is inserted into the `income` table.  
     - If it is a **buying investment**, a replacement is inserted into the `spending` table.  
     - Transaction IDs of the deleted rows are reassigned accordingly.  
   - After successful deletion and replacement, the server responds with JSON `{ "status": "success" }`.  
   - Upon receiving this success status, the client-side JavaScript reloads the page:  
     ```js
     window.location.reload();
     ```  

4. **Deleting Debt Rows (AJAX request using POST)**

   - A **delete button** is provided for fully repaid debt records, as these have less value in the database and can be safely removed.  
   
   - For debts & receivables, if a debt is **fully repaid** (`amount == 0`), the delete button appears on that specific row within the debts & receivables card, controlled by the Jinja condition:  
     ```jinja
     {% if row['amount'] == 0 %} ... {% endif %}
     ```  
   - Clicking the delete button triggers the JavaScript function `deleteDebt(event)`.  
   
   - The `deleteDebt()` function sends the `debtor_or_creditor` string to the server via an AJAX POST request to the route:  
     ```python
     @app.route("/delete_debt", methods=["POST"])
     ```  
   
   - **Note 1:** POST method is used because this operation modifies server-side data (deletion), which is not reflected directly on the frontend without a reload.  
   
   - On the server side, the `delete_debt()` function:  
     - Retrieves relevant rows from the `debt` table into a variable.  
     - Uses the helper function `repay_check(debtor_or_creditor)` (from `helpers.py`) to obtain and store:  
       - The **very first debt_category**  
       - The **very first transaction_id**  
   
   - **Note 2:**  
     The database updates twice for each repayment in the `/budgetary` route—once for the paid amount and once for the remaining amount.  
     - If the **very first debt_category** is `borrow` and a partial repayment exists, the remaining amount is recorded with the same debt_category (`borrow`).  
     - Therefore, reassigning *all* deleted transaction IDs into the `income` table would inflate the data due to this partial repayment.  
     - To avoid this, only the **very first transaction_id** is reassigned to either the `income` or `spending` table for all debt_categories other than `repayment`.  
   
   - The deletion and reassignment logic:  
     - Deletes relevant rows from the `debt` table.  
     - If the deleted row's `debt_category` is `borrow` or `lend` and its `transaction_id` **is not equal** to the very first transaction ID, the corresponding row in the `transactions` table (matching `transactions.id`) is also deleted.  
     - If the deleted row's `debt_category` is `borrow` and its `transaction_id` **equals** the very first transaction ID, a replacement row is inserted into the `income` table.  
     - If the deleted row's `debt_category` is `lend` and its `transaction_id` equals the very first transaction ID, a replacement row is inserted into the `spending` table.  
     - If the deleted row's `debt_category` is `repayment`:  
       - And the very first debt_category is `lend`, a replacement row is inserted into the `income` table.  
       - Otherwise, if the very first debt_category is `borrow`, a replacement row is inserted into the `spending` table.  
   
   - Upon successful deletion and reassignment, the server responds with JSON:  
     ```json
     { "status": "success" }
     ```  
   - The client-side JavaScript listens for this response and reloads the page upon success:  
     ```js
     window.location.reload();
     ```

- **GET Request:** 

    1. **Getting User Currencies**

        - **Note:** When calculating budgets, relying solely on the `user-selected currencies` stored in the `user_currencies` table is insufficient. If a user previously used a currency but later changes their selections, data for those previously used currencies still exist under the same `user_id` in the database. Ignoring them risks accuracy errors during calculations.

        - To avoid this, retrieve both:
          - The `user-selected currencies` from the `user_currencies` table, and
          - The `previously-used currencies` from the `transactions` table for the same `user_id`.

        - Combine these two sets of currencies so calculations include all relevant currencies without accuracy issues.

        - Later in the `/` route, if any previously used currency has a non-zero amount in `cash` or `bank deposit`, add that currency to the `user_currencies` table to keep the data consistent.

    2. **Cash & Bank Deposits Calculation**

        - Loop through each currency in the combined `user-selected currencies`.

        - For each currency, separately obtain totals for `cash` and `bank transfer` categories from the `income`, `spending`, and `transactions` tables.

        - Similarly, get totals for `cash` and `bank transfer` categories under `investment: buy` and `investment: sell` from the `investment` and `transactions` tables.

        - Retrieve relevant `debt_rows` from the `debt` table (including the first row and all repayment rows for each `debtor_or_creditor`) as explained in *Note 2* of the section **4. Deleting Debt Rows**. For these, separately total amounts for `cash` and `bank transfer` under the categories `borrow`, `lend`, `borrow repay`, and `lend repay` from the `debt` and `transactions` tables.

        - Calculate existing `cash` and `bank deposits` for the current currency by summing:
          - `income`, `investment: sell`, `borrow`, and `lend repay`
          - Then subtracting `spending`, `investment: buy`, `lend`, and `borrow repay`

        - Convert these `cash` and `bank deposits` values to `USD` for consistent total amount calculation.

        - After processing all currencies, store the user's total `cash` and `bank deposits` in USD.

        - Render the cash & bank deposits information per currency and the total amount in USD on the homepage’s corresponding information card.

    3. **Investments Calculation**

        - **Note:** Previously, `cash & bank deposits` were calculated, but to determine the `total net worth` accurately, the value of investments must be included.

        - Retrieve the user's `investment_rows`, where quantities and amounts are already aggregated per investment item.

        - Loop through each investment row:

            - For **stocks**:
              - Use the `amount_in_usd` as the original purchase value.
              - Obtain the current stock price via the `Yahoo API` using `stock_lookup(symbol)`.
              - Calculate the current market value as `current price × quantity`.
              - Profit/loss = `market value - amount_in_usd`.

            - For **cryptocurrencies**:
              - Use the `amount_in_usd` as the original purchase value.
              - Obtain current crypto price via the `Binance API` using `crypto_lookup(symbol)`.
              - Calculate current market value as `current price × quantity`.
              - Profit/loss = `market value - amount_in_usd`.

            - For **real estate** or **other investments**:
              - Market values cannot be fetched dynamically.
              - If the item is not sold (`quantity = 1`), market value = original value, profit/loss = 0.
              - If sold (`quantity = 0`), market value = 0, profit/loss is the sold value minus the purchase value (already pre-calculated in the database).

        - Render each investment item with its market value and profit/loss in the homepage's investments card.

        - All investment values are in USD, enabling straightforward aggregation for `total_investment`.

    4. **Debts & Receivables Calculation**

        - **Note 1:** To calculate the user's `total net worth` precisely, add receivables and subtract debts in addition to cash, bank deposits, and investments.

        - Retrieve `debt_rows` from the `debt` table, selecting only the last inserted row for each unique `debtor_or_creditor`.

        - **Note 2:** If no repayment rows exist for a debtor/creditor, the very first debt row is used for interest calculations to maintain accuracy. If repayment rows do exist, using the last inserted row still provides correct interest information, as it reflects the remaining debt (refer to *Note 2* in section **4. Deleting Debt Rows**).

        - Loop through each `debt_row` to:

            - Extract the original debt amount and monthly interest rate.
            - Calculate the days passed since the transaction date with `days_difference(past_date_str)` from `helpers.py`.
            - Compute the interest in the original currency using the formula:
              
              ```
              interest = original_debt_amount × monthly_interest_rate × (days_diff / 30)
              ```

            - Convert the interest to USD for the total interest calculation.
            - Calculate the final debt amount as:
              
              ```
              final_debt = original_debt_amount + interest
              ```

            - Convert the final debt to USD for total debt aggregation.

        - Render each debt row with its calculated interest and final debt on the homepage’s debts & receivables card, along with total interest and total debt values.

---

### 6. Budget Analysis and Visualization

- **Routes in `app.py`:**  
  - `@app.route("/analysis", methods=["GET", "POST"])`  
  - `@app.route("/analysis_filter")`

- **Templates:**  
  - `analysis.html`  
  - `layout.html` (in `templates`)

- **Server-Side Login Validation:**  
  - Uses the `login_required` decorator from `helpers.py`

- **Database Tables:**  
  - `user_currencies`  
  - `transactions`  
  - `income`  
  - `spending`  
  - `investment`  
  - `debt`

- **`analysis.html` Template Details:**

  1. **Layout**  
     - Contains 4 cards:  
       - `Total Net Worth Breakdown`  
       - `Inflows vs Outflows Analysis`  
       - `Inflows Breakdown`  
       - `Outflows Breakdown`  
     - Each card includes a `<canvas>` element for dynamic chart rendering.

  2. **Chart Creation Using Chart.js**  
     - Chart.js library is included via:  
       ```html
       <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
       ```  
     - Data sets are extracted from HTML elements and converted from strings to numbers using:  
       ```js
       Number(document.getElementById('#id-name').innerText)
       ```  
     - Labels and background colors are hard-coded per chart.  
     - Chart types:  
       - Doughnut chart:  
         ```js
         new Chart('#canvas-id', { type: 'doughnut', ... })
         ```  
       - Bar chart:  
         ```js
         type: 'bar'
         ```  
       - Stacked bar chart configuration:  
         ```js
         x: { stacked: true },  
         y: { stacked: true }
         ```  
       - Horizontal bar chart uses:  
         ```js
         options: { indexAxis: 'y' }
         ```

  3. **Hiding Data Labels with Zero Values**  
     - Some data labels in `inflows vs outflows analysis`, `inflows breakdown`, and `outflows breakdown` may be zero.  
     - To improve chart clarity, zero-value labels are hidden using the function:  
       ```js
       hideElementByClass('checkZero')
       ```  
     - Structure:  
       - Each data label has a `checkZero` class.  
       - Its parent container has a `parentElement` class.  
     - The function loops through `.checkZero` elements, parses their text content, and if the value is zero, sets the parent element’s display to `none`.

  4. **Updating Charts via Filtering (AJAX GET Request)**  
     - The `Inflows vs Outflows Analysis` card includes filter inputs: `start date`, `end date`, and `currency`.  
     - On clicking the filter button, the AJAX function `analysisFilter()` is triggered.  
     - This function sends the filter inputs and the `total net worth breakdown` data to the server through the `/analysis_filter` GET route.  
     - The server responds with a JSON payload containing updated data for all charts.  
     - The client parses this JSON and updates the corresponding label values in the HTML.  
     - Chart datasets are replaced with updated data, and each chart is refreshed via `chartName.update();`.  
     - After chart updates, zero-value labels are again hidden by calling `hideElementByClass('checkZero');`.  
     - The element with ID `#formatted-net-balance` has its CSS class updated based on its value to reflect:  
       - Greenish background for positive values  
       - Reddish background for negative values  
       - Greyish background for zero  
       This is handled by the function:  
       ```js
       updateNetBalanceDisplay(data.net_balance, selectedCurrency);
       ```  
     - Finally, all numeric data values are formatted to show 2 decimal places with comma separators, adjusted for the selected currency, via:  
       ```js
       updateCurrencyDisplay(selectedCurrency);
       ```

- **GET Request:**  

  1. **`/analysis` Route**  

     - **Purpose:**  
       This route calculates the necessary values used in the charts on the analysis page.  

     - **Investments Calculation:**  
       Investment values are computed using the same logic as described in  
       *5. Multi-Currency Budget Monitoring > GET Request > 3. Investments Calculation*.  

     - **Debts & Receivables Calculation:**  
       Calculated following the method outlined in  
       *5. Multi-Currency Budget Monitoring > GET Request > 4. Debts & Receivables Calculation*.  

     - **Inflows & Outflows Calculation:**  
       The calculation here differs from the `/` route (`index.html`). The `/` route focuses on cash and bank deposits by currency for precise budget monitoring.  
       In contrast, the `/analysis` route centers on the `type` of each budget category in SQLite queries, as `type-amount` relationships are essential for budget analysis.  

       - The process begins by looping through each user currency as explained in  
         *5. Multi-Currency Budget Monitoring > GET Request > 1. Getting User Currencies*.  
       - For each currency, the amounts associated with each `type` in the `income`, `spending`, `investment`, and `debt` tables are queried. For detailed understanding, refer to the database queries in  
         *5. Multi-Currency Budget Monitoring > GET Request > ...*.  
       - All calculated values are stored in a dictionary named `currency_var`. This dictionary helps reduce API calls in the `/analysis` route.  
       - The sum of values in `currency_var` (`currency_var_sum`) is computed. If this sum is `0`, the foreign exchange API call is skipped for that currency to reduce load time, especially when many currencies have zero values.  
       - Values are converted to USD to unify currency units for chart display.  
         - If the currency is `MMK`, a manual exchange rate `MMK_EXCHANGE_RATE` is applied.  
         - For other currencies (excluding USD), the exchange rate is fetched using `forex_rate(currency_v)["rate"]` via the Yahoo API.  
       - Financial components for inflows and outflows are then calculated, enabling computation of `net_balance = inflows - outflows` and `total_assets` (aka total net worth).  
       - Finally, the route renders the page, providing all required data for chart generation and label values.

  2. **`/analysis_filter` Route**  

     - **Purpose:**  
       This route handles AJAX GET requests from the `analysisFilter()` JavaScript function when the user applies filters for `start date`, `end date`, and `currency` and clicks the filter button.  
       Client data is accessed via `request.args.get("key")`.  

     - **Calculations:**  
       - The calculation steps closely follow those in the `/analysis` route.  
       - However, the `total net worth` is **not recalculated**, since it was already obtained during the initial GET request. The data for the `total net worth breakdown` chart is reused from the client side, avoiding redundant computations for investments and debts & receivables.  
       - Because filtering by date is required, an additional `WHERE` clause is dynamically added to the database queries.  
         - If both `start date` and `end date` are provided, the clause becomes:  
           ```sql
           transactions.transaction_date BETWEEN ? AND ?
           ```
           to restrict data to the requested period.  
         - Otherwise, the `WHERE` clause remains empty to include all data for the user.  
       - The selected currency filter is applied by converting all calculated USD values back to the user-selected currency:  
         - `MMK` uses `MMK_EXCHANGE_RATE`.  
         - Other currencies use `forex_rate(selected_currency)["rate"]` from the Yahoo API.  
       - Finally, the filtered and currency-converted data is returned as JSON to the client, where the browser updates the charts and label data accordingly.

---

### 7. Budget History Review

- **Route:**  
  `@app.route("/history", methods=["GET", "POST"])` in `app.py`

- **Templates:**  
  `history.html` and `layout.html` (located in `templates` folder)

- **Server-Side Login Validation:**  
  Uses the `login_required` decorator from `helpers.py`

- **Database Tables:**  
  `transactions`, `income`, `spending`, `investment`, and `debt`

- **`history.html` Template:**  

  1. **Layout:**  
     - Contains **3 information cards** displaying historical logs for:  
       - `Incomes & Expenses`  
       - `Investments`  
       - `Debts & Receivables`  
     - Each card is conditionally displayed only if there is relevant data, using Jinja: 
       ```jinja
       {% if income_spending_rows %}
       {% if investment_rows %}
       {% if debt_rows %}
       ```

  2. **Searching and Highlighting Keywords with Mark.js:**  
     - Mark.js library is included via CDN in `layout.html` header:  
       ```html
       <script src="https://cdn.jsdelivr.net/npm/mark.js/dist/mark.min.js"></script>
       ```  
     - The search input with id `searchKeyword` listens for user input:  
       ```js
       document.getElementById('searchKeyword').addEventListener('input', function() { ... });
       ```  
     - Search is case-insensitive by converting input and table row text content to lowercase.  
     - Each table row is processed:  
       - Previous highlights are cleared with `.unmark()` before applying new highlights.  
       - If a row contains the keyword, it is shown (`row.style.display = '';`) and matching text is highlighted using Mark.js:  
         ```js
         instance.mark(filter, ...);
         ```  
       - Rows without matches are hidden (`row.style.display = 'none';`).

- **GET Request:**  

  - Data extraction queries:  
    - `income_spending_query` retrieves combined data from `income` and `spending` tables.  
    - `investment_query` retrieves data from `investment` table (excluding the `comment` column for `stock` and `cryptocurrency` types; instead, the `symbol` column is selected).  
    - `debt_query` retrieves data from `debt` table.  

  - In `debt_query`, if the category is `repay`, the function `repay_check(debtor_or_creditor)` (from `helpers.py`) clarifies whether it is a `borrow repay` or `lend repay`.  
    - This classification controls the text color in HTML:  
      - `lend repay` → green text  
      - `borrow repay` → red text  

  - Extracted rows are passed to `history.html` and rendered inside the 3 respective information cards.

- **POST Request:**  

  - Triggered when the user filters history by `start date` and `end date`.  
  - Query logic mirrors the GET request with the addition of a date filter:  
    ```sql
    WHERE transactions.transaction_date BETWEEN ? AND ?
    ```  
  - If either `start date` or `end date` is missing, the filter is ignored and unfiltered data is returned.  
  - Debt categories with `repay` are processed as in the GET request for display clarity.  
  - Filtered data is rendered in `history.html` within the same 3 information cards.

---

### 8. Changing Password

- **Route:**  
  `@app.route("/change-password", methods=["GET", "POST"])` in `app.py`

- **Templates:**  
  `change-password.html` and `layout.html` (located in `templates` folder)

- **Server-Side Login Validation:**  
  Uses the `login_required` decorator from `helpers.py`

- **Database:**  
  `users` table in `budgetary.db`

- **GET Request:**  
  - Renders the `change-password.html` template.

- **POST Request:**  

  1. **Server-side Validation:**  
     - Verifies that the fields `old password`, `new password`, and `confirmation` are submitted.  
     - Checks if `new password` and `confirmation` match.  
     - Validates the `old password` against the stored hash in the `users` table using `check_password_hash` from the `werkzeug.security` module.

  2. **If Validation Passes:**  
     - Updates the user’s password hash in the `users` table with the hash of the `new password`, generated via `generate_password_hash` from `werkzeug.security`.  
     - Redirects the user back to the `/change-password` route.  
     - Displays a flash message notifying the user that the password was successfully changed.

  3. **If Validation Fails:**  
     - Redirects the user back to the `/change-password` route.  
     - Displays a flash message with the appropriate error message.

---

### 9. Logout

- **Route:**  
  `@app.route("/logout")` in `app.py`

- **Templates:**  
  `layout.html` (located in `templates` folder)

- **GET Request:**  
  - Logs the user out by clearing the session.  
  - Redirects the user to the `/login` page.

---

## Copyrights and Credits

- **Web Application Name:**  
  **BUDGETARY** (suggested by [ChatGPT](https://www.openai.com/chatgpt)).

- **Background Image:**  
  Created by `588ku - pngtree`.  
  Source: [Cartoon Internet Business Finance Poster Background](https://th.pngtree.com/freebackground/cartoon-internet-business-finance-poster-background_1071853.html?sol=downref&id=bef)

- **Budget Icon:**  
  Created by `Freepik - Flaticon`.  
  Source: [Budget Icons on Flaticon](https://www.flaticon.com/free-icons/budget)

---
