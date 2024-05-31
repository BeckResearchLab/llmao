import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from textwrap import fill
from pymongo import MongoClient
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import requests
from bs4 import BeautifulSoup
import urllib3
import pandas as pd
import time
from pymongo.errors import ServerSelectionTimeoutError


# with st.sidebar:
st.logo("/home/ubuntu/llmao/docs/logo.png")

connect_string = st.secrets['connect_string']

# Disable SSL warnings# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# MongoDB connection

def get_mongo_client(connect_string, retries=5, delay=5):
    for attempt in range(retries):
        try:
            client = MongoClient(connect_string, serverSelectionTimeoutMS=20000)
            # The ismaster command is cheap and does not require auth
            client.admin.command('ismaster')
            return client
        except ServerSelectionTimeoutError as err:
            print(f"Attempt {attempt + 1} of {retries} failed: {err}")
            time.sleep(delay)
    raise Exception(f"Failed to connect to MongoDB after {retries} attempts")

client = get_mongo_client(connect_string)
db = client["aop_wiki"]
key_event = db['key-event']

# Function to get available MIEs from the database
@st.cache_data
def get_available_mies():
    mies = key_event.find({"biological-organization-level": "Molecular"}, {"title": 1, "_id": 0})
    return [mie["title"] for mie in mies]

# Function to get available AOs from the database
@st.cache_data
def get_available_aos():
    aos = key_event.find({"biological-organization-level": "Individual"}, {"title": 1, "_id": 0})
    return [ao["title"] for ao in aos]

# Function to get available KEs from the database
@st.cache_data
def get_available_kes():
    kes = key_event.find({"biological-organization-level": {"$in": ["Cellular", "Tissue", "Organ"]}}, {"title": 1, "_id": 0})
    return [ke["title"] for ke in kes]

# Function to wrap text for labels
def wrap_label(text, width):
    return fill(text, width)

# Function to fetch verified AOPs
@st.cache_data
def fetch_verified_aops():
    url = "https://aopwiki.org/aops"
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Parse the verified AOPs (adjust the selector based on actual HTML structure)
    aops = []
    table = soup.find('table')  # Locate the table containing AOPs
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 1:  # Adjust based on actual class attribute or structure
                title = cells[1].text.strip()
                link = cells[1].find('a')['href']
                aops.append((title, f"https://aopwiki.org{link}"))
    return dict(aops)

@st.cache_data
def fetch_aop_details(aop_url):
    response = requests.get(aop_url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    tables = soup.find_all('table')
    data = []
    headers = ['Type', 'Event ID', 'Title', 'Short name']  # Define expected headers

    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if cells and cells[0].get_text(strip=True) in ['MIE', 'KE', 'AO']:
                cell_data = [cell.get_text(strip=True) for cell in cells]
                if len(cell_data) == len(headers):
                    print(f"Row data: {cell_data}")  # Debug statement to print row data
                    data.append(cell_data)

    if not data:
        print("No data found in the 'Events' table.")

    return headers, data

@st.cache_data
def fetch_relationship_data(aop_url):
    response = requests.get(aop_url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the "Relationship Between Two Key Events" table by looking for specific keywords in headers
    tables = soup.find_all('table')
    data = []
    headers = ['Title', 'Adjacency', 'Evidence', 'Quantitative Understanding']  # Define expected headers

    for idx, table in enumerate(tables):
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if cells and any('leads to' in cell.get_text(strip=True) for cell in cells):
                cell_data = [cell.get_text(strip=True) for cell in cells]
                if len(cell_data) == len(headers):
                    print(f"Row data: {cell_data}")  # Debug statement to print row data
                    data.append(cell_data)

    if not data:
        print("No data found in the 'Relationship Between Two Key Events' table.")

    return headers, data

def generate_diagram(mie_title, ke_titles, ao_title):
    # Process input
    ke_titles = [ke.strip() for ke in ke_titles]

    # Initialize the graph
    G = nx.DiGraph()

    # Add the MIE node
    MIE_id = "MIE_" + mie_title.replace(" ", "_")
    G.add_node(MIE_id, title=f"{mie_title}", type="MIE")

    # Add the KE nodes and edges sequentially
    KE_ids = ["KE_" + ke.replace(" ", "_") for ke in ke_titles]
    for i, ke_title in enumerate(ke_titles):
        G.add_node(KE_ids[i], title=f"{ke_title}", type="KE")
        if i == 0:
            G.add_edge(MIE_id, KE_ids[i])
        else:
            G.add_edge(KE_ids[i-1], KE_ids[i])

    # Add the AO node and edge from the last KE to AO
    AO_id = "AO_" + ao_title.replace(" ", "_")
    G.add_node(AO_id, title=f"{ao_title}", type="AO")
    G.add_edge(KE_ids[-1], AO_id)

    # Wrap text for labels
    labels = {node: wrap_label(G.nodes[node]['title'], 25) for node in G.nodes}

    # Position the nodes vertically with dynamic spacing
    pos = {}
    row = 0
    spacing = 4  # Fixed spacing between nodes
    for i, node in enumerate([MIE_id] + KE_ids + [AO_id]):
        pos[node] = (0, -row)
        row += spacing

    color_map = {'MIE': 'green', 'KE': 'orange', 'AO': 'red'}
    node_colors = [color_map[G.nodes[node]['type']] for node in G.nodes]

    # Dynamically adjust the figure size based on the number of key events
    fig_height = 3 + len(KE_ids) * 2
    plt.figure(figsize=(8, fig_height))

    # Increase node size and spacing
    node_size = 5000

    # Draw larger white nodes for arrow gaps
    nx.draw_networkx_nodes(G, pos, node_color='white', node_size=node_size * 1.5, alpha=1, node_shape='s')

    # Draw colored nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_size, edgecolors='black', alpha=0.9, node_shape='s')

    # Draw edges with larger arrows
    nx.draw_networkx_edges(G, pos, edgelist=G.edges, node_size=node_size * 1.5, arrowstyle='->', arrowsize=20, width=2, edge_color='black')

    # Draw labels
    for node, (x, y) in pos.items():
        plt.text(x, y, labels[node], horizontalalignment='center', verticalalignment='center',
                 bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'), fontsize=10)

    # Adding a legend
    green_patch = mpatches.Patch(color='green', label='Molecular Initiating Event (MIE)')
    orange_patch = mpatches.Patch(color='orange', label='Key Event (KE)')
    red_patch = mpatches.Patch(color='red', label='Adverse Outcome (AO)')
    arrow_line = mlines.Line2D([], [], color='black', marker='>', linestyle='-', markersize=10, label='Key Event Relationship')
    plt.legend(handles=[green_patch, orange_patch, red_patch, arrow_line], loc='upper right', bbox_to_anchor=(1.2, 1))

    plt.title("Adverse Outcome Pathway Diagram")
    plt.axis('off')
    st.pyplot(plt)

    # Save the plot as an image
    import io
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)

    # Provide a download button for the image
    st.download_button(
        label="Download Diagram",
        data=buf,
        file_name='aop_diagram.png',
        mime='image/png'
    )

def generate_diagram_with_relationships(mie_title, ke_titles, ao_title, relationships):
    generate_diagram(mie_title, ke_titles, ao_title)

    # Display relationship information
    st.markdown("### Relationships Between Key Events")
    for rel in relationships:
        st.write(f"{rel[0]}: {rel[1]} (Evidence: {rel[2]}, Quantitative Understanding: {rel[3]})")

# Streamlit UI
st.title("Adverse Outcome Pathway Diagram Generator")

st.markdown("""
### What is an Adverse Outcome Pathway (AOP)?
An Adverse Outcome Pathway (AOP) is a conceptual framework that links a molecular-level perturbation to an adverse health effect. It is used to better understand the mechanisms through which chemicals cause harmful effects and to predict outcomes of chemical exposures.

### Why are AOPs Important?
AOPs provide a structured way to organize biological information that can be used in chemical safety assessments and regulatory decisions. They help in identifying key events and processes that can be targeted for testing and intervention.

### How to Use This Tool
1. **Create Custom Pathway**:
   - Use this option to build your own AOP by selecting a Molecular Initiating Event (MIE), Key Events (KEs), and an Adverse Outcome (AO).
   - You can specify the number of Key Events and choose them from the available list.
   - Click "Generate Diagram" to visualize the pathway.

2. **Select Verified Pathway**:
   - Choose this option to select from a list of experimentally verified AOPs.
   - The list is fetched from the AOP-Wiki, a collaborative database that contains verified AOPs.
   - Select a pathway to see its details and generate a diagram based on the verified data.

### Verified AOPs
The verified AOPs are experimentally validated pathways that have been reviewed and accepted by the scientific community. These pathways provide reliable information on how certain chemicals can lead to adverse health outcomes.
""")

# Fetch verified AOPs
verified_aops = fetch_verified_aops()

# Add option to select a verified AOP
option = st.radio("Choose an option:", ("Create Custom Pathway", "Select Verified Pathway"))

if option == "Select Verified Pathway":
    if verified_aops:
        selected_aop = st.selectbox("Select a Verified AOP:", list(verified_aops.keys()))
        selected_aop_url = verified_aops[selected_aop]
        st.write(f"More details: [Link]({selected_aop_url})")

        # Fetch and display AOP details
        headers, data = fetch_aop_details(selected_aop_url)
        if data:
            df = pd.DataFrame(data, columns=headers)
            st.dataframe(df)

            try:
                # Extract MIE, KEs, and AO for the diagram
                mie_title = df[df['Type'] == 'MIE']['Title'].values[0]
                ke_titles = df[df['Type'] == 'KE']['Title'].values
                ao_title = df[df['Type'] == 'AO']['Title'].values[0]

                # Fetch relationship data
                relationship_headers, relationship_data = fetch_relationship_data(selected_aop_url)
                generate_diagram_with_relationships(mie_title, ke_titles, ao_title, relationship_data)
            except IndexError as e:
                st.error("Unable to extract necessary details from the selected AOP. Please check the data.")
                print("Error extracting MIE, KE, or AO:", e)
        else:
            st.write("No details available for the selected AOP.")
    else:
        st.write("No verified AOPs available.")
else:
    # Custom Pathway Section
    if option == "Create Custom Pathway":
        # Get available MIEs, KEs, and AOs
        available_mies = get_available_mies()
        available_kes = get_available_kes()
        available_aos = get_available_aos()

        # Searchable MIE input
        mie_title = st.selectbox("Select or search for a Molecular Initiating Event (MIE):", available_mies)

        # Allow the user to specify the number of KEs
        num_kes = st.number_input("How many Key Events (KEs) do you want to add?", min_value=1, max_value=10, value=5)

        # Searchable KE inputs
        ke_titles = []
        for i in range(num_kes):
            ke_title = st.selectbox(f"Select or search for Key Event (KE) {i+1}:", available_kes, key=f"ke_{i}")
            ke_titles.append(ke_title)

        # Searchable AO input
        ao_title = st.selectbox("Select or search for an Adverse Outcome (AO):", available_aos)

        # Button to generate the diagram
        if st.button("Generate Diagram"):
            generate_diagram(mie_title, ke_titles, ao_title)

            # Display adjacency information
            if verified_aops:
                selected_aop_url = verified_aops.get(list(verified_aops.keys())[0])
                if selected_aop_url:
                    relationship_headers, relationship_data = fetch_relationship_data(selected_aop_url)
                    adjacency_dict = {(rel[0], rel[0].split(" leads to ")[1]): rel[1] for rel in relationship_data if " leads to " in rel[0]}
                    for i in range(len(ke_titles) - 1):
                        pair = (ke_titles[i], ke_titles[i + 1])
                        if pair in adjacency_dict:
                            st.write(f"The relationship between '{pair[0]}' and '{pair[1]}' is: {adjacency_dict[pair]}")
                        else:
                            st.write(f"The relationship between '{pair[0]}' and '{pair[1]}' has not been verified.")