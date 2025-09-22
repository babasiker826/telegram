import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import requests
import io
from flask import Flask
from threading import Thread

# Flask uygulamasını oluştur
app = Flask('')

@app.route('/')
def home():
    return "Bot çalışıyor"

def run():
    app.run(host='0.0.0.0', port=8080)

# Flask'ı ayrı bir thread'de çalıştır
Thread(target=run, daemon=True).start()

# Logging ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# API URL'leri
API_ENDPOINTS = {
    "TC Sorgulama": "https://keneviz.kolsuzpabg.workers.dev/tc_sorgulama?tc={}",
    "TC Pro Sorgulama": "https://keneviz.kolsuzpabg.workers.dev/tc_pro_sorgulama?tc={}",
    "Hayat Hikayesi": "https://keneviz.kolsuzpabg.workers.dev/hayat_hikayesi?tc={}",
    "Ad Soyad": "https://keneviz.kolsuzpabg.workers.dev/ad_soyad?ad={}&soyad={}",
    "Ad Soyad Pro": "https://keneviz.kolsuzpabg.workers.dev/ad_soyad_pro?tc={}",
    "İş Yeri": "https://keneviz.kolsuzpabg.workers.dev/is_yeri?tc={}",
    "Vergi No": "https://keneviz.kolsuzpabg.workers.dev/vergi_no?vergi={}",
    "Yaş": "https://keneviz.kolsuzpabg.workers.dev/yas?tc={}",
    "TC GSM": "https://keneviz.kolsuzpabg.workers.dev/tc_gsm?tc={}",
    "GSM TC": "https://keneviz.kolsuzpabg.workers.dev/gsm_tc?gsm={}",
    "Adres": "https://keneviz.kolsuzpabg.workers.dev/adres?tc={}",
    "Hane": "https://keneviz.kolsuzpabg.workers.dev/hane?tc={}",
    "Apartman": "https://keneviz.kolsuzpabg.workers.dev/apartman?tc={}",
    "Ada Parsel": "https://keneviz.kolsuzpabg.workers.dev/ada_parsel?il={}&ada={}&parsel={}",
    "Adı İl İlçe": "https://keneviz.kolsuzpabg.workers.dev/adi_il_ilce?ad={}&il={}",
    "Aile": "https://keneviz.kolsuzpabg.workers.dev/aile?tc={}",
    "Aile Pro": "https://keneviz.kolsuzpabg.workers.dev/aile_pro?tc={}",
    "Eş": "https://keneviz.kolsuzpabg.workers.dev/es?tc={}",
    "Sülale": "https://keneviz.kolsuzpabg.workers.dev/sulale?tc={}",
    "LGS": "https://keneviz.kolsuzpabg.workers.dev/lgs?tc={}",
    "E-Kurs": "https://keneviz.kolsuzpabg.workers.dev/e_kurs?tc={}&okulno={}",
    "IP Sorgu": "https://keneviz.kolsuzpabg.workers.dev/ip?domain={}",
    "DNS": "https://keneviz.kolsuzpabg.workers.dev/dns?domain={}",
    "Whois": "https://keneviz.kolsuzpabg.workers.dev/whois?domain={}",
    "Subdomain": "https://keneviz.kolsuzpabg.workers.dev/subdomain?url={}",
    "Leak": "https://keneviz.kolsuzpabg.workers.dev/leak?query={}",
    "Telegram": "https://keneviz.kolsuzpabg.workers.dev/telegram?kullanici={}",
    "Şifre Encrypt": "https://keneviz.kolsuzpabg.workers.dev/sifre_encrypt?method={}&password={}",
    "Premium Ad": "https://keneviz.kolsuzpabg.workers.dev/prem_ad?ad={}&il={}&ilce={}",
    "MHRS Randevu": "https://keneviz.kolsuzpabg.workers.dev/mhrs_randevu?tc={}",
    "Premium Adres": "https://keneviz.kolsuzpabg.workers.dev/prem_adres?tc={}",
    "SGK Pro": "https://keneviz.kolsuzpabg.workers.dev/sgk_pro?tc={}",
    "Vergi Levhası": "https://keneviz.kolsuzpabg.workers.dev/vergi_levhasi?tc={}",
    "Facebook": "https://keneviz.kolsuzpabg.workers.dev/facebook?numara={}",
    "Diploma": "https://keneviz.kolsuzpabg.workers.dev/diploma?tc={}",
    "Başvuru": "https://keneviz.kolsuzpabg.workers.dev/basvuru?tc={}",
    "Nöbetçi Eczane": "https://keneviz.kolsuzpabg.workers.dev/nobetci_eczane?il={}&ilce={}",
    "Randevu": "https://keneviz.kolsuzpabg.workers.dev/randevu?tc={}",
    "Internet": "https://keneviz.kolsuzpabg.workers.dev/internet?tc={}",
    "Personel": "https://keneviz.kolsuzpabg.workers.dev/personel?tc={}",
    "Interpol": "https://keneviz.kolsuzpabg.workers.dev/interpol?ad={}&soyad={}",
    "Şehit": "https://keneviz.kolsuzpabg.workers.dev/sehit?Ad={}&Soyad={}",
    "Araç Parça": "https://keneviz.kolsuzpabg.workers.dev/arac_parca?plaka={}",
    "Üniversite": "https://keneviz.kolsuzpabg.workers.dev/universite?tc={}",
    "Sertifika": "https://keneviz.kolsuzpabg.workers.dev/sertifika?tc={}",
    "Nude": "https://keneviz.kolsuzpabg.workers.dev/nude",
    "Araç Borç": "https://keneviz.kolsuzpabg.workers.dev/arac_borc?plaka={}",
    "LGS 2": "https://keneviz.kolsuzpabg.workers.dev/lgs_2?tc={}",
    "Muhalle": "https://keneviz.kolsuzpabg.workers.dev/muhalle?tc={}",
    "Vesika": "https://keneviz.kolsuzpabg.workers.dev/vesika?tc={}",
    "Ehliyet": "https://keneviz.kolsuzpabg.workers.dev/ehliyet?tc={}",
    "Hava Durumu": "https://keneviz.kolsuzpabg.workers.dev/hava_durumu?sehir={}",
    "Email": "https://keneviz.kolsuzpabg.workers.dev/email?email={}",
    "Boy": "https://keneviz.kolsuzpabg.workers.dev/boy?tc={}",
    "Ayak No": "https://keneviz.kolsuzpabg.workers.dev/ayak_no?tc={}",
    "CM": "https://keneviz.kolsuzpabg.workers.dev/cm?tc={}",
    "Burç": "https://keneviz.kolsuzpabg.workers.dev/burc?tc={}",
    "Çocuk": "https://keneviz.kolsuzpabg.workers.dev/cocuk?tc={}",
    "IMEI": "https://keneviz.kolsuzpabg.workers.dev/imei?imei={}",
    "Baba": "https://keneviz.kolsuzpabg.workers.dev/baba?tc={}",
    "Anne": "https://keneviz.kolsuzpabg.workers.dev/anne?tc={}",
    "Operatör": "https://keneviz.kolsuzpabg.workers.dev/operator?gsm={}",
    "Fatura": "https://keneviz.kolsuzpabg.workers.dev/fatura?tc={}",
    "Hexnox Subdomain": "https://keneviz.kolsuzpabg.workers.dev/hexnox_subdomain?url={}",
    "Sex Görsel": "https://keneviz.kolsuzpabg.workers.dev/sexgorsel?soru={}",
    "Meslek Hex": "https://keneviz.kolsuzpabg.workers.dev/meslek_hex?tc={}",
    "SGK Hex": "https://keneviz.kolsuzpabg.workers.dev/sgk_hex?tc={}",
    "Subdomain Generic": "https://keneviz.kolsuzpabg.workers.dev/subdomain_generic?url={}",
    "Seçmen": "https://keneviz.kolsuzpabg.workers.dev/secmen?tc={}",
    "Öğretmen": "https://keneviz.kolsuzpabg.workers.dev/ogretmen?ad={}&soyad={}",
    "SMS Bomber": "https://keneviz.kolsuzpabg.workers.dev/smsbomber?number={}",
    "Yabancı": "https://keneviz.kolsuzpabg.workers.dev/yabanci?ad={}&soyad={}",
    "Log": "https://keneviz.kolsuzpabg.workers.dev/log?site={}",
    "Vesika 2": "https://keneviz.kolsuzpabg.workers.dev/vesika2?tc={}",
    "Tapu 2": "https://keneviz.kolsuzpabg.workers.dev/tapu2?tc={}",
    "Aile Detaylı": "https://keneviz.kolsuzpabg.workers.dev/aile_detayli?tc={}",
    "Türk Telekom": "https://keneviz.kolsuzpabg.workers.dev/turk_telekom?gsm={}",
    "Yetimlik Sorgu": "https://keneviz.kolsuzpabg.workers.dev/yetimlik?tc={}",
    "Stilale Sorgu": "https://keneviz.kolsuzpabg.workers.dev/stilale?tc={}",
    "Detaylı Yaş": "https://keneviz.kolsuzpabg.workers.dev/detayli_yas?tc={}",
    "Yeğen Sorgu": "https://keneviz.kolsuzpabg.workers.dev/yegen?tc={}",
    "Kızlık Soyadı": "https://keneviz.kolsuzpabg.workers.dev/kizlik_soyadi?tc={}",
    "Sıra No Sorgu": "https://keneviz.kolsuzpabg.workers.dev/sira_no?tc={}",
    "Operatör Sorgu": "https://keneviz.kolsuzpabg.workers.dev/operator_sorgu?gsm={}",
    "İban Sorgu": "https://keneviz.kolsuzpabg.workers.dev/iban?iban={}",
    "Sim Kart Sorgu": "https://keneviz.kolsuzpabg.workers.dev/sim_kart?gsm={}",
    "Seri No Sorgu": "https://keneviz.kolsuzpabg.workers.dev/seri_no?seri={}",
    "Mersis Dükkan": "https://keneviz.kolsuzpabg.workers.dev/mersis_dukkan?mersis={}",
    "Sicil Sorgu": "https://keneviz.kolsuzpabg.workers.dev/sicil?sicil={}",
    "Mahkum Sorgu": "https://keneviz.kolsuzpabg.workers.dev/mahkum?tc={}",
    "Araç Muayene": "https://keneviz.kolsuzpabg.workers.dev/arac_muayene?plaka={}",
    "Plaka Sorgu": "https://keneviz.kolsuzpabg.workers.dev/plaka?plaka={}",
    "Tapu Sorgu": "https://keneviz.kolsuzpabg.workers.dev/tapu?tc={}",
    "Soyağacı Sorgu": "https://keneviz.kolsuzpabg.workers.dev/soyagaci?tc={}",
    "Muayene Sorgu": "https://keneviz.kolsuzpabg.workers.dev/muayene?tc={}"
}

# Emoji ataması
SORGU_EMOJILERI = {
    "TC Sorgulama": "🆔", "TC Pro Sorgulama": "🔍", "Hayat Hikayesi": "📖",
    "Ad Soyad": "👤", "Ad Soyad Pro": "👥", "İş Yeri": "🏢", "Vergi No": "💰",
    "Yaş": "🎂", "TC GSM": "📱", "GSM TC": "☎️", "Adres": "🏠", "Hane": "👨‍👩‍👧‍👦",
    "Apartman": "🏘️", "Ada Parsel": "📊", "Adı İl İlçe": "📍", "Aile": "👪",
    "Aile Pro": "👨‍👩‍👧‍👦", "Eş": "💑", "Sülale": "🧬", "LGS": "🎓", "E-Kurs": "📚",
    "IP Sorgu": "🌐", "DNS": "🔗", "Whois": "🔎", "Subdomain": "🔍", "Leak": "🔓",
    "Telegram": "✈️", "Şifre Encrypt": "🔒", "Premium Ad": "⭐", "MHRS Randevu": "🏥",
    "Premium Adres": "🏡", "SGK Pro": "🏛️", "Vergi Levhası": "📄", "Facebook": "📘",
    "Diploma": "🎓", "Başvuru": "📝", "Nöbetçi Eczane": "💊", "Randevu": "📅",
    "Internet": "🌐", "Personel": "👔", "Interpol": "👮", "Şehit": "🇹🇷",
    "Araç Parça": "🚗", "Üniversite": "🎓", "Sertifika": "📜", "Nude": "🔞",
    "Araç Borç": "💳", "LGS 2": "🎓", "Muhalle": "🍮", "Vesika": "📇", "Ehliyet": "🚦",
    "Hava Durumu": "☀️", "Email": "📧", "Boy": "📏", "Ayak No": "👣", "CM": "📐",
    "Burç": "♈", "Çocuk": "👶", "IMEI": "📲", "Baba": "👨", "Anne": "👩",
    "Operatör": "📶", "Fatura": "🧾", "Hexnox Subdomain": "🌐", "Sex Görsel": "🔞",
    "Meslek Hex": "⚒️", "SGK Hex": "🏛️", "Subdomain Generic": "🔗", "Seçmen": "🗳️",
    "Öğretmen": "👨‍🏫", "SMS Bomber": "💣", "Yabancı": "👤", "Log": "📋", "Vesika 2": "📇",
    "Tapu 2": "🏠", "Aile Detaylı": "👨‍👩‍👧‍👦", "Türk Telekom": "📞", "Yetimlik Sorgu": "😢",
    "Stilale Sorgu": "🧬", "Detaylı Yaş": "🎂", "Yeğen Sorgu": "👦", "Kızlık Soyadı": "👰",
    "Sıra No Sorgu": "🔢", "Operatör Sorgu": "📶", "İban Sorgu": "💳", "Sim Kart Sorgu": "📱",
    "Seri No Sorgu": "🔢", "Mersis Dükkan": "🏪", "Sicil Sorgu": "📋", "Mahkum Sorgu": "🔒",
    "Araç Muayene": "🚗", "Plaka Sorgu": "🚘", "Tapu Sorgu": "🏠", "Soyağacı Sorgu": "🌳",
    "Muayene Sorgu": "🏥"
}

# Kullanıcıdan hangi sorgu için hangi parametrelerin isteneceği bilgisi
QUERY_PARAMS = {
    "TC Sorgulama": ["TC Kimlik No (11 haneli)"],
    "TC Pro Sorgulama": ["TC Kimlik No (11 haneli)"],
    "Hayat Hikayesi": ["TC Kimlik No (11 haneli)"],
    "Ad Soyad": ["Ad", "Soyad"],
    "Ad Soyad Pro": ["TC Kimlik No (11 haneli)"],
    "İş Yeri": ["TC Kimlik No (11 haneli)"],
    "Vergi No": ["Vergi No"],
    "Yaş": ["TC Kimlik No (11 haneli)"],
    "TC GSM": ["TC Kimlik No (11 haneli)"],
    "GSM TC": ["GSM No"],
    "Adres": ["TC Kimlik No (11 haneli)"],
    "Hane": ["TC Kimlik No (11 haneli)"],
    "Apartman": ["TC Kimlik No (11 haneli)"],
    "Ada Parsel": ["İl", "Ada", "Parsel"],
    "Adı İl İlçe": ["Ad", "İl"],
    "Aile": ["TC Kimlik No (11 haneli)"],
    "Aile Pro": ["TC Kimlik No (11 haneli)"],
    "Eş": ["TC Kimlik No (11 haneli)"],
    "Sülale": ["TC Kimlik No (11 haneli)"],
    "LGS": ["TC Kimlik No (11 haneli)"],
    "E-Kurs": ["TC Kimlik No (11 haneli)", "Okul No"],
    "IP Sorgu": ["Domain/IP"],
    "DNS": ["Domain"],
    "Whois": ["Domain"],
    "Subdomain": ["URL"],
    "Leak": ["Sorgu"],
    "Telegram": ["Kullanıcı Adı"],
    "Şifre Encrypt": ["Method", "Password"],
    "Premium Ad": ["Ad", "İl", "İlçe"],
    "MHRS Randevu": ["TC Kimlik No (11 haneli)"],
    "Premium Adres": ["TC Kimlik No (11 haneli)"],
    "SGK Pro": ["TC Kimlik No (11 haneli)"],
    "Vergi Levhası": ["TC Kimlik No (11 haneli)"],
    "Facebook": ["Telefon Numarası"],
    "Diploma": ["TC Kimlik No (11 haneli)"],
    "Başvuru": ["TC Kimlik No (11 haneli)"],
    "Nöbetçi Eczane": ["İl", "İlçe"],
    "Randevu": ["TC Kimlik No (11 haneli)"],
    "Internet": ["TC Kimlik No (11 haneli)"],
    "Personel": ["TC Kimlik No (11 haneli)"],
    "Interpol": ["Ad", "Soyad"],
    "Şehit": ["Ad", "Soyad"],
    "Araç Parça": ["Plaka"],
    "Üniversite": ["TC Kimlik No (11 haneli)"],
    "Sertifika": ["TC Kimlik No (11 haneli)"],
    "Nude": [],
    "Araç Borç": ["Plaka"],
    "LGS 2": ["TC Kimlik No (11 haneli)"],
    "Muhalle": ["TC Kimlik No (11 haneli)"],
    "Vesika": ["TC Kimlik No (11 haneli)"],
    "Ehliyet": ["TC Kimlik No (11 haneli)"],
    "Hava Durumu": ["Şehir"],
    "Email": ["Email"],
    "Boy": ["TC Kimlik No (11 haneli)"],
    "Ayak No": ["TC Kimlik No (11 haneli)"],
    "CM": ["TC Kimlik No (11 haneli)"],
    "Burç": ["TC Kimlik No (11 haneli)"],
    "Çocuk": ["TC Kimlik No (11 haneli)"],
    "IMEI": ["IMEI No"],
    "Baba": ["TC Kimlik No (11 haneli)"],
    "Anne": ["TC Kimlik No (11 haneli)"],
    "Operatör": ["GSM No"],
    "Fatura": ["TC Kimlik No (11 haneli)"],
    "Hexnox Subdomain": ["URL"],
    "Sex Görsel": ["Soru"],
    "Meslek Hex": ["TC Kimlik No (11 haneli)"],
    "SGK Hex": ["TC Kimlik No (11 haneli)"],
    "Subdomain Generic": ["URL"],
    "Seçmen": ["TC Kimlik No (11 haneli)"],
    "Öğretmen": ["Ad", "Soyad"],
    "SMS Bomber": ["Telefon Numarası"],
    "Yabancı": ["Ad", "Soyad"],
    "Log": ["Site"],
    "Vesika 2": ["TC Kimlik No (11 haneli)"],
    "Tapu 2": ["TC Kimlik No (11 haneli)"],
    "Aile Detaylı": ["TC Kimlik No (11 haneli)"],
    "Türk Telekom": ["GSM No"],
    "Yetimlik Sorgu": ["TC Kimlik No (11 haneli)"],
    "Stilale Sorgu": ["TC Kimlik No (11 haneli)"],
    "Detaylı Yaş": ["TC Kimlik No (11 haneli)"],
    "Yeğen Sorgu": ["TC Kimlik No (11 haneli)"],
    "Kızlık Soyadı": ["TC Kimlik No (11 haneli)"],
    "Sıra No Sorgu": ["TC Kimlik No (11 haneli)"],
    "Operatör Sorgu": ["GSM No"],
    "İban Sorgu": ["IBAN No"],
    "Sim Kart Sorgu": ["GSM No"],
    "Seri No Sorgu": ["Seri No"],
    "Mersis Dükkan": ["Mersis No"],
    "Sicil Sorgu": ["Sicil No"],
    "Mahkum Sorgu": ["TC Kimlik No (11 haneli)"],
    "Araç Muayene": ["Plaka"],
    "Plaka Sorgu": ["Plaka"],
    "Tapu Sorgu": ["TC Kimlik No (11 haneli)"],
    "Soyağacı Sorgu": ["TC Kimlik No (11 haneli)"],
    "Muayene Sorgu": ["TC Kimlik No (11 haneli)"]
}

# Kategoriler ve sorgu dağılımları
CATEGORIES = {
    "📋 Temel Sorgular": ["TC Sorgulama", "Ad Soyad", "TC GSM", "GSM TC", "Adres", "Aile", "Eş", "Çocuk", "Anne", "Baba"],
    "🔍 Detaylı Sorgular": ["TC Pro Sorgulama", "Ad Soyad Pro", "Aile Pro", "Hayat Hikayesi", "Sülale", "Yaş", "İş Yeri", "Üniversite", "Ehliyet", "Vesika"],
    "📊 Diğer Sorgular": ["IP Sorgu", "Telegram", "Facebook", "Email", "Hava Durumu", "Nöbetçi Eczane", "Araç Parça", "Araç Borç", "Vergi No", "Şehit"],
    "⚙️ Teknik Sorgular": ["DNS", "Whois", "Subdomain", "Leak", "Log", "IMEI", "SMS Bomber", "Şifre Encrypt"],
    "🏠 Adres/Vergi": ["Ada Parsel", "Vergi Levhası", "Tapu Sorgu", "Tapu 2", "Mersis Dükkan"],
    "📞 GSM/Operatör": ["Operatör", "Operatör Sorgu", "Türk Telekom", "Sim Kart Sorgu", "Fatura"],
    "👥 Aile Sorguları": ["Aile Detaylı", "Stilale Sorgu", "Yeğen Sorgu", "Kızlık Soyadı", "Yetimlik Sorgu"],
    "🔐 Özel Sorgular": ["İban Sorgu", "Seri No Sorgu", "Sicil Sorgu", "Mahkum Sorgu", "Soyağacı Sorgu"],
    "📦 Ek Sorgular": ["Hane", "Apartman", "Adı İl İlçe", "LGS", "E-Kurs", "Premium Ad", "MHRS Randevu", "Premium Adres",
                      "SGK Pro", "Diploma", "Başvuru", "Randevu", "Internet", "Personel", "Interpol", "Sertifika",
                      "Nude", "LGS 2", "Muhalle", "Boy", "Ayak No", "CM", "Burç", "Hexnox Subdomain", "Sex Görsel",
                      "Meslek Hex", "SGK Hex", "Subdomain Generic", "Seçmen", "Öğretmen", "Yabancı", "Vesika 2",
                      "Detaylı Yaş", "Sıra No Sorgu", "Araç Muayene", "Plaka Sorgu", "Muayene Sorgu"]
}

# Kullanıcı durumlarını tutmak için basit dict (küçük botlar için yeterli)
user_states = {}

# Başlangıç mesajı ve ana menü butonları
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"👋 Merhaba {user.first_name}! \n\n"
        "Bu bot ile çeşitli sorgular yapabilirsiniz. Aşağıdaki butonlardan seçim yapabilirsiniz.\n\n"
        "🔍 *Sorgular* - Farklı sorgu türlerini seçip kullanabilirsiniz.\n"
        "ℹ️ *Hakkında* - Bot hakkında bilgi alabilirsiniz."
    )
    keyboard = [
        [InlineKeyboardButton("🔍 Sorgular", callback_data="menu_sorgular"),
         InlineKeyboardButton("ℹ️ Hakkında", callback_data="menu_hakkinda")]
    ]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Ana menü callback handler
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "menu_sorgular":
        buttons = []
        for category_name in CATEGORIES.keys():
            buttons.append([InlineKeyboardButton(category_name, callback_data=f"category_{category_name}")])
        buttons.append([InlineKeyboardButton("⬅️ Geri", callback_data="menu_ana")])
        await query.edit_message_text("Lütfen bir kategori seçin:", reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data.startswith("category_"):
        category_name = query.data[9:]
        if category_name in CATEGORIES:
            queries = CATEGORIES[category_name]
            buttons = []
            row = []
            count = 0
            for query_name in queries:
                emoji = SORGU_EMOJILERI.get(query_name, "🔍")
                row.append(InlineKeyboardButton(f"{emoji} {query_name}", callback_data=f"sorgu_{query_name}"))
                count += 1
                if count % 2 == 0:
                    buttons.append(row)
                    row = []
            if row:
                buttons.append(row)
            buttons.append([InlineKeyboardButton("⬅️ Geri", callback_data="menu_sorgular")])
            await query.edit_message_text(f"{category_name} - Lütfen sorgu türünü seçin:", reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data == "menu_hakkinda":
        hakkinda_text = (
            "🤖 *Bot Hakkında*\n\n"
            "Bu bot, 2025 yılında geliştirilmiştir.\n"
            "74 farklı API ile çeşitli sorgular yapabilirsiniz.\n"
            "Telegram bot API ve python-telegram-bot kütüphanesi kullanılmıştır.\n"
            "Geliştirici: @sukazatkinis\n"
            "Herhangi bir sorunuz için iletişime geçebilirsiniz.\n"
            "Yakin Zamanda Sorgu Sayisi 120 Cikartilicak Ve Free Sizlere Sunulcak\n"
            "Sizden Tek Istediğimiz Kanalarimizda Botumuzda Aktif Olmaniz"
        )
        buttons = [[InlineKeyboardButton("⬅️ Geri", callback_data="menu_ana")]]
        await query.edit_message_text(hakkinda_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

    elif query.data == "menu_ana":
        buttons = [
            [InlineKeyboardButton("🔍 Sorgular", callback_data="menu_sorgular"),
             InlineKeyboardButton("ℹ️ Hakkında", callback_data="menu_hakkinda")]
        ]
        await query.edit_message_text(
            f"👋 Ana menüye hoş geldiniz, {update.effective_user.first_name}!",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif query.data.startswith("sorgu_"):
        sorgu_adi = query.data[6:]
        user_id = query.from_user.id
        user_states[user_id] = {"sorgu": sorgu_adi, "params": [], "step": 0}

        param_list = QUERY_PARAMS.get(sorgu_adi, [])
        if not param_list:
            user_states.pop(user_id)
            await query.edit_message_text("Sorgunuz işleniyor, lütfen bekleyin...")
            try:
                response = requests.get(API_ENDPOINTS[sorgu_adi], timeout=10)
                if response.status_code == 200:
                    data = response.text
                    if len(data) > 4000:
                        file_data = io.BytesIO(data.encode('utf-8'))
                        file_data.name = f"{sorgu_adi}_sonuc.txt"
                        await query.message.reply_document(document=file_data, caption=f"📊 {sorgu_adi} sonucu (çok uzun, dosya olarak gönderildi)")
                    else:
                        await query.message.reply_text(f"📊 {sorgu_adi} sonucu:\n\n{data}")
                else:
                    await query.message.reply_text("API'den geçerli bir yanıt alınamadı.")
            except Exception as e:
                await query.message.reply_text(f"API çağrısında hata oluştu: {e}")
            return

        await query.edit_message_text(
            f"📝 {sorgu_adi} sorgusu için lütfen aşağıdaki bilgiyi girin:\n\n"
            f"{param_list[0]}"
        )

# Kullanıcıdan parametreleri alma ve API çağrısı yapma
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_states:
        await update.message.reply_text("Lütfen önce bir sorgu seçin. /start yazabilirsiniz.")
        return

    state = user_states[user_id]
    sorgu_adi = state["sorgu"]
    params = state["params"]
    step = state["step"]

    param_list = QUERY_PARAMS.get(sorgu_adi, [])
    params.append(update.message.text.strip())
    step += 1

    if step < len(param_list):
        user_states[user_id]["params"] = params
        user_states[user_id]["step"] = step
        await update.message.reply_text(f"Lütfen {param_list[step]} girin:")
    else:
        user_states.pop(user_id)
        try:
            url = API_ENDPOINTS[sorgu_adi]
            for param in params:
                url = url.replace("{}", param, 1)
        except Exception as e:
            await update.message.reply_text("Parametrelerde hata oluştu, lütfen tekrar deneyin.")
            return

        await update.message.reply_text("Sorgunuz işleniyor, lütfen bekleyin...")

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.text
                if len(data) > 4000:
                    file_data = io.BytesIO(data.encode('utf-8'))
                    file_data.name = f"{sorgu_adi}_sonuc.txt"
                    await update.message.reply_document(document=file_data, caption=f"📊 {sorgu_adi} sonucu (çok uzun, dosya olarak gönderildi)")
                else:
                    await update.message.reply_text(f"📊 {sorgu_adi} sonucu:\n\n{data}")
            else:
                await update.message.reply_text("API'den geçerli bir yanıt alınamadı.")
        except Exception as e:
            await update.message.reply_text(f"API çağrısında hata oluştu: {e}")

async def main():
    TOKEN = "8026378524:AAHcJH1O73P_IkRFm6EpG7wY0j7X5s46D_w"
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("Bot çalışıyor...")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
