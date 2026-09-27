import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message

# Configuration
BOT_TOKEN = "8629276780:AAE_XJSmZ_1Y_egfGKJAPHreZKeNg2eyGzw"
ADMIN_ID = 8616559205  # ያንተ Telegram ID
TELEBIRR_NUMBER = "0999942281"

# Products Definition (100% Correct Telegram File IDs)
PRODUCTS = {
    "p1": {
        "name": "🎬 3D Card Lyrics Edit Tutorial Video",
        "price": "200 ብር",
        "caption": "የ 3D Card Lyrics Video አሰራር ሙሉ ቱቶሪያል ቪዲዮ።",
        "delivery_type": "video",
        "content": "BAACAgQAAxkBAAEi7uxquMpEMf1EROWbSWYJjolZYUwa6QACZiEAAq0VyFFbTbSlsYN2Yj0E"
    },
    "p2": {
        "name": "🎬 Text Animation Lyrics Edit Tutorial Video",
        "price": "200 ብር",
        "caption": "የ Text Animation Lyrics Video አሰራር ሙሉ ቱቶሪያል ቪዲዮ።",
        "delivery_type": "video",
        "content": "BAACAgQAAxkBAAEi7utquMpEdmT3t9ONfy7Z7AO04LsrvgACYSEAAq0VyFF9ccA4B4tRmT0E"
    },
    "p3": {
        "name": "📄 Text Animation Lyrics Edit XML File",
        "price": "150 ብር",
        "caption": "ለ Text Animation Lyrics Edit የሚሆን XML Preset ፋይል።",
        "delivery_type": "document",
        "content": "BQACAgQAAxkBAAEi7kxquKiRJZq5mHe4CsUswcjrRI0JWgAC6RsAAq0VwFFEK9YKYq-Q8j0E"
    },
    "p4": {
        "name": "📄 3D Card Lyrics Edit XML File",
        "price": "150 ብር",
        "caption": "ለ 3D Card Lyrics Edit የሚሆን XML Preset ፋይል።",
        "delivery_type": "document",
        "content": "BQACAgQAAxkBAAEi7kpquKh0lQHyGXgbT7Mo4FtDWt5wiQACZyEAAq0VyFEls1lywTAapD0E"
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

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id in user_orders:
        del user_orders[user_id]
        
    welcome_text = (
        f"ሰላም {callback.from_user.first_name}! 👋\n\n"
        "እባክዎን መግዛት የሚፈልጉትን ምርት ይምረጡ፦"
    )
    await callback.message.edit_text(welcome_text, reply_markup=get_main_keyboard())
    await callback.answer()

@dp.callback_query(F.data.in_(PRODUCTS.keys()))
async def process_product_selection(callback: CallbackQuery):
    prod_key = callback.data
    user_orders[callback.from_user.id] = prod_key
    product = PRODUCTS[prod_key]
    
    pay_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ ተመለስ (Back)", callback_data="back_to_menu")]
        ]
    )
    
    text = (
        f"የመረጡት ምርት፦ *{product['name']}*\n"
        f"ክፍያ፦ *{product['price']}*\n\n"
        f"💳 **የክፍያ መመሪያ፦**\n"
        f"እባክዎን ክፍያውን በ Telebirr Wallet ቁጥር፦ `{TELEBIRR_NUMBER}` ይላኩ።\n\n"
        "ክፍያውን ፈፅመው ሲጨርሱ የከፈሉበትን **Screenshot (ደረሰኝ)** እዚሁ ቦት ላይ ይላኩ።"
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=pay_keyboard)
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
                InlineKeyboardButton(text="✅ Approve", callback_data=f"a|{user_id}|{prod_key}"),
                InlineKeyboardButton(text="❌ Reject", callback_data=f"r|{user_id}|{prod_key}")
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

@dp.callback_query(F.data.startswith("a|"))
async def approve_payment(callback: CallbackQuery):
    _, user_id_str, prod_key = callback.data.split("|")
    target_user_id = int(user_id_str)
    product = PRODUCTS[prod_key]

    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n✅ **ሁኔታ፦ ጸድቋል (Approved)**"
    )

    try:
        if product["delivery_type"] == "video":
            await bot.send_video(
                chat_id=target_user_id,
                video=product["content"],
                caption=f"🎬 {product['name']}\n\nስለገዙ እናመሰግናለን!"
            )
        elif product["delivery_type"] == "document":
            await bot.send_document(
                chat_id=target_user_id,
                document=product["content"],
                caption=f"📄 {product['name']}\n\nስለገዙ እናመሰግናለን!"
            )

        await bot.send_message(
            chat_id=target_user_id,
            text=f"🎉 **ክፍያዎ ተረጋግጧል!**\n\nየመረጡት፦ *{product['name']}* በላይ ተልኮልዎታል።\n\nሌላ ተጨማሪ ትምህርት ወይም XML መግዛት ከፈለጉ ድጋሚ /start በማለት መግዛት ይችላሉ!",
            parse_mode="Markdown"
        )
        await callback.answer("ክፍያው ጸድቋል፤ ቪዲዮው/ፋይሉ ለተጠቃሚው ተልኳል!")

    except Exception as e:
        logging.error(f"Failed to send file: {e}")
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"⚠️ **ፋይል መላክ አልተቻለም!**\n\n**Error:** `{e}`",
            parse_mode="Markdown"
        )
        await callback.answer("ስህተት ተፈጥሯል፤ ፋይሉ አልተላከም!", show_alert=True)

    if target_user_id in user_orders:
        del user_orders[target_user_id]

@dp.callback_query(F.data.startswith("r|"))
async def reject_payment(callback: CallbackQuery):
    _, user_id_str, prod_key = callback.data.split("|")
    target_user_id = int(user_id_str)

    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n❌ **ሁኔታ፦ ውድቅ ተደርጓል (Rejected)**"
    )

    await bot.send_message(
        chat_id=target_user_id,
        text="❌ ይቅርታ! የላኩት የክፍያ ደረሰኝ አልተረጋገጠም። እባክዎን ትክክለኛ ደረሰኝ መላክዎን ያረጋግጡ ወይም አድሚኑን ያናግሩ።"
    )

    if target_user_id in user_orders:
        del user_orders[target_user_id]

    await callback.answer("ክፍያው ውድቅ ተደርጓል።")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
