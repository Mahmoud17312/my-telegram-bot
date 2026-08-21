"""
سكربت لتعبئة قاعدة البيانات بفئات ومنتجات تجريبية (placeholder).
بدّل هالبيانات بمنتجاتك/خدماتك الحقيقية قبل التشغيل الفعلي.
شغّله مرة وحدة بالأمر: python -m bot.seed
"""
import asyncio
import aiosqlite
from bot.config import settings
from bot.database import init_db


async def seed():
    await init_db()
    async with aiosqlite.connect(settings.db_path) as db:
        # فئة تجريبية
        cur = await db.execute(
            "INSERT INTO categories (name, emoji) VALUES (?, ?)",
            ("خدمات أمن المعلومات", "🛡"),
        )
        cat_id = cur.lastrowid

        # منتجات تجريبية -- بدّلها بمنتجاتك الحقيقية
        products = [
            (
                cat_id,
                "استشارة أمنية - 30 دقيقة",
                "جلسة استشارة عبر مكالمة صوتية أو نصية لمناقشة وضعك الأمني.",
                15.0,
                50,
                "text",
                "سيتم التواصل معك من قبل الدعم لتحديد الموعد خلال 24 ساعة.",
            ),
            (
                cat_id,
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
    print("تم إدخال البيانات التجريبية بنجاح ✅")


if __name__ == "__main__":
    asyncio.run(seed())
