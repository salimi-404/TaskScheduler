"""سیستم ثبت وقایع (Logger) سبک برای نمایش در کنسول.

این ماژول صرفاً یک تابع کمکی ارائه می‌دهد تا پیام‌های خروجی را 
همراه با زمان دقیق (ساعت:دقیقه:ثانیه) برچسب‌گذاری کند.
"""

from __future__ import annotations

from datetime import datetime


def log(message: str) -> None:
    """چاپ پیام در خروجی استاندارد همراه با زمان فعلی.

    Args:
        message (str): متنی که باید در کنسول چاپ شود.
    """

    # قالب‌بندی زمان به صورت ساعت:دقیقه:ثانیه
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
