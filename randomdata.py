import random
from shapely import Point, Polygon
from datalists import Drone, DeliveryPoints, NoFlyZones
from datetime import datetime, timedelta
import json

def randomZaman():
    saat = random.randint(10, 17)
    dakika = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
    baslangic_zamani = datetime(2025, 1, 1, saat, dakika)
    görev_süresi = random.randint(1, 10)  # 1 ila 10 dakika arası

    bitis_zamani = baslangic_zamani + timedelta(minutes=görev_süresi)
    return (baslangic_zamani.strftime("%H:%M"), bitis_zamani.strftime("%H:%M"))



def randomCoordinate(): #Dörtgen şeklinde rastgele bir bölge tanımlar. Rastgele x,y değerlerine rastgele genişlik, yükseklik değerleri ekleyerek dörtgen oluşturur.
    genislik = random.randint(10, 30)
    yukseklik = random.randint(10, 30)
    x = random.randint(0, 70)
    y = random.randint(0, 70)
    kose1 = (x, y)
    kose2 = (x + genislik, y)
    kose3 = (x + genislik, y + yukseklik)
    kose4 = (x, y + yukseklik)

    return [kose1, kose2, kose3, kose4]

def yasakliBolgeler(adet): #Rastgele yasaklı bölge oluşturan fonksiyon
    yasakListe = []
    for i in range(adet):
        yasak_listesi = NoFlyZones(
            id = i,
            coordinates = randomCoordinate(),
            active_time = randomZaman()
        )
        yasakListe.append(yasak_listesi)
    return yasakListe

def droneListesi(adet, no_fly_listesi): #Rastgele drone oluşturan fonksiyon
    droneListe = []
    sayac = 0

    while len(droneListe) < adet: #İstenen adet kadar fonksiyon döner
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        nokta = Point(x, y)

        icindemi = False #Buradaki for döngüsünde rastgele üretilen dronenun, üretilen yasaklı bölge içine hatalı bir şekilde düşmemesi için kontrolü yapılır.
        for zone in no_fly_listesi:
            poligon = Polygon(zone.coordinates)
            if poligon.contains(nokta):
                icindemi = True
                break

        if icindemi: #Eğer oluşturulan drone, yasaklı bölgeye temas ediyorsa döngü tekrar başlar ve yasaklı bölgeden çıkana kadar rastgele koordinatlarda drone oluşturma devam eder.
            continue

        drone_listesi = Drone(
            id=sayac,
            max_weight=random.uniform(5.0, 10.0),
            battery=random.randint(5000, 10000),
            speed=random.uniform(0.5, 2.0),
            start_pos=(x, y)
        )
        droneListe.append(drone_listesi)
        sayac += 1

    return droneListe


def teslimatNoktalari(adet, no_fly_listesi): #Rastgele teslimat noktası oluşturan fonksiyon
    teslimatListe = []
    sayac = 0

    while len(teslimatListe) < adet: #İstenen adet kadar döngü devam eder.
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        nokta = Point(x, y)

        icindemi = False #Buradaki for döngüsünde rastgele üretilen teslimat noktalarının, üretilen yasaklı bölge içine hatalı bir şekilde düşmemesi için kontrolü yapılır.
        for zone in no_fly_listesi:
            poligon = Polygon(zone.coordinates)
            if poligon.contains(nokta):
                icindemi = True
                break

        if icindemi: #Eğer oluşturulan teslimat noktası, yasaklı bölgeye temas ediyorsa döngü tekrar başlar ve yasaklı bölgeden çıkana kadar rastgele
            #koordinatlarda uygun teslimat noktası oluşturma devam eder.
            continue

        teslimat_listesi = DeliveryPoints(
            id=sayac,
            pos=(x, y),
            weight=random.uniform(4.0, 8.0),
            priority=random.choice([1, 2, 3, 4, 5]),
            time_window=randomZaman()
        )
        teslimatListe.append(teslimat_listesi)
        sayac += 1

    return teslimatListe


def json_veri_kayit(drone_adet, teslimat_adet, yasak_adet): #Oluşturulan 3 bileşen de json formatındaki dosyaya kaydedilir.
    yasak_listesi = yasakliBolgeler(yasak_adet) #Önce yasaklı bölgeler oluşturulur. Çünkü diğer 2 bileşenin yasaklı bölgeye düşüp düşmediğinin kontrolü gereklidir.
    drone_listesi = droneListesi(drone_adet, yasak_listesi)
    teslimat_listesi = teslimatNoktalari(teslimat_adet, yasak_listesi)

    data = {
        "drones": [d.__dict__ for d in drone_listesi],
        "deliveries": [t.__dict__ for t in teslimat_listesi],
        "no_fly_zones": [z.__dict__ for z in yasak_listesi]
    }

    with open("randomdata.json", "w") as dosya:
        json.dump(data, dosya, indent=4)

json_veri_kayit(5,20,2) # 5 drone, 20 teslimat noktası ve 2 yasaklı bölge senaryosu
