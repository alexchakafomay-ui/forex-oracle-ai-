import requests
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def format_signal(s):
    return f"""
━━━━━━━━━━━━━━━
🚀 <b>FOREX ORACLE AI — SIGNAL</b> 🚀
━━━━━━━━━━━━━━━

💱 <b>Pair:</b> {s['pair']}
📊 <b>Arah:</b> {'🟢 BUY' if s['direction']=='BUY' else '🔴 SELL'}
⭐ <b>Confidence:</b> {s['confidence']}%
⏱ <b>TF Entry:</b> {s['tf']} | 🕐 {s['time_wib']} WIB
⚡ <b>Mode:</b> {s['mode']}

🎯 <b>ENTRY:</b> {s['entry']}
🛑 <b>SL:</b> {s['sl']} ({s['sl_pips']} pips)
✅ <b>TP1:</b> {s['tp1']} ({s['tp1_pips']} pips)
✅ <b>TP2:</b> {s['tp2']} ({s['tp2_pips']} pips)
🔥 <b>TP3:</b> {s['tp3']} ({s['tp3_pips']} pips)
💰 <b>Risk:</b> {s['risk_pct']}% akun

📈 <b>TEKNIKAL:</b>
{chr(10).join('• ' + r for r in s['reasons'][:4])}

🧠 <b>SMART MONEY:</b>
• Order Block: {'✅' if s['smc_bullish_ob'] else '❌'}
• BOS/CHoCH: {'✅' if s['smc_bos_bull'] else '❌'}

📰 <b>BERITA:</b>
• Sentimen: {s['news_label']}
• High-impact 2 jam: {s['next_news']}

🎲 <b>PROBABILITAS CANDLE:</b>
🟢 Bullish: {s['p_bull']}% | 🔴 Bearish: {s['p_bear']}% | ⚪ Sideway: {s['p_side']}%

🌍 <b>REGIME:</b> {s['regime']} | ⚠️ <b>Risiko:</b> {s['risk_level']}
💡 <i>{s['note']}</i>

━━━━━━━━━━━━━━━
🤖 Forex Oracle AI v1.0 — Zero Spread Edition
📌 Bukan nasihat keuangan. Kelola risiko Anda.
━━━━━━━━━━━━━━━
"""

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()
