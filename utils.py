import openpyxl
import xlrd
import pdfplumber
import re
import os

def xls_oku(dosya_yolu):
    """Eski .xls uzantılı çoklu sekme (MEB Kazanım Değerlendirme) dosyalarını okur."""
    wb = xlrd.open_workbook(dosya_yolu)
    konsolide_veriler = {}
    
    ders_haritasi = {
        "T": "TÜRKÇE", "M": "MATEMATİK", "HB": "HAYAT BİLGİSİ",
        "BEO": "BEDEN EĞİTİMİ VE OYUN", "MÜ": "MÜZİK", "GS": "GÖRSEL SANATLAR"
    }

    for sheet_name in wb.sheet_names():
        # Bilgiler sekmesini ve sistem sekmelerini pas geç, sadece ders sekmelerini tara
        if "bilgi" in sheet_name.lower() or "not" in sheet_name.lower():
            continue
            
        sheet = wb.sheet_by_name(sheet_name)
        temiz_kod = re.sub(r'[^a-zA-ZğüşıöçĞÜŞİÖÇ]', '', sheet_name).upper().strip()
        ders_adi = ders_haritasi.get(temiz_kod, f"DERS ({sheet_name})")
        
        # Bu MEB şablonlarında başlık satırı genellikle SIRA NO ile başlayan satırdır
        baslik_satiri = 3
        for r in range(min(sheet.nrows, 6)):
            if sheet.ncols > 2:
                h_val = str(sheet.cell_value(r, 2) or '').upper()
                if "ADI" in h_val or "SOYADI" in h_val or "SIRA" in str(sheet.cell_value(r, 0 or 0)).upper():
                    baslik_satiri = r
                    break
                    
        # Puan sütunlarını ayırt et (D sütunundan yani 3. indeksten başlayarak puanları toplar)
        puan_sutunlari = []
        if sheet.nrows > baslik_satiri:
            for col in range(3, sheet.ncols):
                b_degeri = str(sheet.cell_value(baslik_satiri, col) or '').upper()
                if "ORTALAMA" in b_degeri or "SONUÇ" in b_degeri or b_degeri == "":
                    continue
                puan_sutunlari.append(col)
                
            # Öğrencileri satır satır tarıyoruz
            for r in range(baslik_satiri + 1, sheet.nrows):
                ogrenci_adi = sheet.cell_value(r, 2)  # C Sütunu Ad Soyad
                okul_no_val = sheet.cell_value(r, 1)  # B Sütunu Okul No
                
                if not ogrenci_adi:
                    continue
                    
                ogrenci_adi_str = str(ogrenci_adi).strip().upper()
                
                # Raporlama/İmza satırlarını eliyoruz
                if any(k in ogrenci_adi_str for k in ["TOPLAM", "SINIF ÖĞRETMENİ", "OKUL MÜDÜRÜ", "GRAFİK", "MÜDÜR"]):
                    continue
                
                # Okul numarası kısmı boş olan veya geçersiz satırları atla
                if okul_no_val is None or str(okul_no_val).strip() == "" or "OKUL" in str(okul_no_val).upper():
                    continue
                    
                toplam_puan = 0
                gecerli_puan_sayisi = 0
                
                for col in puan_sutunlari:
                    hucre_degeri = sheet.cell_value(r, col)
                    if hucre_degeri is not None and hucre_degeri != "":
                        try:
                            puan_float = float(hucre_degeri)
                            toplam_puan += puan_float
                            gecerli_puan_sayisi += 1
                        except ValueError:
                            continue
                
                # Eğer öğrencinin o derse ait girilmiş kazanım puanı varsa ortalama çıkar
                if gecerli_puan_sayisi > 0:
                    ham_ortalama = toplam_puan / gecerli_puan_sayisi
                    # 4'lük sistemi 100'lük nota çevir
                    yuzluk_not = (ham_ortalama / 4.0) * 100 if ham_ortalama <= 4.0 else ham_ortalama
                    
                    if ogrenci_adi_str not in konsolide_veriler:
                        konsolide_veriler[ogrenci_adi_str] = {}
                    konsolide_veriler[ogrenci_adi_str][ders_adi] = round(yuzluk_not, 2)

    # Sözlük verisini frontend'in istediği şık liste yapısına dönüştür
    ogrenci_listesi = []
    for ogr_ad, dersler in konsolide_veriler.items():
        if not dersler:
            continue
        genel_ort = sum(dersler.values()) / len(dersler)
        ogrenci_listesi.append({
            "ogrenci_adi": ogr_ad,
            "notlar": dersler,
            "ortalama": round(genel_ort, 2)
        })
    return sorted(ogrenci_listesi, key=lambda x: x['ogrenci_adi'])


def xlsx_oku(dosya_yolu):
    """Modern .xlsx uzantılı basit veya çoklu sekme dosyalarını okur."""
    wb = openpyxl.load_workbook(dosya_yolu, data_only=True)
    
    # EĞER TEK SEKME VARSA: Eski basit sistem devrede
    if len(wb.sheetnames) == 1:
        sheet = wb.active
        ogrenci_listesi = []
        dersler = []
        BASLANGIC_SUTUNU = 2
        BASLIK_SATIRI = 5
        
        for col in range(BASLANGIC_SUTUNU, sheet.max_column + 1):
            ders_adi = sheet.cell(row=BASLIK_SATIRI, column=col).value
            if ders_adi:
                dersler.append(ders_adi)
                
        for row in range(6, sheet.max_row + 1):
            ogrenci_girdi = sheet.cell(row=row, column=1).value
            if ogrenci_girdi is not None:
                ogrenci_adi = str(ogrenci_girdi).replace("Öğrenci Adı:", "").strip().upper()
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
                            continue
                
                ortalama = toplam_not / ders_sayisi if ders_sayisi > 0 else 0
                ogrenci_listesi.append({
                    "ogrenci_adi": ogrenci_adi,
                    "notlar": notlar,
                    "ortalama": round(ortalama, 2)
                })
        return sorted(ogrenci_listesi, key=lambda x: x['ogrenci_adi'])

    # EĞER ÇOKLU SEKME VARSA: Modern çok sekmeli kazanım ölçeği sistemi devrede
    else:
        konsolide_veriler = {}
        ders_haritasi = {
            "T": "TÜRKÇE", "M": "MATEMATİK", "HB": "HAYAT BİLGİSİ",
            "BEO": "BEDEN EĞİTİMİ VE OYUN", "MÜ": "MÜZİK", "GS": "GÖRSEL SANATLAR"
        }

        for sheet_name in wb.sheetnames:
            if "bilgi" in sheet_name.lower():
                continue
                
            sheet = wb[sheet_name]
            temiz_kod = re.sub(r'[^a-zA-ZğüşıöçĞÜŞİÖÇ]', '', sheet_name).upper().strip()
            ders_adi = ders_haritasi.get(temiz_kod, f"DERS ({sheet_name})")
            
            baslik_satiri = 4
            for r in range(1, 6):
                h_val = str(sheet.cell(row=r, column=3).value or '').upper()
                if "ADI" in h_val or "SOYADI" in h_val:
                    baslik_satiri = r
                    break
                    
            puan_sutunlari = []
            for col in range(4, sheet.max_column + 1):
                b_degeri = str(sheet.cell(row=baslik_satiri, column=col).value or '').upper()
                if "ORTALAMA" in b_degeri or "SONUÇ" in b_degeri or b_degeri == "":
                    continue
                puan_sutunlari.append(col)
                
            for r in range(baslik_satiri + 1, sheet.max_row + 1):
                ogrenci_adi = sheet.cell(row=r, column=3).value
                if not ogrenci_adi or any(k in str(ogrenci_adi).upper() for k in ["TOPLAM", "ORTALAMA", "SINIF"]):
                    continue
                    
                ogrenci_adi = str(ogrenci_adi).strip().upper()
                toplam_puan = 0
                gecerli_puan_sayisi = 0
                
                for col in puan_sutunlari:
                    hucre_degeri = sheet.cell(row=r, column=col).value
                    if hucre_degeri is not None:
                        try:
                            puan_float = float(hucre_degeri)
                            toplam_puan += puan_float
                            gecerli_puan_sayisi += 1
                        except ValueError:
                            continue
                
                if gecerli_puan_sayisi > 0:
                    ham_ortalama = toplam_puan / gecerli_puan_sayisi
                    yuzluk_not = (ham_ortalama / 4.0) * 100 if ham_ortalama <= 4.0 else ham_ortalama
                    
                    if ogrenci_adi not in konsolide_veriler:
                        konsolide_veriler[ogrenci_adi] = {}
                    konsolide_veriler[ogrenci_adi][ders_adi] = round(yuzluk_not, 2)

        ogrenci_listesi = []
        for ogr_ad, dersler in konsolide_veriler.items():
            if not dersler:
                continue
            genel_ort = sum(dersler.values()) / len(dersler)
            ogrenci_listesi.append({
                "ogrenci_adi": ogr_ad,
                "notlar": dersler,
                "ortalama": round(genel_ort, 2)
            })
        return sorted(ogrenci_listesi, key=lambda x: x['ogrenci_adi'])


def pdf_oku(dosya_yolu):
    """Standart e-Okul PDF karnelerini okur."""
    ogrenci_listesi = []
    DERS_ADI_IDX = 0
    NOT_IDX = 2
    
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
    """Dosya uzantısına göre yönlendirme yapan ana orchestrator."""
    uzanti = os.path.splitext(dosya_yolu)[1].lower()
    if uzanti == '.xlsx':
        return xlsx_oku(dosya_yolu)
    elif uzanti == '.xls':
        return xls_oku(dosya_yolu)
    elif uzanti == '.pdf':
        return pdf_oku(dosya_yolu)
    else:
        raise ValueError("Desteklenmeyen dosya formatı!")