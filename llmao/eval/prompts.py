GENERAL_PROMPT = """Your goal is to evaluate the AI response to the user's question based on the criterion listed below.
Ensure your response follows only the formatting guidelines specified in the prompt.

User question - {question}
AI response - {response}
Context - {context}
"""

PRECISION_CRITERA = """
A response is concise if it:
    - focuses on the main points relevant to the topic or question.
    - uses precise language and avoids unnecessary words or phrases.
    - omits irrelevant or extraneous details that don't contribute to the main point.
"""

PRECISION_EXAMPLES = """"
<example_1>
Question: 'Look up two chemicals in the AOP database'
Answer: 'Here are two chemicals found in the Adverse Outcome Pathway (AOP) database:
1. Bevonium (Chemical ID: MESH:C000002)
2. Insulin, neutral (Chemical ID: MESH:C000006)
Score: 1 </example1>
"""

FAITHFULNESS_CRITERIA = """
To find determine faithfulness, you must determine the following values, where A MUST be larger than Bw:
    A = Total number of claims in the AI response
    B = Number of claims in the AI response which can be inferred from the context.
"""

FAITHFULNESS_EXAMPLES = """
AI response: The query "SELECT AOP_id, AOP_name FROM aop_info LIMIT 5;" retrieves the AOP identification number and name for the first 5 entries in the aop_info table of the adverse outcome pathway database, and the results show the AOP IDs and names for those 5 entries, which include pathways related to liver damage, Parkinson's disease, ecdysis in insects, effects of pentachlorophenol, and PPARα antagonism leading to weight loss.
Context: The Adverse Outcome Pathway (AOP) database is a collection of information related to understanding how biological perturbations at the molecular level can lead to adverse outcomes at higher levels of biological organization. The query you provided shows a sampling of AOPs in the database, such as "Uncharacterized liver damage leading to hepatocellular carcinoma" and "Inhibition of the mitochondrial complex I of nigro-striatal neurons leads to parkinsonian motor deficits". These entries describe pathways by which an initial molecular event can cascade through biological processes to ultimately result in an adverse health effect. The purpose of compiling this information is to better understand mechanisms of toxicity and facilitate more predictive risk assessment for chemicals and other stressors. The AOP framework aims to connect data across multiple biological scales in a knowledgebase to improve environmental and human health decision-making.	
A = 7
B = 4
"""

CORRECTNESS_CRITERIA = """
Determine the following values to help the correctness:
    True Positives: Facts or statements that are present in both the ground truth and the ai answer
    False Positives: Facts or statements that are present in the ai answer but not in the ground truth
    False Negatives: Facts or statements that are present in the ground truth but not in the ai answer
"""

CORRECTNESS_EXAMPLES = """
"""

CONTEXT_RELEVANCY_CRITERIA = """"
Context relevancy requires noting when sentences from the retrieved context are relevant to the user's question.
To find the context relevancy, determine the following two values:
    S: The number of sentences in the retrieved context which are relevant to the user's question
    T: The total number of sentences in the retrieved context
"""

CONTEXT_RELEVANCY_EXAMPLES = """
Question: What is the capital of France?
High context relevancy: France, in Western Europe, encompasses medieval cities, alpine villages and Mediterranean beaches. Paris, its capital, is famed for its fashion houses, classical art museums including the Louvre and monuments like the Eiffel Tower.
Low context relevancy: France, in Western Europe, encompasses medieval cities, alpine villages and Mediterranean beaches. Paris, its capital, is famed for its fashion houses, classical art museums including the Louvre and monuments like the Eiffel Tower. The country is also renowned for its wines and sophisticated cuisine. Lascaux’s ancient cave drawings, Lyon’s Roman theater and the vast Palace of Versailles attest to its rich history.
"""

ANSWER_RELEVANCY_CRITERIA = """
Rather than evaluating the AI response, your goal is to generate questions from the AI answer.
Using the AI response only, try to reverse engineer the response to come up with 3 questions that
could be answered using the same AI response.
"""

ANSWER_RELEVANCY_EXAMPLES = """
        AI response: "The Adverse Outcome Pathway (AOP) database contains information about key events, molecular initiating events, and other relevant details related to toxicological pathways. The query you provided shows some example entries from the event_info table, which stores details about specific events involved in AOPs.
                        The results include events like reduction of estradiol synthesis by ovarian granulosa cells (a key event), decreased activity of an enzyme involved in fatty acid metabolism (also a key event), activation of a serotonin receptor (a molecular initiating event), accumulation of acetylcholine in synapses (a key event), and inhibition of acetylcholinesterase (a molecular initiating event).
                        For each event, the database stores information such as the event type (key event or molecular initiating event), the AOPs the event is involved in, the biological level the event occurs at (e.g. cellular, molecular), relevant biological processes, chemicals, proteins, cell types, tissues, and organs. This comprehensive information helps characterize the key events driving adverse outcomes related to chemical exposure and biological perturbations."
        Your response: ["How does the AOP database help in characterizing adverse outcomes related to chemical exposure and biological perturbations?",
                        "Can you provide examples of key events and molecular initiating events stored in the AOP database?", 
                        "What information does the Adverse Outcome Pathway (AOP) database contain?"]
"""

METRICS_DICT = {'precision': str((GENERAL_PROMPT, PRECISION_CRITERA, PRECISION_EXAMPLES, "Formatting: {format_instructions}")),
                'faithfulness': str( (GENERAL_PROMPT, FAITHFULNESS_CRITERIA, FAITHFULNESS_EXAMPLES, "Formatting: {format_instructions}")),
                'correctnesss': str((GENERAL_PROMPT, CORRECTNESS_CRITERIA, CORRECTNESS_EXAMPLES, "Formatting: {format_instructions}")),
                'context_relevancy':str((GENERAL_PROMPT, CONTEXT_RELEVANCY_CRITERIA, CONTEXT_RELEVANCY_EXAMPLES, "Formatting: {format_instructions}")),
                'answer_relevancy': str((GENERAL_PROMPT, ANSWER_RELEVANCY_CRITERIA, ANSWER_RELEVANCY_EXAMPLES, "Formatting: {format_instructions}"))}