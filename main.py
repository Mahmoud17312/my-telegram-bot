import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# سيرفر وهمي لإبقاء الخطي المجانية على Render نشطة
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# كود البوت الأساسي
TOKEN = os.environ.get("8847445337:AAFayzATCl8C-4sexybj_wHD90rnkVHTxIs")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! البوت يعمل بنجاح 🚀")

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN is missing!")
        return

    # تشغيل سيرفر الويب في المسار الخلفي
    threading.Thread(target=run_health_check_server, daemon=True).start()

    # تشغيل البوت
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
