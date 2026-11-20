import csv
import os
from datetime import datetime

# Built-in fallback prices (used if sp500_tickers.csv is not found or ticker isn't listed)
FALLBACK_PRICES = {
    "AAPL": ("Apple Inc.", 228.50),
    "MSFT": ("Microsoft Corp.", 425.00),
    "GOOGL": ("Alphabet Inc.", 176.80),
    "AMZN": ("Amazon.com Inc.", 205.40),
    "TSLA": ("Tesla Inc.", 310.20),
    "NVDA": ("NVIDIA Corp.", 142.60),
    "META": ("Meta Platforms", 585.00),
    "NFLX": ("Netflix Inc.", 790.50),
    "TCS": ("Tata Consultancy Services", 4120.00),
    "INFY": ("Infosys Ltd.", 1865.00)
}

def load_market_prices(csv_filename="sp500_tickers.csv"):
    """Loads ticker symbols, company names, and current prices from CSV if available."""
    market_data = dict(FALLBACK_PRICES)
    if not os.path.exists(csv_filename):
        return market_data

    try:
        with open(csv_filename, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Normalize column headers to handle different CSV formats cleanly
                norm_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
                symbol = (
                    norm_row.get("symbol")
                    or norm_row.get("ticker")
                    or norm_row.get("stock")
                )
                name = (
                    norm_row.get("name")
                    or norm_row.get("company")
                    or norm_row.get("security")
                    or symbol
                )
                price_str = (
                    norm_row.get("price")
                    or norm_row.get("current_price")
                    or norm_row.get("close")
                    or norm_row.get("last")
                )
                if symbol and price_str:
                    try:
                        price = float(price_str.replace("$", "").replace(",", ""))
                        market_data[symbol.upper()] = (name, price)
                    except ValueError:
                        continue
    except Exception as e:
        print(f"Warning: Could not parse '{csv_filename}' ({e}). Using built-in prices.")

    return market_data

def collect_holdings(market_data):
    """Collects stock holdings from the user interactively."""
    holdings = {}
    sample_tickers = ", ".join(list(market_data.keys())[:8])

    print("=" * 65)
    print("           STOCK PORTFOLIO PERFORMANCE TRACKER")
    print("=" * 65)
    print(f"Sample Available Tickers: {sample_tickers}")
    print("Type 'DONE' when you finish adding stocks.\n")

    while True:
        ticker = input("Enter Stock Ticker Symbol (or 'DONE' to calculate): ").strip().upper()
        if ticker == "DONE":
            if not holdings:
                print("Please add at least one stock before finishing.\n")
                continue
            break

        if not ticker.isalpha():
            print("Invalid ticker symbol. Please enter letters only (e.g., AAPL).\n")
            continue

        # Check if ticker exists in dataset; otherwise allow manual current price entry
        if ticker in market_data:
            company_name, current_price = market_data[ticker]
            print(f"Found: {company_name} | Current Market Price: ${current_price:.2f}")
        else:
            print(f"Ticker '{ticker}' not found in dataset.")
            company_name = ticker
            while True:
                try:
                    current_price = float(input(f"Enter current market price for {ticker}: $").strip())
                    if current_price <= 0:
                        raise ValueError
                    break
                except ValueError:
                    print("Please enter a valid positive number.")

        # Get buy price
        while True:
            try:
                buy_price = float(input(f"Enter your Buy Price per share for {ticker}: $").strip())
                if buy_price <= 0:
                    raise ValueError
                break
            except ValueError:
                print("Please enter a valid positive number.")

        # Get quantity
        while True:
            try:
                quantity = float(input(f"Enter Share Quantity for {ticker}: ").strip())
                if quantity <= 0:
                    raise ValueError
                break
            except ValueError:
                print("Please enter a valid positive quantity.")

        # Merge if user enters the same ticker twice
        if ticker in holdings:
            old_qty = holdings[ticker]["quantity"]
            old_cost = holdings[ticker]["buy_price"] * old_qty
            new_qty = old_qty + quantity
            avg_buy_price = (old_cost + (buy_price * quantity)) / new_qty
            holdings[ticker]["quantity"] = new_qty
            holdings[ticker]["buy_price"] = avg_buy_price
        else:
            holdings[ticker] = {
                "company": company_name,
                "buy_price": buy_price,
                "current_price": current_price,
                "quantity": quantity
            }

        print(f"Added {quantity:g} shares of {ticker}!\n")

    return holdings

def generate_report_and_csv(holdings, output_file="portfolio_summary.csv"):
    """Computes portfolio metrics, prints a formatted table, and logs to CSV."""
    total_invested = 0.0
    total_current = 0.0
    rows_for_csv = []

    print("\n" + "=" * 88)
    print(f"{'TICKER':<8} {'QTY':>8} {'BUY ($)':>11} {'CURR ($)':>11} {'INVESTED ($)':>14} {'VALUE ($)':>14} {'GAIN/LOSS':>14}")
    print("-" * 88)

    for ticker, data in holdings.items():
        qty = data["quantity"]
        buy_p = data["buy_price"]
        curr_p = data["current_price"]

        invested = qty * buy_p
        current_val = qty * curr_p
        pnl = current_val - invested
        pnl_pct = (pnl / invested) * 100

        total_invested += invested
        total_current += current_val

        sign = "+" if pnl >= 0 else ""
        pnl_display = f"{sign}{pnl:,.2f} ({sign}{pnl_pct:.1f}%)"

        print(
            f"{ticker:<8} {qty:>8g} {buy_p:>11,.2f} {curr_p:>11,.2f} "
            f"{invested:>14,.2f} {current_val:>14,.2f} {pnl_display:>14}"
        )

        rows_for_csv.append({
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Ticker": ticker,
            "Company": data["company"],
            "Quantity": qty,
            "Buy_Price": round(buy_p, 2),
            "Current_Price": round(curr_p, 2),
            "Total_Invested": round(invested, 2),
            "Current_Value": round(current_val, 2),
            "Gain_Loss_Amount": round(pnl, 2),
            "Gain_Loss_Percent": round(pnl_pct, 2)
        })

    total_pnl = total_current - total_invested
    total_pnl_pct = (total_pnl / total_invested) * 100 if total_invested else 0.0
    tot_sign = "+" if total_pnl >= 0 else ""

    print("-" * 88)
    print(f"Total Invested Capital : ${total_invested:,.2f}")
    print(f"Current Portfolio Value: ${total_current:,.2f}")
    print(f"Overall Net Gain/Loss  : {tot_sign}${total_pnl:,.2f} ({tot_sign}{total_pnl_pct:.2f}%)")
    print("=" * 88)

    # Save summary to CSV
    fieldnames = [
        "Timestamp", "Ticker", "Company", "Quantity", "Buy_Price",
        "Current_Price", "Total_Invested", "Current_Value",
        "Gain_Loss_Amount", "Gain_Loss_Percent"
    ]
    with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_for_csv)

    print(f"\nReport successfully saved to '{output_file}'!")

def main():
    market_data = load_market_prices()
    holdings = collect_holdings(market_data)
    generate_report_and_csv(holdings)

if __name__ == "__main__":
    main()