import discord
import os
import asyncio
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

TRIGGER = "!ai"
MODEL = "llama-3.3-70b-versatile"

client = discord.Client(intents=discord.Intents.all(), self_bot=True)

groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

@client.event
async def on_ready():
    print(f"✅ Bot running as: {client.user}")

@client.event
async def on_message(message):
    if message.author.id != client.user.id:
        if message.content.lower().startswith(TRIGGER):
            query = message.content[len(TRIGGER):].strip()
            if not query:
                return

            async with message.channel.typing():
                try:
                    response = await groq_client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {"role": "system", "content": "You are a helpful and fun AI."},
                            {"role": "user", "content": query}
                        ],
                        temperature=0.7,
                        max_tokens=800
                    )
                    reply = response.choices[0].message.content
                    await message.reply(reply[:1900])
                except:
                    await message.reply("Sorry, I'm having trouble right now.")

client.run(os.getenv("DISCORD_USER_TOKEN"))
