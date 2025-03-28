class DijkstraRouter:
    def __init__(self, stop_graph):
        self.stop_graph = stop_graph

    def _validate_stops(self, start_stop, end_stop):
        if start_stop not in self.stop_graph or end_stop not in self.stop_graph:
            print("ERROR: Przystanek startowy lub końcowy nie istnieje w grafie.")
            return False
        return True

    def _initialize_search_structures(self, start_stop, start_time):
        base_date = datetime(2025, 1, 1)
        start_datetime = base_date.replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second)
        
        travel_times = {name: float('inf') for name in self.stop_graph}
        previous = {name: None for name in self.stop_graph}
        arrival_times = {name: None for name in self.stop_graph}
        previous_lines = {name: None for name in self.stop_graph}
        
        travel_times[start_stop] = 0
        arrival_times[start_stop] = start_datetime
        
        return travel_times, previous, arrival_times, previous_lines, start_datetime

    def _group_connections_by_destination(self, current_stop):
        grouped_connections = {}
        for conn in current_stop.connections:
            destination = conn.end.name
            if destination not in grouped_connections:
                grouped_connections[destination] = []
            grouped_connections[destination].append(conn)
        return grouped_connections

    def _reconstruct_route(self, previous, end_stop):
        route = []
        current = end_stop
        while current and previous[current]:
            prev_stop, conn = previous[current]
            route.append(conn)
            current = prev_stop
        route.reverse()
        return route

    def find_route(self, start_stop, end_stop, start_time, boarding_time=1):

        if not self._validate_stops(start_stop, end_stop):
            return None

        start_measure = time.time()

        # Inicjalizacja struktur wyszukiwania
        travel_times, previous, arrival_times, previous_lines, current_time = self._initialize_search_structures(start_stop, start_time)
        
        # Kolejka priorytetowa (open set) dla algorytmu Dijkstry
        open_set = [(0, start_stop)]
        # Zbiór odwiedzonych węzłów (closed set)
        closed_set = set()
        
        while open_set:
            current_travel_time, current_stop_name = heapq.heappop(open_set)
            
            # Jeśli przystanek już był przetwarzany, pomijamy go
            if current_stop_name in closed_set:
                continue
            
            # Dodajemy przystanek do zbioru zamkniętych
            closed_set.add(current_stop_name)
            
            # Jeśli dotarliśmy do celu, przerywamy pętlę
            if current_stop_name == end_stop:
                break
            
            current_stop = self.stop_graph[current_stop_name]
            current_arrival_time = arrival_times[current_stop_name]
            current_line = previous_lines[current_stop_name]
            
            # Grupowanie połączeń wg przystanków docelowych
            grouped_connections = self._group_connections_by_destination(current_stop)
            
            for next_stop_name, conns in grouped_connections.items():
                # Znajdź najwcześniejsze połączenie z uwzględnieniem zasad przesiadek
                earliest_conn = find_earliest_connection(
                    conns, current_arrival_time, 
                    previous_line=current_line, 
                    boarding_time=boarding_time
                )
                
                if earliest_conn is None:
                    continue
                
                travel_time = (earliest_conn.arrival_time - current_arrival_time).total_seconds() / 60
                
                # Aktualizujemy tylko, jeśli znaleziono szybszą trasę
                if current_travel_time + travel_time < travel_times[next_stop_name]:
                    travel_times[next_stop_name] = current_travel_time + travel_time
                    previous[next_stop_name] = (current_stop_name, earliest_conn)
                    arrival_times[next_stop_name] = earliest_conn.arrival_time
                    previous_lines[next_stop_name] = earliest_conn.line
                    
                    heapq.heappush(open_set, (travel_times[next_stop_name], next_stop_name))
        
        end_measure = time.time()
          
        if travel_times[end_stop] == float('inf'):
            print("DEBUG: Brak dostępnej trasy!")
            return None
        
        # Rekonstrukcja trasy
        route = self._reconstruct_route(previous, end_stop)
        
        # Obliczenie całkowitego czasu podróży
        hours = travel_times[end_stop] // 60
        minutes = travel_times[end_stop] % 60
        total_cost = f"{int(hours)}h {int(minutes)}min"
        
        return {
            'route': route,
            'total_cost': total_cost,
            'calculation_time': end_measure - start_measure,
            'transfers': None
        }