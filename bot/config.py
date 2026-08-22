import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    # ضع التوكن تبع بوتك (من BotFather) بملف .env تحت اسم BOT_TOKEN
    bot_token: str = os.getenv("BOT_TOKEN", "8847445337:AAFayzATCl8C-4sexybj_wHD90rnkVHTxIs")

    # آيدي حسابك على تيليجرام (رقمي) عشان يوصلك إشعار الطلبات الجديدة
    admin_ids: list[int] = field(
        default_factory=lambda: [
            int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
        ]
    )

    db_path: str = os.getenv("DB_PATH", "shop.db")

    # مفتاح Etherscan / BscScan API للفحص التلقائي
    bscscan_api_key: str = os.getenv(
        "BSCSCAN_API_KEY", 
        "DZAT8UBAMWJBJF67IGGG3IW889FGRISB4B"
    )

    # عناوين المحافظ - ضع عنوان محفظتك من Trust Wallet هنا
    wallets: dict = field(
        default_factory=lambda: {
            "BEP20": os.getenv("WALLET_BEP20", "0x013c272413F0a6b49b8c042082f87D2da1f732C5"),
            "TRC20": os.getenv("WALLET_TRC20", "TYourTRC20AddressHere"),
            "POLYGON": os.getenv("WALLET_POLYGON", "0xYourPolygonAddressHere"),
        }
    )

    currency_symbol: str = "USD"


settings = Settings()
