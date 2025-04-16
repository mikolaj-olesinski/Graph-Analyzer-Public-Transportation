
This project contains an in-depth analysis of optimal route-finding in public transportation systems. It is organized into several key sections, each focusing on a different algorithm or method used for route optimization.

## Dijkstra's Algorithm
- **Overview:**  
  Implements the classic shortest path algorithm for weighted graphs with non-negative edge weights.
- **Functionality:**  
  - Starts at the source stop with a cost of 0.
  - Uses a priority queue to continuously choose the stop with the lowest current cost.
  - Updates the cost for each neighbor if a cheaper route is found.
- **Purpose:**  
  Guarantees the optimal solution in terms of route cost and serves as a baseline for comparing more advanced algorithms.

## A* Algorithm Variants
- **Overview:**  
  Enhances Dijkstra's approach by incorporating heuristic functions to predict the remaining cost from a given stop to the destination.
- **Implemented Variants & Their Functions:**  
  - **Time Penalty Function:** Optimizes for the fastest overall travel time by considering departure and arrival schedules.  
  - **Transfer Penalty Function:** Focuses on minimizing the number of transfers, even if it may increase the total travel cost.  
  - **Distance & Direction Penalty Functions:** Utilize geographical distance and routing direction to better balance travel cost and natural route flow.  
  - **Hybrid Penalty Function:** Combines distance and directional penalties to provide a balanced solution in terms of travel time, cost, and number of transfers.
- **Purpose:**  
  These variants allow for flexible optimization strategies depending on whether the priority is reducing travel time, cost, or the number of transfers.

## Tabu Search
- **Overview:**  
  Implements a metaheuristic method designed to overcome local optimum problems by using a memory structure (tabu list) to avoid revisiting recently explored solutions.
- **Implementation Details:**  
  - **Dynamic Tabu List:** The length of the tabu list adjusts based on the problem’s size, adapting the search intensity accordingly.
  - **Aspiration Criteria:** Permits overriding the tabu status if a move produces a solution that is better than the best known.
  - **Neighborhood Sampling Strategies:**  
    - **Swap:** Exchanges the positions of two stops.
    - **2-opt:** Reverses a segment of the route.
    - **Insert:** Moves a stop to a different position in the route.
    - **Hybrid & Adaptive:** Mix various strategies to increase diversification in the search.
- **Purpose:**  
  Provides a robust alternative to greedy search methods, seeking to optimize overall route efficiency by exploring a wider solution space.

## Key Findings
- **Algorithm Comparison:**  
  Testing on 20 randomly generated routes showed that some A* variants (especially those using distance and hybrid penalty functions) offer competitive route costs and significantly reduced computation times compared to Dijkstra's algorithm.
- **Trade-offs Identified:**  
  The A* variant minimizing transfers effectively reduces the number of transfers but generally incurs longer computation times.
- **Customization:**  
  The choice between algorithms can be tailored to specific priorities such as fastest computation time versus the lowest number of transfers, making the project versatile in addressing diverse public transportation challenges.
