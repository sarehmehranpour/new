# Improved Selenium Automation Script

این اسکریپت بهبود یافته Selenium با مدیریت خطای بهتر و ساختار منظم‌تر است.

## ویژگی‌های بهبود یافته

### 1. مدیریت خطا (Error Handling)
- مدیریت خطاهای Selenium با try-catch blocks
- Timeout handling برای عناصر صفحه
- Logging کامل برای debugging

### 2. ساختار بهتر کد
- استفاده از کلاس‌ها برای سازماندهی بهتر
- Configuration management با dataclass
- Context manager برای مدیریت منابع

### 3. قابلیت‌های جدید
- Safe element finding با timeout
- Safe clicking و sending keys
- API request handling
- CSV export functionality
- Comprehensive logging

## نصب و راه‌اندازی

### 1. نصب dependencies
```bash
pip install -r requirements.txt
```

### 2. تنظیم Chrome Profile (اختیاری)
اگر می‌خواهید از Chrome profile خاصی استفاده کنید، مسیر آن را در `Config` class تغییر دهید:

```python
chrome_profile_path: str = "/path/to/your/chrome/profile"
```

### 3. اجرای اسکریپت
```bash
python improved_selenium_script.py
```

## نحوه استفاده

### مثال پایه
```python
from improved_selenium_script import SeleniumAutomation, Config

# تنظیمات
config = Config(
    default_timeout=10,
    send_message_timeout=15,
    api_url="https://your-api-url.com"
)

# اجرای automation
with SeleniumAutomation(config) as automation:
    # باز کردن صفحه
    automation.driver.get("https://example.com")
    
    # کلیک روی دکمه
    automation.safe_click(By.ID, "login-button")
    
    # وارد کردن متن
    automation.safe_send_keys(By.NAME, "username", "your_username")
    
    # درخواست API
    api_data = automation.make_api_request({"param": "value"})
    
    # ذخیره در CSV
    automation.save_to_csv(data, "output.csv")
```

### متدهای اصلی

#### `safe_find_element(by, value, timeout=None)`
عنصر را با timeout و error handling پیدا می‌کند.

#### `safe_click(by, value, timeout=None)`
روی عنصر کلیک می‌کند با error handling.

#### `safe_send_keys(by, value, text, timeout=None)`
متن را در عنصر وارد می‌کند با error handling.

#### `make_api_request(params=None)`
درخواست API می‌فرستد با error handling.

#### `save_to_csv(data, filename)`
داده‌ها را در فایل CSV ذخیره می‌کند.

## Logging

اسکریپت تمام فعالیت‌ها را در فایل `selenium_automation.log` ثبت می‌کند و همچنین در console نمایش می‌دهد.

## مزایای کد بهبود یافته

1. **قابلیت نگهداری بهتر**: کد ساختار یافته و قابل فهم
2. **مدیریت خطای قوی**: خطاها به درستی مدیریت می‌شوند
3. **قابلیت توسعه**: به راحتی می‌توان قابلیت‌های جدید اضافه کرد
4. **Logging کامل**: برای debugging و monitoring
5. **Resource Management**: منابع به درستی آزاد می‌شوند
6. **Type Hints**: برای IDE support بهتر

## نکات مهم

- قبل از اجرا، مطمئن شوید که ChromeDriver نصب شده است
- برای استفاده از Chrome profile، مسیر صحیح را تنظیم کنید
- در صورت نیاز به تغییر timeout ها، در `Config` class تغییر دهید