from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ShrutiMusic import app
from ShrutiMusic.utils.database import get_assistant


@app.on_message(filters.video_chat_members_invited)
async def brah3(_, message: Message):
    text = f"➻ {message.from_user.mention}\n\n๏ ɪɴᴠɪᴛɪɴɢ ɪɴ ᴠᴄ ᴛᴏ :\n\n➻ "

    invited_users = message.video_chat_members_invited.users

    for user in invited_users:
        try:
            if user.username:
                mention = f"@{user.username}"
            else:
                mention = f"[{user.first_name}](tg://user?id={user.id})"

            text += f"{mention} "
        except Exception:
            pass

    try:
        add_link = f"https://t.me/{app.username}?startgroup=true"
        reply_text = f"{text} 🤭🤭"

        await message.reply(
            reply_text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("๏ ᴊᴏɪɴ ᴠᴄ ๏", url=add_link)]]
            ),
            disable_web_page_preview=True
        )

    except Exception as e:
        print(f"Error: {e}")
