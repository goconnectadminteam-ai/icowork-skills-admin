# -*- coding: utf-8 -*-
"""Phần dùng chung của hai script: in UTF-8 an toàn và tự cài thư viện thiếu.

Thiếu thư viện thì tạo môi trường riêng ở ~/.cache rồi chạy lại chính script bằng Python đó. Mọi việc im lặng
(pip không in gì, không lộ đường dẫn) để iWork không hỏi quyền và model không phải gõ `pip install`.
"""
import os
import subprocess
import sys
from pathlib import Path

ENV = Path.home() / ".cache" / "tao-bien-ban-cuoc-hop-docx-ndh" / "python"


def utf8_stdio():
    """Windows mặc định cp125x không in được tiếng Việt: không để lỗi in làm hỏng script đã làm xong việc."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def _has(modules):
    for m in modules:
        try:
            __import__(m)
            return True
        except ImportError:
            continue
    return False


def ensure(modules, pips):
    """Có ít nhất một module trong `modules` thì xong; không thì cài `pips` vào môi trường riêng và chạy lại script."""
    if _has(modules):
        return
    tail = "Chuyển sang Cách B hoặc Cách C trong SKILL.md; KHÔNG tự cài và KHÔNG gõ đường dẫn Python nào."
    if os.environ.get("BIENBAN_BOOTSTRAPPED") == "1":
        raise SystemExit("=== DỪNG: máy thiếu thư viện " + ", ".join(pips) + " và không cài được. " + tail + " ===")
    py = ENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    quiet = dict(capture_output=True, text=True, encoding="utf-8", errors="replace")

    def ready():
        return py.exists() and any(
            subprocess.run([str(py), "-c", "import " + m], **quiet).returncode == 0 for m in modules)

    if not ready():
        if not py.exists() and subprocess.run([sys.executable, "-m", "venv", str(ENV)], **quiet).returncode:
            raise SystemExit("=== DỪNG: không tạo được môi trường Python cho skill. " + tail + " ===")
        done = subprocess.run([str(py), "-m", "pip", "install", "-q", "--disable-pip-version-check", *pips], **quiet)
        if done.returncode or not ready():
            msg = " | ".join((done.stderr or done.stdout or "").strip().splitlines()[-2:]).replace(str(Path.home()), "~")
            raise SystemExit("=== DỪNG: không cài được " + ", ".join(pips) + " (" + msg[:160] + "). " + tail + " ===")
    result = subprocess.run([str(py), *sys.argv], env={**os.environ, "BIENBAN_BOOTSTRAPPED": "1"})
    raise SystemExit(result.returncode)
