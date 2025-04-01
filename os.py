class TSPSolver:
    def __init__(self, stop_graph, router):
        self.stop_graph = stop_graph
        self.router = router
        self.stops_cache = {}  

    def _validate_stops(self, stops_list):
        """Sprawdzenie, czy wszystkie przystanki istnieją w grafie."""
        for stop in stops_list:
            if stop not in self.stop_graph:
                print(f"ERROR: Przystanek {stop} nie istnieje w grafie.")
                return False
        return True

    def _find_route_between_stops(self, start_stop, end_stop, start_time, optimization_type='t'):
        """Znajdź najlepszą trasę między dwoma przystankami."""
        # Sprawdź, czy trasa jest w cache
        cache_key = (start_stop, end_stop, start_time.strftime('%H:%M:%S'), optimization_type)
        if cache_key in self.stops_cache:
            return self.stops_cache[cache_key]
        
        # Znajdź trasę
        route = self.router.find_route(start_stop, end_stop, start_time)
        
        # Dodaj wynik do cache
        self.stops_cache[cache_key] = route
        return route

    def _calculate_solution_cost(self, solution, start_time, optimization_type='t'):
        """Oblicz koszt rozwiązania (sekwencji przystanków)."""
        total_time = 0
        total_transfers = 0
        current_time = start_time
        previous_stop = solution[0]
        
        for next_stop in solution[1:]:
            route = self._find_route_between_stops(previous_stop, next_stop, current_time, optimization_type)
            
            if route is None:
                # Jeśli nie znaleziono trasy, zwróć maksymalny koszt
                return float('inf'), float('inf')
            
            # Handling different types of total_cost
            if isinstance(route['total_cost'], str):
                # Handle string format "Xh Ymin"
                route_time_parts = route['total_cost'].split()
                hours = int(route_time_parts[0].replace('h', ''))
                minutes = int(route_time_parts[1].replace('min', ''))
                route_time_minutes = hours * 60 + minutes
            elif isinstance(route['total_cost'], (int, float)):
                # Handle numeric format (assuming minutes)
                route_time_minutes = route['total_cost']
            else:
                # Unexpected format
                print(f"Unexpected total_cost format: {route['total_cost']}")
                return float('inf'), float('inf')
            
            total_time += route_time_minutes
            total_transfers += route['transfers']
            
            # Aktualizuj czas dla następnego odcinka
            last_connection = route['route'][-1]
            current_time = last_connection.arrival_time
            previous_stop = next_stop
        
        # Dodaj trasę powrotną do punktu początkowego
        return_route = self._find_route_between_stops(solution[-1], solution[0], current_time, optimization_type)
        
        if return_route is None:
            return float('inf'), float('inf')
        
        # Dodaj koszt trasy powrotnej
        if isinstance(return_route['total_cost'], str):
            route_time_parts = return_route['total_cost'].split()
            hours = int(route_time_parts[0].replace('h', ''))
            minutes = int(route_time_parts[1].replace('min', ''))
            route_time_minutes = hours * 60 + minutes
        elif isinstance(return_route['total_cost'], (int, float)):
            route_time_minutes = return_route['total_cost']
        else:
            print(f"Unexpected total_cost format: {return_route['total_cost']}")
            return float('inf'), float('inf')
        
        total_time += route_time_minutes
        total_transfers += return_route['transfers']
        
        return total_time, total_transfers

    def _get_solution_cost(self, solution, start_time, optimization_type):
        """Pobierz koszt rozwiązania na podstawie typu optymalizacji."""
        time_cost, transfers_cost = self._calculate_solution_cost(solution, start_time, optimization_type)
        return time_cost if optimization_type == 't' else transfers_cost

    def _generate_neighbors(self, solution, neighborhood_strategy='swap'):
        """Generuj sąsiednie rozwiązania na podstawie wybranej strategii."""
        neighbors = []
        n = len(solution)
        
        # Zawsze zachowaj pierwszy przystanek (punkt startowy) jako stały
        if neighborhood_strategy == 'swap':
            # Strategia zamiany: wymiana pozycji dwóch przystanków
            for i in range(1, n):
                for j in range(i+1, n):
                    neighbor = solution.copy()
                    neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                    neighbors.append(neighbor)
        
        elif neighborhood_strategy == '2-opt':
            # Strategia 2-opt: odwrócenie segmentu trasy
            for i in range(1, n-1):
                for j in range(i+1, n):
                    neighbor = solution.copy()
                    # Odwróć segment między i a j
                    neighbor[i:j+1] = neighbor[i:j+1][::-1]
                    neighbors.append(neighbor)
        
        elif neighborhood_strategy == 'insert':
            # Strategia wstawiania: przeniesienie przystanku na inną pozycję
            for i in range(1, n):
                for j in range(1, n):
                    if i != j:
                        neighbor = solution.copy()
                        stop = neighbor.pop(i)
                        neighbor.insert(j, stop)
                        neighbors.append(neighbor)
        
        elif neighborhood_strategy == 'hybrid':
            # Mieszanka strategii dla dywersyfikacji
            swap_neighbors = self._generate_neighbors(solution, 'swap')
            opt_neighbors = self._generate_neighbors(solution, '2-opt')
            insert_neighbors = self._generate_neighbors(solution, 'insert')
            
            # Losowo wybierz sąsiadów z każdej strategii
            neighbors.extend(random.sample(swap_neighbors, min(5, len(swap_neighbors))))
            neighbors.extend(random.sample(opt_neighbors, min(5, len(opt_neighbors))))
            neighbors.extend(random.sample(insert_neighbors, min(5, len(insert_neighbors))))
        
        elif neighborhood_strategy == 'adaptive':
            # Adaptacyjne próbkowanie w zależności od rozmiaru rozwiązania
            if n <= 5:
                # Dla małych problemów, użyj wszystkich sąsiadów
                neighbors = self._generate_neighbors(solution, 'swap')
                neighbors.extend(self._generate_neighbors(solution, '2-opt'))
            else:
                # Dla większych problemów, użyj losowej podgrupy
                subset_size = max(10, n)  # Co najmniej 10 sąsiadów
                
                # Generuj różne typy i wybieraj z nich próbki
                swap_neighbors = self._generate_neighbors(solution, 'swap')
                opt_neighbors = self._generate_neighbors(solution, '2-opt')
                
                if len(swap_neighbors) > 0:
                    neighbors.extend(random.sample(swap_neighbors, min(subset_size // 2, len(swap_neighbors))))
                if len(opt_neighbors) > 0:
                    neighbors.extend(random.sample(opt_neighbors, min(subset_size // 2, len(opt_neighbors))))
        
        return neighbors

    def _initialize_search_structures(self, start_stop, stops_to_visit):
        """Inicjalizacja struktur danych potrzebnych do przeszukiwania."""
        # Utwórz kompletną listę przystanków, w tym przystanek początkowy
        all_stops = [start_stop] + stops_to_visit
        
        # Inicjalizacja obecnego rozwiązania (zaczynając od przystanków w podanej kolejności)
        current_solution = all_stops.copy()
        
        return all_stops, current_solution

    def _reconstruct_full_route(self, best_solution, start_time, optimization_type):
        """Odtwarzanie pełnej trasy na podstawie najlepszego rozwiązania."""
        full_route = []
        total_time = 0
        total_transfers = 0
        current_time_obj = start_time
        previous_stop = best_solution[0]
        
        for next_stop in best_solution[1:] + [best_solution[0]]:  # Dodaj przystanek początkowy na końcu, aby zakończyć cykl
            route_segment = self._find_route_between_stops(previous_stop, next_stop, current_time_obj, optimization_type)
            
            if route_segment:
                full_route.extend(route_segment['route'])
                
                # Aktualizuj liczniki i czas - obsługa różnych formatów total_cost
                if isinstance(route_segment['total_cost'], str):
                    route_time_parts = route_segment['total_cost'].split()
                    hours = int(route_time_parts[0].replace('h', ''))
                    minutes = int(route_time_parts[1].replace('min', ''))
                    route_time_minutes = hours * 60 + minutes
                elif isinstance(route_segment['total_cost'], (int, float)):
                    route_time_minutes = route_segment['total_cost']
                else:
                    print(f"Unexpected total_cost format: {route_segment['total_cost']}")
                    route_time_minutes = 0
                
                total_time += route_time_minutes
                total_transfers += route_segment['transfers']
                
                # Aktualizuj czas bieżący dla następnego odcinka
                if route_segment['route']:
                    current_time_obj = route_segment['route'][-1].arrival_time
                
                previous_stop = next_stop
        
        # Oblicz całkowite metryki
        hours = total_time // 60
        minutes = total_time % 60
        total_cost = f"{int(hours)}h {int(minutes)}min"
        
        return full_route, total_cost, total_transfers

    def tabu_search(self, start_stop, stops_to_visit, start_time, optimization_type='t', 
                    max_iterations=100, tabu_size=None, aspiration=False, sampling_strategy='swap'):
        if not self._validate_stops([start_stop] + stops_to_visit):
            return None
            
        start_measure = time.time()
        
        # Inicjalizacja struktur wyszukiwania
        all_stops, current_solution = self._initialize_search_structures(start_stop, stops_to_visit)
        
        # Ustaw rozmiar tabu na podstawie rozmiaru problemu, jeśli nie określono
        if tabu_size is None:
            tabu_size = len(stops_to_visit)
        
        # Inicjalizacja najlepszego rozwiązania
        best_solution = current_solution.copy()
        best_cost = self._get_solution_cost(current_solution, start_time, optimization_type)
        
        # Inicjalizacja listy tabu jako deque dla efektywnych operacji FIFO
        tabu_list = deque(maxlen=tabu_size)
        
        # Śledzenie iteracji bez poprawy
        no_improvement_count = 0
        diversification_threshold = max(10, len(stops_to_visit) * 2)
        
        # Główna pętla algorytmu
        for iteration in range(max_iterations):
            # Generowanie sąsiadów
            neighbors = self._generate_neighbors(current_solution, sampling_strategy)
            
            # Znalezienie najlepszego sąsiada niebędącego tabu
            best_neighbor = None
            best_neighbor_cost = float('inf')
            
            for neighbor in neighbors:
                # Sprawdzenie, czy ruch jest tabu
                move_is_tabu = str(neighbor) in tabu_list
                
                # Obliczenie kosztu
                neighbor_cost = self._get_solution_cost(neighbor, start_time, optimization_type)
                
                # Sprawdzenie kryterium aspiracji: zaakceptuj ruch tabu, jeśli jest lepszy niż najlepsze rozwiązanie
                if aspiration and move_is_tabu and neighbor_cost < best_cost:
                    move_is_tabu = False
                
                # Aktualizacja najlepszego sąsiada, jeśli nie jest tabu lub spełnia aspirację
                if not move_is_tabu and neighbor_cost < best_neighbor_cost:
                    best_neighbor = neighbor
                    best_neighbor_cost = neighbor_cost
            
            # Jeśli nie znaleziono sąsiada niebędącego tabu, przerwij
            if best_neighbor is None:
                break
            
            # Aktualizacja bieżącego rozwiązania
            current_solution = best_neighbor
            
            # Dodanie do listy tabu
            tabu_list.append(str(current_solution))
            
            # Aktualizacja najlepszego rozwiązania, jeśli uległo poprawie
            if best_neighbor_cost < best_cost:
                best_solution = current_solution.copy()
                best_cost = best_neighbor_cost
                no_improvement_count = 0
            else:
                no_improvement_count += 1
            
            # Strategia dywersyfikacji: jeśli brak poprawy przez pewien czas, zaburz rozwiązanie
            if no_improvement_count >= diversification_threshold:
                # Wykonaj losową permutację na niestałej części rozwiązania
                shuffled_part = current_solution[1:]
                random.shuffle(shuffled_part)
                current_solution = [current_solution[0]] + shuffled_part
                no_improvement_count = 0
        
        end_measure = time.time()
        
        # Odtwarzanie pełnych szczegółów trasy
        full_route, total_cost, total_transfers = self._reconstruct_full_route(
            best_solution, start_time, optimization_type
        )
        
        # Zwróć szczegóły trasy
        return {
            'route': full_route,
            'total_cost': total_cost,
            'calculation_time': end_measure - start_measure,
            'transfers': total_transfers,
            'best_solution': best_solution
        }