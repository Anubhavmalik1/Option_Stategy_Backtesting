---

## 🧠 Strategy: Bank Nifty Option Selling Based on Early Trend

### 🎯 Objective:

To capture early directional moves in Bank Nifty using a simple price action-based rule and generate intraday profits by selling ATM (At-The-Money) options.

---

### 🔧 Strategy Logic:

1. **Static Entry & Exit:**

   * **Entry Time:** 9:25 AM
   * **Exit Time:** 3:15 PM (intraday only)

2. **Signal Generation Based on Price Movement:**

   * Retrieve **Bank Nifty LTP at 9:15 AM** and **9:25 AM**.
   * Compare the two:

     * If **9:25 LTP > 9:15 LTP**, market is showing early bullish momentum → **Sell ATM PUT**
     * If **9:25 LTP < 9:15 LTP**, market is showing early bearish momentum → **Sell ATM CALL**

3. **Strike Price Selection:**

   * Determine the **ATM strike** by rounding the 9:25 AM  price to the nearest 100 (e.g., 36545 → 36500).

4. **Instrument Selection:**

   * Use the **monthly expiry option** for the determined strike and direction (CE/PE).

5. **Trade Execution:**

   * Sell the identified CE/PE at 9:25 AM.
   * Square off the trade at 3:15 PM.

6. **Position Size:**

   * One lot per trade. (Typically 30 quantity for Bank Nifty)

7. **Logging & Reporting:**

   * Daily trade logs include:

     * Date, strike, direction (CE/PE)
     * Entry/exit time & prices
     * Lot size, per-unit P\&L, total P\&L
   * A **final summary** of cumulative performance metrics is printed.

---

### 📜 Sample Log Snapshot (from `ST_Option_Selling_20_50_20042025.log`):

* **Date:** 01-04-2022
* **Signal:** 9:25 LTP > 9:15 LTP → Sell PE
* **Strike Sold:** 36500 PE
* **Entry Price:** ₹983.80
* **Exit Price:** ₹665.15
* **Total P\&L:** ₹9559.50 (1 lot)

---

### 📊 Strategy Summary (Apr 2022 Backtest Results):

* **Total Days Traded:** 18
* **Win Days:** 13
* **Loss Days:** 5
* **Win Rate:** 72.22%
* **Cumulative P\&L:** ₹30,559.50
* **Most Profitable Day:** ₹9559.50 on 01-04-2022
* **Most Loss-Making Day:** ₹-7045.50 on 13-04-2022
* **Average Trade P\&L:** ₹1697.75
* **Profit Factor:** 2.52
* **Sharpe Ratio:** 0.38
* **Max Drawdown:** ₹13,359
* **Max Consecutive Wins:** 6
* **Max Consecutive Losses:** 2
* **Daily Volatility:** ₹4505.49

---

### 📝 Observations:

* The strategy is simple and reactive to early trend direction.
* Outlier losses (e.g., ₹-7045.50 on 13th April) indicate potential for risk management (e.g., SL or hedging).
* Profit factor > 2 and win rate > 70% suggest promising baseline performance.

---

### 🗂 File Structure:

```
banknifty-options-strategy/
│
├── logs/
│   └── ST_Option_Selling_20_50_20042025.log
│
├── data_utils.py
├── main.py
├── strategy.py
├── config.py
├── README.md   
```    
