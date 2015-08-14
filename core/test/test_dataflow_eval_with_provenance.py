from nose.tools import assert_raises
from time import sleep

from openalea.core.dataflow import DataFlow
from openalea.core.dataflow_state import DataflowState
from openalea.core.dataflow_evaluation import (BruteEvaluation,
                                               LazyEvaluation)
from openalea.core.dataflow_evaluation_environment import EvaluationEnvironment
from openalea.core.node import Node, FuncNode


def int_func(a):
    sleep(0.001)
    return int(a)


def add_func(a, b):
    sleep(0.001)
    return a + b


def print_func(*args):
    sleep(0.001)
    print "print_func", args


def fixed_function():
    sleep(0.001)
    return 5


def double_fixed_function():
    sleep(0.001)
    return 5, 5


def get_dataflow():
    df = DataFlow()
    vid1 = df.add_vertex()
    pid10 = df.add_in_port(vid1, "in")
    pid11 = df.add_out_port(vid1, "out")
    vid2 = df.add_vertex()
    pid21 = df.add_out_port(vid2, "out")

    vid3 = df.add_vertex()
    pid31 = df.add_in_port(vid3, "in1")
    pid32 = df.add_in_port(vid3, "in2")
    pid33 = df.add_out_port(vid3, "res")

    vid4 = df.add_vertex()
    pid41 = df.add_in_port(vid4, "in")
    pid42 = df.add_out_port(vid4, "out")

    df.connect(pid11, pid31)
    df.connect(pid21, pid32)
    df.connect(pid33, pid41)

    df.set_actor(vid1, FuncNode({}, {}, int_func))
    df.set_actor(vid2, FuncNode({}, {}, fixed_function))
    df.set_actor(vid3, FuncNode({}, {}, add_func))
    df.set_actor(vid4, FuncNode({}, {}, print_func))

    return df, (pid10, pid42)


def test_df_eval_with_prov_init():
    df, (pid_in, pid_out) = get_dataflow()
    algo = BruteEvaluation(df)

    env = EvaluationEnvironment(0)
    dfs = DataflowState(df)
    dfs.set_data(pid_in, 1)

    assert not dfs.is_valid()
    algo.eval(env, dfs, df.vertex(pid_out))
    assert dfs.is_valid()


def test_df_eval_with_prov_single_run():
    df, (pid_in, pid_out) = get_dataflow()
    algo = BruteEvaluation(df)

    env = EvaluationEnvironment()
    env.set_provenance(df)
    env.new_execution()
    dfs = DataflowState(df)
    dfs.set_data(pid_in, 1)

    prov = env.provenance()
    assert env.current_execution() not in prov

    algo.eval(env, dfs, df.vertex(pid_out))

    assert env.current_execution() in prov
    state = prov.get_state(env.current_execution())
    assert dict(dfs.items()) == dict(state.items())

    # test task recording
    state = prov.get_state(env.current_execution())
    for vid in df.vertices():
        assert state.task_end_time(vid) > state.task_start_time(vid)


def test_df_eval_with_prov_multiple_runs():
    df, (pid_in, pid_out) = get_dataflow()
    algo = BruteEvaluation(df)

    env = EvaluationEnvironment()
    env.set_provenance(df)
    prov = env.provenance()

    dfs = DataflowState(df)

    eids = []
    for i in range(3):
        dfs.reinit()
        dfs.set_data(pid_in, i)

        env.new_execution()
        eids.append(env.current_execution())
        assert env.current_execution() not in prov

        algo.clear()
        algo.eval(env, dfs)

        assert env.current_execution() in prov

    ref = prov.get_state(eids[0])
    for eid in eids[1:]:
        state = prov.get_state(eid)
        assert dict(ref.items()) != dict(state.items())

    # test task recording
    for eid in eids:
        state = prov.get_state(eid)
        for vid in df.vertices():
            assert state.task_end_time(vid) > state.task_start_time(vid)

    for vid in df.vertices():
        t_sts = tuple(prov.get_state(eid).task_start_time(vid) for eid in eids)
        t_ends = tuple(prov.get_state(eid).task_end_time(vid) for eid in eids)
        assert t_sts == tuple(sorted(t_sts))
        assert t_ends == tuple(sorted(t_ends))


def test_df_eval_lazy_with_prov():
    df = DataFlow()
    vid0 = df.add_vertex()
    pid0 = df.add_in_port(vid0, "in")
    pid1 = df.add_out_port(vid0, "out")
    df.set_actor(vid0, FuncNode({}, {}, int_func))
    vid1 = df.add_vertex()
    pid2 = df.add_in_port(vid1, "in")
    pid3 = df.add_out_port(vid1, "out")
    df.set_actor(vid1, FuncNode({}, {}, int_func))
    df.connect(pid1, pid2)
    df.actor(vid1).set_lazy(False)

    algo = LazyEvaluation(df)
    dfs = DataflowState(df)
    dfs.set_data(pid0, 1)

    env = EvaluationEnvironment()
    env.set_provenance(df)
    prov = env.provenance()

    eids = [env.current_execution()]
    algo.clear()
    algo.eval(env, dfs)

    for i in range(3):
        env.new_execution(env.current_execution())
        eids.append(env.current_execution())

        assert env.current_execution() not in prov

        algo.clear()
        algo.eval(env, dfs)

        assert env.current_execution() in prov

    last_eid = eids[-1]
    assert prov.last_evaluation(vid0) == eids[0]
    assert prov.last_evaluation(vid1) == last_eid
