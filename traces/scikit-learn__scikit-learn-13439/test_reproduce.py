"""
Test to reproduce the issue where Pipeline should implement __len__
"""
from sklearn import svm
from sklearn.datasets import samples_generator
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_regression
from sklearn.pipeline import Pipeline

def test_pipeline_len():
    """
    Test that Pipeline implements __len__ method.
    This should fail on base commit (no __len__) and pass on head commit (with __len__).
    """
    # Generate some data to play with
    X, y = samples_generator.make_classification(
        n_informative=5, n_redundant=0, random_state=42)

    anova_filter = SelectKBest(f_regression, k=5)
    clf = svm.SVC(kernel='linear')
    pipe = Pipeline([('anova', anova_filter), ('svc', clf)])

    # This should work - get the length of the pipeline
    pipe_length = len(pipe)

    # The pipeline has 2 steps, so length should be 2
    assert pipe_length == 2, f"Expected pipeline length to be 2, got {pipe_length}"

    # Also test that pipe[:len(pipe)] works as mentioned in the issue
    sub_pipeline = pipe[:len(pipe)]
    assert len(sub_pipeline) == pipe_length, f"Expected sub-pipeline length to be {pipe_length}, got {len(sub_pipeline)}"

    print("Test passed - Pipeline.__len__ is working correctly")

if __name__ == "__main__":
    test_pipeline_len()