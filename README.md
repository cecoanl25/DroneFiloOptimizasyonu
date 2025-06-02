
# 🚁 Drone Filo Teslimat Simülasyonu

Bu proje, dinamik kısıtlar altında birden fazla drone’un teslimat görevlerini en uygun şekilde gerçekleştirmesini amaçlar. Sistem, **zaman pencereleri**, **batarya sınırlamaları**, **öncelikler** ve **uçuşa yasak bölgeler** gibi gerçekçi kısıtları dikkate alır. Simülasyon hem **A\*** algoritması hem de **Genetik Algoritma** (GA) ile gerçekleştirilir. 

## 🎯 Temel Özellikler

- 🧠 **A\***: Her teslimat için en uygun rotayı belirler. Zaman, enerji ve kısıtlar göz önüne alınır.
- 🧬 **Genetik Algoritma**: Tüm teslimatları global düzeyde en iyi şekilde dağıtır.
- ⛔ **No-Fly Zones**: Belirli saatlerde aktif olan bölgeler, rotaların oluşumunu etkiler.
- ⏱️ **Gerçek Zamanlı Simülasyon**: Teslimatlar zaman akışına göre animasyonla gösterilir.
- 🔋 **Enerji Takibi**: Drone’ların kalan batarya seviyeleri hesaplanır ve görsel olarak gösterilir.

## 📁 Proje Yapısı

```
.
├── ga_gorsel.py            # GA çözümünü görselleştirir (zamanlı teslimat çizimi)
├── gorsel.py               # A* çözümünü zaman akışına göre animasyonla gösterir
├── graph.py                # Uçuş grafı ve yasaklı bölge kesişim hesaplamaları
├── a_star.py               # A* algoritması uygulaması
├── multi_a.py              # A* temelli görev atama motoru
├── genetic_algorithm.py    # Genetik algoritma sınıfı ve çözüm üretimi
├── kıyas.py                # A* vs GA karşılaştırması ve süre analizi
├── randomdata.py           # Rastgele senaryo üretimi (drone, görev, bölge)
├── datalists.py            # Veri sınıfları (Drone, Teslimat, Yasaklı Bölge)
├── randomdata.json         # Senaryo verisi (dinamik üretilir)
└── README.md               # Bu dosya
```

## ▶️ Kurulum ve Çalıştırma
1. Senaryo verisi oluşturmak için:
```bash
python randomdata.py
```

2. Genetik Algoritma + görselleştirme çalıştırmak için:

```bash
python ga_gorsel.py
```

3. A* + görselleştirme çalıştırmak için:

```bash
python gorsel.py
```

## 🧪 Simülasyon Açıklamaları

### 🎥 Gerçek Zamanlı Görsel Akış

- Simülasyon saati 10:00’da başlar.
- Teslimatlar yalnızca kendi zaman penceresinde çizilir.
- Yasaklı bölgeler **aktif olduklarında kırmızı**, **pasif olduklarında gri** olarak çizilir.

### 🛰️ Drone – Teslimat Atamaları

- Her teslimat için ağırlık, zaman ve enerji uygunluğu kontrol edilir.
- Zaman penceresiyle çakışan görevler atlanır.
- Enerji yetersizse görev reddedilir.
- Genetik algoritma, teslimatların maksimum verimle dağılımını sağlar.

## 📈 Özet Çıktılar

Her iki algoritma sonunda:

- Toplam teslimat sayısı
- Tamamlanma oranı
- Toplam ve ortalama enerji tüketimi
- Acil teslimatların durumu

metrikleri yazdırılır.

## 🗺️ Görseller 
#### A* Algoritması:
- ![image](https://github.com/user-attachments/assets/8731d90c-2959-4921-9986-9ef6c1eb1225)
#### Genetik Algoritması:
- ![image](https://github.com/user-attachments/assets/aaf93709-2e79-4465-8746-ba000968f511)

---

📌 **Not:**  
Veriler her çalıştırmada yeniden üretilir. Aynı sonucu elde etmek için `randomdata.json` sabitlenmelidir. 
Farklı veri setlerini randomdata.py dosyasını çalıştırarak elde edebilirsiniz.
Simülasyon animasyonu matplotlib ile çalışır, interaktif pencere üzerinden izlenebilir.

---

👨‍💻 **Hazırlayan:**  
Akıllı dağıtım sistemleri üzerinde çalışan bu proje, gerçek dünya senaryolarına uygun simülasyon ortamı oluşturmayı hedefler.
