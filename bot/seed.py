"""
سكربت لتعبئة قاعدة البيانات بفئات ومنتجات (ChatGPT, Claude, Gemini, خدمات أمنية).
شغّله مرة واحدة بالأمر: python -m bot.seed
"""
import asyncio
import aiosqlite
from bot.config import settings
from bot.database import init_db


async def seed():
    await init_db()
    async with aiosqlite.connect(settings.db_path) as db:
        
        # 1. فئة ChatGPT
        cur = await db.execute(
            "INSERT INTO categories (name, emoji) VALUES (?, ?)",
            ("ChatGPT", "🟢"),
        )
        cat_chatgpt = cur.lastrowid

        # 2. فئة Claude
        cur = await db.execute(
            "INSERT INTO categories (name, emoji) VALUES (?, ?)",
            ("Claude", "🟠"),
        )
        cat_claude = cur.lastrowid

        # 3. فئة Gemini
        cur = await db.execute(
            "INSERT INTO categories (name, emoji) VALUES (?, ?)",
            ("Gemini", "🔵"),
        )
        cat_gemini = cur.lastrowid

        # 4. فئة خدمات أمن المعلومات (واحدة فقط)
        cur = await db.execute(
            "INSERT INTO categories (name, emoji) VALUES (?, ?)",
            ("خدمات أمن المعلومات", "🛡"),
        )
        cat_security = cur.lastrowid

        # قائمة المنتجات والخدمات
        products = [
            # --- منتجات ChatGPT ---
            (
                cat_chatgpt,
                "حساب ChatGPT Plus (شهر)",
                "اشتراك شهري في خادم رسمي مفعل بالكامل مع الوصول لـ GPT-4o.",
                20.0,
                10,
                "text",
                "الإيميل: chatgpt_user1@example.com | كلمة السر: Pass123456",
            ),
            # --- منتجات Claude ---
            (
                cat_claude,
                "حساب Claude Pro (شهر)",
                "وصول كامل لنموذج Claude 3.5 Sonnet مع حدود استخدام أعلى.",
                20.0,
                5,
                "text",
                "الإيميل: claude_user1@example.com | كلمة السر: Pass123456",
            ),
            # --- منتجات Gemini ---
            (
                cat_gemini,
                "اشتراك Gemini Advanced (شهر)",
                "وصول لنموذج Ultra مع مساحة 2TB على Google One.",
                19.0,
                8,
                "text",
                "الإيميل: gemini_user1@example.com | كلمة السر: Pass123456",
            ),
            # --- خدمات أمن المعلومات ---
            (
                cat_security,
                "استشارة أمنية - 30 دقيقة",
                "جلسة استشارة عبر مكالمة صوتية أو نصية لمناقشة وضعك الأمني.",
                15.0,
                50,
                "text",
                "سيتم التواصل معك من قبل الدعم لتحديد الموعد خلال 24 ساعة.",
            ),
            (
                cat_security,
                "تقرير Pentest أساسي",
                "فحص أساسي لموقع أو تطبيق واحد وتقرير مكتوب بالثغرات المكتشفة.",
                80.0,
                20,
                "text",
                "أرسل رابط الهدف بعد إتمام الشراء عبر زر المساعدة.",
            ),
        ]

        for p in products:
            await db.execute(
                """INSERT INTO products
                   (category_id, name, description, price, stock, delivery_type, delivery_content, active)
                   VALUES (?,?,?,?,?,?,?,1)""",
                p,
            )
        await db.commit()
    print("تم إدخال البيانات والتصنيفات بنجاح ✅")


if __name__ == "__main__":
    asyncio.run(seed())
