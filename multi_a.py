import json
from DroneFiloOptimizasyonu.graph import get_dynamic_graph_for
from a_star import a_star
from rich import print
import math
import heapq 

def hesapla_enerji(rota, node_konumlari, agirlik=0, katsayi=10):
    enerji = 0
    for i in range(len(rota) - 1):
        baslangic = node_konumlari[rota[i]]
        hedef = node_konumlari[rota[i + 1]]
        mesafe = math.dist(baslangic, hedef)
        enerji += mesafe * (1 + agirlik / 10) * katsayi
    return enerji

with open("randomdata.json", "r") as dosya:
    veri = json.load(dosya)

drones = veri["drones"]
deliveries = veri["deliveries"]

drone_rotalari_sonuc = {str(i): [] for i in range(len(drones))}
node_konumlari = {}

for i, d in enumerate(drones):
    node_konumlari[i] = tuple(d["start_pos"])
for i, t in enumerate(deliveries):
    node_konumlari[i + len(drones)] = tuple(t["pos"])

kalan_batarya = {i: drone["battery"] for i, drone in enumerate(drones)}
tamamlanmamis_teslimatlar = set(i for i in range(len(deliveries)))

teslimat_heap = [(-t["priority"], i) for i, t in enumerate(deliveries)]
heapq.heapify(teslimat_heap)

while teslimat_heap:
    _, teslimat_index = heapq.heappop(teslimat_heap)
    if teslimat_index not in tamamlanmamis_teslimatlar:
        continue

    atandi = False
    en_iyi_maliyet = float("inf")
    en_iyi_drone = None
    en_iyi_gidis = None
    en_iyi_donus = None
    en_iyi_enerji = None

    print(f"\n[bold]---------- TESLİMAT {teslimat_index} İÇİN UYGUN DRONE ATAMASI ----------")

    for drone_index, drone in enumerate(drones):
        print(f"Drone {drone_index}:")

        if deliveries[teslimat_index]["weight"] > drone["max_weight"]:
            print(f"[red] Reddedildi: Ağırlık {deliveries[teslimat_index]['weight']} > kapasite {drone['max_weight']}")
            continue

        graph_gidis = get_dynamic_graph_for(drone_index, teslimat_index)
        hedef_id = teslimat_index + len(drones)

        rota_gidis = a_star(graph_gidis, drone_index, hedef_id, node_konumlari, drone_index)
        if rota_gidis is None:
            print("[red] Reddedildi: A* rota bulunamadı.")
            continue

        agirlik = deliveries[teslimat_index]["weight"]
        enerji_gidis = hesapla_enerji(rota_gidis, node_konumlari, agirlik)

        rota_donus = list(reversed(rota_gidis))
        enerji_donus = hesapla_enerji(rota_donus, node_konumlari, agirlik=0)

        toplam_enerji = enerji_gidis + enerji_donus

        if toplam_enerji > kalan_batarya[drone_index]:
            print(f"[red] Reddedildi: Enerji yetersiz. Gerekli: {round(toplam_enerji, 2)} mAh, Kalan: {round(kalan_batarya[drone_index], 2)} mAh")
            continue

        toplam_maliyet = 0
        for i in range(len(rota_gidis) - 1):
            kaynak = rota_gidis[i]
            hedef = rota_gidis[i + 1]
            for komsu, maliyet, _ in graph_gidis.get(kaynak, []):
                if komsu == hedef:
                    toplam_maliyet += maliyet
                    break

        print(f"[blue] Kabul adayı: Maliyet = {round(toplam_maliyet, 2)}, Enerji = {round(toplam_enerji, 2)} mAh")

        if toplam_maliyet < en_iyi_maliyet:
            en_iyi_maliyet = toplam_maliyet
            en_iyi_drone = drone_index
            en_iyi_gidis = rota_gidis
            en_iyi_donus = rota_donus
            en_iyi_enerji = toplam_enerji

    if en_iyi_drone is not None:
        drone_rotalari_sonuc[str(en_iyi_drone)].append(en_iyi_gidis)
        drone_rotalari_sonuc[str(en_iyi_drone)].append(en_iyi_donus)
        kalan_batarya[en_iyi_drone] -= en_iyi_enerji
        tamamlanmamis_teslimatlar.remove(teslimat_index)
        print(f"[green][bold] Teslimat {teslimat_index}, Drone {en_iyi_drone} tarafından üstlenildi.")
        print("[cyan][bold] Rota:", end=" ")
        for node in en_iyi_gidis:
            if node < len(drones):
                print(f"D{drones[node]['id']}", end=" → ")
            else:
                teslimat_index = node - len(drones)
                print(f"T{deliveries[teslimat_index]['id']}", end=" → ")
        print("End")

        yuzde = kalan_batarya[en_iyi_drone] / drones[en_iyi_drone]["battery"]
        if yuzde >= 0.50:
            renk = "green"
        elif yuzde >= 0.25:
            renk = "yellow"
        elif yuzde >= 0.10:
            renk = "orange3"
        else:
            renk = "red"
        print(f"[{renk}][bold] Drone {en_iyi_drone} için kalan batarya: {kalan_batarya[en_iyi_drone]:.2f} mAh")
        atandi = True

    if not atandi:
        print("\nAtanabilecek başka teslimat kalmadı.")
        break


print("\n[bold]---------- GÖREV ÖZETİ ----------")
for k, rotalar in drone_rotalari_sonuc.items():
    print(f"[bold]Drone {k} toplam {len(rotalar)//2} teslimat yaptı.")
