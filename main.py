
import os
import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

TOKEN = os.getenv("TOKEN")

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content == "!안녕":
        await message.channel.send("안녕하세요!")

client.run(TOKEN)
