import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.animation import FuncAnimation
from genetic_algorithm import GeneticDroneRouter, ga_ozet
from datetime import datetime, timedelta

router = GeneticDroneRouter()
best_solution = router.evolve()
ga_ozet(best_solution, router.deliveries, router.drones, router.node_positions, router.urgent_deliveries)

drone_routes = best_solution.drone_routes
node_positions = router.node_positions
drones = router.drones
deliveries = router.deliveries
no_fly_zones = router.no_fly_zones

zamanli_gorevler = []

for drone_id, drone_route in drone_routes.items():
    rota = drone_route.route
    for i in range(0, len(rota) - 1, 2):
        if i + 1 >= len(rota):
            break
        teslimat_node = rota[i + 1] if rota[i + 1] >= len(drones) else rota[i]
        if teslimat_node < len(drones):
            continue
        teslimat_index = teslimat_node - len(drones)
        teslimat_time_str = deliveries[teslimat_index]["time_window"][0] + ":00"
        teslimat_time = datetime.strptime(teslimat_time_str, "%H:%M:%S")
        zamanli_gorevler.append({
            "zaman": teslimat_time,
            "drone_id": drone_id,
            "rota": rota[i:i + 2]
        })

zamanli_gorevler.sort(key=lambda x: x["zaman"])

simulasyon_zamani = datetime.strptime("10:00:00", "%H:%M:%S")
fig, ax = plt.subplots(figsize=(12, 10))
plt.xlabel("X Koordinatı")
plt.ylabel("Y Koordinatı")
plt.grid(True)
plt.axis("equal")

for drone in drones:
    x, y = drone["start_pos"]
    ax.scatter(x, y, color="blue", marker="^", s=100)
    ax.text(x + 1, y + 1, f"D{drone['id']}", fontsize=9)

for teslimat in deliveries:
    x, y = teslimat["pos"]
    ax.scatter(x, y, color="green", marker="o", s=70)
    ax.text(x + 1, y, f"T{teslimat['id']}", fontsize=8)

zaman_metni = ax.text(0.02, 0.02, "", transform=ax.transAxes, fontsize=14, color="black", ha="left", va="bottom")

renkler = ["red", "blue", "green", "orange", "purple", "magenta", "cyan"]
lines = []

def bolge_aktif_mi(active_time, current_time):
    start = datetime.strptime(active_time[0] + ":00", "%H:%M:%S")
    end = datetime.strptime(active_time[1] + ":00", "%H:%M:%S")
    return start <= current_time <= end

def guncelle(frame):
    global simulasyon_zamani, zamanli_gorevler
    simulasyon_zamani += timedelta(minutes=2)
    zaman_metni.set_text(f"Simülasyon Zamanı: {simulasyon_zamani.strftime('%H:%M:%S')}")

    for patch in reversed(ax.patches):
        patch.remove()

    for zone in no_fly_zones:
        aktif = bolge_aktif_mi(zone["active_time"], simulasyon_zamani)
        renk = "red" if aktif else "gray"
        polygon = MplPolygon(zone["coordinates"], closed=True, edgecolor=renk, fill=False, linewidth=2)
        ax.add_patch(polygon)
        xs, ys = zip(*zone["coordinates"])
        ort_x, ort_y = sum(xs) / len(xs), sum(ys) / len(ys)
        ax.text(ort_x, ort_y, f"Z{zone['id']}", color=renk, fontsize=8)

    cizilecekler = []
    kalanlar = []
    sayac = 0

    for gorev in zamanli_gorevler:
        if gorev["zaman"] <= simulasyon_zamani and sayac < 3:
            cizilecekler.append(gorev)
            sayac += 1
        else:
            kalanlar.append(gorev)
    zamanli_gorevler[:] = kalanlar

    for gorev in cizilecekler:
        drone_id = gorev["drone_id"]
        rota = gorev["rota"]
        renk = renkler[drone_id % len(renkler)]
        koordinatlar = [node_positions[n] for n in rota]
        x_vals, y_vals = zip(*koordinatlar)
        line, = ax.plot(x_vals, y_vals, color=renk, linewidth=2, marker='o', label=f"Drone {drone_id}")
        lines.append(line)

    return lines

anim = FuncAnimation(fig, guncelle, frames=100, interval=1000, repeat=False)
plt.legend()
plt.tight_layout()
plt.show()