import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    # ضع التوكن تبع بوتك (من BotFather) بملف .env تحت اسم BOT_TOKEN
    bot_token: str = os.getenv("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")

    # آيدي حسابك على تيليجرام (رقمي) عشان يوصلك إشعار الطلبات الجديدة
    admin_ids: list[int] = field(
        default_factory=lambda: [
            int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
        ]
    )

    db_path: str = os.getenv("DB_PATH", "shop.db")

    # عناوين المحافظ - بدّلها بعناوينك الحقيقية قبل التشغيل الفعلي
    wallets: dict = field(
        default_factory=lambda: {
            "BEP20": os.getenv("WALLET_BEP20", "0xYourBEP20AddressHere"),
            "TRC20": os.getenv("WALLET_TRC20", "TYourTRC20AddressHere"),
            "POLYGON": os.getenv("WALLET_POLYGON", "0xYourPolygonAddressHere"),
        }
    )

    currency_symbol: str = "USD"


settings = Settings()
