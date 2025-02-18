import base64
import hashlib
import random
import string
from cryptography.fernet import Fernet
from typing import Dict, Any

class CrystalObfuscator:
    def __init__(self):
        self.encryption_key = Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)
        
    def generate_junk(self, length: int) -> str:
        """Generate random junk code"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def encrypt_strings(self, code: str) -> tuple[str, Dict[str, str]]:
        """Encrypt string literals in code"""
        string_map = {}
        encrypted_code = code
        
        # Find and encrypt strings
        import re
        strings = re.findall(r'"([^"]*)"', code)
        for s in strings:
            if s not in string_map:
                encrypted = self.fernet.encrypt(s.encode()).decode()
                key = f"CRYSTAL_{hashlib.md5(s.encode()).hexdigest()[:8]}"
                string_map[key] = encrypted
                encrypted_code = encrypted_code.replace(f'"{s}"', f'decrypt("{key}")')
                
        return encrypted_code, string_map
    
    def obfuscate(self, script: str, metadata: Dict[str, Any]) -> str:
        """Full obfuscation process"""
        # Add watermark
        obfuscated = f"--[[ Crystal Hub Premium | {metadata['version']} ]]--\n"
        
        # Add runtime variables
        obfuscated += """
local function GetRuntimeVar(key)
    return _G._CRYSTAL_RUNTIME[key]
end
"""
        
        # Add decryption function
        obfuscated += f"""
local _CRYSTAL_KEY = "{self.encryption_key.decode()}"
local _CRYSTAL_STRINGS = {{
"""
        
        # Encrypt strings
        encrypted_code, string_map = self.encrypt_strings(script)
        for key, value in string_map.items():
            obfuscated += f'    ["{key}"] = "{value}",\n'
        
        obfuscated += "}\n"
        
        # Add anti-tamper
        obfuscated += """
local function VerifyIntegrity()
    if not _G._CRYSTAL_RUNTIME then
        error("Crystal Hub: Runtime verification failed")
    end
    
    local hwid = GetRuntimeVar("hwid")
    if not hwid or hwid ~= _G._CRYSTAL_HWID then
        error("Crystal Hub: HWID verification failed")
    end
end

local function SecureRequire(module)
    local success, result = pcall(require, module)
    if not success then
        error("Crystal Hub: Module verification failed")
    end
    return result
end
"""
        
        # Add main code with VM
        obfuscated += f"""
local function LoadCrystalScript()
    VerifyIntegrity()
    local env = setmetatable({{
        require = SecureRequire,
        GetRuntimeVar = GetRuntimeVar,
    }}, {{__index = _G}})
    
    local code = [=[
{encrypted_code}
]=]
    
    local fn = load(code, "Crystal Hub", "t", env)
    if not fn then
        error("Crystal Hub: Script verification failed")
    end
    
    return fn()
end

return LoadCrystalScript()
"""
        
        return obfuscated 
