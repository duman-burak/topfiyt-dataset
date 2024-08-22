import pandas as pd

# TDK kelime listesini yükleme
def tdk_kelimeleri_yukle(dosya_yolu):
    with open(dosya_yolu, 'r', encoding='utf-8') as file:
        kelimeler = set(line.strip().lower() for line in file)
    return kelimeler

# Verilen metindeki kelimeleri TDK listesine göre filtreleme
def tdk_filtreleme(metin, tdk_kelimeler):
    if pd.isna(metin):
        return ''
    
    kelimeler = metin.lower().split()
    kelimeler = [kelime for kelime in kelimeler if kelime in tdk_kelimeler]
    return ' '.join(kelimeler)

# Excel dosyasını yükle
df = pd.read_excel(r'C:\Users\burak\Desktop\yorum\yorumlar_turkce9.xlsx', header=3)

# TDK kelime listesini yükle
tdk_kelimeler = tdk_kelimeleri_yukle(r'C:\Users\burak\Desktop\yorum\tdk.txt')

# Yorumları TDK kelime listesine göre filtrele
df['Temizlenmiş Yorum'] = df['Yorum'].apply(lambda x: tdk_filtreleme(x, tdk_kelimeler))

# Temizlenmiş yorumları eski yorumların yerine koy
df['Yorum'] = df['Temizlenmiş Yorum']

# Geçici sütunu kaldır
df.drop(columns=['Temizlenmiş Yorum'], inplace=True)

# Dosyayı kaydet
df.to_excel(r'C:\Users\burak\Desktop\yorum\yorumlar_tdk_filtresi.xlsx', index=False)