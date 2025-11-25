# 💾 Steam Library Rescuer (ACF File Generator)

This tool is designed to **fix the issue of missing `appmanifest_xxxxx.acf` files** in the Steam library. When the Steam client loses track of installed games, but the game folders still exist in `steamapps/common`, this tool automatically matches the AppID based on the game folder names and generates the necessary `.acf` files, allowing Steam to recognize the games again.

The project offers two versions: the **Python Local Version** and the **Web Browser Version**.

---

## 💻 1. Python Local Version 

This version executes directly on your computer, providing superior file system access and automation, making it the preferred method for fixing your Steam library.

### ✨ Advantages

* **Full Automation:** Directly reads Steam's `steamapps` and `common` paths without manual folder selection.
* **Direct Write:** Automatically writes the generated `.acf` files directly into the correct `steamapps` directory, eliminating manual copy-pasting.
* **Reliable Template:** Automatically extracts a template from existing `.acf` files or generates a universal one.

### 🚀 Usage (Python)

1.  **Preparation:** Ensure you have **Python 3.x** installed.
2.  **Install Dependencies:**
    ```bash
    pip install requests
    ```
3.  **Run the Rescuer:**
    ```bash
    python python/steam_rescuer.py
    ```
4.  **Follow Prompts:** The script will automatically scan the Steam path, download the AppID list, and proceed with batch repair.
5.  **Final Steps:**
    * **Fully exit** the Steam client.
    * Restart Steam. Games should now appear as "Installed."
    * Right-click on each recovered game and select "**Verify integrity of game files...**" to complete the final validation.

### ⚙️ Configuration

You can modify the configuration variables at the top of the `python/steam_rescuer.py` file to accommodate non-standard Steam installation paths:

```python
# python/steam_rescuer.py
# --- 1. Configuration ---
STEAM_ROOT = r"D:\Program Files (x86)\Steam" # <-- Change your Steam root directory
# ... other configurations
```

---

## 🌐 2. Web Browser Version

This version is suitable for users who cannot install Python or need to perform quick operations anywhere. It utilizes the browser's File System Access API for file handling.

### ✨ Advantages

* **No Installation:** Only a modern browser is required to run.
* **Offline Operation:** All processing is done locally within the browser; **no data is uploaded to any server.**
* **ZIP Output:** Packages the generated `.acf` files into a ZIP archive for easy download.

### 🚀 Usage (Web)

1.  **Open the Tool:** Open the `web/index.html` file in a web browser (Chrome, Firefox, Edge, etc.).
2.  **Select Folder:** Click the button to select the `steamapps/common` folder under your Steam installation path.
3.  **Scan & Generate:** Follow the 3 steps on the page: scan folders, identify AppIDs, and generate/download the ZIP file.
4.  **Apply the Fix:**
    * Extract the downloaded ZIP file.
    * Copy all the `appmanifest_xxxxx.acf` files.
    * Paste them into Steam's `steamapps` folder (e.g., `C:\Program Files (x86)\Steam\steamapps`).
    * Restart the Steam client and run "**Verify integrity of game files...**"

---

## 📂 Project Structure

The project has been refactored to house both the local and web versions of the code.

```
SteamLibraryRescuer/
├── python/
│   └── steam_rescuer.py     # Core Python local execution script (Recommended)
├── web/
│   ├── index.html           # Web version interface structure
│   └── app.js               # Web version JavaScript logic (Scanning, AppID Matching, ACF Generation)
├── README.md                # Main project documentation (This file)
└── LICENSE                  # Project license (if applicable)
```

---

# 💾 Steam 遊戲庫救援工具 (ACF 檔案產生器)

這是一個用於**修復 Steam 遊戲庫中遺失 `appmanifest_xxxxx.acf` 檔案**的跨平台工具。當 Steam 客戶端遺失了遊戲安裝記錄，但遊戲資料夾（位於 `steamapps/common` 中）仍然存在時，本工具可以根據遊戲資料夾名稱，自動匹配 AppID 並生成必要的 `.acf` 檔案，讓 Steam 重新識別遊戲。

專案提供兩種版本：**Python 本地執行版** 和 **Web 瀏覽器版**。

---

## 💻 1. Python 本地執行版

此版本直接在您的電腦上執行，提供更強大的檔案系統存取能力和自動化程度，是修復 Steam 遊戲庫的首選方法。

### ✨ 功能優勢

* **完全自動化：** 直接讀取 Steam 的 `steamapps` 和 `common` 路徑，無需手動選擇資料夾。
* **直接寫入：** 自動將生成的 `.acf` 檔案寫入正確的 `steamapps` 目錄，無需手動複製貼上。
* **可靠範本：** 自動從現有的 `.acf` 檔案中提取範本，或在找不到時生成一個通用範本。

### 🚀 使用方法 (Python)

1.  **環境準備：** 確保您的電腦已安裝 **Python 3.x**。
2.  **安裝依賴：**
    ```bash
    pip install requests
    ```
3.  **執行修復：**
    ```bash
    python python/steam_rescuer.py
    ```
4.  **遵循提示：** 程式會自動掃描 Steam 路徑、下載 AppID 清單，並開始批量修復。
5.  **完成步驟：**
    * 請**完全退出** Steam 客戶端。
    * 重新啟動 Steam。遊戲現在將顯示為『已安裝』狀態。
    * 對每個恢復的遊戲點擊右鍵，選擇「**驗證遊戲檔案的完整性...**」，以完成最終驗證。

### ⚙️ 配置設定

您可以修改 `python/steam_rescuer.py` 檔案頂部的配置變數，以適應非標準的 Steam 安裝路徑：

```python
# python/steam_rescuer.py
# --- 1. 配置 ---
STEAM_ROOT = r"D:\Program Files (x86)\Steam" # <-- 更改您的 Steam 根目錄
# ... 其他配置
```

---

## 🌐 2. Web 瀏覽器版

此版本適合不方便安裝 Python 環境或希望在任何地方快速操作的用戶。它利用瀏覽器的 File System Access API 進行檔案處理。

### ✨ 功能優勢

* **無需安裝：** 只需一個現代瀏覽器即可運行。
* **離線操作：** 所有處理均在瀏覽器內部完成；**不會有任何資料被上傳至任何伺服器。**
* **ZIP 輸出：** 將生成的 `.acf` 檔案打包成一個 ZIP 壓縮檔，便於下載。

### 🚀 使用方法 (Web)

1.  **開啟工具：** 在網頁瀏覽器 (Chrome, Firefox, Edge 等) 中開啟 `web/index.html` 檔案。
2.  **選擇資料夾：** 點擊按鈕，選擇 Steam 安裝路徑下的 `steamapps/common` 資料夾。
3.  **掃描與生成：** 遵循頁面上的 3 個步驟：掃描資料夾、識別 AppID、生成並下載 ZIP 檔案。
4.  **應用修復：**
    * 解壓縮下載的 ZIP 檔案。
    * 複製所有生成的 `appmanifest_xxxxx.acf` 檔案。
    * 將它們直接貼上到 Steam 的 `steamapps` 資料夾中 (例如：`C:\Program Files (x86)\Steam\steamapps`)。
    * 重新啟動 Steam 客戶端，並執行「**驗證遊戲檔案的完整性...**」。

---

## 📂 專案結構

本專案已重構，以便同時容納本地和 Web 版本的程式碼。

```
SteamLibraryRescuer/
├── python/
│   └── steam_rescuer.py     # Python 本地執行版的核心修復腳本 (推薦)
├── web/
│   ├── index.html           # Web 版的介面結構
│   └── app.js               # Web 版的所有 JavaScript 邏輯 (掃描、AppID 匹配、ACF 生成)
├── README.md                # 專案主說明文件 (本檔案)
```