from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from googletrans import Translator
import re
import random
import os

# Çeviriciyi başlat
translator = Translator()

# Çeviri yapmayı deneyin, başarısız olursa yeniden deneyin
def deneme_ile_cevir(yorum, deneme_sayisi=3):
    for _ in range(deneme_sayisi):
        try:
            temiz_yorum = re.sub(r'\s+', ' ', yorum).strip()
            translated = translator.translate(temiz_yorum, src='en', dest='tr')
            return translated.text
        except Exception as e:
            print(f"Çeviri hatası: {e}, yeniden deneme")
            time.sleep(random.uniform(1, 3))
    return yorum

# Film verilerini çekme ve yorumları işleme fonksiyonu
def film_verilerini_cek_ve_yorumlari_yaz(film_url, sheet_name):
    driver.get(film_url)
    
    # Film bilgilerini çek
    film_adi_element = driver.find_element(By.CSS_SELECTOR, 'a.sidebar-title[data-qa="sidebar-media-link"]')
    film_adi = film_adi_element.text

    # Çıkış tarihi ve tür bilgilerini çek
    film_bilgileri_element = driver.find_element(By.CSS_SELECTOR, 'ul[data-qa="sidebar-movie-details"]')
    film_bilgileri = film_bilgileri_element.find_elements(By.TAG_NAME, 'li')

    cikis_tarihi = ''
    turu = ''

    for bilgi in film_bilgileri:
        text = bilgi.text
        if 'In Theaters:' in text:
            cikis_tarihi = text.split('In Theaters:')[1].strip()
        elif 'Adventure' in text or 'Action' in text:
            turu = text.strip()

    # Yorumları tutmak için liste
    yorumlar_listesi = []

    # "Daha Fazla Yükle" butonuna tıklama sayısını takip et
    tıklama_sayısı = 0
    maks_tıklama = 5

    # Tüm yorumları yükle
    while True:
        try:
            # Yorumları çek
            elements = driver.find_elements(By.CSS_SELECTOR, 'p.audience-reviews__review.js-review-text[data-qa="review-text"]')
            print(f"Bulunan yorum sayısı: {len(elements)}")
            for element in elements:
                text = element.text
                if text not in yorumlar_listesi:
                    yorumlar_listesi.append(text)
                    
            print(f"Toplam yorum sayısı: {len(yorumlar_listesi)}")

            # Eğer yorum sayısı yeterliyse döngüyü kır
            if len(yorumlar_listesi) >= 100:
                break

            # "Daha Fazla Yükle" butonunu bul ve tıkla
            try:
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "rt-button[data-qa='load-more-btn']"))
                )
                driver.execute_script("arguments[0].scrollIntoView();", load_more_button)  # Butonu görünür yap
                load_more_button.click()
                time.sleep(2)
                tıklama_sayısı += 1
                if tıklama_sayısı >= maks_tıklama:
                    break
            except Exception as e:
                print(f"‘Daha Fazla Yükle’ butonu bulunamadı veya tıklanamadı: {e}")
                break

        except Exception as e:
            print(f"Hata oluştu: {e}")
            break

    # Yorumları Türkçeye çevir
    yorumlar_turkce = []
    for yorum in yorumlar_listesi:
        cevirilmis_yorum = deneme_ile_cevir(yorum)
        yorumlar_turkce.append(cevirilmis_yorum)

    # Excel dosyasını yükle veya oluştur
    file_path = 'yorumlar_turkce9.xlsx'
    if os.path.exists(file_path):
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            film_bilgileri_df = pd.DataFrame({
                'Film Adı': [film_adi],
                'Çıkış Tarihi': [cikis_tarihi],
                'Türü': [turu]
            })

            yorumlar_df = pd.DataFrame({
                'Yorum No': range(1, len(yorumlar_turkce) + 1),
                'Yorum': yorumlar_turkce
            })

            film_bilgileri_df.to_excel(writer, sheet_name='Film Yorumları', index=False, startrow=writer.sheets['Film Yorumları'].max_row + 1)

            yorumlar_df.to_excel(writer, sheet_name='Film Yorumları', index=False, startrow=writer.sheets['Film Yorumları'].max_row + 2)
    else:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            film_bilgileri_df = pd.DataFrame({
                'Film Adı': [film_adi],
                'Çıkış Tarihi': [cikis_tarihi],
                'Türü': [turu]
            })

            yorumlar_df = pd.DataFrame({
                'Yorum No': range(1, len(yorumlar_turkce) + 1),
                'Yorum': yorumlar_turkce
            })

            film_bilgileri_df.to_excel(writer, sheet_name='Film Yorumları', index=False, startrow=0)
            yorumlar_df.to_excel(writer, sheet_name='Film Yorumları', index=False, startrow=len(film_bilgileri_df) + 2)

    print(f"{film_adi} için veriler başarıyla 'yorumlar_turkce9.xlsx' dosyasına kaydedildi.")

# Chrome sürücüsünü başlat
driver = webdriver.Chrome()

# Kullanıcıdan film adını alın
filmAdi = input("Film adını giriniz: ")

filmAdi_formatlanmis = filmAdi.lower().replace(' ', '_')

# İşlem yapılacak film URL'lerini listeye ekleyin
film_urls = [
    f"https://www.rottentomatoes.com/m/{filmAdi_formatlanmis}/reviews?type=user"
]

# Her film için verileri çek ve yorumları yaz
for url in film_urls:
    film_verilerini_cek_ve_yorumlari_yaz(url, 'Film Yorumları')

# Tarayıcıyı kapat
driver.quit()