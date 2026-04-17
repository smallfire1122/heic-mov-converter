# GitHub 上傳流程

以下示範假設你的 GitHub repository 名稱是：

```text
heic-mov-converter
```

並且你的 GitHub 使用者名稱是：

```text
YOUR_GITHUB_USERNAME
```

## 1. 在 GitHub 建立 repository

到 GitHub 建立一個新的 repository，例如：

```text
heic-mov-converter
```

建議不要先勾選自動建立 `README`、`.gitignore` 或 `LICENSE`，因為這些檔案我們已經在本機準備好了。

## 2. 初始化 git

在專案資料夾執行：

```powershell
git init
git branch -M main
git add .
git commit -m "Initial release"
```

## 3. 連接 GitHub repository

把下面網址換成你的 GitHub repository：

```powershell
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/heic-mov-converter.git
git push -u origin main
```

如果你使用 SSH，也可以改成：

```powershell
git remote add origin git@github.com:YOUR_GITHUB_USERNAME/heic-mov-converter.git
git push -u origin main
```

## 4. 建立第一個 Release

在 GitHub repository 頁面：

1. 進入 `Releases`
2. 點擊 `Draft a new release`
3. Tag 可填：

```text
v1.0.0
```

4. Release title 可填：

```text
HeicMovConverter v1.0.0
```

5. 內容可直接貼上 [RELEASE_NOTES_v1.0.0.md](RELEASE_NOTES_v1.0.0.md) 的文字
6. 上傳附件：

```text
dist\HeicMovConverter.exe
```

## 5. 建議 repository About 設定

- Description:

```text
Batch convert HEIC to JPG and MOV to MP4 on Windows.
```

- Topics:

```text
python tkinter ffmpeg heic jpg mov mp4 windows
```

## 6. 發布後的建議

- 在 README 中引導一般使用者去 Releases 下載 `EXE`
- 每次新版本都更新 release notes
- 如果更換 FFmpeg 來源或版本，記得同步更新 `THIRD_PARTY_NOTICES.md`
