#!/usr/bin/env python3
"""
WhatsApp Bot - ربات واتساپ
رباتی که شماره‌ها را از API می‌گیرد، بررسی می‌کند آیا در واتساپ ثبت‌نام کرده‌اند یا نه،
مخاطبین را اضافه می‌کند و پیام می‌فرستد.
"""

import logging
import time
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException


@dataclass
class Config:
    """تنظیمات ربات"""
    api_url: str = "https://your-api-endpoint.com/numbers"  # آدرس API شما
    api_key: str = "your-api-key"  # کلید API شما
    default_message: str = "سلام! این پیام از ربات واتساپ ارسال شده است."
    default_timeout: int = 10
    wait_between_actions: float = 2.0
    log_file: str = "whatsapp_bot.log"
    results_file: str = "results.json"


class WhatsAppBot:
    """کلاس اصلی ربات واتساپ"""
    
    def __init__(self, config: Config):
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self._setup_logging()
        self.results = {
            "successful": [],
            "not_registered": [],
            "failed": [],
            "timestamp": datetime.now().isoformat()
        }
    
    def _setup_logging(self) -> None:
        """راه‌اندازی سیستم لاگینگ"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self) -> bool:
        """راه‌اندازی مرورگر Chrome"""
        try:
            chrome_options = Options()
            
            # تنظیمات Chrome برای واتساپ وب
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # غیرفعال کردن notifications
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2
            })
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.config.default_timeout)
            
            self.logger.info("مرورگر Chrome با موفقیت راه‌اندازی شد")
            return True
            
        except Exception as e:
            self.logger.error(f"خطا در راه‌اندازی مرورگر: {str(e)}")
            return False
    
    def open_whatsapp_web(self) -> bool:
        """باز کردن واتساپ وب"""
        try:
            self.driver.get("https://web.whatsapp.com")
            self.logger.info("واتساپ وب باز شد")
            
            # منتظر QR code یا لاگین
            self.logger.info("لطفاً QR code را اسکن کنید یا وارد شوید...")
            
            # منتظر بارگذاری کامل صفحه
            self.wait.until(EC.presence_of_element_located((By.ID, "side")))
            self.logger.info("واتساپ وب با موفقیت بارگذاری شد")
            return True
            
        except TimeoutException:
            self.logger.error("خطا در بارگذاری واتساپ وب")
            return False
        except Exception as e:
            self.logger.error(f"خطا در باز کردن واتساپ وب: {str(e)}")
            return False
    
    def get_numbers_from_api(self) -> List[str]:
        """دریافت شماره‌ها از API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(self.config.api_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # استخراج شماره‌ها از پاسخ API
            numbers = []
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and 'phone' in item:
                        numbers.append(item['phone'])
                    elif isinstance(item, str):
                        numbers.append(item)
            elif isinstance(data, dict) and 'numbers' in data:
                numbers = data['numbers']
            
            self.logger.info(f"{len(numbers)} شماره از API دریافت شد")
            return numbers
            
        except Exception as e:
            self.logger.error(f"خطا در دریافت شماره‌ها از API: {str(e)}")
            return []
    
    def format_phone_number(self, phone: str) -> str:
        """فرمت کردن شماره تلفن برای واتساپ"""
        # حذف کاراکترهای غیرضروری
        phone = re.sub(r'[^\d+]', '', phone)
        
        # اگر شماره با + شروع نشده، اضافه کردن کد کشور ایران
        if not phone.startswith('+'):
            if phone.startswith('0'):
                phone = '+98' + phone[1:]
            elif phone.startswith('98'):
                phone = '+' + phone
            else:
                phone = '+98' + phone
        
        return phone
    
    def check_contact_exists(self, phone: str) -> bool:
        """بررسی وجود مخاطب در لیست"""
        try:
            # کلیک روی دکمه جستجو
            search_box = self.wait.until(EC.presence_of_element_located((
                By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'
            )))
            search_box.clear()
            search_box.send_keys(phone)
            time.sleep(2)
            
            # بررسی وجود نتیجه جستجو
            try:
                contact_element = self.driver.find_element(By.XPATH, 
                    f'//span[@title="{phone}"]')
                self.logger.info(f"مخاطب {phone} در لیست موجود است")
                return True
            except NoSuchElementException:
                self.logger.info(f"مخاطب {phone} در لیست موجود نیست")
                return False
                
        except Exception as e:
            self.logger.error(f"خطا در بررسی مخاطب {phone}: {str(e)}")
            return False
    
    def add_contact(self, phone: str) -> bool:
        """اضافه کردن مخاطب جدید"""
        try:
            # کلیک روی دکمه منو (سه نقطه)
            menu_button = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, '//div[@data-testid="menu-bar-menu"]'
            )))
            menu_button.click()
            time.sleep(1)
            
            # کلیک روی "New contact"
            new_contact_button = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, '//div[contains(text(), "New contact")]'
            )))
            new_contact_button.click()
            time.sleep(1)
            
            # وارد کردن نام مخاطب
            name_field = self.wait.until(EC.presence_of_element_located((
                By.XPATH, '//input[@data-testid="contact-name-input"]'
            )))
            contact_name = f"کدیورز{phone}"
            name_field.send_keys(contact_name)
            
            # وارد کردن شماره تلفن
            phone_field = self.wait.until(EC.presence_of_element_located((
                By.XPATH, '//input[@data-testid="contact-phone-input"]'
            )))
            phone_field.send_keys(phone)
            
            # کلیک روی دکمه ذخیره
            save_button = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, '//div[@data-testid="save-button"]'
            )))
            save_button.click()
            time.sleep(2)
            
            self.logger.info(f"مخاطب {phone} با نام {contact_name} اضافه شد")
            return True
            
        except Exception as e:
            self.logger.error(f"خطا در اضافه کردن مخاطب {phone}: {str(e)}")
            return False
    
    def check_whatsapp_registration(self, phone: str) -> bool:
        """بررسی ثبت‌نام شماره در واتساپ"""
        try:
            # باز کردن چت با شماره
            chat_url = f"https://web.whatsapp.com/send?phone={phone.replace('+', '')}"
            self.driver.get(chat_url)
            time.sleep(5)
            
            # بررسی وجود پیام خطا
            try:
                error_element = self.driver.find_element(By.XPATH, 
                    '//div[contains(text(), "Phone number shared via url is invalid")]')
                self.logger.warning(f"شماره {phone} در واتساپ ثبت‌نام نکرده است")
                return False
            except NoSuchElementException:
                # بررسی وجود دکمه ارسال پیام
                try:
                    send_button = self.driver.find_element(By.XPATH, 
                        '//span[@data-testid="send"]')
                    self.logger.info(f"شماره {phone} در واتساپ ثبت‌نام کرده است")
                    return True
                except NoSuchElementException:
                    self.logger.warning(f"شماره {phone} در واتساپ ثبت‌نام نکرده است")
                    return False
                    
        except Exception as e:
            self.logger.error(f"خطا در بررسی ثبت‌نام {phone}: {str(e)}")
            return False
    
    def send_message(self, phone: str, message: str = None) -> bool:
        """ارسال پیام به شماره"""
        try:
            # باز کردن چت با شماره
            chat_url = f"https://web.whatsapp.com/send?phone={phone.replace('+', '')}"
            self.driver.get(chat_url)
            time.sleep(5)
            
            # وارد کردن پیام
            message_box = self.wait.until(EC.presence_of_element_located((
                By.XPATH, '//div[@contenteditable="true"][@data-tab="6"]'
            )))
            
            message_text = message or self.config.default_message
            message_box.send_keys(message_text)
            time.sleep(1)
            
            # ارسال پیام
            send_button = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, '//span[@data-testid="send"]'
            )))
            send_button.click()
            time.sleep(2)
            
            self.logger.info(f"پیام به {phone} ارسال شد")
            return True
            
        except Exception as e:
            self.logger.error(f"خطا در ارسال پیام به {phone}: {str(e)}")
            return False
    
    def process_number(self, phone: str) -> Dict[str, any]:
        """پردازش یک شماره"""
        result = {
            "phone": phone,
            "status": "unknown",
            "message": "",
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # فرمت کردن شماره
            formatted_phone = self.format_phone_number(phone)
            
            # بررسی ثبت‌نام در واتساپ
            if not self.check_whatsapp_registration(formatted_phone):
                result["status"] = "not_registered"
                result["message"] = "شماره در واتساپ ثبت‌نام نکرده است"
                self.results["not_registered"].append(result)
                return result
            
            # بررسی وجود در مخاطبین
            if not self.check_contact_exists(formatted_phone):
                # اضافه کردن مخاطب
                if self.add_contact(formatted_phone):
                    result["message"] += "مخاطب اضافه شد. "
                else:
                    result["status"] = "failed"
                    result["message"] += "خطا در اضافه کردن مخاطب. "
                    self.results["failed"].append(result)
                    return result
            
            # ارسال پیام
            if self.send_message(formatted_phone):
                result["status"] = "successful"
                result["message"] += "پیام با موفقیت ارسال شد"
                self.results["successful"].append(result)
            else:
                result["status"] = "failed"
                result["message"] += "خطا در ارسال پیام"
                self.results["failed"].append(result)
            
        except Exception as e:
            result["status"] = "failed"
            result["message"] = f"خطای عمومی: {str(e)}"
            self.results["failed"].append(result)
        
        return result
    
    def save_results(self) -> None:
        """ذخیره نتایج در فایل"""
        try:
            with open(self.config.results_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            self.logger.info(f"نتایج در فایل {self.config.results_file} ذخیره شد")
        except Exception as e:
            self.logger.error(f"خطا در ذخیره نتایج: {str(e)}")
    
    def run(self) -> None:
        """اجرای اصلی ربات"""
        try:
            # راه‌اندازی مرورگر
            if not self.setup_driver():
                return
            
            # باز کردن واتساپ وب
            if not self.open_whatsapp_web():
                return
            
            # دریافت شماره‌ها از API
            numbers = self.get_numbers_from_api()
            if not numbers:
                self.logger.error("هیچ شماره‌ای از API دریافت نشد")
                return
            
            # پردازش هر شماره
            for i, phone in enumerate(numbers, 1):
                self.logger.info(f"پردازش شماره {i}/{len(numbers)}: {phone}")
                result = self.process_number(phone)
                
                # نمایش نتیجه
                status_emoji = {
                    "successful": "✅",
                    "not_registered": "❌",
                    "failed": "⚠️"
                }
                emoji = status_emoji.get(result["status"], "❓")
                self.logger.info(f"{emoji} {phone}: {result['message']}")
                
                # تاخیر بین عملیات
                time.sleep(self.config.wait_between_actions)
            
            # ذخیره نتایج
            self.save_results()
            
            # نمایش خلاصه
            self.logger.info("=== خلاصه نتایج ===")
            self.logger.info(f"موفق: {len(self.results['successful'])}")
            self.logger.info(f"ثبت‌نام نکرده: {len(self.results['not_registered'])}")
            self.logger.info(f"ناموفق: {len(self.results['failed'])}")
            
        except Exception as e:
            self.logger.error(f"خطای عمومی در اجرای ربات: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("مرورگر بسته شد")


def main():
    """تابع اصلی"""
    # تنظیمات ربات
    config = Config(
        api_url="https://your-api-endpoint.com/numbers",  # آدرس API خود را وارد کنید
        api_key="your-api-key",  # کلید API خود را وارد کنید
        default_message="سلام! این پیام از ربات واتساپ ارسال شده است.",
        default_timeout=15,
        wait_between_actions=3.0
    )
    
    # ایجاد و اجرای ربات
    bot = WhatsAppBot(config)
    bot.run()


if __name__ == "__main__":
    main()