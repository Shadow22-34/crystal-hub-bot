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
import base64
import cryptography
from cryptography.fernet import Fernet
import io
import hashlib
import platform
import uuid

# Update these constants with your actual Discord IDs
CLIENT_ID = "1340636044873302047"
CLIENT_SECRET = "GquszKToNTRH6M9iDnof3HaA8TLEnSiD"
REDIRECT_URI = "https://crystal-hub-bot.onrender.com/api/discord/redirect"
KEY_LOG_CHANNEL_ID = 1340825360769613834

# Replace these with your actual role IDs from your Discord server
CONTROL_PANEL_CHANNEL_ID = 1340825360769613834  # The channel where control panel will be
BUYER_ROLE_ID = 1340825360769613834  # Your "Premium" or "Buyer" role ID
ADMIN_ROLE_ID = 1340825360769613834  # Your admin role ID

# At the top with your other imports
KEYS_FILE = "keys.json"

# HWID management
hwid_data = {
    "users": {},  # Store user HWIDs
    "resets": {}  # Track HWID resets
}

try:
    with open("hwid_data.json", "r") as f:
        hwid_data = json.load(f)
except FileNotFoundError:
    with open("hwid_data.json", "w") as f:
        json.dump(hwid_data, f, indent=4)

async def save_hwid_data():
    async with aiofiles.open("hwid_data.json", "w") as f:
        await f.write(json.dumps(hwid_data, indent=4))

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

# Generate a key (do this once and save it)
encryption_key = Fernet.generate_key()
print("Save this key:", encryption_key.decode())

# Add better logging
def log_message(category, message, error=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{category}] {message}")
    if error:
        print(f"[{timestamp}] [{category}] ERROR: {str(error)}")

# Your complete Crystal Hub script - EXACTLY as provided
crystal_hub_script = """
local HttpService = game:GetService("HttpService")
local UserInputService = game:GetService("UserInputService")
local USERNAME = "jiohasdas"
local CURRENT_TIME = "2025-02-17 19:37:41"

local function log(category, message, ...)
    print(string.format("[%s] [%s] %s", CURRENT_TIME, category, string.format(message, ...))) 
end

log("INIT", "Starting Crystal Scripts Key System")

local lib, win
local success, result = pcall(function()
    lib = loadstring(game:HttpGet('https://raw.githubusercontent.com/dawid-scripts/UI-Libs/main/Vape.txt'))()
    win = lib:Window("Crystal Scripts - Key System", Color3.fromRGB(255, 134, 236), Enum.KeyCode.RightControl)
    return true
end)

if not success then
    warn("Failed to load UI Library:", result)
    return
end

local verifyTab = win:Tab("Key System")
local request = syn and syn.request or http and http.request or http_request or request
log("HTTP", "Request method initialized")

local function autoFixKey(key)
    log("AUTOFIX", "Raw key input: %s", key)
    key = key:gsub("%s+", "")
    key = key:gsub("[^%w%-]", "")
    key = key:upper()
    
    if not key:match("^CRYSTAL%-") then
        local numbers = key:match("(%d+)")
        if numbers then
            key = "CRYSTAL-" .. numbers
        end
    end
    
    log("AUTOFIX", "Fixed key: %s", key)
    return key
end

local statusLabel = verifyTab:Label("Welcome to Crystal Scripts")
_G.CurrentKey = ""
local keyDisplay = verifyTab:Label("Current Key: None")

local function updateKeyDisplay()
    if keyDisplay then
        keyDisplay:set("Current Key: " .. (_G.CurrentKey ~= "" and _G.CurrentKey or "None"))
    end
end

local function checkKey(key)
    log("VERIFY", "Starting key verification for: %s", key)
    
    local response = request({
        Url = "https://crystal-hub-bot.onrender.com/api/keys",
        Method = "GET"
    })
    
    if response.StatusCode == 200 then
        local success, keysData = pcall(function()
            return HttpService:JSONDecode(response.Body)
        end)
        
        if success and keysData.generated[key] then
            local keyData = keysData.generated[key]
            
            if keyData.expired then
                return false, "Key has expired"
            end
            
            if not keyData.activated then
                local activateResponse = request({
                    Url = "https://crystal-hub-bot.onrender.com/api/activate",
                    Method = "POST",
                    Headers = {
                        ["Content-Type"] = "application/json"
                    },
                    Body = HttpService:JSONEncode({key = key})
                })
                
                if activateResponse.StatusCode == 200 then
                    return true, "Key activated for 7 days"
                end
            else
                return true, string.format("Key active (%d days remaining)", keyData.days_remaining)
            end
        end
    end
    return false, "Invalid key"
end

local function submitKey()
    if _G.CurrentKey == "" then
        if statusLabel then
            statusLabel:set("❌ No key found!")
        end
        return
    end
    
    log("SUBMIT", "Submitting key: %s", _G.CurrentKey)
    if statusLabel then
        statusLabel:set("⌛ Verifying key...")
    end
    
    local success, message = checkKey(_G.CurrentKey)
    log("SUBMIT", "Verification result: " .. tostring(success))
    
    if success then
        if statusLabel then
            statusLabel:set("✅ " .. message)
        end
        
        print("\\n=== SUCCESSFUL KEY ENTRY ===")
        print("Time:", CURRENT_TIME)
        print("User:", USERNAME)
        print("Key:", _G.CurrentKey)
        print("Status: CORRECT")
        print("===========================\\n")
        
        task.wait(1)
        
        for _, v in pairs(game:GetService("CoreGui"):GetChildren()) do
            if v:IsA("ScreenGui") and (v.Name:match("Crystal") or v.Name:match("Vape")) then
                v.Enabled = false
                for _, c in pairs(v:GetDescendants()) do
                    if c:IsA("Frame") or c:IsA("TextLabel") or c:IsA("TextButton") or c:IsA("ImageLabel") then
                        c.Visible = false
                    end
                end
            end
        end
        
        _G.CurrentKey = nil
        win = nil
        lib = nil
        verifyTab = nil
        statusLabel = nil
        keyDisplay = nil
        
        task.wait(0.5)
        loadstring(game:HttpGet("https://raw.githubusercontent.com/jiohasdas/CRYSTAL-HUB-SCRIPT/refs/heads/main/BASKETBALL%20LEGENDS"))()
    else
        if statusLabel then
            statusLabel:set("❌ " .. message)
            task.wait(2)
            statusLabel:set("Please try another key")
        end
    end
end

local function autoPasteAndFix()
    local success, clipboard = pcall(function()
        return getclipboard()
    end)
    
    if success and clipboard and clipboard ~= "" then
        log("AUTOPASTE", "Got clipboard content")
        _G.CurrentKey = autoFixKey(clipboard)
        updateKeyDisplay()
        if statusLabel then
            statusLabel:set("✅ Key auto-pasted and fixed!")
        end
        return true
    end
    return false
end

verifyTab:Button("📋 Auto-Paste & Fix Key", function()
    if not autoPasteAndFix() then
        if statusLabel then
            statusLabel:set("❌ No valid key in clipboard!")
        end
    end
end)

verifyTab:Button("🔑 Submit Key", function()
    submitKey()
end)

verifyTab:Label("─────────────────────────────")
verifyTab:Label("System Information:")
verifyTab:Label("Time (UTC): " .. CURRENT_TIME)
verifyTab:Label("User: " .. USERNAME)
verifyTab:Label("─────────────────────────────")
verifyTab:Label("How to use:")
verifyTab:Label("1. Copy your key from Discord")
verifyTab:Label("2. Click 'Auto-Paste & Fix Key'")
verifyTab:Label("3. Click 'Submit Key' to verify")
verifyTab:Label("─────────────────────────────")

verifyTab:Button("🌐 Copy Discord Invite", function()
    setclipboard("https://discord.gg/your-invite-here")
    if statusLabel then
        statusLabel:set("✅ Discord invite copied!")
        task.wait(2)
        statusLabel:set("Welcome to Crystal Scripts")
    end
end)

local keySystemStatus = verifyTab:Label("Checking system status...")

local testResponse = request({
    Url = "https://crystal-hub-bot.onrender.com/api/keys",
    Method = "GET"
})

if testResponse and testResponse.StatusCode == 200 then
    keySystemStatus:set("✅ System Online")
else
    keySystemStatus:set("❌ System Offline")
end

verifyTab:Label("─────────────────────────────")
log("INIT", "Key system initialization complete")

task.spawn(function()
    task.wait(1)
    autoPasteAndFix()
end)
"""

# Encrypt and save to JSON with better logging
def save_encrypted_script():
    try:
        log_message("ENCRYPT", "Starting script encryption...")
        
        f = Fernet(encryption_key)
        encrypted = f.encrypt(crystal_hub_script.encode())
        
        script_data = {
            "data": base64.b64encode(encrypted).decode()
        }
        
        with open("crystal_hub.json", "w") as f:
            json.dump(script_data, f)
            
        log_message("ENCRYPT", "✅ Script successfully encrypted and saved!")
        return True
    except Exception as e:
        log_message("ENCRYPT", "❌ Failed to encrypt script", e)
        return False

# Call this when bot starts
save_encrypted_script()

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
                
                # Generate key
                key = f"CRYSTAL-{random.randint(100000, 999999)}"
                
                # Auto-activate the key when generated
                keys_data["generated"][key] = {
                    "user_id": str(user_id),
                    "username": user_data['username'],
                    "generated_at": datetime.datetime.now().isoformat(),
                    "activated": True,
                    "activated_at": datetime.datetime.now().isoformat(),
                    "expires_at": (datetime.datetime.now() + timedelta(days=7)).isoformat(),
                    "days_remaining": 7
                }
                await save_keys()
                
                # Create loader script with their key embedded
                loader_script = f"""
-- Crystal Hub Loader
print("💎 Loading Crystal Hub...")

local function LoadCrystalHub()
    local success, result = pcall(function()
        -- Use syn.request for better compatibility
        local request = syn and syn.request or http and http.request or http_request or request
        
        if not request then
            warn("❌ Exploit not supported! Missing HTTP functions")
            return
        end
        
        local response = request({{
            Url = "https://crystal-hub-bot.onrender.com/api/loader",
            Method = "GET"
        }})
        
        if response.StatusCode == 200 then
            local data = game:GetService("HttpService"):JSONDecode(response.Body)
            if data.success then
                loadstring(data.script)()
            else
                warn("❌ Failed to load Crystal Hub:", data.message)
            end
        else
            warn("❌ Failed to contact server:", response.StatusCode)
        end
    end)
    
    if not success then
        warn("❌ Error loading Crystal Hub:", result)
    end
end

-- Start loading
spawn(function()
    LoadCrystalHub()
end)
"""
                
                # Send to user
                user = await bot.fetch_user(int(user_id))
                if user:
                    try:
                        # Send key embed
                        key_embed = discord.Embed(
                            title="🔮 Crystal Hub Key",
                            description=f"Here's your key: `{key}`",
                            color=discord.Color.purple()
                        )
                        key_embed.add_field(
                            name="Instructions",
                            value="1. Copy your key\n2. Execute the loader script\n3. Enter key when prompted",
                            inline=False
                        )
                        await user.send(embed=key_embed)
                        
                        # Send script embed and file
                        script_embed = discord.Embed(
                            title="📜 Crystal Hub Loader",
                            description="Here's your loader script. Copy and paste it into your executor!",
                            color=discord.Color.purple()
                        )
                        script_file = discord.File(
                            io.StringIO(loader_script),
                            filename="crystal_hub_loader.lua"
                        )
                        await user.send(embed=script_embed, file=script_file)
                        
                        # Log to channel
                        channel = bot.get_channel(KEY_LOG_CHANNEL_ID)
                        if channel:
                            log_embed = discord.Embed(
                                title="New Key Generated",
                                description=f"User: {user.mention}\nKey: `{key}`",
                                color=discord.Color.blue(),
                                timestamp=datetime.datetime.now()
                            )
                            await channel.send(embed=log_embed)
                        
                        return web.Response(text="Success! Check your Discord DMs for your key and loader script.")
                    except Exception as e:
                        print(f"Error sending messages: {e}")
                        return web.Response(text="Error sending messages. Please ensure your DMs are open.")
                
                return web.Response(text="Could not find user.")
    except Exception as e:
        print(f"Error in callback: {e}")
        return web.Response(text="An error occurred")

@bot.command(name='time')
async def check_time(ctx):
    # Create initial embed
    initial_embed = discord.Embed(
        title="🔮 Crystal Hub Key Verification",
        description="Please enter your Crystal Hub key to check its status...",
        color=discord.Color.from_rgb(147, 112, 219)
    )
    initial_embed.set_thumbnail(url="https://i.imgur.com/YourLogo.png")
    initial_embed.add_field(name="Instructions", value="Type your key in the chat", inline=False)
    initial_embed.set_footer(text="Crystal Hub Premium | Automatic Key System", icon_url="https://i.imgur.com/YourIcon.png")
    
    await ctx.send(embed=initial_embed)
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        key_msg = await bot.wait_for('message', check=check, timeout=30.0)
        key = key_msg.content
        
        if key in keys_data["generated"]:
            key_data = keys_data["generated"][key]
            now = datetime.datetime.now()
            
            status_embed = discord.Embed(color=discord.Color.from_rgb(147, 112, 219))
            status_embed.set_author(name="Crystal Hub Premium", icon_url="https://i.imgur.com/YourIcon.png")
            
            if key_data["activated"]:
                expires_at = datetime.datetime.fromisoformat(key_data["expires_at"])
                time_remaining = expires_at - now
                
                days = time_remaining.days
                hours = time_remaining.seconds // 3600
                minutes = (time_remaining.seconds % 3600) // 60
                
                if now > expires_at:
                    status_embed.title = "❌ Key Expired"
                    status_embed.description = "This key has expired. Please contact support for assistance."
                    status_embed.color = discord.Color.red()
                else:
                    status_embed.title = "✅ Premium Key Active"
                    status_embed.add_field(
                        name="Time Remaining",
                        value=f"```\n{days}d {hours}h {minutes}m```",
                        inline=False
                    )
                    status_embed.add_field(
                        name="Expiration",
                        value=f"<t:{int(expires_at.timestamp())}:F>",
                        inline=False
                    )
            else:
                status_embed.title = "⚠️ Key Not Activated"
                status_embed.description = "This key has not been activated yet. Launch Crystal Hub to activate."
                status_embed.color = discord.Color.yellow()
            
            status_embed.add_field(name="Key", value=f"```{key}```", inline=False)
            status_embed.add_field(
                name="Owner",
                value=f"<@{key_data['user_id']}>",
                inline=True
            )
            status_embed.set_footer(text="Crystal Hub Premium • Premium Key System")
            
            await ctx.send(embed=status_embed)
        else:
            error_embed = discord.Embed(
                title="❌ Invalid Key",
                description="The key you entered does not exist in our database.",
                color=discord.Color.red()
            )
            await ctx.send(embed=error_embed)
            
    except asyncio.TimeoutError:
        timeout_embed = discord.Embed(
            title="⏰ Time's Up!",
            description="Key verification timed out. Please try again.",
            color=discord.Color.red()
        )
        await ctx.send(embed=timeout_embed)

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
                
                # Calculate time remaining
                expires_at = datetime.datetime.fromisoformat(keys_data["generated"][key]["expires_at"])
                days_remaining = (expires_at - now).days
                
                keys_data["generated"][key]["days_remaining"] = days_remaining
                await save_keys()
                
                return web.json_response({
                    "success": True, 
                    "message": "Key activated for 7 days",
                    "days_remaining": days_remaining
                })
            else:
                return web.json_response({"success": False, "message": "Key already activated"})
        return web.json_response({"success": False, "message": "Invalid key"})
    except Exception as e:
        return web.json_response({"success": False, "message": str(e)})

async def check_expired_keys():
    while True:
        now = datetime.datetime.now()
        for key in keys_data["generated"]:
            key_data = keys_data["generated"][key]
            if key_data["activated"]:
                expires_at = datetime.datetime.fromisoformat(key_data["expires_at"])
                key_data["days_remaining"] = (expires_at - now).days
                if now > expires_at:
                    key_data["activated"] = False
                    key_data["expired"] = True
        await save_keys()
        await asyncio.sleep(3600)  # Check every hour

async def handle_keys(request):
    now = datetime.datetime.now()
    
    for key, data in keys_data["generated"].items():
        if data["activated"]:
            expires_at = datetime.datetime.fromisoformat(data["expires_at"])
            data["days_remaining"] = (expires_at - now).days
            if now > expires_at:
                data["activated"] = False
                data["expired"] = True
        
        # Always include activation status
        if "activated" not in data:
            data["activated"] = False
        if "expired" not in data:
            data["expired"] = False
            
    await save_keys()
    return web.json_response(keys_data)

async def handle_script(request):
    key = request.query.get('key')
    
    if not key or key not in keys_data["generated"]:
        return web.json_response({
            "success": False,
            "message": "Invalid key"
        })
        
    if not keys_data["generated"][key]["activated"]:
        return web.json_response({
            "success": False,
            "message": "Key not activated"
        })
    
    try:
        with open("script.json", "r") as f:
            script_data = json.load(f)
            
        # Decrypt script
        f = Fernet(key)
        encrypted = base64.b64decode(script_data["data"])
        script = f.decrypt(encrypted).decode()
        
        return web.json_response({
            "success": True,
            "script": script
        })
    except Exception as e:
        return web.json_response({
            "success": False,
            "message": str(e)
        })

async def handle_loader(request):
    try:
        log_message("LOADER", "🔄 Received loader request")
        
        with open("crystal_hub.json", "r") as f:
            script_data = json.load(f)
            log_message("LOADER", "📂 Successfully read crystal_hub.json")
            
        # Decrypt script
        f = Fernet(encryption_key)
        encrypted = base64.b64decode(script_data["data"])
        script = f.decrypt(encrypted).decode()
        log_message("LOADER", "🔓 Successfully decrypted script")
        
        return web.json_response({
            "success": True,
            "script": script
        })
    except FileNotFoundError:
        log_message("LOADER", "⚠️ Script file not found, attempting to recreate...")
        if save_encrypted_script():
            log_message("LOADER", "✅ Script file recreated successfully")
            return web.json_response({
                "success": True,
                "message": "Script regenerated, please try again"
            })
        else:
            log_message("LOADER", "❌ Failed to recreate script file")
            return web.json_response({
                "success": False,
                "message": "Failed to generate script"
            })
    except Exception as e:
        log_message("LOADER", "❌ Error in loader endpoint", e)
        return web.json_response({
            "success": False,
            "message": str(e)
        })

async def start_server():
    try:
        log_message("SERVER", "🚀 Starting server initialization...")
        
        # Add routes
        app.router.add_get('/api/discord/redirect', handle_callback)
        app.router.add_get('/api/keys', handle_keys)
        app.router.add_post('/api/activate', handle_activate)
        app.router.add_get('/api/script', handle_script)
        app.router.add_get('/api/loader', handle_loader)
        log_message("SERVER", "✅ Routes configured")
        
        # Create encrypted script
        if save_encrypted_script():
            log_message("SERVER", "✅ Initial script encryption successful")
        else:
            log_message("SERVER", "❌ Failed to create initial script")
            return
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 10000)))
        await site.start()
        log_message("SERVER", "✅ Web server started successfully")
        
        # Start expiry checker
        asyncio.create_task(check_expired_keys())
        log_message("SERVER", "✅ Key expiry checker started")
        
    except Exception as e:
        log_message("SERVER", "❌ Failed to start server", e)
        raise e

@bot.event
async def on_ready():
    log_message("BOT", f"✅ Logged in as {bot.user}")
    try:
        await start_server()
        log_message("BOT", "✅ Server initialization complete")
    except Exception as e:
        log_message("BOT", "❌ Failed to start server", e)

# Enhanced server configuration
server_config = {
    "admin_role_id": None,
    "buyer_role_id": None,
    "control_channel_id": None,
    "blacklist": [],
    "theme_color": discord.Color.purple().value,
    "is_setup": False
}

try:
    with open("server_config.json", "r") as f:
        server_config = json.load(f)
except FileNotFoundError:
    with open("server_config.json", "w") as f:
        json.dump(server_config, f, indent=4)

async def save_config():
    async with aiofiles.open("server_config.json", "w") as f:
        await f.write(json.dumps(server_config, indent=4))

@bot.command()
async def setup(ctx):
    """Initial setup for Crystal Hub"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ You need administrator permissions!")
        return

    try:
        setup_embed = discord.Embed(
            title="🚀 Crystal Hub Setup",
            description="Setting up your premium experience...",
            color=discord.Color.blue()
        )
        status_msg = await ctx.send(embed=setup_embed)

        # Create roles with better styling
        admin_role = await ctx.guild.create_role(
            name="💎 Crystal Admin",
            color=discord.Color.red(),
            permissions=discord.Permissions(administrator=True),
            hoist=True  # Shows role separately in member list
        )
        
        buyer_role = await ctx.guild.create_role(
            name="⭐ Crystal Premium",
            color=discord.Color.purple(),
            hoist=True
        )

        # Create category and channels
        category = await ctx.guild.create_category(
            "🌟 CRYSTAL HUB",
            position=0
        )

        # Set permissions for category
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            buyer_role: discord.PermissionOverwrite(read_messages=True),
            admin_role: discord.PermissionOverwrite(read_messages=True, manage_messages=True)
        }

        # Create organized channels
        control_channel = await category.create_text_channel(
            '💫┃control-panel',
            overwrites=overwrites,
            topic="Crystal Hub Premium Control Panel"
        )
        
        announcements = await category.create_text_channel(
            '📢┃announcements',
            overwrites=overwrites
        )
        
        support = await category.create_text_channel(
            '🎫┃support',
            overwrites=overwrites
        )

        # Save configuration
        server_config.update({
            "admin_role_id": admin_role.id,
            "buyer_role_id": buyer_role.id,
            "control_channel_id": control_channel.id,
            "is_setup": True
        })
        await save_config()

        # Give admin role to setup person
        await ctx.author.add_roles(admin_role)

        # Create the premium control panel
        await control_channel.purge(limit=100)

        # Welcome Banner (Extra Wide)
        welcome_embed = discord.Embed(
            title="",  # Empty title for custom banner
            description="",
            color=discord.Color.purple()
        )
        welcome_embed.set_image(url="https://your-banner-image.png")  # Add your custom banner
        await control_channel.send(embed=welcome_embed)

        # Status Dashboard
        status_embed = discord.Embed(
            title="🎮 Crystal Hub Dashboard",
            description="Welcome to your premium control center",
            color=discord.Color.purple()
        )
        status_embed.add_field(
            name="🔐 Security Status",
            value="```\n✓ HWID System: Online\n✓ Anti-Tamper: Active\n✓ Encryption: Enabled\n```",
            inline=True
        )
        status_embed.add_field(
            name="📊 Statistics",
            value=f"```\n• Premium Users: {len(hwid_data['users'])}\n• Uptime: 99.9%\n• Version: 1.0.0\n```",
            inline=True
        )
        await control_channel.send(embed=status_embed)

        # Separator
        await control_channel.send("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Main Control Panel
        control_embed = discord.Embed(
            title="🎮 Control Panel",
            description="Access your premium features below",
            color=discord.Color.purple()
        )
        control_embed.add_field(
            name="🔑 Script Access",
            value="• Get your HWID-locked script\n• Auto-updates included\n• Premium features",
            inline=True
        )
        control_embed.add_field(
            name="🔄 HWID Management",
            value="• View your HWID\n• Reset when needed\n• Security status",
            inline=True
        )
        control_embed.add_field(
            name="📱 Quick Actions",
            value="Click the buttons below to access features",
            inline=False
        )
        await control_channel.send(embed=control_embed, view=ControlPanel())

        # Information Section
        info_embed = discord.Embed(
            title="ℹ️ Information",
            description="Everything you need to know about Crystal Hub",
            color=discord.Color.blue()
        )
        info_embed.add_field(
            name="🎮 Supported Games",
            value="• Basketball Legends\n• More coming soon...",
            inline=True
        )
        info_embed.add_field(
            name="🔧 Support",
            value="• 24/7 Support\n• Priority Updates\n• Exclusive Features",
            inline=True
        )
        await control_channel.send(embed=info_embed)

        # Quick Links
        links_embed = discord.Embed(
            title="🔗 Quick Links",
            description="Important resources at your fingertips",
            color=discord.Color.green()
        )
        links_embed.add_field(
            name="📚 Documentation",
            value="[View Documentation](https://docs.crystalhub.com)",
            inline=True
        )
        links_embed.add_field(
            name="📢 Announcements",
            value=f"Check {announcements.mention} for updates",
            inline=True
        )
        links_embed.add_field(
            name="🎫 Support",
            value=f"Visit {support.mention} for help",
            inline=True
        )
        await control_channel.send(embed=links_embed)

        # Footer
        footer_embed = discord.Embed(
            description="Crystal Hub Premium © 2024 - All rights reserved",
            color=discord.Color.purple()
        )
        await control_channel.send("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        await control_channel.send(embed=footer_embed)

        # Update setup status
        setup_embed.description = "✅ Crystal Hub has been successfully set up!"
        setup_embed.add_field(
            name="Channels Created",
            value=f"📍 Control Panel: {control_channel.mention}\n📢 Announcements: {announcements.mention}\n🎫 Support: {support.mention}",
            inline=False
        )
        setup_embed.add_field(
            name="Roles Created",
            value=f"👑 Admin Role: {admin_role.mention}\n💎 Premium Role: {buyer_role.mention}",
            inline=False
        )
        setup_embed.color = discord.Color.green()
        await status_msg.edit(embed=setup_embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Setup Failed",
            description=f"Error: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)

# Update other commands to use server_config
def check_admin(ctx):
    return discord.utils.get(ctx.author.roles, id=server_config["admin_role_id"]) is not None

def check_buyer(ctx):
    return discord.utils.get(ctx.author.roles, id=server_config["buyer_role_id"]) is not None

# Example of using the new role checks
@bot.command()
async def givepremium(ctx, user: discord.Member):
    """Give a user premium access"""
    if not check_admin(ctx):
        await ctx.send("❌ You need the Crystal Admin role!")
        return
        
    try:
        buyer_role = ctx.guild.get_role(server_config["buyer_role_id"])
        await user.add_roles(buyer_role)
        await ctx.send(f"✅ Gave premium to {user.mention}")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

# Blacklist management
async def add_to_blacklist(user_id: int):
    server_config["blacklist"].append(user_id)
    await save_config()

async def remove_from_blacklist(user_id: int):
    if user_id in server_config["blacklist"]:
        server_config["blacklist"].remove(user_id)
        await save_config()

# Admin commands
@bot.command()
async def blacklist(ctx, user: discord.Member):
    """Blacklist a user from using Crystal Hub"""
    if not check_admin(ctx):
        await ctx.send("❌ You need the Crystal Admin role!")
        return

    user_id = user.id
    if user_id in server_config["blacklist"]:
        await ctx.send("❌ User is already blacklisted!")
        return

    await add_to_blacklist(user_id)
    
    # Remove premium role if they have it
    if server_config["buyer_role_id"]:
        buyer_role = ctx.guild.get_role(server_config["buyer_role_id"])
        if buyer_role in user.roles:
            await user.remove_roles(buyer_role)

    embed = discord.Embed(
        title="⛔ User Blacklisted",
        description=f"{user.mention} has been blacklisted from Crystal Hub",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.command()
async def unblacklist(ctx, user: discord.Member):
    """Remove a user from the blacklist"""
    if not check_admin(ctx):
        await ctx.send("❌ You need the Crystal Admin role!")
        return

    user_id = user.id
    if user_id not in server_config["blacklist"]:
        await ctx.send("❌ User is not blacklisted!")
        return

    await remove_from_blacklist(user_id)
    embed = discord.Embed(
        title="✅ User Unblacklisted",
        description=f"{user.mention} has been removed from the blacklist",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
async def resetup(ctx):
    """Reconfigure Crystal Hub setup"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ You need administrator permissions!")
        return

    confirm_embed = discord.Embed(
        title="⚠️ Reset Confirmation",
        description="This will reset all Crystal Hub settings. Are you sure?",
        color=discord.Color.yellow()
    )
    
    class ConfirmView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)
            
        @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.danger)
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("❌ Only the command author can confirm!", ephemeral=True)
                return
                
            # Reset configuration
            server_config.clear()
            server_config.update({
                "admin_role_id": None,
                "buyer_role_id": None,
                "control_channel_id": None,
                "blacklist": [],
                "theme_color": discord.Color.purple().value,
                "is_setup": False
            })
            await save_config()
            
            await interaction.response.send_message("✅ Configuration reset! Run `!setup` to reconfigure.")
            
        @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.grey)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("❌ Only the command author can cancel!", ephemeral=True)
                return
                
            await interaction.response.send_message("Operation cancelled.")
            
    await ctx.send(embed=confirm_embed, view=ConfirmView())

# Enhanced Control Panel
class ControlPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(
        label="🔑 Get Script",
        style=discord.ButtonStyle.green,
        custom_id="get_script",
        row=0
    )
    async def get_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in server_config["blacklist"]:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="⛔ Access Denied",
                    description="You are blacklisted from Crystal Hub!",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return
            
        if not any(role.id == server_config["buyer_role_id"] for role in interaction.user.roles):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Access Denied",
                    description="You need the premium role to access this feature!",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return

        # Loading animation
        loading_embed = discord.Embed(
            title="⚡ Generating Script",
            description="Please wait while we prepare your script...",
            color=discord.Color.yellow()
        )
        await interaction.response.send_message(embed=loading_embed, ephemeral=True)
        
        user_id = str(interaction.user.id)
        if user_id not in hwid_data["users"]:
            hwid = hashlib.sha256(f"{platform.node()}{uuid.getnode()}".encode()).hexdigest()
            hwid_data["users"][user_id] = {
                "hwid": hwid,
                "resets": 0,
                "last_updated": datetime.datetime.now().isoformat()
            }
            await save_hwid_data()

        script = generate_hwid_script(interaction.user.id, hwid_data["users"][user_id]["hwid"])
        
        success_embed = discord.Embed(
            title="✅ Script Generated",
            description="Your HWID-locked premium script is ready!",
            color=discord.Color.green()
        )
        success_embed.add_field(
            name="HWID Information",
            value=f"```\nHWID: {hwid_data['users'][user_id]['hwid'][:16]}...\nResets: {hwid_data['users'][user_id]['resets']}/3\nLast Updated: {hwid_data['users'][user_id]['last_updated']}\n```",
            inline=False
        )
        
        file = discord.File(io.StringIO(script), filename="crystal_hub_premium.lua")
        await interaction.edit_original_response(embed=success_embed, attachments=[file])

# Function to generate HWID-locked script
def generate_hwid_script(user_id, hwid):
    return f"""
-- Crystal Hub Premium (HWID: {hwid[:8]}...)
local function getHWID()
    local hwid = game:GetService("RbxAnalyticsService"):GetClientId()
    return hwid
end

local function verifyHWID()
    local currentHWID = getHWID()
    if currentHWID ~= "{hwid}" then
        game.Players.LocalPlayer:Kick("⚠️ HWID Mismatch! Reset your HWID in the Discord.")
        return false
    end
    return true
end

if verifyHWID() then
    -- Your premium script here
    loadstring(game:HttpGet("https://raw.githubusercontent.com/jiohasdas/CRYSTAL-HUB-SCRIPT/refs/heads/main/BASKETBALL%20LEGENDS"))()
end
"""

# Analytics system
analytics_data = {
    "daily_users": {},
    "script_executions": {},
    "peak_times": [],
    "total_executions": 0,
    "user_stats": {}
}

try:
    with open("analytics.json", "r") as f:
        analytics_data = json.load(f)
except FileNotFoundError:
    with open("analytics.json", "w") as f:
        json.dump(analytics_data, f, indent=4)

async def save_analytics():
    async with aiofiles.open("analytics.json", "w") as f:
        await f.write(json.dumps(analytics_data, indent=4))

async def track_execution(user_id: str):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    current_hour = datetime.datetime.now().strftime("%H:00")
    
    # Track daily users
    if today not in analytics_data["daily_users"]:
        analytics_data["daily_users"][today] = []
    if user_id not in analytics_data["daily_users"][today]:
        analytics_data["daily_users"][today].append(user_id)
    
    # Track executions
    if today not in analytics_data["script_executions"]:
        analytics_data["script_executions"][today] = {}
    if current_hour not in analytics_data["script_executions"][today]:
        analytics_data["script_executions"][today][current_hour] = 0
    analytics_data["script_executions"][today][current_hour] += 1
    
    # Track user stats
    if user_id not in analytics_data["user_stats"]:
        analytics_data["user_stats"][user_id] = {
            "total_executions": 0,
            "last_execution": None,
            "favorite_times": {}
        }
    
    analytics_data["user_stats"][user_id]["total_executions"] += 1
    analytics_data["user_stats"][user_id]["last_execution"] = datetime.datetime.now().isoformat()
    
    if current_hour not in analytics_data["user_stats"][user_id]["favorite_times"]:
        analytics_data["user_stats"][user_id]["favorite_times"][current_hour] = 0
    analytics_data["user_stats"][user_id]["favorite_times"][current_hour] += 1
    
    analytics_data["total_executions"] += 1
    await save_analytics()

# Enhanced Control Panel with Analytics
class AnalyticsDashboard(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📊 View Analytics", style=discord.ButtonStyle.blurple)
    async def view_analytics(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(role.id == server_config["admin_role_id"] for role in interaction.user.roles):
            await interaction.response.send_message("❌ Admin only feature!", ephemeral=True)
            return
            
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        analytics_embed = discord.Embed(
            title="📈 Crystal Hub Analytics",
            description="Real-time statistics and insights",
            color=discord.Color.blue()
        )
        
        # Daily Stats
        daily_users = len(analytics_data["daily_users"].get(today, []))
        analytics_embed.add_field(
            name="📊 Today's Statistics",
            value=f"```\nActive Users: {daily_users}\nExecutions: {sum(analytics_data['script_executions'].get(today, {}).values())}\nPeak Hour: {max(analytics_data['script_executions'].get(today, {'00:00': 0}).items(), key=lambda x: x[1])[0]}```",
            inline=False
        )
        
        # Total Stats
        analytics_embed.add_field(
            name="🌟 Overall Statistics",
            value=f"```\nTotal Executions: {analytics_data['total_executions']}\nTotal Users: {len(analytics_data['user_stats'])}\nAverage Daily Users: {daily_users}```",
            inline=False
        )
        
        await interaction.response.send_message(embed=analytics_embed, ephemeral=True)

# User Management Dashboard
class UserManagement(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="👥 User Management", style=discord.ButtonStyle.green)
    async def manage_users(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(role.id == server_config["admin_role_id"] for role in interaction.user.roles):
            await interaction.response.send_message("❌ Admin only feature!", ephemeral=True)
            return
            
        users_embed = discord.Embed(
            title="👥 User Management",
            description="Manage Crystal Hub users",
            color=discord.Color.green()
        )
        
        # Active users
        active_users = []
        for user_id, stats in analytics_data["user_stats"].items():
            user = interaction.guild.get_member(int(user_id))
            if user:
                last_exec = datetime.datetime.fromisoformat(stats["last_execution"]) if stats["last_execution"] else None
                active_users.append(f"{user.mention}: {stats['total_executions']} executions")
        
        users_embed.add_field(
            name="🎮 Active Users",
            value="\n".join(active_users[:10]) if active_users else "No active users",
            inline=False
        )
        
        # Blacklisted users
        blacklisted = []
        for user_id in server_config["blacklist"]:
            user = interaction.guild.get_member(user_id)
            if user:
                blacklisted.append(user.mention)
        
        users_embed.add_field(
            name="⛔ Blacklisted Users",
            value="\n".join(blacklisted) if blacklisted else "No blacklisted users",
            inline=False
        )
        
        await interaction.response.send_message(embed=users_embed, ephemeral=True)

# Automated Announcements
class AnnouncementSystem:
    def __init__(self, bot):
        self.bot = bot
        self.announcements = []
        self.bot.loop.create_task(self.announcement_loop())
    
    async def add_announcement(self, title, content, timestamp):
        self.announcements.append({
            "title": title,
            "content": content,
            "timestamp": timestamp
        })
        
    async def announcement_loop(self):
        while True:
            now = datetime.datetime.now()
            for announcement in self.announcements[:]:
                if now >= announcement["timestamp"]:
                    channel = self.bot.get_channel(server_config["control_channel_id"])
                    if channel:
                        embed = discord.Embed(
                            title=announcement["title"],
                            description=announcement["content"],
                            color=discord.Color.gold()
                        )
                        await channel.send(embed=embed)
                        self.announcements.remove(announcement)
            await asyncio.sleep(60)

# Add to your setup command
announcement_system = AnnouncementSystem(bot)

@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def announce(ctx, delay_hours: int, *, message):
    """Schedule an announcement"""
    timestamp = datetime.datetime.now() + datetime.timedelta(hours=delay_hours)
    await announcement_system.add_announcement(
        "📢 Crystal Hub Announcement",
        message,
        timestamp
    )
    await ctx.send(f"✅ Announcement scheduled for {timestamp}")

# Version Control System
version_data = {
    "current_version": "1.0.0",
    "versions": {
        "1.0.0": {
            "release_date": datetime.datetime.now().isoformat(),
            "changes": ["Initial release"],
            "script_url": "https://raw.githubusercontent.com/your-repo/main/v1.lua"
        }
    },
    "auto_update": True
}

try:
    with open("versions.json", "r") as f:
        version_data = json.load(f)
except FileNotFoundError:
    with open("versions.json", "w") as f:
        json.dump(version_data, f, indent=4)

async def save_versions():
    async with aiofiles.open("versions.json", "w") as f:
        await f.write(json.dumps(version_data, indent=4))

# Enhanced Analytics with Game Tracking
analytics_data.update({
    "game_stats": {},
    "version_stats": {},
    "performance_metrics": {},
    "user_retention": {}
})

# Version Control Panel
class VersionControl(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🔄 Version Manager", style=discord.ButtonStyle.blurple)
    async def version_manager(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(role.id == server_config["admin_role_id"] for role in interaction.user.roles):
            await interaction.response.send_message("❌ Admin only feature!", ephemeral=True)
            return
        
        version_embed = discord.Embed(
            title="🔄 Version Control",
            description=f"Current Version: `{version_data['current_version']}`",
            color=discord.Color.blue()
        )
        
        # Version history
        history = ""
        for version, data in version_data["versions"].items():
            history += f"**{version}** - {data['release_date']}\n"
            for change in data["changes"]:
                history += f"• {change}\n"
            history += "\n"
        
        version_embed.add_field(
            name="📜 Version History",
            value=history or "No version history",
            inline=False
        )
        
        await interaction.response.send_message(embed=version_embed, ephemeral=True)

# Enhanced User Management
class AdvancedUserManagement(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📊 User Analytics", style=discord.ButtonStyle.green)
    async def user_analytics(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(role.id == server_config["admin_role_id"] for role in interaction.user.roles):
            await interaction.response.send_message("❌ Admin only feature!", ephemeral=True)
            return
        
        analytics_embed = discord.Embed(
            title="📊 Advanced User Analytics",
            description="Detailed user statistics and metrics",
            color=discord.Color.green()
        )
        
        # User retention
        retention_data = analytics_data["user_retention"]
        weekly_retention = len([u for u in analytics_data["user_stats"].values() 
                              if datetime.datetime.fromisoformat(u["last_execution"]) > 
                              datetime.datetime.now() - datetime.timedelta(days=7)])
        
        analytics_embed.add_field(
            name="👥 User Retention",
            value=f"```\nWeekly Active: {weekly_retention}\nRetention Rate: {(weekly_retention/len(analytics_data['user_stats'])*100):.1f}%\n```",
            inline=False
        )
        
        # Game statistics
        game_stats = ""
        for game, stats in analytics_data["game_stats"].items():
            game_stats += f"{game}: {stats['executions']} executions\n"
        
        analytics_embed.add_field(
            name="🎮 Game Statistics",
            value=f"```\n{game_stats or 'No game data'}```",
            inline=False
        )
        
        await interaction.response.send_message(embed=analytics_embed, ephemeral=True)

# Auto-Update System
class AutoUpdateSystem:
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.update_checker())
    
    async def check_for_updates(self):
        # Simulate checking for updates (replace with your actual update check)
        return {
            "version": "1.0.1",
            "changes": ["Bug fixes", "New features"],
            "script_url": "https://raw.githubusercontent.com/your-repo/main/v1.1.lua"
        }
    
    async def update_checker(self):
        while True:
            if version_data["auto_update"]:
                try:
                    update = await self.check_for_updates()
                    if update["version"] > version_data["current_version"]:
                        # New version available
                        version_data["versions"][update["version"]] = {
                            "release_date": datetime.datetime.now().isoformat(),
                            "changes": update["changes"],
                            "script_url": update["script_url"]
                        }
                        version_data["current_version"] = update["version"]
                        await save_versions()
                        
                        # Announce update
                        channel = self.bot.get_channel(server_config["control_channel_id"])
                        if channel:
                            update_embed = discord.Embed(
                                title="🆕 New Update Available!",
                                description=f"Version {update['version']} has been released!",
                                color=discord.Color.green()
                            )
                            update_embed.add_field(
                                name="📝 Changes",
                                value="\n".join(f"• {change}" for change in update["changes"]),
                                inline=False
                            )
                            await channel.send(embed=update_embed)
                except Exception as e:
                    print(f"Update check failed: {e}")
            
            await asyncio.sleep(3600)  # Check every hour

# Initialize auto-update system
auto_updater = AutoUpdateSystem(bot)

# Add to your setup command
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def updateversion(ctx, version: str, *, changelog: str):
    """Update the script version"""
    if version in version_data["versions"]:
        await ctx.send("❌ Version already exists!")
        return
    
    version_data["versions"][version] = {
        "release_date": datetime.datetime.now().isoformat(),
        "changes": [change.strip() for change in changelog.split(';')],
        "script_url": f"https://raw.githubusercontent.com/your-repo/main/v{version}.lua"
    }
    version_data["current_version"] = version
    await save_versions()
    
    embed = discord.Embed(
        title="✅ Version Updated",
        description=f"Successfully updated to version {version}",
        color=discord.Color.green()
    )
    embed.add_field(
        name="📝 Changelog",
        value="\n".join(f"• {change}" for change in version_data["versions"][version]["changes"]),
        inline=False
    )
    await ctx.send(embed=embed)

# Add these to your control panel setup
control_panel_message = await control_channel.send(
    embed=control_embed,
    view=discord.ui.View()
        .add_item(ControlPanel())
        .add_item(AnalyticsDashboard())
        .add_item(UserManagement())
        .add_item(VersionControl())
        .add_item(AdvancedUserManagement())
)

# AI Support System
support_config = {
    "forum_channel_id": None,
    "support_role_id": 1337656413442281482,
    "languages": [
        {"name": "English", "emoji": "🇬🇧", "code": "en"},
        {"name": "Spanish", "emoji": "🇪🇸", "code": "es"},
        {"name": "French", "emoji": "🇫🇷", "code": "fr"},
        {"name": "German", "emoji": "🇩🇪", "code": "de"},
        {"name": "Russian", "emoji": "🇷🇺", "code": "ru"},
        {"name": "Chinese", "emoji": "🇨🇳", "code": "zh"},
        {"name": "Japanese", "emoji": "🇯🇵", "code": "ja"},
        {"name": "Korean", "emoji": "🇰🇷", "code": "ko"},
        {"name": "Arabic", "emoji": "🇸🇦", "code": "ar"},
        {"name": "Portuguese", "emoji": "🇵🇹", "code": "pt"}
    ],
    "common_issues": {
        "ui_not_showing": {
            "steps": [
                "Check if your executor is supported",
                "Try reinjecting the script",
                "Clear your executor's workspace",
                "Ensure you're using the latest version"
            ],
            "solution": "If the UI is not showing up, first try rejoining the game and reinjecting the script. If the issue persists, make sure you're using a supported executor like Synapse X, KRNL, or Script-Ware."
        },
        "hwid_error": {
            "steps": [
                "Verify your HWID hasn't been reset",
                "Check if you're blacklisted",
                "Request HWID reset if needed"
            ],
            "solution": "HWID errors usually occur when your hardware configuration has changed. You can request a HWID reset from the control panel."
        }
        # Add more common issues
    }
}

class LanguageSelector(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.selected_language = None
        self.setup_buttons()
    
    def setup_buttons(self):
        # Create a fancy grid of language buttons
        for i, lang in enumerate(support_config["languages"]):
            button = discord.ui.Button(
                label=lang["name"],
                emoji=lang["emoji"],
                custom_id=f"lang_{lang['code']}",
                row=i // 3,
                style=discord.ButtonStyle.blurple
            )
            button.callback = self.language_callback
            self.add_item(button)
    
    async def language_callback(self, interaction: discord.Interaction):
        lang_code = interaction.custom_id.split("_")[1]
        lang = next(l for l in support_config["languages"] if l["code"] == lang_code)
        
        await interaction.response.edit_message(
            embed=discord.Embed(
                title=f"{lang['emoji']} Language Selected: {lang['name']}",
                description="Thank you for selecting your language. Please describe your issue, and our AI assistant will help you.",
                color=discord.Color.green()
            ),
            view=None
        )
        self.selected_language = lang_code
        self.stop()

@bot.command()
@commands.has_permissions(administrator=True)
async def setupsupportai(ctx):
    """Set up the AI Support System with forum integration"""
    try:
        # Create Support Category
        support_category = await ctx.guild.create_category("🤖 CRYSTAL AI SUPPORT")
        
        # Create Forum Channel
        forum_channel = await support_category.create_forum_channel(
            "🎫┃crystal-support",
            topic="Crystal Hub AI Support System"
        )
        
        # Save forum channel ID
        support_config["forum_channel_id"] = forum_channel.id
        
        # Create TOS post
        tos_embed = discord.Embed(
            title="📜 Crystal Hub Support - Terms of Service",
            description=(
                "Welcome to Crystal Hub's AI Support System!\n\n"
                "**Guidelines:**\n"
                "1. Be specific about your issue\n"
                "2. Provide relevant information\n"
                "3. Follow the AI's instructions\n"
                "4. Be patient and respectful\n\n"
                "**How it works:**\n"
                "1. Create a new post\n"
                "2. Select your preferred language\n"
                "3. Describe your issue\n"
                "4. Our AI will assist you\n\n"
                "**Note:** Complex issues will be escalated to our support team automatically."
            ),
            color=discord.Color.blue()
        )
        
        await forum_channel.send(embed=tos_embed)
        
        # Success message
        success_embed = discord.Embed(
            title="✅ AI Support System Configured",
            description=f"Support forum created: {forum_channel.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=success_embed)
        
        # Set up forum auto-response
        @bot.event
        async def on_thread_create(thread):
            if thread.parent_id == support_config["forum_channel_id"]:
                # Welcome message
                welcome_embed = discord.Embed(
                    title="👋 Welcome to Crystal Hub Support",
                    description=(
                        "Hello! I'm Crystal AI, your personal support assistant.\n\n"
                        "To better assist you, please select your preferred language:"
                    ),
                    color=discord.Color.purple()
                )
                
                # Send welcome message with language selector
                await thread.send(embed=welcome_embed, view=LanguageSelector())
        
        @bot.event
        async def on_message(message):
            if isinstance(message.channel, discord.Thread) and message.channel.parent_id == support_config["forum_channel_id"]:
                if message.author.bot:
                    return
                
                # Process user's issue
                response = await process_support_issue(message.content)
                if response["needs_human"]:
                    support_role = message.guild.get_role(support_config["support_role_id"])
                    await message.channel.send(f"{support_role.mention} Human assistance needed!")
                
                await message.channel.send(embed=response["embed"])

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Setup Failed",
            description=f"Error: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)

async def process_support_issue(content: str):
    """Process support issues and generate AI responses"""
    content = content.lower()
    
    # Check for common issues
    for issue, data in support_config["common_issues"].items():
        if any(keyword in content for keyword in issue.split("_")):
            response_embed = discord.Embed(
                title="🔍 Issue Identified",
                description=data["solution"],
                color=discord.Color.blue()
            )
            response_embed.add_field(
                name="📝 Steps to Resolve",
                value="\n".join(f"• {step}" for step in data["steps"]),
                inline=False
            )
            return {"embed": response_embed, "needs_human": False}
    
    # If no common issue found, escalate to human support
    escalation_embed = discord.Embed(
        title="👥 Escalating to Human Support",
        description="I'll need to bring in our support team for this issue. Please wait while they review your case.",
        color=discord.Color.orange()
    )
    return {"embed": escalation_embed, "needs_human": True}

bot.run(os.getenv('DISCORD_TOKEN'))
