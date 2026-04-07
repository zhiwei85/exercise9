# [S13] Visualization - Isochrone Comparison
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import numpy as np

def visualize_isochrones_comparison(facility_id, facility_cent, t_short, t_long):
    """Create comprehensive isochrone visualization"""
    
    # Calculate isochrones
    reachable_before_short, _ = compute_isochrone(G_proj, facility_id, 'travel_time', t_short)
    reachable_before_long, _ = compute_isochrone(G_proj, facility_id, 'travel_time', t_long)
    reachable_after_short, _ = compute_isochrone(G_dyn, facility_id, 'travel_time_adj', t_short)
    reachable_after_long, _ = compute_isochrone(G_dyn, facility_id, 'travel_time_adj', t_long)
    
    # Create polygons
    poly_before_short, _ = nodes_to_polygon(G_proj, reachable_before_short)
    poly_before_long, _ = nodes_to_polygon(G_proj, reachable_before_long)
    poly_after_short, _ = nodes_to_polygon(G_dyn, reachable_after_short)
    poly_after_long, _ = nodes_to_polygon(G_dyn, reachable_after_long)
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'Isochrone Analysis - Facility Node {facility_id} (Centrality: {facility_cent:.4f})', fontsize=16)
    
    # Get road network for background
    gdf_edges, _ = ox.graph_to_gdfs(G_proj, nodes=False)
    
    # Plot 1: Pre-disaster Short
    ax = axes[0, 0]
    gdf_edges.plot(ax=ax, color='gray', linewidth=0.5, alpha=0.3)
    if poly_before_short:
        gpd.GeoDataFrame([poly_before_short], columns=['geometry']).plot(ax=ax, color='blue', alpha=0.3)
    gpd.GeoDataFrame([Point(G_proj.nodes[facility_id]['x'], G_proj.nodes[facility_id]['y'])], 
                   columns=['geometry']).plot(ax=ax, color='red', markersize=10)
    ax.set_title(f'Pre-disaster - {t_short/60:.0f}min')
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    
    # Plot 2: Pre-disaster Long
    ax = axes[0, 1]
    gdf_edges.plot(ax=ax, color='gray', linewidth=0.5, alpha=0.3)
    if poly_before_long:
        gpd.GeoDataFrame([poly_before_long], columns=['geometry']).plot(ax=ax, color='green', alpha=0.3)
    gpd.GeoDataFrame([Point(G_proj.nodes[facility_id]['x'], G_proj.nodes[facility_id]['y'])], 
                   columns=['geometry']).plot(ax=ax, color='red', markersize=10)
    ax.set_title(f'Pre-disaster - {t_long/60:.0f}min')
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    
    # Plot 3: Post-disaster Short
    ax = axes[1, 0]
    gdf_edges.plot(ax=ax, color='gray', linewidth=0.5, alpha=0.3)
    if poly_after_short:
        gpd.GeoDataFrame([poly_after_short], columns=['geometry']).plot(ax=ax, color='orange', alpha=0.3)
    gpd.GeoDataFrame([Point(G_dyn.nodes[facility_id]['x'], G_dyn.nodes[facility_id]['y'])], 
                   columns=['geometry']).plot(ax=ax, color='red', markersize=10)
    ax.set_title(f'Post-disaster - {t_short/60:.0f}min')
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    
    # Plot 4: Post-disaster Long
    ax = axes[1, 1]
    gdf_edges.plot(ax=ax, color='gray', linewidth=0.5, alpha=0.3)
    if poly_after_long:
        gpd.GeoDataFrame([poly_after_long], columns=['geometry']).plot(ax=ax, color='purple', alpha=0.3)
    gpd.GeoDataFrame([Point(G_dyn.nodes[facility_id]['x'], G_dyn.nodes[facility_id]['y'])], 
                   columns=['geometry']).plot(ax=ax, color='red', markersize=10)
    ax.set_title(f'Post-disaster - {t_long/60:.0f}min')
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    
    plt.tight_layout()
    plt.savefig(f'isochrone_comparison_node_{facility_id}.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Calculate and print statistics
    _, area_before_short = nodes_to_polygon(G_proj, reachable_before_short)
    _, area_before_long = nodes_to_polygon(G_proj, reachable_before_long)
    _, area_after_short = nodes_to_polygon(G_dyn, reachable_after_short)
    _, area_after_long = nodes_to_polygon(G_dyn, reachable_after_long)
    
    shrink_short = (1 - area_after_short / area_before_short) * 100 if area_before_short > 0 else 0
    shrink_long = (1 - area_after_long / area_before_long) * 100 if area_before_long > 0 else 0
    
    print(f"Facility {facility_id}:")
    print(f"  Short-range area: {area_before_short/1e6:.2f} km² -> {area_after_short/1e6:.2f} km² ({shrink_short:.1f}% shrink)")
    print(f"  Long-range area: {area_before_long/1e6:.2f} km² -> {area_after_long/1e6:.2f} km² ({shrink_long:.1f}% shrink)")

# Generate visualizations for all selected facilities
print("Generating isochrone visualizations...")
for facility_id, facility_cent in selected_facilities:
    t_short, t_long = get_adaptive_thresholds(G_proj, facility_id, 'travel_time')
    visualize_isochrones_comparison(facility_id, facility_cent, t_short, t_long)

print("All visualizations completed!")
