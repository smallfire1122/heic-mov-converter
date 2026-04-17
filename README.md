# HEIC / MOV Converter

Windows 桌面批次轉檔工具，可將：

- `HEIC` 轉為 `JPG`
- `MOV` 轉為 `MP4`

這個專案使用 Python + Tkinter 製作，並支援打包成單一 `EXE`。對一般使用者來說，下載已打包好的 `HeicMovConverter.exe` 就能直接使用，不需要另外安裝 Python。

## 特色

- 支援加入單一檔案
- 支援直接掃描整個資料夾
- 掃描資料夾時只會加入 `HEIC` 與 `MOV`
- 可指定輸出資料夾，也可輸出到原檔旁
- 可勾選是否在成功後刪除原始 `HEIC` / `MOV`
- 顯示進度與轉換紀錄


## 下載方式

一般使用者請到 GitHub Releases 下載：
[![GitHub release](https://img.shields.io/github/v/release/smallfire1122/heic-mov-converter)](https://github.com/smallfire1122/heic-mov-converter/releases)

## 使用方式

1. 點擊 `加入檔案` 或 `加入資料夾`
2. 如果需要，先選擇輸出資料夾
3. 如果需要，勾選是否在轉換成功後刪除原始檔
4. 點擊 `開始轉換`
5. 在下方查看轉換紀錄

如果沒有指定輸出資料夾，轉換後的檔案會放在原始檔案同一個資料夾。

## 從原始碼執行

先安裝相依套件：

```powershell
pip install -r requirements.txt
```

啟動程式：

```powershell
python app.py
```

從原始碼執行時，`MOV -> MP4` 需要系統已安裝 `ffmpeg`。

## 授權

此 repository 內的原始碼採用 MIT License。

第三方元件授權請參考 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
