import requests
import os
import jdatetime
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = "@nerkh_tahlil"

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
    day_en = now.strftime("%A")
    day_fa = DAYS_FA.get(day_en, day_en)
    return f"{day_fa} {jdt.strftime('%d/%m/%Y')} - {jdt.strftime('%H:%M')}"

def build_message():
    dollar    = fetch("price_dollar_rl")
    emami     = fetch("sekee")
    gold18    = fetch("geram-18")
    gold24    = fetch("geram-24")
    abshodeh  = fetch("gold-abshode")
    bahar     = fetch("sekeb")
    nim       = fetch("nim-sekke")
    rob       = fetch("rob-sekke")
    grami     = fetch("sekke-gram-1")
    ons_gold  = fetch("ons")
    ons_silver= fetch("silver")

    hbab_emami = fetch("hbab-sekke-emami")
    hbab_bahar = fetch("hbab-sekeb")
    hbab_nim   = fetch("hbab-nim-sekke")
    hbab_rob   = fetch("hbab-rob-sekke")
    hbab_grami = fetch("hbab-sekke-gram-1")

    intrinsic_emami = None
    intrinsic_bahar = None
    if abshodeh and hbab_emami:
        try:
            ab = float(str(abshodeh).replace(",", ""))
            hb = float(str(hbab_emami).replace(",", "")) / 100
            em = float(str(emami).replace(",", "")) if emami else None
            if em:
                intrinsic_emami = em / (1 + hb)
        except:
            pass
    if abshodeh and hbab_bahar:
        try:
            ab = float(str(abshodeh).replace(",", ""))
            hb = float(str(hbab_bahar).replace(",", "")) / 100
            bh = float(str(bahar).replace(",", "")) if bahar else None
            if bh:
                intrinsic_bahar = bh / (1 + hb)
        except:
            pass

    abshodeh_intrinsic = None
    if abshodeh and hbab_emami:
        try:
            ab = float(str(abshodeh).replace(",", ""))
            hb = float(str(hbab_emami).replace(",", "")) / 100
            abshodeh_intrinsic = ab
        except:
            pass

    lines = [
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
        f"🔸 ارزش آبشده بدون حباب:   {fmt(abshodeh)}",
        f"🔸 ارزش سکه امامی بدون حباب:   {fmt(intrinsic_emami)}",
        f"🔸 ارزش سکه بهار آزادی بدون حباب:   {fmt(intrinsic_bahar)}",
        "",
        fa_date()
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
