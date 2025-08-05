from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from tinydb import TinyDB, Query
import random
import time
import uuid

API_ID = 21472111
API_HASH = "2a51fd4825b3b947c253f8f9b8f830f7"
BOT_TOKEN = "8246622394:AAEbHlAtOjM8PLnAJl-Qcbf8AV6p9AsSKV8"

app = Client("sps_pvp_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db = TinyDB("sps_users.json")
User = Query()

CHOICES = {"Stone": "🪨 Stone", "Paper": "📄 Paper", "Scissors": "✂️ Scissors"}
SLOTS = ["🍎", "🍋", "🍒", "💎", "🔔"]
pending_pvps = {}
pvp_moves = {}
pvp_chats = {}
mines_games = {}
dice_games = {}
coin_games = {}
slot_games = {}
number_games = {}

def update_stats(uid, result=None, game="sps", gems=0):
    user = db.get(User.id == uid)
    if not user:
        user = {
            "id": uid, "wins": 0, "losses": 0, "draws": 0, "exp": 0, "level": 1,
            "gems": 100, "last_daily": 0, "mines": {"played": 0, "wins": 0, "losses": 0, "safe_reveals": 0},
            "dice": {"played": 0, "wins": 0, "losses": 0}, "coin": {"played": 0, "wins": 0, "losses": 0},
            "slots": {"played": 0, "wins": 0, "losses": 0}, "number": {"played": 0, "wins": 0, "losses": 0}
        }
        db.insert(user)
    else:
        user.setdefault("wins", 0)
        user.setdefault("losses", 0)
        user.setdefault("draws", 0)
        user.setdefault("exp", 0)
        user.setdefault("level", 1)
        user.setdefault("gems", 100)
        user.setdefault("last_daily", 0)
        user.setdefault("mines", {"played": 0, "wins": 0, "losses": 0, "safe_reveals": 0})
        user.setdefault("dice", {"played": 0, "wins": 0, "losses": 0})
        user.setdefault("coin", {"played": 0, "wins": 0, "losses": 0})
        user.setdefault("slots", {"played": 0, "wins": 0, "losses": 0})
        user.setdefault("number", {"played": 0, "wins": 0, "losses": 0})

    exp_gain = 0
    gem_change = gems

    if game == "sps":
        if result == "win":
            user["wins"] += 1
            user["exp"] += 15
            user["gems"] += gem_change
            exp_gain = 15
        elif result == "lose":
            user["losses"] += 1
            user["exp"] += 5
            user["gems"] += gem_change
            exp_gain = 5
        else:
            user["draws"] += 1
            user["exp"] += 8
            exp_gain = 8
    elif game == "mines":
        user["mines"]["safe_reveals"] += 1
        user["exp"] += 5
        user["gems"] += gem_change
        exp_gain = 5
    elif game == "dice":
        user["dice"]["played"] += 1
        if result == "win":
            user["dice"]["wins"] += 1
            user["exp"] += 12
            user["gems"] += gem_change
            exp_gain = 12
        else:
            user["dice"]["losses"] += 1
            user["exp"] += 6
            user["gems"] += gem_change
            exp_gain = 6
    elif game == "coin":
        user["coin"]["played"] += 1
        if result == "win":
            user["coin"]["wins"] += 1
            user["exp"] += 10
            user["gems"] += gem_change
            exp_gain = 10
        else:
            user["coin"]["losses"] += 1
            user["exp"] += 5
            user["gems"] += gem_change
            exp_gain = 5
    elif game == "slots":
        user["slots"]["played"] += 1
        if result == "win":
            user["slots"]["wins"] += 1
            user["exp"] += 20
            user["gems"] += gem_change
            exp_gain = 20
        else:
            user["slots"]["losses"] += 1
            user["exp"] += 8
            user["gems"] += gem_change
            exp_gain = 8
    elif game == "number":
        user["number"]["played"] += 1
        if result == "win":
            user["number"]["wins"] += 1
            user["exp"] += 25
            user["gems"] += gem_change
            exp_gain = 25
        else:
            user["number"]["losses"] += 1
            user["exp"] += 10
            user["gems"] += gem_change
            exp_gain = 10

    leveled_up = False
    if user["exp"] >= user["level"] * 50:
        user["exp"] = 0
        user["level"] += 1
        user["gems"] += 100
        leveled_up = True

    db.update(user, User.id == uid)
    return exp_gain, leveled_up, user["gems"]

def generate_user_specific_data(user_id, data):
    return f"{data}_{user_id}_{uuid.uuid4().hex[:8]}"

@app.on_message(filters.command("start"))
async def start_game(_, msg: Message):
    user_id = msg.from_user.id
    user = db.get(User.id == user_id)
    gems = user["gems"] if user else 100
    await msg.reply(
        f"🎮 **Ultimate Game Arena** 💎\nWelcome, Champion! Gems: {gems}\nChoose your challenge:",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🪨 SPS", callback_data=generate_user_specific_data(user_id, "menu_sps")),
                InlineKeyboardButton("🎯 Mines", callback_data=generate_user_specific_data(user_id, "menu_mines"))
            ],
            [
                InlineKeyboardButton("🎲 Dice", callback_data=generate_user_specific_data(user_id, "menu_dice")),
                InlineKeyboardButton("🪙 Coin", callback_data=generate_user_specific_data(user_id, "menu_coin"))
            ],
            [
                InlineKeyboardButton("🎰 Slots", callback_data=generate_user_specific_data(user_id, "menu_slots")),
                InlineKeyboardButton("🔢 Number", callback_data=generate_user_specific_data(user_id, "menu_number"))
            ],
            [
                InlineKeyboardButton("📊 Stats", callback_data=generate_user_specific_data(user_id, "menu_stats")),
                InlineKeyboardButton("🏆 Leaderboard", callback_data=generate_user_specific_data(user_id, "menu_leaderboard"))
            ],
            [
                InlineKeyboardButton("💰 Shop", callback_data=generate_user_specific_data(user_id, "menu_shop")),
                InlineKeyboardButton("🎁 Gift Gems", callback_data=generate_user_specific_data(user_id, "menu_gift"))
            ],
            [InlineKeyboardButton("🌟 Daily Gems", callback_data=generate_user_specific_data(user_id, "daily_gems"))]
        ])
    )

@app.on_message(filters.command("pvp"))
async def pvp_challenge(_, msg: Message):
    if not msg.reply_to_message:
        return await msg.reply("⚠️ Reply to a user to challenge them!")
    challenger = msg.from_user.id
    user = db.get(User.id == challenger)
    if not user or user["gems"] < 20:
        return await msg.reply("⚠️ Need 20 💎 to challenge!")
    opponent = msg.reply_to_message.from_user.id
    if challenger == opponent:
        return await msg.reply("🙄 Can't challenge yourself!")
    pending_pvps[opponent] = challenger
    pvp_chats[challenger] = msg.chat.id
    await app.send_message(
        opponent,
        f"👊 [{msg.from_user.first_name}](tg://user?id={challenger}) challenges you to SPS PvP! (Cost: 20 💎)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Accept", callback_data=generate_user_specific_data(opponent, f"accept_{challenger}"))]
        ])
    )
    await msg.reply("✅ Challenge sent! Waiting for response...")

@app.on_message(filters.command("gift"))
async def gift_gems(_, msg: Message):
    if not msg.reply_to_message:
        return await msg.reply("⚠️ Reply to a user to gift gems!")
    sender = msg.from_user.id
    receiver = msg.reply_to_message.from_user.id
    if sender == receiver:
        return await msg.reply("🙄 Can't gift yourself!")
    try:
        amount = int(msg.text.split()[1])
        if amount <= 0:
            raise ValueError
    except (IndexError, ValueError):
        return await msg.reply("⚠️ Use: /gift <amount> (positive number)!")
    user = db.get(User.id == sender)
    if not user or user["gems"] < amount:
        return await msg.reply("⚠️ Not enough gems!")
    user["gems"] -= amount
    db.update(user, User.id == sender)
    receiver_user = db.get(User.id == receiver)
    if not receiver_user:
        receiver_user = {"id": receiver, "gems": 100}
        db.insert(receiver_user)
    receiver_user["gems"] += amount
    db.update(receiver_user, User.id == receiver)
    await msg.reply(f"🎁 Sent {amount} 💎 to [{msg.reply_to_message.from_user.first_name}](tg://user?id={receiver})!")
    await app.send_message(receiver, f"🎁 You received {amount} 💎 from [{msg.from_user.first_name}](tg://user?id={sender})!")

@app.on_message(filters.command("stats"))
async def stats_menu(_, msg: Message):
    user_id = msg.from_user.id
    await msg.reply(
        "📊 Select a game to view stats:",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🪨 SPS", callback_data=generate_user_specific_data(user_id, "show_sps_stats")),
                InlineKeyboardButton("🎯 Mines", callback_data=generate_user_specific_data(user_id, "show_mines_stats"))
            ],
            [
                InlineKeyboardButton("🎲 Dice", callback_data=generate_user_specific_data(user_id, "show_dice_stats")),
                InlineKeyboardButton("🪙 Coin", callback_data=generate_user_specific_data(user_id, "show_coin_stats"))
            ],
            [
                InlineKeyboardButton("🎰 Slots", callback_data=generate_user_specific_data(user_id, "show_slots_stats")),
                InlineKeyboardButton("🔢 Number", callback_data=generate_user_specific_data(user_id, "show_number_stats"))
            ]
        ])
    )

@app.on_callback_query()
async def callback_handler(_, query: CallbackQuery):
    user_id = query.from_user.id
    data = query.data.split("_")
    if len(data) < 3 or data[-2] != str(user_id):
        return await query.answer("❌ This button isn't for you!", show_alert=True)
    action = "_".join(data[:-2])

    if action == "menu_stats":
        await query.message.edit_text(
            "📊 Select a game to view stats:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🪨 SPS", callback_data=generate_user_specific_data(user_id, "show_sps_stats")),
                    InlineKeyboardButton("🎯 Mines", callback_data=generate_user_specific_data(user_id, "show_mines_stats"))
                ],
                [
                    InlineKeyboardButton("🎲 Dice", callback_data=generate_user_specific_data(user_id, "show_dice_stats")),
                    InlineKeyboardButton("🪙 Coin", callback_data=generate_user_specific_data(user_id, "show_coin_stats"))
                ],
                [
                    InlineKeyboardButton("🎰 Slots", callback_data=generate_user_specific_data(user_id, "show_slots_stats")),
                    InlineKeyboardButton("🔢 Number", callback_data=generate_user_specific_data(user_id, "show_number_stats"))
                ],
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "show_sps_stats":
        user = db.get(User.id == user_id)
        if not user:
            return await query.answer("ℹ️ No stats yet!", show_alert=True)
        user.setdefault("wins", 0)
        user.setdefault("losses", 0)
        user.setdefault("draws", 0)
        user.setdefault("exp", 0)
        user.setdefault("level", 1)
        user.setdefault("gems", 100)
        text = (
            f"📊 **SPS Stats**\n"
            f"🏅 Level: {user['level']}\n"
            f"🌟 EXP: {user['exp']}/{user['level']*50}\n"
            f"💎 Gems: {user['gems']}\n"
            f"🏆 Wins: {user['wins']}\n"
            f"😢 Losses: {user['losses']}\n"
            f"😐 Draws: {user['draws']}"
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "menu_stats"))]
        ]))
    elif action == "show_mines_stats":
        user = db.get(User.id == user_id)
        if not user:
            return await query.answer("ℹ️ No stats yet!", show_alert=True)
        user.setdefault("mines", {"played": 0, "wins": 0, "losses": 0, "safe_reveals": 0})
        m = user["mines"]
        text = (
            f"📊 **Mines Stats**\n"
            f"💎 Gems: {user['gems']}\n"
            f"🎮 Games Played: {m['played']}\n"
            f"✅ Wins: {m['wins']}\n"
            f"💥 Losses: {m['losses']}\n"
            f"🔎 Safe Tiles: {m['safe_reveals']}"
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "menu_stats"))]
        ]))
    elif action == "show_dice_stats":
        user = db.get(User.id == user_id)
        if not user:
            return await query.answer("ℹ️ No stats yet!", show_alert=True)
        user.setdefault("dice", {"played": 0, "wins": 0, "losses": 0})
        d = user["dice"]
        text = (
            f"📊 **Dice Roll Stats**\n"
            f"💎 Gems: {user['gems']}\n"
            f"🎮 Games Played: {d['played']}\n"
            f"✅ Wins: {d['wins']}\n"
            f"😢 Losses: {d['losses']}"
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "menu_stats"))]
        ]))
    elif action == "show_coin_stats":
        user = db.get(User.id == user_id)
        if not user:
            return await query.answer("ℹ️ No stats yet!", show_alert=True)
        user.setdefault("coin", {"played": 0, "wins": 0, "losses": 0})
        c = user["coin"]
        text = (
            f"📊 **Coin Flip Stats**\n"
            f"💎 Gems: {user['gems']}\n"
            f"🎮 Games Played: {c['played']}\n"
            f"✅ Wins: {c['wins']}\n"
            f"😢 Losses: {c['losses']}"
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "menu_stats"))]
        ]))
    elif action == "show_slots_stats":
        user = db.get(User.id == user_id)
        if not user:
            return await query.answer("ℹ️ No stats yet!", show_alert=True)
        user.setdefault("slots", {"played": 0, "wins": 0, "losses": 0})
        s = user["slots"]
        text = (
            f"📊 **Slots Stats**\n"
            f"💎 Gems: {user['gems']}\n"
            f"🎮 Games Played: {s['played']}\n"
            f"✅ Wins: {s['wins']}\n"
            f"😢 Losses: {s['losses']}"
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "menu_stats"))]
        ]))
    elif action == "show_number_stats":
        user = db.get(User.id == user_id)
        if not user:
            return await query.answer("ℹ️ No stats yet!", show_alert=True)
        user.setdefault("number", {"played": 0, "wins": 0, "losses": 0})
        n = user["number"]
        text = (
            f"📊 **Number Guess Stats**\n"
            f"💎 Gems: {user['gems']}\n"
            f"🎮 Games Played: {n['played']}\n"
            f"✅ Wins: {n['wins']}\n"
            f"😢 Losses: {n['losses']}"
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "menu_stats"))]
        ]))
    elif action == "menu_sps":
        user = db.get(User.id == user_id)
        gems = user["gems"] if user else 100
        await query.message.edit_text(
            f"🪨 **Stone-Paper-Scissors** (Cost: 20 💎)\n💎 Gems: {gems}\nChoose your move:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🪨", callback_data=generate_user_specific_data(user_id, "bot_Stone")),
                    InlineKeyboardButton("📄", callback_data=generate_user_specific_data(user_id, "bot_Paper")),
                    InlineKeyboardButton("✂️", callback_data=generate_user_specific_data(user_id, "bot_Scissors"))
                ],
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_mines":
        if user_id in mines_games:
            return await query.answer("⚠️ Finish your current Mines game!", show_alert=True)
        user = db.get(User.id == user_id)
        gems = user["gems"] if user else 100
        await query.message.edit_text(
            f"🎯 **Mines** (Cost: 30 💎)\n💎 Gems: {gems}\nSelect number of mines (1-10):",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(str(i), callback_data=generate_user_specific_data(user_id, f"mines_select_{i}")) for i in range(1, 6)],
                [InlineKeyboardButton(str(i), callback_data=generate_user_specific_data(user_id, f"mines_select_{i}")) for i in range(6, 11)],
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_dice":
        if user_id in dice_games:
            return await query.answer("⚠️ Finish your current Dice game!", show_alert=True)
        user = db.get(User.id == user_id)
        gems = user["gems"] if user else 100
        await query.message.edit_text(
            f"🎲 **Dice Roll** (Cost: 25 💎)\n💎 Gems: {gems}\nPick a number (1-6):",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(str(i), callback_data=generate_user_specific_data(user_id, f"dice_select_{i}")) for i in range(1, 4)],
                [InlineKeyboardButton(str(i), callback_data=generate_user_specific_data(user_id, f"dice_select_{i}")) for i in range(4, 7)],
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_coin":
        if user_id in coin_games:
            return await query.answer("⚠️ Finish your current Coin Flip game!", show_alert=True)
        user = db.get(User.id == user_id)
        gems = user["gems"] if user else 100
        await query.message.edit_text(
            f"🪙 **Coin Flip** (Cost: 15 💎)\n💎 Gems: {gems}\nHeads or Tails?",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Heads", callback_data=generate_user_specific_data(user_id, "coin_heads")),
                    InlineKeyboardButton("Tails", callback_data=generate_user_specific_data(user_id, "coin_tails"))
                ],
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_slots":
        if user_id in slot_games:
            return await query.answer("⚠️ Finish your current Slots game!", show_alert=True)
        user = db.get(User.id == user_id)
        gems = user["gems"] if user else 100
        await query.message.edit_text(
            f"🎰 **Slot Machine** (Cost: 50 💎)\n💎 Gems: {gems}\nSpin the slots?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎰 Spin", callback_data=generate_user_specific_data(user_id, "slot_spin"))],
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_number":
        if user_id in number_games:
            return await query.answer("⚠️ Finish your current Number Guess game!", show_alert=True)
        user = db.get(User.id == user_id)
        gems = user["gems"] if user else 100
        await query.message.edit_text(
            f"🔢 **Number Guess** (Cost: 40 💎)\n💎 Gems: {gems}\nGuess a number (1-10):",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(str(i), callback_data=generate_user_specific_data(user_id, f"number_select_{i}")) for i in range(1, 6)],
                [InlineKeyboardButton(str(i), callback_data=generate_user_specific_data(user_id, f"number_select_{i}")) for i in range(6, 11)],
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_shop":
        user = db.get(User.id == user_id)
        gems = user["gems"] if user else 100
        exp = user["exp"] if user else 0
        await query.message.edit_text(
            f"💰 **Gem Shop**\n💎 Gems: {gems} | 🌟 EXP: {exp}\nBuy gems with EXP:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("50 💎 (100 EXP)", callback_data=generate_user_specific_data(user_id, "buy_gems_50")),
                    InlineKeyboardButton("100 💎 (180 EXP)", callback_data=generate_user_specific_data(user_id, "buy_gems_100"))
                ],
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_gift":
        await query.message.edit_text("🎁 Reply with /gift <amount> to send gems to another user!")
    elif action == "buy_gems_50":
        user = db.get(User.id == user_id)
        if not user or user["exp"] < 100:
            return await query.answer("⚠️ Need 100 EXP to buy 50 💎!", show_alert=True)
        user["exp"] -= 100
        user["gems"] += 50
        db.update(user, User.id == user_id)
        await query.message.edit_text(
            f"✅ Purchased 50 💎 for 100 EXP!\n💎 Gems: {user['gems']} | 🌟 EXP: {user['exp']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "menu_shop"))]
            ])
        )
    elif action == "buy_gems_100":
        user = db.get(User.id == user_id)
        if not user or user["exp"] < 180:
            return await query.answer("⚠️ Need 180 EXP to buy 100 💎!", show_alert=True)
        user["exp"] -= 180
        user["gems"] += 100
        db.update(user, User.id == user_id)
        await query.message.edit_text(
            f"✅ Purchased 100 💎 for 180 EXP!\n💎 Gems: {user['gems']} | 🌟 EXP: {user['exp']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "menu_shop"))]
            ])
        )
    elif action == "daily_gems":
        user = db.get(User.id == user_id)
        if not user:
            user = {"id": user_id, "gems": 100, "last_daily": 0}
            db.insert(user)
        current_time = int(time.time())
        if current_time - user["last_daily"] < 86400:
            return await query.answer("⚠️ Come back tomorrow for your daily gems!", show_alert=True)
        user["gems"] += 50
        user["last_daily"] = current_time
        db.update(user, User.id == user_id)
        await query.message.edit_text(
            f"🌟 Claimed 50 💎 daily reward!\n💎 Gems: {user['gems']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_leaderboard":
        users = sorted(db.all(), key=lambda x: x["gems"], reverse=True)[:5]
        text = "🏆 **Leaderboard (Top 5 by Gems)**\n\n"
        for i, user in enumerate(users, 1):
            username = (await app.get_users(user["id"])).first_name
            text += f"{i}. [{username}](tg://user?id={user['id']}): {user['gems']} 💎\n"
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "mines_select":
        user = db.get(User.id == user_id)
        if not user or user["gems"] < 30:
            return await query.message.edit_text("⚠️ Need 30 💎 to play Mines!")
        count = int(data[-3])
        mine_positions = random.sample([(r, c) for r in range(5) for c in range(5)], count)
        mines_games[user_id] = {"mines": mine_positions, "revealed": [], "count": count}
        user["mines"]["played"] += 1
        user["gems"] -= 30
        db.update(user, User.id == user_id)
        reply = await query.message.reply(
            f"💥 **Mines Game Started!**\n💎 Gems: {user['gems']}\n💣 Mines: {count}\nFind all safe tiles!",
            reply_markup=build_grid(user_id)
        )
        mines_games[user_id]["grid_msg"] = (reply.chat.id, reply.id)
        await query.message.delete()
    elif action == "mines_cell":
        if user_id not in mines_games:
            return await query.answer("❗ No active game!", show_alert=True)
        r, c = map(int, data[-4:-2])
        state = mines_games[user_id]
        if (r, c) in state["revealed"]:
            return await query.answer("⚠️ Already revealed!", show_alert=True)
        if (r, c) in state["mines"]:
            await query.message.edit_text("💥 **Boom!** You hit a mine!\nGame Over.")
            user = db.get(User.id == user_id)
            user["mines"]["losses"] += 1
            db.update(user, User.id == user_id)
            del mines_games[user_id]
            return
        state["revealed"].append((r, c))
        exp_gain, leveled_up, gems = update_stats(user_id, game="mines", gems=10)
        level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
        chat_id, msg_id = state["grid_msg"]
        await app.edit_message_reply_markup(chat_id, msg_id, reply_markup=build_grid(user_id))
        await query.answer(f"✅ Safe! +{exp_gain} EXP, +10 💎{level_text}", show_alert=True)
        if len(state["revealed"]) == 25 - state["count"]:
            gem_reward = state["count"] * 15
            exp_gain, leveled_up, gems = update_stats(user_id, game="mines", gems=gem_reward)
            await app.send_message(chat_id, f"🎉 **You won!** All safe tiles cleared!\n+{gem_reward} 💎, +{len(state['revealed'])*5} EXP")
            user = db.get(User.id == user_id)
            user["mines"]["wins"] += 1
            db.update(user, User.id == user_id)
            del mines_games[user_id]
    elif action == "dice_select":
        user = db.get(User.id == user_id)
        if not user or user["gems"] < 25:
            return await query.message.edit_text("⚠️ Need 25 💎 to play Dice!")
        choice = int(data[-3])
        bot_roll = random.randint(1, 6)
        user["gems"] -= 25
        result = "win" if choice == bot_roll else "lose"
        gem_reward = 50 if result == "win" else 0
        exp_gain, leveled_up, gems = update_stats(user_id, result, "dice", gem_reward)
        level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
        await query.message.edit_text(
            f"🎲 **Dice Roll**\nYou rolled: {choice}\n🤖 Bot rolled: {bot_roll}\n"
            f"{'🎉 You win!' if result == 'win' else '😢 You lose!'}\n"
            f"+{exp_gain} EXP, +{gem_reward} 💎\n💎 Gems: {gems}{level_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
        del dice_games[user_id]
    elif action == "coin":
        user = db.get(User.id == user_id)
        if not user or user["gems"] < 15:
            return await query.message.edit_text("⚠️ Need 15 💎 to play Coin Flip!")
        choice = data[-3].capitalize()
        bot_flip = random.choice(["Heads", "Tails"])
        user["gems"] -= 15
        result = "win" if choice == bot_flip else "lose"
        gem_reward = 30 if result == "win" else 0
        exp_gain, leveled_up, gems = update_stats(user_id, result, "coin", gem_reward)
        level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
        await query.message.edit_text(
            f"🪙 **Coin Flip**\nYou chose: {choice}\n🤖 Bot flipped: {bot_flip}\n"
            f"{'🎉 You win!' if result == 'win' else '😢 You lose!'}\n"
            f"+{exp_gain} EXP, +{gem_reward} 💎\n💎 Gems: {gems}{level_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
        del coin_games[user_id]
    elif action == "slot_spin":
        user = db.get(User.id == user_id)
        if not user or user["gems"] < 50:
            return await query.message.edit_text("⚠️ Need 50 💎 to play Slots!")
        user["gems"] -= 50
        slots = [random.choice(SLOTS) for _ in range(3)]
        result = "win" if len(set(slots)) == 1 else "lose"
        gem_reward = 150 if result == "win" else 0
        exp_gain, leveled_up, gems = update_stats(user_id, result, "slots", gem_reward)
        level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
        await query.message.edit_text(
            f"🎰 **Slot Machine**\nResult: {'|'.join(slots)}\n"
            f"{'🎉 Jackpot!' if result == 'win' else '😢 No luck!'}\n"
            f"+{exp_gain} EXP, +{gem_reward} 💎\n💎 Gems: {gems}{level_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
        del slot_games[user_id]
    elif action == "number_select":
        user = db.get(User.id == user_id)
        if not user or user["gems"] < 40:
            return await query.message.edit_text("⚠️ Need 40 💎 to play Number Guess!")
        choice = int(data[-3])
        bot_number = random.randint(1, 10)
        user["gems"] -= 40
        result = "win" if choice == bot_number else "lose"
        gem_reward = 100 if result == "win" else 0
        exp_gain, leveled_up, gems = update_stats(user_id, result, "number", gem_reward)
        level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
        await query.message.edit_text(
            f"🔢 **Number Guess**\nYou chose: {choice}\n🤖 Bot chose: {bot_number}\n"
            f"{'🎉 You win!' if result == 'win' else '😢 You lose!'}\n"
            f"+{exp_gain} EXP, +{gem_reward} 💎\n💎 Gems: {gems}{level_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
        del number_games[user_id]
    elif action == "bot":
        user = db.get(User.id == user_id)
        if not user or user["gems"] < 20:
            return await query.message.edit_text("⚠️ Need 20 💎 to play SPS!")
        move = data[-3]
        bot_move = random.choice(list(CHOICES.keys()))
        result = get_result(move, bot_move)
        gem_reward = 40 if result == "win" else 0
        user["gems"] -= 20
        exp_gain, leveled_up, gems = update_stats(user_id, result, "sps", gem_reward)
        level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
        await query.message.edit_text(
            f"🪨 **SPS**\nYou: {CHOICES[move]}\n🤖 Bot: {CHOICES[bot_move]}\n"
            f"{'🎉 You win!' if result == 'win' else '😢 You lose!' if result == 'lose' else '😐 Draw!'}\n"
            f"+{exp_gain} EXP, +{gem_reward} 💎\n💎 Gems: {gems}{level_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action.startswith("accept_"):
        opponent = int(data[-4])
        if user_id not in pending_pvps or pending_pvps[user_id] != opponent:
            return await query.answer("❗ No valid challenge!", show_alert=True)
        user = db.get(User.id == user_id)
        if not user or user["gems"] < 20:
            return await query.message.edit_text("⚠️ Need 20 💎 to accept!")
        pvp_moves[user_id] = None
        pvp_moves[opponent] = None
        await query.message.edit_text(
            f"👊 **PvP Accepted!**\n💎 Gems: {user['gems']}\nChoose your move:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🪨", callback_data=generate_user_specific_data(user_id, f"pvp_move_Stone_{opponent}")),
                    InlineKeyboardButton("📄", callback_data=generate_user_specific_data(user_id, f"pvp_move_Paper_{opponent}")),
                    InlineKeyboardButton("✂️", callback_data=generate_user_specific_data(user_id, f"pvp_move_Scissors_{opponent}"))
                ]
            ])
        )
        await app.send_message(
            opponent,
            f"✅ [{query.from_user.first_name}](tg://user?id={user_id}) accepted your challenge!\nChoose your move:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🪨", callback_data=generate_user_specific_data(opponent, f"pvp_move_Stone_{user_id}")),
                    InlineKeyboardButton("📄", callback_data=generate_user_specific_data(opponent, f"pvp_move_Paper_{user_id}")),
                    InlineKeyboardButton("✂️", callback_data=generate_user_specific_data(opponent, f"pvp_move_Scissors_{user_id}"))
                ]
            ])
        )
    elif action.startswith("pvp_move_"):
        move = data[-4]
        opponent = int(data[-3])
        if user_id not in pvp_moves or opponent not in pvp_moves:
            return await query.answer("❗ Invalid PvP session!", show_alert=True)
        pvp_moves[user_id] = move
        await query.message.edit_text("⏳ Waiting for opponent's move...")
        if pvp_moves[opponent]:
            user_move = pvp_moves[user_id]
            opponent_move = pvp_moves[opponent]
            result = get_result(user_move, opponent_move)
            user_gems = db.get(User.id == user_id)["gems"]
            opponent_gems = db.get(User.id == opponent)["gems"]
            gem_reward = 50 if result == "win" else 0
            exp_gain, leveled_up, gems = update_stats(user_id, result, "sps", gem_reward)
            level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
            opponent_result = "lose" if result == "win" else "win" if result == "lose" else "draw"
            opponent_gem_reward = 50 if opponent_result == "win" else 0
            opponent_exp_gain, opponent_leveled_up, opponent_gems = update_stats(opponent, opponent_result, "sps", opponent_gem_reward)
            opponent_level_text = "\n✨ Level Up! +100 💎" if opponent_leveled_up else ""
            await query.message.edit_text(
                f"👊 **PvP Result**\nYou: {CHOICES[user_move]}\nOpponent: {CHOICES[opponent_move]}\n"
                f"{'🎉 You win!' if result == 'win' else '😢 You lose!' if result == 'lose' else '😐 Draw!'}\n"
                f"+{exp_gain} EXP, +{gem_reward} 💎\n💎 Gems: {gems}{level_text}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
                ])
            )
            await app.send_message(
                pvp_chats[opponent],
                f"👊 **PvP Result**\nYou: {CHOICES[opponent_move]}\nOpponent: {CHOICES[user_move]}\n"
                f"{'🎉 You win!' if opponent_result == 'win' else '😢 You lose!' if opponent_result == 'lose' else '😐 Draw!'}\n"
                f"+{opponent_exp_gain} EXP, +{opponent_gem_reward} 💎\n💎 Gems: {opponent_gems}{opponent_level_text}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(opponent, "back_to_start"))]
                ])
            )
            del pvp_moves[user_id]
            del pvp_moves[opponent]
            del pending_pvps[user_id]
            del pvp_chats[opponent]
    elif action == "back_to_start":
        user = db.get(User.id == user_id)
        gems = user["gems"] if user else 100
        await query.message.edit_text(
            f"🎮 **Ultimate Game Arena** 💎\nWelcome, Champion! Gems: {gems}\nChoose your challenge:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🪨 SPS", callback_data=generate_user_specific_data(user_id, "menu_sps")),
                    InlineKeyboardButton("🎯 Mines", callback_data=generate_user_specific_data(user_id, "menu_mines"))
                ],
                [
                    InlineKeyboardButton("🎲 Dice", callback_data=generate_user_specific_data(user_id, "menu_dice")),
                    InlineKeyboardButton("🪙 Coin", callback_data=generate_user_specific_data(user_id, "menu_coin"))
                ],
                [
                    InlineKeyboardButton("🎰 Slots", callback_data=generate_user_specific_data(user_id, "menu_slots")),
                    InlineKeyboardButton("🔢 Number", callback_data=generate_user_specific_data(user_id, "menu_number"))
                ],
                [
                    InlineKeyboardButton("📊 Stats", callback_data=generate_user_specific_data(user_id, "menu_stats")),
                    InlineKeyboardButton("🏆 Leaderboard", callback_data=generate_user_specific_data(user_id, "menu_leaderboard"))
                ],
                [
                    InlineKeyboardButton("💰 Shop", callback_data=generate_user_specific_data(user_id, "menu_shop")),
                    InlineKeyboardButton("🎁 Gift Gems", callback_data=generate_user_specific_data(user_id, "menu_gift"))
                ],
                [InlineKeyboardButton("🌟 Daily Gems", callback_data=generate_user_specific_data(user_id, "daily_gems"))]
            ])
        )

def build_grid(user_id):
    buttons = []
    for r in range(5):
        row = []
        for c in range(5):
            text = "⬜️"
            if (r, c) in mines_games[user_id]["revealed"]:
                text = "✅"
            row.append(InlineKeyboardButton(text, callback_data=generate_user_specific_data(user_id, f"mines_cell_{r}_{c}")))
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)

def get_result(a, b):
    if a == b:
        return "draw"
    elif (a == "Stone" and b == "Scissors") or (a == "Paper" and b == "Stone") or (a == "Scissors" and b == "Paper"):
        return "win"
    return "lose"

app.run()
