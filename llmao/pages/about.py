import streamlit as st

#title- Used to add title of app

st.title("What are Adverse Outcome Pathway?")

#Header

#st.header("Lets learn about Adverse Outcome Pathway")

#sub header
st.subheader("Adverse Outcome Pathway(AOP)")

#giving information to user
st.info("An Adverse Outcome Pathway (AOP) is a model that identifies a sequence of molecular and cellular events that may lead to adverse health effects in individuals and populations.An AOP maps out a sequence of biological events following an exposure that may result in illness or injury.")

#write
st.write("In very simple terms, one can think of an AOP like a domino effect - Chemical exposure leads to a biological change within a cell, and then a molecular initiating event (e.g., chemical binding to DNA) triggers more dominos to fall in a cascade of sequential key events (e.g., abnormal cell replication) along toxicity pathway.")
st.image("../docs/AOP-chain diag.png")

st.write("Alkylation of DNA(Deoxyribonucleic Acid) as molecule intiating event followed by key events of inadequate DNA repair and increase mutations leading adverse outcome with increased risk of cancer. ")
st.image("../docs/AOP-cancer.png")

#SubPart 1
st.markdown("### Who uses AOP's?")
st.markdown(":dna:")
st.info("AOP are used by toxicologist,chemical engineers ,biology, researchers and students")
st.write("The adverse outcome pathway database (AOP-DB) is an online database that combines different data types (AOP, gene, chemical, disease, and pathway) to identify the impacts of chemicals on human health and the environment. EPA developed the AOP-DB to better characterize adverse outcomes of toxicological interest that are relevant to human health and the environment.")
#Subpart 2
st.markdown("### Why AOP?")
st.markdown(":face_with_raised_eyebrow:")
st.info("An AOP maps out how a stressor (e.g. chemical) interacts within an organism to cause adverse effects. If the amount of the chemical is sufficient, then cells can be affected, which can then affect tissues (which are collections of cells), organs (which are collections of tissues), and, ultimately, the health of the organism or even the population as a whole.")
st.write("By understanding the individual key events, one can better understand what the health outcome will be. Information used to develop AOPs can come from in vitro assays, animal studies, and computational models. AOPs allow scientists to connect the in vitro results generated from rapid screening protocols to actual adverse outcomes.**")

#Subpart 2
st.markdown("### How to query AOP database in llm-ao?")
st.markdown(":magic_wand:")
st.info("There are 4 types of information associated with each AOP: genes, diseases, stressors, and the pathway.")
st.write("You can start learning by asking llm-ao any question from above and it will give you customised answer.")
st.write("LLM-AO,your AI expert in toxicology was built using acccurate data from AOP-DB using the following link: https://aopdb.epa.gov")
#Sucess message
st.success("Congrats!You have got it and ready to use it.")
