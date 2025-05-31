import heapq
import math
import json

def heuristic(pos1, pos2): #İki nokta arasındaki net mesafeyi hesaplar. Bu mesafeyi hesaplattırmamızın sebebi, en uygun rota belirleme işleminde tahmini maliyet hesabını yaptırmaktır.
    return math.dist(pos1, pos2)

def rotaBelirle(gelinen_yol, mevcut_node): #Başlangıçtan hedefe kadar olan yolu geri takip ederek oluşturur.
    rota = [mevcut_node] #Yol listesi, hedef node ile başlar.
    while mevcut_node in gelinen_yol:
        mevcut_node = gelinen_yol[mevcut_node]
        rota.append(mevcut_node) #Önceki nodelara geri dönülerek rota çıkarılır.
    return rota[::-1] #Rota ters çevrilerek başlangıçtan hedefe olacak şekilde döndürülür.

#A* ALGORİTMASI ÇALIŞMA MANTIĞI

#A* algoritması, drone_index ile seçilen bir dronenun, belirlenen hedef teslimat noktasına kadar olan en uygun yani en az maliyetli rotayı bulmasını sağlar.
#Rota sadece mesafeye göre değil; drone’un kalan bataryası, taşıyabileceği maksimum ağırlık ve uçuş yasağı olan bölgelerin etkisiyle birlikte dinamik olarak belirlenir.
#Öncelik kuyruğu (min-heap) yapısı ile başlatılan algoritma, her adımda en düşük toplam maliyetli düğümü işler.
#Bu şekilde hem düğümler hem de aralarındaki edgeler sürekli en mantıklı olanlar üzerinden seçilerek ilerlenir.

#A* algoritması sadece hedefe ulaşmayı değil, bu yolculuk sırasında geçilen düğümleri de kayıt altına alır.
#Bu sayede elde edilen rotanın hangi adımlardan oluştuğu belirlenebilir ve bir rota çizimi yapılabilmektedir.
#Sonsuz döngüye girilmemesi ve daha önce ziyaret edilen düğümlerin tekrar işlenmemesi için bir geçmiş kontrolü yapılır.

#Bu sistemde iki temel skor yapısı kullanılır: g_score ve f_score.
#g_score, başlangıç noktasından o ana kadar kat edilen toplam gerçek maliyeti temsil eder.
#f_score ise bu g_score üzerine, mevcut düğümden hedefe direkt gidiş maliyeti (heuristic) ekleyerek hesaplanır.
#f_score = g_score + heuristic

#g_score ve f_score başta sonsuz (inf) olarak tanımlanır. Bunun sebebi, algoritmanın başlangıçta en iyi yolları bilmemesidir.
#İşlem ilerledikçe bu değerler güncellenir ve algoritma her zaman en düşük f_score değerine sahip düğümü önce seçerek doğru yolda kalmaya çalışır.
#Bu yapı sayesinde A*, en düşük toplam maliyetli ve en mantıklı rotayı bulma eğilimindedir.


def a_star(graf, baslangic, hedef, node_konumlari, drone_index):
    drone_batarya = drones[drone_index]["battery"] #İlgili dronenun toplam bataryası

    open_list = []  #Öncelik kuyruğu (min-heap). Aslında en uygun rotayı çıkartana dek henüz ziyaret edilmemiş nodeları tutmaktayız.
    heapq.heappush(open_list, (0, baslangic, drone_batarya))

    gelinen_yol = {}  #Hangi node hangi nodedan geldi? Yani geldiğimiz yolu tutuyoruz.
    g_score = {node: float("inf") for node in graf} #Başlangıçtan hedef nodea kadar olan gerçek maliyet
    g_score[baslangic] = 0

    f_score = {node: float("inf") for node in graf} #g_score + heuristic (toplam tahmini maliyet)
    f_score[baslangic] = heuristic(node_konumlari[baslangic], node_konumlari[hedef])

    gecmis_yol = set() #Daha önce geçtiğimiz yollar. Bunu tutmamızın sebebi, geçtiğimiz yoldan tekrar geçmemeye çalışıyoruz. Çünkü bir yerde en düşük maliyetli yol geçtiğimiz
                       #yol çıkarsa devamlı bir döngüye girmiş oluruz. Bu yüzden geçilen yollar kapatılır.

    while open_list:
        _, mevcut_node, mevcut_batarya = heapq.heappop(open_list)

        if mevcut_node == hedef:
            return rotaBelirle(gelinen_yol, mevcut_node)

        if mevcut_node in gecmis_yol: #Tam bu noktada döngü, geçtiğimiz yola denk gelirse hiç işleme koyulmadan devam ettirir.
            continue
        gecmis_yol.add(mevcut_node)

        for komsu_node, maliyet, enerji in graf.get(mevcut_node, []):
            if mevcut_batarya < enerji: #Bu noktada gidilecek kenarlar için batarya yetmiyorsa tekrar döngü başa döner. Ta ki en uygun rota bulunana dek.
                continue

            yeni_maliyet = g_score[mevcut_node] + maliyet
            kalan_batarya = mevcut_batarya - enerji
            #Bu kısımda ilgili node üzerinden gidilen her edge değerlendirilir. Her seferinde maliyeti daha az çıkan bir edge denk gelirse buradaki şartın içinde yeni kenar olarak güncellenir.
            if yeni_maliyet < g_score.get(komsu_node, float("inf")):
                gelinen_yol[komsu_node] = mevcut_node
                g_score[komsu_node] = yeni_maliyet
                tahmini_heuristic = heuristic(node_konumlari[komsu_node], node_konumlari[hedef])
                f_score[komsu_node] = yeni_maliyet + tahmini_heuristic
                heapq.heappush(open_list, (f_score[komsu_node], komsu_node, kalan_batarya))

    return None #Eğer tüm kontrol ve işlemlere rağmen bir rota bulunamamışsa ve artık gidecek edge de kalmamışsa none döner. Yani rota yoktur.

with open("randomdata.json", "r") as dosya: #Veriler okunur.
    veri = json.load(dosya)

drones = veri["drones"]
deliveries = veri["deliveries"]
no_fly_zones = veri["no_fly_zones"]