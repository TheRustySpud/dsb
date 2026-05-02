import discord
import os
from dotenv import load_dotenv

load_dotenv()

print("DISCORD_TOKEN exists:", bool(os.getenv("DISCORD_USER_TOKEN")))
print("GROQ_API_KEY exists:", bool(os.getenv("GROQ_API_KEY")))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents, self_bot=True)

@client.event
async def on_ready():
    print(f"✅ Successfully logged in as {client.user}")

client.run(os.getenv("DISCORD_USER_TOKEN"))
