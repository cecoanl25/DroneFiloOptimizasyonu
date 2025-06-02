import time
from rich import print
from genetic_algorithm import GeneticDroneRouter, ga_ozet

print("\n[bold cyan]----- A* VS GA -----\n")

start_multi = time.time()
import multi_a
multi_ozet = multi_a.multi_a_ozet(
    multi_a.drone_rotalari_sonuc,
    len(multi_a.deliveries),
    multi_a.node_konumlari,
    multi_a.deliveries,
    multi_a.drones
)
end_multi = time.time()
sure_multi = end_multi - start_multi

start_ga = time.time()
router = GeneticDroneRouter()
best_solution = router.evolve()
ga_ozet_sonuc = ga_ozet(
    best_solution,
    router.deliveries,
    router.drones,
    router.node_positions,
    router.urgent_deliveries
)
end_ga = time.time()
sure_ga = end_ga - start_ga

print("\n[bold]----- ALGORİTMA SÜRELERİ -----")
print(f"[bold cyan]A* : {sure_multi:.2f} saniye")
print(f"[bold cyan]GA : {sure_ga:.2f} saniye")
