# 🚁 Drone Filo Teslimat Simülasyonu

Bu proje, dinamik kısıtların olduğu ortamlarda bir drone filosunun teslimat görevlerini en verimli şekilde gerçekleştirmesini amaçlayan bir rota planlama sistemidir. Sistem; enerji sınırları, teslimat öncelikleri, zaman pencereleri ve uçuşa yasak bölgeler gibi çeşitli değişkenleri dikkate alarak hem lokal (A*) hem global (Genetik Algoritma) düzeyde optimizasyon yapar.

![Drone Teslimat Rotaları Görünümü](images/drone_routes.png)

## 🧠 Kullanılan Yöntemler

- **A* Algoritması:** Her bir teslimat için en uygun rotayı belirler.
- **Genetik Algoritma:** Drone-görev eşleştirmelerini sistem genelinde optimize eder.

Tüm algoritmalar, batarya sınırlamaları, zaman kısıtları ve uçuşa yasak bölgeler gibi gerçek dünya kısıtlarını dikkate alarak çalışır.

## 🗂️ Proje Yapısı

```
.
├── main.py               # Simülasyonun ana kontrol dosyası
├── data_generator.py     # Drone, teslimat ve yasak bölge verisi üretimi
├── delivery_planner.py   # A* ve Genetik Algoritma uygulaması
├── visualizer.py         # Harita üzerinde görselleştirme
├── randomdata.json       # Rastgele oluşturulan senaryo verileri
└── README.md             # Proje açıklamaları (bu dosya)
```

## ⚙️ Kurulum ve Çalıştırma

1. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Simülasyonu çalıştırın:
```bash
python main.py
```

Simülasyon çalıştığında, oluşturulan senaryo `randomdata.json` dosyasına kaydedilir. Drone rotaları ve teslimatlar terminalde ve görselleştirme ekranında gösterilir.

## 📊 Çıktı Açıklamaları

### Rota ve Teslimat Görselleştirmesi
- Her drone farklı bir renk ile gösterilir.
- Başlangıç noktaları üçgen ikonlarla, teslimat hedefleri daire ikonlarla ifade edilir.
- Uçuşa yasak bölgeler harita üzerinde belirtilir.

### Batarya ve Zaman Uyumları
- Rotalar sadece mesafeye göre değil, batarya seviyesi ve zaman pencereleri göz önüne alınarak belirlenir.
- Bataryası yetmeyen veya zaman uyumu olmayan görevler atlanır.

## 🔧 Sistem Mimarisi

### 1. Veri Üretimi
- Her drone için farklı kapasite, hız ve batarya verisi rastgele üretilir.
- Teslimatlar ağırlık, öncelik ve zaman penceresi gibi özelliklerle oluşturulur.
- Uçuşa yasak bölgeler belirli zaman aralıklarında aktiftir.

### 2. Rota Ağı (Graf)
- Her nokta bir düğüm, olası yollar bir kenar olarak modellenir.
- Rota maliyetleri: mesafe + ağırlık + yasak bölge etkisi.

### 3. A* ile Rota Belirleme
- Enerji tüketimi, batarya durumu ve zaman uyumu dikkate alınır.
- Geçersiz rotalar (örneğin yasak bölgeyle kesişen) elenir.

### 4. Genetik Algoritma ile Görev Dağılımı
- Geçerli görev dizileri popülasyon olarak değerlendirilir.
- Uygunluk: teslimat sayısı, enerji kullanımı, kural uyumu.
- Çaprazlama & mutasyon ile yeni çözümler üretilir.

### 5. Teslimat Planlaması
- Her teslimat için en uygun drone seçilir.
- Zaman çakışmaları ve batarya uygunluğu kontrol edilir.
- Başarılı atama sonrası drone’un bataryası güncellenir.

### 6. Görselleştirme
- Başlangıç noktaları, hedefler ve rotalar görsel olarak çizilir.
- Uçuşa yasak bölgeler harita üzerinde vurgulanır.

## 🔍 Önemli Notlar

- Veriler her çalıştırmada değişkendir.
- Uçuşa yasak bölgeler belirli saatlerde aktiftir.
- Batarya veya zaman uyumsuzluğu olan görevler atlanır.
- Görevler zaman çakışmalarına göre planlanır.

## 📁 Görseller

> Görseller `images/` klasörüne yerleştirilmelidir:

- `drone_routes.png`: Genel teslimat rotaları
- `map.png`: Detaylı görev ve bölge görünümü
- `timeline.png`: Enerji kullanımı ve zamanlama analizi

---

👨‍💻 **Geliştirici Notu:**  
Bu proje, dağıtım algoritmalarının gerçek dünya senaryolarında test edilmesi ve iyileştirilmesi için geliştirilmiştir.

