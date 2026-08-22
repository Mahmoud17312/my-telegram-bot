"""
سكربت لتعبئة قاعدة البيانات بفئة Gemini فقط بشعار النجمة الرباعية.
"""
import asyncio
import aiosqlite
from bot.config import settings
from bot.database import init_db


async def seed():
    await init_db()
    async with aiosqlite.connect(settings.db_path) as db:
        # مسح التصنيفات والمنتجات القديمة
        await db.execute("DELETE FROM products")
        await db.execute("DELETE FROM categories")

        # استخدام الرمز الرباعي ✦ المطابق لشكل الشعار
        cur = await db.execute(
            "INSERT INTO categories (name, emoji) VALUES (?, ?)",
            ("Gemini", "✦"),
        )
        cat_gemini = cur.lastrowid

        products = [
            (
                cat_gemini,
                "اشتراك Gemini Advanced (شهر)",
                "وصول لنموذج Ultra مع مساحة 2TB على Google One.",
                19.0,
                8,
                "text",
                "الإيميل: gemini_user1@example.com | كلمة السر: Pass123456",
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
    print("تم تحديث البيانات وإضافة Gemini بنجاح ✦")


if __name__ == "__main__":
    asyncio.run(seed())
