# internship

Bu proje, MEB benzeri karne verilerini CSV olarak alıp her öğrenci için seçilen özellikleri kontrol eden ve sonuçları yapay zeka destekli bir dille özetleyen basit bir prototiptir.

## Özellikler
- CSV dosyasından öğrenci verisi okur
- İstenilen alanları seçerek eksik verileri tespit eder
- Tam olanlar için övgü mesajı üretir
- Eksik olanlar için iyimser uyarı mesajı üretir
- Sonuçları JSON dosyasına kaydeder

## Kullanım
1. Örnek dosyayı inceleyin: sample_students.csv
2. Aşağıdaki komutla raporu üretin:

```bash
python main.py --input sample_students.csv --features matematik,fen,ingilizce,devamsizlik,davranis --output report.json
```

3. Oluşan report.json dosyasını inceleyin.

## Test

```bash
python -m unittest discover -s tests -v
```
