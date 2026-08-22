import aiohttp
import aiosqlite
from bot.config import settings

# عقد عملة USDT الرسمي على شبكة BSC (BEP20)
USDT_BEP20_CONTRACT = "0x55d398326f99059fF775485246999027B3197955".lower()


async def check_tx_exists(tx_hash: str) -> bool:
    """التحقق من عدم تكرار استخدام نفس المعاملة"""
    async with aiosqlite.connect(settings.db_path) as db:
        async with db.execute(
            "SELECT 1 FROM transactions WHERE tx_hash = ?", (tx_hash,)
        ) as cursor:
            return await cursor.fetchone() is not None


async def save_tx(tx_hash: str, user_id: int, amount: float):
    """حفظ المعاملة وزيادة رصيد المستخدم في قاعدة البيانات"""
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS transactions (tx_hash TEXT PRIMARY KEY, user_id INTEGER, amount REAL)"
        )
        await db.execute(
            "INSERT INTO transactions (tx_hash, user_id, amount) VALUES (?, ?, ?)",
            (tx_hash, user_id, amount),
        )
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id),
        )
        await db.commit()


async def verify_user_payment(user_id: int, expected_amount: float) -> tuple[bool, str]:
    """فحص البلوكشين مباشرة للتحقق من وصول المبلغ"""
    my_wallet = settings.wallets.get("BEP20", "").lower()
    
    # رابط Etherscan / BscScan API الموحد
    url = (
        f"https://api.etherscan.io/v2/api"
        f"?chainid=56"
        f"&module=account"
        f"&action=tokentx"
        f"&contractaddress={USDT_BEP20_CONTRACT}"
        f"&address={my_wallet}"
        f"&page=1&offset=10&sort=desc"
        f"&apikey={settings.bscscan_api_key}"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                data = await resp.json()

                if data.get("status") != "1" or not data.get("result"):
                    return False, "لم يتم العثور على أي تحويلات في الشبكة حتى الآن."

                for tx in data["result"]:
                    to_address = tx.get("to", "").lower()
                    tx_hash = tx.get("hash")
                    token_decimals = int(tx.get("tokenDecimal", 18))
                    amount_received = float(tx.get("value")) / (10 ** token_decimals)

                    # التحقق من المحفظة والمبلغ والهاش
                    if to_address == my_wallet and amount_received >= expected_amount:
                        if not await check_tx_exists(tx_hash):
                            await save_tx(tx_hash, user_id, amount_received)
                            return True, f"تم تأكيد الدفع بنجاح! تم شحن {amount_received} USDT إلى رصيدك 🎉"

                return False, "لم نجد أي تحويل مطابق للمبلغ المطلوب بعد. يُرجى الانتظار دقيقة وإعادة المحاولة."

    except Exception as e:
        return False, f"حدث خطأ أثناء الاتصال بالشبكة: {str(e)}"
