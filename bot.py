import requests
import os
import jdatetime
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = "@nerkh_tahlil"
CHANNEL_URL = "https://t.me/nerkh_tahlil"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BASE = "https://api.tgju.org/v1/market/indicator/summary-table-data/"

DAYS_FA = {
    "Saturday": "شنبه", "Sunday": "یکشنبه", "Monday": "دوشنبه",
    "Tuesday": "سه‌شنبه", "Wednesday": "چهارشنبه", "Thursday": "پنجشنبه", "Friday": "جمعه"
}

def fetch(symbol):
    try:
        r = requests.get(BASE + symbol, headers=HEADERS, timeout=10)
        data = r.json()
        return data["data"][0][1]
    except:
        return None

def to_float(val):
    try:
        return float(str(val).replace(",", ""))
    except:
        return None

def fmt(val, bubble=False, decimal=False):
    if val is None:
        return "---"
    try:
        v = float(str(val).replace(",", ""))
        if bubble:
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
    dollar     = fetch("price_dollar_rl")
    tether     = fetch("crypto-tether")
    emami      = fetch("sekee")
    gold18     = fetch("geram18")
    gold24     = fetch("geram24")
    abshodeh   = fetch("gold_melted_transfer")
    bahar      = fetch("sekeb")
    nim        = fetch("nim")
    rob        = fetch("rob")
    grami      = fetch("gerami")
    ons_gold   = fetch("ons")
    ons_silver = fetch("silver")

    # محاسبه ارزش ذاتی (بدون حباب) بر اساس وزن طلای هر سکه
    # سکه امامی: 8.133 گرم طلای 22 عیار = 8.133 * (22/24) گرم طلای 24
    COIN_GOLD_GR = 8.133 * (22 / 24)
    BAHAR_GOLD_GR = 8.133 * (22 / 24)
    NIM_GOLD_GR = 4.066 * (22 / 24)
    ROB_GOLD_GR = 2.033 * (22 / 24)
    GRAMI_GOLD_GR = 1.0 * (22 / 24)
    ABSHODEH_GOLD_GR = 1.0

    g24 = to_float(gold24)
    ab  = to_float(abshodeh)

    def intrinsic_from_gold24(weight_gr):
        if g24 and weight_gr:
            return g24 * weight_gr
        return None

    def intrinsic_abshodeh(weight_gr):
        if ab and weight_gr:
            return ab * weight_gr
        return None

    intr_emami  = intrinsic_from_gold24(COIN_GOLD_GR)
    intr_bahar  = intrinsic_from_gold24(BAHAR_GOLD_GR)
    intr_nim    = intrinsic_from_gold24(NIM_GOLD_GR)
    intr_rob    = intrinsic_from_gold24(ROB_GOLD_GR)
    intr_grami  = intrinsic_from_gold24(GRAMI_GOLD_GR)
    intr_abshodeh = abshodeh

    hbab_emami  = calc_bubble_pct(emami, intr_emami)
    hbab_bahar  = calc_bubble_pct(bahar, intr_bahar)
    hbab_nim    = calc_bubble_pct(nim, intr_nim)
    hbab_rob    = calc_bubble_pct(rob, intr_rob)
    hbab_grami  = calc_bubble_pct(grami, intr_grami)

    lines = [
        f"💵 تتر:   {fmt(tether)}",
        f"💰 دلار:   {fmt(dollar)}",
        f"🔸 سکه امامی:   {fmt(emami)}",
        f"🔸 گرم طلای 18:   {fmt(gold18)}",
        f"🔸 گرم طلای 24:   {fmt(gold24)}",
        f"🔸 آبشده:   {fmt(abshodeh)}",
        f"🔸 سکه بهار آزادی:   {fmt(bahar)}",
        f"🔸 نیم سکه:   {fmt(nim)}",
        f"🔸 ربع سکه:   {fmt(rob)}",
        f"🔸 سکه گرمی:   {fmt(grami)}",
        f"🥇 انس طلا:   {fmt(ons_gold, decimal=True)}",
        f"🥈 انس نقره:   {fmt(ons_silver, decimal=True)}",
        "",
        f"🔹 حباب سکه امامی:   {fmt(hbab_emami, bubble=True)}",
        f"🔹 حباب سکه بهار آزادی:   {fmt(hbab_bahar, bubble=True)}",
        f"🔹 حباب نیم سکه:   {fmt(hbab_nim, bubble=True)}",
        f"🔹 حباب ربع سکه:   {fmt(hbab_rob, bubble=True)}",
        f"🔹 حباب سکه گرمی:   {fmt(hbab_grami, bubble=True)}",
        "",
        f"🔸 ارزش آبشده بدون حباب:   {fmt(intr_abshodeh)}",
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
