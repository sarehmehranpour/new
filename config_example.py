#!/usr/bin/env python3
"""
Example Configuration - نمونه تنظیمات
این فایل نشان می‌دهد چگونه تنظیمات API خود را وارد کنید.
"""

from whatsapp_bot import Config

# نمونه تنظیمات برای API شما
def get_config():
    """دریافت تنظیمات ربات"""
    
    config = Config(
        # آدرس API شما - این را تغییر دهید
        api_url="https://your-api-endpoint.com/api/numbers",
        
        # کلید API شما - این را تغییر دهید
        api_key="your-secret-api-key",
        
        # پیام پیش‌فرض - این را تغییر دهید
        default_message="سلام! این پیام از ربات واتساپ ارسال شده است.",
        
        # تنظیمات زمانی
        default_timeout=15,  # ثانیه
        wait_between_actions=3.0,  # ثانیه
        
        # فایل‌های خروجی
        log_file="whatsapp_bot.log",
        results_file="results.json"
    )
    
    return config

# نمونه استفاده
if __name__ == "__main__":
    config = get_config()
    print("تنظیمات ربات:")
    print(f"API URL: {config.api_url}")
    print(f"Default Message: {config.default_message}")
    print(f"Timeout: {config.default_timeout} seconds")
    print(f"Wait between actions: {config.wait_between_actions} seconds")