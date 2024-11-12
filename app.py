import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Set page config and theme
st.set_page_config(layout="wide", page_title="Mouse Activity Dashboard")
st.markdown("""
<style>
.stApp {
    background-color: #0d1117;
    color: #ffffff;
}
div[data-testid="stSelectbox"] {
    margin-left: 1em;
    max-width: 200px;
}
</style>
""", unsafe_allow_html=True)

# Colors and dimensions
BACKGROUND_COLOR = '#0d1117'
TEXT_COLOR = '#ffffff'
EDGE_COLOR = '#8b949e'
NETWORK_WIDTH = 4
NETWORK_HEIGHT = 2.5

@st.cache_data
def load_data():
    """Load all necessary data files"""
    interactions_df = pd.read_parquet('data/processed/rural/mouse_interactions.parquet')
    activity_data = pd.read_parquet('data/processed/rural/mouse_activity_histogram.parquet')
    cage_data = pd.read_parquet('data/processed/rural/mouse_cage_time_all_periods.parquet')
    return interactions_df, activity_data, cage_data

@st.cache_resource
def get_fixed_layout(interactions_df):
    """Calculate and store fixed node positions"""
    master_G = nx.Graph()
    for _, row in interactions_df.iterrows():
        master_G.add_edge(row['mouse1'], row['mouse2'])
    return nx.spring_layout(master_G, k=1, iterations=50)

def plot_social_network(interactions_df, period, width=NETWORK_WIDTH, height=NETWORK_HEIGHT):
    """Generate network plot with fixed positions"""
    fig, ax = plt.subplots(figsize=(width, height))
    plt.style.use('dark_background')
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    ax.set_facecolor(BACKGROUND_COLOR)
    
    # Get fixed positions for all nodes
    pos = get_fixed_layout(interactions_df)
    
    period_data = interactions_df[interactions_df['period'] == period]
    
    G = nx.Graph()
    for _, row in period_data.iterrows():
        G.add_edge(row['mouse1'], row['mouse2'], weight=row['interaction_count'])
    
    degree_cent = nx.degree_centrality(G)
    
    edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
    if edge_weights:
        max_weight = max(edge_weights)
        nx.draw_networkx_edges(G, pos, edge_color=EDGE_COLOR,
                             width=[w/max_weight*3 for w in edge_weights],
                             alpha=0.6)
    
    nx.draw_networkx_nodes(G, pos,
                          node_size=[600 * v for v in degree_cent.values()],
                          node_color=list(degree_cent.values()),
                          cmap='viridis')
    
    nx.draw_networkx_labels(G, pos, font_size=4,
                           font_color=TEXT_COLOR,
                           font_weight='bold')
    
    plt.title('Social Network - Period ' + str(period), color=TEXT_COLOR, pad=10, fontsize=10)
    plt.tight_layout(pad=0.5)
    return fig

def plot_activity_histogram(activity_data, period):
    """Generate plotly histogram"""
    period_data = activity_data[activity_data['Period'] == period]
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=period_data['Hours'],
        y=period_data['Avg_Moves'],
        histfunc='sum',
        nbinsx=int(period_data['Hours'].max()),
        name='Activity'
    ))
    
    fig.update_layout(
        title=dict(
            text=f'Activity Histogram - Period {period}',
            font=dict(size=10),
            y=0.95
        ),
        xaxis_title='Hours Since Period Start',
        yaxis_title='Average Moves per Mouse',
        plot_bgcolor=BACKGROUND_COLOR,
        paper_bgcolor=BACKGROUND_COLOR,
        font=dict(color=TEXT_COLOR, size=10),
        showlegend=False,
        height=250,
        width=820,
        margin=dict(t=30, b=20, l=50, r=20)
    )
    return fig

def plot_cage_heatmap(cage_data, period):
    """Generate plotly heatmap"""
    period_data = cage_data.loc[period]
    
    fig = go.Figure(data=go.Heatmap(
        z=period_data.values,
        x=period_data.columns,
        y=period_data.index,
        colorscale='Viridis'
    ))
    
    fig.update_layout(
        # title=dict(
        #     text='Cage Activity - Period ' + str(period),
        #     font=dict(size=10),
        #     y=0.95
        # ),
        xaxis_title='Cage',
        yaxis_title='Mouse ID',
        plot_bgcolor=BACKGROUND_COLOR,
        paper_bgcolor=BACKGROUND_COLOR,
        font=dict(color=TEXT_COLOR, size=10),
        height=800,
        width=400,
        yaxis=dict(scaleanchor='x'),
        margin=dict(t=30, b=20, l=50, r=50),
        coloraxis_colorbar=dict(
            lenmode='fraction',
            len=0.75,
            yanchor='middle',
            y=0.5,
            thickness=15,
            title=dict(text='Minutes', side='right')
        )
    )
    return fig

def main():
    # Load data
    interactions_df, activity_data, cage_data = load_data()
    
    # Create two main columns with custom width ratio
    left_col, right_col = st.columns([2.5, 1.5])
    
    with left_col:
        # Period selector at top
        periods = sorted(interactions_df['period'].unique())
        selected_period = st.selectbox("Select Period", periods)
        
        # Network graph
        network_fig = plot_social_network(interactions_df, selected_period)
        st.pyplot(network_fig, use_container_width=False)
        
        # Histogram
        hist_fig = plot_activity_histogram(activity_data, selected_period)
        st.plotly_chart(hist_fig, use_container_width=False)
    
    with right_col:
        heatmap_fig = plot_cage_heatmap(cage_data, selected_period)
        st.plotly_chart(heatmap_fig, use_container_width=False)

if __name__ == "__main__":
    main()