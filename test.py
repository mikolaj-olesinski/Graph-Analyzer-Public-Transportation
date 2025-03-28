import heapq
import time
import math
from datetime import datetime, timedelta

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Obliczenie odległości między punktami geograficznymi za pomocą formuły Haversine'a.
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    r = 6371
    return c * r

def advanced_route_heuristic(start_stop, end_stop, transfers=0, max_transfer_penalty=120):
    """
    Zaawansowana funkcja heurystyczna uwzgledniająca:
    1. Odległość geograficzną
    2. Koszt przesiadek
    3. Złożoność trasy
    """
    # Bazowa odległość geograficzna
    geographic_distance = haversine_distance(
        start_stop.lat, start_stop.lon, 
        end_stop.lat, end_stop.lon
    )
    
    # Kara za przesiadki - im więcej przesiadek, tym wyższy koszt
    transfer_cost = transfers * max_transfer_penalty
    
    # Złożoność trasy - preferowanie prostszych tras
    complexity_penalty = math.log(geographic_distance + 1) * 10
    
    # Dynamiczne ważenie składowych
    return (
        geographic_distance * 0.5 +   # Odległość geograficzna
        transfer_cost * 2 +            # Koszt przesiadek
        complexity_penalty             # Kara za złożoność
    )

import heapq
import time
from datetime import datetime