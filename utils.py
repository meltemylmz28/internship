import openpyxl
import pdfplumber
import re
import os

def excel_oku(dosya_yolu):
    wb = openpyxl.load_workbook(dosya_yolu)
    sheet = wb.active
    ogrenci_listesi = []
    
    # 5. satırdaki ders başlıklarını dinamik topla (B sütunundan itibaren)
    dersler = []
    BASLANGIC_SUTUNU = 2
    BASLIK_SATIRI = 5
    
    for col in range(BASLANGIC_SUTUNU, sheet.max_column + 1):
        ders_adi = sheet.cell(row=BASLIK_SATIRI, column=col).value
        if ders_adi:
            dersler.append(ders_adi)
            
    # 6. satırdan itibaren öğrencileri ve notları oku
    VERI_BASLANGIC_SATIRI = 6
    for row in range(VERI_BASLANGIC_SATIRI, sheet.max_row + 1):
        ogrenci_girdi = sheet.cell(row=row, column=1).value
        
        if ogrenci_girdi is not None:
            # ÇÖZÜM: ogrenci_girdi değerini str() ile güvenli hale getirdik
            ogrenci_adi = str(ogrenci_girdi).replace("Öğrenci Adı:", "").strip()
            notlar = {}
            toplam_not = 0
            ders_sayisi = 0
            
            for idx, ders in enumerate(dersler):
                not_degeri = sheet.cell(row=row, column=idx + BASLANGIC_SUTUNU).value
                if not_degeri is not None:
                    try:
                        not_int = int(not_degeri)
                        notlar[ders] = not_int
                        toplam_not += not_int
                        ders_sayisi += 1
                    except ValueError:
                        # Eğer not alanında sayı yerine metin vb. varsa hata vermeden geçsin
                        continue
            
            ortalama = toplam_not / ders_sayisi if ders_sayisi > 0 else 0
            ogrenci_listesi.append({
                "ogrenci_adi": ogrenci_adi,
                "notlar": notlar,
                "ortalama": round(ortalama, 2)
            })
            
    return ogrenci_listesi


def pdf_oku(dosya_yolu):
    ogrenci_listesi = []
    DERS_ADI_IDX = 0
    NOT_IDX = 2  # MEB Karnesi 1. Dönem Puanı Sütunu
    
    with pdfplumber.open(dosya_yolu) as pdf:
        sayfa = pdf.pages[0]
        metin = sayfa.extract_text()
        
        ad_match = re.search(r"ADI SOYADI\s+(.+)", metin)
        ogrenci_adi = ad_match.group(1).strip() if ad_match else "Bilinmeyen Öğrenci"
        
        tablo = sayfa.extract_table()
        notlar = {}
        toplam_not = 0
        ders_sayisi = 0
        
        if tablo:
            for satir in tablo:
                if satir and satir[DERS_ADI_IDX]:
                    ders_adi = satir[DERS_ADI_IDX].strip()
                    
                    if ders_adi.isupper() and "DERS" not in ders_adi and "TOPLAM" not in ders_adi:
                        try:
                            not_metni = satir[NOT_IDX].strip() if satir[NOT_IDX] else "0"
                            if not_metni.replace('.', '', 1).isdigit(): 
                                not_degeri = int(float(not_metni))
                                notlar[ders_adi] = not_degeri
                                toplam_not += not_degeri
                                ders_sayisi += 1
                        except (IndexError, ValueError):
                            continue
        
        ortalama = toplam_not / ders_sayisi if ders_sayisi > 0 else 0
        ogrenci_listesi.append({
            "ogrenci_adi": ogrenci_adi,
            "notlar": notlar,
            "ortalama": round(ortalama, 2)
        })
        
    return ogrenci_listesi


def karne_sistemine_yukle(dosya_yolu):
    uzanti = os.path.splitext(dosya_yolu)[1].lower()
    if uzanti == '.xlsx':
        return excel_oku(dosya_yolu)
    elif uzanti == '.pdf':
        return pdf_oku(dosya_yolu)
    else:
        raise ValueError("Desteklenmeyen dosya formatı!")