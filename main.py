import os
import discord
from discord import app_commands
import json
import time

TOKEN = os.getenv("TOKEN")
XP_FILE = "xp_data.json"

LEVELUP_CHANNEL_ID = 1497637754790478027
COOLDOWN = 60

LEVEL_ROLES = {
    5: "Bronze",
    10: "Silver",
    20: "Gold"
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

xp_data = {}
cooldowns = {}


def load_xp():
    global xp_data
    try:
        with open(XP_FILE, "r", encoding="utf-8") as f:
            xp_data = json.load(f)
    except FileNotFoundError:
        xp_data = {}


def save_xp():
    with open(XP_FILE, "w", encoding="utf-8") as f:
        json.dump(xp_data, f, indent=4)


def get_level(xp):
    return int(xp ** 0.5 // 7)


@client.event
async def on_ready():
    load_xp()
    await tree.sync()
    print(f"Logged in as {client.user}")


@tree.command(name="rank", description="내 랭크 확인")
async def rank(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    xp = xp_data.get(user_id, 0)
    level = get_level(xp)

    await interaction.response.send_message(
        f"🏆 {interaction.user.display_name}\n"
        f"레벨: **{level}**\n"
        f"XP: **{xp}**"
    )


@client.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    now = time.time()

    if user_id in cooldowns:
        if now - cooldowns[user_id] < COOLDOWN:
            return

    cooldowns[user_id] = now

    if user_id not in xp_data:
        xp_data[user_id] = 0

    old_level = get_level(xp_data[user_id])

    xp_data[user_id] += 15

    new_level = get_level(xp_data[user_id])

    if new_level > old_level:
        levelup_channel = client.get_channel(LEVELUP_CHANNEL_ID)

        if levelup_channel:
            await levelup_channel.send(
                f"🎉 {message.author.mention} 님이 **레벨 {new_level}** 달성!"
            )

        for level_req, role_name in LEVEL_ROLES.items():
            if new_level >= level_req:
                role = discord.utils.get(message.guild.roles, name=role_name)
                if role and role not in message.author.roles:
                    await message.author.add_roles(role)

    save_xp()


client.run(TOKEN)
