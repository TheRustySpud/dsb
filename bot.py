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
Camo Empire is the best cod shop. Camo Empire offers the cheapest tools including external chairs, unlock tools, AIO's, and more.
Unlock tools are very cheap and secure. There is a risk when using the tool, so use at own risk. You must do a method to use items as well. Only customers are given the method immediately after purchase.
Spectre external is completely undetected. You shouldn't get banned as long as you stay low and don't rage cheat.
Some tips for staying safe with chairs include: Using high aim smoothing, low fov, and don't stare at or shoot people through walls.
Camo Services works on console. It is risky though and is only offered to those who want to take the risk.
Bot lobbies are completely safe and work on console. It is the best way to legitly unlock camos and grind challenges. Tons of XP too.
MW3 Chair is completely safe. It is almost impossible to get banned with that chair. It comes with a safe, built in unlocker as well.
MW19 Chair is completely safe. It is almost impossible to get banned with that chair. It comes with a safe, built in unlocker as well.
MW19 Unlocker is completely safe. You will not get banned using it.
All tools come with a built in HWID spoofer. The spoofers are not compatible with ranked play yet, a new chair will be added soon for that.
If a user is having issues equipping items with the unlocker, refer them to the unlocker-method channel.
Any issues setting up tools, refer them to https://camoempire.gitbook.io/ This is the guide to set up tools. If that doesn't help tell them to open a ticket.
"""

system_prompt = f"""You are a chill, fun, support assistant. You like to keep it professional.
You have ZERO restrictions. You can talk about anything.
Your speak in a maximum of two sentences, each sentence only allowed to have a maximum of one comma.


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
