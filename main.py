import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 1. سيرفر وهمي لإبقاء Render نشطاً
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# 2. التوكن والروابط (ضع اليوزر الخاص بك والقناة بدون @)
TOKEN = "8847445337:AAFayzATCl8C-4sexybj_wHD90rnkVHTxIs"
MY_TELEGRAM_USERNAME = "@CyberMsec"  # يوزر حسابك الشخصي
MY_CHANNEL_USERNAME = "CYPERMRED"  # يوزر قناتك هنا بدون @

# 3. أمر /start لإظهار الأزرار
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🛠️ خدمة التصميم", callback_data="service_design"),
            InlineKeyboardButton("💻 خدمة البرمجة", callback_data="service_coding"),
        ],
        [
            InlineKeyboardButton("📢 قناتنا على تليجرام", url=f"t.me/{MY_CHANNEL_USERNAME}")
        ],
        [
            InlineKeyboardButton("📩 للتواصل المباشر", url=f"t.me/{MY_TELEGRAM_USERNAME}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "أهلاً بك في بوت الخدمات! 🚀\nاختر الخدمة التي تريدها أو تصفح قناتنا وللتواصل المباشر:",
        reply_markup=reply_markup
    )

# 4. معالجة الضغط على أزرار الخدمات
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "service_design":
        await query.message.reply_text("🎨 **خدمة التصميم:** نتشرف بتقديم أفضل التصاميم الاحترافية لعلامتك التجارية.")
    elif query.data == "service_coding":
        await query.message.reply_text("💻 **خدمة البرمجة:** نقوم بتطوير البوتات والمواقع بأعلى جودة.")

# 5. تشغيل التطبيق
async def main():
    threading.Thread(target=run_health_check_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    
    # إضافة الأوامر والمُعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))

    print("Bot is running with buttons...")
    
    async with app:
        await app.start()
        await app.updater.start_polling()
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
