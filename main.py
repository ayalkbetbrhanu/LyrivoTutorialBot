import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# === እዚህ ጋር መረጃዎችህን አስገባ ===
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_CHAT_ID = 123456789  # የአንተ Telegram User ID (በ @userinfobot ማወቅ ትችላለህ)

# የምርቶችና የፋይሎች ዝርዝር (File ID ወይም የፋይል Path)
PRODUCTS = {
    "p1": {"name": "3D Card Lyrics Edit Tutorial", "file": "YOUR_TUTORIAL_LINK_OR_FILE_ID"},
    "p2": {"name": "Text Animation Lyrics Edit Tutorial", "file": "YOUR_TUTORIAL_LINK_OR_FILE_ID"},
    "p3": {"name": "Text Animation Lyrics Edit XML", "file_path": "files/text_anim.xml"},
    "p4": {"name": "3D Card Lyrics Edit XML", "file_path": "files/3d_card.xml"}
}

# 1. ድህረ ገጹ ላይ ያለውን Start Link ሲጫኑ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        prod_id = args[0]
        if prod_id in PRODUCTS:
            context.user_data['pending_product'] = prod_id
            await update.message.reply_text(
                f"🎯 **የመረጡት ምርት፦** {PRODUCTS[prod_id]['name']}\n\n"
                "እባክዎን የ Telebirr ክፍያ ደረሰኝ (Screenshot) እዚህ ይላኩ።"
            )
            return
    await update.message.reply_text("ሰላም! እባክዎን ምርቶችን ለመግዛት ድህረ ገጻችንን ይጠቀሙ።")

# 2. ደንበኛው Screenshot ሲልክ
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prod_id = context.user_data.get('pending_product')
    if not prod_id:
        await update.message.reply_text("እባክዎን አስቀድመው ከድህረ ገጹ ምርት ይምረጡ።")
        return

    user = update.effective_user
    photo_id = update.message.photo[-1].file_id

    # ለደንበኛው ምላሽ መስጠት
    await update.message.reply_text("⏳ ደረሰኝዎ ደርሶናል! አረጋግጠን ፋይሉን ወዲያውኑ እንልክልዎታለን።")

    # ለአንተ (Admin) ደረሰኙን ከነ ማረጋገጫ ቁልፍ መላክ
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm & Send", callback_data=f"approve_{user.id}_{prod_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    admin_caption = (
        f"📩 **አዲስ ክፍያ ደርሷል!**\n\n"
        f"👤 ደንበኛ፦ {user.full_name} (@{user.username})\n"
        f"🛒 ምርት፦ {PRODUCTS[prod_id]['name']}\n"
        f"🆔 User ID፦ `{user.id}`"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=photo_id,
        caption=admin_caption,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# 3. አንተ (Admin) Confirm ወይም Reject ስትጫን የሚሰራ
async def handle_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    action = data[0]
    user_id = int(data[1])

    if action == "approve":
        prod_id = data[2]
        prod_info = PRODUCTS[prod_id]

        try:
            # ፋይል ከሆነ ፋይሉን ይልካል
            if "file_path" in prod_info:
                await context.bot.send_document(
                    chat_id=user_id,
                    document=open(prod_info["file_path"], 'rb'),
                    caption=f"✅ ክፍያዎ ተረጋግጧል!\n\nእነሆ የ **{prod_info['name']}** XML ፋይል።"
                )
            # ቪዲዮ/ሊንክ ከሆነ ሊንኩን ይልካል
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"✅ ክፍያዎ ተረጋግጧል!\n\nየቱቶሪያል ቪዲዮው ሊንክ፦ {prod_info['file']}"
                )

            await query.edit_message_caption(caption=f"{query.message.caption}\n\n✅ **ተረጋግጦ ፋይሉ ተልኳል!**")
        except Exception as e:
            await query.edit_message_caption(caption=f"{query.message.caption}\n\n⚠️ **ስህተት ተከሰተ፦** {e}")

    elif action == "reject":
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ ይቅርታ! የላኩት የክፍያ ደረሰኝ አልተረጋገጠም። እባክዎን ትክክለኛውን ደረሰኝ እንደገና ይላኩ ወይም በ Telegram ያናግሩን።"
        )
        await query.edit_message_caption(caption=f"{query.message.caption}\n\n❌ **ውድቅ ተደርጓል!**")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(handle_approval))
    app.run_polling()

if __name__ == "__main__":
    main()
