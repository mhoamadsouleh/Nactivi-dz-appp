bot_token = "7723535106:AAFJfJn9TWIBQBxjgL7NbT_JVvSD1nQodF4"
import requests
import json
import re
import os
import threading
import time
from datetime import datetime, timedelta
from collections import defaultdict
from flask import Flask, jsonify, request

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================
# ✅ إعدادات البروكسي
# ============================================
PROXY_URL = "http://iMpekNR2M85WzHa:Jefl2y2z9ccSN4T@51.194.225.55:41716"

PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL
}

PAGE_ACCESS_TOKEN = 'EAAfv9EZALaZA0BSEALmiFUs8IklZAyfXlEytByTs17xh1ZAOEcEnyYRBk6ZB2DQZCcfyTD9zDBHQ3fe4ZAECYoh20GNzTNbOUFEaztHWl59joPTJ4kbI0Q0lMhSTY0Apk1ZAHZCVAZCnRfzttp0rfDGVhBNoCcKR9R3ifc7D1B0XKlpRFDwjG9MWulAegC95x4qM4596wRrckZAwwZDZD'
PAGE_ID = None

# ============================================
# ✅ وضع الصيانة (كلمة سرية: Nactivity)
# ============================================
MAINTENANCE_MODE = False

def toggle_maintenance():
    global MAINTENANCE_MODE
    MAINTENANCE_MODE = not MAINTENANCE_MODE
    return MAINTENANCE_MODE

def get_page_id():
    global PAGE_ID
    try:
        r = requests.get(
            f"https://graph.facebook.com/v18.0/me?access_token={PAGE_ACCESS_TOKEN}",
            timeout=10,
            proxies={}
        )
        if r.status_code == 200:
            PAGE_ID = r.json().get('id')
            print(f"✅ PAGE_ID: {PAGE_ID}")
        else:
            print(f"⚠️ فشل جلب PAGE_ID: {r.status_code}")
            PAGE_ID = None
    except Exception as e:
        print(f"❌ فشل جلب PAGE_ID: {e}")
        PAGE_ID = None

CLIENT_ID      = "87pIExRhxBb3_wGsA5eSEfyATloa"
CLIENT_SECRET  = "uf82p68Bgisp8Yg1Uz8Pf6_v1XYa"
SCOPE_SMSOTP   = "smsotp"
SCOPE_DJEZZY   = "djezzyAppV2"
GRANT_TYPE     = "mobile"
BASE_URL       = "https://apim.djezzy.dz/mobile-api"
API_V1         = f"{BASE_URL}/api/v1"

HEADERS = {
    'User-Agent': "MobileApp/3.0.7",
    'Accept': "application/json",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/json",
    'accept-language': "fr",
}

# ✅ 13 عرض
PAID_OFFERS = [
    {'label': '🔖 عرض 70دج [4 جيقا] 24h',         'code': 'BTLINTSPEEDDAY2Go',       'type': 'shake',           'name': 'عرض 70دج 4Go',      'amount': '4GB',  'price': '70'},
    {'label': '🎁 عرض 100دج [2 جيقا] 24h',         'code': 'DOVINTSPEEDDAY1GoPRE',    'type': 'activate-product','name': 'عرض 100دج 2Go',     'amount': '2GB',  'price': '100'},
    {'label': '📦 عرض 300Mo بـ 30دج مدة 24h',      'code': 'DOVINTSPEEDDAY100MoPRE',  'type': 'activate-product','name': 'عرض 30دج 300Mo',    'amount': '300MB','price': '30'},
    {'label': '📦 عرض 600Mo بـ 50دج مدة 24h',      'code': 'DOVINTSPEEDDAY250MoPRE',  'type': 'activate-product','name': 'عرض 50دج 600Mo',    'amount': '600MB','price': '50'},
    {'label': '📶 عرض 4Go بـ 150دج مدة 7 أيام',    'code': 'DOVINTSPEEDWEEK2GoPRE',   'type': 'activate-product','name': 'عرض 150دج 4Go',     'amount': '4GB',  'price': '150'},
    {'label': '📶 عرض 10Go بـ 300دج مدة 7 أيام',   'code': 'DOVINTSPEEDWEEK3GoPRE',   'type': 'activate-product','name': 'عرض 300دج 10Go',    'amount': '10GB', 'price': '300'},
    {'label': '⚡ عرض 10Go بـ 190دج مدة 72h',      'code': 'BTL4GBDAY',               'type': 'shake',           'name': 'عرض 190دج 10Go',    'amount': '10GB', 'price': '190'},
    {'label': '📘 عرض 3Go بـ 70دج مدة 3 أيام FB',  'code': '1GBFB3DAY',               'type': 'shake',           'name': 'عرض 70دج 3Go FB',   'amount': '3GB',  'price': '70'},
    {'label': '🌙 عرض 12Go بـ 500دج مدة شهر',      'code': 'DOVINTSPEEDMONTH6GoPRE',  'type': 'activate-product','name': 'عرض 500دج 12Go',    'amount': '12GB', 'price': '500'},
    {'label': '🌙 عرض 30Go بـ 1000دج مدة شهر',     'code': 'DOVINTSPEEDMONTH15GoPRE', 'type': 'activate-product','name': 'عرض 1000دج 30Go',   'amount': '30GB', 'price': '1000'},
    {'label': '🌙 عرض 60Go بـ 1500دج مدة شهر',     'code': 'DOVINTSPEEDMONTH30GoPRE', 'type': 'activate-product','name': 'عرض 1500دج 60Go',   'amount': '60GB', 'price': '1500'},
    {'label': '🔥 عرض 100Go بـ 2000دج مدة 30 يوم',  'code': 'DOVINTSPEEDMONTH100GoPRE5G', 'type': 'activate-product','name': 'عرض 2000دج 100Go', 'amount': '100GB', 'price': '2000'},
    {'label': '👑 عرض 200Go بـ 4000دج مدة 30 يوم',  'code': 'DOVINTSPEEDMONTH220GoPRE5G', 'type': 'activate-product','name': 'عرض 4000دج 200Go', 'amount': '200GB', 'price': '4000'},
]

STATE_IDLE            = 0
STATE_WAITING_PHONE   = 1
STATE_WAITING_OTP     = 2
STATE_SELECTING_OFFER = 3
STATE_WAITING_INVITE  = 4
STATE_WAITING_MGM_OTP = 5
STATE_COOLDOWN        = 6
STATE_WAITING_MIGRATION = 7
STATE_WAITING_ANNOUNCEMENT = 8
STATE_WAITING_MGM_PHONE = 9

user_states           = {}
user_offer_data       = {}
pending_otp           = {}
processed_message_ids = set()
user_mgm_data         = {}
user_migration_data   = {}

# ✅ سجل التفعيلات للإحصائيات
activation_stats = {
    'total_users': set(),
    'walk_2go': 0,
    'paid_offers': defaultdict(int),
    'mgm': 0,
    'migrations': 0,
    'last_activations': {},
}

STATS_FILE = 'activation_stats.json'

def load_stats():
    global activation_stats
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                activation_stats['total_users'] = set(data.get('total_users', []))
                activation_stats['walk_2go'] = data.get('walk_2go', 0)
                activation_stats['paid_offers'] = defaultdict(int, data.get('paid_offers', {}))
                activation_stats['mgm'] = data.get('mgm', 0)
                activation_stats['migrations'] = data.get('migrations', 0)
                activation_stats['last_activations'] = data.get('last_activations', {})
    except Exception as e:
        print(f"خطأ تحميل الإحصائيات: {e}")

def save_stats():
    try:
        data = {
            'total_users': list(activation_stats['total_users']),
            'walk_2go': activation_stats['walk_2go'],
            'paid_offers': dict(activation_stats['paid_offers']),
            'mgm': activation_stats['mgm'],
            'migrations': activation_stats['migrations'],
            'last_activations': activation_stats['last_activations']
        }
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"خطأ حفظ الإحصائيات: {e}")

load_stats()

# ============================================
# ✅ نظام الانتظار المستقل لكل خدمة (12 دقيقة)
# ============================================
SERVICE_COOLDOWN_FILE = 'service_cooldown.json'
service_cooldowns = {}  # {user_id: {service_key: datetime}}

def load_service_cooldowns():
    global service_cooldowns
    try:
        if os.path.exists(SERVICE_COOLDOWN_FILE):
            with open(SERVICE_COOLDOWN_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                service_cooldowns = {}
                for user_id, services in data.items():
                    service_cooldowns[user_id] = {}
                    for service_key, dt_str in services.items():
                        service_cooldowns[user_id][service_key] = datetime.fromisoformat(dt_str)
                print(f"✅ تم تحميل {len(service_cooldowns)} سجل انتظار للخدمات")
    except Exception as e:
        print(f"خطأ تحميل service_cooldown: {e}")
        service_cooldowns = {}

def save_service_cooldowns():
    try:
        data = {}
        for user_id, services in service_cooldowns.items():
            data[user_id] = {}
            for service_key, dt in services.items():
                data[user_id][service_key] = dt.isoformat()
        with open(SERVICE_COOLDOWN_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"خطأ حفظ service_cooldown: {e}")

def get_service_key(service_type, offer_code=None):
    """إنشاء مفتاح فريد لكل خدمة"""
    if service_type == 'walk_2go':
        return 'walk_2go'
    elif service_type == 'paid_offer' and offer_code:
        return f'paid_{offer_code}'
    elif service_type == 'mgm':
        return 'mgm'
    elif service_type == 'migration':
        return 'migration'
    elif service_type == 'otp_resend':
        return 'otp_resend'
    return service_type

def check_service_cooldown(user_id, service_key):
    """التحقق من وجود انتظار لخدمة معينة"""
    user_id_str = str(user_id)
    if user_id_str in service_cooldowns:
        if service_key in service_cooldowns[user_id_str]:
            last_time = service_cooldowns[user_id_str][service_key]
            if datetime.now() - last_time < timedelta(minutes=12):
                remaining = int((timedelta(minutes=12) - (datetime.now() - last_time)).total_seconds())
                minutes = remaining // 60
                seconds = remaining % 60
                return {
                    'active': True,
                    'remaining': remaining,
                    'minutes': minutes,
                    'seconds': seconds,
                    'message': f"✅ تلقيت الرد بالفعل\nحاول مجددًا بعد {minutes} دقيقة و {seconds} ثانية 🕒"
                }
            else:
                # حذف الانتهاء
                del service_cooldowns[user_id_str][service_key]
                if not service_cooldowns[user_id_str]:
                    del service_cooldowns[user_id_str]
                save_service_cooldowns()
    return {'active': False}

def set_service_cooldown(user_id, service_key):
    """تسجيل وقت بدء انتظار خدمة معينة"""
    user_id_str = str(user_id)
    if user_id_str not in service_cooldowns:
        service_cooldowns[user_id_str] = {}
    service_cooldowns[user_id_str][service_key] = datetime.now()
    save_service_cooldowns()

def clear_service_cooldown(user_id, service_key=None):
    """مسح انتظار خدمة أو جميع الخدمات لمستخدم"""
    user_id_str = str(user_id)
    if user_id_str in service_cooldowns:
        if service_key:
            if service_key in service_cooldowns[user_id_str]:
                del service_cooldowns[user_id_str][service_key]
                if not service_cooldowns[user_id_str]:
                    del service_cooldowns[user_id_str]
        else:
            del service_cooldowns[user_id_str]
        save_service_cooldowns()

load_service_cooldowns()

# ============================================
# ✅ نظام الإجراءات المعلّقة
# ============================================
pending_actions = {}

def set_pending_action(sender_id, action_type, data=None):
    pending_actions[sender_id] = {'type': action_type, 'data': data or {}}

def clear_pending_action(sender_id):
    pending_actions.pop(sender_id, None)

def execute_pending_action_silent(sender_id):
    action = pending_actions.pop(sender_id, None)
    if not action:
        offers_keyboard(sender_id, "🎉 تم تجديد الجلسة!\n\n👇 اختر العرض:")
        return

    action_type = action['type']
    data        = action['data']
    token       = user_offer_data[sender_id]['token']
    msisdn      = user_offer_data[sender_id]['msisdn']

    if action_type == 'walk_2go':
        result = api_activate_walk_2go(token, msisdn, sender_id)
        if result.get('token_expired'):
            send_message(sender_id, "❌ فشل التجديد التلقائي\n📱 أرسل رقمك مجدداً")
            user_states[sender_id] = STATE_WAITING_PHONE
        else:
            offers_keyboard(sender_id, result['message'])

    elif action_type == 'paid_offer':
        offer  = data.get('offer')
        result = api_activate_paid_offer(token, msisdn, offer, sender_id)
        if result.get('token_expired'):
            send_message(sender_id, "❌ فشل التجديد التلقائي\n📱 أرسل رقمك مجدداً")
            user_states[sender_id] = STATE_WAITING_PHONE
        else:
            if result.get('success') == 'processing':
                return
            offers_keyboard(sender_id, result['message'])

    elif action_type == 'mgm_invite':
        receiver_phone = data.get('receiver_phone')
        threading.Thread(
            target=process_1go_free_interactive,
            args=(sender_id, receiver_phone),
            daemon=True
        ).start()

    elif action_type == 'info':
        info = format_sim_info(msisdn, token)
        if info == TOKEN_EXPIRED:
            send_message(sender_id, "❌ فشل التجديد التلقائي\n📱 أرسل رقمك مجدداً")
            user_states[sender_id] = STATE_WAITING_PHONE
        else:
            offers_keyboard(sender_id, info)

    elif action_type == 'migration':
        threading.Thread(target=handle_migration, args=(sender_id,), daemon=True).start()

    else:
        offers_keyboard(sender_id, "✅ تم تجديد الجلسة!\n\n👇 اختر العرض:")

TOKEN_EXPIRED = "__TOKEN_EXPIRED__"

def create_djezzy_session():
    s = requests.Session()
    s.timeout = 30
    s.proxies = PROXIES
    s.verify = False
    return s

djezzy_session = create_djezzy_session()
facebook_session = requests.Session()
facebook_session.timeout = 30
facebook_session.proxies = {}

# ============================================
# ✅ مؤشر الكتابة (Typing Indicator)
# ============================================
def send_typing_indicator(recipient_id):
    try:
        url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
        data = {
            "recipient": {"id": recipient_id},
            "sender_action": "typing_on"
        }
        r = facebook_session.post(url, json=data, timeout=5)
        return r.status_code == 200
    except Exception as e:
        print(f"Typing indicator error: {e}")
        return False

def send_typing_off(recipient_id):
    try:
        url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
        data = {
            "recipient": {"id": recipient_id},
            "sender_action": "typing_off"
        }
        r = facebook_session.post(url, json=data, timeout=5)
        return r.status_code == 200
    except Exception as e:
        print(f"Typing off error: {e}")
        return False

# ============================================
# ✅ قائمة المستخدمين للإعلانات
# ============================================
USERS_LIST_FILE = 'users_list.json'
ALL_USERS = set()

def load_users_list():
    global ALL_USERS
    try:
        if os.path.exists(USERS_LIST_FILE):
            with open(USERS_LIST_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                ALL_USERS = set(data)
                print(f"✅ تم تحميل {len(ALL_USERS)} مستخدم")
    except Exception as e:
        print(f"خطأ تحميل قائمة المستخدمين: {e}")

def save_users_list():
    try:
        with open(USERS_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(ALL_USERS), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"خطأ حفظ قائمة المستخدمين: {e}")

def add_user(user_id):
    global ALL_USERS
    user_id_str = str(user_id)
    if user_id_str not in ALL_USERS:
        ALL_USERS.add(user_id_str)
        save_users_list()
        print(f"✅ تم إضافة مستخدم جديد: {user_id_str}")

load_users_list()

# ============================================
# ✅ دالة تنظيف الأرقام (دعم جميع الصيغ)
# ============================================
def clean_phone_number(text):
    """تنظيف رقم الهاتف من جميع الفواصل والفراغات والرموز"""
    if not text:
        return None
    
    cleaned = re.sub(r'[^0-9]', '', str(text))
    
    if cleaned.startswith('213'):
        cleaned = '0' + cleaned[3:]
    
    if re.match(r'^0[567][0-9]{8}$', cleaned):
        return cleaned
    else:
        return None

# ============================================
# ✅ دالة إرسال إعلان للجميع
# ============================================
def send_announcement(sender_id):
    send_message(sender_id, 
        "📢 **إرسال إعلان للجميع**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📝 أرسل رسالة الإعلان (نص أو رابط):\n"
        "✅ مثال: مرحباً بكم في البوت الجديد\n"
        f"⏳ سيتم إرساله لـ {len(ALL_USERS)} مستخدم\n"
        "❌ اكتب 'إلغاء' للإلغاء"
    )
    
    user_states[sender_id] = STATE_WAITING_ANNOUNCEMENT

def send_announcement_to_all(sender_id, announcement_text):
    send_message(sender_id, f"📨 جاري إرسال الإعلان إلى {len(ALL_USERS)} مستخدم...")
    
    def send_to_all():
        success_count = 0
        fail_count = 0
        
        for user_id in ALL_USERS:
            try:
                if user_id == str(sender_id):
                    continue
                    
                success = send_message(user_id, 
                    f"📢 إعلان:\n━━━━━━━━━━━━━━━━━━━━━\n\n{announcement_text}\n\n━━━━━━━━━━━━━━━━━━━━━"
                )
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                time.sleep(0.1)
            except Exception as e:
                fail_count += 1
                print(f"❌ فشل إرسال للمستخدم {user_id}: {e}")
        
        send_message(sender_id, 
            f"✅ تم إرسال الإعلان!\n"
            f"📨 تم الإرسال إلى: {success_count} مستخدم\n"
            f"❌ فشل الإرسال إلى: {fail_count} مستخدم"
        )
        
        user_states[sender_id] = STATE_SELECTING_OFFER
        offers_keyboard(sender_id, "✅ تم الإرسال!\n\n👇 اختر العرض:")
    
    threading.Thread(target=send_to_all, daemon=True).start()

# ============================================
# ✅ دوال OTP (POST - يعيد المحاولة فقط عند 429 - 0.15s)
# ============================================

def send_otp_once(sender_id, user_id, phone):
    """إرسال OTP باستخدام POST (يعيد المحاولة فقط عند 429 - 0.15s)"""
    msisdn = "213" + phone[1:]
    pending_otp_set(user_id, phone)
    
    print(f"[OTP_SEND] بدء إرسال OTP إلى {phone}")
    
    attempt = 0
    while True:
        attempt += 1
        try:
            time.sleep(0.15)
            
            url = f"{BASE_URL}/oauth2/registration"
            params = {
                'msisdn': msisdn,
                'client_id': CLIENT_ID,
                'scope': SCOPE_SMSOTP
            }
            payload = json.dumps({
                "consent-agreement": [{"marketing-notifications": False}],
                "is-consent": True
            })
            headers = {
                'User-Agent': "MobileApp/3.0.7",
                'Accept': "application/json",
                'Accept-Encoding': "gzip",
                'Content-Type': "application/json",
                'accept-language': "fr"
            }
            
            r = djezzy_session.post(url, params=params, data=payload, headers=headers, timeout=15)
            print(f"[OTP_SEND] محاولة {attempt} - الكود: {r.status_code}")
            
            if r.status_code in [200, 201]:
                print(f"[OTP_SEND] ✅ تم إرسال OTP بنجاح إلى {phone} بعد {attempt} محاولات")
                pending_otp[user_id]['timestamp'] = datetime.now()
                _save_pending_otp_to_file(pending_otp)
                
                send_message(sender_id, 
                    f"📲 تم إرسال رمز التحقق إلى {phone}\n"
                    f"✉️ أرسل الرمز (6 أرقام)"
                )
                user_states[user_id] = STATE_WAITING_OTP
                return True
            
            elif r.status_code == 429:
                print(f"[OTP_SEND] 429 - إعادة المحاولة {attempt}")
                time.sleep(0.15)
                continue
            
            else:
                print(f"[OTP_SEND] خطأ {r.status_code} - إعادة المحاولة {attempt}")
                time.sleep(0.15)
                continue
                
        except Exception as e:
            print(f"[OTP_SEND] استثناء: {e} - إعادة المحاولة {attempt}")
            time.sleep(0.15)
            continue

def verify_otp_once(sender_id, phone, otp_code):
    """التحقق من OTP باستخدام POST (يعيد المحاولة فقط عند 429 - 0.15s)"""
    msisdn = "213" + phone[1:]
    
    print(f"[OTP_VERIFY] بدء التحقق من الرمز {otp_code} للرقم {phone}")
    send_message(sender_id, "⏳ جاري التحقق من الرمز...")
    
    attempt = 0
    while True:
        attempt += 1
        try:
            time.sleep(0.15)
            
            url = f"{BASE_URL}/oauth2/token"
            payload = (
                f"otp={otp_code}"
                f"&mobileNumber={msisdn}"
                f"&scope={SCOPE_DJEZZY}"
                f"&client_id={CLIENT_ID}"
                f"&client_secret={CLIENT_SECRET}"
                f"&grant_type={GRANT_TYPE}"
            )
            headers = {
                'User-Agent': "MobileApp/3.0.7",
                'Accept': "application/json",
                'Accept-Encoding': "gzip",
                'Content-Type': "application/x-www-form-urlencoded",
                'accept-language': "fr"
            }
            
            r = djezzy_session.post(url, data=payload, headers=headers, timeout=10)
            print(f"[OTP_VERIFY] محاولة {attempt} - الكود: {r.status_code}")
            
            if r.status_code == 200:
                token = r.json().get('access_token')
                
                user_offer_data[sender_id] = {'msisdn': msisdn, 'token': token}
                user_states[sender_id] = STATE_SELECTING_OFFER
                pending_otp_delete(sender_id)
                save_user_token_json(sender_id, msisdn, phone, token)
                
                print(f"[OTP_VERIFY] ✅ تم التحقق بنجاح بعد {attempt} محاولات")
                
                threading.Thread(
                    target=execute_pending_action_silent,
                    args=(sender_id,),
                    daemon=True
                ).start()
                return True
            
            elif r.status_code == 400:
                print(f"[OTP_VERIFY] 400 - رمز غير صحيح")
                pending_otp_delete(sender_id)
                user_states[sender_id] = STATE_WAITING_PHONE
                send_message(sender_id,
                    "❌ رمز التحقق غير صحيح.\n"
                    "📱 يرجى إرسال رقم هاتفك مرة أخرى للحصول على رمز تحقق جديد."
                )
                return False
            
            elif r.status_code == 429:
                print(f"[OTP_VERIFY] 429 - إعادة المحاولة {attempt}")
                time.sleep(0.15)
                continue
            
            else:
                print(f"[OTP_VERIFY] كود {r.status_code} - إعادة المحاولة {attempt}")
                time.sleep(0.15)
                continue
                
        except Exception as e:
            print(f"[OTP_VERIFY] خطأ: {e} - إعادة المحاولة {attempt}")
            time.sleep(0.15)
            continue

def send_otp_background(sender_id, user_id, phone):
    send_otp_once(sender_id, user_id, phone)

def start_otp_verification(sender_id, phone, otp_code):
    threading.Thread(
        target=verify_otp_once,
        args=(sender_id, phone, otp_code),
        daemon=True
    ).start()

def do_send_otp(sender_id, user_id, phone):
    threading.Thread(target=send_otp_background, args=(sender_id, user_id, phone), daemon=True).start()

def resend_otp(sender_id):
    if sender_id in pending_otp:
        # ✅ التحقق من انتظار خدمة OTP
        service_key = get_service_key('otp_resend')
        cooldown_check = check_service_cooldown(sender_id, service_key)
        if cooldown_check['active']:
            send_message(sender_id, cooldown_check['message'])
            return
        
        phone = pending_otp[sender_id]['phone']
        threading.Thread(target=send_otp_background, args=(sender_id, sender_id, phone), daemon=True).start()
        # ✅ تسجيل انتظار إعادة الإرسال
        set_service_cooldown(sender_id, service_key)
    else:
        send_message(sender_id, "❌ لا توجد جلسة OTP نشطة.\n📱 أرسل رقمك من جديد:")
        user_states[sender_id] = STATE_WAITING_PHONE

def handle_phone_resend(sender_id, phone):
    # ✅ التحقق من انتظار خدمة OTP
    service_key = get_service_key('otp_resend')
    cooldown_check = check_service_cooldown(sender_id, service_key)
    if cooldown_check['active']:
        send_message(sender_id, cooldown_check['message'])
        return
    
    pending_otp_delete(sender_id)
    threading.Thread(target=send_otp_background, args=(sender_id, sender_id, phone), daemon=True).start()
    set_service_cooldown(sender_id, service_key)

def login_or_send_otp(sender_id, phone):
    """
    ✅ الدالة الموحّدة لاستقبال رقم الهاتف في كل نقاط البوت:
    - إذا يوجد Token صالح محفوظ لهذا الرقم → تسجيل دخول تلقائي فوراً (بدون OTP)
      وإكمال أي عملية كانت معلّقة تلقائياً.
    - إذا لا يوجد Token صالح → إرسال OTP جديد مباشرة وانتظار إدخال الرمز.
    تُستخدم من STATE_WAITING_PHONE، وأيضاً بعد إعادة إرسال الرقم لأي خدمة
    (عروض جيزي / 2Go / معلوماتي / دعوة MGM / تحويل الشريحة / تغيير الرقم / انتهاء صلاحية الجلسة).
    """
    msisdn = "213" + phone[1:]
    _, _, saved_token = get_valid_token_json(sender_id, msisdn)

    if saved_token:
        user_offer_data[sender_id] = {'msisdn': msisdn, 'token': saved_token}
        user_states[sender_id]     = STATE_SELECTING_OFFER
        sub_type = get_subscription_type(saved_token, msisdn)
        sub_line = f"\n📦 العرض : {sub_type}" if sub_type else ""
        offers_keyboard(sender_id,
            f"🔓 تم تسجيل الدخول تلقائياً!\n\n"
            f"📱 الرقم : {mask_phone(phone)} ✅"
            f"{sub_line}\n\n"
            "✅ جلستك محفوظة - لا حاجة لـ OTP\n\n"
            "اختر العرض المناسب من الأزرار أدناه 🔽")
        # ✅ إكمال أي عملية كانت معلّقة تلقائياً بعد تسجيل الدخول
        if sender_id in pending_actions:
            threading.Thread(
                target=execute_pending_action_silent,
                args=(sender_id,),
                daemon=True
            ).start()
    else:
        handle_phone_resend(sender_id, phone)

# ============================================
# ✅ دوال MGM (POST - يعيد المحاولة فقط عند 429 - 0.15s)
# ============================================

def send_mgm_otp_once(sender_id, receiver_phone):
    """إرسال OTP للمدعو باستخدام POST (يعيد المحاولة فقط عند 429 - 0.15s)"""
    receiver_msisdn = "213" + receiver_phone[1:]
    
    print(f"[MGM_OTP] بدء إرسال OTP إلى {receiver_phone}")
    
    attempt = 0
    while True:
        attempt += 1
        try:
            time.sleep(0.15)
            
            url = f"{BASE_URL}/oauth2/registration"
            params = {
                'msisdn': receiver_msisdn,
                'client_id': CLIENT_ID,
                'scope': SCOPE_SMSOTP
            }
            payload = json.dumps({
                "consent-agreement": [{"marketing-notifications": False}],
                "is-consent": True
            })
            headers = {
                'User-Agent': "MobileApp/3.0.7",
                'Accept': "application/json",
                'Accept-Encoding': "gzip",
                'Content-Type': "application/json",
                'accept-language': "fr"
            }
            
            r = djezzy_session.post(url, params=params, data=payload, headers=headers, timeout=15)
            print(f"[MGM_OTP] محاولة {attempt} - الكود: {r.status_code}")
            
            if r.status_code in [200, 201]:
                print(f"[MGM_OTP] ✅ تم إرسال OTP بنجاح إلى {receiver_phone} بعد {attempt} محاولات")
                
                user_mgm_data[sender_id]['step'] = 'waiting_otp'
                user_mgm_data[sender_id]['timestamp'] = datetime.now()
                
                send_message(sender_id, 
                    f"📲 تم إرسال رمز التحقق إلى {receiver_phone}\n"
                    f"✉️ أرسل الرمز (6 أرقام):"
                )
                user_states[sender_id] = STATE_WAITING_MGM_OTP
                return True
            
            elif r.status_code == 429:
                print(f"[MGM_OTP] 429 - إعادة المحاولة {attempt}")
                time.sleep(0.15)
                continue
            
            else:
                print(f"[MGM_OTP] خطأ {r.status_code} - إعادة المحاولة {attempt}")
                time.sleep(0.15)
                continue
                
        except Exception as e:
            print(f"[MGM_OTP] خطأ: {e} - إعادة المحاولة {attempt}")
            time.sleep(0.15)
            continue

def verify_mgm_otp_once(sender_id, otp_code):
    """التحقق من OTP لـ MGM باستخدام POST (يعيد المحاولة فقط عند 429 - 0.15s)"""
    if sender_id not in user_mgm_data:
        send_message(sender_id, "❌ لا توجد جلسة نشطة")
        return False
    
    mgm_info = user_mgm_data[sender_id]
    receiver_msisdn = mgm_info['receiver_msisdn']
    access_token = user_offer_data[sender_id]['token']
    sender_msisdn = user_offer_data[sender_id]['msisdn']
    
    print(f"[MGM_VERIFY] بدء التحقق من الرمز {otp_code} للرقم {receiver_msisdn}")
    send_message(sender_id, "⏳ جاري التحقق من الرمز...")
    
    attempt = 0
    while True:
        attempt += 1
        try:
            time.sleep(0.15)
            
            url = f"{BASE_URL}/oauth2/token"
            payload = (
                f"otp={otp_code}"
                f"&mobileNumber={receiver_msisdn}"
                f"&scope={SCOPE_DJEZZY}"
                f"&client_id={CLIENT_ID}"
                f"&client_secret={CLIENT_SECRET}"
                f"&grant_type={GRANT_TYPE}"
            )
            headers = {
                'User-Agent': "MobileApp/3.0.7",
                'Accept': "application/json",
                'Accept-Encoding': "gzip",
                'Content-Type': "application/x-www-form-urlencoded",
                'accept-language': "fr"
            }
            
            r = djezzy_session.post(url, data=payload, headers=headers, timeout=10)
            print(f"[MGM_VERIFY] محاولة {attempt} - الكود: {r.status_code}")
            
            if r.status_code == 200:
                print(f"[MGM_VERIFY] ✅ تم التحقق من OTP بنجاح بعد {attempt} محاولات")
                
                send_message(sender_id, "✅ تم التحقق بنجاح! جاري تفعيل المكافأة...")
                
                r_rew, err_rew = api_activate_reward_mgm(access_token, sender_msisdn)
                
                if err_rew == 'expired':
                    send_message(sender_id, "❌ انتهت صلاحية الجلسة\n📱 أعد إرسال رقمك")
                    user_states[sender_id] = STATE_WAITING_PHONE
                    user_mgm_data.pop(sender_id, None)
                    return False
                
                if r_rew and r_rew.status_code in [200, 201]:
                    print(f"[MGM_VERIFY] ✅ تم تفعيل المكافأة بنجاح")
                    
                    activation_stats['mgm'] += 1
                    activation_stats['total_users'].add(str(sender_id))
                    update_cooldown(sender_id)
                    save_stats()
                    
                    offers_keyboard(sender_id,
                        f"🎉🥳 تم تفعيل 1Go مجاناً على حسابك! 💜\n"
                        f"لاتنسى متابعة صفحة ناكتيفي 💙📱"
                    )
                    user_mgm_data.pop(sender_id, None)
                    user_states[sender_id] = STATE_SELECTING_OFFER
                    return True
                else:
                    err_code = r_rew.status_code if r_rew else '?'
                    send_message(sender_id,
                        f"❌ فشل تفعيل المكافأة (كود: {err_code})\n"
                        f"📱 حاول مرة أخرى لاحقاً"
                    )
                    user_mgm_data.pop(sender_id, None)
                    user_states[sender_id] = STATE_SELECTING_OFFER
                    return False
            
            elif r.status_code == 400:
                print(f"[MGM_VERIFY] 400 - رمز غير صحيح")
                send_message(sender_id, "❌ رمز غير صحيح! أعد إدخال الرمز (6 أرقام):")
                return False
            
            elif r.status_code == 429:
                print(f"[MGM_VERIFY] 429 - إعادة المحاولة {attempt}")
                time.sleep(0.15)
                continue
            
            else:
                print(f"[MGM_VERIFY] كود {r.status_code} - إعادة المحاولة {attempt}")
                time.sleep(0.15)
                continue
                
        except Exception as e:
            print(f"[MGM_VERIFY] خطأ: {e} - إعادة المحاولة {attempt}")
            time.sleep(0.15)
            continue

def process_1go_free_interactive(sender_id, receiver_phone):
    """إرسال الدعوة فقط (بدون OTP)"""
    # ✅ التحقق من انتظار خدمة MGM
    service_key = get_service_key('mgm')
    cooldown_check = check_service_cooldown(sender_id, service_key)
    if cooldown_check['active']:
        offers_keyboard(sender_id, cooldown_check['message'])
        return
    
    sender_msisdn   = user_offer_data[sender_id]['msisdn']
    access_token    = user_offer_data[sender_id]['token']
    receiver_msisdn = "213" + receiver_phone[1:]

    send_message(sender_id, "🔄 جاري إرسال الدعوة...")

    r_inv, err_inv = api_send_invitation_mgm(access_token, sender_msisdn, receiver_msisdn)

    if err_inv == 'expired':
        handle_token_expired(sender_id, 'mgm_invite', {'receiver_phone': receiver_phone})
        return
    if err_inv:
        offers_keyboard(sender_id, _err_msg(err_inv))
        return

    print(f"[MGM_INVITE] status={r_inv.status_code}")

    if r_inv.status_code in [200, 201]:
        user_mgm_data[sender_id] = {
            'receiver_phone':  receiver_phone,
            'receiver_msisdn': receiver_msisdn,
            'timestamp':       datetime.now(),
            'step': 'waiting_activate'
        }
        
        # ✅ تسجيل انتظار الخدمة
        set_service_cooldown(sender_id, service_key)
        
        offers_keyboard(sender_id,
            f"✅ تم إرسال الدعوة بنجاح إلى {receiver_phone}!\n\n"
            f"📌 لتفعيل المكافأة اكتب كلمة: **تفعيل**\n"
            f"ثم أدخل رقم المدعو عندما يطلب منك."
        )

    elif r_inv.status_code == 400:
        try:
            res_json  = r_inv.json()
            err_msg_a = res_json.get('message', {}).get('ar', 'لقد وصلت إلى الحد الأقصى لعدد الدعوات (5).')
            offers_keyboard(sender_id, f"⚠️ {err_msg_a}")
        except:
            offers_keyboard(sender_id, "⚠️ لقد وصلت إلى الحد الأقصى لعدد الدعوات (5).")
    else:
        offers_keyboard(sender_id,
            f"❌ فشل الإرسال: هذا الرقم تم دعوته من قبل (كود: {r_inv.status_code})."
        )

    if r_inv.status_code in [200, 201]:
        activation_stats['mgm'] += 1
        activation_stats['total_users'].add(str(sender_id))
        update_cooldown(sender_id)
        save_stats()

def handle_mgm_activate(sender_id):
    """معالجة كلمة 'تفعيل' لتفعيل مكافأة الدعوة"""
    if sender_id not in user_mgm_data:
        send_message(sender_id, "❌ ليس لديك دعوة نشطة\n📱 أرسل دعوة أولاً باستخدام كلمة 'دعوة'")
        return
    
    mgm_info = user_mgm_data[sender_id]
    
    if datetime.now() - mgm_info['timestamp'] > timedelta(minutes=5):
        send_message(sender_id, "❌ انتهت صلاحية الدعوة (5 دقائق)\n📱 أرسل دعوة جديدة")
        user_mgm_data.pop(sender_id, None)
        return
    
    send_message(sender_id, 
        "📱 **تفعيل مكافأة الدعوة**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📝 أرسل رقم الذي قمت بدعوته (يبدأ بـ 07):\n"
        "✅ مثال: 0792123456\n\n"
        "❌ اكتب 'إلغاء' للإلغاء"
    )
    
    user_states[sender_id] = STATE_WAITING_MGM_PHONE

# ============================================
# ✅ إرسال الرسائل
# ============================================
def send_message(recipient_id, text):
    try:
        send_typing_indicator(recipient_id)
        time.sleep(0.1)
        
        url  = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
        data = {"recipient": {"id": recipient_id}, "message": {"text": text}}
        r    = facebook_session.post(url, json=data, timeout=10)
        
        send_typing_off(recipient_id)
        
        if r.status_code != 200:
            print(f"Send error {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"Send exception: {e}")
        return False

def send_quick_reply(recipient_id, text, buttons):
    try:
        send_typing_indicator(recipient_id)
        time.sleep(0.1)
        
        url  = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
        qr   = [{"content_type": "text", "title": b[:20], "payload": b} for b in buttons]
        data = {"recipient": {"id": recipient_id}, "message": {"text": text, "quick_replies": qr}}
        r    = facebook_session.post(url, json=data, timeout=10)
        
        send_typing_off(recipient_id)
        return r.status_code == 200
    except Exception as e:
        print(f"Quick reply error: {e}")
        return False

def offers_keyboard(recipient_id, text="👇 اختر العرض - Nactivi 🤖"):
    buttons = ["🎁 تفعيل 2G", "💰 عروض جيزي", "🎁 دعوة", "📱 معلوماتي", "🔄 تغيير الرقم", "📶 تحويل شريحة"]
    send_quick_reply(recipient_id, text, buttons)

def show_keywords_help(recipient_id):
    send_message(recipient_id,
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📌 الكلمات المفتاحية - بوت ناكتيفي\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔹 (2جيغا) أو (2G) → تفعيل 2Go مجاني 🎁\n"
        "🔹 (دعوة)         → إرسال دعوة جازي (MGM) 🎁\n"
        "🔹 (تفعيل)        → تفعيل مكافأة الدعوة 🎁\n"
        "🔹 (عروض)        → العروض المدفوعة (13 عرض) 💰\n"
        "🔹 (معلوماتي)    → الرصيد والباقات 📱\n"
        "🔹 (تغيير)       → تغيير الرقم 🔄\n"
        "🔹 (تحويل)       → تحويل نوع الشريحة 📶\n"
        "🔹 (👍) (sticker) → تسجيل رقم 📱\n"
        "🔹 (ناكتيفي)     → اسم البوت 🤖\n\n"
        "🔹 أثناء انتظار OTP:\n"
        "   • 1 → إعادة إرسال الرمز\n"
        "   • 2 → إلغاء العملية\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 يمكنك أيضاً استخدام الأزرار أدناه 👇"
    )

# ============================================
# ✅ دالة التحقق من الكولداون (5 دقائق)
# ============================================
def check_cooldown(sender_id):
    if sender_id in activation_stats['last_activations']:
        last_time = datetime.fromisoformat(activation_stats['last_activations'][sender_id])
        if datetime.now() - last_time < timedelta(minutes=5):
            remaining = int((timedelta(minutes=5) - (datetime.now() - last_time)).total_seconds())
            minutes = remaining // 60
            seconds = remaining % 60
            send_message(sender_id, 
                f"⏳ يرجى الانتظار {minutes} دقيقة و {seconds} ثانية\n"
                f"📌 قبل تفعيل خدمة أخرى."
            )
            return False
    return True

def update_cooldown(sender_id):
    activation_stats['last_activations'][sender_id] = datetime.now().isoformat()
    save_stats()

# ============================================
# ✅ دالة عرض الإحصائيات (مخفية)
# ============================================
def show_statistics(sender_id):
    total_users = len(activation_stats['total_users'])
    walk_2go_count = activation_stats['walk_2go']
    mgm_count = activation_stats['mgm']
    migrations_count = activation_stats.get('migrations', 0)
    paid_offers_count = sum(activation_stats['paid_offers'].values())
    
    stats_msg = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 إحصائيات البوت - Nactivi\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 عدد المستخدمين: {total_users}\n"
        f"📱 عدد التفعيلات الكلي: {walk_2go_count + mgm_count + paid_offers_count + migrations_count}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📈 تفاصيل التفعيلات:\n"
        f"🎁 2Go مجاني: {walk_2go_count}\n"
        f"🎁 دعوات MGM: {mgm_count}\n"
        f"💰 عروض مدفوعة: {paid_offers_count}\n"
        f"📶 تحويل شرائح: {migrations_count}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "💳 تفاصيل العروض المدفوعة:\n"
    )
    
    for offer_name, count in activation_stats['paid_offers'].items():
        if count > 0:
            stats_msg += f"  • {offer_name}: {count}\n"
    
    stats_msg += "\n━━━━━━━━━━━━━━━━━━━━━"
    
    send_message(sender_id, stats_msg)

# ============================================
# ✅ كشف انتهاء التوكن
# ============================================
_EXPIRED_KW = ['token','unauthorized','unauthenticated','invalid_token',
               'access denied','invalid token','jwt','expired',
               'authentication failed','token expired','invalid credentials']

def check_response_for_expired(r):
    if r is None: return False
    if r.status_code == 401:
        print("[TOKEN_CHECK] 401 → توكن منتهي"); return True
    try:
        tl = r.text.lower()
        for kw in _EXPIRED_KW:
            if kw in tl:
                print(f"[TOKEN_CHECK] '{kw}' → توكن منتهي"); return True
    except: pass
    return False

def handle_token_expired(sender_id, pending_action_type=None, pending_action_data=None):
    saved_phone, _ = get_saved_phone_for_user(sender_id)
    delete_user_token_json(sender_id)
    user_offer_data.pop(sender_id, None)

    if pending_action_type:
        set_pending_action(sender_id, pending_action_type, pending_action_data)

    if saved_phone:
        send_message(sender_id,
            "🔁 انتهت صلاحية الجلسة - جاري التجديد التلقائي...\n\n"
            f"📱 رقمك: {saved_phone}\n"
            "📲 سيصلك رمز تحقق SMS جديد الآن")
        threading.Thread(target=send_otp_background, args=(sender_id, sender_id, saved_phone), daemon=True).start()
    else:
        clear_pending_action(sender_id)
        send_message(sender_id, "⚠️ انتهت صلاحية الجلسة\n\n📱 أرسل رقم جيزي (يبدأ بـ 07):")
        user_states[sender_id] = STATE_WAITING_PHONE

# ============================================
# ✅ JSON - بيانات المستخدمين
# ============================================
USERS_DATA_FILE  = 'users_data.json'
PENDING_OTP_FILE = 'pending_otp.json'

def _load_users_data():
    try:
        if os.path.exists(USERS_DATA_FILE):
            with open(USERS_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"خطأ تحميل users_data: {e}")
    return {}

def _save_users_data(data):
    try:
        with open(USERS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"خطأ حفظ users_data: {e}")

def save_user_token_json(user_id, msisdn, phone, access_token):
    data = _load_users_data()
    data[str(user_id)] = {
        'msisdn': msisdn, 
        'phone': phone,
        'token': access_token, 
        'saved_time': datetime.now().isoformat(),
        'otp_saved': True,
        'otp_time': datetime.now().isoformat()
    }
    _save_users_data(data)
    activation_stats['total_users'].add(str(user_id))
    save_stats()

def get_valid_token_json(user_id, msisdn=None):
    """جلب التوكن مع حذف المنتهي تلقائياً"""
    data    = _load_users_data()
    uid_str = str(user_id)
    if uid_str in data:
        info = data[uid_str]
        # ✅ حذف التوكن المنتهي (أكثر من 30 يوم)
        if datetime.now() - datetime.fromisoformat(info['saved_time']) < timedelta(days=30):
            if msisdn is None or info.get('msisdn') == msisdn:
                return info.get('phone'), info.get('msisdn'), info.get('token')
        else:
            # حذف التوكن المنتهي
            del data[uid_str]
            _save_users_data(data)
            print(f"[TOKEN] تم حذف توكن منتهي للمستخدم {user_id}")
    return None, None, None

def get_saved_phone_for_user(user_id):
    data = _load_users_data()
    info = data.get(str(user_id), {})
    return info.get('phone'), info.get('msisdn')

def delete_user_token_json(user_id):
    data    = _load_users_data()
    uid_str = str(user_id)
    if uid_str in data:
        del data[uid_str]
        _save_users_data(data)

def _load_pending_otp_from_file():
    """تحميل OTP مع حذف المنتهية (أكثر من 5 دقائق)"""
    try:
        if os.path.exists(PENDING_OTP_FILE):
            with open(PENDING_OTP_FILE, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            result = {}
            now = datetime.now()
            for k, v in raw.items():
                try:
                    timestamp = datetime.fromisoformat(v['timestamp'])
                    if now - timestamp < timedelta(minutes=5):
                        result[int(k)] = {'phone': v['phone'], 'timestamp': timestamp}
                    else:
                        print(f"[OTP] تم حذف OTP منتهي للمستخدم {k}")
                except Exception as e:
                    print(f"[OTP] خطأ في تحميل OTP للمستخدم {k}: {e}")
            return result
    except Exception as e:
        print(f"خطأ تحميل pending_otp: {e}")
    return {}

def _save_pending_otp_to_file(d):
    """حفظ OTP مع تنظيف المنتهية"""
    now = datetime.now()
    cleaned = {}
    for user_id, data in d.items():
        if now - data['timestamp'] < timedelta(minutes=5):
            cleaned[user_id] = data
        else:
            print(f"[OTP] تم حذف OTP منتهي للمستخدم {user_id} أثناء الحفظ")
    
    try:
        raw = {str(k): {'phone': v['phone'], 'timestamp': v['timestamp'].isoformat()}
               for k, v in cleaned.items()}
        with open(PENDING_OTP_FILE, 'w', encoding='utf-8') as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"خطأ حفظ pending_otp: {e}")
    
    return cleaned

pending_otp = _load_pending_otp_from_file()

def pending_otp_set(user_id, phone):
    pending_otp[user_id] = {'phone': phone, 'timestamp': datetime.now()}
    _save_pending_otp_to_file(pending_otp)

def pending_otp_delete(user_id):
    if user_id in pending_otp:
        del pending_otp[user_id]
        _save_pending_otp_to_file(pending_otp)

# ============================================
# ✅ دوال API جيزي
# ============================================
def _api_call(func):
    try:
        r = func()
        if check_response_for_expired(r): return None, 'expired'
        return r, None
    except requests.exceptions.Timeout:         return None, 'timeout'
    except requests.exceptions.ConnectionError: return None, 'connection'
    except Exception as e:
        print(f"[API] Error: {e}");             return None, 'error'

def _err_msg(err):
    return {'timeout': '❌ انتهت مهلة الاتصال - حاول مرة أخرى',
            'connection': '❌ فشل الاتصال بالسيرفر',
            'error': '❌ خطأ في الاتصال'}.get(err, '❌ خطأ غير معروف')

def get_main_balance(access_token, msisdn):
    r, err = api_get_balance(access_token, msisdn)
    if err == 'expired':
        return None, 'expired'
    if err or not r or r.status_code != 200:
        return None, err
    balance = r.json().get('data', {}).get('mainBalance', 0)
    try:
        return float(balance), None
    except:
        return None, 'parse_error'

def msisdn_to_phone(msisdn):
    if msisdn.startswith("213"):
        return "0" + msisdn[3:]
    return msisdn

def mask_phone(phone):
    if len(phone) >= 6:
        return phone[:4] + 'xxxx' + phone[-2:]
    return phone

def get_subscription_type_from_response(r_bal):
    try:
        sub = r_bal.json()['data']['customerInformations']['subscriptionType']['name']
        return sub.get('ar') or sub.get('fr') or sub.get('en')
    except:
        return None

def get_subscription_type(access_token, msisdn):
    r, err = api_get_balance(access_token, msisdn)
    if err or not r or r.status_code != 200:
        return None
    return get_subscription_type_from_response(r)

# ============================================
# ✅ دالة 2Go أسبوعية (بدون عد تنازلي)
# ============================================
def api_activate_walk_2go(access_token, msisdn, user_id):
    """تفعيل 2Go - بدون عد تنازلي"""
    # ✅ التحقق من انتظار خدمة 2Go
    service_key = get_service_key('walk_2go')
    cooldown_check = check_service_cooldown(user_id, service_key)
    if cooldown_check['active']:
        return {'success': False, 'message': cooldown_check['message'], 'token_expired': False}
    
    if not check_cooldown(user_id):
        return {'success': False, 'message': '⏳ انتظر 5 دقائق', 'token_expired': False}

    phone_display = msisdn_to_phone(msisdn)

    send_message(user_id, "🔍 جاري تفعيل 2Go...")

    r, err = _api_call(lambda: djezzy_session.post(
        f"{BASE_URL}/api/v1/services/walk/activate-reward/{msisdn}",
        data=json.dumps({"packageCode": "GIFTWALKWIN2GO"}),
        headers={**HEADERS, 'authorization': f"Bearer {access_token}"},
        timeout=15
    ))

    if err == 'expired':
        return {'success': False, 'message': TOKEN_EXPIRED, 'token_expired': True}
    if err:
        return {'success': False, 'message': _err_msg(err), 'token_expired': False}

    print(f"[WALK] Status: {r.status_code} | Body: {r.text[:200]}")

    # ✅ نجاح التفعيل
    if r.status_code in [200, 201, 202]:
        activation_stats['walk_2go'] += 1
        activation_stats['total_users'].add(str(user_id))
        update_cooldown(user_id)
        save_stats()
        
        # ✅ تسجيل انتظار الخدمة
        set_service_cooldown(user_id, service_key)
        
        return {
            'success': True,
            'message': (
                f"📱 الرقم : {phone_display}\n\n"
                f"🔖 العرض : 2 جيغا 🎉\n"
                f"✅️ تم تفعيل 2Go أسبوعية بنجاح 🥳💜\n"
                f"لاتنسى متابعة قناة ناكتيفي 💙📱"
                f"\n\n⏳ يرجى الانتظار 5 دقائق قبل تفعيل خدمة أخرى"
            ),
            'token_expired': False
        }

    # ✅ استخراج رسالة السيرفر
    srv_msg = ""
    try:
        rj = r.json()
        msg = rj.get('message', {})
        if isinstance(msg, dict):
            srv_msg = msg.get('ar') or msg.get('fr') or str(msg)
        else:
            srv_msg = str(msg)
    except:
        srv_msg = f"كود: {r.status_code}"

    # ✅ حالة 403 فقط → نرسل قانون جازي
    if r.status_code == 403:
        # ✅ تسجيل انتظار الخدمة
        set_service_cooldown(user_id, service_key)
        
        return {
            'success': False,
            'message': (
                f"📱 الرقم : {phone_display}\n\n"
                f"🔖 العرض : 2 جيغا 🎉\n"
                f"📆 الحالة : غير متاح ❌\n\n"
                f"ℹ️ {srv_msg}\n\n"
                f"لإستفادة من 2 جيغا اسبوعية يجب عليك تطبيق قانون(ج):\n"
                f"تشحن 100DA كل شهر وتفعل عرض مدفوع \"2Go ب 100DA\" لإستفادة من 2Go كل اسبوع لمدة 4 أسابيع وتعيد نفس طريقة تشحن... 📲"
            ),
            'token_expired': False
        }

    # ✅ حالات 402, 404, 405, 409 → "لم يكتمل الأسبوع" بدون قانون جازي
    if r.status_code in [402, 404, 405, 409]:
        # ✅ تسجيل انتظار الخدمة
        set_service_cooldown(user_id, service_key)
        
        return {
            'success': False,
            'message': (
                f"📱 الرقم : {phone_display}\n\n"
                f"🔖 العرض : 2 جيغا 🎉\n"
                f"📆 الحالة : لم يكتمل الأسبوع ❌\n\n"
                f"ℹ️ {srv_msg}"
            ),
            'token_expired': False
        }

    # ✅ أي خطأ آخر
    return {
        'success': False,
        'message': (
            f"📱 الرقم : {phone_display}\n\n"
            f"🔖 العرض : 2 جيغا 🎉\n"
            f"❌ حدث خطأ: {srv_msg if srv_msg else 'غير معروف'}"
        ),
        'token_expired': False
    }

# ============================================
# ✅ دوال تفعيل العروض المدفوعة (المعدلة - إعادة محاولة لكل الأخطاء)
# ============================================

def activate_shake_offer_background(access_token, msisdn, offer, user_id):
    """
    تفعيل عرض SHAKE - إعادة محاولة لكل الأخطاء حتى النجاح
    GET يحاول بدون حدود حتى ينجح، ثم POST يحاول بدون حدود حتى ينجح
    """
    pkg_code = offer['code']
    name = offer['name']
    price = int(offer['price'])
    
    # ✅ التحقق من انتظار هذه الخدمة المحددة
    service_key = get_service_key('paid_offer', pkg_code)
    cooldown_check = check_service_cooldown(user_id, service_key)
    if cooldown_check['active']:
        send_message(user_id, cooldown_check['message'])
        return
    
    shake_url = f"{BASE_URL}/api/v1/services/shake/{msisdn}"
    
    print(f"[SHAKE] بدء تفعيل {name}")
    
    hdrs = {
        'User-Agent': "MobileApp/3.0.7",
        'Accept': "application/json",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json",
        'accept-language': "fr",
        'authorization': f"Bearer {access_token}"
    }

    # 🚀 إرسال رسالة "جاري التفعيل" للمستخدم (مرة واحدة فقط)
    send_message(user_id, f"⏳ جاري تفعيل {name}...")

    # 🔄 GET يحاول بدون حدود حتى ينجح (كل الأخطاء تعيد المحاولة)
    offer_found = False
    attempt_get = 0
    
    while not offer_found:
        attempt_get += 1
        try:
            print(f"[SHAKE_GET] محاولة {attempt_get}...")
            r_get = djezzy_session.get(shake_url, headers=hdrs, timeout=15)
            
            # ✅ إذا انتهت صلاحية التوكن
            if check_response_for_expired(r_get):
                send_message(user_id, "❌ انتهت صلاحية الجلسة\n📱 أعد إرسال رقمك")
                return
            
            # ✅ إذا نجح الطلب
            if r_get.status_code == 200:
                try:
                    rj = r_get.json()
                    if rj.get("data", {}).get("code") == pkg_code:
                        offer_found = True
                        print(f"[SHAKE_GET] ✅ العرض موجود بعد {attempt_get} محاولات")
                        break
                except Exception as e:
                    print(f"[SHAKE_GET] خطأ في قراءة JSON: {e}")
                    time.sleep(0.15)
                    continue
            
            # ✅ أي كود آخر (429، 404، 500، 403، إلخ) - نعيد المحاولة
            else:
                print(f"[SHAKE_GET] كود {r_get.status_code} - إعادة المحاولة {attempt_get}")
                time.sleep(0.15)
                continue
                
        except Exception as e:
            print(f"[SHAKE_GET] Exception في المحاولة {attempt_get}: {e}")
            time.sleep(0.15)
            continue

    # ✅ بعد نجاح GET، ننفذ POST (يحاول بدون حدود حتى ينجح)
    print(f"[SHAKE] ✅ GET نجح، نبدأ POST...")
    
    attempt_post = 0
    while True:
        attempt_post += 1
        try:
            time.sleep(0.15)
            
            print(f"[SHAKE_POST] محاولة {attempt_post}...")
            r = djezzy_session.post(
                shake_url, 
                data=json.dumps({"packageCode": pkg_code}), 
                headers=hdrs, 
                timeout=15
            )
            print(f"[SHAKE_POST] Status: {r.status_code}")
            
            # ✅ إذا انتهت صلاحية التوكن
            if check_response_for_expired(r):
                send_message(user_id, "❌ انتهت صلاحية الجلسة\n📱 أعد إرسال رقمك")
                return

            # ✅ نجاح POST
            if r.status_code in [200, 201, 202]:
                print(f"[SHAKE_POST] ✅ تم تفعيل {name} بنجاح بعد {attempt_post} محاولات")
                
                activation_stats['paid_offers'][name] += 1
                activation_stats['total_users'].add(str(user_id))
                update_cooldown(user_id)
                save_stats()
                
                # ✅ تسجيل انتظار الخدمة
                set_service_cooldown(user_id, service_key)
                
                send_message(user_id,
                    f"✅️ تم تفعيل {name} بنجاح 🥳💜\n"
                    f"لاتنسى متابعة صفحة ناكتيفي 💙📱"
                    f"\n\n⏳ يرجى الانتظار 5 دقائق قبل تفعيل خدمة أخرى"
                )
                return
            
            # ❌ رصيد غير كافي - نوقف (السبب الوحيد للتوقف)
            elif r.status_code == 402:
                # ✅ تسجيل انتظار الخدمة
                set_service_cooldown(user_id, service_key)
                
                send_message(user_id,
                    f"❌ رصيدك غير كافي لتفعيل {name}\n"
                    f"📝 المطلوب: {price} دج على الأقل"
                )
                return
            
            # ✅ أي كود آخر (429، 404، 500، 403، 405، إلخ) - نعيد المحاولة
            else:
                print(f"[SHAKE_POST] فشل (كود {r.status_code}) - إعادة المحاولة {attempt_post}")
                time.sleep(0.15)
                continue
                
        except Exception as e:
            print(f"[SHAKE_POST] استثناء: {e} - إعادة المحاولة {attempt_post}")
            time.sleep(0.15)
            continue

def activate_product_background(access_token, msisdn, offer, user_id):
    """
    تفعيل عرض activate-product - POST يحاول بدون حدود حتى ينجح
    كل الأخطاء تعيد المحاولة (ما عدا 402 = رصيد غير كافي)
    """
    pkg_code = offer['code']
    name = offer['name']
    price = int(offer['price'])
    
    # ✅ التحقق من انتظار هذه الخدمة المحددة
    service_key = get_service_key('paid_offer', pkg_code)
    cooldown_check = check_service_cooldown(user_id, service_key)
    if cooldown_check['active']:
        send_message(user_id, cooldown_check['message'])
        return
    
    print(f"[ACTIVATE_PRODUCT] بدء تفعيل {name}")
    
    # 🚀 إرسال رسالة "جاري التفعيل" للمستخدم (مرة واحدة فقط)
    send_message(user_id, f"⏳ جاري تفعيل {name}...")
    
    attempt = 0
    while True:
        attempt += 1
        try:
            time.sleep(0.15)
            
            hdrs = {
                'User-Agent': "MobileApp/3.0.7",
                'Accept': "application/json",
                'Accept-Encoding': "gzip",
                'Content-Type': "application/json",
                'accept-language': "fr",
                'authorization': f"Bearer {access_token}"
            }

            url = f"{BASE_URL}/api/v1/subscribers/activate-product/{msisdn}"
            body = json.dumps({"packageCode": pkg_code})

            print(f"[ACTIVATE_PRODUCT] POST محاولة {attempt}...")
            r = djezzy_session.post(url, data=body, headers=hdrs, timeout=15)
            print(f"[ACTIVATE_PRODUCT] Status: {r.status_code}")
            
            # ✅ إذا انتهت صلاحية التوكن
            if check_response_for_expired(r):
                send_message(user_id, "❌ انتهت صلاحية الجلسة\n📱 أعد إرسال رقمك")
                return
            
            # ✅ نجاح POST
            if r.status_code in [200, 201, 202]:
                print(f"[ACTIVATE_PRODUCT] ✅ تم تفعيل {name} بنجاح بعد {attempt} محاولات")
                
                activation_stats['paid_offers'][name] += 1
                activation_stats['total_users'].add(str(user_id))
                update_cooldown(user_id)
                save_stats()
                
                # ✅ تسجيل انتظار الخدمة
                set_service_cooldown(user_id, service_key)
                
                send_message(user_id,
                    f"✅️ تم تفعيل {name} بنجاح 🥳💜\n"
                    f"لاتنسى متابعة صفحة ناكتيفي 💙📱"
                    f"\n\n⏳ يرجى الانتظار 5 دقائق قبل تفعيل خدمة أخرى"
                )
                return
            
            # ❌ رصيد غير كافي - نوقف (السبب الوحيد للتوقف)
            elif r.status_code == 402:
                # ✅ تسجيل انتظار الخدمة
                set_service_cooldown(user_id, service_key)
                
                send_message(user_id,
                    f"❌ رصيدك غير كافي لتفعيل {name}\n"
                    f"📝 المطلوب: {price} دج على الأقل"
                )
                return
            
            # ✅ أي كود آخر (429، 404، 500، 403، 405، إلخ) - نعيد المحاولة
            else:
                print(f"[ACTIVATE_PRODUCT] فشل (كود {r.status_code}) - إعادة المحاولة {attempt}")
                time.sleep(0.15)
                continue
                
        except Exception as e:
            print(f"[ACTIVATE_PRODUCT] استثناء: {e} - إعادة المحاولة {attempt}")
            time.sleep(0.15)
            continue

def api_activate_paid_offer(access_token, msisdn, offer, user_id):
    """تفعيل العروض المدفوعة"""
    # ✅ التحقق من انتظار هذه الخدمة المحددة
    service_key = get_service_key('paid_offer', offer['code'])
    cooldown_check = check_service_cooldown(user_id, service_key)
    if cooldown_check['active']:
        return {'success': False, 'message': cooldown_check['message'], 'token_expired': False}
    
    if not check_cooldown(user_id):
        return {'success': False, 'message': '⏳ انتظر 5 دقائق', 'token_expired': False}

    price = int(offer['price'])
    name = offer['name']
    offer_type = offer.get('type', 'activate-product')

    # ✅ التحقق من الرصيد
    balance, bal_err = get_main_balance(access_token, msisdn)
    if bal_err == 'expired':
        return {'success': False, 'message': TOKEN_EXPIRED, 'token_expired': True}
    if balance is not None and balance < price:
        return {
            'success': False,
            'message': (
                f"❌ رصيدك غير كافي لتفعيل {name}\n"
                f"💰 رصيدك الحالي: {balance} دج\n"
                f"📝 المطلوب: {price} دج على الأقل"
            ),
            'token_expired': False
        }

    # ✅ تشغيل التفعيل في الخلفية
    if offer_type == 'shake':
        threading.Thread(
            target=activate_shake_offer_background,
            args=(access_token, msisdn, offer, user_id),
            daemon=True
        ).start()
        
        return {
            'success': 'processing',
            'message': f"⏳ جاري تفعيل {name} في الخلفية...",
            'token_expired': False
        }

    elif offer_type == 'activate-product':
        threading.Thread(
            target=activate_product_background,
            args=(access_token, msisdn, offer, user_id),
            daemon=True
        ).start()
        
        return {
            'success': 'processing',
            'message': f"⏳ جاري تفعيل {name} في الخلفية...",
            'token_expired': False
        }

    return {'success': False, 'message': '❌ نوع عرض غير معروف', 'token_expired': False}

def api_get_balance(access_token, msisdn):
    return _api_call(lambda: djezzy_session.get(
        f"{API_V1}/subscribers/main-balance/{msisdn}",
        headers={"authorization": f"Bearer {access_token}"}, timeout=15
    ))

def api_get_connected_products(access_token, msisdn):
    return _api_call(lambda: djezzy_session.get(
        f"{API_V1}/subscribers/connected-products-balances/{msisdn}",
        headers={**HEADERS, 'authorization': f"Bearer {access_token}"}, timeout=15
    ))

def format_sim_info(msisdn, access_token):
    phone_masked = mask_phone(msisdn_to_phone(msisdn))
    lines = [f"📱 معلومات الرقم: {phone_masked}"]
    r_bal, err_bal = api_get_balance(access_token, msisdn)
    if err_bal == 'expired': return TOKEN_EXPIRED
    if err_bal:              lines.append(f"💰 الرصيد: {_err_msg(err_bal)}")
    elif r_bal and r_bal.status_code == 200:
        bal_data = r_bal.json().get('data', {})
        lines.append(f"💰 الرصيد الرئيسي: {bal_data.get('mainBalance','غير معروف')} دج")
        sub_type = get_subscription_type_from_response(r_bal)
        if sub_type:
            lines.append(f"📦 العرض: {sub_type}")
    else: lines.append("💰 الرصيد: ⚠️ غير متاح")

    r_prod, err_prod = api_get_connected_products(access_token, msisdn)
    if err_prod == 'expired': return TOKEN_EXPIRED
    if err_prod:              lines.append(f"📦 الباقات: {_err_msg(err_prod)}")
    elif r_prod and r_prod.status_code == 200:
        products = r_prod.json().get('data', {}).get('products', [])
        if products:
            lines.append("📦 الباقات النشطة:")
            for prod in products:
                name   = prod.get('commercialName', {}).get('ar', 'باقة')
                expiry = prod.get('expiryAt', 'غير محدد')
                for bal in prod.get('balances', []):
                    unit = bal.get('usageUnit', 'MB')
                    rem  = bal.get('remaining', 0)
                    disp = f"{rem/1024:.2f} GB" if unit == 'MB' and rem > 1024 else f"{rem} {unit}"
                    lines.append(f"   • {name}: {disp} (ينتهي {expiry})")
        else:
            lines.append("📦 لا توجد باقات نشطة.")
    else: lines.append("📦 الباقات: ⚠️ غير متاحة")
    return "\n".join(lines)

# ============================================
# MGM API
# ============================================
def api_send_invitation_mgm(token, sender, receiver):
    url     = f"{API_V1}/services/mgm/send-invitation/{sender}"
    payload = json.dumps({"msisdnReciever": int(receiver)})
    hdrs    = {**HEADERS, 'authorization': f"Bearer {token}"}
    return _api_call(lambda: djezzy_session.post(url, data=payload, headers=hdrs, timeout=15))

def api_activate_reward_mgm(token, sender):
    url     = f"{API_V1}/services/mgm/activate-reward/{sender}"
    payload = json.dumps({"packageCode": "MGMBONUS1Go"})
    hdrs    = {**HEADERS, 'authorization': f"Bearer {token}"}
    return _api_call(lambda: djezzy_session.post(url, data=payload, headers=hdrs, timeout=15))

# ============================================
# ✅ تحويل نوع الشريحة (Migration)
# ============================================

def api_get_migration_options(access_token, msisdn):
    url = f"{BASE_URL}/api/v1/customer-care/migrations/{msisdn}"
    params = {'application': 'MOBILEAPP'}
    hdrs = {
        'User-Agent': "MobileApp/3.0.7",
        'Accept': "application/json",
        'Accept-Encoding': "gzip",
        'accept-language': "fr",
        'authorization': f"Bearer {access_token}"
    }
    return _api_call(lambda: djezzy_session.get(url, params=params, headers=hdrs, timeout=15))

def api_execute_migration(access_token, msisdn, migration_id):
    url = f"{BASE_URL}/api/v1/customer-care/migrates/{msisdn}"
    payload = json.dumps({"migrationConfigurationId": migration_id})
    hdrs = {
        'User-Agent': "MobileApp/3.0.7",
        'Accept': "application/json",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json",
        'accept-language': "fr",
        'authorization': f"Bearer {access_token}"
    }
    return _api_call(lambda: djezzy_session.post(url, data=payload, headers=hdrs, timeout=15))

def handle_migration(sender_id):
    # ✅ التحقق من انتظار خدمة التحويل
    service_key = get_service_key('migration')
    cooldown_check = check_service_cooldown(sender_id, service_key)
    if cooldown_check['active']:
        send_message(sender_id, cooldown_check['message'])
        user_states[sender_id] = STATE_SELECTING_OFFER
        return
    
    if sender_id not in user_offer_data:
        send_message(sender_id, "❌ ليس لديك جلسة نشطة\n📱 أرسل رقم جيزي (يبدأ بـ 07):")
        user_states[sender_id] = STATE_WAITING_PHONE
        return
    
    access_token = user_offer_data[sender_id]['token']
    msisdn = user_offer_data[sender_id]['msisdn']
    
    send_message(sender_id, "🔄 جاري جلب خيارات التحويل...")
    
    r, err = api_get_migration_options(access_token, msisdn)
    
    if err == 'expired':
        handle_token_expired(sender_id, 'migration')
        return
    if err:
        send_message(sender_id, f"❌ فشل جلب الخيارات: {_err_msg(err)}")
        return
    
    if r.status_code != 200:
        send_message(sender_id, f"❌ خطأ: الكود {r.status_code}")
        return
    
    try:
        data = r.json().get('data', [])
        if not data:
            send_message(sender_id, "❌ لا توجد خيارات تحويل متاحة")
            return
        
        msg = "📶 خيارات تحويل الشريحة:\n\n"
        options = []
        
        for i, item in enumerate(data, 1):
            from_name = item.get('subscriptionTypeFrom', {}).get('name', {}).get('ar', 'حالي')
            to_name = item.get('subscriptionTypeTo', {}).get('name', {}).get('ar', 'جديد')
            desc = item.get('description', {}).get('ar', '')
            
            msg += f"{i}️⃣ من {from_name} → إلى {to_name}\n"
            if desc:
                msg += f"   📝 {desc[:100]}...\n"
            msg += "\n"
            
            options.append({
                'id': item.get('id'),
                'from': from_name,
                'to': to_name,
                'index': i
            })
        
        msg += "👇 أرسل رقم الخيار (1، 2، 3...):"
        
        user_migration_data[sender_id] = {
            'options': options,
            'timestamp': datetime.now()
        }
        user_states[sender_id] = STATE_WAITING_MIGRATION
        
        send_message(sender_id, msg)
        
    except Exception as e:
        send_message(sender_id, f"❌ خطأ في قراءة البيانات: {e}")

def execute_migration(sender_id, choice_index):
    if sender_id not in user_migration_data:
        send_message(sender_id, "❌ انتهت الجلسة\n📱 حاول مرة أخرى")
        user_states[sender_id] = STATE_SELECTING_OFFER
        return
    
    migration_info = user_migration_data[sender_id]
    
    if datetime.now() - migration_info['timestamp'] > timedelta(minutes=5):
        send_message(sender_id, "❌ انتهت صلاحية الخيارات (5 دقائق)\n📱 حاول مرة أخرى")
        user_states[sender_id] = STATE_SELECTING_OFFER
        user_migration_data.pop(sender_id, None)
        return
    
    try:
        choice_idx = int(choice_index) - 1
        if choice_idx < 0 or choice_idx >= len(migration_info['options']):
            send_message(sender_id, "❌ رقم خيار غير صحيح\n📱 أرسل رقم صحيح:")
            return
        
        selected = migration_info['options'][choice_idx]
        migration_id = selected['id']
        to_name = selected['to']
        
        access_token = user_offer_data[sender_id]['token']
        msisdn = user_offer_data[sender_id]['msisdn']
        
        send_message(sender_id, f"🔄 جاري تحويل شريحتك إلى {to_name}...")
        
        r, err = api_execute_migration(access_token, msisdn, migration_id)
        
        if err == 'expired':
            handle_token_expired(sender_id, 'migration')
            return
        if err:
            send_message(sender_id, f"❌ فشل التحويل: {_err_msg(err)}")
            user_states[sender_id] = STATE_SELECTING_OFFER
            user_migration_data.pop(sender_id, None)
            return
        
        if r.status_code in [200, 201]:
            try:
                msg_data = r.json().get('message', {})
                success_msg = msg_data.get('ar', 'تمت عملية التحول بنجاح')
            except:
                success_msg = 'تمت عملية التحول بنجاح'
            
            activation_stats['migrations'] = activation_stats.get('migrations', 0) + 1
            activation_stats['total_users'].add(str(sender_id))
            save_stats()
            
            # ✅ تسجيل انتظار الخدمة
            service_key = get_service_key('migration')
            set_service_cooldown(sender_id, service_key)
            
            send_message(sender_id,
                f"✅ لقد تم تحويل عرضك إلى {to_name} بنجاح 🥳💜\n"
                f"⏳ قد يستغرق الأمر بضع وقت 💭\n\n"
                f"لاتنسى متابعة صفحة ناكتيفي 💙📱"
            )
        else:
            # ✅ تسجيل انتظار الخدمة حتى في الفشل
            service_key = get_service_key('migration')
            set_service_cooldown(sender_id, service_key)
            
            send_message(sender_id, f"❌ فشل التحويل (كود: {r.status_code})")
        
        user_states[sender_id] = STATE_SELECTING_OFFER
        user_migration_data.pop(sender_id, None)
        
    except Exception as e:
        send_message(sender_id, f"❌ حدث خطأ: {e}")
        user_states[sender_id] = STATE_SELECTING_OFFER
        user_migration_data.pop(sender_id, None)

# ============================================
# ✅ معالجة الرسائل
# ============================================
def handle_message(sender_id, text):
    try:
        _handle_message_inner(sender_id, text)
    except Exception as e:
        print(f"❌ خطأ في معالجة الرسالة: {e}")

def _handle_message_inner(sender_id, text):
    print(f"[MSG] {sender_id}: {text}")
    
    # ✅ كلمة سرية جديدة لإيقاف البوت
    if text.strip() == "Nactivity":
        is_maintenance = toggle_maintenance()
        status_msg = "🛑 بوت في وضع صيانة حالياً 🧑‍🔧" if is_maintenance else "✅ البوت يعمل بشكل طبيعي"
        send_message(sender_id, status_msg)
        print(f"[MAINTENANCE] تم تغيير وضع الصيانة إلى: {is_maintenance}")
        return
    
    # ✅ التحقق من وضع الصيانة
    if MAINTENANCE_MODE:
        send_message(sender_id, "🛑 بوت في وضع صيانة حالياً 🧑‍🔧\n⏳ يرجى المحاولة لاحقاً")
        return
    
    add_user(sender_id)

    if text.strip() == "تفعيل":
        handle_mgm_activate(sender_id)
        return

    if user_states.get(sender_id) == STATE_WAITING_ANNOUNCEMENT:
        if text in ["إلغاء", "الغاء", "❌ إلغاء"]:
            user_states[sender_id] = STATE_SELECTING_OFFER
            offers_keyboard(sender_id, "❌ تم إلغاء الإعلان.\n\n👇 اختر العرض:")
            return
        
        send_announcement_to_all(sender_id, text)
        return

    if text == "احصائيات":
        show_statistics(sender_id)
        return

    if text == "🔙 رجوع":
        if sender_id in user_offer_data:
            offers_keyboard(sender_id, "🔙 تم الرجوع للقائمة الرئيسية:\n\n👇 اختر العرض:")
            user_states[sender_id] = STATE_SELECTING_OFFER
        else:
            send_message(sender_id, "📱 أهلاً بك في بوت ناكتيفي!\nأرسل رقم جيزي (يبدأ بـ 07):")
            user_states[sender_id] = STATE_WAITING_PHONE
        return

    if text == "❌ إلغاء":
        user_states[sender_id] = STATE_SELECTING_OFFER
        pending_otp_delete(sender_id)
        user_mgm_data.pop(sender_id, None)
        user_migration_data.pop(sender_id, None)
        clear_pending_action(sender_id)
        if sender_id in user_offer_data:
            offers_keyboard(sender_id, "❌ تم إلغاء العملية.\n\n👇 اختر العرض:")
        else:
            send_message(sender_id, "❌ تم الإلغاء.\n📱 أرسل رقم جيزي (يبدأ بـ 07):")
            user_states[sender_id] = STATE_WAITING_PHONE
        return

    if text == "🔄 إعادة إرسال الرمز":
        if user_states.get(sender_id) == STATE_WAITING_OTP:
            resend_otp(sender_id)
        else:
            send_message(sender_id, "❌ لا توجد عملية انتظار رمز حالياً.")
        return

    if text in ["👍", "\U0001F44D"]:
        user_states[sender_id] = STATE_WAITING_PHONE
        user_offer_data.pop(sender_id, None)
        send_message(sender_id, "📱 أهلاً بك في بوت ناكتيفي! 🤖\n\nأرسل رقم جيزي (يبدأ بـ 07):\n✅ مثال: 0792123456")
        return

    if text.lower() in ['ناكتيفي', 'nactivi', 'البوت', 'bot']:
        send_message(sender_id, "🤖 مرحباً! أنا بوت ناكتيفي\nاختصاصي تفعيل عروض جيزي 🎁\n\n📌 اكتب (مساعدة) لمعرفة الكلمات المفتاحية")
        return

    if text.lower() in ['مساعدة', 'help', 'كلمات', 'الكلمات']:
        show_keywords_help(sender_id)
        return

    if sender_id not in user_states:
        user_states[sender_id] = STATE_IDLE
    state = user_states[sender_id]

    if text.lower() in ['/start', 'بدء', 'start', 'مرحبا', 'سلام', 'هلو', 'hello']:
        send_message(sender_id,
            "🌟 مرحباً بك في بوت ناكتيفي! 🤖\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🔹 (2جيغا) → 2Go مجاني 🎁\n"
            "🔹 (دعوة)  → إرسال دعوة جازي (MGM) 🎁\n"
            "🔹 (تفعيل) → تفعيل مكافأة الدعوة 🎁\n"
            "🔹 (عروض)  → 13 عرض مدفوع 💰\n"
            "🔹 (معلوماتي) → الرصيد 📱\n"
            "🔹 (تغيير) → تغيير الرقم 🔄\n"
            "🔹 (تحويل) → تحويل نوع الشريحة 📶\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📱 أرسل رقم جيزي (يبدأ بـ 07):")
        user_states[sender_id] = STATE_WAITING_PHONE
        return

    if text in ["🔄 تغيير الرقم", "تغيير"] or 'تغيير' in text:
        user_states[sender_id] = STATE_WAITING_PHONE
        user_offer_data.pop(sender_id, None)
        user_mgm_data.pop(sender_id, None)
        user_migration_data.pop(sender_id, None)
        pending_otp_delete(sender_id)
        clear_pending_action(sender_id)
        send_message(sender_id, "📱 أرسل الرقم الجديد (يبدأ بـ 07):")
        return

    if text in ["📱 معلوماتي", "معلوماتي"] or 'رصيد' in text or 'معلومات' in text:
        if sender_id not in user_offer_data:
            send_message(sender_id, "❌ ليس لديك جلسة نشطة\n📱 أرسل رقم جيزي (يبدأ بـ 07):")
            user_states[sender_id] = STATE_WAITING_PHONE
            return
        info = format_sim_info(user_offer_data[sender_id]['msisdn'], user_offer_data[sender_id]['token'])
        if info == TOKEN_EXPIRED:
            handle_token_expired(sender_id, 'info')
            return
        offers_keyboard(sender_id, info)
        return

    if text in ["🎁 تفعيل 2G", "تفعيل 2G", "2جيغا", "2G", "2g", "تفعيل 2جيغا"] or ('2' in text and 'جيغا' in text):
        if sender_id not in user_offer_data:
            send_message(sender_id, "❌ ليس لديك جلسة نشطة\n📱 أرسل رقم جيزي (يبدأ بـ 07):")
            user_states[sender_id] = STATE_WAITING_PHONE
            return
        threading.Thread(
            target=_handle_walk_2go,
            args=(sender_id,),
            daemon=True
        ).start()
        return

    if text in ["🎁 دعوة", "دعوة", "الدعوة", "دعوه"] or 'دعوة' in text:
        if sender_id not in user_offer_data:
            send_message(sender_id, "❌ ليس لديك جلسة نشطة\n📱 أرسل رقم جيزي (يبدأ بـ 07):")
            user_states[sender_id] = STATE_WAITING_PHONE
            return
        send_message(sender_id, "📱 أرسل رقم الذي تريد دعوته (يبدأ بـ 07):")
        user_states[sender_id] = STATE_WAITING_INVITE
        return

    if text in ["💰 عروض جيزي", "عروض جيزي", "عروض", "العروض"] or 'عرض' in text:
        msg = "💰 عروض جيزي المدفوعة - ناكتيفي 💰\n\n"
        offer_buttons = []
        for i, o in enumerate(PAID_OFFERS):
            msg += f"{i+1:2} - {o['label']}\n"
            offer_buttons.append(f"{i+1}")
        msg += "\n👇 أرسل رقم العرض:"
        send_quick_reply(sender_id, msg, offer_buttons)
        return

    if text in ["📶 تحويل شريحة", "تحويل"] or 'تحويل' in text:
        threading.Thread(target=handle_migration, args=(sender_id,), daemon=True).start()
        return

    if state == STATE_WAITING_MGM_PHONE:
        if text in ["إلغاء", "الغاء", "❌ إلغاء"]:
            user_states[sender_id] = STATE_SELECTING_OFFER
            user_mgm_data.pop(sender_id, None)
            offers_keyboard(sender_id, "❌ تم الإلغاء.\n\n👇 اختر العرض:")
            return
        
        receiver_phone = clean_phone_number(text)
        
        if receiver_phone is None or not receiver_phone.startswith('07'):
            send_message(sender_id, "❌ رقم غير صحيح\n📱 أرسل رقم جيزي يبدأ بـ 07\n✅ مثال: 0792123456")
            return
        
        if sender_id in user_mgm_data:
            saved_phone = user_mgm_data[sender_id]['receiver_phone']
            if receiver_phone != saved_phone:
                send_message(sender_id, 
                    f"❌ الرقم غير صحيح!\n"
                    f"📱 الرقم الذي دعوته هو: {saved_phone}\n"
                    f"📝 أرسل نفس الرقم:"
                )
                return
        
        threading.Thread(
            target=send_mgm_otp_once,
            args=(sender_id, receiver_phone),
            daemon=True
        ).start()
        return

    if state == STATE_WAITING_MGM_OTP:
        if text == "🔙 رجوع" or text == "❌ إلغاء":
            user_states[sender_id] = STATE_SELECTING_OFFER
            user_mgm_data.pop(sender_id, None)
            offers_keyboard(sender_id, "✅ تم الإلغاء.\n\n👇 اختر العرض:")
            return
            
        if re.match(r'^[0-9]{6}$', text):
            if sender_id not in user_mgm_data:
                send_message(sender_id, "❌ انتهت الجلسة\n📱 أرسل دعوة جديدة")
                user_states[sender_id] = STATE_SELECTING_OFFER
                return

            mgm_info = user_mgm_data[sender_id]

            if datetime.now() - mgm_info['timestamp'] > timedelta(minutes=5):
                send_message(sender_id,
                    "❌ انتهت صلاحية الرمز (5 دقائق)\n"
                    "📱 أرسل 'تفعيل' من جديد"
                )
                user_states[sender_id] = STATE_SELECTING_OFFER
                user_mgm_data.pop(sender_id, None)
                return
            
            threading.Thread(
                target=verify_mgm_otp_once,
                args=(sender_id, text),
                daemon=True
            ).start()
            return
            
        else:
            send_message(sender_id, "❌ الرمز يجب أن يكون 6 أرقام\n✉️ أرسل الرمز من 6 أرقام:")
            return

    if state == STATE_WAITING_MIGRATION:
        if text == "🔙 رجوع" or text == "❌ إلغاء":
            user_states[sender_id] = STATE_SELECTING_OFFER
            user_migration_data.pop(sender_id, None)
            offers_keyboard(sender_id, "✅ تم الإلغاء.\n\n👇 اختر العرض:")
            return
        
        if text.isdigit():
            execute_migration(sender_id, text)
        else:
            send_message(sender_id, "❌ أرسل رقم الخيار (1، 2، 3...):")
        return

    if text.isdigit() and 1 <= int(text) <= len(PAID_OFFERS) and sender_id in user_offer_data:
        offer  = PAID_OFFERS[int(text) - 1]
        result = api_activate_paid_offer(
            user_offer_data[sender_id]['token'],
            user_offer_data[sender_id]['msisdn'],
            offer, sender_id
        )
        if result.get('token_expired'):
            handle_token_expired(sender_id, 'paid_offer', {'offer': offer})
            return
        if result.get('success') == 'processing':
            return
        offers_keyboard(sender_id, result['message'])
        return

    if state == STATE_WAITING_PHONE:
        phone = clean_phone_number(text)
        
        if phone is None:
            send_message(sender_id, "❌ رقم غير صحيح\n📱 أرسل رقم جيزي يبدأ بـ 07\n✅ مثال: 0792123456")
            return
        
        if phone.startswith('05'):
            send_message(sender_id, "📲 سيتم إضافة عروض Ooredoo قريباً 🔄\n\n📱 أرسل رقم جيزي (يبدأ بـ 07):")
            return
        
        if phone.startswith('06'):
            send_message(sender_id, "❌ لا يوجد تسجيل موبيليس حالياً ❌\n\n📱 أرسل رقم جيزي (يبدأ بـ 07):")
            return
        
        if phone.startswith('07'):
            login_or_send_otp(sender_id, phone)
        return

    if state == STATE_WAITING_INVITE:
        if text == "🔙 رجوع" or text == "❌ إلغاء":
            user_states[sender_id] = STATE_SELECTING_OFFER
            offers_keyboard(sender_id, "✅ تم الإلغاء.\n\n👇 اختر العرض:")
            return
            
        receiver_phone = clean_phone_number(text)
        
        if receiver_phone is None or not receiver_phone.startswith('07'):
            send_message(sender_id, "❌ رقم غير صحيح\n📱 أرسل رقم جيزي يبدأ بـ 07\n✅ مثال: 0792123456")
            return
        
        user_states[sender_id] = STATE_SELECTING_OFFER
        threading.Thread(target=process_1go_free_interactive, args=(sender_id, receiver_phone), daemon=True).start()
        return

    if state == STATE_WAITING_OTP:
        if text in ["1", "خدمة", "إعادة إرسال", "ارسال", "resend"]:
            resend_otp(sender_id)
            return
        
        if text in ["2", "إلغاء", "الغاء", "cancel"]:
            user_states[sender_id] = STATE_SELECTING_OFFER
            pending_otp_delete(sender_id)
            clear_pending_action(sender_id)
            offers_keyboard(sender_id, "✅ تم الإلغاء.\n\n👇 اختر العرض:")
            return
        
        if text == "🔙 رجوع" or text == "❌ إلغاء":
            user_states[sender_id] = STATE_SELECTING_OFFER
            pending_otp_delete(sender_id)
            clear_pending_action(sender_id)
            offers_keyboard(sender_id, "✅ تم الإلغاء.\n\n👇 اختر العرض:")
            return
            
        if re.match(r'^[0-9]{6}$', text):
            if sender_id not in pending_otp:
                send_message(sender_id, "❌ انتهت الجلسة\n📱 أرسل رقمك مرة أخرى")
                user_states[sender_id] = STATE_WAITING_PHONE
                return
                
            if datetime.now() - pending_otp[sender_id]['timestamp'] > timedelta(minutes=5):
                send_message(sender_id, 
                    "❌ انتهت صلاحية الرمز (5 دقائق)\n"
                    "📌 أرسل '1' لإعادة إرسال الرمز"
                )
                return
                
            phone = pending_otp[sender_id]['phone']
            start_otp_verification(sender_id, phone, text)
            
        else:
            send_message(sender_id, 
                "❌ الرمز يجب أن يكون 6 أرقام\n"
                "✉️ أرسل الرمز من 6 أرقام أو '1' لإعادة الإرسال"
            )
        return

    if state == STATE_SELECTING_OFFER:
        if sender_id not in user_offer_data:
            send_message(sender_id, "❌ انتهت الجلسة\n📱 أرسل رقمك")
            user_states[sender_id] = STATE_WAITING_PHONE
            return
        offers_keyboard(sender_id, "👇 اختر العرض - Nactivi 🤖\nاذا لم يظهر لك ازرار ارسل كلمة 'مساعدة' بدون اقواس 💭")
        return

    send_message(sender_id,
        "📱 أهلاً بك في بوت ناكتيفي!\n"
        "أرسل رقم جيزي (يبدأ بـ 07)\n\n"
        "• اكتب (مساعدة) لمعرفة جميع الكلمات")
    user_states[sender_id] = STATE_WAITING_PHONE

def _handle_walk_2go(sender_id):
    result = api_activate_walk_2go(
        user_offer_data[sender_id]['token'],
        user_offer_data[sender_id]['msisdn'],
        sender_id
    )
    if result.get('token_expired'):
        handle_token_expired(sender_id, 'walk_2go')
        return
    offers_keyboard(sender_id, result['message'])

# ============================================
# ✅ Flask + Ping
# ============================================
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ بوت ناكتيفي شغال!"

@app.route('/ping')
def ping():
    return jsonify({
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "users": len(ALL_USERS),
        "activations": sum(activation_stats['paid_offers'].values()) + activation_stats['walk_2go'] + activation_stats['mgm'] + activation_stats.get('migrations', 0)
    })

@app.route('/stats')
def stats():
    return jsonify({
        "total_users": len(ALL_USERS),
        "walk_2go": activation_stats['walk_2go'],
        "mgm": activation_stats['mgm'],
        "paid_offers": dict(activation_stats['paid_offers']),
        "migrations": activation_stats.get('migrations', 0),
        "last_activations": activation_stats['last_activations']
    })

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ============================================
# ✅ جلب الرسائل
# ============================================
def poll_messages():
    global processed_message_ids, djezzy_session, PAGE_ID

    get_page_id()

    print("=" * 60)
    print("🤖 بوت ناكتيفي - الإصدار المتطور v8")
    print("✅ GET غير محدود لعروض SHAKE حتى النجاح (في الخلفية)")
    print("✅ POST غير محدود لعروض SHAKE حتى النجاح (في الخلفية)")
    print("✅ POST غير محدود لعروض activate-product حتى النجاح (في الخلفية)")
    print("✅ إعادة المحاولة لكل الأخطاء (429، 404، 500، 403، إلخ)")
    print("✅ لا يتم إيقاف المحاولة أبداً إلا عند النجاح أو رصيد غير كافي")
    print("✅ لا رسائل خطأ للمستخدم")
    print("✅ رسالة واحدة: ⏳ جاري التفعيل... ثم ✅ تم التفعيل")
    print("✅ بروكسي جديد: 51.194.225.55:41716")
    print("✅ بروكسي فقط لطلبات جيزي (API)")
    print("✅ بدون بروكسي لفيسبوك")
    print("✅ دعم جميع صيغ الأرقام")
    print("✅ كلمة سرية 'Nactivity' للمطور (إيقاف البوت)")
    print("✅ Flask + Ping على المنفذ 5000")
    print("✅ نظام انتظار مستقل لكل خدمة (12 دقيقة)")
    print("✅ حذف تلقائي للتوكنات و OTP المنتهية")
    print("=" * 60)

    consecutive_errors        = 0
    last_session_refresh_hour = -1

    while True:
        try:
            current_hour = datetime.now().hour
            if current_hour != last_session_refresh_hour and datetime.now().minute == 0:
                djezzy_session = create_djezzy_session()
                last_session_refresh_hour = current_hour
                print("🔄 تجديد جلسة جيزي")

            url = (
                f"https://graph.facebook.com/v18.0/me/conversations"
                f"?fields=messages.limit(1){{id,message,from,created_time,sticker,attachments}}"
                f"&access_token={PAGE_ACCESS_TOKEN}"
            )
            response = facebook_session.get(url, timeout=15)

            if response.status_code == 200:
                consecutive_errors = 0
                now = datetime.utcnow()

                for conversation in response.json().get('data', []):
                    for message in conversation.get('messages', {}).get('data', []):
                        message_id   = message.get('id')
                        sender_id    = message.get('from', {}).get('id')
                        message_text = message.get('message', '')
                        created_time = message.get('created_time', '')
                        
                        if PAGE_ID and sender_id == PAGE_ID:
                            processed_message_ids.add(message_id)
                            continue

                        is_sticker = False

                        if message.get('sticker'):
                            is_sticker = True

                        if not is_sticker:
                            attachments = message.get('attachments', {}).get('data', [])
                            for att in attachments:
                                if att.get('type') == 'sticker':
                                    is_sticker = True
                                    break

                        if is_sticker:
                            if message_id and message_id not in processed_message_ids and sender_id:
                                if created_time:
                                    try:
                                        msg_time = datetime.strptime(created_time, "%Y-%m-%dT%H:%M:%S+0000")
                                        if (datetime.utcnow() - msg_time).total_seconds() > 120:
                                            processed_message_ids.add(message_id)
                                            continue
                                    except Exception:
                                        pass
                                
                                processed_message_ids.add(message_id)
                                send_message(sender_id, "👍")
                            continue

                        if created_time:
                            try:
                                msg_time = datetime.strptime(created_time, "%Y-%m-%dT%H:%M:%S+0000")
                                if (now - msg_time).total_seconds() > 120:
                                    processed_message_ids.add(message_id)
                                    continue
                            except Exception:
                                pass

                        if message_id and message_id not in processed_message_ids and sender_id and message_text:
                            processed_message_ids.add(message_id)
                            threading.Thread(
                                target=handle_message,
                                args=(sender_id, message_text),
                                daemon=True
                            ).start()

                if len(processed_message_ids) > 2000:
                    processed_message_ids = set(list(processed_message_ids)[-1000:])
            else:
                consecutive_errors += 1
                if consecutive_errors % 10 == 0:
                    print(f"⚠️ خطأ: {response.status_code}")

            time.sleep(0.5)

        except Exception as e:
            consecutive_errors += 1
            print(f"❌ خطأ ({consecutive_errors}): {e}")
            if consecutive_errors > 50:
                djezzy_session = create_djezzy_session()
                get_page_id()
                consecutive_errors = 0
            time.sleep(5)

if __name__ == '__main__':
    # ✅ تشغيل Flask في Thread منفصل
    threading.Thread(target=run_flask, daemon=True).start()
    print("✅ Flask شغال على http://0.0.0.0:5000")
    print("✅ /ping للتحقق من الحالة")
    print("✅ /stats للإحصائيات")
    
    # ✅ تشغيل البوت
    poll_messages()