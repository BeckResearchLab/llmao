from eval.tools import Generator, cos_similarity, f1_score
import pytest
import pandas as pd
import numpy as np

def test_Generator():
    assert isinstance(Generator(n=1), list)
    assert isinstance(Generator(n=1, return_list=False), pd.DataFrame)
    with pytest.raises(Exception):
        assert isinstance(Generator(n='str', int='str', return_list='str'))
    return

def test_cos_similarity():
    # 2 strings should have a cosine similarity of 1 if they are the same
    assert np.isclose(cos_similarity(["Hello", "Hello"]), 1)
    assert isinstance(cos_similarity(["Hello", "Hello"], float))
    with pytest.raises(Exception):
        cos_similarity(1, "str"),
        cos_similarity([1, 1])
    return

def test_f1_score():
    return