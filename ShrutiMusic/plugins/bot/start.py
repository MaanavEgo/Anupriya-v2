# ================================
#  SHRUTI + SONALI ANIMATED START
# ================================

import time, asyncio, random
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from py_yt import VideosSearch

import config
from ShrutiMusic import app
from ShrutiMusic.misc import _boot_
from ShrutiMusic.plugins.sudo.sudoers import sudoers_list
from ShrutiMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from ShrutiMusic.utils import bot_sys_stats
from ShrutiMusic.utils.decorators.language import LanguageStart
from ShrutiMusic.utils.formatters import get_readable_time
from ShrutiMusic.utils.inline import help_pannel_page1, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

# ============================
#         EMOJIS / MEDIA
# ============================

EMOJIS = ["🥰", "🔥", "💖", "🩷", "🩵", "🩶", "💘", "🩷", "🩵", "🩶", " 👍"]

ANIM_STICKERS = [
    "CAACAgUAAxkBAAKOmmkz-ntJaFPXb0carGSNRtKHl69sAAL7HQACNIWhVdDyUdqb8yMtHgQ",
    "CAACAgUAAxkBAAKOm2kz-nsnFNG9zS0eyjaE9mEriTN2AAKLHQACXmKhVWRYc-mThaGHHgQ",
    "CAACAgUAAxkBAAKOnGkz-ny89GKzIC8y38Gqdg_ujQg4AAIkHAAChPKgVcjV8fUfimNGHgQ",
    "CAACAgUAAxkBAAKOnWkz-nz5cZGEYLoWfp7QZgIbf9HbAAIRHQAC_jOgVdqhnaopN_EJHgQ", 
    "CAACAgUAAxkBAAKOnmkz-n013B233W24UyE4KiAtEbRlAAKAGwAC0VOgVe_Z1cRSzI-sHgQ", 
    "CAACAgUAAxkBAAKOn2kz-n2FSJi7MKC9q0Wy6T7CilM8AALTHAACvgABoFXBEMums5ywdR4E", 
    "CAACAgUAAxkBAAKOoGkz-n7ENOqTjvLOaCZFSkOZLiYCAAJaGwACWXKgVaxKbq4HeZ4MHgQ",
    "CAACAgUAAxkBAAKOoWkz-n7JfmZjgzI7n5srNEY_bkyGAAINGgACbpigVSc4KH8aMEshHgQ", 
    "CAACAgUAAxkBAAKOomkz-n-62srSaAOYMPKLHPevi8FBAAJvHAACcwmgVbva9WxHwDJIHgQ", 
    "CAACAgUAAxkBAAKOo2kz-oBmaCHZ96BNQafgepRINZKYAAKjGwACeZmgVSPTNWP_M9WLHgQ", 
]

START_IMAGES = [
    "https://files.catbox.moe/m3nwoc.jpg",
    "https://files.catbox.moe/1aq05n.jpg",
    "https://files.catbox.moe/qmzpc7.jpg",
    "https://files.catbox.moe/9ajyzg.jpg",
    "https://files.catbox.moe/ecg4k6.jpg",
    "https://files.catbox.moe/25a0yk.jpg",
]

EFFECT_IDS = [
    5046509860389126442,
    5107584321108051014,
    5104841245755180586,
    5159385139981059251,
]

# ============================
#     GET USER PHOTO/VIDEO
# ============================

async def get_user_media(user_id):
    """
    Returns user's profile photo/video frame.
    Fallback → random START_IMAGES
    """
    try:
        async for p in app.get_chat_photos(user_id, limit=1):
            return p.file_id
        return random.choice(START_IMAGES)
    except:
        return random.choice(START_IMAGES)

# ============================
#     START – PRIVATE
# ============================

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):

    await add_served_user(message.from_user.id)

    # Reaction
    try:
        await message.react(random.choice(EMOJIS))
    except:
        pass

    # Sticker animation
    stkr = await message.reply_sticker(random.choice(ANIM_STICKERS))
    await asyncio.sleep(1)
    await stkr.delete()

    # ========= PARAMETER HANDLER ==========
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        # HELP
        if name.startswith("help"):
            keyboard = help_pannel_page1(_)
            return await message.reply_photo(
                photo=random.choice(START_IMAGES),
                caption=_["help_1"].format(config.SUPPORT_GROUP),
                message_effect_id=random.choice(EFFECT_IDS),
                has_spoiler=True,
                reply_markup=keyboard,
            )

        # SUDOLIST
        if name.startswith("sud"):
            return await sudoers_list(client=client, message=message, _=_)

        # VIDEO INFO
        if name.startswith("inf"):

            m = await message.reply_text("🔎 Searching...")

            query = name.replace("info_", "")
            query = f"https://www.youtube.com/watch?v={query}"

            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                chlink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]

            text = _["start_6"].format(
                title, duration, views, published, chlink, channel, app.mention
            )

            btn = InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(_["S_B_8"], url=link),
                    InlineKeyboardButton(_["S_B_9"], url=config.SUPPORT_GROUP),
                ]]
            )

            await m.delete()

            return await app.send_photo(
                message.chat.id,
                photo=thumbnail,
                caption=text,
                has_spoiler=True,
                message_effect_id=random.choice(EFFECT_IDS),
                reply_markup=btn,
            )

    # ========= NORMAL START TEXT ==========
    t = await message.reply_text(f"<b>ʜᴇʏ {message.from_user.mention} 💕</b>")
    await asyncio.sleep(0.4)
    await t.edit_text("<b>ɪ ᴧᴍ ʏᴏᴜʀ ᴍᴜsɪᴄ ʙᴏᴛ 🎧</b>")
    await asyncio.sleep(0.4)
    await t.edit_text("<b>ʜᴏᴡ ᴧʀᴇ ʏᴏᴜ ᴛᴏᴅᴧʏ..? 💫</b>")
    await asyncio.sleep(0.4)
    await t.delete()

    # Get user profile media (photo/video) or fallback random image
    user_media = await get_user_media(message.from_user.id)

    # Final Card
    out = private_panel(_)
    return await message.reply_photo(
        user_media,
        caption=_["start_2"].format(message.from_user.mention, app.mention),
        has_spoiler=True,
        message_effect_id=random.choice(EFFECT_IDS),
        reply_markup=InlineKeyboardMarkup(out),
    )

# ============================
#         START – GROUPS
# ============================

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):

    uptime = int(time.time() - _boot_)
    out = start_panel(_)

    return await message.reply_photo(
        random.choice(START_IMAGES),
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        has_spoiler=True,
        reply_markup=InlineKeyboardMarkup(out),
    )

# ============================
#       WELCOME SYSTEM
# ============================

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):

    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

            # Bot joined
            if member.id == app.id:

                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_GROUP,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)

                await message.reply_photo(
                    random.choice(START_IMAGES),
                    caption=_["start_3"].format(
                        message.from_user.first_name,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    has_spoiler=True,
                    reply_markup=InlineKeyboardMarkup(out),
                )

                await add_served_chat(message.chat.id)
                await message.stop_propagation()

        except Exception as ex:
            print(ex)
