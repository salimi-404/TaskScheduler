from functools import total_ordering


@total_ordering
class Task:
    """مدل دامنه وظیفه (Task).

    یک وظیفه نمایانگر واحدی از کار است که باید زمان‌بندی شود. عملگرهای مقایسه‌ای
    تعریف شده در این کلاس، صرفاً بر اساس اولویت (priority) کار می‌کنند (طبق نیاز تست‌های پروژه).

    Args:
        task_id (str): شناسه منحصربه‌فرد برای وظیفه.
        priority (int): اولویت عددی (اولویت 0 بیشترین فوریت را دارد).
        duration (int): مدت زمان تخمینی انجام کار (عدد صحیح مثبت).
        dependencies (list, optional): لیست اختیاری از شناسه‌های وظایف پیش‌نیاز.
        deadline (int, optional): زمان نهایی (Timestamp) یا None.
        profit (int, optional): سود حاصل از تکمیل وظیفه (عدد صحیح).

    Raises:
        ValueError: در صورتی که قوانین اعتبارسنجی نقض شوند (مانند شناسه خالی، اولویت منفی، 
            زمان اجرای غیرمثبت، زمان نهایی منفی یا وابستگی وظیفه به خودش).
    """

    def __init__(self, task_id, priority, duration, dependencies=None, deadline=None, profit=0):
        if dependencies is None:
            dependencies = []

        self.task_id = task_id.strip()
        self.priority = priority
        self.duration = duration
        self.dependencies = dependencies
        self.deadline = deadline
        self.profit = profit

        # اجرای اعتبارسنجی در هنگام نمونه‌سازی
        self._validate()

    def _validate(self):
        """اعتبارسنجی داخلی فیلدهای وظیفه.

        رشته‌های وابستگی را پاک‌سازی کرده و قوانین اصلی داده‌ها را بررسی می‌کند.
        """

        # پاک‌سازی لیست وابستگی‌ها از فضاهای خالی
        clean_deps = []
        for d in self.dependencies:
            d = d.strip()
            if d:
                clean_deps.append(d)
        self.dependencies = clean_deps

        # بررسی خالی نبودن شناسه
        if self.task_id == "":
            raise ValueError("Task id cannot be empty")

        # اولویت نمی‌تواند عدد منفی باشد
        if self.priority < 0:
            raise ValueError("Priority must be >= 0")

        # مدت زمان اجرا باید حتماً بزرگتر از صفر باشد
        if self.duration <= 0:
            raise ValueError("Duration must be > 0")

        # زمان نهایی در صورت وجود نباید منفی باشد
        if self.deadline is not None and self.deadline < 0:
            raise ValueError("Deadline cannot be negative")

        # یک وظیفه نمی‌تواند به خودش وابسته باشد
        if self.task_id in self.dependencies:
            raise ValueError("Task cannot depend on itself")

    def __lt__(self, other):
        """بررسی کوچک‌تر بودن بر اساس اولویت."""
        return self.priority < other.priority

    def __eq__(self, other):
        """بررسی برابری بر اساس اولویت."""
        return self.priority == other.priority

    def is_urgent(self):
        """بررسی فوری بودن وظیفه.
        
        Returns:
            bool: اگر اولویت برابر با 0 باشد، مقدار True برمی‌گرداند.
        """
        return self.priority == 0

    def has_deadline(self):
        """بررسی وجود زمان نهایی برای وظیفه.
        
        Returns:
            bool: اگر زمان نهایی تنظیم شده باشد، مقدار True برمی‌گرداند.
        """
        return self.deadline is not None

    @classmethod
    def from_csv_line(cls, line):
        """ایجاد یک شیء Task از یک خط با فرمت CSV.

        فرمت مورد انتظار: ``id, priority, duration, dependencies, deadline, profit``
        وابستگی‌ها می‌توانند با کاراکتر ``|`` جدا شوند. برای موارد خالی از ``-`` استفاده شود.
        
        Args:
            line (str): یک خط متن از فایل CSV.

        Returns:
            Task: یک نمونه جدید از کلاس Task.
        """
        parts = line.split(",")
        task_id = parts[0].strip()
        priority = int(parts[1])
        duration = int(parts[2])

        # پردازش وابستگی‌ها
        dependencies = []
        if len(parts) > 3 and parts[3] != "-":
            dependencies = parts[3].split("|")

        # پردازش زمان نهایی
        deadline = None
        if len(parts) > 4 and parts[4] != "-":
            deadline = int(parts[4])

        # پردازش سود
        profit = 0
        if len(parts) > 5 and parts[5] != "-":
            profit = int(parts[5])

        return cls(task_id, priority, duration, dependencies, deadline, profit)

    def to_short_text(self):
        """ایجاد یک خلاصه متنی کوتاه و قابل خواندن از وظیفه.
        
        Returns:
            str: خلاصه‌ای از ویژگی‌های اصلی وظیفه.
        """
        deps = "-" if not self.dependencies else "|".join(self.dependencies)
        dl = "-" if self.deadline is None else str(self.deadline)
        return f"{self.task_id} (p={self.priority}, d={self.duration}, deps={deps}, dl={dl}, profit={self.profit})"
