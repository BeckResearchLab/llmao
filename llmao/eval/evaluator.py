from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_community.chat_models import BedrockChat
import eval.prompts
from eval.metrics import PARSER_DICT
from langfuse.decorators import langfuse_context
from typing import Optional
from pydantic import BaseModel, computed_field
from langchain_core.exceptions import OutputParserException

class _Metric_Handler():
    '''
    Handler class maps user input (metric name) to a LLMao metric object using the PARSER_DICT
    '''
    def __init__(self, metric):
        self.metric = metric
        # verify the kind of metric passed is valid
        if metric not in eval.prompts.METRICS_DICT:
            raise ValueError('Invalid metric given:' + str(metric) + ' is not a valid metric type. Please specify a valid metric type.')
        else:
            self.prompt = eval.prompts.METRICS_DICT[metric]
        return
    
    def _get_metric(self):
        return self.metric
    
    def get_parser(self):    
        return PydanticOutputParser(pydantic_object=PARSER_DICT[self.metric])
    
    def get_metric_prompt(self):
        return self.prompt
    
class Evaluator(BaseModel):
    '''
    Use specified metrics to score RAG questions (w/ or w/out ground-truth depending on metric)
    
    init params
        model - string for model_id, claude 3 default
        batch - whether to evaluate a pd dataframe of RAG question/answers
        metrics - list of metrics to use based on:
            precision: concisness + relevance
            correctness: 
            faithfulness (reference free): 
            context_relevancy (reference free):
    		answer_relevancy (reference free):
        data - list of lists in format: ['human_question', 'ai_response', 'context', 'truth']
                truth - optional ground truth required for 'correctness'
        batch - 
     '''
    
    metrics: list[str] = ["faithfulness", "answer_relevancy"]
    data: list[list]
    output: Optional[str] = "dict"
    model: Optional[str] = "anthropic.claude-3-sonnet-20240229-v1:0"
    batch: Optional[bool] = False

    def _get_data(self):
        return self.data
    
    def _get_model(self):
        return self.model
    
    def _get_metrics(self):
        return self.metrics
    
    def _get_output(self):
        return self.output

    def _get_data(self):
        return self.data
    
    @computed_field
    @property
    def _evaluate(self) -> dict:
        #metrics = self._get_metrics()
        model = "anthropic.claude-3-haiku-20240307-v1:0"
        llm = BedrockChat(credentials_profile_name="default", model_id=model, verbose=True)
        #llm = Bedrock(credentials_profile_name="default", model_id="mistral.mixtral-8x7b-instruct-v0:1", verbose=True)
        # llm = Bedrock(credentials_profile_name="default", model_id=self._get_model(), verbose=True)

        if self.batch:
            scores_list = []

        # iterate through each entry of question, answer, context for each passed metric
        for data_list in self._get_data():
            input_dict = {
                        'question': data_list[0],
                        'response': data_list[1],
                        'context': data_list[2]
                        }

            scores = {} # define score for each entry

            for metric_name in self._get_metrics():
                # initialize _Metric_Handler object
                metric = _Metric_Handler(metric_name)
                prompt = metric.get_metric_prompt()
                # get output parser based on the metric type
                parser = metric.get_parser()
                prompt_template = PromptTemplate(template=prompt,
                                                input_variables=list(input_dict.keys()),
                                                partial_variables={"format_instructions": parser.get_format_instructions()})
                
                # invoking this chain will generate a metric object
                chain = prompt_template | llm | parser

                try:
                    metric_object = chain.invoke(input_dict)
                except OutputParserException:
                    metric_object = chain.invoke(input_dict)

                if metric_name == 'answer_relevancy':
                  metric_object.user_question = input_dict['question']
                elif metric_name == 'correctness':
                    metric_object.ai_response = input_dict['response']
                    metric_object.true_answer = input_dict['truth']
                scores[metric_name] = metric_object.score
                
                if self.batch:
                    scores_list.append(scores)
                    
        if self.batch:
            return scores_list
        else:
            return scores

    def get_scores(self) -> dict:
        return self._evaluate

    def trace_scores(self):
        '''
        send scores to langfuse
        '''
        metrics = self._get_metrics()
        scores = self.get_scores()
        for i in range(0, len(self._get_metrics())):
            metric = metrics[i]
            score = scores[metric]
            langfuse_context.score_current_trace(
                name=metric,
                value=score
            )
        return