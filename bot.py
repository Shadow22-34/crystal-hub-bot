import discord
from discord.ext import commands
from aiohttp import web
import asyncio
from urllib.parse import urlencode
import aiohttp
import random
import datetime
import os
from dotenv import load_dotenv

# Update these constants
CLIENT_ID = "1340636044873302047"
CLIENT_SECRET = "GquszKToNTRH6M9iDnof3HaA8TLEnSiD"
REDIRECT_URI = "https://crystal-hub-bot.onrender.com/api/discord/redirect"
KEY_LOG_CHANNEL_ID = 1340825360769613834

load_dotenv()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

async def handle_callback(request):
    try:
        code = request.query.get('code')
        if not code:
            return web.Response(text="No code provided")
        
        async with aiohttp.ClientSession() as session:
            token_url = "https://discord.com/api/oauth2/token"
            data = {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI
            }
            
            async with session.post(token_url, data=data) as resp:
                if resp.status != 200:
                    return web.Response(text="Failed to get token")
                token_data = await resp.json()
                
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}"
            }
            async with session.get("https://discord.com/api/users/@me", headers=headers) as resp:
                if resp.status != 200:
                    return web.Response(text="Failed to get user info")
                user_data = await resp.json()
                
                user_id = int(user_data['id'])
                key = f"CRYSTAL-{random.randint(100000, 999999)}"
                
                user = bot.get_user(user_id)
                if user:
                    try:
                        user_embed = discord.Embed(
                            title="Crystal Hub Key",
                            description=f"Here's your key: `{key}`",
                            color=discord.Color.green()
                        )
                        await user.send(embed=user_embed)
                        
                        channel = bot.get_channel(KEY_LOG_CHANNEL_ID)
                        if channel:
                            log_embed = discord.Embed(
                                title="New Key Generated",
                                description=f"User: {user.mention}\nKey: `{key}`",
                                color=discord.Color.blue(),
                                timestamp=datetime.datetime.now()
                            )
                            log_embed.set_footer(text=f"User ID: {user.id}")
                            await channel.send(f"🔑 New key generated for {user.mention}", embed=log_embed)
                            print(f"Key sent to channel for user {user.name}")
                        else:
                            print(f"Could not find channel with ID {KEY_LOG_CHANNEL_ID}")
                            
                        return web.Response(text="Success! Check your Discord DMs for your key.")
                    except Exception as e:
                        print(f"Error sending messages: {e}")
                        return web.Response(text="Error sending messages. Please ensure your DMs are open.")
                
                return web.Response(text="Could not find user.")
    except Exception as e:
        print(f"Error in callback: {e}")
        return web.Response(text="An error occurred")

async def start_server():
    app = web.Application()
    app.router.add_get('/api/discord/redirect', handle_callback)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv('PORT', 3000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"OAuth2 callback server started on port {port}")

@bot.event
async def on_ready():
    print(f'Bot is logged in as {bot.user}')
    await start_server()

bot.run(os.getenv('DISCORD_TOKEN'))
