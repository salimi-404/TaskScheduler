# 📋 مستندات زمان‌بند (Task Scheduler)

در این بخش، ساختار کلاس اصلی زمان‌بندی وظایف و منطق چیدمان آن‌ها بررسی شده است. این مستندات به ترتیب جریان منطقی سیستم تنظیم شده‌اند.

---

## ۱. مقداردهی اولیه و ساخت گراف
کلاس اصلی زمان‌بند که وظیفه گرفتن وظایف و ساخت گراف وابستگی‌ها را بر عهده دارد.

::: scheduler.task_scheduler.TaskScheduler
    options:
      members:
        - __init__

---

## ۲. موتور اصلی زمان‌بندی (Logic)
این متد قلب تپنده بخش زمان‌بند است. فرآیند کشف دور (Cycle)، مدیریت صف اولویت‌دار (Heap)، بررسی ددلاین‌ها و اختصاص زمان به تسک‌ها در این بخش مدیریت می‌شود.

::: scheduler.task_scheduler.TaskScheduler
    options:
      members:
        - schedule

---

## ۳. متدها و مکانیک‌های داخلی (زیر کاپوت)
این متدها وظایف کمکی زمان‌بند را برای مدیریت اولویت‌ها بر اساس میزان Slack و مدیریت آبشاری تسک‌های مسدود شده بر عهده دارند.

::: scheduler.task_scheduler.TaskScheduler
    options:
      members:
        - _push_ready_task
        - _mark_dependents_blocked
        - _tasks_in_cycle