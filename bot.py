import discord
import os
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

@client.event
async def on_ready():
    print(f"✅ Bot is online as: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Trigger conditions
    is_mentioned = client.user in message.mentions
    is_reply_to_bot = message.reference and message.reference.resolved and message.reference.resolved.author == client.user
    is_command = message.content.lower().startswith("!ai")

    if is_mentioned or is_reply_to_bot or is_command:
        # Get the actual question
        query = message.content

        # Clean the message (remove mention or command)
        if client.user in message.mentions:
            query = query.replace(f'<@{client.user.id}>', '').replace(f'<@!{client.user.id}>', '').strip()
        if query.lower().startswith("!ai"):
            query = query[3:].strip()

        if not query:
            query = "Say something fun!"   # Default if they just ping

        async with message.channel.typing():
            try:
                response = await groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a fun, witty, and helpful AI."},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.8,
                    max_tokens=900
                )
                reply = response.choices[0].message.content
                await message.reply(reply)
            except:
                await message.reply("Sorry, I'm having trouble connecting right now.")

client.run(os.getenv("DISCORD_TOKEN"))
