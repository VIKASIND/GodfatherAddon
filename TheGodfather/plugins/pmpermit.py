from pyrogram import filters, Client
import asyncio

from pyrogram.methods import messages
from TheGodfather import CMD_HELP
from TheGodfather.helpers.pyrohelper import get_arg, denied_users
import TheGodfather.database.pmpermitdb as Zectdb
from config import PREFIX

CMD_HELP.update(
    {
        "Anti-PM": """
『 **Anti-PM** 』
  `pmguard` [on or off] -> Activates or deactivates anti-pm.
  `setpmmsg` [message or default] -> Sets a custom anti-pm message.
  `setblockmsg` [message or default] -> Sets custom block message.
  `setlimit` [value] -> This one sets a max. message limit for unwanted PMs and when they go beyond it, bamm!.
  `allow` -> Allows a user to PM you.
  `deny` -> Denies a user to PM you.
  """
    }
)

FLOOD_CTRL = 0
ALLOWED = []
USERS_AND_WARNS = {}


@Client.on_message(filters.command("pmguard", PREFIX) & filters.me)
async def pmguard(app: Client, message):
    arg = get_arg(message)
    if not arg:
        await message.edit("**I only understand on or off**")
        return
    if arg == "off":
        await db.set_pm(False)
        await message.edit("**PM Guard Deactivated**")
    if arg == "on":
        await db.set_pm(True)
        await message.edit("**PM Guard Activated**")


@Client.on_message(filters.command("setlimit", PREFIX) & filters.me)
async def pmguard(app: Client, message):
    arg = get_arg(message)
    if not arg:
        await message.edit("**Set limit to what?**")
        return
    await db.set_limit(int(arg))
    await message.edit(f"**Limit set to {arg}**")


@Client.on_message(filters.command("setpmmsg", PREFIX) & filters.me)
async def setpmmsg(app: Client, message):
    arg = get_arg(message)
    if not arg:
        await message.edit("**What message to set**")
        return
    if arg == "default":
        await db.set_permit_message(db.PMPERMIT_MESSAGE)
        await message.edit("**Anti_PM message set to default**.")
        return
    await db.set_permit_message(f"`{arg}`")
    await message.edit("**Custom anti-pm message set**")


@Client.on_message(filters.command("setblockmsg", PREFIX) & filters.me)
async def setpmmsg(app: Client, message):
    arg = get_arg(message)
    if not arg:
        await message.edit("**What message to set**")
        return
    if arg == "default":
        await db.set_block_message(db.BLOCKED)
        await message.edit("**Block message set to default**.")
        return
    await db.set_block_message(f"`{arg}`")
    await message.edit("**Custom block message set**")


@Client.on_message(filters.command("allow", PREFIX) & filters.me & filters.private)
async def allow(app: Client, message):
    chat_id = message.chat.id
    pmpermit, pm_message, limit, block_message = await db.get_pm_settings()
    await db.allow_user(chat_id)
    await message.edit(f"**I have allowed [you](tg://user?id={chat_id}) to PM me.**")
    async for message in app.search_messages(
        chat_id=message.chat.id, query=pm_message, limit=1, from_user="me"
    ):
        await message.delete()
    USERS_AND_WARNS.update({chat_id: 0})


@Client.on_message(filters.command("deny", PREFIX) & filters.me & filters.private)
async def deny(app: Client, message):
    chat_id = message.chat.id
    await db.deny_user(chat_id)
    await message.edit(f"**I have denied [you](tg://user?id={chat_id}) to PM me.**")


@Client.on_message(
    filters.private
    & filters.create(denied_users)
    & filters.incoming
    & ~filters.service
    & ~filters.me
    & ~filters.bot
)
async def reply_pm(app: Client, message):
    global FLOOD_CTRL
    pmpermit, pm_message, limit, block_message = await db.get_pm_settings()
    user = message.from_user.id
    user_warns = 0 if user not in USERS_AND_WARNS else USERS_AND_WARNS[user]
    if user_warns <= limit - 2:
        user_warns += 1
        USERS_AND_WARNS.update({user: user_warns})
        if not FLOOD_CTRL > 0:
            FLOOD_CTRL += 1
        else:
            FLOOD_CTRL = 0
            return
        async for message in app.search_messages(
            chat_id=message.chat.id, query=pm_message, limit=1, from_user="me"
        ):
            await message.delete()
        await message.reply(pm_message, disable_web_page_preview=True)
        return
    await message.reply(block_message, disable_web_page_preview=True)
    await app.block_user(message.chat.id)
    USERS_AND_WARNS.update({user: 0})
