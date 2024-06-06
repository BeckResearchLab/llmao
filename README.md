<p align="center">
  <img src="https://github.com/BeckResearchLab/llmao/blob/main/docs/logo.png" width="250" height="250">
</p>

# LLMao

**LLMao** is a data science graduate capstone project from the Chemical Engineering department at the University of Washington. 

**Goal of LLMao: Develop a large language model (LLM) that can perform retrieval augmented generation (RAG) with the adverse outcome pathway (AOP) database from the Environmental Protection Agency (EPA).**

## Quickstart

After cloning the repository, set up a conda environment using environment.yml:
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

Large language models (LLM) continue to be developed and are quickly integrating into our everyday lives. 

Many of these LLMs have been trained on a massive amount of data. While many LLMs offer a lot of knowledgeable scientific information, LLM can often be inaccurate or not providing enough information for the general public to understand complex scientific questions. 

Our group envisions to build a bridge between scientists (e.g., biologists and toxicologists) and the general population. Instead of searching through resources with confusing graphics to find out more about toxicology, we are hoping that they can turn to this specialized LLM that has access to a large number of textbooks, papers, journals, etc, and get the insightful, accurate, and concise information within a matter of seconds. 

## How this is being accomplished

To perform retrieval augmented generation (RAG) with the adverse outcome pathway (AOP) database, we are following the steps outlined in the figure below.

<p align="center">
  <img src="https://github.com/BeckResearchLab/llmao/assets/155478918/7c64c8b2-8341-48a2-bf76-f8d6c6793165">
</p>

We have been accomplishing this by using LangChain, which is a framework for developing applications powered by large language models (LLMs). Given that this project is a capstone project and the limited time we have, we are using an open-source LLM that has already been trained and evaluated. This has allowed us to directly connect the AOP database and perform RAG.

More information about LangChain: https://www.langchain.com

We are currently working with the adverse outcome pathway database (AOP-db) developed by the Environmental Protection Agency (EPA). This dataset has been chosen as this group is specifically building an LLM that is capable of answering domain-specific questions in the field of toxicology. 

Accessing AOP-DB: https://aopdb.epa.gov (The file size is around 16GB)

## Goals

Below are a few tasks that this group hopes to accomplish within the allotted time for this capstone project:
* Perform RAG with the LLM (i.e., verify that the LLM successfully connects to the AOP and can retrieve the necessary information and generate a response with context to the original question).
* Evaluate the model's responses based on various prompts. 
* Incorporate references into the model to provide the user with context on where the LLM is generating the response from.
* Perform fine-tuning on the model as necessary.

## Interested?
Interested in contributing to this project or have valuable insights that pertain to this project? Reach out using the pull requests! :)
