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
from graphviz import Digraph
from PIL import Image
from io import BytesIO
import base64  # Import base64 module

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# MongoDB connection
connect_string = st.secrets['connect_string']

def get_mongo_client(connect_string, retries=5, delay=5):
    for attempt in range(retries):
        try:
            client = MongoClient(connect_string, serverSelectionTimeoutMS=20000)
            client.admin.command('ismaster')
            return client
        except ServerSelectionTimeoutError as err:
            print(f"Attempt {attempt + 1} of {retries} failed: {err}")
            time.sleep(delay)
    raise Exception(f"Failed to connect to MongoDB after {retries} attempts")

client = get_mongo_client(connect_string)
db = client["aop_wiki"]
key_event = db['key-event']

@st.cache_data
def get_available_mies():
    mies = key_event.find({"biological-organization-level": "Molecular"}, {"title": 1, "_id": 0})
    return [mie["title"] for mie in mies]

@st.cache_data
def get_available_aos():
    aos = key_event.find({"biological-organization-level": "Individual"}, {"title": 1, "_id": 0})
    return [ao["title"] for ao in aos]

@st.cache_data
def get_available_kes():
    kes = key_event.find({"biological-organization-level": {"$in": ["Cellular", "Tissue", "Organ"]}}, {"title": 1, "_id": 0})
    return [ke["title"] for ke in kes]

def wrap_label(text, width):
    return fill(text, width)

@st.cache_data
def fetch_verified_aops():
    url = "https://aopwiki.org/aops"
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    aops = []
    table = soup.find('table')
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 1:
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
    headers = ['Type', 'Event ID', 'Title', 'Short name']

    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if cells and cells[0].get_text(strip=True) in ['MIE', 'KE', 'AO']:
                cell_data = [cell.get_text(strip=True) for cell in cells]
                if len(cell_data) == len(headers):
                    print(f"Row data: {cell_data}")
                    data.append(cell_data)

    if not data:
        print("No data found in the 'Events' table.")

    return headers, data

def wrap_label2(text, width):
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > width:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word) + 1

    lines.append(' '.join(current_line))
    return '\n'.join(lines)

def generate_diagram(mie_title, ke_titles, ao_title, output_filename='aop_diagram'):
    ke_titles = [ke.strip() for ke in ke_titles]

    dot = Digraph()
    dot.attr(rankdir='TB')
    dot.attr('node', shape='rect', style='filled', color='black', fontname='Arial', fontsize='12')

    MIE_id = "MIE_" + mie_title.replace(" ", "_")
    dot.node(MIE_id, wrap_label2(mie_title, 25), color='green', style='filled', tooltip='MIE')

    KE_ids = ["KE_" + ke.replace(" ", "_") for ke in ke_titles]
    for i, ke_title in enumerate(ke_titles):
        dot.node(KE_ids[i], wrap_label2(ke_title, 25), color='yellow', style='filled', tooltip='Key Events')
        if i == 0:
            dot.edge(MIE_id, KE_ids[i])
        else:
            dot.edge(KE_ids[i-1], KE_ids[i])

    AO_id = "AO_" + ao_title.replace(" ", "_")
    dot.node(AO_id, wrap_label2(ao_title, 25), color='red', style='filled', tooltip='Adverse Outcome')
    dot.edge(KE_ids[-1], AO_id)

    with dot.subgraph(name='cluster_legend') as s:
        s.attr(rank='min', margin='0')
        s.node('legend', label=(
        '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4" BGCOLOR="white">'
        '<TR><TD COLSPAN="2" ALIGN="CENTER"><B>Legend</B></TD></TR>'
        '<TR><TD>Molecular Initiating Event (MIE)</TD><TD BGCOLOR="green"></TD></TR>'
        '<TR><TD>Key Event (KE)</TD><TD BGCOLOR="yellow"></TD></TR>'
        '<TR><TD>Adverse Outcome (AO)</TD><TD BGCOLOR="red"></TD></TR>'
        '<TR><TD>Key Event Relationship</TD>'
        '<TD ALIGN="CENTER"><FONT COLOR="black">&#8594;</FONT></TD></TR>'
        '</TABLE>>'
    ), shape='none')

    dot.render(output_filename, format='png', cleanup=True)
    img = Image.open(output_filename + '.png')

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return img_str


st.title("Adverse Outcome Pathway Diagram Generator")

st.markdown("""
**This work is being done as a shared capstone project in the Department of Chemical Engineering at the University of Washington.**

### What is an Adverse Outcome Pathway (AOP)?
An Adverse Outcome Pathway (AOP) is a conceptual framework that links a molecular-level perturbation to an adverse health effect. It is used to better understand the mechanisms through which chemicals cause harmful effects and to predict outcomes of chemical exposures.
The image below shows an example of visually representing AOPs:""")

st.image("/home/ubuntu/llmao/docs/AOP-chain diag.png", caption="General AOP Framework")

st.markdown("""
### Why are AOPs Important?
AOPs provide a structured way to organize biological information that can be used in chemical safety assessments and regulatory decisions. They help in identifying key events and processes that can be targeted for testing and intervention.

### Verified AOPs
The verified AOPs are experimentally validated pathways that have been reviewed and accepted by the scientific community. These pathways provide reliable information on how certain chemicals can lead to adverse health outcomes.

### Purpose
Given the complex nature of the Adverse Outcome Pathway (AOP) database from the Environmental Protection Agency (EPA) and the AOP-Wiki, we wanted to provide a framework for people to easily visualize the AOP. This website is helpful for researchers by allowing them to:

- Learn more information from a list of verified AOPs and generate AOP diagrams.
- Experiment with making their own AOP diagrams that have not been verified by scientists yet.

The dropdown menus for the MIE, KE, and AO are all verified potential options for each of them. This allows users to play with the full framework of each MIE, KE, and AO.
### How to Use This Tool
1. **Select Verified Pathway**:
   - Choose this option to select from a list of experimentally verified AOPs.
   - The list is fetched from the AOP-Wiki, a collaborative database that contains verified AOPs.
   - Select a pathway to see its details and generate a diagram based on the verified data.
            
2. **Create Custom Pathway**:
   - Use this option to build your own AOP by selecting a Molecular Initiating Event (MIE), Key Events (KEs), and an Adverse Outcome (AO).
   - You can specify the number of Key Events and choose them from the available list.
   - Click "Generate Diagram" to visualize the pathway.
""")

verified_aops = fetch_verified_aops()

option = st.radio("Choose an option:", ("Create Custom Pathway", "Select Verified Pathway"))

if option == "Select Verified Pathway":
    if verified_aops:
        selected_aop = st.selectbox("Select a Verified AOP:", list(verified_aops.keys()))
        selected_aop_url = verified_aops[selected_aop]
        st.write(f"More details: [Link]({selected_aop_url})")

        headers, data = fetch_aop_details(selected_aop_url)
        if data:
            df = pd.DataFrame(data, columns=headers)
            st.dataframe(df)

            try:
                mie_title = df[df['Type'] == 'MIE']['Title'].values[0]
                ke_titles = df[df['Type'] == 'KE']['Title'].values
                ao_title = df[df['Type'] == 'AO']['Title'].values[0]

                img_str = generate_diagram(mie_title, ke_titles, ao_title)

                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: center; position: relative;">
                        <img src="data:image/png;base64,{img_str}" alt="Generated Image">
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                with open('aop_diagram.png', 'rb') as f:
                    st.download_button(
                        label="Download Diagram",
                        data=f,
                        file_name='aop_diagram.png',
                        mime='image/png'
                    )
            except IndexError as e:
                st.error("Unable to extract necessary details from the selected AOP. Please check the data.")
                print("Error extracting MIE, KE, or AO:", e)
        else:
            st.write("No details available for the selected AOP.")
    else:
        st.write("No verified AOPs available.")
else:
    if option == "Create Custom Pathway":
        available_mies = get_available_mies()
        available_kes = get_available_kes()
        available_aos = get_available_aos()

        mie_title = st.selectbox("Select or search for a Molecular Initiating Event (MIE):", available_mies)
        num_kes = st.number_input("How many Key Events (KEs) do you want to add?", min_value=1, max_value=10, value=5)

        ke_titles = []
        for i in range(num_kes):
            ke_title = st.selectbox(f"Select or search for Key Event (KE) {i+1}:", available_kes, key=f"ke_{i}")
            ke_titles.append(ke_title)

        ao_title = st.selectbox("Select or search for an Adverse Outcome (AO):", available_aos)

        if st.button("Generate Diagram"):
            img_str = generate_diagram(mie_title, ke_titles, ao_title)

            st.markdown(
                f"""
                <div style="display: flex; justify-content: center; position: relative;">
                    <img src="data:image/png;base64,{img_str}" alt="Generated Image">
                </div>
                """,
                unsafe_allow_html=True
            )
            
            with open('aop_diagram.png', 'rb') as f:
                st.download_button(
                    label="Download Diagram",
                    data=f,
                    file_name='aop_diagram.png',
                    mime='image/png'
                )

# Citations section
st.markdown("""
### Citations
- [AOP Database](https://aopdb.epa.gov)
- [AOP-Wiki](https://aopwiki.org)
""")