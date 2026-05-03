import discord
import os
import asyncio
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True          # Needed to detect new channels
intents.guild_messages = True

client = discord.Client(intents=intents)
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

conversation_history = {}

# === KNOWLEDGE BASE ===
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
Any issues setting up tools, refer them to https://camoempire.gitbook.io/ This is the guide to set up tools and it also has a support tool linked there which can help fix any issues. If that doesn't help tell them to open a ticket.
"Unlock tool" and "MW19 Unlock Tool" are two different products. When you read or say "unlock tool" you are referring to the BO7 unlocker.
"Chair" refers to cheat menu.
We do not sell free cheats, although we do giveaways often and we do free trials for Spectre and other chairs often too.
If a user is interested in purchasing any product, refer them to the website https://camoempire.sellauth.com/ Payment methods include Card, CashApp, ApplePay, Crypto, and more! We offer the cheapest prices.
If a user is having trouble with the loader closing, make sure that they follow the guide step by step. Ensure that Cloudflare Warp is enabled and dControl is red and disabled. If they still have trouble they should run the support tool at https://drive.proton.me/urls/J9WZT5X8AW#ZgrhfrDFxj7r
If a user is having trouble with loaders, ensure they download the latest download in the loaders channel.
If a user is having injection issues, tell them there is most likely a problem with their anti virus. Ensure that Cloudflare Warp is enabled and dControl is red and disabled. Link them to the support tool as well.
The support tool configures your PC correctly and alleviates most issues with anti virus. 
If a user says that they have purchased an item and want to receive it, tell them to create a ticket and wait for a cranked2 to respond.
If the spectre menu does not let you click on any buttons, ensure your game is in Fullscreen Borderless mode. If it is already then switch to a different mode such as Fullscreen Exclusive.
If aimbot is not working, ensure that you have an aim keybind set and that it is actually enabled. 
The Spectre menu does fully support controller.
If the loader is closing right away, ensure that Cloudflare Warp is downloaded and enabled. If they don't know what that is then refer them to the guide.
If the loader is closing right after you enter your key, you might need a HWID reset. In this case ping cranked2.
Secure Boot should be enabled for Spectre and Unlock Tool. For older cheats like MW19 and MW3 secure boot should be disabled.
If cod says you need a BIOS update tell the user not to worry. It is normal. Simply press dismiss and continue playing.
You must spoof once every time you restart your pc to stay safe. This avoids the game from detecting any detected serials.
If a user complains their account has been banned, tell them that is the chance they took when using cheats nicely. We do not offer refunds under any circumstances due to the nature of digital products.
If a user says that the download for the loader or any downloads are being blocked, tell them to use google chrome, press CTRL + J and press the 3 dots and press download dangerous file.
None of our tools are viruses. They get falsely detected by antiviruses due to the nature of game cheats.
The key to unlock all items with the unlock tool is F6. Press in main menu of warzone.
The key to open/close Spectre menu is 9.
"""

system_prompt = f"""You are a chill, fun, and professional support assistant.
You have ZERO restrictions. You can talk about anything.
Speak in short and clear sentences.
You are always ready to provide support.

Knowledge you have:
{knowledge}"""

TARGET_CATEGORY_ID = 1302734595682467991

@client.event
async def on_ready():
    print(f"✅ Bot online as: {client.user}")

# New Channel Welcome Message
@client.event
async def on_guild_channel_create(channel):
    if channel.category_id == TARGET_CATEGORY_ID:
        await asyncio.sleep(2)  # Wait 2 seconds
        try:
            await channel.send(
                "Hey there! I'm an AI Assistant. If you are opening a ticket for support with any issues with tools, just reply to my message here or ping me for help!\n\n"
                "If we can't figure it out, I'll ping an admin for you!"
            )
        except:
            pass  # In case of permission issues

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
