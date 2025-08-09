#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import re      
import html
import time
import copy
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import *          # Handlers, Updater, etc.
from tinydb import TinyDB, Query    # Use explicit classes (best practice)

# Example TinyDB init (change path if needed)
db = TinyDB('db.json')
UserQuery = Query()

# Custom escape_markdown for Telegram Markdown V2
def escape_markdown(text):
    """
    Simple escape function for Telegram Markdown V2 special characters.
    Ensures user-generated text won't break your formatting.
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

# Global dict to store ongoing PvP battles per chat
pvp_battles = {}



BOT_TOKEN = os.getenv('BOT_TOKEN')
updater = Updater('8498367728:AAFkUKs6xAqGLoQXL0OKqRbZX7wK6pklE5A', use_context=True)
dispatcher = updater.dispatcher

db = TinyDB('players.json')
UserQuery = Query()
#init_user
def init_user(update, context):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    # Try to fetch user from DB
    user_info = db.get(UserQuery.user_id == user_id)

    # All user fields with their safe defaults
    defaults = {
        'user_id': user_id,
        'username': username,
        'level': 1,
        'xp': 0,
        'coins': 1000,
        'essences': 0,
        'moonshards': 0,
        'max_xp': 100,
        'battles_played': 0,
        'explores_won': 0,
        'explores_lost': 0,
        'explores_played': 0,
        'power': 50,
        'max_power': 50,
        'max_hp': 100,
        'hp': 100,
        'agility': 200,
        'max_agility': 200,
        'user_weapons': {},
        'equiped_weapon': None,
        'pvp_battles_won': 0,
        'pvp_battles_lost': 0,
        'pvp_battles_played': 0
    }

    updated = False
    if user_info is None:
        # User doesn't exist in db: create fresh one
        user_info = defaults.copy()
        db.insert(user_info)
    else:
        # Patch any missing fields for old users in DB
        for key, value in defaults.items():
            if key not in user_info:
                user_info[key] = value
                updated = True
        if updated:
            db.update(user_info, UserQuery.user_id == user_id)

    return user_info

        
    return user_info 
    context.user_data.update(user_info)

def add_field_to_all_users(field_name, default_value):
    for user in db.all():
        if field_name not in user:
            db.update({field_name: default_value}, UserQuery.user_id == user['user_id'])
 #monster_db       
add_field_to_all_users('magical_items',[])
add_field_to_all_users('explores_played',0)
monster_db = {
    'lasher': {
        'hp': 100, 'dmg': 100, 'agility': 300,
        'photo': "AgACAgUAAxkBAAINfmiV-8k3XKyDaBEh2IpWWyv-Pk0qAAKXxjEbdoyxVEdHn_YxLf4pAQADAgADeQADNgQ"
    },
    'slayer': {
        'hp': 80, 'dmg': 80, 'agility': 260,
        'photo': "AgACAgUAAxkBAAINf2iV-8kXZj7um1j_sZBco8BWji03AAKYxjEbdoyxVAxhQ1-X5-AhAQADAgADeQADNgQ"
    },
    'gloam': {
        'hp': 75, 'dmg': 95, 'agility': 210,
        'photo': "AgACAgUAAxkBAAINgGiV-8nQxkd2bUwJecopBB6iXYoDAAKZxjEbdoyxVLuVEDkg189iAQADAgADeQADNgQ"
    },
    'razorbeak': {
        'hp': 50, 'dmg': 90, 'agility': 240,
        'photo': "AgACAgUAAxkBAAINgWiV-8lElhjVKwPmCjVmh5lMg345AAKaxjEbdoyxVF1wBfcmGhN3AQADAgADeAADNgQ"
    },
    'blightborn': {
        'hp': 30, 'dmg': 40, 'agility': 100,
        'photo': "AgACAgUAAxkBAAINgmiV-8mSo4DBhhjPhGJXrQie0nJ8AAKbxjEbdoyxVPAm76E_YObYAQADAgADeQADNgQ"
    },
    'shadefang': {
        'hp': 40, 'dmg': 50, 'agility': 170,
        'photo': "AgACAgUAAxkBAAINg2iV-8l1BwvKyjCL4L7tKROpIMvqAAKexjEbdoyxVBvB4eUZo6KKAQADAgADeQADNgQ"
    },
    'duskmaw': {
        'hp': 60, 'dmg': 60, 'agility': 155,
        'photo': "AgACAgUAAxkBAAINhGiV-8kAAeytiXeU21wRv5xa_-n1HgACn8YxG3aMsVTgRAgO89dufgEAAwIAA3kAAzYE"
    },
    'hollowroot': {
        'hp': 65, 'dmg': 70, 'agility': 150,
        'photo': "AgACAgUAAxkBAAINhWiV-8nALq4cH4ltO8zZr1GKXogHAAKgxjEbdoyxVBPCqXnhr2k_AQADAgADeAADNgQ"
    },
    'vilethorn': {
        'hp': 70, 'dmg': 80, 'agility': 165,
        'photo': "AgACAgUAAxkBAAINhmiV-8lcxBmij39Ut0N7WbuICwbVAAKhxjEbdoyxVBTBrYof85srAQADAgADeQADNgQ"
    },
    'embergut': {
        'hp': 85, 'dmg': 75, 'agility': 175,
        'photo': "AgACAgUAAxkBAAINh2iV-8nOKrlknIfAgPeLpJyG5WQAA6TGMRt2jLFUjjODUhhGY9cBAAMCAAN5AAM2BA"
    },
    'doomcaller': {
        'hp': 90, 'dmg': 35, 'agility': 170,
        'photo': "AgACAgUAAxkBAAINiGiV-8nwXWbRGvL0Vln4fYZJxjVhAAKlxjEbdoyxVHP_wG3Tc-qwAQADAgADeQADNgQ"
    },
    'rotclaw': {
        'hp': 30, 'dmg': 20, 'agility': 135,
        'photo': "AgACAgUAAxkBAAINiWiV-8m_p_K_lyWFQUrxT_DAt55YAAKmxjEbdoyxVKBT_bN8PPphAQADAgADeAADNgQ"
    },
    'ashen_wyrm': {
        'hp': 95, 'dmg': 25, 'agility': 160,
        'photo': "AgACAgUAAxkBAAINimiV-8kobB-FsztMEEoLPXLIpuU_AAKnxjEbdoyxVC64FTmHN2xQAQADAgADeAADNgQ"
    },
    'blackvein': {
        'hp': 65, 'dmg': 35, 'agility': 130,
        'photo': "AgACAgUAAxkBAAINi2iV-8nxncjEJAYjHH-Srv1Eid0uAAKoxjEbdoyxVOWvG8_fEMOfAQADAgADeAADNgQ"
    },
    'soulgnaw': {
        'hp': 60, 'dmg': 30, 'agility': 125,
        'photo': "AgACAgUAAxkBAAINjGiV-8ndgtf5IKqnKgfCKm5f7w_nAAKpxjEbdoyxVFDClP7XytlEAQADAgADeQADNgQ"
    },
    'thornfiend': {
        'hp': 55, 'dmg': 65, 'agility': 145,
        'photo': "AgACAgUAAxkBAAINjWiV-8mdsoO7e6pCATXudUAYSn_lAAKqxjEbdoyxVHQiW9zfwJvYAQADAgADeAADNgQ"
    },
    'voidlurker': {
        'hp': 100, 'dmg': 110, 'agility': 195,
        'photo': "AgACAgUAAxkBAAINjmiV-8m9tSa6z9gr4yB9Xg92St_WAAKsxjEbdoyxVA7TtZyIF4GXAQADAgADeQADNgQ"
    },
    'nethermaw': {
        'hp': 120, 'dmg': 85, 'agility': 185,
        'photo': "AgACAgUAAxkBAAINj2iV-8kGpxysKWBZYJkAAVvuGt0qnQACrcYxG3aMsVSeRKlUTIREewEAAwIAA3gAAzYE"
    },
    'cragjaw': {
        'hp': 80, 'dmg': 45, 'agility': 115,
        'photo': "AgACAgUAAxkBAAINkGiV-8ntOsj6T6DG7IgUG5vGQ8MjAAKuxjEbdoyxVAE7aSVD2V2XAQADAgADeQADNgQ"
    },
    'stormhide': {
        'hp': 90, 'dmg': 95, 'agility': 200,
        'photo': "AgACAgUAAxkBAAINkWiV-8kLxR9TyhJJMovs7RVH9jKcAAKwxjEbdoyxVL6AgFWi5JSOAQADAgADeAADNgQ"
    },
    'skyripper': {
        'hp': 120, 'dmg': 60, 'agility': 200,
        'photo': "AgACAgUAAxkBAAINkmiV-8n5UCPhLD4VtOyhHyIm4FHjAAKyxjEbdoyxVJIsS33zoo-wAQADAgADeQADNgQ"
    },
    'deathbloom': {
        'hp': 110, 'dmg': 75, 'agility': 210,
        'photo': "AgACAgUAAxkBAAINk2iV-8lIEi635A6ilNIfA79RUcnnAAKzxjEbdoyxVAuBViFY2YbqAQADAgADeAADNgQ"
    },
    'pyrelord': {
        'hp': 110, 'dmg': 120, 'agility': 240,
        'photo': "AgACAgUAAxkBAAINlGiV-8mbOejOOtA56mV39tfxLyheAAK1xjEbdoyxVO2RCH7tETBCAQADAgADeQADNgQ"
    },
    'glarefang': {
        'hp': 80, 'dmg': 100, 'agility': 420,
        'photo': "AgACAgUAAxkBAAINlWiV-8ljphR7pzWTtFIi8u8GRCnXAAK4xjEbdoyxVMIp2AGB2zKbAQADAgADeAADNgQ"
    },
    'timbergnash': {
        'hp': 240, 'dmg': 55, 'agility': 300,
        'photo': "AgACAgUAAxkBAAINlmiV-8neiS7joBQpHVdVr64FY-kuAAK5xjEbdoyxVCfLYl6YKDXaAQADAgADeQADNgQ"
    }
}
     
weapon_list = {
    'Bronze Sword': {
        'name': 'Bronze Sword',
        'bonus_power': 10,
        'bonus_hp': 5,
        'price': 1,
        'rarity': 'Common',
        'bonus_agility': 50,
        'weapon_level': 1,
        'weapon_xp': 0,
        'weapon_max_xp': 150,
        'photo':"AgACAgUAAxkBAAINR2iV5xqtiKk7dUCyX_Fe-g7m5_6DAAKmyjEbsDKwVPy0UV1aOCAXAQADAgADeQADNgQ"
    },
    'Iron Blade': {
        'name': 'Iron Blade',
        'bonus_power': 20,
        'bonus_hp': 15,
        'price': 5,
        'rarity': 'Common',
        'bonus_agility': 75,
        'weapon_level': 1,
        'weapon_xp': 0,
        'weapon_max_xp': 150,
        'photo':"AgACAgUAAxkBAAINQ2iV5xWGX5YHGPSAbkS68hVlrsv2AAKqyjEbsDKwVAoh22qI3RGlAQADAgADeQADNgQ"
    },
    'Crystal Lance': {
        'name': 'Crystal Lance',
        'bonus_power': 30,
        'bonus_hp': 20,
        'price': 10,
        'rarity': 'Uncommon',
        'bonus_agility': 100,
        'weapon_level': 1,
        'weapon_xp': 0,
        'weapon_max_xp': 150,
        'photo':"AgACAgUAAxkBAAINQWiV5xOqqIqJCpsX9dG3hN2AOncGAAKoyjEbsDKwVA9o3H25EL4aAQADAgADeQADNgQ"
    },
    'Void Edge': {
        'name': 'Void Edge',
        'bonus_power': 50,
        'bonus_hp': 40,
        'price': 20,
        'rarity': 'Rare',
        'bonus_agility': 200,
        'weapon_level': 1,
        'weapon_xp': 0,
        'weapon_max_xp': 150,
        'photo':"AgACAgUAAxkBAAINRWiV5xgjov4p49ex0UOUD40-MJErAAKpyjEbsDKwVPTgPUSRux_yAQADAgADeAADNgQ"
    }
}
#save_user_data
def save_user_data(user_info):
    
    if user_info['coins'] <= 0:
      user_info['coins'] = 0
    db.upsert(user_info, UserQuery.user_id == user_info['user_id'])
    
    
ADMINS = [ 6616792088, 1428143946 ]  # Replace with real Telegram user IDs
#reset_all
def reset_all(update, context):
    user_id = update.effective_user.id

    if user_id not in ADMINS:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return

    db.truncate()
    update.message.reply_text("✅ All user data has been reset.")    


def escape_markdown(text: str) -> str:
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text) 
    
#reset_user
def reset_user(update, context):
    if update.effective_user.id not in ADMINS:
        update.message.reply_text('❌ You are not authorized to use this command.')
        return

    if not context.args:
        update.message.reply_text("⚠️ Please give a user ID.\nExample: `/reset_user 123456789`", parse_mode='Markdown')
        return

    try:
        user_id = int(context.args[0])  # convert to int

        # ✅ Check if user exists
        if db.search(UserQuery.user_id == user_id):
            db.remove(UserQuery.user_id == user_id)
            update.message.reply_text(f"✅ User `{user_id}` has been removed!", parse_mode='Markdown')
        else:
            update.message.reply_text("⚠️ User not found in database.")
    
    except Exception as e:
        update.message.reply_text(f"❌ Invalid ID! Error: `{e}`", parse_mode='Markdown')
 #xp           
def xp_system(update,context):
    
    user_id = update.effective_user.id
    user_info = init_user(update,context)
    user_data = context.user_data
    
    leveled_up = False
    # Add earned XP before this check
    while user_info['xp'] >= user_info['max_xp']:
      user_info['xp'] = user_info['xp'] - user_info['max_xp']  # Explicit subtraction
      user_info['level'] += 1
      user_info['max_xp'] += 50 * user_info['level']
      user_info['hp'] += 10 * user_info['level']
      user_info['power'] += 5 * user_info['level']
      user_info['agility'] += 20 * user_info['level']
      leveled_up = True
      save_user_data(user_info)

    if leveled_up:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"""🌟 Level Up! 🌟  
Congratulations, brave adventurer!
    
🧍 You’ve reached <b>Level {user_info['level']}</b>!  
Keep exploring, battling, and rising to greatness!"""
        , parse_mode = ParseMode.HTML)
      
    save_user_data(user_info)
    
def weapon_xp_system(update,context):
  user_id = update.effective_user.id
  user_info = init_user(update,context)
  user_data = context.user_data
   
  user_info['user_weapons'][user_info['equiped_weapon']]['weapon_xp'] += 30
    
  if user_info['user_weapons'][user_info['equiped_weapon']]['weapon_xp'] >= user_info['user_weapons'][user_info['equiped_weapon']]['weapon_max_xp']:
    user_info['user_weapons'][user_info['equiped_weapon']]['weapon_xp'] -= user_info['user_weapons'][user_info['equiped_weapon']]['weapon_max_xp']
    user_info['user_weapons'][user_info['equiped_weapon']]['weapon_level'] += 1
    user_info['user_weapons'][user_info['equiped_weapon']]['weapon_max_xp'] += 50*user_info['user_weapons'][user_info['equiped_weapon']]['weapon_level']
    user_info['user_weapons'][user_info['equiped_weapon']]['bonus_hp'] += 10*user_info['user_weapons'][user_info['equiped_weapon']]['weapon_level']
    user_info['user_weapons'][user_info['equiped_weapon']]['bonus_power'] += 5*user_info['user_weapons'][user_info['equiped_weapon']]['weapon_level']
    user_info['user_weapons'][user_info['equiped_weapon']]['bonus_agility'] += 20*user_info['user_weapons'][user_info['equiped_weapon']]['weapon_level']
    
    
    
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id = chat_id , text = f'''⚔️✨ Your weapon has leveled up! ✨⚔️

🔹 <b>Name:</b> {user_info['equiped_weapon']}  
🔹 <b>New Level:</b> {user_info['user_weapons'][user_info['equiped_weapon']]['weapon_level']}
🔹 <b>Weapon XP:</b> {user_info['user_weapons'][user_info['equiped_weapon']]['weapon_xp']} / {user_info['user_weapons'][user_info['equiped_weapon']]['weapon_max_xp']}

🔥 Keep battling to make it even stronger!''',
parse_mode = ParseMode.HTML)

  save_user_data(user_info)
  
#start    
def start(update, context):
    user_id = update.effective_user.id
    user_info = init_user(update,context)
    user_data = context.user_data
    username = user_info['username']
    
    images = [
    "https://files.catbox.moe/x4ah5l.jpg",  # Replace with actual file_id or direct URL
    "https://files.catbox.moe/lt70jg.jpg"
]

    chosen_image = random.choice(images)

    caption = f"""
━━━━━━━━━━━━━━━━━━━━━━  
🌌 *WELCOME TO THE REALM* 🌌  
━━━━━━━━━━━━━━━━━━━━━━  

👤 *User:* `@{username}`

You awaken beneath a fading sky, the scent of old magic thick in the air...  
Ancient whispers call your name — the realm has been waiting.

From forgotten ruins to shadowed forests, from arcane towers to cursed seas...  
your path is unwritten, your legacy yet to form.

Will you rise as a hero, fall as a legend, or vanish in silence?

━━━━━━━━━━━━━━━━━━━━━━  
📝 _The journey begins — may your choices echo through eternity._  
━━━━━━━━━━━━━━━━━━━━━━
"""

    update.message.reply_photo(
    photo=chosen_image,
    caption=caption,
    parse_mode=ParseMode.MARKDOWN)
    
#help
def help(update, context):
    user_id = update.effective_user.id
    user_info = init_user(update,context)
    user_data = context.user_data
    
    update.message.reply_text(
    """*🤖 Bot Command List*
━━━━━━━━━━━━━━━━━━━━━━

Here are all the cool things you can do:

• `/start` – 🌟 _Begin your journey!_  
• `/mystats` – 🧍‍♂️ _View your full character profile_  
• `/explore` – 🧭 _Go on an adventure and fight monsters_  
• `/guess` – 🎯 _Play the number guessing game to win coins_  
• `/toss` – 🎲 _Toss a coin and test your luck_  
• `/shop` – 🛒 _Buy Essences, weapons, and more_  
• `/myinventory` – 🎒 _Check your collected items_  
• `/mygear` – ⚔️ _View your equipped battle gear_  
• `/view <weapon>` – 🔍 _See detailed stats of a weapon available in-game_  
• `/help` – ❓ _Show this help message again_
• `/give` - _To give an item to another user_

━━━━━━━━━━━━━━━━━━━━━━  
*✨ Enjoy your adventure, hero!*  
_The realm awaits your next move..._
""",
    parse_mode=ParseMode.MARKDOWN
)

#explore 
def explore(update, context):
    
    
    user_id = update.effective_user.id
    user_info = init_user(update,context)
    user_data = context.user_data
    
    
    if update.message.chat.type != 'private':
        update.message.reply_text("❌ Use this command in DM!")
        return
        
     
     
    current_monster = random.choice(list(monster_db.keys()))
    context.user_data['current_monster'] = current_monster
    
    user_info['explores_played'] += 1
    save_user_data(user_info)   
    
    monster_stats = monster_db[current_monster]
    context.user_data['monster_hp'] = monster_stats['hp']
    context.user_data['monster_dmg'] = monster_stats['dmg']
    context.user_data['monster_agility'] = monster_stats['agility']
    monster_photo = monster_db[current_monster]['photo']
    monster_level = random.randint(1,int(user_info['level']))
    context.user_data['monster_level'] = monster_level
    context.user_data['monster_hp'] = context.user_data['monster_hp'] * monster_level
    context.user_data['monster_dmg'] = context.user_data['monster_dmg'] * monster_level
    context.user_data['monster_agility'] = context.user_data['monster_agility'] * monster_level
    keyboard = [
    [InlineKeyboardButton('⚔️ Hunt the Monster', callback_data='hunt')]
]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_photo(photo = monster_photo,
    caption=
    f"""
    🌫️ The air thickens with mystery...  
⚠️ You feel a powerful presence nearby.  

━━━━━━━━━━━━━━━━━━━━━━ 

✨ *A Wild {current_monster} Has Appeared!* ✨  
*Level:* `{monster_level}`

*Monster HP:* {context.user_data['monster_hp']}
*Monster Power:* {context.user_data['monster_dmg']}
*Monster Agility:* {context.user_data['monster_agility']}

🧝 *Brave adventurer*, what will you do?

━━━━━━━━━━━━━━━━━━━━━━  
⚔️ *Hunt* — Face the beast head-on  
━━━━━━━━━━━━━━━━━━━━━━""",
    reply_markup=reply_markup,
    parse_mode=ParseMode.MARKDOWN
)
def explore_button(update,context):
  user_info = init_user(update,context)
  user_data = context.user_data
  
  query = update.callback_query
  if 'current_monster' not in context.user_data:
    query.answer('The monster fled!', show_alert = False)
    return
  explore_option = query.data
  
  if explore_option == 'hunt':
    current_monster = context.user_data['current_monster']
    monster_hp = context.user_data['monster_hp']
    monster_dmg = context.user_data['monster_dmg']
    monster_agility = context.user_data['monster_agility']
    query.edit_message_caption(
      caption = (
      f'''
⚔️─────────────⚔️
        
<b>You chose to attack the {current_monster}!</b>
         
───────────────
         
👾 <b>Monster HP:</b> {monster_hp}
💥 <b>Monster Damage:</b> {monster_dmg}
⚡ <b>Monster Agility:</b> {monster_agility}
        
───────────────
🔥<b> Prepare for battle!</b>
⚔️ <b>Attack</b> — Face the beast head-on  
🚶 <b>Retreat</b> — Live to fight another day
⚔️─────────────⚔️
    '''),
    parse_mode = ParseMode.HTML,
    reply_markup = InlineKeyboardMarkup(
      [
        [InlineKeyboardButton('⚔️ Attack the Monster',callback_data='attack')],
        [InlineKeyboardButton('🚶 Retreat Silently',callback_data='retreat')]
      ]
    )
  )
def button(update, context):
    user_id = update.effective_user.id
    user_info = init_user(update,context)
    user_data = context.user_data
    query = update.callback_query
    answer = query.data
    
    # NEW: Handle PvP attack
    if answer == 'attack' and 'pvp_battle' in context.chat_data:
        return pvp_attack_button(update, context)
    
    # EXISTING: Continue with monster battle logic
    if 'current_monster' not in context.user_data:
        query.answer('The monster fled')
        return
    # ... rest of your existing button function stays the same
        
def button(update, context):
    
    
    user_id = update.effective_user.id
    user_info = init_user(update,context)
    user_data = context.user_data
    
    query = update.callback_query
    if 'current_monster' not in context.user_data:
      query.answer('The monster fled')
      return
    answer = query.data
    
    monster_level = context.user_data['monster_level']
    current_monster = context.user_data['current_monster']
    monster_hp = context.user_data['monster_hp']
    monster_dmg = context.user_data['monster_dmg']
    monster_agility = context.user_data['monster_agility']
    equiped_weapon = user_info['equiped_weapon']
    
    if not equiped_weapon or equiped_weapon not in user_info['user_weapons']:
      total_hp = user_info['hp']
      user_battle_power = user_info['power']
      user_battle_agility = user_info['agility']
    else:
      total_hp = user_info['hp'] + user_info['user_weapons'][equiped_weapon]['bonus_hp']
      user_battle_power = user_info['power'] + user_info['user_weapons'][equiped_weapon]['bonus_power']
      user_battle_agility = user_info['agility'] + user_info['user_weapons'][equiped_weapon]['bonus_agility']

# 🩹 Use or create current_hp if not there yet
    if 'current_hp' not in user_info:
      user_info['current_hp'] = total_hp
    
    user_battle_hp = user_info['current_hp']
    
    if answer == 'attack':
      
      explore_log = ""
      if user_battle_agility >= monster_agility:
        monster_hp -= user_battle_power
        context.user_data['monster_hp'] = monster_hp
        explore_log += f"👤 You attacked first and dealt <b>{user_battle_power}</b> damage!\n"
        
        if monster_hp > 0:
          user_battle_hp -= monster_dmg
          user_info['current_hp'] = user_battle_hp 
          save_user_data(user_info)
          
          explore_log += f"👾 {current_monster} struck back and dealt <b>{monster_dmg}</b> damage!\n"
            
      if user_battle_agility < monster_agility:
        user_battle_hp -= monster_dmg
        user_info['current_hp'] = user_battle_hp
        save_user_data(user_info)
        explore_log += f"👾 {current_monster} attacked first and dealt <b>{monster_dmg}</b> damage!\n"
        
        if user_battle_hp > 0:
          monster_hp -= user_battle_power
          context.user_data['monster_hp'] = monster_hp
          explore_log += f"👤 You struck back and dealt <b>{user_battle_power}</b> damage!\n"
        
        
        # Update stored HPs
        
        context.user_data['monster_hp'] = monster_hp
        
      if monster_hp <= 0:
        user_info['coins']+=20
        user_info['xp']+=15
        user_info['explores_won'] += 1
        user_info['current_hp'] = total_hp
        save_user_data(user_info)
        xp_system(update,context)
        if not equiped_weapon or equiped_weapon not in user_info['user_weapons']:
          weapon_xp_msg = ''
          pass
        else:
          
          weapon_xp_system(update,context)
          
          weapon_xp_msg = '<b>🗡️ Weapon XP Gained:</b> +30'
          
        
        query.edit_message_caption(
          caption =
    f"""⚔️ <b>Battle Log</b>  
━━━━━━━━━━━━━━━━━━━━━━  

{explore_log}

🏆 <b>Victory!</b>  
━━━━━━━━━━━━━━━━━━━━━━  
You defeated <b>{current_monster}</b> in a fierce battle!

🪙 <b>Coins Earned:</b> +20  
✨ <b>XP Gained:</b> +15
{weapon_xp_msg}
   
━━━━━━━━━━━━━━━━━━━━━━  
🎮 Use /explore to battle more monsters!""",
    parse_mode=ParseMode.HTML
)
        
        
        
        
        
        del user_data['current_monster']
        del user_data['monster_hp']
        del user_data['monster_dmg']
        del user_data['monster_agility']
          # full HP again
        
        
      elif user_info['current_hp'] <= 0:
        user_info['coins'] -= 10
        user_info['xp'] += 5
        user_info['explores_lost'] += 1
        user_info['current_hp'] = total_hp
        save_user_data(user_info)
        xp_system(update,context)
        if not equiped_weapon or equiped_weapon not in user_info['user_weapons']:
          weapon_xp_msg = ''
          pass
        else:
          
        
          weapon_xp_system(update,context)
          
          weapon_xp_msg = '<b>Weapon XP Gained:</b> +30'
          
        query.edit_message_caption(
          caption=
    f"""⚔️ <b>Battle Log</b>  
━━━━━━━━━━━━━━━━━━━━━━  

{explore_log}

💀 <b>Defeat...</b>  
━━━━━━━━━━━━━━━━━━━━━━  
You fought bravely, but <b>{current_monster}</b> was too strong.

🧍‍♂️ You have fallen in battle.  
🪙 <b>Coins Lost:</b> 10  
✨ <b>XP Gained:</b>+5  
   {weapon_xp_msg}
━━━━━━━━━━━━━━━━━━━━━━  
🔁 Use /explore to try again and redeem your honor!
""",
    parse_mode=ParseMode.HTML
)
        
        
        
        
        
        
        
        del user_data['current_monster']
        del user_data['monster_hp']
        del user_data['monster_dmg']
        del user_data['monster_agility']
          # full HP again
        
        
      else:
        keyboard5 = [
    [InlineKeyboardButton('⚔️ Attack Again', callback_data='attack')],
    [InlineKeyboardButton('🚶 Retreat', callback_data='retreat')]
]
        reply_markup5 = InlineKeyboardMarkup(keyboard5)

        query.edit_message_caption(
          caption =
    f"""⚔️ <b>Attack Turn</b>  
━━━━━━━━━━━━━━━━━━━━━━  

{explore_log}

━━━━━━━━━━━━━━━━━━━━━━  
📉 <b>{current_monster}'s HP:</b> <code>{monster_hp}</code>  
❤️ <b>Your HP:</b> <code>{user_battle_hp}</code>

━━━━━━━━━━━━━━━━━━━━━━""",
    reply_markup=reply_markup5,
    parse_mode=ParseMode.HTML
)
       
        
    elif answer == 'retreat':
      query.edit_message_caption(
        caption =
  """🚶‍♂️ *You Chose to Retreat*  
━━━━━━━━━━━━━━━━━━━━━━  
Sometimes, retreat is the wisest choice.  
Your journey doesn’t end here...

📜 _Live to fight another day, brave soul._  
━━━━━━━━━━━━━━━━━━━━━━""",
  parse_mode=ParseMode.MARKDOWN
)
    

        
    
#inventory    
def inventory(update, context):
    
    user_id = update.effective_user.id
    user_info = init_user(update,context)
    user_data = context.user_data
    username = user_info['username'] or user_info['first_name']
    
    inv_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("⚔️ Weapons", callback_data='inv_weapons'),
        InlineKeyboardButton("✨ Magical Items", callback_data='inv_magic')
    ]
])
    update.message.reply_text(
    f"*👤 Your Inventory*\n\n"
    f"`Username:` `{username}`\n\n"
    f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    f"💰 *Coins:* {user_info['coins']}\n"
    f"🔮 *Essences:* {user_info['essences']}\n"
    f"🐚 *Moonshards:* {user_info['moonshards']}\n\n"
    f"━━━━━━━━━━━━━━━━━━━━━━",
    parse_mode=ParseMode.MARKDOWN,
    reply_markup = inv_markup
)

def inv_button(update,context):
  
  user_info = init_user(update,context)
  user_id = user_info['user_id']
  username = user_info['username'] or user_info['first_name']
  user_data = context.user_data
  
  query = update.callback_query
  query.answer()
  
  inv_chosen = query.data
  
  if inv_chosen == 'inv_weapons':
    inv_weapons_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📦 Inventory", callback_data='inv_main'),
        InlineKeyboardButton("✨ Magical Items", callback_data='inv_magic')
    ]
])
    if not user_info['user_weapons']:
      query.edit_message_text(
      text=(
          "⚔️ *Weapon Inventory*\n"
          "━━━━━━━━━━━━━━━━━━━━━━\n"
          "You open your worn-out satchel... 🧳\n"
          "_It's empty... for now._\n\n"
          "You haven’t discovered any weapons yet.\n"
          "Explore the world or win battles to find powerful gear!\n"
          "━━━━━━━━━━━━━━━━━━━━━━"
      ),
      parse_mode=ParseMode.MARKDOWN,
      reply_markup = inv_weapons_markup
  )
  
    else:
      user_wp_list = "\n".join([f"🗡️ {wp}" for wp in user_info["user_weapons"].keys()])
      
      message = f"""
🧰 <b>YOUR INVENTORY</b>

✨ Here are all your equipped and owned weapons:

━━━━━━━━━━━━━━━━━━━━

{user_wp_list}

━━━━━━━━━━━━━━━━━━━━

💡 <b>Tip:</b> Use /mygear to view your equipped weapon!
"""
      query.edit_message_text(message,
        reply_markup = inv_weapons_markup,
        parse_mode = ParseMode.HTML)
        
  elif inv_chosen == 'inv_magic':
    inv_magic_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📦 Inventory", callback_data='inv_main'),
        InlineKeyboardButton("⚔️ Weapons", callback_data='inv_weapons')
    ]
])
    query.edit_message_text(
    text=(
        "✨ *Magical Items*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "You gaze into your enchanted pouch... 🔮\n"
        "_But it's silent and empty..._\n\n"
        "No magical items have been discovered yet.\n"
        "Seek out mystical places, defeat bosses, or unlock ancient chests!\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    ),
    parse_mode=ParseMode.MARKDOWN,
    reply_markup = inv_magic_markup
)
  elif inv_chosen == 'inv_main':
    inv_main_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("⚔️ Weapons", callback_data='inv_weapons'),
        InlineKeyboardButton("✨ Magical Items", callback_data='inv_magic')
    ]
])
    query.edit_message_text(
    f"*👤 Your Inventory*\n"
    f"`Username:` `{username}`\n"
    f"━━━━━━━━━━━━━━━━━━━━━━\n"
    f"💰 *Coins:* {user_info['coins']}\n"
    f"🔮 *Essences:* {user_info['essences']}\n"
    f"🐚 *Moonshards:* {user_info['moonshards']}\n"
    f"━━━━━━━━━━━━━━━━━━━━━━",
    parse_mode=ParseMode.MARKDOWN,
    reply_markup = inv_main_markup
)

BUY_WEAPON = range(1)
CHOOSE_QUANTITY = range(1)

def cancel(update, context):
    update.message.reply_text("❌ Purchase cancelled. You can /shop again anytime!")
    return ConversationHandler.end
    
#shop
def shop(update, context):
    user_info = init_user(update,context)
  
    if update.message.chat.type != 'private':
        update.message.reply_text("❌ Use this command in DM!")
        return
  
    image = "AgACAgUAAxkBAAIPKWiWR8bCk2-C5LXjUr6jLKdjoTnUAAKf0zEb5V-wVFwym1zA70KmAQADAgADeAADNgQ"  # Replace with your image URL or file_id

    caption = f"""
━━━━━━━━━━━━━━━━━━━━━━  
🏪 *THE GRAND SHOP*  
━━━━━━━━━━━━━━━━━━━━━━

Step into a world of trades and treasures.  
Choose where you want to browse:

🪙 *Resource Shop*  
Buy *Moonshards* and rare *Essences* to boost your power.

🗡️ *Weapon Shop*  
*Buy Amazing And powerful Weapons to increase your gear power*

⭐ *Magic Shop*  
🔒 Locked — *Coming soon...*

━━━━━━━━━━━━━━━━━━━━━━  
📜 _New shops will open as your journey unfolds..._
"""

    keyboard7 = [
    [InlineKeyboardButton("🎒 Resource Shop", callback_data="resource_shop")],
    [InlineKeyboardButton("🛡️ Weapon Shop", callback_data="weapon_shop")],
    [InlineKeyboardButton("🌟 Magic Shop", callback_data="magic_shop")]
    
]

    reply_markup7 = InlineKeyboardMarkup(keyboard7)

    update.message.reply_photo(
        photo=image,
        caption=caption,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup7
    )

def button2(update, context):
    
    user_id = update.effective_user.id
    user_info = init_user(update,context)
    user_data = context.user_data
    
    query = update.callback_query
    query.answer()
    context.user_data['chosen_shop'] = query.data
    
    if context.user_data['chosen_shop'] == 'resource_shop':
      keyboard4 = [
        [InlineKeyboardButton('💥 Buy Essences (1000 🪙)', callback_data='essences')],
        [InlineKeyboardButton('🧿 Buy Moonshards (100 🪙)', callback_data='moonshards')]
    ]
      reply_markup2 = InlineKeyboardMarkup(keyboard4)
      
      query.edit_message_caption(
      caption = ( """
🎒 *Resource Shop*  
━━━━━━━━━━━━━━━━━━━━━━  
Here you'll find rare materials that fuel your journey:  

🪙 Coins — Common trade currency  
🔮 Essences — Crystallized magical energy  
🐚 Moonshards — Fragments of ancient power

💡 _Spend wisely, traveler. These items are more than they appear..._
"""
    ),reply_markup = reply_markup2,
    parse_mode=ParseMode.MARKDOWN
)
 
      
      
    elif context.user_data['chosen_shop'] == 'weapon_shop':
      query.edit_message_caption(
        caption = (
    """
🏰 *Welcome to the Weapon Shop!* 🏰  
━━━━━━━━━━━━━━━━━━━━━━  
🛒 Choose your blade and forge your destiny!

`Bronze Sword`  
💰 Price: 1 Essence 🎖️ Rarity: Common  

`Iron Blade`  
💰 Price: 5 Essence 🎖️ Rarity :Common  

`Crystal Lance`  
💰 Price: 10 Essence 🎖️ Rarity :Uncommon

`Void Edge`  
💰 Price: 20 Essence 🎖️ Rarity: Rare  

━━━━━━━━━━━━━━━━━━━━━━  
📝 *Send the name of the weapon you want to buy.*
*use /cancel to cancel the purchase *
"""
),
parse_mode  = ParseMode.MARKDOWN)

      return BUY_WEAPON 
      

    elif context.user_data['chosen_shop'] == 'magic_shop':
      query.edit_message_caption(
        caption = ("""
✨ *Magic Shop - Not Yet Awakened* ✨  
━━━━━━━━━━━━━━━━━━━━━━  
📦 Enchanted tomes remain sealed...  
🔮 Mystic lights flicker behind dusty shelves...  
🧙‍♂️ The magician has yet to return from his arcane journey.

📜 *Patience, young adventurer — true magic takes time.*  
━━━━━━━━━━━━━━━━━━━━━━
"""),
parse_mode = ParseMode.MARKDOWN)

def button7(update,context):
  
  user_info = init_user(update,context)
  user_data = context.user_data
  
  query = update.callback_query
  query.answer()
  
  context.user_data['item_to_buy'] = query.data
  item_name = context.user_data.get("item_to_buy", "Unknown Item")
  currency_emoji = '🪙'
  item_to_buy = context.user_data['item_to_buy']

  if item_to_buy == "essences":
    item_price = 1000
  elif item_to_buy == "moonshards":
    item_price = 100
    
  query.edit_message_caption(
    caption = (f"""
🛒 <b>Purchase Menu</b>  
━━━━━━━━━━━━━━━━━━━━━━  
✨ You have selected: <b>{item_name}</b>  
💰 <b>Price:</b> {item_price} {currency_emoji} per unit  
📦 <b>Stock:</b> Unlimited

🧮 <i>How many would you like to buy?</i>  
<b>Send the quantity below.</b>  
<b>Send /cancel to cancel purchase.</b>
━━━━━━━━━━━━━━━━━━━━━━
"""),
parse_mode = ParseMode.HTML
)
  return CHOOSE_QUANTITY
    
def handle_quantity(update, context):
    
    user_id = update.effective_user.id
    user_info = init_user(update,context)
    user_data = context.user_data
    item = context.user_data['item_to_buy']
    
    if not update.effective_user:
      update.message.reply_text('not you')
    try:
        amount = int(update.message.text)
        if amount <= 0:
            update.message.reply_text("❌ Please enter a number greater than 0.")
            return CHOOSE_QUANTITY
    except:
        update.message.reply_text("❌ Please enter a valid number.")
        return CHOOSE_QUANTITY

    if item == 'essences':
        price = 1000
        if user_info['coins'] >= amount * price:
            user_info['coins'] -= amount * price
            user_info['essences'] += amount
            save_user_data(user_info)
            update.message.reply_text(f"✅ Bought {amount} Essences for {amount * price} coins!")
        else:
            update.message.reply_text("❌ Not enough coins!")

    elif item == 'moonshards':
        price = 100
        if user_info['coins'] >= amount * price:
            user_info['coins'] -= amount * price
            user_info['moonshards'] += amount
            save_user_data(user_info)
            update.message.reply_text(f"✅ Bought {amount} Moonshards for {amount * price} coins!")
        else:
            update.message.reply_text("❌ Not enough coins!")

    return ConversationHandler.END
    
    
shop_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(button7, pattern='^(essences|moonshards)$')],
    states={
        CHOOSE_QUANTITY: [MessageHandler(Filters.text & ~Filters.command, handle_quantity)],
    },
    fallbacks=[CommandHandler('cancel',cancel)],
)
# This is your cancel handler – works for the whole conversation

    
def buy_wp(update,context):
  user_info = init_user(update,context)
  
  user_wp_name = update.message.text
  
  if user_wp_name not in list(weapon_list.keys()):
    update.message.reply_text(
    "⚠️ *No such weapon found!*\n"
    "Please double-check the name and try again.\n\n"
    "💡 *Tip:* Long press the weapon name in the list to copy it easily.",
    parse_mode=ParseMode.MARKDOWN
)
    return BUY_WEAPON
    
  elif user_wp_name in list(weapon_list.keys()):
    if user_wp_name not in list(user_info['user_weapons'].keys()):
      if user_info['essences'] >= weapon_list[user_wp_name]['price']:
        user_info['user_weapons'][user_wp_name] = copy.deepcopy(weapon_list[user_wp_name])
        user_info['essences'] -= weapon_list[user_wp_name]['price']
        save_user_data(user_info)
        update.message.reply_text(
      f"""
  ━━━━━━━━━━━━━━━━━━━━━━  
  ✅ You have successfully purchased ``{user_wp_name}``  
  💰 Price: {weapon_list[user_wp_name]['price']} Essences  
  ━━━━━━━━━━━━━━━━━━━━━━  
  🧰 The weapon has been added to your inventory.  
  ⚙️ Equip it using `/mygear` to use it in battle!  
  ━━━━━━━━━━━━━━━━━━━━━━
  """,
      parse_mode=ParseMode.MARKDOWN
  )
        return ConversationHandler.END
      
      else:
        update.message.reply_text(
    "🚫 Not Enough Essences!\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "You don’t have enough 💠 *Essences* to buy that weapon.\n"
    "Keep exploring and defeating monsters to earn more!\n\n"
    "💡 *Tip:* Stronger monsters drop more essences.\n"
    "━━━━━━━━━━━━━━━━━━━━━━",
    parse_mode=ParseMode.MARKDOWN
)
        return ConversationHandler.END

  
    elif user_wp_name in list(user_info['user_weapons'].keys()):
      update.message.reply_text(
    "⚠️ You Already Own This Weapon!\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "You already have this weapon in your inventory.\n"
    "Check it out using /mygear!\n\n"
    "💡 <b>Tip:</b>You can only buy each weapon once.\n"
    "━━━━━━━━━━━━━━━━━━━━━━",
    parse_mode=ParseMode.HTML
)
      return ConversationHandler.END
  
weapon_conv_handler = ConversationHandler(
      entry_points=[CallbackQueryHandler(button2, pattern='^(weapon_shop)$')],
      states={
          BUY_WEAPON: [MessageHandler(Filters.text & ~Filters.command, buy_wp)],
      },
      fallbacks=[CommandHandler('cancel',cancel)]  # No fallback used in your case
  )
    
    
  
guess_num = range(1)
#guess 
def guess(update,context):
    
    user_id = update.effective_user.id
    user_info = init_user(update,context)
    user_data = context.user_data
    
    if update.message.chat.type != 'private':
        update.message.reply_text(
    text="""
🕵️‍♂️ *Guessing Game Notice*  
━━━━━━━━━━━━━━━━━━━━━━  
This game can only be played in *private chat* with me.

👤 Tap my profile and press *Start* to begin your challenge!
━━━━━━━━━━━━━━━━━━━━━━  
""",
    parse_mode=ParseMode.MARKDOWN
)
        return
        
    # Check if user is on cooldown
      
        
    now = time.time()
    cooldown = context.user_data.get('guess_cooldown', 0)
    
    if now < cooldown:
         wait_time = int(cooldown - now)
         update.message.reply_text(
    text="⏳ *Please wait!* \n\nYou're on cooldown. Try again in *{} seconds*!".format(wait_time),
    parse_mode=ParseMode.MARKDOWN
)
         return ConversationHandler.END
    
        # Set new cooldown (60 seconds from now)
    context.user_data['guess_cooldown'] = now + 60
    
    
    context.user_data['number']= random.randint(1,100)
    
    keyboard2 = [
    [InlineKeyboardButton("✅ Yes! Let's Play", callback_data='yes')],
    [InlineKeyboardButton("❌ No, Maybe Later", callback_data='no')]
]
    
    reply_markup3 = InlineKeyboardMarkup(keyboard2)
    
    update.message.reply_text(
    "🎯 *Welcome to the Number Guessing Game!*  \n"
    "━━━━━━━━━━━━━━━━━━━━━━  \n"
    "🔢 A number between *1 and 100* has been chosen...  \n"
    "❓ Can you guess it right?  \n\n"
    "🏆 *Reward:* +100 Coins  \n"
    "⏱️ *Note:* Play once every 1 minute.  \n"
    "━━━━━━━━━━━━━━━━━━━━━━",
    parse_mode=ParseMode.MARKDOWN,
    reply_markup=reply_markup3
)
    
def button3(update,context):
    
    
    
    user_id = update.effective_user.id
    user_info = init_user(update,context)
    user_data = context.user_data
    
    query=update.callback_query
    query.answer()
    
    user_choice = query.data
    
    
    if user_choice == 'yes':
        query.edit_message_text(
    text="🎯 *Great!* Let's begin the challenge!  \n"
         "━━━━━━━━━━━━━━━━━━━━━━  \n"
         "📨 Send me a number between *1 and 100* to make your guess.  \n"
         "💡 Trust your instincts and take a shot!  \n"
         "━━━━━━━━━━━━━━━━━━━━━━",
    parse_mode=ParseMode.MARKDOWN
)
        return guess_num
        
    elif user_choice == 'no':
        query.edit_message_text(
    text="🚪 *You chose to walk away...*  \n"
         "━━━━━━━━━━━━━━━━━━━━━━  \n"
         "Sometimes, a wise retreat is better than a risky gamble.  \n"
         "🎲 Come back anytime to test your luck again! 😉  \n"
         "━━━━━━━━━━━━━━━━━━━━━━",
    parse_mode=ParseMode.MARKDOWN
)
        return ConversationHandler.END
        
def guess_numb(update,context):
     
        user_id = update.effective_user.id
        user_info = init_user(update,context)
        user_data = context.user_data
        
        
        user_ans = int(update.message.text)
        correct_ans = int(context.user_data['number'])
            
         
    
    
        if user_ans == correct_ans:
            user_info['coins']+=100
            del context.user_data['number']
            user_info['xp']+=25
            save_user_data(user_info)
            xp_system(update,context)
            update.message.reply_text(
    "🎉 *You guessed it right!* 🎯  \n"
    "━━━━━━━━━━━━━━━━━━━━━━  \n"
    "💰 *Reward:* +100 Coins  \n"
    "✨ *XP Gained:* +25 XP  \n"
    "━━━━━━━━━━━━━━━━━━━━━━  \n"
    "Keep it up, champion! 🧠🔥",
    parse_mode=ParseMode.MARKDOWN
)
            return ConversationHandler.END
            
        elif user_ans >= correct_ans:
            update.message.reply_text(
    "❌ *Wrong answer!*\nYour guess is *too high* 📈\nTry a smaller number!",
    parse_mode=ParseMode.MARKDOWN
)
            return guess_num
            
            
        elif user_ans <= correct_ans:
            update.message.reply_text(
    "❌ *Wrong answer!*\nYour guess is *too low* 📉\nTry a bigger number!",
    parse_mode=ParseMode.MARKDOWN
)
            return guess_num
            
conv_handler = ConversationHandler(
        entry_points =[CallbackQueryHandler(button3,pattern='^yes|no$')],
        states = {
                        guess_num: [MessageHandler(Filters.text & ~Filters.command , guess_numb )]
                        },
                        fallbacks = []
                        )        
   
 #toss  
def toss(update,context):
    user_id = update.effective_user.id
    user_info = init_user(update,context)
    user_data = context.user_data
    
    # Check if user is on cooldown
    now = time.time()
    cooldown = context.user_data.get('toss_cooldown', 0)

    if now < cooldown:
        wait_time = int(cooldown - now)
        update.message.reply_text(
    text=f"⏳ *Whoa there!* You just tossed the coin!\n\n🪙 Please wait *{wait_time} seconds* before trying again!",
    parse_mode=ParseMode.MARKDOWN
)
        return

    # Set new cooldown (60 seconds from now)
    context.user_data['toss_cooldown'] = now + 30
    
    
    two_option = ['heads','tails']
    bot_option = random.choice(two_option)
    context.user_data['bot_option'] = bot_option
    
    keyboard3 = [
    [
        InlineKeyboardButton("🪙 Heads", callback_data='heads'),
        InlineKeyboardButton("🐢 Tails", callback_data='tails')
    ]
]
    reply_markup4 = InlineKeyboardMarkup(keyboard3)
    
    update.message.reply_text(
    "🪙 *Time to Toss the Coin!* 🎯  \n"
    "━━━━━━━━━━━━━━━━━━━━━━  \n"
    "Choose your side wisely:  \n"
    "Heads or Tails? 🤔",
    reply_markup=reply_markup4,
    parse_mode=ParseMode.MARKDOWN
)
    
    
def button4(update,context):
    user_id = update.effective_user.id
    user_info = init_user(update,context)
    user_data = context.user_data
    
    query = update.callback_query
    query.answer()
    
    chosen_option = query.data
    
    if chosen_option == context.user_data['bot_option']:
        query.edit_message_text(
    f"🪙 *Coin Toss Result!* 🎯\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    f"🎉 The coin landed on: *{context.user_data['bot_option'].capitalize()}*\n"
    "✅ *You won the toss!*\n"
    "🪙 *Reward:* +20 Coins\n"
    "✨ *XP Gained:* +15",
    parse_mode=ParseMode.MARKDOWN
)
        user_info['coins'] += 20
        user_info['xp']+=15
        save_user_data(user_info)
        xp_system(update,context)
        
    else:
        query.edit_message_text(
    f"🪙 *Coin Toss Result!* 🎯\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    f"😢 The coin landed on: *{context.user_data['bot_option'].capitalize()}*\n"
    "❌ *You lost the toss!*\n"
    "💸 *Penalty:* -10 Coins",
    parse_mode=ParseMode.MARKDOWN
)
        user_info['coins']-= 10
        save_user_data(user_info)
  #stats      
def stats(update,context):
    user_id = update.effective_user.id
    user_info = init_user(update,context)
    user_data = context.user_data
    
    username = user_info["username"]
    hp = user_info["hp"]
    max_hp = user_info["hp"]
    power = user_info["power"]
    level = user_info["level"]
    agility = user_info["agility"]
    xp = user_info["xp"]
    max_xp = user_info["max_xp"]
    coins = user_info["coins"]
    moonshards = user_info["moonshards"]
    essences = user_info["essences"]
    equiped_weapon = user_info['equiped_weapon'] or 'No weapons or not equiped one'
    

    if not equiped_weapon or equiped_weapon not in user_info['user_weapons']:
      bonus_hp = 0
      bonus_power = 0
      bonus_agility = 0
      
    else:
      bonus_hp = user_info['user_weapons'][equiped_weapon].get('bonus_hp', 0)
      bonus_power = user_info['user_weapons'][user_info['equiped_weapon']]['bonus_power']
      bonus_agility = user_info['user_weapons'][user_info['equiped_weapon']]['bonus_agility']
     
    
    stats_message = f"""
━━━━━━━━━━━━━━━━━━━━━━  
🏰 *CHARACTER PROFILE* 🏰  
━━━━━━━━━━━━━━━━━━━━━━

👤 *Username:* `@{username}`

━━━━━━━━━━━━━━━━━━━━━━  

🎚️ *LEVEL & XP*  
*Level:* *{level}*  
*XP:* *{xp} / {max_xp}*

━━━━━━━━━━━━━━━━━━━━━━  

❤️ *STATS*  
*HP:* *{hp}* *(+{bonus_hp})*
*Power:* *{power}* *(+{bonus_power})*
*Agility:* *{agility}* *(+{bonus_agility})*
*Equiped Weapon:* *{equiped_weapon} *

━━━━━━━━━━━━━━━━━━━━━━  
📝 *Play more to grow stronger — the realm remembers those who act.*  
━━━━━━━━━━━━━━━━━━━━━━"""
    
    
    
    keyboard6 = [
    [
        InlineKeyboardButton("⚔️ Battle Stats", callback_data="battle_stats"),
        InlineKeyboardButton("🧭 Explore Stats", callback_data="explore_stats")
    ]
]

    reply_markup6 = InlineKeyboardMarkup(keyboard6)


    
    update.message.reply_text(stats_message,     reply_markup = reply_markup6 , 
parse_mode = ParseMode.MARKDOWN)

def button6(update,context):
    user_info = init_user(update,context)
    user_data = context.user_data
    
    query = update.callback_query
    query.answer()
    
    chosen_stats = query.data
    
    if chosen_stats == 'battle_stats':
        
        battles_played = user_info['battles_played']
        battles_won = user_info['battles_won']
        battles_lost = user_info['battles_lost']
        
        battle_text = f"""
*BATTLE STATS*

Battles Played: `{battles_played}`  
Battles Won: `{battles_won}`  
Battles Lost: `{battles_lost}`

_Keep fighting, warrior!_
"""
        reply_markup7=InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🎯 My Stats", callback_data="my_stats"),
        InlineKeyboardButton("🧭 Explore Stats", callback_data="explore_stats")
    ]
])

        query.edit_message_text(
        battle_text,
        reply_markup = reply_markup7,
        parse_mode = ParseMode.MARKDOWN)
        
    elif chosen_stats == 'explore_stats':
        
        explores_played = user_info['explores_played']
        explores_won = user_info['explores_won']
        explores_lost = user_info['explores_lost']
        
        explore_text = f"""
* EXPLORE STATS*

 *Explores Done:* `{explores_played}`  
 *Victories:* `{explores_won}`  
 *Defeats:* `{explores_lost}`

_Keep exploring, adventurer! _
"""
        reply_markup8=InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🎯 My Stats", callback_data="my_stats"),
        InlineKeyboardButton("⚔️ Battle Stats", callback_data="battle_stats")
    ]
])

        query.edit_message_text(
        explore_text,
        reply_markup=reply_markup8,
        parse_mode = ParseMode.MARKDOWN)
        
        
    elif chosen_stats == 'my_stats':
        
        username = user_info["username"]
        hp = user_info["hp"]
        max_hp = user_info["hp"]
        power = user_info["power"]
        level = user_info["level"]
        agility = user_info["agility"]
        xp = user_info['xp']
        max_xp = user_info['max_xp']
        coins = user_info["coins"]
        moonshards = user_info["moonshards"]
        essences = user_info["essences"]
        equiped_weapon = user_info['equiped_weapon'] or 'No weapons or not equiped one'
        if not equiped_weapon or equiped_weapon not in user_info['user_weapons']:
          bonus_hp = 0
          bonus_power = 0
          bonus_agility = 0
      
        else:
          bonus_hp = user_info['user_weapons'][equiped_weapon].get('bonus_hp', 0)
          bonus_power = user_info['user_weapons'][user_info['equiped_weapon']]['bonus_power']
          bonus_agility = user_info['user_weapons'][user_info['equiped_weapon']]['bonus_agility']

        stats_message = f"""
━━━━━━━━━━━━━━━━━━━━━━
🏰 <b>CHARACTER PROFILE</b> 🏰
━━━━━━━━━━━━━━━━━━━━━━

👤 <b>Username:</b> @{username}

━━━━━━━━━━━━━━━━━━━━━━

🎚️ <b>LEVEL & XP</b>
<b>Level:</b> {level}
<b>XP:</b> {xp} / {max_xp}

━━━━━━━━━━━━━━━━━━━━━━

❤️ <b>STATS</b>
<b>HP:</b> {hp} (+{bonus_hp})
<b>Power:</b> {power} (+{bonus_power})
<b>Agility:</b> {agility} (+{bonus_agility})
<b>Equiped Weapon:</b> {equiped_weapon or 'No Weapon'}

━━━━━━━━━━━━━━━━━━━━━━

📝 <i>Play more to grow stronger — the realm remembers those who act.</i>
━━━━━━━━━━━━━━━━━━━━━━
"""



        
        keyboard6 = [
    [
        InlineKeyboardButton("⚔️ Battle Stats", callback_data="battle_stats"),
        InlineKeyboardButton("🧭 Explore Stats", callback_data="explore_stats")
    ]
]
        reply_markup6 = InlineKeyboardMarkup(keyboard6)

        query.edit_message_text(
    text=stats_message,
    reply_markup=reply_markup6,
    parse_mode=ParseMode.HTML
)
 
def add(update, context):
    admin_id = update.effective_user.id
    if admin_id not in ADMINS:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    # Determine target user and item/amount
    if update.message.reply_to_message:
        # Reply-to-user method: /add <item> <amount>
        recipient = update.message.reply_to_message.from_user
        recipient_id = recipient.id
        recipient_name = recipient.username or recipient.first_name

        if len(context.args) < 2:
            update.message.reply_text(
                "Usage (reply): `/add <item> <amount>`",
                parse_mode="Markdown"
            )
            return
        target_user_item = context.args[0]
        try:
            item_amount = int(context.args[1])
        except ValueError:
            update.message.reply_text("❌ Invalid amount.")
            return

    else:
        # Manual: /add <user_id> <item> <amount>
        if len(context.args) < 3:
            update.message.reply_text(
                "Usage: `/add <user_id> <item> <amount>`\nOr reply to a user with `/add <item> <amount>`",
                parse_mode="Markdown"
            )
            return
        try:
            recipient_id = int(context.args[0])
            target_user_item = context.args[1]
            item_amount = int(context.args[2])
        except ValueError:
            update.message.reply_text("❌ Invalid arguments.")
            return

        rec_info = db.get(UserQuery.user_id == recipient_id)
        recipient_name = rec_info.get('username', f"user_{recipient_id}") if rec_info else f"user_{recipient_id}"

    if item_amount <= 0:
        update.message.reply_text("❌ Amount must be positive.")
        return

    # Get or init the recipient in DB
    user_info = db.get(UserQuery.user_id == recipient_id)
    if not user_info:
        user_info = get_user_info_by_user_id(recipient_id, recipient_name)

    # Update the item
    new_value = user_info.get(target_user_item, 0) + item_amount
    db.update({target_user_item: new_value}, UserQuery.user_id == recipient_id)

    # Confirmation to admin
    update.message.reply_text(f"""
✅ *Item Successfully Added!*

━━━━━━━━━━━━━━━━━━━━
👤 *User:* `{recipient_id}`
📦 *Item:* `{target_user_item}`
➕ *Amount Added:* `{item_amount}`
📊 *New Total:* `{new_value}`
━━━━━━━━━━━━━━━━━━━━
""", parse_mode="Markdown")

    # Notify recipient in PM if possible
    try:
        context.bot.send_message(
            chat_id=recipient_id,
            text=f"""
💰 *An admin has added an item to your account!*

━━━━━━━━━━━━━━━━━━━━
📦 *Item:* `{target_user_item}`
➕ *Amount Added:* `{item_amount}`
📊 *Your New Total:* `{new_value}`
━━━━━━━━━━━━━━━━━━━━
""",
            parse_mode="Markdown"
        )
    except:
        pass  # Ignore if recipient can't be messaged



EQUIP_WEAPON = range(0)


#my_gear
def my_gear(update,context):
  chat_type = update.effective_chat.type
  user_info = init_user(update,context)
  user_data = context.user_data
  
  if chat_type in ['group','supergroup']:
    update.message.reply_text(
      f"""
  🛡️ <b>Your Battle Gear</b>
  
  ━━━━<b> Your equiped weapon </b>━━━━
  
  🔹 <b>Equipped Weapon:</b> {user_info['equiped_weapon']}
  
  ━━━━ 🧪 <b>Magical Items </b>🧪 ━━━━
  
  <i>Coming Soon...</i>
  
  ━━━━━━━━━━━━━━━━━━━━
  <b> Use /mygear in DM to edit your gear </b>
  
  """,
      parse_mode=ParseMode.HTML
  )
  
  
  else:
    
    my_gear_keyboard = [
      [InlineKeyboardButton("🗡️ Equip Weapon", callback_data='equip_weapon')],
      [InlineKeyboardButton("🧪 Edit Magical Items", callback_data='edit_magic')]
  ]
  
    my_gear_markup = InlineKeyboardMarkup(my_gear_keyboard)
    
    update.message.reply_text(
      f"""
  🛡️ *Your Battle Gear*
  
  ━━━━<b> Your equiped Weapon </b>━━━━
  
  🔹 *Equipped Weapon:* {user_info['equiped_weapon']}
  
  ━━━━ 🧪 *Magical Items* 🧪 ━━━━
  
  _Coming Soon..._
  
  ━━━━━━━━━━━━━━━━━━━━
  """,
      parse_mode="Markdown",
      reply_markup = my_gear_markup
  )
    return ConversationHandler.END

def my_gear_button(update,context):
  
  user_info = init_user(update,context)
  
  query = update.callback_query
  query.answer()
  
  my_gear_option = query.data
  
  if my_gear_option == 'edit_magic':
    query.edit_message_text(
    f"""
🧪 *Edit Magical Items*

━━━━━━━━━━━━━━━━━━━━

✨ This feature is *coming soon*...
Get ready to enhance your powers!

━━━━━━━━━━━━━━━━━━━━
""",
    parse_mode="Markdown"
)

  elif my_gear_option == 'equip_weapon':
    user_weapons = user_info['user_weapons']
    weapons_list = '\n'.join([f"🔸 `{w}`" for w in user_weapons])  # Replace `user_weapons` with your weapon list variable

    query.edit_message_text(
    f"""
🗡️ *Equip Weapon*

━━━━━━━━━━━━━━━━━━━━

Here are your available weapons:

{weapons_list if weapons_list else "You have no weapons yet."}

━━━━━━━━━━━━━━━━━━━━
📤 Send the *weapon name* to equip it.
━━━━━━━━━━━━━━━━━━━━
""",
    parse_mode="Markdown"
)
    return EQUIP_WEAPON

def equip_weapon(update,context):
  
  sent_weapon_name = update.message.text.title()
  user_info = init_user(update,context)
  
  if sent_weapon_name in list(weapon_list.keys()):
    if sent_weapon_name not in list(user_info['user_weapons'].keys()):
      update.message.reply_text(
      """
  🚫 *Oops!*
  
  ━━━━━━━━━━━━━━━━━━━━
  
  You do *not* own this weapon.
  
  Please check your inventory and try again with a valid weapon name.
  
  ━━━━━━━━━━━━━━━━━━━━
  """,
      parse_mode="Markdown"
  )
      return EQUIP_WEAPON
    
    else:
      user_info['equiped_weapon'] = sent_weapon_name
      save_user_data(user_info)
      update.message.reply_text(
      f"""
  ✅ *Weapon Equipped!*
  
  ━━━━━━━━━━━━━━━━━━━━
  
  You have successfully equipped the weapon:
  🗡️ *{sent_weapon_name.title()}*
  
  Get ready for battle, warrior!
  
  ━━━━━━━━━━━━━━━━━━━━
  """,
      parse_mode="Markdown"
  )
      return ConversationHandler.END
      
  else:
    update.message.reply_text(
    f"""
❌ *Invalid Weapon Name!*

━━━━━━━━━━━━━━━━━━━━

There is no such weapon .
Please double-check and send the correct weapon name.

━━━━━━━━━━━━━━━━━━━━
""",
    parse_mode="Markdown"
)
    return EQUIP_WEAPON
    
    

gear_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(my_gear_button, pattern='^(equip_weapon)$')
    ],
    states={
        EQUIP_WEAPON: [
            MessageHandler(Filters.text & ~Filters.command, equip_weapon)
        ],
    },
    fallbacks=[
        CommandHandler('cancel', cancel)
    ]
)
  
  
def view(update, context):
    user_info = init_user(update, context)
    
    # Check if weapon name argument is provided
    if len(context.args) < 1:
        update.message.reply_text(
            """🚫 *Oops! You're not using this command correctly.*

📌 Here's how to use it:  
`/view <weapon>`

🧪 *Example:*  
`/view Bronze Sword`

Try again using the correct format! 😊""",
            parse_mode="Markdown"
        )
        return
    
    item_to_view = ' '.join(context.args).title()

    # Check if weapon exists in master weapon list
    if item_to_view not in list(weapon_list.keys()):
        update.message.reply_text(
            """❌ *Invalid Weapon Name!*

━━━━━━━━━━━━━━━━━━━━  
It seems like the item you're trying to view doesn't exist.

🧠 *Tip:* Use the command like this:  
`/view Bronze Sword`

━━━━━━━━━━━━━━━━━━━━
""",
            parse_mode="Markdown"
        )
        return

    # If player does NOT own this weapon, show base info from weapon_list
    if item_to_view not in list(user_info.get('user_weapons', {}).keys()):
        weapon_data = weapon_list[item_to_view]
        update.message.reply_photo(
            photo=weapon_data['photo'],
            caption=f"""
🗡️ *Item Info*

━━━━━━━━━━━━━━━━━━━━

🔹 *Item:* `{item_to_view}`
🌟 *Rarity:* `{weapon_data['rarity'].title()}`

━━ ⚔️ *Weapon Stats* ⚔️ ━━

💥 *Power:* `{weapon_data['bonus_power']}`
❤️ *HP:* `{weapon_data['bonus_hp']}`
🏃 *Agility:* `{weapon_data['bonus_agility']}`

━━━━━━━━━━━━━━━━━━━━
""",
            parse_mode="Markdown"
        )
    else:
        # Player owns this weapon - show user-specific weapon info with EXP etc.
        weapon_data = user_info['user_weapons'].get(item_to_view, {})
        base_data = weapon_list[item_to_view]

        # Fallback keys for compatibility if you have different naming conventions in your code
        level = weapon_data.get('weapon_level', weapon_data.get('level', 1))
        xp = weapon_data.get('weapon_xp', weapon_data.get('exp', 0))
        max_xp = weapon_data.get('weapon_max_xp', level * 100)
        power = weapon_data.get('bonus_power', base_data.get('bonus_power', 0))
        hp = weapon_data.get('bonus_hp', base_data.get('bonus_hp', 0))
        agility = weapon_data.get('bonus_agility', base_data.get('bonus_agility', 0))
        rarity = base_data.get('rarity', 'unknown').title()
        photo = base_data.get('photo', None)

        update.message.reply_photo(
            photo=photo,
            caption=f"""
🗡️ *Item Info*

━━━━━━━━━━━━━━━━━━━━

🔹 *Item:* {item_to_view}
🌟 *Rarity:* {rarity}

━━ ⚔️ *Weapon Stats* ⚔️ ━━

💥 *Power:* {power}
❤️ *HP:* {hp}
🏃 *Agility:* {agility}

━━ 🧪 *Progress Stats* 🧪 ━━

📈 *Level:* {level}
🔸 *XP:* {xp}/{max_xp} (to Level {level+1})

━━━━━━━━━━━━━━━━━━━━
""",
            parse_mode="Markdown"
        )

      
def give(update, context):
    user_info = init_user(update, context)
   
    if len(context.args) < 2:
        update.message.reply_text(
            '''❌ **Oops! You used the command the wrong way.**  
To give an item, please use this format:  
➡️ /give item amount  

For example: /give essences 3  

Try again! ''')
        return
  
    if not update.message.reply_to_message:
        update.message.reply_text(
            '''You didn’t reply to anyone’s message.
Please reply to a message to use this command!''')
        return
  
    taker = update.message.reply_to_message.from_user
    giver = update.effective_user
  
    taker_data = db.search(UserQuery.user_id == taker.id)
    if not taker_data:
        update.message.reply_text(
            '''The user you replied to has not started the bot yet!
Please reply to a person who has started the bot.''')
        return
    
    item_to_give = context.args[0]
    
    if item_to_give not in ['essences', 'essence', 'moonshard', 'moonshards', 'coins', 'coin']:
      update.message.reply_text('You cannot give this item!')
      return

    if item_to_give in ['essence', 'moonshard', 'coin']:
      item_to_give += 's'
      pass
    try:
        amount_to_give = int(context.args[1])  # Convert amount to integer
    except ValueError:
        update.message.reply_text("❌ The amount must be a number!")
        return
  
    # Check if giver has enough items
    if user_info.get(item_to_give, 0) < amount_to_give:
        update.message.reply_text(
            f'''You do not have enough {item_to_give}''')
        return
    
    # Reduce giver's items
    user_info[item_to_give] -= amount_to_give

    # Get taker's full data (assuming taker_data is a list of dicts)
    taker_info = taker_data[0]
def create_hp_bar(current_hp, max_hp, length=10):
    """Create a visual HP bar"""
    filled = int((current_hp / max_hp) * length) if max_hp > 0 else 0

    empty = length - filled
    return "█" * filled + "░" * empty

def check_level_up(user_id):
    """
    Checks if user has enough XP to level up, applies stat bonus per level,
    supports multiple level-ups, and updates db. Returns new level if leveled up, else None.
    """
    user = db.get(UserQuery.user_id == user_id)
    if not user:
        return None

    # Safe defaults
    power_bonus = 5
    hp_bonus = 10
    agility_bonus = 2

    leveled_up = False
    new_level = user.get('level', 1)
    xp = user.get('xp', 0)
    max_xp = user.get('max_xp', 100)
    excess_xp = xp

    # Allow user to gain multiple levels in one go!
    while excess_xp >= max_xp:
        excess_xp -= max_xp
        new_level += 1
        max_xp += 50   # Put your formula here if you want something more advanced.
        leveled_up = True

    if leveled_up:
        db.update({
            'level': new_level,
            'xp': excess_xp,
            'max_xp': max_xp,
            'power': user.get('power', 50) + power_bonus,
            'max_hp': user.get('max_hp', 100) + hp_bonus,
            'hp': user.get('hp', 100) + hp_bonus,  # full heal with HP bonus
            'agility': user.get('agility', 200) + agility_bonus
        }, UserQuery.user_id == user_id)
        return new_level
    return None


def add_weapon_exp(user_id, exp_gained):
    user = db.get(UserQuery.user_id == user_id)
    equipped = user.get('equiped_weapon')
    
    if equipped and equipped in user.get('user_weapons', {}):
        weapon = user['user_weapons'][equipped]
        weapon['exp'] = weapon.get('exp', 0) + exp_gained
        weapon['level'] = weapon.get('level', 1)

        exp_needed = weapon['level'] * 100
        if weapon['exp'] >= exp_needed:
            weapon['level'] += 1
            weapon['exp'] -= exp_needed
            weapon['bonus_power'] = weapon.get('bonus_power', 0) + 3
            weapon['bonus_hp'] = weapon.get('bonus_hp', 0) + 5
            weapon['bonus_agility'] = weapon.get('bonus_agility', 0) + 1
        
        # ✅ Save updated weapons dict to DB
        db.update({'user_weapons': user['user_weapons']}, UserQuery.user_id == user_id)
        return weapon['level']
    return None


    # Add to taker's items
    taker_info[item_to_give] = taker_info.get(item_to_give, 0) + amount_to_give

    # Save both users' data (You need a function to update both in your DB)
    save_user_data(user_info)          # Save giver's updated data
    db.update(taker_info, UserQuery.user_id == taker.id)  # Save taker's updated data

    update.message.reply_text(
        f'Sent {amount_to_give} {item_to_give} to {taker.first_name}!')
        
def get_file_id(update, context):
    photo = update.message.photo[-1]  # get highest resolution photo
    file_id = photo.file_id
    update.message.reply_text(f"File ID: <code>{file_id}</code>",parse_mode=ParseMode.HTML)

def open_keyboard(update, context):
    # One persistent button
    explore_button = [[KeyboardButton("/explore")],[KeyboardButton("/mygear"),KeyboardButton("/close")]]
    
    open_markup = ReplyKeyboardMarkup(
        explore_button, 
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    update.message.reply_text(
        "Opened keyboard!",
        reply_markup=open_markup
    )



def remove_keyboard(update, context):
    update.message.reply_text(
        "Keyboard removed ✅",
        reply_markup=ReplyKeyboardRemove()
    )
# ==== PvP SYSTEM ====
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from tinydb import Query

UserQuery = Query()
# Global dict to store ongoing PvP battles per chat
pvp_battles = {}

def pvp_attack_button(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = update.effective_chat.id

    if chat_id not in pvp_battles:
        query.answer("No active PvP battle!", show_alert=True)
        return

    battle = pvp_battles[chat_id]

    if user_id != battle['turn']:
        query.answer("Wait for your turn!", show_alert=True)
        return

    if user_id == battle['player1']:
        my_label, enemy_id = 'player1', battle['player2']
    elif user_id == battle['player2']:
        my_label, enemy_id = 'player2', battle['player1']
    else:
        query.answer("You're not in this battle!", show_alert=True)
        return

    # Setup HP on first battle step
    if battle['hp1'] is None or battle['hp2'] is None:
        p1_info = db.get(UserQuery.user_id == battle['player1'])
        p2_info = db.get(UserQuery.user_id == battle['player2'])

        def get_battle_stats(user_info):
            eq = user_info.get('equiped_weapon')
            if eq and eq in user_info.get('user_weapons', {}):
                weapon = user_info['user_weapons'][eq]
                return {
                    'hp': user_info.get('hp', 100) + weapon.get('bonus_hp', 0),
                    'power': user_info.get('power', 50) + weapon.get('bonus_power', 0),
                    'agility': user_info.get('agility', 200) + weapon.get('bonus_agility', 0)
                }
            return {
                'hp': user_info.get('hp', 100),
                'power': user_info.get('power', 50),
                'agility': user_info.get('agility', 200)
            }

        p1_stats = get_battle_stats(p1_info)
        p2_stats = get_battle_stats(p2_info)

        battle['hp1'] = p1_stats['hp']
        battle['hp2'] = p2_stats['hp']
        battle['max_hp1'] = p1_stats['hp']
        battle['max_hp2'] = p2_stats['hp']

        if p1_stats['agility'] > p2_stats['agility']:
            battle['turn'] = battle['player1']
        elif p2_stats['agility'] > p1_stats['agility']:
            battle['turn'] = battle['player2']
        else:
            battle['turn'] = random.choice([battle['player1'], battle['player2']])

        pvp_battles[chat_id] = battle

    my_info = db.get(UserQuery.user_id == user_id)
    eq = my_info.get('equiped_weapon')
    if eq and eq in my_info.get('user_weapons', {}):
        atk = my_info.get('power', 50) + my_info['user_weapons'][eq].get('bonus_power', 0)
    else:
        atk = my_info.get('power', 50)

    if my_label == 'player1':
        battle['hp2'] -= atk
        hp_left = battle['hp2']
        max_hp = battle['max_hp2']
    else:
        battle['hp1'] -= atk
        hp_left = battle['hp1']
        max_hp = battle['max_hp1']

    enemy_info = db.get(UserQuery.user_id == enemy_id)
    safe_my_name = html.escape(my_info.get('username') or my_info.get('first_name', 'Player'))
    safe_enemy_name = html.escape(enemy_info.get('username') or enemy_info.get('first_name', 'Opponent'))

    def create_hp_bar(current_hp, max_hp, length=12):
        filled = int((current_hp / max_hp) * length) if max_hp > 0 else 0
        empty = length - filled
        return "█" * filled + "░" * empty

    hp_bar = create_hp_bar(max(hp_left, 0), max_hp, 12)
    hp_percentage = max(0, (hp_left / max_hp) * 100) if max_hp > 0 else 0

    # WIN/LOSE state
    if battle['hp1'] <= 0 or battle['hp2'] <= 0:
        if battle['hp1'] <= 0:
            winner_id, loser_id = battle['player2'], battle['player1']
        else:
            winner_id, loser_id = battle['player1'], battle['player2']

        winner_info = db.get(UserQuery.user_id == winner_id)
        loser_info = db.get(UserQuery.user_id == loser_id)
        safe_winner = html.escape(winner_info.get('username') or winner_info.get('first_name', 'Winner'))
        safe_loser = html.escape(loser_info.get('username') or loser_info.get('first_name', 'Loser'))

        win_xp, lose_xp = 75, 15
        weapon_exp_win, weapon_exp_lose = 35, 25
        db.update({'xp': winner_info.get('xp', 0) + win_xp}, UserQuery.user_id == winner_id)
        db.update({'xp': loser_info.get('xp', 0) + lose_xp}, UserQuery.user_id == loser_id)

        # Weapon exp, level up
        winner_weapon_level = add_weapon_exp(winner_id, weapon_exp_win)
        loser_weapon_level = add_weapon_exp(loser_id, weapon_exp_lose)
        winner_new_level = check_level_up(winner_id)
        loser_new_level = check_level_up(loser_id)

        db.update({'pvp_battles_won': winner_info.get('pvp_battles_won', 0) + 1}, UserQuery.user_id == winner_id)
        db.update({'pvp_battles_lost': loser_info.get('pvp_battles_lost', 0) + 1}, UserQuery.user_id == loser_id)
        db.update({'pvp_battles_played': winner_info.get('pvp_battles_played', 0) + 1}, UserQuery.user_id == winner_id)
        db.update({'pvp_battles_played': loser_info.get('pvp_battles_played', 0) + 1}, UserQuery.user_id == loser_id)

        victory_msg = f"💥 <b>{safe_my_name}</b> deals <b>{atk} damage</b>!\n\n"
        victory_msg += f"🏆 <b>{safe_winner} WINS THE DUEL!</b> 🏆\n"
        victory_msg += f"━━━━━━━━━━━━━━━━━━━━\n"
        victory_msg += f"🎯 <b>Battle Rewards:</b>\n"
        victory_msg += f"🥇 {safe_winner}: +{win_xp} XP\n"
        victory_msg += f"🥈 {safe_loser}: +{lose_xp} XP\n"
        if winner_weapon_level:
            victory_msg += f"⚔️ {safe_winner}'s weapon leveled up to Lv.{winner_weapon_level}!\n"
        if loser_weapon_level:
            victory_msg += f"⚔️ {safe_loser}'s weapon leveled up to Lv.{loser_weapon_level}!\n"
        if winner_new_level:
            victory_msg += f"🎉 {safe_winner} reached Level {winner_new_level}!\n"
        if loser_new_level:
            victory_msg += f"🎉 {safe_loser} reached Level {loser_new_level}!\n"
        victory_msg += f"\n🏅 GG! Well fought, warriors!"

        query.edit_message_text(victory_msg, parse_mode=ParseMode.HTML)
        del pvp_battles[chat_id]
        return

    # Continue battle
    battle_msg = f"⚔️ <b>{safe_my_name}</b> strikes!\n"
    battle_msg += f"💥 Deals <b>{atk} damage</b> to {safe_enemy_name}\n\n"
    battle_msg += f"❤️ <b>{safe_enemy_name}'s HP:</b> {max(hp_left, 0)}/{max_hp}\n"
    battle_msg += f"{hp_bar} <code>{hp_percentage:.0f}%</code>\n\n"
    battle_msg += f"🎯 <b>{safe_enemy_name}'s turn to attack!</b>"
    
    battle['turn'] = enemy_id
    pvp_battles[chat_id] = battle

    keyboard = [[InlineKeyboardButton("⚔️ Attack", callback_data="pvp_attack")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(battle_msg, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    query.answer()



def view_leaderboard(update, context):
    users = db.all()
    top = sorted(users, key=lambda u: u.get('pvp_battles_won', 0), reverse=True)[:10]
    msg = "🏆 PvP Leaderboard — Most Wins 🏆\n\n"
    
    if not top or all(u.get('pvp_battles_won', 0) == 0 for u in top):
        msg += "No battles fought yet."
    else:
        for i, u in enumerate(top, 1):
            wins = u.get('pvp_battles_won', 0)
            if wins == 0:
                break
            username = u.get('username') or u.get('first_name', 'Unknown')
            msg += f"{i}. {username} — {wins} wins\n"
    
    update.message.reply_text(msg)  # NO parse_mode to avoid markdown errors
def get_user_info_by_user_id(user_id, username=None):
    user_info = db.get(UserQuery.user_id == user_id)
    if not user_info:
        user_info = {
            'user_id': user_id,
            'username': username or f"user_{user_id}",
            'level': 1,
            'xp': 0,
            'coins': 1000,
            'agility': 200,
            'max_agility': 200,
            'power': 50,
            'hp': 100,
            'max_hp': 100,
            'user_weapons': {},
            'equiped_weapon': None,
            'pvp_battles_won': 0,
            'pvp_battles_lost': 0,
            'pvp_battles_played': 0,
            'weapon_exp_total': 0
        }
        db.insert(user_info)
    return user_info

def fix_missing_fields():
    """Patch database so every user has all required fields with safe defaults."""
    for user in db.all():
        updates = {}
        
        # Core profile
        if 'user_id' not in user:
            continue  # If somehow missing, skip (should never happen)
        if 'username' not in user:
            updates['username'] = f"user_{user['user_id']}"
        
        # Currency & resources
        if 'coins' not in user: 
          updates['coins'] = 1000
        if 'essences' not in user: updates['essences'] = 0
        if 'moonshards' not in user: updates['moonshards'] = 0
        
        # XP & progression
        if 'xp' not in user: updates['xp'] = 0
        if 'max_xp' not in user: updates['max_xp'] = 100
        if 'level' not in user: updates['level'] = 1
        
        # Stats
        if 'power' not in user: updates['power'] = 50
        if 'max_power' not in user: updates['max_power'] = 50
        if 'hp' not in user: updates['hp'] = 100
        if 'max_hp' not in user: updates['max_hp'] = 100
        if 'agility' not in user: updates['agility'] = 200
        if 'max_agility' not in user: updates['max_agility'] = 200
        
        # PvE stats
        if 'battles_played' not in user: updates['battles_played'] = 0
        if 'battles_won' not in user: updates['battles_won'] = 0
        if 'battles_lost' not in user: updates['battles_lost'] = 0
        if 'explores_won' not in user: updates['explores_won'] = 0
        if 'explores_lost' not in user: updates['explores_lost'] = 0
        if 'explores_played' not in user: updates['explores_played'] = 0
        
        # Equipment
        if 'user_weapons' not in user: updates['user_weapons'] = {}
        if 'equiped_weapon' not in user: updates['equiped_weapon'] = None
        
        # PvP stats
        if 'pvp_battles_won' not in user: updates['pvp_battles_won'] = 0
        if 'pvp_battles_lost' not in user: updates['pvp_battles_lost'] = 0
        if 'pvp_battles_played' not in user: updates['pvp_battles_played'] = 0
        
        # Weapon EXP system
        if 'weapon_exp_total' not in user: updates['weapon_exp_total'] = 0
        
        if updates:
            db.update(updates, UserQuery.user_id == user['user_id'])
    
    print("✅ Fixed missing fields for all users!")
def remove(update, context):
    user_info = init_user(update, context)
    if update.effective_user.id not in ADMINS:
        update.message.reply_text('You are not authorized for this cmd ')
        return

    if len(context.args) < 3:
        update.message.reply_text(
            '''*Please provide*
*User ID* :- _The user to which you want item to remove_
*Item* :- _The item you want to remove_
*Amount* :- _How much you want to remove_
            ''',
            parse_mode='Markdown')
        return

    try:
        target_userid = int(context.args[0])
        target_user_item = context.args[1]
        item_amount = int(context.args[2])
    except ValueError:
        update.message.reply_text("❌ Invalid arguments. Use `/remove <user_id> <item> <amount>`", parse_mode='Markdown')
        return

    result = db.search(UserQuery.user_id == target_userid)
    if not result:
        update.message.reply_text(f'No user with ID {target_userid} found.')
        return

    user_data = result[0]
    new_value = user_data.get(target_user_item, 0) - item_amount
    db.update({target_user_item: new_value}, UserQuery.user_id == target_userid)

    update.message.reply_text(f"""
*Item Successfully Removed!*

━━━━━━━━━━━━━━━━━━━━
👤 *User:* `{target_userid}`
📦 *Item:* `{target_user_item}`
➖ *Amount Removed:* `{item_amount}`
📊 *New Total:* `{new_value}`
━━━━━━━━━━━━━━━━━━━━
""", parse_mode="Markdown")

def mystats(update, context):
    user_info = init_user(update, context)
    user_id = user_info['user_id']

    # Refresh user data to get latest weapon progress
    fresh_user = db.get(UserQuery.user_id == user_id)
    if fresh_user:
        user_info = fresh_user

    username = user_info.get('username') or user_info.get('first_name', 'Player')
    level = user_info.get('level', 1)
    xp = user_info.get('xp', 0)
    max_xp = user_info.get('max_xp', 100)
    coins = user_info.get('coins', 0)
    power = user_info.get('power', 50)
    hp = user_info.get('hp', 100)
    agility = user_info.get('agility', 200)

    equipped = user_info.get('equiped_weapon')
    weapon_block = ""
    
    if equipped and equipped in user_info.get('user_weapons', {}):
        weapon = user_info['user_weapons'][equipped]
        weapon_level = weapon.get('level', 1)
        weapon_exp = weapon.get('exp', weapon.get('weapon_xp', 0))
        weapon_exp_needed = weapon_level * 100  # or your formula

        bonus_power = weapon.get('bonus_power', 0)
        bonus_hp = weapon.get('bonus_hp', 0)
        bonus_agility = weapon.get('bonus_agility', 0)

        total_power = power + bonus_power
        total_hp = hp + bonus_hp
        total_agility = agility + bonus_agility

        weapon_block = (
            f"\n🗡️ *Equipped Weapon:* {escape_markdown(equipped, version=2)}\n"
            f"    • Level: {weapon_level}\n"
            f"    • EXP: {weapon_exp}/{weapon_exp_needed}\n"
            f"    • Power Bonus: +{bonus_power}\n"
            f"    • HP Bonus: +{bonus_hp}\n"
            f"    • Agility Bonus: +{bonus_agility}"
        )
    else:
        # No weapon equipped or no weapon data
        total_power = power
        total_hp = hp
        total_agility = agility
        weapon_block = "\n🗡️ *No weapon equipped*"

    msg = (
        f"👤 *{escape_markdown(username, version=2)}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏅 *Level:* {level}\n"
        f"📈 *XP:* {xp}/{max_xp}\n"
        f"💰 *Coins:* {coins}\n"
        f"❤️ *HP:* {total_hp}\n"
        f"💪 *Power:* {total_power}\n"
        f"🏃‍♂️ *Agility:* {total_agility}\n"
        f"{weapon_block}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )

    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2)
    
def mystats(update, context):
    """Show player's stats including live updated weapon info."""
    user_info = init_user(update, context)
    user_id = user_info['user_id']

    # Refresh latest data from DB so weapon upgrades show instantly
    fresh_user = db.get(UserQuery.user_id == user_id)
    if fresh_user:
        user_info = fresh_user

    username = user_info.get('username') or user_info.get('first_name', 'Player')
    level = user_info.get('level', 1)
    xp = user_info.get('xp', 0)
    max_xp = user_info.get('max_xp', 100)
    coins = user_info.get('coins', 0)
    power = user_info.get('power', 50)
    hp = user_info.get('hp', 100)
    agility = user_info.get('agility', 200)

    equipped = user_info.get('equiped_weapon')
    if equipped and equipped in user_info.get('user_weapons', {}):
        weapon = user_info['user_weapons'][equipped]
        total_power = power + weapon.get('bonus_power', 0)
        total_hp = hp + weapon.get('bonus_hp', 0)
        total_agility = agility + weapon.get('bonus_agility', 0)

        weapon_block = (
            f"\n🗡️ *Equipped Weapon:* {escape_markdown(equipped)}\n"
            f"    • Level: {weapon.get('level', 1)}\n"
            f"    • EXP: {weapon.get('exp', 0)}/{weapon.get('level', 1) * 100}\n"
            f"    • Power Bonus: +{weapon.get('bonus_power', 0)}\n"
            f"    • HP Bonus: +{weapon.get('bonus_hp', 0)}\n"
            f"    • Agility Bonus: +{weapon.get('bonus_agility', 0)}"
        )
    else:
        total_power = power
        total_hp = hp
        total_agility = agility
        weapon_block = "\n🗡️ *No weapon equipped*"

    msg = (
        f"👤 *{escape_markdown(username)}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏅 *Level:* {level}\n"
        f"📈 *XP:* {xp}/{max_xp}\n"
        f"💰 *Coins:* {coins}\n"
        f"❤️ *HP:* {total_hp}\n"
        f"💪 *Power:* {total_power}\n"
        f"🏃‍♂️ *Agility:* {total_agility}\n"
        f"{weapon_block}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )

    update.message.reply_text(msg, parse_mode="MarkdownV2")
def handle_group_pvp(update, context):
    query = update.callback_query
    parts = query.data.split("_")

    # Defensive: ensure we have enough parts
    if len(parts) < 4:
        query.answer("Invalid PvP command.", show_alert=True)
        return

    action = parts[1]
    challenger_id = int(parts[2])  # FIX: correct index instead of int(parts)
    target_id = int(parts[3])      # FIX: proper index instead of asset nonsense
    clicker = query.from_user.id

    # Only the target player can accept/reject
    if clicker != target_id:
        query.answer("❌ You are not the challenged player!", show_alert=True)
        return

    if action == "accept":
        p1 = db.get(UserQuery.user_id == challenger_id)
        p2 = db.get(UserQuery.user_id == target_id)

        # Get agility with weapon bonus
        def get_agi(user):
            eq = user.get('equiped_weapon')
            bonus = 0
            if eq and eq in user.get('user_weapons', {}):
                bonus = user['user_weapons'][eq].get('bonus_agility', 0)
            return user.get('agility', 200) + bonus

        p1_agi = get_agi(p1)
        p2_agi = get_agi(p2)

        import random
        if p1_agi > p2_agi:
            first_player = challenger_id
            first_name = p1.get('username') or p1.get('first_name', '')
        elif p2_agi > p1_agi:
            first_player = target_id
            first_name = p2.get('username') or p2.get('first_name', '')
        else:
            first_player = random.choice([challenger_id, target_id])
            if first_player == challenger_id:
                first_name = p1.get('username') or p1.get('first_name', '')
            else:
                first_name = p2.get('username') or p2.get('first_name', '')

        chat_id = update.effective_chat.id
        # Init battle state
        pvp_battles[chat_id] = {
            'player1': challenger_id,
            'player2': target_id,
            'turn': first_player,
            'hp1': None,
            'hp2': None
        }

        p1_name = html.escape(p1.get('username') or p1.get('first_name', ''))
        p2_name = html.escape(p2.get('username') or p2.get('first_name', ''))
        first_name_safe = html.escape(first_name)

        # Start message
        battle_start_msg = f"""🔥 <b>Challenge Accepted!</b>

🏟 <b>Arena Battle Begins!</b>
━━━━━━━━━━━━━━━━━━━━
🥊 <b>{p1_name}</b> vs <b>{p2_name}</b>
⚡ Agility: {p1_agi} vs {p2_agi}

🏃‍♂️ <b>{first_name_safe}</b> moves first!
<i>({'Same agility – random start' if p1_agi == p2_agi else 'Higher agility starts first'})</i>"""

        # Attack button
        keyboard = [[InlineKeyboardButton("⚔️ Attack", callback_data="pvp_attack")]]
        query.edit_message_text(
            battle_start_msg,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

    elif action == "reject":
        query.edit_message_text("❌ Challenge rejected.")

def pvp_command(update, context):
    # Must reply to someone in a group
    if not update.message.reply_to_message:
        update.message.reply_text("⚠️ Reply to a player's message with /pvp to challenge them!")
        return

    challenger = update.effective_user
    target_user = update.message.reply_to_message.from_user

    if target_user.id == challenger.id:
        update.message.reply_text("❌ You can't challenge yourself!")
        return

    # Initialize both users in DB
    challenger_info = init_user(update, context)
    target_info = db.get(UserQuery.user_id == target_user.id)
    if not target_info:
        target_info = get_user_info_by_user_id(target_user.id, target_user.username)

    # Buttons
    keyboard = [[
        InlineKeyboardButton("✅ Accept", callback_data=f"pvp_accept_{challenger.id}_{target_user.id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"pvp_reject_{challenger.id}_{target_user.id}")
    ]]
    markup = InlineKeyboardMarkup(keyboard)
    text = (
        "🏟 *The Arena Calls!*\n\n"
        f"⚔️ *{challenger.first_name}* has challenged *{target_user.first_name}* to an epic duel!\n"
        "_Only one will emerge victorious..._\n\n"
        f"{target_user.first_name}, will you accept?"
    )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=markup,
        parse_mode=ParseMode.MARKDOWN
    )

#Handlers
dispatcher.add_handler(CommandHandler('reset_user',reset_user))
dispatcher.add_handler(CommandHandler('reset_all',reset_all))
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('explore', explore))
dispatcher.add_handler(CommandHandler('shop', shop))
dispatcher.add_handler(CommandHandler('guess',guess))
dispatcher.add_handler(CommandHandler('toss',toss))
dispatcher.add_handler(CommandHandler('mystats',stats))
dispatcher.add_handler(CommandHandler('myinventory',inventory))
dispatcher.add_handler(CommandHandler('add',add))
dispatcher.add_handler(CommandHandler('remove',remove))
dispatcher.add_handler(CommandHandler('view',view))
dispatcher.add_handler(CommandHandler('mygear',my_gear))
updater.dispatcher.add_handler(MessageHandler(Filters.photo, get_file_id))
dispatcher.add_handler(CommandHandler("open", open_keyboard))
dispatcher.add_handler(CommandHandler("close",remove_keyboard))
dispatcher.add_handler(conv_handler)
dispatcher.add_handler(shop_conv)
dispatcher.add_handler(weapon_conv_handler)
dispatcher.add_handler(gear_conv_handler)
dispatcher.add_handler(CommandHandler('give',give))
dispatcher.add_handler(CallbackQueryHandler(inv_button,pattern='^(inv_weapons|inv_magic|inv_main)$'))
dispatcher.add_handler(CallbackQueryHandler(button2,pattern='^(resource_shop|weapon_shop|magic_shop)$'))  # Handles shop buttons
dispatcher.add_handler(CallbackQueryHandler(button,pattern='^(attack|retreat)$'))   # Handles hunt/walk
dispatcher.add_handler(CallbackQueryHandler(explore_button,pattern='^(hunt)$'))
dispatcher.add_handler(CallbackQueryHandler(button4,pattern='^(heads|tails)$'))
dispatcher.add_handler(CallbackQueryHandler(button6,pattern='^(battle_stats|explore_stats|my_stats)$'))
dispatcher.add_handler(CallbackQueryHandler(my_gear_button,pattern='^(equip_weapon|edit_magic)$'))
# --- PvP Handlers ---
dispatcher.add_handler(CommandHandler('pvp', pvp_command))
dispatcher.add_handler(CallbackQueryHandler(handle_group_pvp, pattern=r'^pvp_(accept|reject)_'))
dispatcher.add_handler(CommandHandler('leaderboard', view_leaderboard))
dispatcher.add_handler(CallbackQueryHandler(pvp_attack_button, pattern='^pvp_attack$'))
# --- End PvP Handlers ---
updater.start_polling()
updater.idle()