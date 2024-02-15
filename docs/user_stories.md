## User Stories: 
Ashley is a student. She wants one place to access the LD50 value of chlorobenzene.
She needs the information to be easily accessible and reliable. Ashley needs it to 
be quick. Ashley is familiar with machine learning, but is unsure does not have any 
previous knowledge on toxiicity. She doesn’t know how to ask the questions (i.e., prompt engineering). 

Joe is a professor. Joe wants to check the safety requirements for 
experiments he will be running in his lab. He wants the mechanism for the adverse outcome pathway.
He wants to use chemicals that are not typical where the chemical information is more difficult to find. Joe is an 
expert in toxicology. 

Evan is a chef. Evan wants to check the dose that was perscribed to him by his doctor. He wants little technical information, that would be easy to understand. He wants an interface that is easily accessible and easy to use. He has has no medical background or any information on toxicology.

## Use Cases:
- Access toxicity information (e.g., lethal dose)
- Interpret medical figures
- Learn more about toxicology data
- Check the dose
- Confirm safety requirements
- Acessible for all skill levels

## Component Specifications:
Name: Document loaders
  What it does: Load data from a source, LC loaders: csv, html, json, md, pdf
  Inputs (with type information)
  Outputs (with type information)
  Components used:
  Side effects: memory consumption


Name: Text splitter
  What it does: Transform large text data into smaller pieces
  Inputs (with type information)
  Outputs (with type information)
  Components used:
  Side effects: 

Name: Data Storage/Embedding
  What it does: 
  Inputs (with type information)
  Outputs (with type information)
  Components used:
  Side effects:

Name: Data Retrieval
  What it does: 
  Inputs (with type information)
  Outputs (with type information)
  Components used:
  Side effects:

Name: Answer Generation
  What it does: 
  Inputs (with type information)
  Outputs (with type information)
  Components used:
  Side effects:

Name: Prompt Generation
  What it does: 
  Inputs (with type information)
  Outputs (with type information)
  Components used:
  Side effects:

Name: Model 

Name: Database
  What it does: 
  Inputs (with type information)
  Outputs (with type information)
  Components used:
  Side effects:
