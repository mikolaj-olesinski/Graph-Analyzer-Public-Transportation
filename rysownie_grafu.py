# import networkx as nx
# import matplotlib.pyplot as plt

# # Funkcja do filtrowania połączeń dla danej linii
# def filter_connections_for_line(stop_graph, line):
#     filtered_graph = {}
#     for stop, stop_obj in stop_graph.items():
#         # Filtrowanie przystanków, które mają połączenia z wybraną linią
#         has_connection = any(connection.line == line for connection in stop_obj.connections)
#         if has_connection:
#             filtered_graph[stop] = stop_obj
#     return filtered_graph

# # Funkcja do rysowania grafu
# def draw_graph(stop_graph, line=None):
#     G = nx.DiGraph()

#     # Filtruj dane, jeśli podano linię
#     if line:
#         stop_graph = filter_connections_for_line(stop_graph, line)

#     # Dodaj węzły do grafu
#     for stop, stop_obj in stop_graph.items():
#         G.add_node(stop, label=stop_obj.name, pos=(stop_obj.lon, stop_obj.lat))

#     # Dodaj krawędzie (połączenia) do grafu
#     for stop, stop_obj in stop_graph.items():
#         for connection in stop_obj.connections:
#             if line and connection.line == line:
#                 G.add_edge(connection.start.name, connection.end.name, label=connection.line)

#     # Pobieramy pozycje węzłów
#     pos = nx.get_node_attributes(G, 'pos')

#     if line:
#         plt.figure(figsize=(40, 40))
#     else:
#         plt.figure(figsize=(150, 150))
        
#     nx.draw(G, pos, with_labels=True, node_size=1000, node_color="lightblue", edge_color="gray", font_size=10, font_weight="bold", arrows=True)

#     # Etykiety krawędzi (linii)
#     edge_labels = nx.get_edge_attributes(G, 'label')
#     nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

#     plt.title(f"Graf przystanków i połączeń dla linii {line}" if line else "Graf wszystkich przystanków i połączeń")
#     plt.show()

# # Wywołanie funkcji:
# draw_graph(stop_graph, line="911")
