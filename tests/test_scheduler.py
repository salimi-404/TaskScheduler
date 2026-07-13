"""تست‌های واحد (Unit Tests) برای شبیه‌ساز زمان‌بندی وظایف.

این تست‌ها مواردی مانند مقایسه وظایف، مدیریت وابستگی‌ها، تشخیص دور (Cycle)
و رفتار مسدودکننده در صورت اتمام مهلت زمانی (Deadline) را پوشش می‌دهند.
"""

from __future__ import annotations

import unittest

from models.task import Task
from scheduler.task_scheduler import TaskScheduler


class TaskSchedulerTests(unittest.TestCase):
    """مجموعه تست‌ها برای بررسی صحت عملکرد کلاس TaskScheduler."""

    def test_task_comparison_uses_priority(self) -> None:
        """اطمینان از اینکه مقایسه وظایف (<، >، ==) فقط بر اساس اولویت است.
        
        طبق نیاز پروژه، وظیفه‌ای که اولویت عددی کمتری دارد (مثلاً ۰)،
        باید «کمتر» یا کوچک‌تر در نظر گرفته شود تا در صف اولویت زودتر خارج شود.
        """

        urgent = Task("urgent", priority=0, duration=1)
        normal = Task("normal", priority=2, duration=1)

        self.assertLess(urgent, normal)
        self.assertGreater(normal, urgent)

        # وظایف با اولویت یکسان باید برابر در نظر گرفته شوند، فارغ از سایر فیلدها
        self.assertEqual(
            Task("a", priority=1, duration=1),
            Task("b", priority=1, duration=3)
        )

    def test_schedule_respects_dependencies(self) -> None:
        """بررسی اینکه زمان‌بند محدودیت‌های وابستگی را رعایت می‌کند.
        
        خروجی باید یک ترتیب اجرای توپولوژیک درست باشد.
        """

        tasks = [
            Task("A", priority=2, duration=1),
            Task("B", priority=0, duration=1, dependencies=["A"]),
            Task("C", priority=1, duration=1, dependencies=["B"]),
        ]

        result = TaskScheduler(tasks).schedule()

        # با وجود اینکه B اولویت بالاتری دارد، اما چون به A وابسته است باید بعد از آن بیاید.
        self.assertEqual(result.order, ["A", "B", "C"])
        self.assertFalse(result.skipped)

    def test_cycle_is_detected(self) -> None:
        """اطمینان از تشخیص وابستگی‌های چرخشی (Circular Dependencies).
        
        در صورت وجود دور، هیچ وظیفه‌ای نباید اجرا شود.
        """

        tasks = [
            Task("A", priority=0, duration=1, dependencies=["C"]),
            Task("B", priority=1, duration=1, dependencies=["A"]),
            Task("C", priority=2, duration=1, dependencies=["B"]),
        ]

        result = TaskScheduler(tasks).schedule()

        self.assertTrue(result.cycle_report.has_cycle)
        self.assertEqual(result.events, [])

    def test_expired_dependency_blocks_children(self) -> None:
        """بررسی اینکه اگر وظیفه‌ای منقضی شود، تمام وابستگان آن نیز حذف می‌شوند.
        
        اگر وظیفه A به دلیل اتمام مهلت (Deadline) حذف شود، وظیفه B که به آن
        وابسته است هم دیگر نباید اجرا شود.
        """

        tasks = [
            Task("A", priority=0, duration=5, deadline=3),
            Task("B", priority=0, duration=1, dependencies=["A"]),
        ]

        result = TaskScheduler(tasks).schedule()

        self.assertIn("A", result.skipped)
        self.assertIn("B", result.skipped)
        self.assertEqual(result.order, [])


if __name__ == "__main__":
    # اجرای تست‌ها
    unittest.main()
