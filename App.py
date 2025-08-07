from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from tinydb import TinyDB, Query
import random
import time
import uuid
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re
from collections import defaultdict
import math

API_ID = 21472111
API_HASH = "2a51fd4825b3b947c253f8f9b8f830f7"
BOT_TOKEN = "8246622394:AAEbHlAtOjM8PLnAJl-Qcbf8AV6p9AsSKV8"

app = Client("ultimate_game_arena", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db = TinyDB("game_users.json")
User = Query()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CHOICES = {"Stone": "🪨 Stone", "Paper": "📄 Paper", "Scissors": "✂️ Scissors"}
SLOTS = ["🍎", "🍋", "🍒", "💎", "🔔", "🍊", "🍇", "🍉", "🍓", "🍐"]
MINES_GRID_SIZE = 5
WHEEL_SEGMENTS = ["x0", "x1", "x2", "x5", "x10", "x20", "Jackpot"]
RPSLS_CHOICES = {"Rock": "🪨 Rock", "Paper": "📄 Paper", "Scissors": "✂️ Scissors", "Lizard": "🦎 Lizard", "Spock": "🖖 Spock"}
TICTACTOE_GRID = 3
BLACKJACK_CARDS = [f"{rank}{suit}" for rank in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"] for suit in ["♠", "♥", "♦", "♣"]]
HANGMAN_WORDS = ["PYTHON", "CODING", "GAMING", "ROBOT", "ALGORITHM", "DATABASE", "NETWORK", "PROGRAMMING", "DEVELOPER", "SOFTWARE"]
HANGMAN_ATTEMPTS = 6
MEMORY_PAIRS = ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼"]

pending_pvps = {}
pvp_moves = {}
pvp_chats = {}
mines_games = {}
dice_games = {}
coin_games = {}
slot_games = {}
number_games = {}
wheel_games = {}
rpsls_games = {}
tictactoe_games = {}
blackjack_games = {}
hangman_games = {}
memory_games = {}
active_games = defaultdict(list)
user_sessions = {}
leaderboard_cache = {}
achievement_cache = {}

def initialize_user_data(uid: int) -> Dict:
    user = db.get(User.id == uid)
    if not user:
        user = {
            "id": uid,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "exp": 0,
            "level": 1,
            "gems": 100,
            "last_daily": 0,
            "last_hourly": 0,
            "streak": 0,
            "achievements": [],
            "sps": {"played": 0, "wins": 0, "losses": 0, "draws": 0},
            "mines": {"played": 0, "wins": 0, "losses": 0, "safe_reveals": 0},
            "dice": {"played": 0, "wins": 0, "losses": 0},
            "coin": {"played": 0, "wins": 0, "losses": 0},
            "slots": {"played": 0, "wins": 0, "losses": 0},
            "number": {"played": 0, "wins": 0, "losses": 0},
            "wheel": {"played": 0, "wins": 0, "losses": 0},
            "rpsls": {"played": 0, "wins": 0, "losses": 0, "draws": 0},
            "tictactoe": {"played": 0, "wins": 0, "losses": 0, "draws": 0},
            "blackjack": {"played": 0, "wins": 0, "losses": 0, "draws": 0},
            "hangman": {"played": 0, "wins": 0, "losses": 0},
            "memory": {"played": 0, "wins": 0, "losses": 0}
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
        user.setdefault("last_hourly", 0)
        user.setdefault("streak", 0)
        user.setdefault("achievements", [])
        user.setdefault("sps", {"played": 0, "wins": 0, "losses": 0, "draws": 0})
        user.setdefault("mines", {"played": 0, "wins": 0, "losses": 0, "safe_reveals": 0})
        user.setdefault("dice", {"played": 0, "wins": 0, "losses": 0})
        user.setdefault("coin", {"played": 0, "wins": 0, "losses": 0})
        user.setdefault("slots", {"played": 0, "wins": 0, "losses": 0})
        user.setdefault("number", {"played": 0, "wins": 0, "losses": 0})
        user.setdefault("wheel", {"played": 0, "wins": 0, "losses": 0})
        user.setdefault("rpsls", {"played": 0, "wins": 0, "losses": 0, "draws": 0})
        user.setdefault("tictactoe", {"played": 0, "wins": 0, "losses": 0, "draws": 0})
        user.setdefault("blackjack", {"played": 0, "wins": 0, "losses": 0, "draws": 0})
        user.setdefault("hangman", {"played": 0, "wins": 0, "losses": 0})
        user.setdefault("memory", {"played": 0, "wins": 0, "losses": 0})
    return user

def update_stats(uid: int, result: Optional[str] = None, game: str = "sps", gems: int = 0) -> Tuple[int, bool, int]:
    user = initialize_user_data(uid)
    exp_gain = 0
    gem_change = gems
    game_stats = user[game]
    
    if game == "sps":
        game_stats["played"] += 1
        if result == "win":
            user["wins"] += 1
            game_stats["wins"] += 1
            exp_gain = 15
            gem_change += 40
        elif result == "lose":
            user["losses"] += 1
            game_stats["losses"] += 1
            exp_gain = 5
        else:
            user["draws"] += 1
            game_stats["draws"] += 1
            exp_gain = 8
    elif game == "mines":
        game_stats["played"] += 1
        if result == "win":
            game_stats["wins"] += 1
            exp_gain = 20
            gem_change += 50
        elif result == "lose":
            game_stats["losses"] += 1
            exp_gain = 5
        game_stats["safe_reveals"] += 1
        exp_gain += 5
    elif game == "dice":
        game_stats["played"] += 1
        if result == "win":
            game_stats["wins"] += 1
            exp_gain = 12
            gem_change += 50
        else:
            game_stats["losses"] += 1
            exp_gain = 6
    elif game == "coin":
        game_stats["played"] += 1
        if result == "win":
            game_stats["wins"] += 1
            exp_gain = 10
            gem_change += 30
        else:
            game_stats["losses"] += 1
            exp_gain = 5
    elif game == "slots":
        game_stats["played"] += 1
        if result == "win":
            game_stats["wins"] += 1
            exp_gain = 20
            gem_change += 150
        else:
            game_stats["losses"] += 1
            exp_gain = 8
    elif game == "number":
        game_stats["played"] += 1
        if result == "win":
            game_stats["wins"] += 1
            exp_gain = 25
            gem_change += 100
        else:
            game_stats["losses"] += 1
            exp_gain = 10
    elif game == "wheel":
        game_stats["played"] += 1
        if result == "win":
            game_stats["wins"] += 1
            exp_gain = 30
            gem_change += 200
        else:
            game_stats["losses"] += 1
            exp_gain = 10
    elif game == "rpsls":
        game_stats["played"] += 1
        if result == "win":
            game_stats["wins"] += 1
            exp_gain = 18
            gem_change += 50
        elif result == "lose":
            game_stats["losses"] += 1
            exp_gain = 6
        else:
            game_stats["draws"] += 1
            exp_gain = 10
    elif game == "tictactoe":
        game_stats["played"] += 1
        if result == "win":
            game_stats["wins"] += 1
            exp_gain = 20
            gem_change += 60
        elif result == "lose":
            game_stats["losses"] += 1
            exp_gain = 8
        else:
            game_stats["draws"] += 1
            exp_gain = 12
    elif game == "blackjack":
        game_stats["played"] += 1
        if result == "win":
            game_stats["wins"] += 1
            exp_gain = 25
            gem_change += 80
        elif result == "lose":
            game_stats["losses"] += 1
            exp_gain = 10
        else:
            game_stats["draws"] += 1
            exp_gain = 15
    elif game == "hangman":
        game_stats["played"] += 1
        if result == "win":
            game_stats["wins"] += 1
            exp_gain = 22
            gem_change += 70
        else:
            game_stats["losses"] += 1
            exp_gain = 8
    elif game == "memory":
        game_stats["played"] += 1
        if result == "win":
            game_stats["wins"] += 1
            exp_gain = 20
            gem_change += 60
        else:
            game_stats["losses"] += 1
            exp_gain = 8

    user["exp"] += exp_gain
    user["gems"] += gem_change
    leveled_up = False
    while user["exp"] >= user["level"] * 50:
        user["exp"] -= user["level"] * 50
        user["level"] += 1
        user["gems"] += 100
        leveled_up = True
        check_achievements(uid, user)
    
    user["streak"] = user["streak"] + 1 if result == "win" else 0
    check_achievements(uid, user)
    db.update(user, User.id == uid)
    return exp_gain, leveled_up, user["gems"]

def check_achievements(uid: int, user: Dict) -> None:
    achievements = user["achievements"]
    total_wins = sum(user[game]["wins"] for game in ["sps", "mines", "dice", "coin", "slots", "number", "wheel", "rpsls", "tictactoe", "blackjack", "hangman", "memory"])
    
    if total_wins >= 10 and "novice" not in achievements:
        achievements.append("novice")
        user["gems"] += 50
    if total_wins >= 50 and "pro" not in achievements:
        achievements.append("pro")
        user["gems"] += 150
    if total_wins >= 100 and "master" not in achievements:
        achievements.append("master")
        user["gems"] += 300
    if user["streak"] >= 5 and "streak_5" not in achievements:
        achievements.append("streak_5")
        user["gems"] += 100
    if user["level"] >= 10 and "level_10" not in achievements:
        achievements.append("level_10")
        user["gems"] += 200
    if user["gems"] >= 1000 and "rich" not in achievements:
        achievements.append("rich")
        user["gems"] += 500
    
    db.update({"achievements": achievements, "gems": user["gems"]}, User.id == uid)

def generate_user_specific_data(user_id: int, data: str) -> str:
    return f"{data}_{user_id}_{uuid.uuid4().hex[:8]}"

def get_sps_result(a: str, b: str) -> str:
    if a == b:
        return "draw"
    elif (a == "Stone" and b == "Scissors") or (a == "Paper" and b == "Stone") or (a == "Scissors" and b == "Paper"):
        return "win"
    return "lose"

def get_rpsls_result(a: str, b: str) -> str:
    if a == b:
        return "draw"
    winning_moves = {
        "Rock": ["Scissors", "Lizard"],
        "Paper": ["Rock", "Spock"],
        "Scissors": ["Paper", "Lizard"],
        "Lizard": ["Paper", "Spock"],
        "Spock": ["Rock", "Scissors"]
    }
    return "win" if b in winning_moves[a] else "lose"

def build_mines_grid(user_id: int) -> InlineKeyboardMarkup:
    buttons = []
    for r in range(MINES_GRID_SIZE):
        row = []
        for c in range(MINES_GRID_SIZE):
            text = "⬜️"
            if (r, c) in mines_games[user_id]["revealed"]:
                text = "✅"
            row.append(InlineKeyboardButton(text, callback_data=generate_user_specific_data(user_id, f"mines_cell_{r}_{c}")))
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))])
    return InlineKeyboardMarkup(buttons)

def build_tictactoe_grid(user_id: int) -> InlineKeyboardMarkup:
    buttons = []
    grid = tictactoe_games[user_id]["grid"]
    for r in range(TICTACTOE_GRID):
        row = []
        for c in range(TICTACTOE_GRID):
            text = grid[r][c] if grid[r][c] else "⬜️"
            row.append(InlineKeyboardButton(text, callback_data=generate_user_specific_data(user_id, f"tictactoe_move_{r}_{c}")))
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))])
    return InlineKeyboardMarkup(buttons)

def build_memory_grid(user_id: int) -> InlineKeyboardMarkup:
    buttons = []
    grid = memory_games[user_id]["grid"]
    revealed = memory_games[user_id]["revealed"]
    for r in range(4):
        row = []
        for c in range(4):
            text = grid[r][c] if (r, c) in revealed else "⬜️"
            row.append(InlineKeyboardButton(text, callback_data=generate_user_specific_data(user_id, f"memory_cell_{r}_{c}")))
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))])
    return InlineKeyboardMarkup(buttons)

def check_tictactoe_win(grid: List[List[str]], player: str) -> bool:
    for i in range(TICTACTOE_GRID):
        if all(grid[i][j] == player for j in range(TICTACTOE_GRID)) or all(grid[j][i] == player for j in range(TICTACTOE_GRID)):
            return True
    if all(grid[i][i] == player for i in range(TICTACTOE_GRID)) or all(grid[i][TICTACTOE_GRID-1-i] == player for i in range(TICTACTOE_GRID)):
        return True
    return False

def get_blackjack_value(cards: List[str]) -> int:
    value = 0
    aces = 0
    for card in cards:
        rank = card[:-1]
        if rank in ["J", "Q", "K"]:
            value += 10
        elif rank == "A":
            aces += 1
        else:
            value += int(rank)
    for _ in range(aces):
        if value + 11 <= 21:
            value += 11
        else:
            value += 1
    return value

async def update_leaderboard() -> None:
    global leaderboard_cache
    users = sorted(db.all(), key=lambda x: x["gems"], reverse=True)[:10]
    leaderboard_cache = {user["id"]: {"gems": user["gems"], "level": user["level"]} for user in users}

@app.on_message(filters.command("start"))
async def start_game(_, msg: Message):
    user_id = msg.from_user.id
    user = initialize_user_data(user_id)
    await msg.reply(
        f"🎮 **Ultimate Game Arena** 💎\nWelcome, Champion! 💎 Gems: {user['gems']} | 🌟 Level: {user['level']}\nChoose your challenge:",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🪨 SPS", callback_data=generate_user_specific_data(user_id, "menu_sps")),
                InlineKeyboardButton("🎯 Mines", callback_data=generate_user_specific_data(user_id, "menu_mines")),
                InlineKeyboardButton("🎲 Dice", callback_data=generate_user_specific_data(user_id, "menu_dice"))
            ],
            [
                InlineKeyboardButton("🪙 Coin", callback_data=generate_user_specific_data(user_id, "menu_coin")),
                InlineKeyboardButton("🎰 Slots", callback_data=generate_user_specific_data(user_id, "menu_slots")),
                InlineKeyboardButton("🔢 Number", callback_data=generate_user_specific_data(user_id, "menu_number"))
            ],
            [
                InlineKeyboardButton("🎡 Wheel", callback_data=generate_user_specific_data(user_id, "menu_wheel")),
                InlineKeyboardButton("🦎 RPSLS", callback_data=generate_user_specific_data(user_id, "menu_rpsls")),
                InlineKeyboardButton("⭕ Tic-Tac-Toe", callback_data=generate_user_specific_data(user_id, "menu_tictactoe"))
            ],
            [
                InlineKeyboardButton("🃏 Blackjack", callback_data=generate_user_specific_data(user_id, "menu_blackjack")),
                InlineKeyboardButton("🔤 Hangman", callback_data=generate_user_specific_data(user_id, "menu_hangman")),
                InlineKeyboardButton("🧠 Memory", callback_data=generate_user_specific_data(user_id, "menu_memory"))
            ],
            [
                InlineKeyboardButton("📊 Stats", callback_data=generate_user_specific_data(user_id, "menu_stats")),
                InlineKeyboardButton("🏆 Leaderboard", callback_data=generate_user_specific_data(user_id, "menu_leaderboard")),
                InlineKeyboardButton("🏅 Achievements", callback_data=generate_user_specific_data(user_id, "menu_achievements"))
            ],
            [
                InlineKeyboardButton("💰 Shop", callback_data=generate_user_specific_data(user_id, "menu_shop")),
                InlineKeyboardButton("🎁 Gift Gems", callback_data=generate_user_specific_data(user_id, "menu_gift")),
                InlineKeyboardButton("🌟 Daily Gems", callback_data=generate_user_specific_data(user_id, "daily_gems"))
            ],
            [InlineKeyboardButton("🕒 Hourly Bonus", callback_data=generate_user_specific_data(user_id, "hourly_bonus"))]
        ])
    )

@app.on_message(filters.command("pvp"))
async def pvp_challenge(_, msg: Message):
    if not msg.reply_to_message:
        return await msg.reply("⚠️ Reply to a user to challenge them!")
    challenger = msg.from_user.id
    user = initialize_user_data(challenger)
    if user["gems"] < 20:
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
            [InlineKeyboardButton("✅ Accept", callback_data=generate_user_specific_data(opponent, f"accept_sps_{challenger}"))]
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
    user = initialize_user_data(sender)
    if user["gems"] < amount:
        return await msg.reply("⚠️ Not enough gems!")
    user["gems"] -= amount
    db.update(user, User.id == sender)
    receiver_user = initialize_user_data(receiver)
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
                InlineKeyboardButton("🎯 Mines", callback_data=generate_user_specific_data(user_id, "show_mines_stats")),
                InlineKeyboardButton("🎲 Dice", callback_data=generate_user_specific_data(user_id, "show_dice_stats"))
            ],
            [
                InlineKeyboardButton("🪙 Coin", callback_data=generate_user_specific_data(user_id, "show_coin_stats")),
                InlineKeyboardButton("🎰 Slots", callback_data=generate_user_specific_data(user_id, "show_slots_stats")),
                InlineKeyboardButton("🔢 Number", callback_data=generate_user_specific_data(user_id, "show_number_stats"))
            ],
            [
                InlineKeyboardButton("🎡 Wheel", callback_data=generate_user_specific_data(user_id, "show_wheel_stats")),
                InlineKeyboardButton("🦎 RPSLS", callback_data=generate_user_specific_data(user_id, "show_rpsls_stats")),
                InlineKeyboardButton("⭕ Tic-Tac-Toe", callback_data=generate_user_specific_data(user_id, "show_tictactoe_stats"))
            ],
            [
                InlineKeyboardButton("🃏 Blackjack", callback_data=generate_user_specific_data(user_id, "show_blackjack_stats")),
                InlineKeyboardButton("🔤 Hangman", callback_data=generate_user_specific_data(user_id, "show_hangman_stats")),
                InlineKeyboardButton("🧠 Memory", callback_data=generate_user_specific_data(user_id, "show_memory_stats"))
            ],
            [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
        ])
    )

@app.on_message(filters.command("help"))
async def help_command(_, msg: Message):
    help_text = (
        "🎮 **Ultimate Game Arena Help** 🎮\n\n"
        "Welcome to the Ultimate Game Arena! Here are the available commands and games:\n\n"
        "**Commands:**\n"
        "- /start: Launch the main menu to choose games and other options.\n"
        "- /pvp: Challenge another user to a Stone-Paper-Scissors match (Reply to a user).\n"
        "- /gift <amount>: Gift gems to another user (Reply to a user).\n"
        "- /stats: View your game statistics.\n"
        "- /help: Display this help message.\n\n"
        "**Games:**\n"
        "- 🪨 **Stone-Paper-Scissors (SPS)**: Classic game, 20 💎 to play, 40 💎 reward for winning.\n"
        "- 🎯 **Mines**: Avoid mines on a 5x5 grid, 30 💎 to play, rewards based on safe tiles.\n"
        "- 🎲 **Dice Roll**: Pick a number (1-6), 25 💎 to play, 50 💎 reward for winning.\n"
        "- 🪙 **Coin Flip**: Choose Heads or Tails, 15 💎 to play, 30 💎 reward for winning.\n"
        "- 🎰 **Slots**: Spin for a jackpot, 50 💎 to play, 150 💎 reward for winning.\n"
        "- 🔢 **Number Guess**: Guess a number (1-10), 40 💎 to play, 100 💎 reward for winning.\n"
        "- 🎡 **Wheel of Fortune**: Spin the wheel, 60 💎 to play, up to 200 💎 reward.\n"
        "- 🦎 **RPSLS**: Rock-Paper-Scissors-Lizard-Spock, 25 💎 to play, 50 💎 reward for winning.\n"
        "- ⭕ **Tic-Tac-Toe**: Play against the bot, 30 💎 to play, 60 💎 reward for winning.\n"
        "- 🃏 **Blackjack**: Try to get 21, 40 💎 to play, 80 💎 reward for winning.\n"
        "- 🔤 **Hangman**: Guess the word, 35 💎 to play, 70 💎 reward for winning.\n"
        "- 🧠 **Memory**: Match pairs, 30 💎 to play, 60 💎 reward for winning.\n\n"
        "**Other Features:**\n"
        "- 💰 **Shop**: Buy gems with EXP.\n"
        "- 🏆 **Leaderboard**: View top players by gems.\n"
        "- 🏅 **Achievements**: Earn rewards for milestones.\n"
        "- 🌟 **Daily Gems**: Claim 50 💎 every 24 hours.\n"
        "- 🕒 **Hourly Bonus**: Claim 10 💎 every hour.\n\n"
        "Have fun and good luck, Champion! 🚀"
    )
    await msg.reply(help_text)

@app.on_callback_query()
async def callback_handler(_, query: CallbackQuery):
    user_id = query.from_user.id
    data = query.data.split("_")
    if len(data) < 3 or data[-2] != str(user_id):
        return await query.answer("❌ This button isn't for you!", show_alert=True)
    action = "_".join(data[:-2])
    user = initialize_user_data(user_id)

    if action == "menu_stats":
        await query.message.edit_text(
            "📊 Select a game to view stats:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🪨 SPS", callback_data=generate_user_specific_data(user_id, "show_sps_stats")),
                    InlineKeyboardButton("🎯 Mines", callback_data=generate_user_specific_data(user_id, "show_mines_stats")),
                    InlineKeyboardButton("🎲 Dice", callback_data=generate_user_specific_data(user_id, "show_dice_stats"))
                ],
                [
                    InlineKeyboardButton("🪙 Coin", callback_data=generate_user_specific_data(user_id, "show_coin_stats")),
                    InlineKeyboardButton("🎰 Slots", callback_data=generate_user_specific_data(user_id, "show_slots_stats")),
                    InlineKeyboardButton("🔢 Number", callback_data=generate_user_specific_data(user_id, "show_number_stats"))
                ],
                [
                    InlineKeyboardButton("🎡 Wheel", callback_data=generate_user_specific_data(user_id, "show_wheel_stats")),
                    InlineKeyboardButton("🦎 RPSLS", callback_data=generate_user_specific_data(user_id, "show_rpsls_stats")),
                    InlineKeyboardButton("⭕ Tic-Tac-Toe", callback_data=generate_user_specific_data(user_id, "show_tictactoe_stats"))
                ],
                [
                    InlineKeyboardButton("🃏 Blackjack", callback_data=generate_user_specific_data(user_id, "show_blackjack_stats")),
                    InlineKeyboardButton("🔤 Hangman", callback_data=generate_user_specific_data(user_id, "show_hangman_stats")),
                    InlineKeyboardButton("🧠 Memory", callback_data=generate_user_specific_data(user_id, "show_memory_stats"))
                ],
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "show_sps_stats":
        text = (
            f"📊 **SPS Stats**\n"
            f"🏅 Level: {user['level']}\n"
            f"🌟 EXP: {user['exp']}/{user['level']*50}\n"
            f"💎 Gems: {user['gems']}\n"
            f"🎮 Games Played: {user['sps']['played']}\n"
            f"🏆 Wins: {user['sps']['wins']}\n"
            f"😢 Losses: {user['sps']['losses']}\n"
            f"😐 Draws: {user['sps']['draws']}"
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "menu_stats"))]
        ]))
    elif action == "show_mines_stats":
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
    elif action == "show_wheel_stats":
        w = user["wheel"]
        text = (
            f"📊 **Wheel of Fortune Stats**\n"
            f"💎 Gems: {user['gems']}\n"
            f"🎮 Games Played: {w['played']}\n"
            f"✅ Wins: {w['wins']}\n"
            f"😢 Losses: {w['losses']}"
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "menu_stats"))]
        ]))
    elif action == "show_rpsls_stats":
        r = user["rpsls"]
        text = (
            f"📊 **RPSLS Stats**\n"
            f"💎 Gems: {user['gems']}\n"
            f"🎮 Games Played: {r['played']}\n"
            f"✅ Wins: {r['wins']}\n"
            f"😢 Losses: {r['losses']}\n"
            f"😐 Draws: {r['draws']}"
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "menu_stats"))]
        ]))
    elif action == "show_tictactoe_stats":
        t = user["tictactoe"]
        text = (
            f"📊 **Tic-Tac-Toe Stats**\n"
            f"💎 Gems: {user['gems']}\n"
            f"🎮 Games Played: {t['played']}\n"
            f"✅ Wins: {t['wins']}\n"
            f"😢 Losses: {t['losses']}\n"
            f"😐 Draws: {t['draws']}"
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "menu_stats"))]
        ]))
    elif action == "show_blackjack_stats":
        b = user["blackjack"]
        text = (
            f"📊 **Blackjack Stats**\n"
            f"💎 Gems: {user['gems']}\n"
            f"🎮 Games Played: {b['played']}\n"
            f"✅ Wins: {b['wins']}\n"
            f"😢 Losses: {b['losses']}\n"
            f"😐 Draws: {b['draws']}"
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "menu_stats"))]
        ]))
    elif action == "show_hangman_stats":
        h = user["hangman"]
        text = (
            f"📊 **Hangman Stats**\n"
            f"💎 Gems: {user['gems']}\n"
            f"🎮 Games Played: {h['played']}\n"
            f"✅ Wins: {h['wins']}\n"
            f"😢 Losses: {h['losses']}"
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "menu_stats"))]
        ]))
    elif action == "show_memory_stats":
        m = user["memory"]
        text = (
            f"📊 **Memory Stats**\n"
            f"💎 Gems: {user['gems']}\n"
            f"🎮 Games Played: {m['played']}\n"
            f"✅ Wins: {m['wins']}\n"
            f"😢 Losses: {m['losses']}"
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "menu_stats"))]
        ]))
    elif action == "menu_sps":
        if user_id in active_games:
            return await query.answer("⚠️ Finish your current game first!", show_alert=True)
        active_games[user_id].append("sps")
        await query.message.edit_text(
            f"🪨 **Stone-Paper-Scissors** (Cost: 20 💎)\n💎 Gems: {user['gems']}\nChoose your move:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🪨", callback_data=generate_user_specific_data(user_id, "bot_sps_Stone")),
                    InlineKeyboardButton("📄", callback_data=generate_user_specific_data(user_id, "bot_sps_Paper")),
                    InlineKeyboardButton("✂️", callback_data=generate_user_specific_data(user_id, "bot_sps_Scissors"))
                ],
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_mines":
        if user_id in active_games:
            return await query.answer("⚠️ Finish your current game first!", show_alert=True)
        active_games[user_id].append("mines")
        await query.message.edit_text(
            f"🎯 **Mines** (Cost: 30 💎)\n💎 Gems: {user['gems']}\nSelect number of mines (1-10):",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(str(i), callback_data=generate_user_specific_data(user_id, f"mines_select_{i}")) for i in range(1, 6)],
                [InlineKeyboardButton(str(i), callback_data=generate_user_specific_data(user_id, f"mines_select_{i}")) for i in range(6, 11)],
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_dice":
        if user_id in active_games:
            return await query.answer("⚠️ Finish your current game first!", show_alert=True)
        active_games[user_id].append("dice")
        await query.message.edit_text(
            f"🎲 **Dice Roll** (Cost: 25 💎)\n💎 Gems: {user['gems']}\nPick a number (1-6):",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(str(i), callback_data=generate_user_specific_data(user_id, f"dice_select_{i}")) for i in range(1, 4)],
                [InlineKeyboardButton(str(i), callback_data=generate_user_specific_data(user_id, f"dice_select_{i}")) for i in range(4, 7)],
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_coin":
        if user_id in active_games:
            return await query.answer("⚠️ Finish your current game first!", show_alert=True)
        active_games[user_id].append("coin")
        await query.message.edit_text(
            f"🪙 **Coin Flip** (Cost: 15 💎)\n💎 Gems: {user['gems']}\nHeads or Tails?",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Heads", callback_data=generate_user_specific_data(user_id, "coin_heads")),
                    InlineKeyboardButton("Tails", callback_data=generate_user_specific_data(user_id, "coin_tails"))
                ],
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_slots":
        if user_id in active_games:
            return await query.answer("⚠️ Finish your current game first!", show_alert=True)
        active_games[user_id].append("slots")
        await query.message.edit_text(
            f"🎰 **Slot Machine** (Cost: 50 💎)\n💎 Gems: {user['gems']}\nSpin the slots?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎰 Spin", callback_data=generate_user_specific_data(user_id, "slot_spin"))],
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_number":
        if user_id in active_games:
            return await query.answer("⚠️ Finish your current game first!", show_alert=True)
        active_games[user_id].append("number")
        await query.message.edit_text(
            f"🔢 **Number Guess** (Cost: 40 💎)\n💎 Gems: {user['gems']}\nGuess a number (1-10):",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(str(i), callback_data=generate_user_specific_data(user_id, f"number_select_{i}")) for i in range(1, 6)],
                [InlineKeyboardButton(str(i), callback_data=generate_user_specific_data(user_id, f"number_select_{i}")) for i in range(6, 11)],
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_wheel":
        if user_id in active_games:
            return await query.answer("⚠️ Finish your current game first!", show_alert=True)
        active_games[user_id].append("wheel")
        await query.message.edit_text(
            f"🎡 **Wheel of Fortune** (Cost: 60 💎)\n💎 Gems: {user['gems']}\nSpin the wheel?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎡 Spin", callback_data=generate_user_specific_data(user_id, "wheel_spin"))],
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_rpsls":
        if user_id in active_games:
            return await query.answer("⚠️ Finish your current game first!", show_alert=True)
        active_games[user_id].append("rpsls")
        await query.message.edit_text(
            f"🦎 **RPSLS** (Cost: 25 💎)\n💎 Gems: {user['gems']}\nChoose your move:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🪨", callback_data=generate_user_specific_data(user_id, "bot_rpsls_Rock")),
                    InlineKeyboardButton("📄", callback_data=generate_user_specific_data(user_id, "bot_rpsls_Paper")),
                    InlineKeyboardButton("✂️", callback_data=generate_user_specific_data(user_id, "bot_rpsls_Scissors"))
                ],
                [
                    InlineKeyboardButton("🦎", callback_data=generate_user_specific_data(user_id, "bot_rpsls_Lizard")),
                    InlineKeyboardButton("🖖", callback_data=generate_user_specific_data(user_id, "bot_rpsls_Spock"))
                ],
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_tictactoe":
        if user_id in active_games:
            return await query.answer("⚠️ Finish your current game first!", show_alert=True)
        active_games[user_id].append("tictactoe")
        tictactoe_games[user_id] = {
            "grid": [["" for _ in range(TICTACTOE_GRID)] for _ in range(TICTACTOE_GRID)],
            "player": "X",
            "bot": "O",
            "turn": "player"
        }
        user["gems"] -= 30
        db.update(user, User.id == user_id)
        reply = await query.message.reply(
            f"⭕ **Tic-Tac-Toe** (Cost: 30 💎)\n💎 Gems: {user['gems']}\nYour turn (X):",
            reply_markup=build_tictactoe_grid(user_id)
        )
        tictactoe_games[user_id]["grid_msg"] = (reply.chat.id, reply.id)
        await query.message.delete()
    elif action == "menu_blackjack":
        if user_id in active_games:
            return await query.answer("⚠️ Finish your current game first!", show_alert=True)
        active_games[user_id].append("blackjack")
        user["gems"] -= 40
        db.update(user, User.id == user_id)
        blackjack_games[user_id] = {
            "player_cards": [random.choice(BLACKJACK_CARDS), random.choice(BLACKJACK_CARDS)],
            "bot_cards": [random.choice(BLACKJACK_CARDS), random.choice(BLACKJACK_CARDS)],
            "status": "playing"
        }
        player_value = get_blackjack_value(blackjack_games[user_id]["player_cards"])
        bot_visible = blackjack_games[user_id]["bot_cards"][0]
        await query.message.edit_text(
            f"🃏 **Blackjack** (Cost: 40 💎)\n💎 Gems: {user['gems']}\nYour cards: {' '.join(blackjack_games[user_id]['player_cards'])} ({player_value})\nDealer's card: {bot_visible}\nHit or Stand?",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Hit", callback_data=generate_user_specific_data(user_id, "blackjack_hit")),
                    InlineKeyboardButton("Stand", callback_data=generate_user_specific_data(user_id, "blackjack_stand"))
                ],
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_hangman":
        if user_id in active_games:
            return await query.answer("⚠️ Finish your current game first!", show_alert=True)
        active_games[user_id].append("hangman")
        word = random.choice(HANGMAN_WORDS)
        hangman_games[user_id] = {
            "word": word,
            "guessed": set(),
            "attempts": HANGMAN_ATTEMPTS,
            "revealed": ["_" if c.isalpha() else c for c in word]
        }
        user["gems"] -= 35
        db.update(user, User.id == user_id)
        await query.message.edit_text(
            f"🔤 **Hangman** (Cost: 35 💎)\n💎 Gems: {user['gems']}\nWord: {' '.join(hangman_games[user_id]['revealed'])}\nAttempts left: {HANGMAN_ATTEMPTS}\nChoose a letter:",
            reply_markup=build_hangman_keyboard(user_id)
        )
    elif action == "menu_memory":
        if user_id in active_games:
            return await query.answer("⚠️ Finish your current game first!", show_alert=True)
        active_games[user_id].append("memory")
        pairs = MEMORY_PAIRS * 2
        random.shuffle(pairs)
        grid = [[pairs[i*4+j] for j in range(4)] for i in range(4)]
        memory_games[user_id] = {
            "grid": grid,
            "revealed": [],
            "matched": [],
            "last_pick": None
        }
        user["gems"] -= 30
        db.update(user, User.id == user_id)
        reply = await query.message.reply(
            f"🧠 **Memory Match** (Cost: 30 💎)\n💎 Gems: {user['gems']}\nMatch all pairs!",
            reply_markup=build_memory_grid(user_id)
        )
        memory_games[user_id]["grid_msg"] = (reply.chat.id, reply.id)
        await query.message.delete()
    elif action == "menu_shop":
        await query.message.edit_text(
            f"💰 **Gem Shop**\n💎 Gems: {user['gems']} | 🌟 EXP: {user['exp']}\nBuy gems with EXP:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("50 💎 (100 EXP)", callback_data=generate_user_specific_data(user_id, "buy_gems_50")),
                    InlineKeyboardButton("100 💎 (180 EXP)", callback_data=generate_user_specific_data(user_id, "buy_gems_100")),
                    InlineKeyboardButton("200 💎 (350 EXP)", callback_data=generate_user_specific_data(user_id, "buy_gems_200"))
                ],
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_gift":
        await query.message.edit_text("🎁 Reply with /gift <amount> to send gems to another user!")
    elif action == "menu_achievements":
        achievements = user["achievements"]
        text = "🏅 **Achievements**\n\n"
        achievement_list = [
            ("novice", "Novice: Win 10 games", 50),
            ("pro", "Pro: Win 50 games", 150),
            ("master", "Master: Win 100 games", 300),
            ("streak_5", "Streak: 5 wins in a row", 100),
            ("level_10", "Veteran: Reach level 10", 200),
            ("rich", "Tycoon: Collect 1000 gems", 500)
        ]
        for ach_id, desc, reward in achievement_list:
            status = "✅" if ach_id in achievements else "⬜️"
            text += f"{status} {desc} - {reward} 💎\n"
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "buy_gems_50":
        if user["exp"] < 100:
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
        if user["exp"] < 180:
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
    elif action == "buy_gems_200":
        if user["exp"] < 350:
            return await query.answer("⚠️ Need 350 EXP to buy 200 💎!", show_alert=True)
        user["exp"] -= 350
        user["gems"] += 200
        db.update(user, User.id == user_id)
        await query.message.edit_text(
            f"✅ Purchased 200 💎 for 350 EXP!\n💎 Gems: {user['gems']} | 🌟 EXP: {user['exp']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data=generate_user_specific_data(user_id, "menu_shop"))]
            ])
        )
    elif action == "daily_gems":
        current_time = int(time.time())
        if current_time - user["last_daily"] < 86400:
            return await query.answer("⚠️ Come back tomorrow for your daily gems!", show_alert=True)
        user["gems"] += 50
        user["last_daily"] = current_time
        db.update(user, User.id == user_id)
        await query.message.edit_text(
            f"🌟 Claimed 50 💎 daily reward!\n💎 Gems: {user['gems']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "hourly_bonus":
        current_time = int(time.time())
        if current_time - user["last_hourly"] < 3600:
            return await query.answer("⚠️ Come back in an hour for your bonus!", show_alert=True)
        user["gems"] += 10
        user["last_hourly"] = current_time
        db.update(user, User.id == user_id)
        await query.message.edit_text(
            f"🕒 Claimed 10 💎 hourly bonus!\n💎 Gems: {user['gems']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "menu_leaderboard":
        await update_leaderboard()
        text = "🏆 **Leaderboard (Top 10 by Gems)**\n\n"
        for i, (uid, data) in enumerate(leaderboard_cache.items(), 1):
            username = (await app.get_users(uid)).first_name
            text += f"{i}. [{username}](tg://user?id={uid}): {data['gems']} 💎 (Level {data['level']})\n"
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "mines_select":
        if user["gems"] < 30:
            return await query.message.edit_text("⚠️ Need 30 💎 to play Mines!")
        count = int(data[-3])
        mine_positions = random.sample([(r, c) for r in range(MINES_GRID_SIZE) for c in range(MINES_GRID_SIZE)], count)
        mines_games[user_id] = {"mines": mine_positions, "revealed": [], "count": count}
        user["gems"] -= 30
        db.update(user, User.id == user_id)
        reply = await query.message.reply(
            f"💥 **Mines Game Started!**\n💎 Gems: {user['gems']}\n💣 Mines: {count}\nFind all safe tiles!",
            reply_markup=build_mines_grid(user_id)
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
            exp_gain, leveled_up, gems = update_stats(user_id, "lose", "mines")
            level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
            await query.message.edit_text(
                f"💥 **Boom!** You hit a mine!\nGame Over.\n+{exp_gain} EXP\n💎 Gems: {gems}{level_text}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
                ])
            )
            active_games[user_id].remove("mines")
            del mines_games[user_id]
            return
        state["revealed"].append((r, c))
        exp_gain, leveled_up, gems = update_stats(user_id, game="mines", gems=10)
        level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
        chat_id, msg_id = state["grid_msg"]
        await app.edit_message_reply_markup(chat_id, msg_id, reply_markup=build_mines_grid(user_id))
        await query.answer(f"✅ Safe! +{exp_gain} EXP, +10 💎{level_text}", show_alert=True)
        if len(state["revealed"]) == 25 - state["count"]:
            gem_reward = state["count"] * 15
            exp_gain, leveled_up, gems = update_stats(user_id, "win", "mines", gem_reward)
            level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
            await app.send_message(chat_id, f"🎉 **You won!** All safe tiles cleared!\n+{gem_reward} 💎, +{exp_gain} EXP{level_text}")
            active_games[user_id].remove("mines")
            del mines_games[user_id]
    elif action == "dice_select":
        if user["gems"] < 25:
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
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
        active_games[user_id].remove("dice")
    elif action == "coin":
        if user["gems"] < 15:
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
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
        active_games[user_id].remove("coin")
    elif action == "slot_spin":
        if user["gems"] < 50:
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
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
        active_games[user_id].remove("slots")
    elif action == "number_select":
        if user["gems"] < 40:
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
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
        active_games[user_id].remove("number")
    elif action == "wheel_spin":
        if user["gems"] < 60:
            return await query.message.edit_text("⚠️ Need 60 💎 to play Wheel of Fortune!")
        user["gems"] -= 60
        result = random.choice(WHEEL_SEGMENTS)
        gem_reward = 200 if result == "Jackpot" else int(result[1:]) * 10 if result != "x0" else 0
        game_result = "win" if gem_reward > 0 else "lose"
        exp_gain, leveled_up, gems = update_stats(user_id, game_result, "wheel", gem_reward)
        level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
        await query.message.edit_text(
            f"🎡 **Wheel of Fortune**\nResult: {result}\n"
            f"{'🎉 You win!' if game_result == 'win' else '😢 No luck!'}\n"
            f"+{exp_gain} EXP, +{gem_reward} 💎\n💎 Gems: {gems}{level_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
        active_games[user_id].remove("wheel")
    elif action == "bot_sps":
        if user["gems"] < 20:
            return await query.message.edit_text("⚠️ Need 20 💎 to play SPS!")
        move = data[-3]
        bot_move = random.choice(list(CHOICES.keys()))
        result = get_sps_result(move, bot_move)
        user["gems"] -= 20
        gem_reward = 40 if result == "win" else 0
        exp_gain, leveled_up, gems = update_stats(user_id, result, "sps", gem_reward)
        level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
        await query.message.edit_text(
            f"🪨 **SPS**\nYou: {CHOICES[move]}\n🤖 Bot: {CHOICES[bot_move]}\n"
            f"{'🎉 You win!' if result == 'win' else '😢 You lose!' if result == 'lose' else '😐 Draw!'}\n"
            f"+{exp_gain} EXP, +{gem_reward} 💎\n💎 Gems: {gems}{level_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
        active_games[user_id].remove("sps")
    elif action == "bot_rpsls":
        if user["gems"] < 25:
            return await query.message.edit_text("⚠️ Need 25 💎 to play RPSLS!")
        move = data[-3]
        bot_move = random.choice(list(RPSLS_CHOICES.keys()))
        result = get_rpsls_result(move, bot_move)
        user["gems"] -= 25
        gem_reward = 50 if result == "win" else 0
        exp_gain, leveled_up, gems = update_stats(user_id, result, "rpsls", gem_reward)
        level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
        await query.message.edit_text(
            f"🦎 **RPSLS**\nYou: {RPSLS_CHOICES[move]}\n🤖 Bot: {RPSLS_CHOICES[bot_move]}\n"
            f"{'🎉 You win!' if result == 'win' else '😢 You lose!' if result == 'lose' else '😐 Draw!'}\n"
            f"+{exp_gain} EXP, +{gem_reward} 💎\n💎 Gems: {gems}{level_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
        active_games[user_id].remove("rpsls")
    elif action == "tictactoe_move":
        if user_id not in tictactoe_games:
            return await query.answer("❗ No active game!", show_alert=True)
        r, c = map(int, data[-4:-2])
        state = tictactoe_games[user_id]
        if state["grid"][r][c]:
            return await query.answer("⚠️ Cell already taken!", show_alert=True)
        state["grid"][r][c] = state["player"]
        if check_tictactoe_win(state["grid"], state["player"]):
            exp_gain, leveled_up, gems = update_stats(user_id, "win", "tictactoe", 60)
            level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
            await query.message.edit_text(
                f"⭕ **Tic-Tac-Toe**\n🎉 You win!\n+60 💎, +{exp_gain} EXP\n💎 Gems: {gems}{level_text}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
                ])
            )
            active_games[user_id].remove("tictactoe")
            del tictactoe_games[user_id]
            return
        if all(state["grid"][r][c] for r in range(TICTACTOE_GRID) for c in range(TICTACTOE_GRID)):
            exp_gain, leveled_up, gems = update_stats(user_id, "draw", "tictactoe")
            level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
            await query.message.edit_text(
                f"⭕ **Tic-Tac-Toe**\n😐 Draw!\n+{exp_gain} EXP\n💎 Gems: {gems}{level_text}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
                ])
            )
            active_games[user_id].remove("tictactoe")
            del tictactoe_games[user_id]
            return
        available = [(r, c) for r in range(TICTACTOE_GRID) for c in range(TICTACTOE_GRID) if not state["grid"][r][c]]
        if available:
            bot_r, bot_c = random.choice(available)
            state["grid"][bot_r][bot_c] = state["bot"]
            if check_tictactoe_win(state["grid"], state["bot"]):
                exp_gain, leveled_up, gems = update_stats(user_id, "lose", "tictactoe")
                level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
                await query.message.edit_text(
                    f"⭕ **Tic-Tac-Toe**\n😢 You lose!\n+{exp_gain} EXP\n💎 Gems: {gems}{level_text}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
                    ])
                )
                active_games[user_id].remove("tictactoe")
                del tictactoe_games[user_id]
                return
        chat_id, msg_id = state["grid_msg"]
        await app.edit_message_reply_markup(chat_id, msg_id, reply_markup=build_tictactoe_grid(user_id))
        await query.message.edit_text(
            f"⭕ **Tic-Tac-Toe**\nBot played. Your turn (X):",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "blackjack_hit":
        if user_id not in blackjack_games:
            return await query.answer("❗ No active game!", show_alert=True)
        state = blackjack_games[user_id]
        state["player_cards"].append(random.choice(BLACKJACK_CARDS))
        player_value = get_blackjack_value(state["player_cards"])
        if player_value > 21:
            exp_gain, leveled_up, gems = update_stats(user_id, "lose", "blackjack")
            level_text = "\n✨ Level Up! +100 💎" if leveled_up else ""
            await query.message.edit_text(
                f"🃏 **Blackjack**\nYour cards: {' '.join(state['player_cards'])} ({player_value})\n😢 Bust! You lose!\n+{exp_gain} EXP\n💎 Gems: {gems}{level_text}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
                ])
            )
            active_games[user_id].remove("blackjack")
            del blackjack_games[user_id]
            return
        await query.message.edit_text(
            f"🃏 **Blackjack**\nYour cards: {' '.join(state['player_cards'])} ({player_value})\nDealer's card: {state['bot_cards'][0]}\nHit or Stand?",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Hit", callback_data=generate_user_specific_data(user_id, "blackjack_hit")),
                    InlineKeyboardButton("Stand", callback_data=generate_user_specific_data(user_id, "blackjack_stand"))
                ],
                [InlineKeyboardButton("🏠 Home", callback_data=generate_user_specific_data(user_id, "back_to_start"))]
            ])
        )
    elif action == "blackjack_stand":
        if user_id not in blackjack_games:
            return await query.answer("❗ No active game!", show_alert=True)


app.run()
