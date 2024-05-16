from pydantic import BaseModel, Field, field_validator, computed_field
from eval.tools import f1_score, cos_similarity
from typing import Union

class Faithfulness(BaseModel):
    """
    Faithfulness is calculated by dividing B / A where 
      -A = Total number of claims in the AI response
      -B = Number of claims in the AI response which can be inferred from the context")
    """
    A: float = Field(description="Total number of claims in the AI response")
    B: float = Field(description="Number of claims in the AI response which can be inferred from the context")

    # will not be added to the schema
    @computed_field
    def score(self) -> float:
        return self.B / self.A
            

class Correctness(BaseModel):
    TP: int = Field(description="Facts or statements that are present in both the ground truth and the ai answer")
    FP: int = Field(description="Facts or statements that are present in the ai answer but not in the ground truth")
    FN: int = Field(description="Facts or statements that are present in the ground truth but not in the ai answer")
    score: None

    def _get_f1(self) -> float:
        return f1_score(self.TP, self.FP, self.FN)

    # will not be added to the schema
    @property
    def score(self) -> float:
        return self._score
    
    def calculate(self, ai_answer, ground_truth) -> float:
        semantic_similarity = cos_similarity([ai_answer, ground_truth])
        self._score = (semantic_similarity + self._get_f1()) / 2 
        return
    
class Precision(BaseModel):
    precision: float=Field(description="""0 - a imprecise answer, where none of the information in the response is relevant or necessary to answer the user's question
                                    1 - a precise answer, wihere all information in the response is relevant and needed to answer the user's question""")

    @property
    def score(self) -> float:
        return self.precision

class Answer_Relevancy(BaseModel):
    questions: list[str] = Field(description="A list of k (default 3) questions which the LLM derived from the AI's reponse")
    user_question: Union[str, None]

    # set human question dynamically
    @property
    def user_question(self) -> str:
        return self.user_question

    @user_question.setter
    def user_question(self, user_question: str) -> str:
        self.user_question = user_question
        self.score()

    @computed_field
    def score(self) -> float:
        scores = []
        for synthetic_question in self.questions:
            scores.append(cos_similarity([self.user_question, synthetic_question]))
        return sum(scores) / len(scores)
    

class Context_Relevancy(BaseModel):
    S: int = Field(description="The number of sentences in the retrieved context which are relevant to the user's question")
    T: int = Field(description="The total number of sentences in the retrieved context.")

    @property
    def score(self) -> float:
        try:
            return self.S / self.T
        except ZeroDivisionError:
            return self.S / 1

PARSER_DICT = {
    "faithfulness": Faithfulness,
    "context_relevancy": Context_Relevancy,
    "answer_relevancy": Answer_Relevancy,
    "precision": Precision,
    "correctness": Correctness,
}