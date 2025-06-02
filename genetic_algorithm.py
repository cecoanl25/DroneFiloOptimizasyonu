from datetime import datetime, timedelta
import json
import random
import math
import heapq
import copy
from typing import List, Dict, Tuple, Optional
from shapely import LineString, Polygon
from rich import print

class DroneRoute:
    """Bir drone'un rotasını temsil eden sınıf"""
    def __init__(self, drone_id: int, route: List[int], energy_consumed: float = 0):
        self.drone_id = drone_id
        self.route = route
        self.energy_consumed = energy_consumed
        self.deliveries_completed = 0
        self.constraint_violations = 0

class Individual:
    """Genetik algoritma için birey (çözüm) sınıfı"""
    def __init__(self, drone_routes: Dict[int, DroneRoute]):
        self.drone_routes = drone_routes
        self.fitness = 0.0
        self.total_deliveries = 0
        self.total_energy = 0.0
        self.total_violations = 0

class GeneticDroneRouter:
    def __init__(self, data_file: str = "randomdata.json"):
        with open(data_file, "r") as file:
            self.data = json.load(file)
        
        self.drones = self.data["drones"]
        self.deliveries = self.data["deliveries"]
        self.no_fly_zones = self.data["no_fly_zones"]
        
        # Node konumları
        self.node_positions = {}
        for i, drone in enumerate(self.drones):
            self.node_positions[i] = tuple(drone["start_pos"])
        for i, delivery in enumerate(self.deliveries):
            self.node_positions[i + len(self.drones)] = tuple(delivery["pos"])
        
        # Acil teslimatlar için min-heap
        self.urgent_deliveries = []
        for i, delivery in enumerate(self.deliveries):
            if delivery["priority"] <= 2:  # Priority 1 ve 2 acil kabul edilir
                heapq.heappush(self.urgent_deliveries, (delivery["priority"], i))
        
        self.population_size = 50
        self.generations = 100
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
        self.elitism_rate = 0.1

    def calculate_route_energy(self, route: List[int], weight: float = 0) -> float:
        """Rota için enerji tüketimini hesapla"""
        total_energy = 0
        energy_coefficient = 10
        
        for i in range(len(route) - 1):
            start_pos = self.node_positions[route[i]]
            end_pos = self.node_positions[route[i + 1]]
            distance = math.dist(start_pos, end_pos)
            total_energy += distance * (1 + weight / 10) * energy_coefficient
        
        return total_energy

    def is_valid_route(self, drone_id: int, route: List[int]) -> Tuple[bool, int]:
        violations = 0
        drone = self.drones[drone_id]
        total_energy = 0

        for i in range(len(route) - 1):
            current_node = route[i]
            next_node = route[i + 1]

            start_pos = self.node_positions[current_node]
            end_pos = self.node_positions[next_node]
            segment_line = LineString([start_pos, end_pos])
            for zone in self.no_fly_zones:
                polygon = Polygon(zone["coordinates"])
                if segment_line.intersects(polygon):
                    distance = segment_line.length
                    speed = drone["speed"]
                    estimated_seconds = distance / speed
                    estimated_time = datetime.strptime("10:00:00", "%H:%M:%S") + timedelta(seconds=estimated_seconds)
                    start_str, end_str = zone["active_time"]
                    fmt = "%H:%M"
                    zone_start = datetime.strptime(start_str, fmt)
                    zone_end = datetime.strptime(end_str, fmt)
                    if zone_start <= estimated_time <= zone_end:
                        violations += 1


            weight = 0
            if current_node < len(self.drones) and next_node >= len(self.drones):
                delivery_idx = next_node - len(self.drones)
                if delivery_idx < 0 or delivery_idx >= len(self.deliveries):
                    violations += 1
                    continue

                delivery = self.deliveries[delivery_idx]
                weight = delivery["weight"]

                if weight > drone["max_weight"]:
                    violations += 1
                speed = drone["speed"]
                distance = math.dist(start_pos, end_pos)
                estimated_seconds = distance / speed

                start_str, end_str = delivery["time_window"]
                fmt = "%H:%M"
                start_time = datetime.strptime(start_str, fmt)
                end_time = datetime.strptime(end_str, fmt)
                estimated_time = start_time + timedelta(seconds=estimated_seconds)

                if not (start_time <= estimated_time <= end_time):
                    violations += 1

            segment_energy = self.calculate_route_energy([current_node, next_node], weight)
            total_energy += segment_energy

        # 🔋 Toplam batarya kontrolü
        if total_energy > drone["battery"]:
            violations += 1

        return violations == 0, violations

    def create_random_individual(self) -> Individual:
        """Rastgele geçerli bir birey oluştur"""
        drone_routes = {}
        assigned_deliveries = set()
        
        for drone_id in range(len(self.drones)):
            drone_routes[drone_id] = DroneRoute(drone_id, [drone_id])
        
        # Önce acil teslimatları ata
        urgent_copy = self.urgent_deliveries.copy()
        while urgent_copy:
            _, delivery_idx = heapq.heappop(urgent_copy)
            if delivery_idx in assigned_deliveries:
                continue
                
            # Bu teslimat için uygun drone bul
            best_drone = self.find_best_drone_for_delivery(delivery_idx, drone_routes, assigned_deliveries)
            if best_drone is not None:
                delivery_node = delivery_idx + len(self.drones)
                # Gidis-donus rotası ekle
                drone_routes[best_drone].route.extend([delivery_node, best_drone])
                assigned_deliveries.add(delivery_idx)
        
        # Kalan teslimatları rastgele ata
        remaining_deliveries = [i for i in range(len(self.deliveries)) if i not in assigned_deliveries]
        random.shuffle(remaining_deliveries)
        
        for delivery_idx in remaining_deliveries:
            best_drone = self.find_best_drone_for_delivery(delivery_idx, drone_routes, assigned_deliveries)
            if best_drone is not None:
                delivery_node = delivery_idx + len(self.drones)
                drone_routes[best_drone].route.extend([delivery_node, best_drone])
                assigned_deliveries.add(delivery_idx)
        
        individual = Individual(drone_routes)
        # Çakışan teslimatları temizle
        self.fix_duplicate_deliveries(individual)
        return individual

    def find_best_drone_for_delivery(self, delivery_idx: int, drone_routes: Dict[int, DroneRoute], 
                                   assigned_deliveries: set) -> Optional[int]:
        """Bir teslimat için en uygun drone'u bul"""
        delivery = self.deliveries[delivery_idx]
        best_drone = None
        best_cost = float('inf')
        
        for drone_id, drone in enumerate(self.drones):
            # Ağırlık kontrolü
            if delivery["weight"] > drone["max_weight"]:
                continue
            
            # Mevcut rota uzunluğu kontrolü (çok uzun rotalar engelle)
            if len(drone_routes[drone_id].route) > 10:
                continue
            
            # Test rotası oluştur
            test_route = drone_routes[drone_id].route.copy()
            delivery_node = delivery_idx + len(self.drones)
            test_route.extend([delivery_node, drone_id])
            
            # Rota geçerliliğini kontrol et
            is_valid, violations = self.is_valid_route(drone_id, test_route)
            if not is_valid:
                continue
            
            # Maliyet hesapla (mesafe + ağırlık + öncelik)
            current_pos = self.node_positions[drone_routes[drone_id].route[-1]]
            delivery_pos = self.node_positions[delivery_node]
            distance = math.dist(current_pos, delivery_pos)
            cost = distance * delivery["weight"] + delivery["priority"] * 100
            
            if cost < best_cost:
                best_cost = cost
                best_drone = drone_id
        
        return best_drone

    def calculate_fitness(self, individual: Individual) -> float:
        """Fitness fonksiyonu: (teslimat sayisi x 50) - (toplam enerji x 0.1) - (ihlal x 1000)"""
        total_deliveries = 0
        total_energy = 0.0
        total_violations = 0
        
        for drone_id, drone_route in individual.drone_routes.items():
            # Teslimat sayısını hesapla (sadece teslimat noktalarına gidiş)
            delivery_count = 0
            current_weight = 0
            route_energy = 0
            
            for i in range(len(drone_route.route) - 1):
                current_node = drone_route.route[i]
                next_node = drone_route.route[i + 1]
                
                # Eğer teslimat noktasına gidiyorsak (drone'dan teslimat noktasına)
                if current_node < len(self.drones) and next_node >= len(self.drones):
                    delivery_idx = next_node - len(self.drones)
                    delivery = self.deliveries[delivery_idx]
                    current_weight = delivery["weight"]
                    delivery_count += 1
                # Eğer teslimat noktasından drone'a dönüyorsak
                elif current_node >= len(self.drones) and next_node < len(self.drones):
                    current_weight = 0
                
                # Enerji hesapla
                segment_energy = self.calculate_route_energy([current_node, next_node], current_weight)
                route_energy += segment_energy
            
            # Kısıt ihlallerini kontrol et
            _, violations = self.is_valid_route(drone_id, drone_route.route)
            
            total_deliveries += delivery_count
            total_energy += route_energy
            total_violations += violations
        
        # Fitness hesapla - daha yüksek teslimat sayısı için bonus
        fitness = (total_deliveries * 100) - (total_energy * 0.05) - (total_violations * 2000)
        
        # Acil teslimatları tamamlama bonusu
        urgent_bonus = 0
        for priority, delivery_idx in self.urgent_deliveries:
            delivery_node = delivery_idx + len(self.drones)
            for drone_route in individual.drone_routes.values():
                if delivery_node in drone_route.route:
                    urgent_bonus += 50 * (3 - priority)  # Priority 1 = 100 bonus, Priority 2 = 50 bonus
                    break
        
        fitness += urgent_bonus
        
        # Individual'ın istatistiklerini güncelle
        individual.total_deliveries = total_deliveries
        individual.total_energy = total_energy
        individual.total_violations = total_violations
        individual.fitness = fitness
        
        return fitness

    def tournament_selection(self, population: List[Individual], tournament_size: int = 3) -> Individual:
        """Turnuva seçimi"""
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness)

    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """İki ebeveynden iki çocuk üret"""
        child1_routes = {}
        child2_routes = {}
        
        # Her drone için rastgele olarak hangi ebeveynden alınacağını belirle
        for drone_id in range(len(self.drones)):
            if random.random() < 0.5:
                child1_routes[drone_id] = copy.deepcopy(parent1.drone_routes[drone_id])
                child2_routes[drone_id] = copy.deepcopy(parent2.drone_routes[drone_id])
            else:
                child1_routes[drone_id] = copy.deepcopy(parent2.drone_routes[drone_id])
                child2_routes[drone_id] = copy.deepcopy(parent1.drone_routes[drone_id])
        
        child1 = Individual(child1_routes)
        child2 = Individual(child2_routes)
        
        # Çakışan teslimatları düzelt
        self.fix_duplicate_deliveries(child1)
        self.fix_duplicate_deliveries(child2)
        
        return child1, child2

    def fix_duplicate_deliveries(self, individual: Individual):
        """Çakışan teslimatları düzelt"""
        assigned_deliveries = set()
        
        # Önce hangi teslimatların çakıştığını bul ve düzelt
        for drone_id, drone_route in individual.drone_routes.items():
            new_route = [drone_route.route[0]]  # Drone'un başlangıç pozisyonu
            
            i = 1
            while i < len(drone_route.route):
                node = drone_route.route[i]
                
                if node >= len(self.drones):  # Teslimat noktası
                    delivery_idx = node - len(self.drones)
                    if delivery_idx not in assigned_deliveries:
                        new_route.append(node)
                        assigned_deliveries.add(delivery_idx)
                        # Dönüş rotasını da ekle (eğer varsa)
                        if i + 1 < len(drone_route.route) and drone_route.route[i + 1] == drone_id:
                            new_route.append(drone_id)
                            i += 1  # Dönüş node'unu da atla
                else:  # Drone pozisyonu
                    if len(new_route) > 1 and new_route[-1] != drone_id:
                        new_route.append(node)
                
                i += 1
            
            drone_route.route = new_route

    def mutate(self, individual: Individual):
        """Mutasyon: Rastgele bir teslimat noktasını değiştir"""
        if random.random() > self.mutation_rate:
            return
        
        # Rastgele bir drone seç
        drone_id = random.randint(0, len(self.drones) - 1)
        drone_route = individual.drone_routes[drone_id]
        
        # Teslimat noktalarını bul
        delivery_indices = []
        for i, node in enumerate(drone_route.route):
            if node >= len(self.drones):
                delivery_indices.append(i)
        
        if not delivery_indices:
            return
        
        # Rastgele bir teslimat noktasını değiştir
        change_idx = random.choice(delivery_indices)
        old_delivery = drone_route.route[change_idx] - len(self.drones)
        
        # Yeni bir teslimat noktası seç
        available_deliveries = []
        for i in range(len(self.deliveries)):
            if i != old_delivery and self.deliveries[i]["weight"] <= self.drones[drone_id]["max_weight"]:
                available_deliveries.append(i)
        
        if available_deliveries:
            new_delivery = random.choice(available_deliveries)
            drone_route.route[change_idx] = new_delivery + len(self.drones)

    def create_initial_population(self) -> List[Individual]:
        """Başlangıç popülasyonunu oluştur"""
        population = []
        for _ in range(self.population_size):
            individual = self.create_random_individual()
            self.calculate_fitness(individual)
            population.append(individual)
        return population

    def evolve(self) -> Individual:
        """Genetik algoritma ana döngüsü"""
        print("[bold blue]Genetik Algoritma Başlatılıyor...")
        print(f"Popülasyon boyutu: {self.population_size}")
        print(f"Nesil sayısı: {self.generations}")
        print(f"Acil teslimat sayısı: {len(self.urgent_deliveries)}")
        print(f"Toplam teslimat sayısı: {len(self.deliveries)}")
        
        # Başlangıç popülasyonu
        population = self.create_initial_population()
        
        best_fitness_history = []
        
        for generation in range(self.generations):
            # Fitness hesapla
            for individual in population:
                self.calculate_fitness(individual)
            
            # Popülasyonu fitness'a göre sırala
            population.sort(key=lambda x: x.fitness, reverse=True)
            
            best_fitness = population[0].fitness
            best_fitness_history.append(best_fitness)
            
            if generation % 10 == 0:
                print(f"[cyan]Nesil {generation}: En iyi fitness = {best_fitness:.2f}")
                print(f"  Teslimat: {population[0].total_deliveries}, Enerji: {population[0].total_energy:.2f}, İhlal: {population[0].total_violations}")
            
            # Yeni nesil oluştur
            new_population = []
            
            # Elitizm: En iyi bireyleri koru
            elite_count = int(self.population_size * self.elitism_rate)
            new_population.extend(population[:elite_count])
            
            # Crossover ve mutation ile yeni bireyler üret
            while len(new_population) < self.population_size:
                parent1 = self.tournament_selection(population)
                parent2 = self.tournament_selection(population)
                
                if random.random() < self.crossover_rate:
                    child1, child2 = self.crossover(parent1, parent2)
                else:
                    child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
                
                self.mutate(child1)
                self.mutate(child2)
                
                new_population.extend([child1, child2])
            
            # Popülasyon boyutunu sınırla
            population = new_population[:self.population_size]
        
        # En iyi çözümü döndür
        for individual in population:
            self.calculate_fitness(individual)
        
        best_individual = max(population, key=lambda x: x.fitness)
        
        print(f"\n[bold green]Algoritma tamamlandı!")
        print(f"En iyi fitness: {best_individual.fitness:.2f}")
        print(f"Toplam teslimat: {best_individual.total_deliveries}")
        print(f"Toplam enerji: {best_individual.total_energy:.2f}")
        print(f"Kısıt ihlalleri: {best_individual.total_violations}")
        
        return best_individual

    def print_solution(self, solution: Individual):
        """Çözümü yazdır"""
        print("\n[bold]---------- GENETİK ALGORİTMA ÇÖZÜMÜ ----------")
        
        total_system_deliveries = 0
        completed_urgent_deliveries = 0
        all_delivered_items = set()
        
        for drone_id, drone_route in solution.drone_routes.items():
            route = drone_route.route
            if len(route) <= 1:
                continue
                
            print(f"\n[bold]Drone {drone_id} Rotası:")
            
            # Rotayı yazdır
            route_str = ""
            total_deliveries = 0
            route_energy = 0
            delivered_items = []
            
            for i in range(len(route) - 1):
                current_node = route[i]
                next_node = route[i + 1]
                
                # Node isimlerini yazdır
                if current_node < len(self.drones):
                    route_str += f"D{current_node} → "
                else:
                    delivery_idx = current_node - len(self.drones)
                    route_str += f"T{delivery_idx} → "
                
                # Teslimat sayısını güncelle (sadece drone'dan teslimat noktasına gidiş)
                if current_node < len(self.drones) and next_node >= len(self.drones):
                    delivery_idx = next_node - len(self.drones)
                    if delivery_idx not in all_delivered_items:  # Çakışma kontrolü
                        total_deliveries += 1
                        delivered_items.append(delivery_idx)
                        all_delivered_items.add(delivery_idx)
                        
                        # Acil teslimat kontrolü
                        for priority, urgent_delivery_idx in self.urgent_deliveries:
                            if urgent_delivery_idx == delivery_idx:
                                completed_urgent_deliveries += 1
                                break
                
                # Enerji hesapla
                weight = 0
                if current_node < len(self.drones) and next_node >= len(self.drones):
                    delivery_idx = next_node - len(self.drones)
                    weight = self.deliveries[delivery_idx]["weight"]
                
                segment_energy = self.calculate_route_energy([current_node, next_node], weight)
                route_energy += segment_energy
            
            # Son node'u yazdır
            last_node = route[-1]
            if last_node < len(self.drones):
                route_str += f"D{last_node}"
            else:
                delivery_idx = last_node - len(self.drones)
                route_str += f"T{delivery_idx}"
            
            print(route_str)
            print(f"  Toplam teslimat: {total_deliveries}")
            if delivered_items:
                print(f"  Teslim edilen paketler: {delivered_items}")
            print(f"  Harcanan enerji: {route_energy:.2f} mAh")
            
            # Kalan batarya
            remaining_battery = self.drones[drone_id]["battery"] - route_energy
            battery_percentage = remaining_battery / self.drones[drone_id]["battery"]
            
            if battery_percentage >= 0.50:
                color = "green"
            elif battery_percentage >= 0.25:
                color = "yellow"
            elif battery_percentage >= 0.10:
                color = "orange3"
            else:
                color = "red"
            
            print(f"  [{color}]Kalan batarya: {remaining_battery:.2f} mAh ({battery_percentage*100:.1f}%)")
            
            total_system_deliveries += total_deliveries
        
        print(f"\n[bold]Sistem Özeti:")
        print(f"  Toplam teslim edilen paket: {total_system_deliveries}")
        print(f"  Toplam paket sayısı: {len(self.deliveries)}")
        print(f"  Teslim oranı: {(total_system_deliveries/len(self.deliveries)*100):.1f}%")
        print(f"  Tamamlanan acil teslimat: {completed_urgent_deliveries}/{len(self.urgent_deliveries)}")
        
        # Teslim edilemeyen paketleri göster
        undelivered = []
        for i in range(len(self.deliveries)):
            if i not in all_delivered_items:
                undelivered.append(i)
        
        if undelivered:
            print(f"  [red]Teslim edilemeyen paketler: {undelivered}")
        else:
            print(f"  [green]Tüm paketler başarıyla teslim edildi!")

if __name__ == "__main__":
    router = GeneticDroneRouter()
    best_solution = router.evolve()
    router.print_solution(best_solution) 


def ga_ozet(best_solution, deliveries, drones, node_positions, urgent_deliveries):
    total_deliveries = 0
    total_energy = 0
    total_urgent = len(urgent_deliveries)
    completed_urgent = 0

    print("\n[bold blue]---------- GÖREV ÖZETİ (GENETİK ALGORİTMA) ----------")

    for drone_id, drone_route in best_solution.drone_routes.items():
        route = drone_route.route
        teslimat_sayisi = sum(1 for i in range(len(route)-1) if route[i] < len(drones) and route[i+1] >= len(drones))
        print(f"[bold]Drone {drone_id} → [green]{teslimat_sayisi} teslimat")

        drone_total = 0
        for i in range(len(route) - 1):
            bas = node_positions[route[i]]
            son = node_positions[route[i + 1]]
            mesafe = math.dist(bas, son)

            if route[i] < len(drones) and route[i+1] >= len(drones):
                delivery_idx = route[i+1] - len(drones)
                agirlik = deliveries[delivery_idx]["weight"]
                enerji = mesafe * (1 + agirlik / 10) * 10
                total_deliveries += 1
                drone_total += enerji

                for p, urgent_idx in urgent_deliveries:
                    if urgent_idx == delivery_idx:
                        completed_urgent += 1
            elif route[i] >= len(drones) and route[i+1] < len(drones):
                enerji = mesafe * 1 * 10
                drone_total += enerji
            else:
                enerji = mesafe * 10
                drone_total += enerji

        total_energy += drone_total

    ortalama_enerji = total_energy / total_deliveries if total_deliveries > 0 else 0
    tamamlanma_orani = total_deliveries / len(deliveries) * 100

    print(f"\n[bold cyan]Toplam teslimat sayısı      : {len(deliveries)}")
    print(f"[bold cyan]Tamamlanan teslimat sayısı  : {total_deliveries}")
    print(f"[bold cyan]Tamamlanma oranı (%)         : {tamamlanma_orani:.1f}%")
    print(f"[bold cyan]Toplam enerji tüketimi    : {total_energy:.2f} mAh")
    print(f"[bold cyan]Ortalama enerji tüketimi  : {ortalama_enerji:.2f} mAh")

    return {
        "tamamlanan": total_deliveries,
        "toplam": len(deliveries),
        "oran": tamamlanma_orani,
        "toplam_enerji": total_energy,
        "ortalama_enerji": ortalama_enerji
    }