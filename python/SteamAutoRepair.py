import os
import re
import time
import requests
import json 
from typing import Dict, Any, Optional

# --- 1. Configuration ---
STEAM_ROOT = r"G:\SteamLibrary"
STEAM_APPS_DIR = os.path.join(STEAM_ROOT, "steamapps")
COMMON_DIR = os.path.join(STEAM_APPS_DIR, "common")
APPID_JSON_URL = "https://raw.githubusercontent.com/jsnli/steamappidlist/master/data/games_appid.json"
ACF_ENCODING = 'ascii' 

# --- 2. Core Function Definitions ---

def confirm_step(message: str) -> bool:
    """Prompt the user to confirm whether to proceed to the next step"""
    print("-" * 50)
    response = input(f"{message} Please enter 'y' to continue, or any other key to exit: ").lower()
    print("-" * 50)
    return response == 'y'

def normalize_name(name: str) -> str:
    """Normalize game names for fuzzy matching"""
    normalized = name.upper()
    normalized = re.sub(r'\s', '', normalized)
    normalized = re.sub(r'[^A-Z0-9]', '', normalized)
    return normalized

def get_directory_size(path: str) -> int:
    """Calculate the total size of a directory recursively"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total_size += os.path.getsize(fp)
            except OSError:
                pass
    return total_size

def parse_acf_content(content: str) -> Dict[str, str]:
    """Extract key-value pairs from VDF content using regular expressions"""
    data = {}
    matches = re.findall(r'"(appid|installdir|name|StateFlags|LastUpdated|SizeOnDisk|BytesToDownload|BytesDownloaded|BytesToStage|BytesStaged|AutoUpdateBehavior|AllowOtherDownloadsWhileRunning|ScheduledAutoUpdate)"\s+"([^"]*)"', content)
    for key, value in matches:
        data[key] = value
    return data

def build_acf_content(data: Dict[str, Any]) -> str:
    """Build formatted ACF/VDF content from dictionary data"""
    content_lines = ['"AppState"', '{']
    app_state = data.get('AppState', {})
    
    for key, value in app_state.items():
        line = f'\t"{key}"\t\t"{value}"'
        content_lines.append(line)
        
    content_lines.append('}')
    return "\n".join(content_lines)

def find_or_create_template() -> Optional[Dict[str, Any]]:
    """Find an existing ACF file as a template, otherwise create from scratch"""
    print("-> Attempting to find an existing ACF file as a template...")
    
    acf_files = [f for f in os.listdir(STEAM_APPS_DIR) if f.startswith('appmanifest_') and f.endswith('.acf')]
    
    # --- Attempt to read existing template ---
    if acf_files:
        template_file = acf_files[0]
        template_path = os.path.join(STEAM_APPS_DIR, template_file)
        
        try:
            with open(template_path, 'r', encoding=ACF_ENCODING) as f:
                content = f.read()
            
            parsed_data = parse_acf_content(content)
            
            template_appid = parsed_data.get('appid')
            template_installdir = parsed_data.get('installdir')
            
            if template_appid and template_installdir:
                print(f"✅ Successfully found and parsed existing template ACF file: {template_file}")
                return {
                    'path': template_path, 
                    'appid': template_appid, 
                    'installdir': template_installdir, 
                    'source': 'ExistingFile',
                    'content': content
                }
            else:
                print(f"❌ Error: Unable to extract AppID or Installdir from template {template_file}. Attempting to create from scratch.")
        except Exception as e:
            print(f"❌ Error: Unable to read template file {template_file}. Attempting to create from scratch. Error message: {e}")

    # --- Not found or parsing failed, create from scratch ---
    print("⚠️ Warning: No valid ACF template found, will automatically generate a generic template.")
    
    template_appid = "999999" 
    template_installdir = "GenericTemplate"
    temp_acf_name = f"appmanifest_{template_appid}.acf"
    template_path = os.path.join(STEAM_APPS_DIR, temp_acf_name)
    current_unix_time = str(int(time.time()))

    base_data = {
        "AppState": {
            "appid": template_appid,
            "universe": "1",
            "name": "Generic ACF Template",
            "StateFlags": "4",
            "installdir": template_installdir,
            "LastUpdated": current_unix_time,
            "SizeOnDisk": "100000000",
            "buildid": "1",
            "LastOwner": "0",
            "DownloadType": "1",
            "UpdateResult": "0",
            "BytesToDownload": "0",
            "BytesDownloaded": "0",
            "BytesToStage": "0",
            "BytesStaged": "0",
            "AutoUpdateBehavior": "0",
            "AllowOtherDownloadsWhileRunning": "0",
            "ScheduledAutoUpdate": "0"
        }
    }
    
    base_content = build_acf_content(base_data)

    try:
        with open(template_path, 'w', encoding=ACF_ENCODING) as f:
            f.write(base_content)
        
        print(f"✅ Temporary generic template created: {temp_acf_name}")
        return {
            'path': template_path, 
            'appid': template_appid, 
            'installdir': template_installdir, 
            'source': 'GeneratedTemplate',
            'content': base_content
        }
    except Exception as e:
        print(f"❌ Error: Unable to create temporary ACF file. Please check permissions. Error message: {e}")
        return None

def download_and_map_appids() -> Optional[Dict[str, str]]:
    """Download AppID JSON list and create mapping table"""
    print("\n=== [Step 2/3] Download AppID list and create mapping table (JSON) ===")
    print("-> Downloading the latest AppID JSON list from GitHub...")
    
    try:
        response = requests.get(APPID_JSON_URL, timeout=10)
        response.raise_for_status()
        
        json_data = response.json()
        app_id_map = {}
        
        # Handle list structure: [{"appid": ..., "name": ...}, ...]
        if isinstance(json_data, list):
            for item in json_data:
                if isinstance(item, dict) and 'appid' in item and 'name' in item:
                    appid_str = str(item['appid'])
                    name_str = item['name']
                    
                    if appid_str.isdigit() and name_str:
                        normalized_name = normalize_name(name_str)
                        app_id_map[normalized_name] = appid_str
            
        elif isinstance(json_data, dict):
            # Handle dictionary structure: {appid: name}
            for appid_str, name_str in json_data.items():
                if appid_str.isdigit() and name_str:
                    normalized_name = normalize_name(name_str)
                    app_id_map[normalized_name] = appid_str
        
        else:
            print("❌ Error: Downloaded JSON data format unrecognized (neither dictionary nor list).")
            return None

        print(f"✅ AppID list download and parsing completed. Loaded {len(app_id_map)} items.")
        return app_id_map

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: Failed to retrieve AppID list. Please check network connection. Error message: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error: JSON parsing failed. Data format incorrect. Error message: {e}")
        return None

def batch_repair_and_write(game_map: Dict[str, str], template_info: Dict[str, Any]) -> bool:
    """Batch repair games in the common folder"""
    print("\n=== [Step 3/3] Scan games and create ACF files ===")
    
    template_appid = template_info['appid']
    template_installdir = template_info['installdir']
    template_path = template_info['path']
    template_content = template_info['content']
    repaired_count = 0

    try:
        game_folders = [f for f in os.listdir(COMMON_DIR) if os.path.isdir(os.path.join(COMMON_DIR, f))]
        print(f"-> Found {len(game_folders)} game folders in the common directory...")
    except FileNotFoundError:
        print(f"❌ Error: Common folder not found: {COMMON_DIR}")
        return False
    except PermissionError:
        print("❌ Error: No permission to read common folder. Please run as administrator.")
        return False

    current_unix_time = str(int(time.time()))

    for folder_name in game_folders:
        normalized_folder_name = normalize_name(folder_name)
        target_appid = game_map.get(normalized_folder_name)

        if not target_appid:
            # print(f"   ⚠️ Game '{folder_name}' AppID not found, skipping.")
            continue # To keep output concise, only output successfully repaired items

        target_acf_file = os.path.join(STEAM_APPS_DIR, f"appmanifest_{target_appid}.acf")

        if os.path.exists(target_acf_file):
            continue

        print(f"   🛠️ Repairing: '{folder_name}' (AppID: {target_appid})...")

        # Calculate actual size on disk
        game_path = os.path.join(COMMON_DIR, folder_name)
        size_on_disk = str(get_directory_size(game_path))

        try:
            new_content = template_content
            
            # 2. Replace key fields (using regex for text replacement)
            new_content = re.sub(r'("appid"\s+)".*?"', r'\1"' + target_appid + '"', new_content)
            new_content = re.sub(r'("installdir"\s+)".*?"', r'\1"' + folder_name + '"', new_content)
            new_content = re.sub(r'("name"\s+)".*?"', r'\1"' + folder_name + '"', new_content)
            new_content = re.sub(r'("SizeOnDisk"\s+)".*?"', r'\1"' + size_on_disk + '"', new_content)
            
            new_content = re.sub(r'("StateFlags"\s+)".*?"', r'\1"4"', new_content)
            new_content = re.sub(r'("LastUpdated"\s+)".*?"', r'\1"' + current_unix_time + '"', new_content)
            
            # Ensure download/stage counts are 0
            new_content = re.sub(r'("BytesToDownload"\s+)".*?"', r'\1"0"', new_content)
            new_content = re.sub(r'("BytesDownloaded"\s+)".*?"', r'\1"0"', new_content)
            new_content = re.sub(r'("BytesToStage"\s+)".*?"', r'\1"0"', new_content)
            new_content = re.sub(r'("BytesStaged"\s+)".*?"', r'\1"0"', new_content)

            # 3. Write target ACF file
            with open(target_acf_file, 'w', encoding=ACF_ENCODING) as f:
                f.write(new_content)
            
            repaired_count += 1
            print("   👍 Repair successful.")

        except Exception as e:
            print(f"   ❌ Serious error occurred while repairing '{folder_name}': {e}")

    # Process summary and cleanup
    if template_info['source'] == 'GeneratedTemplate':
        try:
            os.remove(template_info['path'])
            print("✅ Temporary generic template file cleaned up.")
        except Exception as e:
            print(f"❌ Failed to clean up temporary template, please manually delete: {template_info['path']}")

    print(f"\n🌟 Batch repair completed! Successfully created/repaired {repaired_count} ACF files.")
    return True

# --- 3. Main Execution Area ---
if __name__ == "__main__":
    print("========================================================")
    print("           Steam ACF File Auto-Repair Tool (Python)")
    print("========================================================")

    # Step 1: Initialization
    print("\n=== [Step 1/3] Initialization and Path Setup ===")
    
    if not os.path.exists(STEAM_APPS_DIR):
        print(f"❌ Error: Steam applications directory not found: {STEAM_APPS_DIR}")
        exit(1)
    
    template_info = find_or_create_template()
    if not template_info:
        exit(1)
        
    if not confirm_step("Step 1 completed. Steam path confirmed and ACF template prepared."):
        exit(0)


    # Step 2: Download mapping table
    game_map = download_and_map_appids()
    if not game_map:
        exit(1)

    print(f"✅ AppID list download and parsing completed. Loaded {len(game_map)} items.")
    if not confirm_step("Step 2 completed. Successfully downloaded and created AppID mapping table."):
        exit(0)


    # Step 3: Execute repair
    if batch_repair_and_write(game_map, template_info):
        print("\n========================================================")
        print("   🥳 All steps completed successfully!")
        print("   1. Please **completely exit** the Steam client immediately.")
        print("   2. Restart Steam, all games will show as 'Installed' status.")
        print("   3. Right-click these games and run 'Verify Integrity of Game Files' to complete the final repair.")
        print("========================================================")
    else:
        print("\n❌ Run failed, please check the error messages above and try again.")