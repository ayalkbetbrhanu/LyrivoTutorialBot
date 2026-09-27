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
        "name": "🎬 3D Card Lyrics Edit Tutorial Video",
        "price": "200 ብር",
        "caption": "የ 3D Card Lyrics Video አሰራር ሙሉ ቱቶሪያል ቪዲዮ።",
        "delivery_type": "video",
        "content": "AAMCBAADGQEDmFZxarijYpL7lST8B0TLWpn8BOk7Q3gAAmYhAAKtFchRvnLTuz25K5wBAAdtAAM9BA"
    },
    "prod_2": {
        "name": "🎬 Text Animation Lyrics Edit Tutorial Video",
        "price": "200 ብር",
        "caption": "የ Text Animation Lyrics Video አሰራር ሙሉ ቱቶሪያል ቪዲዮ።",
        "delivery_type": "video",
        "content": "AAMCBAADGQEDmFb3arilFmh9-l-0pCgnuwUGpZGzmFEAAmEhAAKtFchRth-ezFqfd9EBAAdtAAM9BA"
    },
    "prod_xml_text": {
        "name": "📄 Text Animation Lyrics Edit XML File",
        "price": "150 ብር",
        "caption": "ለ Text Animation Lyrics Edit የሚሆን XML Preset ፋይል።",
        "delivery_type": "document",
        "content": "BQACAgQAAxKBAAEi7kpquKh01QHyGXgbT7Mo4FtDWt5wiQACZYEAAq0VyFEls1lywTAapDOE"
    },
    "prod_xml_3d": {
        "name": "📄 3D Card Lyrics Edit XML File",
        "price": "150 ብር",
        "caption": "ለ 3D Card Lyrics Edit የሚሆን XML Preset ፋይል።",
        "delivery_type": "document",
        "content": "BQACAgQAAxKBAAEi7kpquKh01QHyGXgbT7Mo4FtDWt5wiQACZyEAAq0VyFEls1lywTAapDOE"
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

    # አድሚኑ ጋር ያለውን መልእክት ማስተካከል
    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n✅ **ሁኔታ፦ ጸድቋል (Approved)**"
    )

    # ለተጠቃሚው ማሳወቂያ መላክ
    await bot.send_message(
        chat_id=target_user_id,
        text=f"🎉 **ክፍያዎ ተረጋግጧል!**\n\nየመረጡት፦ *{product['name']}* ከታች ይላክሎታል።\n\nሌላ ተጨማሪ ትምህርት ወይም XML መግዛት ከፈለጉ ድጋሚ /start በማለት መግዛት ይችላሉ!",
        parse_mode="Markdown"
    )

    # አውቶማቲክ ቪዲዮ ወይም ፋይል መላክ
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

    # የተጠቃሚውን የትዕዛዝ ታሪክ ማጽዳት (ድጋሚ ሌላ ምርት መግዛት እንዲችል)
    if target_user_id in user_orders:
        del user_orders[target_user_id]

    await callback.answer("ክፍያው ጸድቋል፤ ቪዲዮው/ፋይሉ ለተጠቃሚው ተልኳል!")

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

    # ውድቅ ከተደረገ በኋላም ቢሆን ድጋሚ መሞከር እንዲችል ማጽዳት
    if target_user_id in user_orders:
        del user_orders[target_user_id]

    await callback.answer("ክፍያው ውድቅ ተደርጓል።")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
