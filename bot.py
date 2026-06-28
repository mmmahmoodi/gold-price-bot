import requests
import os
import jdatetime
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = "@nerkh_tahlil"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

SYMBOLS = [
    ("price_dollar_rl",  "dollar"),
    ("sekke-emami",      "emami"),
    ("geram-18",         "gold18"),
    ("geram-24",         "gold24"),
    ("gold-abshode",     "abshodeh"),
    ("sekeb",            "bahar"),
    ("nim-sekke",        "nim"),
    ("rob-sekke",        "rob"),
    ("sekke-gram-1",     "grami"),
    ("ons",              "ons_gold"),
    ("silver",           "silver"),
    ("hbab-sekke-emami", "hbab_emami"),
    ("hbab-sekeb",       "hbab_bahar"),
    ("hbab-nim-sekke",   "hbab_nim"),
    ("hbab-rob-sekke",   "hbab_rob"),
    ("hbab-sekke-gram-1","hbab_grami"),
]

def fetch_price(symbol):
    try:
        url = f"https://api.tgju.org/v1/market/indicator/summary-table-data/{symbol}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        return data["data"][0][1]
    except:
        return None

def fmt(val, is_bubble=False, is_ons=False):
    if val is None:
        return "---"
    try:
        v = float(str(val).replace(",", ""))
        if is_bubble:
            return f"{v:+.2f}%"
        if is_ons:
            return f"{v:,.2f}"
        return f"{int(v):,}"
    except:
        return str(val)

def calc_bubble(coin_price, abshodeh_price, weight_gr):
    try:
        intrinsic = float(str(abshodeh_price).replace(",", "")) * weight_gr
        coin = float(str(coin_price).replace(",", ""))
        return ((coin - intrinsic) / intrinsic) * 100
    except:
        return None

def build_message():
    prices = {}
    for symbol, key in SYMBOLS:
        prices[key] = fetch_price(symbol)

    now_ir = jdatetime.datetime.fromgregorian(
        datetime=datetime.now(timezone(timedelta(hours=3, minutes=30)))
    )
    date_str = now_ir.strftime("%A %d/%m/%Y - %H:%M")

    abshodeh = prices.get("abshodeh")

    intrinsic_emami = None
    intrinsic_bahar = None
    if abshodeh:
        try:
            ab = float(str(abshodeh).replace(",", ""))
            intrinsic_emami = ab * 8.133
            intrinsic_bahar = ab * 8.133
        except:
            pass

    lines = [
        f"💰 دلار:   {fmt(prices['dollar'])}",
        f"🔸 سکه امامی:   {fmt(prices['emami'])}",
        f"🔸 گرم طلای 18:   {fmt(prices['gold18'])}",
        f"🔸 گرم طلای 24:   {fmt(prices['gold24'])}",
        f"🔸 آبشده:   {fmt(prices['abshodeh'])}",
        f"🔸 سکه بهار آزادی:   {fmt(prices['bahar'])}",
        f"🔸 نیم سکه:   {fmt(prices['nim'])}",
        f"🔸 ربع سکه:   {fmt(prices['rob'])}",
        f"🔸 سکه گرمی:   {fmt(prices['grami'])}",
        f"🥇 انس طلا:   {fmt(prices['ons_gold'], is_ons=True)}",
        f"🥈 انس نقره:   {fmt(prices['silver'], is_ons=True)}",
        "",
        f"🔹 حباب سکه امامی:   {fmt(prices['hbab_emami'], is_bubble=True)}",
        f"🔹 حباب سکه بهار آزادی:   {fmt(prices['hbab_bahar'], is_bubble=True)}",
        f"🔹 حباب نیم سکه:   {fmt(prices['hbab_nim'], is_bubble=True)}",
        f"🔹 حباب ربع سکه:   {fmt(prices['hbab_rob'], is_bubble=True)}",
        f"🔹 حباب سکه گرمی:   {fmt(prices['hbab_grami'], is_bubble=True)}",
        "",
        f"🔸 ارزش سکه امامی بدون حباب:   {fmt(intrinsic_emami)}",
        f"🔸 ارزش سکه بهار آزادی بدون حباب:   {fmt(intrinsic_bahar)}",
        "",
        date_str
    ]
    return "\n".join(lines)

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHANNEL_ID, "text": text})
    print("Status:", r.status_code)

def main():
    print("Fetching prices...")
    msg = build_message()
    print(msg)
    send_to_telegram(msg)

if __name__ == "__main__":
    main()
