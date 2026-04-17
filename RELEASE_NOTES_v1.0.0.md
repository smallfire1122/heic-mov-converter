# HeicMovConverter v1.0.0

## 版本亮點

- 新增 Windows 圖形介面，可批次轉換 `HEIC -> JPG` 與 `MOV -> MP4`
- 支援加入整個資料夾，並自動只挑出 `HEIC` 與 `MOV`
- 可指定輸出資料夾
- 可選擇是否在轉換成功後刪除原始檔
- 單一 `EXE` 版本可內建 `ffmpeg`，下載後可直接使用
- 轉換 `MOV` 時不會跳出黑色終端機視窗

## 下載

- `HeicMovConverter.exe`

## 使用提醒

- `HEIC` 會轉為 `JPG`
- `MOV` 會轉為 `MP4`
- 如果勾選刪除原始檔，只有在新檔成功建立後才會刪除原始 `HEIC` / `MOV`

## 已知事項

- 首次啟動單檔 `EXE` 可能會稍慢，因為需要先解壓縮內部資源
- 某些 Windows 防毒軟體可能會在第一次執行時多掃描幾秒
