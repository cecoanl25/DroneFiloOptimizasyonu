import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from a_star import rota_sonucu, node_konumlari_sonucu
import json

with open("randomdata.json", "r") as dosya: #Veriler okunur.
    veri = json.load(dosya)

drones = veri["drones"]
deliveries = veri["deliveries"]
no_fly_zones = veri["no_fly_zones"]

#A* algoritmasından doğan rota ve node konum bilgileri çekilir.
rota = rota_sonucu
node_konumlari = node_konumlari_sonucu

#Node konumları, hem drone hem teslimat noktaları için yeniden oluşturulur.
node_konumlari = {}
for i, drone in enumerate(drones):
    node_konumlari[i] = tuple(drone["start_pos"])  #Drone'ların başlangıç konumu
for i, teslimat in enumerate(deliveries):
    node_konumlari[i + len(drones)] = tuple(teslimat["pos"]) #Teslimat noktalarının pozisyonları

plt.figure(figsize=(10, 8)) #Figür boyutu

#Dronelar, harita üzerinde mavi üçgen şeklinde çizilir ve D0, D1 vs. olarak etiketlenir.
for i, drone in enumerate(drones):
    x, y = drone["start_pos"]
    plt.scatter(x, y, color="blue", marker="^", s=100)
    plt.text(x + 1, y + 1, f"D{drone['id']}", fontsize=9)

#Teslimat noktaları yeşil daire şeklinde gösterilir ve T0, T1 vs. olarak etiketlenir.
for teslimat in deliveries:
    x, y = teslimat["pos"]
    plt.scatter(x, y, color="green", marker="o", s=70)
    plt.text(x + 1, y, f"T{teslimat['id']}", fontsize=8)

#Yasaklı bölgeler kırmızı dörtgen şeklinde çizilir ve içlerine Z0, Z1 vs. olarak etiketlenir.
for zone in no_fly_zones:
    kose_noktalari = zone["coordinates"]
    polygon = MplPolygon(kose_noktalari, closed=True, edgecolor='red', fill=False, linewidth=2)
    plt.gca().add_patch(polygon)
    xs, ys = zip(*kose_noktalari)
    ort_x, ort_y = sum(xs) / len(xs), sum(ys) / len(ys) #Dörtgenin merkez noktası belirlenir.
    plt.text(ort_x, ort_y, f"Z{zone['id']}", color='red', fontsize=8)

#Rota üzerindeki tüm noktalar sırayla alınarak çizgi çizilir. (turuncu çizgi)
rota_koord = [node_konumlari[node] for node in rota]
x_vals, y_vals = zip(*rota_koord)
plt.plot(x_vals, y_vals, color="orange", linewidth=2, marker='o', label="Rota")

#Grafik başlık ve eksen etiketleri eklenir.
plt.title("Drone Teslimat Rotası")
plt.xlabel("X Koordinatı")
plt.ylabel("Y Koordinatı")
plt.grid(True)
plt.axis("equal")
plt.legend()
plt.tight_layout()
plt.show()
