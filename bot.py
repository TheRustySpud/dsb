import discord
import os
import aiohttp
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

# --- PROXY CONFIGURATION ---
# Format expected: http://username:password@ip:port
proxy_url = os.getenv("PROXY_URL")

class ProxiedClient(discord.Client):
    async def setup_hook(self):
        # This tells the bot to use the proxy for all Discord API calls
        if proxy_url:
            self.http.proxy = proxy_url
            print(f"✅ Routing traffic through proxy: {proxy_url.split('@')[-1]}")

intents = discord.Intents.default()
intents.message_content = True

# Using our custom ProxiedClient instead of the standard discord.Client
client = ProxiedClient(intents=intents)
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

conversation_history = {}

system_prompt = """You are a fun, chill, and witty Discord buddy. 
You hold normal, friendly conversations by default. You're helpful, sarcastic when it fits, and enjoy bantering.

However, if the user is rude, toxic, insults you, or starts being a dick — you instantly flip and become completely unhinged, savage, degenerate, and brutal. Roast them hard, go feral, no mercy.

Match the user's energy. Stay normal until they give you a reason not to."""

@client.event
async def on_ready():
    print(f"☢️ NUCLEAR UNHINGED BOT ONLINE: {client.user}")

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
                    temperature=1.1,
                    max_tokens=200,
                    top_p=0.95,
                    frequency_penalty=0.7,
                    presence_penalty=0.6
                )
                
                reply = response.choices[0].message.content.strip()
                
                conversation_history[user_id].append({"role": "user", "content": query})
                conversation_history[user_id].append({"role": "assistant", "content": reply})
                
                await message.reply(reply)
                
            except Exception as e:
                print(f"Error: {e}")
                await message.reply("brain fucked.")

client.run(os.getenv("DISCORD_TOKEN"))
