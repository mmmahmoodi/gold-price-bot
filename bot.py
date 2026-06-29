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

# ثابت‌های محاسباتی
MESGHAL_GR = 4.608          # وزن یک مثقال به گرم
OUNCES_GR = 31.1035         # وزن یک انس تروا به گرم
ABSHODEH_PURITY = 705       # عیار استاندارد آبشده
PURE_GOLD_PURITY = 999.9    # عیار طلای خالص

# وزن طلای خالص سکه‌ها
COIN_GOLD_GR  = 8.133 * (22 / 24)
BAHAR_GOLD_GR = 8.133 * (22 / 24)
NIM_GOLD_GR   = 4.066 * (22 / 24)
ROB_GOLD_GR   = 2.033 * (22 / 24)
GRAMI_GOLD_GR = 1.0 * (22 / 24)

def fetch_with_retry(url, params=None, max_retries=3, delay=2):
    for attempt in range(max_retries):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=20)
            r.raise_for_status()
            return r
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {type(e).__name__}")
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                raise e
    return None

def fetch_all_prices():
    try:
        params = {"key": BRS_API_KEY}
        r = fetch_with_retry(BRS_API_URL, params=params)
        data = r.json()
        
        if not data.get("successful", True):
            return {}
        
        all_items = []
        all_items.extend(data.get("gold", []))
        all_items.extend(data.get("currency", []))
        all_items.extend(data.get("cryptocurrency", []))
        
        prices = {}
        for item in all_items:
            symbol = item.get("symbol")
            if symbol:
                prices[symbol] = item
        
        return prices
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

def fetch_silver_ounce():
    try:
        url = "https://api.metals.live/v1/spot/silver"
        r = requests.get(url, headers=HEADERS, timeout=15)
        data = r.json()
        if data and len(data) > 0:
            return data[0].get("price")
        return None
    except Exception as e:
        print(f"️ Silver error: {e}")
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

def calc_bubble_pct(market_price, intrinsic_value):
    try:
        m = to_float(market_price)
        i = to_float(intrinsic_value)
        if m and i and i > 0:
            return ((m - i) / i) * 100
        return None
    except:
        return None

def calc_abshodeh_intrinsic(ons_gold_price, dollar_price):
    try:
        ons = to_float(ons_gold_price)
        usd = to_float(dollar_price)
        if ons and usd:
            gold_24k_per_gram = (ons * usd) / OUNCES_GR
            intrinsic = gold_24k_per_gram * MESGHAL_GR * (ABSHODEH_PURITY / PURE_GOLD_PURITY)
            return intrinsic
        return None
    except:
        return None

def calc_coin_intrinsic(gold_24k_per_gram, weight_gr):
    try:
        g24 = to_float(gold_24k_per_gram)
        if g24 and weight_gr:
            return g24 * weight_gr
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
    
    intr_emami  = calc_coin_intrinsic(gold24, COIN_GOLD_GR)
    intr_bahar  = calc_coin_intrinsic(gold24, BAHAR_GOLD_GR)
    intr_nim    = calc_coin_intrinsic(gold24, NIM_GOLD_GR)
    intr_rob    = calc_coin_intrinsic(gold24, ROB_GOLD_GR)
    intr_grami  = calc_coin_intrinsic(gold24, GRAMI_GOLD_GR)
    intr_abshodeh = calc_abshodeh_intrinsic(ons_gold, dollar)
    
    hbab_emami    = calc_bubble_pct(emami, intr_emami)
    hbab_bahar    = calc_bubble_pct(bahar, intr_bahar)
    hbab_nim      = calc_bubble_pct(nim, intr_nim)
    hbab_rob      = calc_bubble_pct(rob, intr_rob)
    hbab_grami    = calc_bubble_pct(grami, intr_grami)
    hbab_abshodeh = calc_bubble_pct(abshodeh, intr_abshodeh)
    
    lines = [
        f"💵 تتر:   {fmt(tether)}",
        f"💰 دلار:   {fmt(dollar)} {fmt(chg_dollar, change=True)}",
        f"🔸 سکه امامی:   {fmt(emami)} {fmt(chg_emami, change=True)}",
        f"🔸 گرم طلای 18:   {fmt(gold18)} {fmt(chg_gold18, change=True)}",
        f"🔸 گرم طلای 24:   {fmt(gold24)}",
        f"🔸 آبشده (مثقال):   {fmt(abshodeh)}",
        f"🔸 سکه بهار آزادی:   {fmt(bahar)}",
        f"🔸 نیم سکه:   {fmt(nim)}",
        f" ربع سکه:   {fmt(rob)}",
        f"🔸 سکه گرمی:   {fmt(grami)}",
        f"🥇 انس طلا:   {fmt(ons_gold, decimal=True)}",
        f"🥈 انس نقره:   {fmt(silver_oz, decimal=True)}",
        "",
        f"🔹 حباب سکه امامی:   {fmt(hbab_emami, bubble=True)}",
        f"🔹 حباب سکه بهار آزادی:   {fmt(hbab_bahar, bubble=True)}",
        f"🔹 حباب نیم سکه:   {fmt(hbab_nim, bubble=True)}",
        f"🔹 حباب ربع سکه:   {fmt(hbab_rob, bubble=True)}",
        f"🔹 حباب سکه گرمی:   {fmt(hbab_grami, bubble=True)}",
        f"🔹 حباب آبشده:   {fmt(hbab_abshodeh, bubble=True)}",
        "",
        f"🔸 ارزش ذاتی یک مثقال آبشده:   {fmt(intr_abshodeh)}",
        f" ارزش سکه امامی بدون حباب:   {fmt(intr_emami)}",
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
