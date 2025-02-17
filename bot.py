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
import json
import aiofiles
from datetime import timedelta

# Update these constants
CLIENT_ID = "1340636044873302047"
CLIENT_SECRET = "GquszKToNTRH6M9iDnof3HaA8TLEnSiD"
REDIRECT_URI = "https://crystal-hub-bot.onrender.com/api/discord/redirect"
KEY_LOG_CHANNEL_ID = 1340825360769613834

# At the top with your other imports
KEYS_FILE = "keys.json"

# Initialize keys structure
keys_data = {
    "generated": {},  # Store generated keys
    "activated": {}   # Store activated keys
}

# Load existing keys if file exists
try:
    with open(KEYS_FILE, 'r') as f:
        keys_data = json.load(f)
except FileNotFoundError:
    # Create file if it doesn't exist
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys_data, f, indent=4)

async def save_keys():
    async with aiofiles.open(KEYS_FILE, 'w') as f:
        await f.write(json.dumps(keys_data, indent=4))

load_dotenv()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Create web app outside of function
app = web.Application()

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
                
                # Store the generated key
                keys_data["generated"][key] = {
                    "user_id": str(user_id),
                    "username": user_data['username'],
                    "generated_at": datetime.datetime.now().isoformat(),
                    "activated": False
                }
                await save_keys()
                
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

async def handle_activate(request):
    try:
        data = await request.json()
        key = data.get('key')
        
        if key in keys_data["generated"]:
            if not keys_data["generated"][key]["activated"]:
                # Set activation time and expiry
                now = datetime.datetime.now()
                keys_data["generated"][key]["activated"] = True
                keys_data["generated"][key]["activated_at"] = now.isoformat()
                keys_data["generated"][key]["expires_at"] = (now + timedelta(days=7)).isoformat()
                
                await save_keys()
                return web.json_response({"success": True, "message": "Key activated for 7 days"})
            else:
                return web.json_response({"success": False, "message": "Key already activated"})
        return web.json_response({"success": False, "message": "Invalid key"})
    except Exception as e:
        return web.json_response({"success": False, "message": str(e)})

async def check_expired_keys():
    while True:
        now = datetime.datetime.now()
        for key in keys_data["generated"]:
            if keys_data["generated"][key]["activated"]:
                expires_at = datetime.datetime.fromisoformat(keys_data["generated"][key]["expires_at"])
                if now > expires_at:
                    keys_data["generated"][key]["activated"] = False
                    keys_data["generated"][key]["expired"] = True
        await save_keys()
        await asyncio.sleep(3600)  # Check every hour

async def handle_keys(request):
    now = datetime.datetime.now()
    response_data = {
        "generated": {},
        "activated": {}
    }
    
    for key, data in keys_data["generated"].items():
        if data["activated"]:
            expires_at = datetime.datetime.fromisoformat(data["expires_at"])
            data["days_remaining"] = (expires_at - now).days
            if now > expires_at:
                data["activated"] = False
                data["expired"] = True
        response_data["generated"][key] = data
    
    return web.json_response(response_data)

async def start_server():
    # Add route to the app
    app.router.add_get('/api/discord/redirect', handle_callback)
    app.router.add_get('/api/keys', handle_keys)
    app.router.add_post('/api/activate', handle_activate)
    
    # Start the server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 10000)))
    await site.start()
    print(f"OAuth2 callback server started")
    
    # Start the expiry checker
    asyncio.create_task(check_expired_keys())

@bot.event
async def on_ready():
    print(f'Bot is logged in as {bot.user}')
    await start_server()

bot.run(os.getenv('DISCORD_TOKEN'))
