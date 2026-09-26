import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message

# Configuration
BOT_TOKEN = "8629276780:AAE_XJSmZ_1Y_egfGKJAPHreZKeNg2eyGzw"
ADMIN_ID = 8616559205  # ያንተ Telegram ID
TELEBIRR_NUMBER = "0999942281"

# Products Definition
PRODUCTS = {
    "prod_1": {
        "name": "🎬 3D Card Lyrics Edit Tutorial",
        "price": "200 ብር",
        "caption": "የ 3D Card Lyrics Video አሰራር ሙሉ ቱቶሪያል ቪዲዮ።"
    },
    "prod_2": {
        "name": "🎬 Text Animation Lyrics Edit Tutorial",
        "price": "200 ብር",
        "caption": "የ Text Animation Lyrics Video አሰራር ሙሉ ቱቶሪያል ቪዲዮ።"
    },
    "prod_xml": {
        "name": "📄 Alight Motion XML Preset File",
        "price": "150 ብር",
        "caption": "ለ Alight Motion የሚሆን ዝግጁ XML Preset ፋይል።"
    }
}

user_orders = {}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_main_keyboard():
    buttons = [
        [InlineKeyboardButton(text=f"{data['name']} - {data['price']}", callback_data=key)]
        for key, data in PRODUCTS.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(CommandStart())
async def start_cmd(message: Message):
    welcome_text = (
        f"ሰላም {message.from_user.first_name}! 👋\n\n"
        "እንኳን ወደ አላይት ሞሽን (Alight Motion) ትምህርቶች እና ኤክስኤምኤል (XML) መግዣ ቦት በደህና መጡ።\n\n"
        "እባክዎን መግዛት የሚፈልጉትን ምርት ይምረጡ፦"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@dp.callback_query(F.data.in_(PRODUCTS.keys()))
async def process_product_selection(callback: CallbackQuery):
    prod_key = callback.data
    user_orders[callback.from_user.id] = prod_key
    product = PRODUCTS[prod_key]
    
    text = (
        f"የመረጡት ምርት፦ *{product['name']}*\n"
        f"ክፍያ፦ *{product['price']}*\n\n"
        f"💳 **የክፍያ መመሪያ፦**\n"
        f"እባክዎን ክፍያውን በ Telebirr Wallet ቁጥር፦ `{TELEBIRR_NUMBER}` ይላኩ።\n\n"
        "ክፍያውን ፈፅመው ሲጨርሱ የከፈሉበትን **Screenshot (ደረሰኝ)** እዚሁ ቦት ላይ ይላኩ።"
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()

@dp.message(F.photo)
async def handle_screenshot(message: Message):
    user_id = message.from_user.id
    
    if user_id not in user_orders:
        await message.answer("እባክዎን አስቀድመው መግዛት የሚፈልጉትን ምርት ለመምረጥ /start የሚለውን ይጫኑ።")
        return

    prod_key = user_orders[user_id]
    product = PRODUCTS[prod_key]
    photo_id = message.photo[-1].file_id

    admin_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Approve", callback_data=f"app_{user_id}_{prod_key}"),
                InlineKeyboardButton(text="❌ Reject", callback_data=f"rej_{user_id}_{prod_key}")
            ]
        ]
    )

    admin_text = (
        f"📥 **አዲስ ክፍያ መጥቷል!**\n\n"
        f"👤 **ተጠቃሚ፦** {message.from_user.full_name} (@{message.from_user.username or 'NoUsername'})\n"
        f"🆔 **User ID፦** `{user_id}`\n"
        f"🛒 **የመረጠው ምርት፦** {product['name']}\n"
        f"💰 **ዋጋ፦** {product['price']}"
    )

    await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=admin_text, reply_markup=admin_kb)
    
    await message.answer("የከፈሉበት ደረሰኝ ለአድሚን ተልኳል። ክፍያው ተራጋግጦ አድሚን እንዳጸደቀው ቦቱ ምርቱን ወዲያውኑ ይልክልዎታል!")

@dp.callback_query(F.data.startswith("app_"))
async def approve_payment(callback: CallbackQuery):
    _, user_id_str, prod_key = callback.data.split("_")
    target_user_id = int(user_id_str)
    product = PRODUCTS[prod_key]

    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n✅ **ሁኔታ፦ ጸድቋል (Approved)**"
    )

    await bot.send_message(
        chat_id=target_user_id,
        text=f"🎉 ክፍያዎ ተረጋግጧል!\nለማውረድ የተዘጋጀው፦ *{product['name']}*",
        parse_mode="Markdown"
    )
    
    await bot.send_message(
        chat_id=target_user_id,
        text="🔗 ምርትዎን ለማግኘት በቴሌግራም አድሚኑን ያናግሩ ወይም Link/File በቅርቡ ይላክልዎታል።"
    )
    
    await callback.answer("ክፍያው ጸድቋል፤ ለተጠቃሚው ተልኳል።")

@dp.callback_query(F.data.startswith("rej_"))
async def reject_payment(callback: CallbackQuery):
    _, user_id_str, prod_key = callback.data.split("_")
    target_user_id = int(user_id_str)

    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n❌ **ሁኔታ፦ ውድቅ ተደርጓል (Rejected)**"
    )

    await bot.send_message(
        chat_id=target_user_id,
        text="❌ ይቅርታ! የላኩት የክፍያ ደረሰኝ አልተረጋገጠም። እባክዎን ትክክለኛ ደረሰኝ መላክዎን ያረጋግጡ ወይም አድሚኑን ያናግሩ።"
    )

    await callback.answer("ክፍያው ውድቅ ተደርጓል።")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
