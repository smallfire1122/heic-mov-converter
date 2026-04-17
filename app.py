from __future__ import annotations

import sys
import queue
import shutil
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image
from pillow_heif import register_heif_opener


register_heif_opener()


SUPPORTED_EXTENSIONS = {".heic", ".mov"}


def get_bundled_path(filename: str) -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)) / filename
    return Path(__file__).resolve().parent / "vendor" / filename


def resolve_ffmpeg_path() -> str | None:
    bundled_ffmpeg = get_bundled_path("ffmpeg.exe")
    if bundled_ffmpeg.exists():
        return str(bundled_ffmpeg)
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    return None


@dataclass
class ConversionResult:
    source: Path
    target: Path | None
    success: bool
    message: str
    deleted_source: bool = False


class ConverterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HEIC / MOV Converter")
        self.root.geometry("760x560")
        self.root.minsize(700, 500)

        self.items: list[Path] = []
        self.output_dir = tk.StringVar()
        self.delete_originals = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="請先加入 HEIC 或 MOV 檔案。")
        self.queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self.is_running = False
        self.ffmpeg_path = resolve_ffmpeg_path()

        self._build_ui()
        self.root.after(100, self._process_queue)

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)

        title = ttk.Label(
            container,
            text="HEIC / MOV 批次轉檔",
            font=("Microsoft JhengHei UI", 18, "bold"),
        )
        title.grid(row=0, column=0, sticky="w")

        controls = ttk.Frame(container, padding=(0, 16, 0, 12))
        controls.grid(row=1, column=0, sticky="ew")
        for column in range(4):
            controls.columnconfigure(column, weight=1)

        ttk.Button(controls, text="加入檔案", command=self.add_files).grid(
            row=0, column=0, padx=(0, 8), sticky="ew"
        )
        ttk.Button(controls, text="加入資料夾", command=self.add_folder).grid(
            row=0, column=1, padx=8, sticky="ew"
        )
        ttk.Button(controls, text="清空清單", command=self.clear_items).grid(
            row=0, column=2, padx=8, sticky="ew"
        )
        ttk.Button(controls, text="開始轉換", command=self.start_conversion).grid(
            row=0, column=3, padx=(8, 0), sticky="ew"
        )

        list_frame = ttk.LabelFrame(container, text="待轉換檔案", padding=12)
        list_frame.grid(row=2, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.file_list = tk.Listbox(
            list_frame,
            font=("Consolas", 10),
            selectmode=tk.EXTENDED,
        )
        self.file_list.grid(row=0, column=0, sticky="nsew")

        list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_list.yview)
        list_scroll.grid(row=0, column=1, sticky="ns")
        self.file_list.config(yscrollcommand=list_scroll.set)

        output_frame = ttk.LabelFrame(container, text="輸出設定", padding=12)
        output_frame.grid(row=3, column=0, pady=12, sticky="ew")
        output_frame.columnconfigure(0, weight=1)

        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir)
        output_entry.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        ttk.Button(output_frame, text="選擇輸出資料夾", command=self.choose_output_dir).grid(
            row=0, column=1, sticky="ew"
        )
        ttk.Checkbutton(
            output_frame,
            text="轉換成功後刪除原始 HEIC / MOV",
            variable=self.delete_originals,
        ).grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="w")

        progress_frame = ttk.Frame(container)
        progress_frame.grid(row=4, column=0, sticky="ew")
        progress_frame.columnconfigure(0, weight=1)

        self.progress = ttk.Progressbar(progress_frame, mode="determinate")
        self.progress.grid(row=0, column=0, sticky="ew")

        status = ttk.Label(
            progress_frame,
            textvariable=self.status_var,
            font=("Microsoft JhengHei UI", 10),
        )
        status.grid(row=1, column=0, pady=(8, 0), sticky="w")

        log_frame = ttk.LabelFrame(container, text="轉換紀錄", padding=12)
        log_frame.grid(row=5, column=0, pady=(12, 0), sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        container.rowconfigure(5, weight=1)

        self.log_text = tk.Text(
            log_frame,
            height=10,
            wrap="word",
            font=("Consolas", 10),
            state="disabled",
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")

        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scroll.grid(row=0, column=1, sticky="ns")
        self.log_text.config(yscrollcommand=log_scroll.set)

    def add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="選擇 HEIC 或 MOV 檔案",
            filetypes=[
                ("Supported files", "*.heic *.HEIC *.mov *.MOV"),
                ("All files", "*.*"),
            ],
        )
        self._add_paths(Path(path) for path in paths)

    def add_folder(self) -> None:
        folder = filedialog.askdirectory(title="選擇資料夾")
        if not folder:
            return
        files = [path for path in Path(folder).rglob("*") if path.suffix.lower() in SUPPORTED_EXTENSIONS]
        self._add_paths(files)

    def choose_output_dir(self) -> None:
        folder = filedialog.askdirectory(title="選擇輸出資料夾")
        if folder:
            self.output_dir.set(folder)

    def clear_items(self) -> None:
        if self.is_running:
            return
        self.items.clear()
        self.file_list.delete(0, tk.END)
        self.progress["value"] = 0
        self.status_var.set("已清空清單。")
        self._append_log("已清空待轉換檔案。\n")

    def start_conversion(self) -> None:
        if self.is_running:
            messagebox.showinfo("轉換中", "目前正在轉換，請稍候。")
            return
        if not self.items:
            messagebox.showwarning("沒有檔案", "請先加入要轉換的 HEIC 或 MOV 檔案。")
            return

        output_dir = Path(self.output_dir.get().strip()) if self.output_dir.get().strip() else None
        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)

        if any(path.suffix.lower() == ".mov" for path in self.items) and self.ffmpeg_path is None:
            messagebox.showerror(
                "缺少 ffmpeg",
                "偵測到 MOV 檔案，但程式內找不到可用的 ffmpeg。\n\n請重新下載完整版本，或先只轉換 HEIC 檔案。",
            )
            return

        self.is_running = True
        self.progress["maximum"] = len(self.items)
        self.progress["value"] = 0
        self.status_var.set(f"開始轉換，共 {len(self.items)} 個檔案。")
        self._append_log(f"開始轉換，共 {len(self.items)} 個檔案。\n")

        worker = threading.Thread(
            target=self._convert_worker,
            args=(list(self.items), output_dir, self.delete_originals.get()),
            daemon=True,
        )
        worker.start()

    def _convert_worker(self, items: list[Path], output_dir: Path | None, delete_originals: bool) -> None:
        success_count = 0
        for index, source in enumerate(items, start=1):
            try:
                result = self._convert_file(source, output_dir, delete_originals)
            except Exception as exc:  # noqa: BLE001
                result = ConversionResult(source, None, False, f"轉換失敗: {exc}")

            if result.success:
                success_count += 1

            self.queue.put(("item_done", (index, len(items), result)))

        self.queue.put(("all_done", (success_count, len(items))))

    def _convert_file(self, source: Path, output_dir: Path | None, delete_originals: bool) -> ConversionResult:
        extension = source.suffix.lower()
        target_dir = output_dir if output_dir is not None else source.parent

        if extension == ".heic":
            target = target_dir / f"{source.stem}.jpg"
            with Image.open(source) as image:
                rgb_image = image.convert("RGB")
                rgb_image.save(target, "JPEG", quality=95)
            deleted_source = self._delete_source_file(source, delete_originals)
            return ConversionResult(source, target, True, "HEIC -> JPG 完成", deleted_source)

        if extension == ".mov":
            target = target_dir / f"{source.stem}.mp4"
            command = [
                self.ffmpeg_path or "ffmpeg",
                "-y",
                "-i",
                str(source),
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                "-movflags",
                "+faststart",
                str(target),
            ]
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if completed.returncode != 0:
                error_message = completed.stderr.strip() or "ffmpeg 執行失敗"
                raise RuntimeError(error_message)
            deleted_source = self._delete_source_file(source, delete_originals)
            return ConversionResult(source, target, True, "MOV -> MP4 完成", deleted_source)

        raise ValueError(f"不支援的格式: {source.suffix}")

    def _delete_source_file(self, source: Path, delete_originals: bool) -> bool:
        if not delete_originals:
            return False
        source.unlink()
        return True

    def _process_queue(self) -> None:
        try:
            while True:
                event, payload = self.queue.get_nowait()
                if event == "item_done":
                    index, total, result = payload
                    self.progress["value"] = index
                    self.status_var.set(f"已處理 {index}/{total}: {result.source.name}")
                    if result.success and result.target is not None:
                        suffix = "，原始檔已刪除" if result.deleted_source else ""
                        self._append_log(f"[成功] {result.source.name} -> {result.target.name}{suffix}\n")
                    else:
                        self._append_log(f"[失敗] {result.source.name}: {result.message}\n")
                elif event == "all_done":
                    success_count, total = payload
                    self.is_running = False
                    self.status_var.set(f"轉換完成，成功 {success_count}/{total}。")
                    self._append_log(f"全部完成，成功 {success_count}/{total}。\n")
                    messagebox.showinfo("完成", f"轉換完成，成功 {success_count}/{total}。")
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._process_queue)

    def _add_paths(self, paths: list[Path] | tuple[Path, ...] | object) -> None:
        if self.is_running:
            return

        existing = {path.resolve() for path in self.items}
        added = 0
        for path in paths:
            resolved = Path(path).resolve()
            if not resolved.is_file():
                continue
            if resolved.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            if resolved in existing:
                continue
            self.items.append(resolved)
            existing.add(resolved)
            self.file_list.insert(tk.END, str(resolved))
            added += 1

        self.status_var.set(f"目前共有 {len(self.items)} 個待轉換檔案。")
        if added:
            self._append_log(f"已加入 {added} 個檔案。\n")

    def _append_log(self, message: str) -> None:
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")


def main() -> None:
    root = tk.Tk()
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    ConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
