def find_route(self, start_stop, end_stop, start_time, boarding_time=1):
    if not self._validate_stops(start_stop, end_stop):
        return None

    start_measure = time.time()
    
    travel_times, previous, arrival_times, previous_lines, current_time = self._initialize_search_structures(start_stop, start_time)
    
    open_set = [(0, 0, start_stop)]
    closed_set = set()
    
    best_cost = float('inf')  # najlepszy koszt dotarcia do celu

    while open_set:
        current_f, current_g, current_stop_name = heapq.heappop(open_set)
        
        # Jeśli koszt dotychczasowej ścieżki już przekracza najlepszy znaleziony, pomijamy ją
        if current_g > best_cost:
            continue
        
        if current_stop_name in closed_set:
            continue
        
        closed_set.add(current_stop_name)
        
        # Jeśli dotarliśmy do celu, aktualizujemy best_cost
        if current_stop_name == end_stop:
            best_cost = min(best_cost, current_g)
            # Możesz także przerwać, jeśli jesteś pewien, że dalsze szukanie nie poprawi wyniku
            continue
        
        current_stop = self.stop_graph[current_stop_name]
        current_arrival_time = arrival_times[current_stop_name]
        current_line = previous_lines[current_stop_name]
        
        grouped_connections = self._group_connections_by_destination(current_stop)
        
        for next_stop_name, conns in grouped_connections.items():
            if next_stop_name in closed_set:
                continue
            
            earliest_conn = find_earliest_connection(conns, current_arrival_time, previous_line=current_line, boarding_time=boarding_time)
            
            if earliest_conn is None:
                continue
            
            travel_time = (earliest_conn.arrival_time - current_arrival_time).total_seconds() / 60

            heuristic_args = {
                'current_line': current_line,
                'next_line': earliest_conn.line,
                'current_stop': current_stop,
                'end_stop': self.stop_graph[end_stop],
                'current_time': current_arrival_time,
                'start_time': start_time
            }
            h_cost = self.heuristic(**heuristic_args)
            
            new_g = current_g + travel_time
            f_cost = new_g + h_cost
            
            # Jeśli nowy koszt przekracza najlepszy znaleziony koszt, nie dodajemy tego węzła
            if new_g >= best_cost:
                continue
            
            if new_g < travel_times[next_stop_name]:
                travel_times[next_stop_name] = new_g
                previous[next_stop_name] = (current_stop_name, earliest_conn)
                arrival_times[next_stop_name] = earliest_conn.arrival_time
                previous_lines[next_stop_name] = earliest_conn.line
                
                heapq.heappush(open_set, (f_cost, new_g, next_stop_name))
    
    end_measure = time.time()
    
    if travel_times[end_stop] == float('inf'):
        print("DEBUG: Brak dostępnej trasy!")
        return None
    
    route = self._reconstruct_route(previous, end_stop)

    transfer_count = 0
    for i in range(1, len(route)):
        if route[i].line != route[i-1].line:
            transfer_count += 1
    
    hours = travel_times[end_stop] // 60
    minutes = travel_times[end_stop] % 60
    total_cost = f"{int(hours)}h {int(minutes)}min"
    
    return {
        'route': route,
        'total_cost': total_cost,
        'calculation_time': end_measure - start_measure,
        'transfers': transfer_count
    }
