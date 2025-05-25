import json
import math
from shapely.geometry import LineString, Polygon


with open("randomdata.json", "r") as dosya: #randomdata.json dosyasından verileri okur
    veri = json.load(dosya)

drones = veri["drones"]
deliveries = veri["deliveries"]
no_fly_zones = veri["no_fly_zones"]

def get_dynamic_graph_for(drone_index: int, target_delivery_index: int): #Belirli bir drone ve hedef teslimat için dinamik bir graf olusturur.
    hedef_agirlik = deliveries[target_delivery_index]["weight"]
    hedef_oncelik = deliveries[target_delivery_index]["priority"]
    drone_max_weight = drones[drone_index]["max_weight"]
    drone_battery = drones[drone_index]["battery"]

    enerji_katsayi = 10  #Batarya harcama sistemi için 1 birim mesafe başına 10 birim enerji tüketimi şeklinde uygulandı.

    if hedef_agirlik > drone_max_weight: # Eğer teslimat, dronenun alabileceği maksimum ağırlığı aşıyorsa uyarı verilir.
        print(f"UYARI: Drone {drone_index} teslimat {target_delivery_index} paketini taşıyamaz! ({hedef_agirlik:.2f} kg > {drone_max_weight:.2f} kg)")
        return {}

    dynamic_graf = {}

    dynamic_graf[drone_index] = [] #Başlangıç olarak dronenun bulunduğu düğüm eklenir

    for j, delivery in enumerate(deliveries): #Dronedan her teslimat noktasına kenarları oluştur. Bu, droneların başlangıç noktasından itibaren ilk hareket için gereklidir.
        delivery_node = j + len(drones) #Teslimat düğüm numarası

        line = LineString([tuple(drones[drone_index]["start_pos"]), tuple(delivery["pos"])])  #Dronenun pozisyonundan teslimat noktasına doğru çizgi (kenar) çizilir
        no_fly_penalty = 0

        for zone in no_fly_zones: #Çizgi yasaklı bölgelerden geçiyorsa 1000 birim ceza puanı eklenir
            polygon = Polygon(zone["coordinates"])
            if line.intersects(polygon):
                no_fly_penalty = 1000


        #Mesafe, maliyet ve enerji hesabı yapılır
        mesafe = math.dist(drones[drone_index]["start_pos"], delivery["pos"]) 
        maliyet = mesafe * hedef_agirlik + (hedef_oncelik * 100) + no_fly_penalty
        enerji = mesafe * hedef_agirlik * enerji_katsayi

        if enerji > drone_battery: #Gidilecek düğüme batarya yetmiyorsa bu edge dahil edilmez.
            continue


        dynamic_graf[drone_index].append((delivery_node, maliyet, enerji)) #Geçerli kenar grafiğe eklenir

    for i, d1 in enumerate(deliveries):  #Teslimat noktaları arasında kenarlar oluştur. Bu da belirli bir rota üzerinde ilerlenildiğinde teslimat noktalarının birbiri ile bağlantısı belirlenir.
        node_i = i + len(drones)
        dynamic_graf.setdefault(node_i, [])

        for j, d2 in enumerate(deliveries):
            if i == j:
                continue

            node_j = j + len(drones)

            line = LineString([tuple(d1["pos"]), tuple(d2["pos"])])
            no_fly_penalty = 0

            for zone in no_fly_zones: #Eğer çizilen yol, yasaklı bölgeye temas ediyorsa ceza puanı uygulanır.
                polygon = Polygon(zone["coordinates"])
                if line.intersects(polygon):
                    no_fly_penalty = 1000
            #İlgili edge için mesafe, maliyet, enerji hesaplamaları yapılır
            mesafe = math.dist(d1["pos"], d2["pos"])
            maliyet = mesafe * hedef_agirlik + (hedef_oncelik * 100) + no_fly_penalty
            enerji = mesafe * hedef_agirlik * enerji_katsayi 

            dynamic_graf[node_i].append((node_j, maliyet, enerji)) #Bağlantı kurulur

    return dynamic_graf

def yazdir_dynamic_graph(graf): #Drone->Teslimat ve Teslimat->Teslimat yolları için maliyet ve harcanan enerji işlemlerinin terminalde yazımını yapan fonksiyon.
    for node_index, komsular in graf.items():
        if node_index < len(drones):
            for hedef, maliyet, enerji in komsular:
                teslimat_index = hedef - len(drones)
                print(f"Drone {drones[node_index]['id']} → Teslimat {deliveries[teslimat_index]['id']} : Maliyet = {maliyet:.2f} : Harcanan Enerji = {enerji:.2f}")
        else:
            kaynak_index = node_index - len(drones)
            for hedef, maliyet, enerji in komsular:
                hedef_index = hedef - len(drones)
                print(f"Teslimat {deliveries[kaynak_index]['id']} → Teslimat {deliveries[hedef_index]['id']} : Maliyet = {maliyet:.2f} : Harcanan Enerji = {enerji:.2f}")

#GRAF ÇALIŞMA ŞEKLİ

#Bu graf yapısının çalışma mantığı dinamikliktir. Yani önce teslimatı yapacak olan drone ve o dronenun yapacağı teslimat belirlenir.
#Bu ikili belirlendikten sonra oluşturulan graf yapısında ilgili dronenun ve o dronenun yapacağı teslimat bilgilerine göre tüm edgeler (kenarlar) yeniden hesaplanır.
#Dronenun sahip olduğu batarya kapasitesine ve taşıdığı ağırlığa göre tüm noktalar arasındaki bağlantıların maliyetleri dinamik olarak yeniden hesaplanır.
#Bu konseptte bir hesabı yapmamın sebebi, A* algoritmasında en az maliyetli rotanın belirleme işleminde daha rahat ve düzgün bir sistem hazırlayabilmektir.