import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.animation import FuncAnimation
import json
from datetime import datetime, timedelta
from multi_a import drone_rotalari_sonuc, node_konumlari

with open("randomdata.json", "r") as dosya:
    veri = json.load(dosya)

drones = veri["drones"]
deliveries = veri["deliveries"]
no_fly_zones = veri["no_fly_zones"]

# Teslimat görevlerini zamanlarına göre sırala
zamanli_gorevler = []
for drone_id_str, rotalar in drone_rotalari_sonuc.items():
    for i in range(0, len(rotalar), 2):  # her çift (gidiş, dönüş)
        rota = rotalar[i]
        teslimat_node = rota[-1]
        teslimat_index = teslimat_node - len(drones)
        teslimat_time_str = deliveries[teslimat_index]["time_window"][0] + ":00"
        teslimat_time = datetime.strptime(teslimat_time_str, "%H:%M:%S")
        zamanli_gorevler.append({
            "zaman": teslimat_time,
            "drone_id": int(drone_id_str),
            "rota": rota
        })

zamanli_gorevler.sort(key=lambda x: x["zaman"])

# Simülasyon başlangıcı
simulasyon_zamani = datetime.strptime("10:00:00", "%H:%M:%S")

fig, ax = plt.subplots(figsize=(12, 10))
plt.xlabel("X Koordinatı")
plt.ylabel("Y Koordinatı")
plt.grid(True)
plt.axis("equal")

# Sabit alanları çiz
for i, drone in enumerate(drones):
    x, y = drone["start_pos"]
    ax.scatter(x, y, color="blue", marker="^", s=100)
    ax.text(x + 1, y + 1, f"D{drone['id']}", fontsize=9)

for teslimat in deliveries:
    x, y = teslimat["pos"]
    ax.scatter(x, y, color="green", marker="o", s=70)
    ax.text(x + 1, y, f"T{teslimat['id']}", fontsize=8)

for zone in no_fly_zones:
    kose_noktalari = zone["coordinates"]
    polygon = MplPolygon(kose_noktalari, closed=True, edgecolor='red', fill=False, linewidth=2)
    ax.add_patch(polygon)
    xs, ys = zip(*kose_noktalari)
    ort_x, ort_y = sum(xs) / len(xs), sum(ys) / len(ys)
    ax.text(ort_x, ort_y, f"Z{zone['id']}", color='red', fontsize=8)

renkler = ["red", "blue", "green", "orange", "purple", "magenta", "cyan"]
lines = []

def guncelle(frame):
    global simulasyon_zamani, zamanli_gorevler
    simulasyon_zamani += timedelta(minutes=10)

    ax.set_title(f"Simülasyon Zamanı: {simulasyon_zamani.strftime('%H:%M:%S')}")
    cizilecekler = []
    kalanlar = []
    sayac = 0

    for gorev in zamanli_gorevler:
        if gorev["zaman"] <= simulasyon_zamani and sayac < 3:
            cizilecekler.append(gorev)
            sayac += 1
        else:
            kalanlar.append(gorev)
    zamanli_gorevler = kalanlar

    for gorev in cizilecekler:
        drone_id = gorev["drone_id"]
        rota = gorev["rota"]
        renk = renkler[drone_id % len(renkler)]
        koordinatlar = [node_konumlari[n] for n in rota]
        x_vals, y_vals = zip(*koordinatlar)
        line, = ax.plot(x_vals, y_vals, color=renk, linewidth=2, marker='o', label=f"Drone {drone_id}")
        lines.append(line)

    return lines

anim = FuncAnimation(fig, guncelle, frames=100, interval=1000, repeat=False)
plt.legend()
plt.tight_layout()
plt.show()
