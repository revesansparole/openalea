from nose.tools import assert_raises

from openalea.core.dataflow import DataFlow
from openalea.core.dataflow_state import DataflowState
from openalea.core.dataflow_evaluation import LazyEvaluation
from openalea.core.dataflow_evaluation_environment import EvaluationEnvironment
from openalea.core.node import FuncNodeSingle


def task0(a):
    return a * 5


def task1(a):
    return int(a)


def get_dataflow():
    df = DataFlow()
    ip = df.in_port
    op = df.out_port

    df.add_actor(FuncNodeSingle(({'name': 'in'},),
                                ({'name': 'out'},),
                                task0), 0)

    df.add_actor(FuncNodeSingle(({'name': 'in'},),
                                ({'name': 'out'},),
                                task1), 1)

    df.connect(op(0, 'out'), ip(1, 'in'))

    return df


def test_df_eval_with_prov_simple():
    df = get_dataflow()
    ip = df.in_port
    op = df.out_port
    df.actor(1).set_lazy(False)

    algo = LazyEvaluation(df)

    env = EvaluationEnvironment()
    env.set_provenance(df)
    eid0 = env.current_execution()

    dfs = DataflowState(df)
    dfs.set_data(ip(0, 'in'), 0)

    algo.eval(env, dfs)

    eid1 = env.new_execution(eid0, '>')
    algo.clear()
    algo.eval(env, dfs)

    prov = env.provenance()
    assert len(prov.execution_graph()) == 2
    assert prov.last_evaluation(0) == eid0
    assert prov.last_evaluation(1) == eid1
    assert prov.last_change(ip(0, 'in')) == eid0
    assert prov.last_change(op(0, 'out')) == eid0
    assert prov.last_change(op(1, 'out')) == eid1

    eid2 = env.new_execution(eid1, '>')
    dfs.set_data(ip(0, 'in'), 1)
    algo.clear()
    algo.eval(env, dfs)

    assert prov.last_evaluation(0) == eid2
    assert prov.last_evaluation(1) == eid2
    assert prov.last_change(ip(0, 'in')) == eid2
    assert prov.last_change(op(0, 'out')) == eid2
    assert prov.last_change(op(1, 'out')) == eid2

    assert prov.last_evaluation(0, eid1) == eid0
    assert prov.last_evaluation(1, eid1) == eid1
    assert prov.last_change(ip(0, 'in'), eid1) == eid0
    assert prov.last_change(op(0, 'out'), eid1) == eid0
    assert prov.last_change(op(1, 'out'), eid1) == eid1


def test_df_eval_with_prov_simple2():
    # check that even if node is non lazy
    # input changed is still considered as
    # unchanged
    df = get_dataflow()
    ip = df.in_port
    op = df.out_port
    df.actor(0).set_lazy(False)

    algo = LazyEvaluation(df)

    env = EvaluationEnvironment()
    env.set_provenance(df)
    eid0 = env.current_execution()

    dfs = DataflowState(df)
    dfs.set_data(ip(0, 'in'), 0)

    algo.eval(env, dfs)

    eid1 = env.new_execution(eid0, '>')
    algo.clear()
    algo.eval(env, dfs)

    prov = env.provenance()
    assert len(prov.execution_graph()) == 2
    assert prov.last_evaluation(0) == eid1
    assert prov.last_evaluation(1) == eid1
    assert prov.last_change(ip(0, 'in')) == eid0
    assert prov.last_change(op(0, 'out')) == eid1
    assert prov.last_change(op(1, 'out')) == eid1
