
# st.title("DisViz")

# st.subtitle()

# st.image("/home/ubuntu/llmao/docs/DisViz.png")

# st.write("""
# For our final project, we are using the Adverse Outcome Pathway (AOP) Wiki to allow users to utilize and dynamically create visualizations for this biological framework. 
# A unique AOP is defined by the adverse outcome and the molecular initiating event (MIE), where a chemical stressor interacts with a molecular level biological process. 
# The following key events, which may occur at difference biological scales, are linked together by key-event relationships and lead to an adverse outcome.
# We downloaded the AOP Wiki XML and query it using MongoDB, due to the complex, nested data structure. The prototype image shows 1 possible pathway, and future goals in the project
# are to utilize user input to allow for dynamic visualization of an entire adverse outcome pathway. The visualization itself is built using NetworkX, and we plan to host the final
# project on the website we are using for our shared Capstone project related to AOPs (llm-ao.com).
         
# To improve upon the project, our main goal will be to incorporate user input. The main challenge is that any sequence of MIE, key-events, and adverse outcome
# can be considered an AOP; we are struggling to determine how much flexibility the user should be given to create these visuals. For instance, should the user be able to
# select an 
# """)

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from textwrap import fill
from pymongo import MongoClient
import matplotlib.patches as mpatches

#st.header("Disease & Adverse Outcome Pathway Visualization")

# MongoDB connection
connect_string = st.secrets['connect_string'],
client = MongoClient(connect_string)
db = client["aop_wiki"]
key_event = db['key-event']

# Function to get available MIEs from the database
def get_available_mies():
    mies = key_event.find({"biological-organization-level": "Molecular"}, {"title": 1, "_id": 0})
    return [mie["title"] for mie in mies]

# Function to get available AOs from the database
def get_available_aos():
    aos = key_event.find({"biological-organization-level": "Individual"}, {"title": 1, "_id": 0})
    return [ao["title"] for ao in aos]

# Function to wrap text for labels
def wrap_label(text, width):
    return fill(text, width)

# Streamlit UI
st.title("Adverse Outcome Pathway Diagram Generator")

# Get available MIEs and AOs
available_mies = get_available_mies()
available_aos = get_available_aos()

# Searchable MIE input
mie_title = st.selectbox("Select or search for a Molecular Initiating Event (MIE):", available_mies)

# Text inputs for Key Events and searchable AO input
ke_titles = st.text_area("Enter Key Events (KEs) separated by commas:", "Inadequate DNA repair, Increase, Mutations, Increase Chromosomal Aberrations, Increased microRNA expression, Decreased SIRT1 expression, Increased activation, Nuclear factor kappa B (NF-kB), Antagonism, Estrogen receptor, Epithelial Mesenchymal Transition (EMT)")
ao_title = st.selectbox("Select or search for an Adverse Outcome (AO):", available_aos)

# Button to generate the diagram
if st.button("Generate Diagram"):
    # Process input
    ke_titles = [ke.strip() for ke in ke_titles.split(',')]

    # Initialize the graph
    G = nx.DiGraph()

    # Add the MIE node
    MIE_id = "MIE_" + mie_title.replace(" ", "_")
    G.add_node(MIE_id, title=f"MIE: {mie_title}", type="MIE")

    # Add the KE nodes and edges sequentially
    KE_ids = ["KE_" + ke.replace(" ", "_") for ke in ke_titles]
    for i, ke_title in enumerate(ke_titles):
        G.add_node(KE_ids[i], title=f"KE: {ke_title}", type="KE")
        if i == 0:
            G.add_edge(MIE_id, KE_ids[i])
        else:
            G.add_edge(KE_ids[i-1], KE_ids[i])

    # Add the AO node and edge from the last KE to AO
    AO_id = "AO_" + ao_title.replace(" ", "_")
    G.add_node(AO_id, title=f"AO: {ao_title}", type="AO")
    G.add_edge(KE_ids[-1], AO_id)

    # Wrap text for labels
    labels = {node: wrap_label(G.nodes[node]['title'], 25) for node in G.nodes}

    # Position the nodes vertically
    pos = {}
    row = 0
    for i, node in enumerate([MIE_id] + KE_ids + [AO_id]):
        pos[node] = (0, -row)
        row += 2

    color_map = {'MIE': 'green', 'KE': 'orange', 'AO': 'red'}
    node_colors = [color_map[G.nodes[node]['type']] for node in G.nodes]

    plt.figure(figsize=(8, 15))

    # Increase node size
    node_size = 3000

    # Draw larger white nodes for arrow gaps
    nx.draw_networkx_nodes(G, pos, node_color='white', node_size=node_size * 1.25, alpha=1, node_shape='s')

    # Draw colored nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_size, edgecolors='black', alpha=0.9, node_shape='s')

    # Draw edges with larger arrows
    nx.draw_networkx_edges(G, pos, edgelist=G.edges, node_size=node_size * 1.25, arrowstyle='->', arrowsize=15, width=2, edge_color='gray')

    # Draw labels
    for node, (x, y) in pos.items():
        plt.text(x, y, labels[node], horizontalalignment='center', verticalalignment='center',
                 bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'), fontsize=10)

    # Adding a legend
    green_patch = mpatches.Patch(color='green', label='Molecular Initiating Event (MIE)')
    orange_patch = mpatches.Patch(color='orange', label='Key Event (KE)')
    red_patch = mpatches.Patch(color='red', label='Adverse Outcome (AO)')
    plt.legend(handles=[green_patch, orange_patch, red_patch], loc='upper right', bbox_to_anchor=(1.2, 1))

    plt.title("Adverse Outcome Pathway Diagram for DNA damage and mutations leading to Metastatic Breast Cancer")
    plt.axis('off')
    st.pyplot(plt)