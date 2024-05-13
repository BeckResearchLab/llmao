from eval.evaluator import Evaluator
import numpy as np
import pandas as pd
import pytest

sample_df = pd.read_csv("/home/ubuntu/llmao/llmao/data/data.csv")
sample_data = (sample_df.iloc[:5]).drop(axis=1, columns=["Number"])
sample_data = sample_data.to_numpy().tolist()

# test case where evaluator object successfully initialized
def test_init_eval_pass():
    evaluator = Evaluator(data = sample_data, metrics = ["faithfulness", "answer_relevancy"])
    assert evaluator.metrics == ["faithfulness", "answer_relevancy"]
    assert evaluator.data == sample_data
    #assert isinstance(evaluator, dict)
    assert isinstance(evaluator.get_scores(), dict)
    assert isinstance(evaluator.get_average_score(), float)

# invalid evaluator initialization
def test_init_eval_edge_cases():
    invalid_data = [[1, "string", True], ["string2", False, False]]
    # invalid data
    with pytest.raises(Exception):
        evaluator = Evaluator(data = invalid_data, metrics = ["faithfulness", "answer_relevancy"])
        evaluator = Evaluator(data = sample_data, metrics = ["faithfulness", 2])
        evaluator = Evaluator()
        evaluator = Evaluator(data = sample_df, metrics = ["faithfulness", "answer_relevancy"])