import json
import math
from datetime import datetime, timedelta
from shapely.geometry import LineString, Polygon, Point

with open("randomdata.json", "r") as dosya:
    veri = json.load(dosya)

drones = veri["drones"]
deliveries = veri["deliveries"]
no_fly_zones = veri["no_fly_zones"]

def zaman_cakisiyor(zone_time, tahmini_zaman):
    fmt = "%H:%M:%S"
    bas = datetime.strptime(zone_time[0] + ":00", fmt)
    bit = datetime.strptime(zone_time[1] + ":00", fmt)
    an = datetime.strptime(tahmini_zaman, fmt)
    return bas <= an <= bit

def get_dynamic_graph_for(drone_index: int, target_delivery_index: int):
    hedef_agirlik = deliveries[target_delivery_index]["weight"]
    hedef_oncelik = deliveries[target_delivery_index]["priority"]
    drone_max_weight = drones[drone_index]["max_weight"]
    drone_battery = drones[drone_index]["battery"]
    drone_speed = drones[drone_index]["speed"]

    if hedef_agirlik > drone_max_weight:
        print(f"UYARI: Drone {drone_index} teslimat {target_delivery_index} paketini taşıyamaz! ({hedef_agirlik:.2f} kg > {drone_max_weight:.2f} kg)")
        return {}

    dynamic_graf = {drone_index: []}

    for j, delivery in enumerate(deliveries):
        delivery_node = j + len(drones)
        no_fly_penalty = 0

        start_pos = tuple(drones[drone_index]["start_pos"])
        end_pos = tuple(delivery["pos"])
        line = LineString([start_pos, end_pos])
        mesafe = line.length
        maliyet = mesafe * hedef_agirlik + (hedef_oncelik * 100)
        enerji = mesafe * hedef_agirlik * 10

        for zone in no_fly_zones:
            polygon = Polygon(zone["coordinates"])
            if line.intersects(polygon):
                intersection = line.intersection(polygon)
                if intersection.is_empty:
                    continue
                if intersection.geom_type == "Point":
                    distance_to_intersection = LineString([start_pos, (intersection.x, intersection.y)]).length
                elif intersection.geom_type == "MultiPoint":
                    first_point = list(intersection.geoms)[0]
                    distance_to_intersection = LineString([start_pos, (first_point.x, first_point.y)]).length
                else:
                    distance_to_intersection = mesafe / 2
                gecis_suresi = distance_to_intersection / drone_speed
                gecis_saati = (datetime.strptime("10:00:00", "%H:%M:%S") + timedelta(seconds=gecis_suresi)).strftime("%H:%M:%S")
                if zaman_cakisiyor(zone["active_time"], gecis_saati):
                    no_fly_penalty += 1000
                 

        maliyet += no_fly_penalty
        if enerji <= drone_battery:
            dynamic_graf[drone_index].append((delivery_node, maliyet, enerji))

    for i, d1 in enumerate(deliveries):
        node_i = i + len(drones)
        dynamic_graf.setdefault(node_i, [])

        for j, d2 in enumerate(deliveries):
            if i == j:
                continue
            node_j = j + len(drones)
            line = LineString([tuple(d1["pos"]), tuple(d2["pos"])])
            mesafe = line.length
            maliyet = mesafe * hedef_agirlik + (hedef_oncelik * 100)
            enerji = mesafe * hedef_agirlik * 10
            no_fly_penalty = 0
            for zone in no_fly_zones:
                polygon = Polygon(zone["coordinates"])
                if line.intersects(polygon):
                    intersection = line.intersection(polygon)
                    if intersection.is_empty:
                        continue
                    if intersection.geom_type == "Point":
                        distance_to_intersection = LineString([tuple(d1["pos"]), (intersection.x, intersection.y)]).length
                    elif intersection.geom_type == "MultiPoint":
                        first_point = list(intersection.geoms)[0]
                        distance_to_intersection = LineString([tuple(d1["pos"]), (first_point.x, first_point.y)]).length
                    else:
                        distance_to_intersection = mesafe / 2
                    gecis_suresi = distance_to_intersection / drone_speed
                    gecis_saati = (datetime.strptime("10:00:00", "%H:%M:%S") + timedelta(seconds=gecis_suresi)).strftime("%H:%M:%S")
                    if zaman_cakisiyor(zone["active_time"], gecis_saati):
                        no_fly_penalty += 1000
                  
            maliyet += no_fly_penalty
            if enerji <= drone_battery:
                dynamic_graf[node_i].append((node_j, maliyet, enerji))

    return dynamic_graf

def yazdir_dynamic_graph(graf):
    for node_index, komsular in graf.items():
        if node_index < len(drones):
            for hedef, maliyet, enerji in komsular:
                teslimat_index = hedef - len(drones)
        else:
            kaynak_index = node_index - len(drones)
            for hedef, maliyet, enerji in komsular:
                hedef_index = hedef - len(drones)

import json
import math
from datetime import datetime, timedelta
from shapely.geometry import LineString, Polygon, Point

with open("randomdata.json", "r") as dosya:
    veri = json.load(dosya)

drones = veri["drones"]
deliveries = veri["deliveries"]
no_fly_zones = veri["no_fly_zones"]

def zaman_cakisiyor(zone_time, tahmini_zaman):
    fmt = "%H:%M:%S"
    bas = datetime.strptime(zone_time[0] + ":00", fmt)
    bit = datetime.strptime(zone_time[1] + ":00", fmt)
    an = datetime.strptime(tahmini_zaman, fmt)
    return bas <= an <= bit

def get_dynamic_graph_for(drone_index: int, target_delivery_index: int):
    hedef_agirlik = deliveries[target_delivery_index]["weight"]
    hedef_oncelik = deliveries[target_delivery_index]["priority"]
    drone_max_weight = drones[drone_index]["max_weight"]
    drone_battery = drones[drone_index]["battery"]
    drone_speed = drones[drone_index]["speed"]

    if hedef_agirlik > drone_max_weight:
        print(f"UYARI: Drone {drone_index} teslimat {target_delivery_index} paketini taşıyamaz! ({hedef_agirlik:.2f} kg > {drone_max_weight:.2f} kg)")
        return {}

    dynamic_graf = {drone_index: []}

    for j, delivery in enumerate(deliveries):
        delivery_node = j + len(drones)
        no_fly_penalty = 0

        start_pos = tuple(drones[drone_index]["start_pos"])
        end_pos = tuple(delivery["pos"])
        line = LineString([start_pos, end_pos])
        mesafe = line.length
        maliyet = mesafe * hedef_agirlik + (hedef_oncelik * 100)
        enerji = mesafe * hedef_agirlik * 10

        for zone in no_fly_zones:
            polygon = Polygon(zone["coordinates"])
            if line.intersects(polygon):
                intersection = line.intersection(polygon)
                if intersection.is_empty:
                    continue
                if intersection.geom_type == "Point":
                    distance_to_intersection = LineString([start_pos, (intersection.x, intersection.y)]).length
                elif intersection.geom_type == "MultiPoint":
                    first_point = list(intersection.geoms)[0]
                    distance_to_intersection = LineString([start_pos, (first_point.x, first_point.y)]).length
                else:
                    distance_to_intersection = mesafe / 2
                gecis_suresi = distance_to_intersection / drone_speed
                gecis_saati = (datetime.strptime("10:00:00", "%H:%M:%S") + timedelta(seconds=gecis_suresi)).strftime("%H:%M:%S")
                if zaman_cakisiyor(zone["active_time"], gecis_saati):
                    no_fly_penalty += 1000
                 

        maliyet += no_fly_penalty
        if enerji <= drone_battery:
            dynamic_graf[drone_index].append((delivery_node, maliyet, enerji))

    for i, d1 in enumerate(deliveries):
        node_i = i + len(drones)
        dynamic_graf.setdefault(node_i, [])

        for j, d2 in enumerate(deliveries):
            if i == j:
                continue
            node_j = j + len(drones)
            line = LineString([tuple(d1["pos"]), tuple(d2["pos"])])
            mesafe = line.length
            maliyet = mesafe * hedef_agirlik + (hedef_oncelik * 100)
            enerji = mesafe * hedef_agirlik * 10
            no_fly_penalty = 0
            for zone in no_fly_zones:
                polygon = Polygon(zone["coordinates"])
                if line.intersects(polygon):
                    intersection = line.intersection(polygon)
                    if intersection.is_empty:
                        continue
                    if intersection.geom_type == "Point":
                        distance_to_intersection = LineString([tuple(d1["pos"]), (intersection.x, intersection.y)]).length
                    elif intersection.geom_type == "MultiPoint":
                        first_point = list(intersection.geoms)[0]
                        distance_to_intersection = LineString([tuple(d1["pos"]), (first_point.x, first_point.y)]).length
                    else:
                        distance_to_intersection = mesafe / 2
                    gecis_suresi = distance_to_intersection / drone_speed
                    gecis_saati = (datetime.strptime("10:00:00", "%H:%M:%S") + timedelta(seconds=gecis_suresi)).strftime("%H:%M:%S")
                    if zaman_cakisiyor(zone["active_time"], gecis_saati):
                        no_fly_penalty += 1000
                  
            maliyet += no_fly_penalty
            if enerji <= drone_battery:
                dynamic_graf[node_i].append((node_j, maliyet, enerji))

    return dynamic_graf

def yazdir_dynamic_graph(graf):
    for node_index, komsular in graf.items():
        if node_index < len(drones):
            for hedef, maliyet, enerji in komsular:
                teslimat_index = hedef - len(drones)
        else:
            kaynak_index = node_index - len(drones)
            for hedef, maliyet, enerji in komsular:
                hedef_index = hedef - len(drones)
