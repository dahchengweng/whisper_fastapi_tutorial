# 📚 Whisper 語音辨識循序漸進教學 (Tutorials)

本目錄提供從零開始的六個階段獨立範例，幫助開發者逐步掌握 **Faster-Whisper 本地部署**、**Silero VAD 語音活動檢測**、**FastAPI 微服務封裝**，以及最終**與 Java 系統整合**的完整流程。

---

## ⚙️ 執行前共通準備

在執行任何一個 Tutorial 之前，請先開啟終端機（PowerShell 或 Terminal）並完成以下兩個步驟：

1. **切換至專案根目錄並啟動虛擬環境**：
   ```powershell
   # 切換到專案根目錄 (請依實際路徑調整)
   cd D:\development\Projects\RAG\whisper_project

   # 啟動虛擬環境 (Windows PowerShell)
   .\.venv\Scripts\activate
   ```
   *(確認終端機提示字元前方出現 `(.venv)` 即代表成功)*

2. **確認本地模型路徑**：
   檢查各支 `.py` 檔案內的 `MODEL_PATH` 是否指向你本機的模型資料夾（預設為 `r"D:\development\localmodels\faster-whisper-medium"`）。

---

## 🗺️ 學習路線總覽

| 階段 | 檔案 / 資料夾 | 學習主題 | 執行方式 |
| :--- | :--- | :--- | :--- |
| **01** | `tutorial01_hello_whisper.py` | 載入本地模型與基礎語音辨識 | 直接執行 Python 腳本 |
| **02** | `tutorial02_vad_and_opencc.py` | 加入 VAD 靜音過濾與 OpenCC 繁體轉換 | 直接執行 Python 腳本 |
| **03** | `tutorial03_basic_fastapi.py` | 包裝成 FastAPI RESTful 接口 | 啟動 Uvicorn + Swagger UI |
| **04** | `tutorial04_web_recorder/` | 瀏覽器直接錄音與 API 串接 | 啟動 Uvicorn + 網頁測試 |
| **05** | `tutorial05_vad_energy_chart/` | 即時音量能量計算與 VAD 機率圖表 | 啟動 Uvicorn + 網頁測試 |
| **06** | `tutorial06_java_integration/` | Java Spring Boot 呼叫 Python API 範例 | 搭配 Spring Boot 專案執行 |

---

## 🚀 各階段詳細執行方式

### 階段 1：`tutorial01_hello_whisper.py`（純 Python 基礎辨識）
* **前置準備**：請先準備一段測試音檔（支援 `.wav`、`.mp3`、`.m4a` 等），並命名為 `sample.wav` 放入 `tutorial/` 資料夾內（即 `tutorial\sample.wav`）。
* **執行指令**：
  ```powershell
  python tutorial/tutorial01_hello_whisper.py
  ```
* **預期結果**：終端機將印出偵測到的語言、音訊總秒數，以及逐句的時間軸與辨識文字。

---

### 階段 2：`tutorial02_vad_and_opencc.py`（VAD 過濾與台灣繁體轉換）
* **前置準備**：同階段 1，確保 `tutorial\sample.wav` 存在。
* **執行指令**：
  ```powershell
  python tutorial/tutorial02_vad_and_opencc.py
  ```
* **預期結果**：終端機將顯示「原始音訊長度」與「VAD 過濾後的有效長度」，並對照印出模型原始輸出與經過 OpenCC 轉換後的台灣正體中文。

---

### 階段 3：`tutorial03_basic_fastapi.py`（包裝成 FastAPI 微服務）
* **執行指令**：
  ```powershell
  uvicorn tutorial.tutorial03_basic_fastapi:app --host 127.0.0.1 --port 8000 --reload
  ```
* **測試方式**：
  1. 啟動後開啟瀏覽器，前往 Swagger API 互動文件：`http://127.0.0`
  2. 點開 **`POST /transcribe`** 區塊 -> 點擊右上角 **`Try it out`**。
  3. 上傳任意音訊檔並設定 `threshold`（預設 `0.5`），點擊 **`Execute`** 即可在下方看到回傳的 JSON 結果。
* **結束方式**：在終端機按下 `Ctrl + C` 停止伺服器。

---

### 階段 4：`tutorial04_web_recorder/`（瀏覽器麥克風錄音原型）
* **執行指令**：
  ```powershell
  uvicorn tutorial.tutorial04_web_recorder.server:app --host 127.0.0.1 --port 8000 --reload
  ```
* **測試方式**：
  1. 開啟瀏覽器前往：`http://127.0.0.1:8000`
  2. 點擊 **「🔴 開始錄音」**（瀏覽器跳出麥克風權限視窗時請點選「允許」）。
  3. 對著麥克風說話後，點擊 **「⏹️ 停止並送出」**，網頁下方即會顯示繁體中文辨識文字。
* **結束方式**：在終端機按下 `Ctrl + C` 停止伺服器。

---

### 階段 5：`tutorial05_vad_energy_chart/`（VAD 能量計算與門檻圖表）
* **執行指令**：
  ```powershell
  uvicorn tutorial.tutorial05_vad_energy_chart.server:app --host 127.0.0.1 --port 8000 --reload
  ```
* **測試方式**：
  1. 開啟瀏覽器前往：`http://127.0.0.1:8000`
  2. 調整上方的 **Threshold 門檻滑桿**（例如 `0.5`），點擊錄音並說話。
  3. 停止錄音後，畫面除了顯示辨識文字外，底部的黑色畫布還會畫出整段錄音的 **Silero VAD 語音機率折線（綠線）** 與 **Threshold 門檻線（紅線）**。
* **結束方式**：在終端機按下 `Ctrl + C` 停止伺服器。

---

### 階段 6：`tutorial06_java_integration/`（Java Spring Boot 整合示範）
本階段展示當網頁移交給 Java 接手時，如何透過後端轉發音檔給 Python 微服務：

1. **啟動 Python 正式 MVC 後端（Port 8000）**：
   ```powershell
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
2. **設定 Java Spring Boot 專案（Port 8080）**：
   * 將 `SttClientExample.java` 放入你的 Spring Boot `controller` 套件中（需使用 Spring Boot 3.2+ 以支援 `RestClient`）。
   * 將 `application.properties` 內的設定加入你的 Spring Boot 設定檔（放寬檔案上傳大小至 `50MB` 並指定 Python API 網址）。
3. **測試呼叫**：
   啟動 Java 專案後，前端網頁即可將錄音檔發送至 Java 接口 `POST http://127.0.0`，由 Java 轉發給 Python 完成辨識並回傳結果。
