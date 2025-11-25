import os
import re
import time
import requests
import json 
from typing import Dict, Any, Optional

# --- 1. 配置 ---
STEAM_ROOT = r"D:\Program Files (x86)\Steam"
STEAM_APPS_DIR = os.path.join(STEAM_ROOT, "steamapps")
COMMON_DIR = os.path.join(STEAM_APPS_DIR, "common")
APPID_JSON_URL = "https://raw.githubusercontent.com/jsnli/steamappidlist/master/data/games_appid.json"
ACF_ENCODING = 'ascii' 

# --- 2. 核心函數定義 ---

def confirm_step(message: str) -> bool:
    """提示使用者確認是否繼續下一步"""
    print("-" * 50)
    response = input(f"{message} 請輸入 'y' 繼續，或輸入其他鍵退出: ").lower()
    print("-" * 50)
    return response == 'y'

def normalize_name(name: str) -> str:
    """標準化遊戲名稱以進行模糊匹配"""
    normalized = name.upper()
    normalized = re.sub(r'\s', '', normalized)
    normalized = re.sub(r'[-_:.,()]', '', normalized)
    return normalized

def parse_acf_content(content: str) -> Dict[str, str]:
    """使用正則表達式從 VDF 內容中提取關鍵鍵值對"""
    data = {}
    matches = re.findall(r'"(appid|installdir|name|StateFlags|LastUpdated|BytesToDownload|BytesDownloaded|BytesToStage|BytesStaged|AutoUpdateBehavior|AllowOtherDownloadsWhileRunning|ScheduledAutoUpdate)"\s+"([^"]*)"', content)
    for key, value in matches:
        data[key] = value
    return data

def build_acf_content(data: Dict[str, Any]) -> str:
    """從字典資料建立格式化的 ACF/VDF 內容"""
    content_lines = ['"AppState"', '{']
    app_state = data.get('AppState', {})
    
    for key, value in app_state.items():
        line = f'\t"{key}"\t\t"{value}"'
        content_lines.append(line)
        
    content_lines.append('}')
    return "\n".join(content_lines)

def find_or_create_template() -> Optional[Dict[str, Any]]:
    """尋找現有的 ACF 檔案作為範本，否則從零建立"""
    print("-> 正在嘗試尋找現有的 ACF 檔案作為範本...")
    
    acf_files = [f for f in os.listdir(STEAM_APPS_DIR) if f.startswith('appmanifest_') and f.endswith('.acf')]
    
    # --- 嘗試讀取現有範本 ---
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
                print(f"✅ 成功找到並解析現有範本 ACF 檔案: {template_file}")
                return {
                    'path': template_path, 
                    'appid': template_appid, 
                    'installdir': template_installdir, 
                    'source': 'ExistingFile',
                    'content': content
                }
            else:
                print(f"❌ 錯誤: 無法從範本 {template_file} 中提取 AppID 或 Installdir。嘗試從零建立。")
        except Exception as e:
            print(f"❌ 錯誤: 無法讀取範本檔案 {template_file}. 嘗試從零建立. 錯誤訊息: {e}")

    # --- 找不到或解析失敗，從零開始建立 ---
    print("⚠️ 警告: 找不到有效的 ACF 範本，將自動生成一個通用範本。")
    
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
        
        print(f"✅ 已創建臨時通用範本: {temp_acf_name}")
        return {
            'path': template_path, 
            'appid': template_appid, 
            'installdir': template_installdir, 
            'source': 'GeneratedTemplate',
            'content': base_content
        }
    except Exception as e:
        print(f"❌ 錯誤: 無法建立臨時 ACF 檔案。請檢查權限。錯誤訊息: {e}")
        return None

def download_and_map_appids() -> Optional[Dict[str, str]]:
    """下載 AppID JSON 清單並建立映射表"""
    print("\n=== [步驟 2/3] 下載 AppID 清單並建立映射表 (JSON) ===")
    print("-> 正在從 GitHub 下載最新的 AppID JSON 清單...")
    
    try:
        response = requests.get(APPID_JSON_URL, timeout=10)
        response.raise_for_status()
        
        json_data = response.json()
        app_id_map = {}
        
        # 處理列表結構: [{"appid": ..., "name": ...}, ...]
        if isinstance(json_data, list):
            for item in json_data:
                if isinstance(item, dict) and 'appid' in item and 'name' in item:
                    appid_str = str(item['appid'])
                    name_str = item['name']
                    
                    if appid_str.isdigit() and name_str:
                        normalized_name = normalize_name(name_str)
                        app_id_map[normalized_name] = appid_str
            
        elif isinstance(json_data, dict):
            # 處理字典結構: {appid: name}
            for appid_str, name_str in json_data.items():
                if appid_str.isdigit() and name_str:
                    normalized_name = normalize_name(name_str)
                    app_id_map[normalized_name] = appid_str
        
        else:
            print("❌ 錯誤: 下載的 JSON 數據格式無法識別 (既非字典也非列表)。")
            return None

        print(f"✅ AppID 清單下載並解析完成。共載入 {len(app_id_map)} 個項目。")
        return app_id_map

    except requests.exceptions.RequestException as e:
        print(f"❌ 錯誤: 獲取 AppID 清單失敗。請檢查網路連線。錯誤訊息: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ 錯誤: JSON 解析失敗。數據格式不正確。錯誤訊息: {e}")
        return None

def batch_repair_and_write(game_map: Dict[str, str], template_info: Dict[str, Any]) -> bool:
    """批量修復 common 資料夾中的遊戲"""
    print("\n=== [步驟 3/3] 掃描遊戲並創建 ACF 檔案 ===")
    
    template_appid = template_info['appid']
    template_installdir = template_info['installdir']
    template_path = template_info['path']
    template_content = template_info['content']
    repaired_count = 0

    try:
        game_folders = [f for f in os.listdir(COMMON_DIR) if os.path.isdir(os.path.join(COMMON_DIR, f))]
        print(f"-> 在 common 資料夾中找到 {len(game_folders)} 個遊戲資料夾...")
    except FileNotFoundError:
        print(f"❌ 錯誤: 找不到 common 資料夾: {COMMON_DIR}")
        return False
    except PermissionError:
        print("❌ 錯誤: 沒有權限讀取 common 資料夾。請以管理員身份運行。")
        return False

    current_unix_time = str(int(time.time()))

    for folder_name in game_folders:
        normalized_folder_name = normalize_name(folder_name)
        target_appid = game_map.get(normalized_folder_name)

        if not target_appid:
            # print(f"   ⚠️ 遊戲 '{folder_name}' 找不到 AppID，跳過。")
            continue # 為了保持輸出簡潔，只輸出修復成功的項目

        target_acf_file = os.path.join(STEAM_APPS_DIR, f"appmanifest_{target_appid}.acf")

        if os.path.exists(target_acf_file):
            continue

        print(f"   🛠️ 修復中: '{folder_name}' (AppID: {target_appid})...")

        try:
            new_content = template_content
            
            # 2. 替換關鍵欄位 (使用正則表達式進行文本替換)
            new_content = re.sub(r'("appid"\s+)".*?"', r'\1"' + target_appid + '"', new_content)
            new_content = re.sub(r'("installdir"\s+)".*?"', r'\1"' + folder_name + '"', new_content)
            new_content = re.sub(r'("name"\s+)".*?"', r'\1"' + folder_name + '"', new_content)
            
            new_content = re.sub(r'("StateFlags"\s+)".*?"', r'\1"4"', new_content)
            new_content = re.sub(r'("LastUpdated"\s+)".*?"', r'\1"' + current_unix_time + '"', new_content)
            
            # 確保下載/階段計數為 0
            new_content = re.sub(r'("BytesToDownload"\s+)".*?"', r'\1"0"', new_content)
            new_content = re.sub(r'("BytesDownloaded"\s+)".*?"', r'\1"0"', new_content)
            new_content = re.sub(r'("BytesToStage"\s+)".*?"', r'\1"0"', new_content)
            new_content = re.sub(r'("BytesStaged"\s+)".*?"', r'\1"0"', new_content)

            # 3. 寫入目標 ACF 檔案
            with open(target_acf_file, 'w', encoding=ACF_ENCODING) as f:
                f.write(new_content)
            
            repaired_count += 1
            print("   👍 修復成功。")

        except Exception as e:
            print(f"   ❌ 修復 '{folder_name}' 時發生嚴重錯誤: {e}")

    # 流程總結與清理
    if template_info['source'] == 'GeneratedTemplate':
        try:
            os.remove(template_info['path'])
            print("✅ 已清理臨時通用範本文件。")
        except Exception as e:
            print(f"❌ 清理臨時範本失敗，請手動刪除: {template_info['path']}")

    print(f"\n🌟 批次修復完成！成功創建/修復 {repaired_count} 個 ACF 檔案。")
    return True

# --- 3. 主要執行區 ---
if __name__ == "__main__":
    print("========================================================")
    print("           Steam ACF 檔案自動修復工具 (Python)")
    print("========================================================")

    # 步驟 1: 初始化
    print("\n=== [步驟 1/3] 初始化與設定路徑 ===")
    
    if not os.path.exists(STEAM_APPS_DIR):
        print(f"❌ 錯誤：找不到 Steam 應用程式目錄: {STEAM_APPS_DIR}")
        exit(1)
    
    template_info = find_or_create_template()
    if not template_info:
        exit(1)
        
    if not confirm_step("步驟 1 完成。已確認 Steam 路徑並準備好 ACF 範本。"):
        exit(0)


    # 步驟 2: 下載映射表
    game_map = download_and_map_appids()
    if not game_map:
        exit(1)

    print(f"✅ AppID 清單下載並解析完成。共載入 {len(game_map)} 個項目。")
    if not confirm_step("步驟 2 完成。已成功下載並建立 AppID 映射表。"):
        exit(0)


    # 步驟 3: 執行修復
    if batch_repair_and_write(game_map, template_info):
        print("\n========================================================")
        print("   🥳 所有步驟已成功完成！")
        print("   1. 請立即**完全退出** Steam 客戶端。")
        print("   2. 重新啟動 Steam，所有遊戲將顯示為『已安裝』狀態。")
        print("   3. 對這些遊戲點擊右鍵執行『驗證遊戲檔案的完整性』，完成最終修復。")
        print("========================================================")
    else:
        print("\n❌ 運行失敗，請檢查上方錯誤訊息並重新嘗試。")