# [S14] Save Project Files

# Save accessibility benefit-cost table
accessibility_table.to_csv('accessibility_benefit_cost_table.csv', index=False, encoding='utf-8-sig')
print("Saved accessibility_benefit_cost_table.csv")

# Save road network data
import networkx as nx
nx.write_graphml(G_proj, 'hualien_network.graphml')
print("Saved hualien_network.graphml")

# Save dynamic network for reference
nx.write_graphml(G_dyn, 'hualien_network_dynamic.graphml')
print("Saved hualien_network_dynamic.graphml")

# Save top 5 bottleneck nodes as GeoJSON
top_5_gdf.to_file('top_5_bottleneck_nodes.geojson', driver='GeoJSON')
print("Saved top_5_bottleneck_nodes.geojson")

# Save rainfall simulation data
import json
with open('rainfall_simulation.json', 'w') as f:
    json.dump(rainfall_layer, f)
print("Saved rainfall_simulation.json")
