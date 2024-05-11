from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import BedrockChat
import numpy as np
from langchain_core.runnables import RunnablePassthrough
import eval.prompts
from eval.tools import cos_similarity
from ast import literal_eval

class Metric():
    
    def __init__(self, metric):
        self.metric = metric
        # verify the kind of metric passed is valid
        if metric not in eval.prompts.METRICS_DICT:
            raise ValueError('Invalid metric given:' + str(metric) + ' is not a valid metric type. Please specify a valid metric type.')
        else:
            criteria, examples, scale = eval.prompts.METRICS_DICT[metric]
            self.criteria = criteria
            self.examples = examples
            self.scale = scale
        return

    def _get_metric(self):
        return self.metric
    
    def metric_info(self):
        return self.criteria, self.examples, self.scale


class Evaluator():
    '''
    Use specified metrics to score RAG questions (w/ or w/out ground-truth depending on metric)
    
    init params
        model - string for model_id, claude 3 default
        batch - whether to evaluate a pd dataframe of RAG question/answers
        context - True if ground-truth / context provided for all questions
        metrics - list of metrics to use based on:
            precision: concisness + relevance
            correctness: 
            faithfulness (reference free): 
            context_relevancy:
    		answer_relevancy (reference free):
        data - list of strings in format: ['human_question', 'ai_response', 'context', 'truth']
                truth - optional ground truth required for 'correctness'
     '''

    def __init__(self, metrics, data, model="anthropic.claude-3-sonnet-20240229-v1:0"):
        self.model = model
        self.metrics = metrics
        self.data = data
    
    def _get_data(self):
        return self.data

    def _resolve_data(self):
        dtype = str(type(self._get_data()))
        if dtype == "<class 'dict'>":
            return 'dict'
        elif dtype == "<class 'pandas.core.frame.DataFrame'>" :
            return 'database'
        elif dtype == "<class 'list'>":
            return 'list'
        else:
            raise ValueError("Data type " + dtype + ' is not a supported data format.')
    
    def _get_model(self):
        return self.model
    
    def _get_metrics(self):
        return self.metrics

    def data(self):
        return self.data

    def evaluate(self):
        data_list= self._resolve_data()
        metrics = self._get_metrics()
        # set to a generic metric if none specified
        if metrics == 0:
            metrics = ['precision']
        else:
            pass

        llm = BedrockChat(
             credentials_profile_name="default", model_id=self._get_model(), verbose=True)

        scores = {}
        # calculate a score for each metric
        for metric_name in metrics:
            # initialize metric object
            metric = Metric(metric_name)
            criteria, examples, formatting = metric.metric_info()
            prompt = eval.prompts.GENERAL_PROMPT
            chain = ChatPromptTemplate.from_template(prompt) | llm | StrOutputParser()
        
            for data_list in self._get_data():
                input_dict = {
                        'criteria': criteria,
                        'examples': examples,
                        'formatting': formatting,
                        'question': data_list[0],
                        'response': data_list[1],
                        'context': data_list[2]
                    }
                # correctness requires additional calculations
                if metric_name == 'correctness':
                    semantic_similarity = cos_similarity([data_list[2], data_list[3]])
                    # for correctness, output will be "[TP, FP, FN]""
                    input_dict['truth'] = data_list[3]
                    evaluation = chain.invoke(input_dict)
                    f1_score = literal_eval(evaluation)
                    scores[metric_name] = (f1_score + semantic_similarity) / 2
                elif metric_name == 'context_relevancy':
                    # score using (# of relevant sentences in response)/(Total # of sentences)
                    evaluation = literal_eval(chain.invoke(input_dict))
                    scores[metric_name] = evaluation[0]/evaluation[1]
                elif metric_name == 'answer_relevancy':
                    # answer relevancy prompt will return default 3 questions:
                    evaluation = literal_eval(chain.invoke(input_dict))
                    relevancy = []
                    for q in evaluation:
                        # cosine similarity between original question, artificial questions
                        relevancy.append(cos_similarity([data_list[0], q]))
                    scores[metric_name] = sum(relevancy) / len(relevancy)
                elif metric_name == 'faithfulness':
                    # evaluation = [A, B]
                    evaluation = literal_eval(chain.invoke(input_dict))
                    scores[metric_name] = evaluation[1] / evaluation[0]
                else:
                    evaluation = chain.invoke(input_dict)
                    scores[metric_name] = evaluation

        self.results = scores
        return

    def load_scores(self):
        '''
        return each score (from 0-1) for each metric passed to init
        '''
        return self.results

    def total_score(self):
        '''
        calculate the average score across all metrics used, returns float from 0-1
        '''
        score = []
        for metric_name in self._get_metrics():
            score.append(float(self.results[metric_name]))
        self.total_score = np.average(score)
        return self.total_score
    
    def trace_scores(self, trace_id):
        '''
        
        '''
        return