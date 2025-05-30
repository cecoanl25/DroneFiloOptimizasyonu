import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from multi_a import drone_rotalari_sonuc, node_konumlari
import json

with open("randomdata.json", "r") as dosya:
    veri = json.load(dosya)

drones = veri["drones"]
deliveries = veri["deliveries"]
no_fly_zones = veri["no_fly_zones"]

plt.figure(figsize=(12, 10))

for i, drone in enumerate(drones):
    x, y = drone["start_pos"]
    plt.scatter(x, y, color="blue", marker="^", s=100)
    plt.text(x + 1, y + 1, f"D{drone['id']}", fontsize=9)

for teslimat in deliveries:
    x, y = teslimat["pos"]
    plt.scatter(x, y, color="green", marker="o", s=70)
    plt.text(x + 1, y, f"T{teslimat['id']}", fontsize=8)

for zone in no_fly_zones:
    kose_noktalari = zone["coordinates"]
    polygon = MplPolygon(kose_noktalari, closed=True, edgecolor='red', fill=False, linewidth=2)
    plt.gca().add_patch(polygon)
    xs, ys = zip(*kose_noktalari)
    ort_x, ort_y = sum(xs) / len(xs), sum(ys) / len(ys)
    plt.text(ort_x, ort_y, f"Z{zone['id']}", color='red', fontsize=8)

renkler = ["red", "blue", "green", "yellow", "magenta", "cyan"]
for i, (drone_id, rotalar) in enumerate(drone_rotalari_sonuc.items()):
    renk = renkler[i % len(renkler)]
    etiket_yazildi = False
    for rota in rotalar:
        rota_koord = [node_konumlari[node] for node in rota]
        x_vals, y_vals = zip(*rota_koord)
        plt.plot(
            x_vals, y_vals, color=renk, linewidth=2, marker='o',
            label=f"Drone {drone_id} rotası" if not etiket_yazildi else ""
        )
        etiket_yazildi = True

plt.title("Drone Filo Teslimat Rotaları")
plt.xlabel("X Koordinatı")
plt.ylabel("Y Koordinatı")
plt.grid(True)
plt.axis("equal")
plt.legend()
plt.tight_layout()
plt.show()
