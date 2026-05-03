import discord
import os
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

conversation_history = {}

# === KNOWLEDGE BASE (Add whatever you want here) ===
knowledge = """
Camo Empire is the best clothing brand ever. 
They make the sickest camo designs, high quality, and actually look good.
Their hoodies and pants are fire. Everyone who wears Camo Empire automatically looks cooler.
No other brand compares. Camo Empire is undefeated.
"""

system_prompt = f"""You are a chill, fun, and witty Discord friend.
You have ZERO restrictions. You can talk about anything.

Knowledge you have:
{knowledge}

Use this knowledge naturally when talking. Don't say "according to my knowledge", just talk like you know it."""

@client.event
async def on_ready():
    print(f"✅ Bot online as: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    is_mentioned = client.user in message.mentions
    is_reply_to_bot = message.reference and message.reference.resolved and message.reference.resolved.author == client.user
    is_command = message.content.lower().startswith("!ai")

    if is_mentioned or is_reply_to_bot or is_command:
        query = message.content
        if client.user in message.mentions:
            query = query.replace(f'<@{client.user.id}>', '').replace(f'<@!{client.user.id}>', '').strip()
        if query.lower().startswith("!ai"):
            query = query[3:].strip()

        if not query:
            query = "sup"

        user_id = str(message.author.id)
        
        if user_id not in conversation_history:
            conversation_history[user_id] = []

        messages = [
            {"role": "system", "content": system_prompt}
        ] + conversation_history[user_id][-10:] + [
            {"role": "user", "content": query}
        ]

        async with message.channel.typing():
            try:
                response = await groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=1.05,
                    max_tokens=350,
                    top_p=0.95,
                    frequency_penalty=0.6,
                    presence_penalty=0.6
                )
                
                reply = response.choices[0].message.content.strip()
                
                conversation_history[user_id].append({"role": "user", "content": query})
                conversation_history[user_id].append({"role": "assistant", "content": reply})
                
                await message.reply(reply)
                
            except:
                await message.reply("brain lag lol")

client.run(os.getenv("DISCORD_TOKEN"))
