import json
from graph import get_dynamic_graph_for
from a_star import a_star
from rich import print
import math
import heapq 
from datetime import datetime, timedelta

def zaman_uygun_mu(rota, node_konumlari, hedef_time_window, drone_speed):
    toplam_sure = 0
    for i in range(len(rota) - 1):
        bas = node_konumlari[rota[i]]
        son = node_konumlari[rota[i + 1]]
        mesafe = math.dist(bas, son)
        toplam_sure += mesafe / drone_speed  # saniye

    teslimat_suresi = toplam_sure

    bas = datetime.strptime(hedef_time_window[0] + ":00", "%H:%M:%S")
    bit = datetime.strptime(hedef_time_window[1] + ":00", "%H:%M:%S")
    pencere_suresi = (bit - bas).total_seconds()

    return teslimat_suresi <= pencere_suresi, toplam_sure

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

drone_zaman_araliklari = {i: [] for i in range(len(drones))}

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

        teslimat_bas = datetime.strptime(deliveries[teslimat_index]["time_window"][0] + ":00", "%H:%M:%S")
        teslimat_bit = datetime.strptime(deliveries[teslimat_index]["time_window"][1] + ":00", "%H:%M:%S")

        graph_gidis = get_dynamic_graph_for(drone_index, teslimat_index)
        hedef_id = teslimat_index + len(drones)
        rota_gidis = a_star(graph_gidis, drone_index, hedef_id, node_konumlari, drone_index)
        if rota_gidis is None:
            print("[red] Reddedildi: A* rota bulunamadı.")
            continue

        zaman_uygun, teslim_sure = zaman_uygun_mu(rota_gidis, node_konumlari, deliveries[teslimat_index]["time_window"], drone["speed"])
        if not zaman_uygun:
            print("[red] Reddedildi: Teslimat zaman penceresine uymuyor.")
            continue

        gorev_bas = teslimat_bas
        gorev_bit = gorev_bas + timedelta(seconds=teslim_sure * 2)

        uyusmazlik = False
        for onceki_bas, onceki_bit in drone_zaman_araliklari[drone_index]:
            if not (gorev_bit <= onceki_bas or gorev_bas >= onceki_bit):
                uyusmazlik = True
                break

        if uyusmazlik:
            print("[red] Reddedildi: Zaman aralığı çakışıyor (gidiş + dönüş süresiyle).")
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
        drone_zaman_araliklari[en_iyi_drone].append((gorev_bas, gorev_bit))

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

def multi_a_ozet(drone_rotalari: dict, delivery_sayisi: int, konumlar: dict, delivery_liste: list, drones: list):
    total_energy = 0
    total_deliveries = 0

    print("\n[bold blue]---------- GÖREV ÖZETİ (A*) ----------")
    for k, rotalar in drone_rotalari.items():
        teslimat_sayisi = len(rotalar) // 2
        print(f"[bold]Drone {k} → [green]{teslimat_sayisi} teslimat")

        for i in range(0, len(rotalar), 2):
            rota = rotalar[i]
            teslimat_node = rota[-1]
            teslimat_index = teslimat_node - len(drones)
            agirlik = delivery_liste[teslimat_index]["weight"]
            enerji_gidis = hesapla_enerji(rota, konumlar, agirlik)
            rota_donus = rotalar[i+1]
            enerji_donus = hesapla_enerji(rota_donus, konumlar, agirlik=0)
            toplam = enerji_gidis + enerji_donus
            total_energy += toplam
            total_deliveries += 1

    ortalama_enerji = total_energy / total_deliveries if total_deliveries > 0 else 0
    tamamlanan_oran = total_deliveries / delivery_sayisi * 100

    print(f"\n[bold cyan]Toplam teslimat sayısı      : {delivery_sayisi}")
    print(f"[bold cyan]Tamamlanan teslimat sayısı  : {total_deliveries}")
    print(f"[bold cyan]Tamamlanma oranı (%)         : {tamamlanan_oran:.1f}%")
    print(f"[bold cyan]Toplam enerji tüketimi    : {total_energy:.2f} mAh")
    print(f"[bold cyan]Ortalama enerji tüketimi  : {ortalama_enerji:.2f} mAh\n")

    return {
        "tamamlanan": total_deliveries,
        "toplam": delivery_sayisi,
        "oran": tamamlanan_oran,
        "toplam_enerji": total_energy,
        "ortalama_enerji": ortalama_enerji
    }
if __name__ == "__main__":
    multi_a_ozet(drone_rotalari_sonuc, len(deliveries), node_konumlari, deliveries, drones)
