import requests
import jdatetime
import os
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = "@nerkh_tahlil"

TGJU_URL = "https://www.tgju.org/json/major_data"

ITEMS = {
    "price_dollar_rl":     ("دلار",              "💰"),
    "sekke-emami":         ("سکه امامی",          "🔸"),
    "geram-18":            ("گرم طلای 18",        "🔸"),
    "geram-24":            ("گرم طلای 24",        "🔸"),
    "gold-abshode":        ("آبشده",              "🔸"),
    "sekeb":               ("سکه بهار آزادی",     "🔸"),
    "nim-sekke":           ("نیم سکه",            "🔸"),
    "rob-sekke":           ("ربع سکه",            "🔸"),
    "sekke-gram-1":        ("سکه گرمی",           "🔸"),
    "gold":                ("انس طلا",            "🥇"),
    "silver":              ("انس نقره",           "🥈"),
    "hbab-sekke-emami":    ("حباب سکه امامی",     "🔹"),
    "hbab-sekeb":          ("حباب سکه بهار آزادی","🔹"),
    "hbab-nim-sekke":      ("حباب نیم سکه",       "🔹"),
    "hbab-rob-sekke":      ("حباب ربع سکه",       "🔹"),
    "hbab-sekke-gram-1":   ("حباب سکه گرمی",      "🔹"),
}

def fmt_price(val, key):
    try:
        v = float(str(val).replace(",", ""))
        if "hbab" in key:
            return f"{v:+.2f}%"
        if key in ("gold", "silver"):
            return f"{v:,.2f}"
        return f"{int(v):,}"
    except:
        return str(val)

def get_prices():
    r = requests.get(TGJU_URL, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    data = r.json()
    return data

def build_message(data):
    now_ir = jdatetime.datetime.now(tz=jdatetime.datetime.now().tzinfo or None)
    now_ir = jdatetime.datetime.fromgregorian(datetime=datetime.now(timezone(timedelta(hours=3, minutes=30))))
    date_str = now_ir.strftime("%A %d/%m/%Y - %H:%M")

    lines = []
    for key, (label, icon) in ITEMS.items():
        try:
            val = data[key]["p"]
            lines.append(f"{icon} {label}:   {fmt_price(val, key)}")
        except:
            lines.append(f"  {label}:   ---")

    lines.append("")
    lines.append(date_str)
    return "\n".join(lines)

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHANNEL_ID, "text": text})
    print("Status:", r.status_code)

def main():
    print("Fetching prices...")
    data = get_prices()
    msg = build_message(data)
    print(msg)
    send_to_telegram(msg)
    print("Done.")

if __name__ == "__main__":
    main()
