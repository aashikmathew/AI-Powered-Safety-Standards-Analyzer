# safety_standards_analyzer/components/visualization.py

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from typing import List, Dict, Any

def create_gap_visualization(gaps: List[Dict[str, Any]]):
    """
    Create a visualization of identified gaps by risk level and domain.
    
    Args:
        gaps: List of gap dictionaries
        
    Returns:
        Matplotlib figure
    """
    # Extract domains and risk levels
    domains = list(set(gap["domain"] for gap in gaps))
    risk_levels = ["High", "Medium", "Low"]
    
    # Create data structure for visualization
    data = np.zeros((len(domains), len(risk_levels)))
    
    # Populate data
    for gap in gaps:
        domain_idx = domains.index(gap["domain"])
        risk_idx = risk_levels.index(gap["risk_level"])
        data[domain_idx, risk_idx] += 1
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create heatmap
    im = ax.imshow(data, cmap="YlOrRd")
    
    # Configure axes
    ax.set_xticks(np.arange(len(risk_levels)))
    ax.set_yticks(np.arange(len(domains)))
    ax.set_xticklabels(risk_levels)
    ax.set_yticklabels(domains)
    
    # Rotate x-axis labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.set_label("Number of Gaps")
    
    # Add title and labels
    ax.set_title("Safety Standard Gaps by Domain and Risk Level")
    ax.set_xlabel("Risk Level")
    ax.set_ylabel("Technology Domain")
    
    # Add text annotations
    for i in range(len(domains)):
        for j in range(len(risk_levels)):
            text = ax.text(j, i, int(data[i, j]),
                          ha="center", va="center", color="black")
    
    fig.tight_layout()
    return fig

def create_standards_network(network_data: Dict[str, Any]):
    """
    Create a network visualization of standards relationships.
    
    Args:
        network_data: Dictionary with nodes and edges
        
    Returns:
        Matplotlib figure
    """
    # Create graph
    G = nx.Graph()
    
    # Add nodes
    for node in network_data.get("nodes", []):
        G.add_node(node["id"], label=node["label"], size=node.get("size", 1))
    
    # Add edges
    for edge in network_data.get("edges", []):
        G.add_edge(edge["source"], edge["target"], weight=edge.get("weight", 1))
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Draw graph
    pos = nx.spring_layout(G, seed=42)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, ax=ax, 
                          node_size=[G.nodes[n].get("size", 1) * 300 for n in G.nodes],
                          node_color="skyblue")
    
    # Draw edges with width based on weight
    nx.draw_networkx_edges(G, pos, ax=ax,
                          width=[G[u][v].get("weight", 1) * 2 for u, v in G.edges])
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, ax=ax, 
                           labels={n: G.nodes[n].get("label", n) for n in G.nodes})
    
    # Set title
    ax.set_title("Standards Relationship Network")
    
    # Remove axis
    ax.axis("off")
    
    fig.tight_layout()
    return fig