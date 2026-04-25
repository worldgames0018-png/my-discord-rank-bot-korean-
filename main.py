import os
import discord
import json
import time

TOKEN = os.getenv("TOKEN")
XP_FILE = "xp_data.json"

LEVELUP_CHANNEL_ID = 1497637754790478027  # 레벨업 알림 채널 ID
COOLDOWN = 60  # XP 쿨다운(초)

LEVEL_ROLES = {
    5: "Bronze",
    10: "Silver",
    20: "Gold"
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

xp_data = {}
cooldowns = {}


# XP 파일 불러오기
def load_xp():
    global xp_data
    try:
        with open(XP_FILE, "r", encoding="utf-8") as f:
            xp_data = json.load(f)
    except FileNotFoundError:
        xp_data = {}


# XP 저장
def save_xp():
    with open(XP_FILE, "w", encoding="utf-8") as f:
        json.dump(xp_data, f, indent=4)


# 레벨 계산
def get_level(xp):
    return int(xp ** 0.5 // 5)


@client.event
async def on_ready():
    load_xp()
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    now = time.time()

    # /rank 대신 !rank 명령어
    if message.content == "!rank":
        xp = xp_data.get(user_id, 0)
        level = get_level(xp)

        await message.channel.send(
            f"🏆 {message.author.display_name}\n"
            f"레벨: **{level}**\n"
            f"XP: **{xp}**"
        )
        return

    # XP 쿨다운
    if user_id in cooldowns:
        if now - cooldowns[user_id] < COOLDOWN:
            return

    cooldowns[user_id] = now

    # XP 지급
    if user_id not in xp_data:
        xp_data[user_id] = 0

    old_level = get_level(xp_data[user_id])

    xp_data[user_id] += 15

    new_level = get_level(xp_data[user_id])

    # 레벨업 처리
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
