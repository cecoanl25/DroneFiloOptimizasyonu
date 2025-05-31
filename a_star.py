import heapq
import math
from DroneFiloOptimizasyonu.graph import get_dynamic_graph_for, yazdir_dynamic_graph
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

# #Burada bir drone ve o drone için bir teslimat noktası belirlenir.
# drone_index = 1
# target_delivery_index = 2
# baslangic = drone_index #Başlangıç düğümü dronenun bulunduğu konum olarak ayarlanır.
# hedef = target_delivery_index + len(drones) # Hedef düğüm teslimat nodedu (dronelar başta olduğu için index kaydırılır. Yani işin temelinde teslimatlar, id karışıklığı yaşanmaması için droneların toplamından sonra id alır.)

# node_konumlari = {} # Tüm düğüm noktalarının (drone + teslimat) pozisyon bilgileri sözlük olarak oluşturulur.
# for i, drone in enumerate(drones):
#     node_konumlari[i] = tuple(drone["start_pos"])  #Droneların başlangıç pozisyonları atanır.
# for i, teslimat in enumerate(deliveries):
#     node_konumlari[i + len(drones)] = tuple(teslimat["pos"]) #Teslimat noktalarının konumları atanır. (index kaydırılarak)

# graf = get_dynamic_graph_for(drone_index, target_delivery_index) #Seçilen drone ve hedef teslimat noktasına özel olarak dinamik graf yapısı oluşturulur
# yazdir_dynamic_graph(graf) #Oluşturulan grafın terminal tarafına yazdırma fonksiyonu çağrılır.

# rota = a_star(graf, baslangic, hedef, node_konumlari, drone_index) #A* algoritması çağrılır ve elde edilen rota değişkenine atanır.

# print("\nRota:", end=" ") #Rota bilgisi terminalde yazdırılır.
# if rota is None:
#     print("Rota Bulunamadı")  #Eğer hedefe giden geçerli bir rota bulunamazsa bilgi verilir.
# else:
#     for node in rota:
#         if node < len(drones): #Node bir drone ise
#             print(f"D{drones[node]['id']}", end=" → ")
#         else:  #Node bir teslimat noktası ise
#             teslimat_index = node - len(drones)
#             print(f"T{deliveries[teslimat_index]['id']}", end=" → ")
#     print("End") #Rota yazdırımı tamamlandığında (Buradaki rota yazdırma işleminde okunaklılık sağlanmıştır.)

#     #Rota boyunca toplam maliyet ve enerji tüketimi hesaplanır.
#     toplam_maliyet = 0
#     kalan_batarya = drones[drone_index]["battery"]

#     for i in range(len(rota) - 1):
#         mevcut_node = rota[i]
#         sonraki_node = rota[i + 1]

#         for komsu_node, maliyet, enerji in graf[mevcut_node]:
#             if komsu_node == sonraki_node:
#                 toplam_maliyet += maliyet #Rota üzerindeki kenar maliyetleri toplanır.
#                 kalan_batarya -= enerji #Harcanan enerji toplamdan düşülür.
#                 break

#     #Sonuçlar terminale yazdırılır.
#     print("Toplam rota maliyeti:", round(toplam_maliyet, 2))
#     print("Drone batarya kapasitesi:", round(drones[drone_index]["battery"]), "mAh")
#     print("Harcanan batarya:", round(drones[drone_index]["battery"] - kalan_batarya, 2), "mAh")
#     print("Kalan batarya:", round(kalan_batarya, 2), "mAh")

# #Elde edilen rota ve düğüm koordinatları, görselleştirme işlemi için global olarak tutulur.
# rota_sonucu = rota
# node_konumlari_sonucu = node_konumlari