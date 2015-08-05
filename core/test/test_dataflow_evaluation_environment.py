from nose.tools import assert_raises

from openalea.core.dataflow import DataFlow
from openalea.core.dataflow_evaluation_environment import EvaluationEnvironment


def test_evaluation_environment_init():
    env = EvaluationEnvironment()

    assert env.current_execution() is None
    assert not env.record_provenance()
    assert env.provenance() is None


def test_evaluation_environment_set_provenance():
    df = DataFlow()
    env = EvaluationEnvironment()

    env.set_provenance(df)
    assert env.record_provenance()
    prov = env.provenance()
    assert prov is not None
    assert env.current_execution() is None

def test_evaluation_environment_new_execution():
    df = DataFlow()
    env = EvaluationEnvironment()

    env.set_provenance(df)
    env.new_execution()
    eid = env.current_execution()
    prov = env.provenance()
    assert eid in prov.execution_graph()
