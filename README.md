# 🎙️ Whisper STT Web Service (FastAPI + Faster-Whisper)

基於 **FastAPI** 與 **Faster-Whisper** 建置的本地離線語音辨識（Speech-to-Text）微服務。採用標準 **MVC 分層架構**設計，內建瀏覽器即時錄音介面、**Silero VAD 語音活動檢測能量視覺化**，並整合 **OpenCC** 確保輸出道地的台灣繁體中文。

本專案後端設計為純 RESTful API 模式，前端測試網頁（`static/`）未來可無痛抽換並整合至 **Java (Spring Boot)** 系統中。

---

## ✨ 核心功能

- **完全離線推論**：支援指定本機 `faster-whisper` 模型路徑，無需依賴外部雲端 API。
- **標準 MVC 架構**：將路由（Controller）、核心推論（Service）與資料結構（Model/Schema）徹底解耦。
- **網頁即時錄音與能量監控**：使用 Web Audio API 與 MediaRecorder 實現瀏覽器直接錄音，即時顯示麥克風 RMS 能量與 Threshold 門檻紅線。
- **Silero VAD 語音機率曲線**：後端計算整段音訊的語音活動機率時間軸（0.0 ~ 1.0），回傳並繪製對照圖表。
- **台灣繁體中文輸出**：透過 `initial_prompt` 引導與 `OpenCC (s2twp)` 轉換，自動將簡體字與大陸用語轉為台灣正體中文。

---

## 📂 專案目錄結構

```text
whisper_project/
├── app/
│   ├── __init__.py
│   ├── main.py                 # 應用程式進入點、CORS 設定與靜態網頁掛載
│   ├── controllers/            # [Controller] API 路由與請求參數驗證
│   │   ├── __init__.py
│   │   └── stt_controller.py
│   ├── models/                 # [Model] Pydantic 資料結構 (對應 Java DTO)
│   │   ├── __init__.py
│   │   └── stt_schema.py
│   └── services/               # [Service] Faster-Whisper 推論、VAD 計算與 OpenCC 轉換
│       ├── __init__.py
│       └── whisper_service.py
├── static/                     # [View] 前期測試用前端 (未來可由 Java 專案接手)
│   ├── index.html
│   ├── style.css
│   └── app.js
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

## 🚀 快速開始

### 1. 建立並啟動虛擬環境
建議使用 Python 3.10 ~ 3.13 版本：

```bash
# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境 (Windows PowerShell)
.\.venv\Scripts\activate

# 啟動虛擬環境 (Mac / Linux)
source .venv/bin/activate
```

### 2. 安裝依賴套件
```bash
pip install fastapi uvicorn python-multipart faster-whisper numpy opencc-python-reimplemented
```
*(註：若在 Python 3.13 環境下遇到 PyAV `metadata_errors` 參數相容性問題，請升級 `faster-whisper` 至最新版或移除 `faster_whisper/audio.py` 中的該參數。)*

### 3. 設定本地模型路徑
請先將 CTranslate2 格式的 Whisper 模型（如 `faster-whisper-medium`）下載至本機目錄，並確認 `app/services/whisper_service.py` 中的路徑設定正確：
```python
self.model_path = r"D:\development\localmodels\faster-whisper-medium"
```

### 4. 啟動服務
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **網頁測試台**：開啟瀏覽器前往 `http://127.0.0.1:8000`（需允許麥克風權限）
- **Swagger API 文件**：開啟瀏覽器前往 `http://127.0.0`

---

## 🔌 API 規格說明

### `POST /api/stt/transcribe`
接收音訊檔案並執行 VAD 檢測與語音辨識。

- **Content-Type**: `multipart/form-data`
- **請求參數**：

  | 欄位名稱 | 型別 | 預設值 | 說明 |
  | :--- | :--- | :--- | :--- |
  | `file` | File | (必填) | 音訊檔案（支援 `.webm`, `.wav`, `.mp3`, `.m4a` 等格式） |
  | `vad_filter` | Boolean | `true` | 是否啟用 VAD 靜音過濾 |
  | `min_silence_duration_ms` | Integer | `500` | 判定為靜音的最短毫秒數 |
  | `threshold` | Float | `0.5` | 語音活動判定門檻值（`0.0` ~ `1.0`） |

- **回應範例 (`200 OK`)**：
  ```json
  {
    "status": "success",
    "language": "zh",
    "duration": 3.45,
    "vad_metrics": {
      "enabled": true,
      "threshold": 0.5,
      "min_silence_duration_ms": 500,
      "max_speech_prob": 0.982,
      "avg_speech_prob": 0.614,
      "timeline": [
        { "time_sec": 0.0, "speech_prob": 0.012 },
        { "time_sec": 0.1, "speech_prob": 0.945 }
      ]
    },
    "full_text": "這是一段繁體中文語音辨識測試。",
    "segments": [
      {
        "start": 0.12,
        "end": 3.20,
        "text": "這是一段繁體中文語音辨識測試。"
      }
    ]
  }
  ```

---

## ☕ 未來整合至 Java (Spring Boot) 指南

當網頁介面移交給 Java 專案接手時，無需改動 Python 端的核心推論邏輯：
1. **移除測試前端**：刪除 `app/main.py` 中的 `app.mount("/", StaticFiles(...))`，讓 FastAPI 純粹作為背景推論微服務（Port 8000）。
2. **搬移靜態資源**：將 `static/` 內的 `style.css` 與 `app.js` 複製到 Java Spring Boot 的 `src/main/resources/static/` 目錄下。
3. **API 對接方式**：
   - **架構 A（Java 後端轉發 - 推薦）**：前端將錄音送至 Java Controller，Java 透過 `RestClient` / `WebClient` 轉發 `multipart/form-data` 至 `http://127.0.0`，取得結果後進行權限控管或寫入資料庫。
   - **架構 B（前端直連）**：修改 `app.js` 最上方的 `API_URL` 為 Python 伺服器位址即可直接跨域呼叫（後端已預設開啟 CORS）。

---

## 📄 授權條款
本專案採用 [MIT License](LICENSE) 授權。
