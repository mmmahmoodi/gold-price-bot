import requests
import os
import jdatetime
import time
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = "@nerkh_tahlil"
CHANNEL_URL = "https://t.me/nerkh_tahlil"

BRS_API_KEY = os.environ.get("BRS_API_KEY")
BRS_API_URL = "https://Api.BrsApi.ir/Market/Gold_Currency.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

DAYS_FA = {
    "Saturday": "شنبه", "Sunday": "یکشنبه", "Monday": "دوشنبه",
    "Tuesday": "سه‌شنبه", "Wednesday": "چهارشنبه", "Thursday": "پنجشنبه", "Friday": "جمعه"
}

SYMBOLS = {
    "dollar": "USD",
    "tether": "USDT_IRT",
    "emami": "IR_COIN_EMAMI",
    "bahar": "IR_COIN_BAHAR",
    "nim": "IR_COIN_HALF",
    "rob": "IR_COIN_QUARTER",
    "grami": "IR_COIN_1G",
    "gold18": "IR_GOLD_18K",
    "gold24": "IR_GOLD_24K",
    "abshodeh": "IR_GOLD_MELTED",
    "ons_gold": "XAUUSD"
}

def fetch_with_retry(url, params=None, max_retries=3, delay=2):
    """درخواست با مکانیزم retry"""
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1}/{max_retries}...")
            r = requests.get(url, params=params, headers=HEADERS, timeout=20)
            r.raise_for_status()
            return r
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {type(e).__name__}")
            if attempt < max_retries - 1:
                print(f"⏳ Waiting {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # افزایش زمان انتظار
            else:
                raise e
    return None

def fetch_all_prices():
    try:
        print(f"🔑 API Key exists: {bool(BRS_API_KEY)}")
        print(f"📡 Connecting to BrsApi...")
        
        params = {"key": BRS_API_KEY}
        r = fetch_with_retry(BRS_API_URL, params=params)
        
        print(f"📊 Status Code: {r.status_code}")
        
        data = r.json()
        
        if not data.get("successful", True):
            print(f"❌ API Error: {data.get('message_error', 'Unknown')}")
            return {}
        
        all_items = []
        all_items.extend(data.get("gold", []))
        all_items.extend(data.get("currency", []))
        all_items.extend(data.get("cryptocurrency", []))
        
        print(f"✅ Received {len(all_items)} items")
        
        prices = {}
        for item in all_items:
            symbol = item.get("symbol")
            if symbol:
                prices[symbol] = item
        
        return prices
    
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return {}

def fetch_silver_ounce():
    """دریافت انس نقره از TGJU"""
    try:
        url = "https://api.tgju.org/v1/market/indicator/summary-table-data/silver"
        r = requests.get(url, headers=HEADERS, timeout=15)
        data = r.json()
        return data["data"][0][1]
    except Exception as e:
        print(f"⚠️ Silver fetch error: {e}")
        return None

def get_price(prices, key):
    symbol = SYMBOLS.get(key)
    if not symbol or symbol not in prices:
        return None
    return prices[symbol].get("price")

def get_change(prices, key):
    symbol = SYMBOLS.get(key)
    if not symbol or symbol not in prices:
        return None
    return prices[symbol].get("change_percent")

def to_float(val):
    try:
        return float(str(val).replace(",", ""))
    except:
        return None

def fmt(val, bubble=False, decimal=False, change=False):
    if val is None:
        return "---"
    try:
        v = float(str(val).replace(",", ""))
        if bubble or change:
            return f"{v:+.2f}%"
        if decimal:
            return f"{v:,.2f}"
        return f"{int(v):,}"
    except:
        return str(val)

def fa_date():
    now = datetime.now(timezone(timedelta(hours=3, minutes=30)))
    jdt = jdatetime.datetime.fromgregorian(datetime=now)
    day_fa = DAYS_FA.get(now.strftime("%A"), "")
    return f"{day_fa} {jdt.strftime('%d/%m/%Y')} - {jdt.strftime('%H:%M')}"

def calc_bubble_pct(coin_price, intrinsic):
    try:
        c = to_float(coin_price)
        i = to_float(intrinsic)
        if c and i and i > 0:
            return ((c - i) / i) * 100
        return None
    except:
        return None

def build_message():
    prices = fetch_all_prices()
    silver_oz = fetch_silver_ounce()
    
    if not prices:
        return "❌ خطا در دریافت اطلاعات از سرور."
    
    tether     = get_price(prices, "tether")
    dollar     = get_price(prices, "dollar")
    emami      = get_price(prices, "emami")
    gold18     = get_price(prices, "gold18")
    gold24     = get_price(prices, "gold24")
    abshodeh   = get_price(prices, "abshodeh")
    bahar      = get_price(prices, "bahar")
    nim        = get_price(prices, "nim")
    rob        = get_price(prices, "rob")
    grami      = get_price(prices, "grami")
    ons_gold   = get_price(prices, "ons_gold")
    
    chg_dollar = get_change(prices, "dollar")
    chg_emami  = get_change(prices, "emami")
    chg_gold18 = get_change(prices, "gold18")
    
    COIN_GOLD_GR  = 8.133 * (22 / 24)
    BAHAR_GOLD_GR = 8.133 * (22 / 24)
    NIM_GOLD_GR   = 4.066 * (22 / 24)
    ROB_GOLD_GR   = 2.033 * (22 / 24)
    GRAMI_GOLD_GR = 1.0 * (22 / 24)

    g24 = to_float(gold24)

    def intr(weight_gr):
        if g24 and weight_gr:
            return g24 * weight_gr
        return None

    intr_emami  = intr(COIN_GOLD_GR)
    intr_bahar  = intr(BAHAR_GOLD_GR)
    intr_nim    = intr(NIM_GOLD_GR)
    intr_rob    = intr(ROB_GOLD_GR)
    intr_grami  = intr(GRAMI_GOLD_GR)

    hbab_emami  = calc_bubble_pct(emami, intr_emami)
    hbab_bahar  = calc_bubble_pct(bahar, intr_bahar)
    hbab_nim    = calc_bubble_pct(nim, intr_nim)
    hbab_rob    = calc_bubble_pct(rob, intr_rob)
    hbab_grami  = calc_bubble_pct(grami, intr_grami)

    lines = [
        f"💵 تتر:   {fmt(tether)}",
        f"💰 دلار:   {fmt(dollar)} {fmt(chg_dollar, change=True)}",
        f"🔸 سکه امامی:   {fmt(emami)} {fmt(chg_emami, change=True)}",
        f"🔸 گرم طلای 18:   {fmt(gold18)} {fmt(chg_gold18, change=True)}",
        f"🔸 گرم طلای 24:   {fmt(gold24)}",
        f"🔸 آبشده:   {fmt(abshodeh)}",
        f"🔸 سکه بهار آزادی:   {fmt(bahar)}",
        f"🔸 نیم سکه:   {fmt(nim)}",
        f"🔸 ربع سکه:   {fmt(rob)}",
        f"🔸 سکه گرمی:   {fmt(grami)}",
        f"🥇 انس طلا:   {fmt(ons_gold, decimal=True)}",
        f"🥈 انس نقره:   {fmt(silver_oz, decimal=True)}",
        "",
        f"🔹 حباب سکه امامی:   {fmt(hbab_emami, bubble=True)}",
        f"🔹 حباب سکه بهار آزادی:   {fmt(hbab_bahar, bubble=True)}",
        f"🔹 حباب نیم سکه:   {fmt(hbab_nim, bubble=True)}",
        f"🔹 حباب ربع سکه:   {fmt(hbab_rob, bubble=True)}",
        f"🔹 حباب سکه گرمی:   {fmt(hbab_grami, bubble=True)}",
        "",
        f"🔸 ارزش آبشده بدون حباب:   {fmt(abshodeh)}",
        f"🔸 ارزش سکه امامی بدون حباب:   {fmt(intr_emami)}",
        f"🔸 ارزش سکه بهار آزادی بدون حباب:   {fmt(intr_bahar)}",
        "",
        fa_date(),
        "",
        CHANNEL_URL
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
