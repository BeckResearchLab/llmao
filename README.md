# LLMao

**LLMao** is a data science graduate capstone project from the Chemical Engineering department at the University of Washington. 

**Goal of LLaMo: Develop a large language model (LLM) that can perform retrieval augmented generation (RAG) with the adverse outcome pathway (AOP) database from the Environmental Protection Agency (EPA).**

## Instructions

After cloning the repository, set up a conda environment using environment.yml (use basic-rag branch for now):
```python
conda env create --file environment.yml
```

Set up your .aws config profile using either aws configure (via AWS CLI) or manually (for more info on AWS configuration: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html). 

To run the streamlit application, use:

```python
streamlit run main.py
```

To run the model without a GUI, use:
```python
python bedrock.py
```

![image](https://github.com/BeckResearchLab/llmao/assets/86797031/4dcd3322-6d92-40b6-ae6f-1d4b30eb2983)

## Motivation

Large language models (LLM) continue to be developed and are quickly becoming integrated into our everyday lives. 

Many of these LLMs have been trained on massive amounts of data. While many LLMs can offer a lot of knowledgeable scientific information, the LLM can often be inaccurate or not provide enough information for the general public to understand complex scientific questions. 

Our group hopes to build a bridge between scientists (e.g., biologists, and toxicologists) and the general population. Instead of the general public having to search through multiple textbooks with confusing graphics to find out more about toxicology, we are hoping that they can turn to this LLM that can sort through the massive amounts of textbooks, papers, journals, etc., to provide insightful, accurate, and concise information to these users within a matter of seconds. 

## How this is being accomplished

To perform retrieval augmented generation (RAG) with the adverse outcome pathway (AOP) database, we are following the steps outlined in the figure below.

![image](https://github.com/BeckResearchLab/llmao/assets/155478918/7c64c8b2-8341-48a2-bf76-f8d6c6793165)

We have been accomplishing this by using Langchain, which is a framework for developing applications powered by large language models (LLMS).

More information about Langchain: https://www.langchain.com

Given that this project is just a capstone project (at this current moment) and the limited time we have, we are currently using an open-source LLM that has already been trained and evaluated. This has allowed us to directly connect the AOP database with an open-source LLM and perform RAG.

We are currently working with the adverse outcome pathway (AOP) database (DB) developed by the Environmental Protection Agency (EPA).

Access to this AOP-DB: https://aopdb.epa.gov

This dataset has been chosen as this group is specifically building an LLM that is capable of answering domain-specific questions in the field of toxicology. 

## Goals

Below are a few tasks that this group hopes to accomplish within the allotted time for this capstone project:
* Perform basic RAG with the LLM (i.e., test that the LLM successfully connects to the AOP and can retrieve the necessary information and then generate a response with context to the original question).
* Evaluate the model's responses based on various prompts. Based on the model's response, we can successfully determine if the model will need fine-tuning.
* Incorporate references into the model to provide the user with more context on where the LLM is generating the response from.
* Perform fine-tuning on the model as necessary.

## Interested?
Interested in helping on this project or have any valuable insight that pertains to this project? Please reach out using the pull requests!
