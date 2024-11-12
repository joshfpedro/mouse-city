import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import os

st.set_page_config(
    page_title="Mouse Social Connections",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🐭",
)

def load_interactions(filepath):
    return pd.read_parquet(filepath)

def create_network(df, pos, period, weight_type):
    # Set the background to GitHub dark theme
    net = Network(height="500px", width="100%", bgcolor="#0d1117", font_color="#000000", directed=False)
    
    # Keep the original node and edge styles
    net.set_options("""
    {
      "interaction": {
        "hover": true,
        "navigationButtons": false,
        "keyboard": true
      },
      "physics": {
        "stabilization": {
          "iterations": 1000
        },
        "barnesHut": {
          "gravitationalConstant": -20000,
          "centralGravity": 0.3,
          "springLength": 200,
          "springConstant": 0.04,
          "damping": 0.09,
          "avoidOverlap": 0.5
        }
      },
      "nodes": {
        "shape": "dot",
        "size": 10,
        "borderWidth": 1,
        "borderWidthSelected": 2,
        "color": {
          "highlight": {
            "border": "red",
            "background": "red"
          }
        },
        "font": {
          "size": 0
        }
      },
      "edges": {
        "color": {
          "color": "rgba(128,128,128,0.3)",
          "highlight": "red"
        },
        "smooth": {
          "type": "continuous"
        }
      }
    }
    """)

    period_df = df[df['Period'] == period]

    G = nx.Graph()
    for _, row in period_df.iterrows():
        mouse1 = row['Mouse1']
        mouse2 = row['Mouse2']
        interactions = row['Interactions']
        time_together = row['TimeTogether']
        G.add_edge(mouse1, mouse2, interactions=interactions, time=time_together)

    strengths = dict(G.degree(weight='time' if weight_type == 'Time Together' else 'interactions'))
    max_strength = max(strengths.values()) if strengths else 1
    node_sizes = {node: ((strengths.get(node, 0) / max_strength) * 4.5) ** 2 + 4 for node in G.nodes()}

    for node in G.nodes():
        net.add_node(
            node,
            label="",
            title=f"Mouse: {node}\nWeighted Degree: {strengths.get(node, 0):.2f}",
            size=node_sizes[node],
            borderWidth=1
        )

    weight_attr = 'time' if weight_type == 'Time Together' else 'interactions'
    weights = [data[weight_attr] for _, _, data in G.edges(data=True)]
    max_weight = max(weights) if weights else 1

    for edge in G.edges(data=True):
        source, target, data = edge
        weight = data[weight_attr]
        interactions = data['interactions']
        time_together = data['time']
        length = max(300 - (weight / max_weight) * 200, 50)
        width = (weight / max_weight) * 5
        net.add_edge(
            source,
            target,
            value=weight,
            title=f"Interactions: {interactions}\nTime Together: {time_together:.2f} minutes",
            length=length,
            width=width,
            color={'color': 'rgba(128,128,128,0.3)', 'highlight': 'red'}
        )

    custom_js = """
    <script type="text/javascript">
    document.addEventListener('DOMContentLoaded', function() {
        var network = document.getElementById('mynetwork').network;
        
        // Adjust the initial zoom level after stabilization
        network.once('stabilizationIterationsDone', function () {
            network.moveTo({
                position: {x: 0, y: 2},
                scale: 1.5,  // Adjust this value to set the desired zoom level
                animation: {
                    duration: 1000,
                    easingFunction: 'easeInOutQuad'
                }
            });
        });
        
        network.on("click", function(params) {
            if (params.nodes.length > 0) {
                var nodeId = params.nodes[0];
                var connectedEdges = network.getConnectedEdges(nodeId);
                network.body.data.edges.update(connectedEdges.map(function(edgeId) {
                    return {id: edgeId, color: 'red'};
                }));
                network.body.data.nodes.update({id: nodeId, color: {border: 'red', background: 'red'}});
                network.body.data.edges.forEach(function(edge) {
                    if (!connectedEdges.includes(edge.id)) {
                        network.body.data.edges.update({id: edge.id, color: 'rgba(128,128,128,0.3)'});
                    }
                });
                network.body.data.nodes.forEach(function(node) {
                    if (node.id !== nodeId) {
                        network.body.data.nodes.update({id: node.id, color: {border: '#000000', background: '#000000'}});
                    }
                });
            } else {
                network.body.data.edges.forEach(function(edge) {
                    network.body.data.edges.update({id: edge.id, color: 'rgba(128,128,128,0.3)'});
                });
                network.body.data.nodes.forEach(function(node) {
                    network.body.data.nodes.update({id: node.id, color: {border: '#000000', background: '#000000'}});
                });
            }
        });
    });
    </script>
    """

    html = net.generate_html()
    html = html.replace("</body>", f"{custom_js}</body>")

    return html

def main():
    st.title("📊 Mouse Social Connection Visualization")
    st.markdown("""
    This application visualizes the social connections between mice based on the frequency and time they spend together in the same cage.
    Explore different periods to see how interactions evolve over time.
    """)

    st.sidebar.header("Settings")

    data_path = 'data/processed/mouse_interactions_per_period.parquet'

    if not os.path.exists(data_path):
        st.sidebar.error(f"Data file not found at `{data_path}`. Please ensure the file exists in the specified directory.")
        st.stop()

    interactions_df = load_interactions(data_path)

    periods = sorted(interactions_df['Period'].unique())

    G_master = nx.Graph()
    G_master.add_nodes_from(interactions_df['Mouse1'].unique())
    G_master.add_nodes_from(interactions_df['Mouse2'].unique())
    pos = nx.spring_layout(G_master, seed=42)

    selected_period = st.sidebar.selectbox("Select Period", periods, index=0)

    weight_type = st.sidebar.selectbox("Edge Weight by", ["Interactions", "Time Together"], index=0)

    network_html = create_network(interactions_df, pos, selected_period, weight_type)

    st.components.v1.html(network_html, height=500, width=500, scrolling=True)

if __name__ == "__main__":
    main()