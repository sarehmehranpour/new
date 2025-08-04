#!/usr/bin/env python3
"""
Test file for WhatsApp Bot - فایل تست ربات واتساپ
"""

from whatsapp_bot import WhatsAppBot, Config
import json

def test_with_sample_data():
    """تست ربات با داده‌های نمونه"""
    
    # تنظیمات تست
    config = Config(
        api_url="https://jsonplaceholder.typicode.com/users",  # API تست
        api_key="test-key",
        default_message="سلام! این پیام تست از ربات واتساپ است.",
        default_timeout=10,
        wait_between_actions=1.0
    )
    
    # ایجاد ربات
    bot = WhatsAppBot(config)
    
    # تست دریافت شماره‌ها از API
    print("در حال دریافت شماره‌ها از API...")
    numbers = bot.get_numbers_from_api()
    print(f"تعداد شماره‌های دریافت شده: {len(numbers)}")
    
    # تست فرمت کردن شماره‌ها
    print("\nتست فرمت کردن شماره‌ها:")
    test_numbers = ["09123456789", "+989876543210", "98987654321"]
    for phone in test_numbers:
        formatted = bot.format_phone_number(phone)
        print(f"{phone} -> {formatted}")
    
    # تست ذخیره نتایج
    print("\nتست ذخیره نتایج...")
    test_results = {
        "successful": [
            {
                "phone": "+989123456789",
                "status": "successful",
                "message": "پیام با موفقیت ارسال شد",
                "timestamp": "2024-01-01T12:00:00"
            }
        ],
        "not_registered": [
            {
                "phone": "+989876543210",
                "status": "not_registered",
                "message": "شماره در واتساپ ثبت‌نام نکرده است",
                "timestamp": "2024-01-01T12:00:00"
            }
        ],
        "failed": [],
        "timestamp": "2024-01-01T12:00:00"
    }
    
    bot.results = test_results
    bot.save_results()
    print("نتایج تست ذخیره شد")
    
    print("\n✅ تست‌ها با موفقیت انجام شد!")

def test_api_formats():
    """تست فرمت‌های مختلف API"""
    
    print("تست فرمت‌های مختلف API:")
    
    # فرمت 1: آرایه ساده
    format1 = ["+989123456789", "+989876543210"]
    print(f"فرمت 1: {format1}")
    
    # فرمت 2: آرایه با آبجکت
    format2 = [{"phone": "+989123456789"}, {"phone": "+989876543210"}]
    print(f"فرمت 2: {format2}")
    
    # فرمت 3: آبجکت با کلید numbers
    format3 = {"numbers": ["+989123456789", "+989876543210"]}
    print(f"فرمت 3: {format3}")

if __name__ == "__main__":
    print("=== تست ربات واتساپ ===\n")
    
    # تست فرمت‌های API
    test_api_formats()
    print()
    
    # تست اصلی
    test_with_sample_data()