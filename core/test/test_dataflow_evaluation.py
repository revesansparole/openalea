from nose.tools import assert_raises
import operator

from openalea.core.dataflow import DataFlow
from openalea.core.dataflow_state import DataflowState
from openalea.core.dataflow_evaluation import (EvaluationError,
                                               AbstractEvaluation,
                                               BruteEvaluation,
                                               LazyEvaluation)
from openalea.core.dataflow_evaluation_environment import EvaluationEnvironment
from openalea.core.node import Node, FuncNodeRaw, FuncNodeSingle


def print_func(*args):
    print "print_func", args
    return args,


def display_func(*args):
    print "print_func", args


def fixed_function():
    return 5


def double_fixed_function():
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

    df.set_actor(vid1, FuncNodeSingle({}, {}, int))
    df.set_actor(vid2, FuncNodeSingle({}, {}, fixed_function))
    df.set_actor(vid3, FuncNodeSingle({}, {}, operator.add))
    df.set_actor(vid4, FuncNodeRaw({}, {}, print_func))

    return df, (pid10, pid42)


def test_dataflow_evaluation_init():
    df = get_dataflow()[0]
    algo = AbstractEvaluation(df)
    assert_raises(NotImplementedError, lambda: algo.eval(0, None))
    assert_raises(NotImplementedError, lambda: algo.require_evaluation())

    algo = BruteEvaluation(df)
    algo.clear()

    assert algo.require_evaluation()


def test_dataflow_evaluation_eval_init():
    df = get_dataflow()[0]
    algo = BruteEvaluation(df)

    env = None
    dfs = DataflowState(df)
    assert_raises(EvaluationError, lambda: algo.eval(env, dfs))

    env = EvaluationEnvironment()
    assert_raises(EvaluationError, lambda: algo.eval(env, dfs))


def test_dataflow_evaluation_eval():
    df, (pid_in, pid_out) = get_dataflow()
    algo = BruteEvaluation(df)

    env = EvaluationEnvironment(0)
    dfs = DataflowState(df)
    dfs.set_data(pid_in, 1)

    assert not dfs.is_valid()
    algo.eval(env, dfs, df.vertex(pid_out))
    assert dfs.is_valid()
    assert not algo.require_evaluation()


def test_dataflow_evaluation_eval_no_vid():
    df, (pid_in, pid_out) = get_dataflow()
    algo = BruteEvaluation(df)

    env = EvaluationEnvironment(0)
    dfs = DataflowState(df)
    dfs.set_data(pid_in, 1)

    assert not dfs.is_valid()
    algo.eval(env, dfs)
    assert dfs.is_valid()


def test_dataflow_evaluation_eval_no_vid2():
    df = DataFlow()
    vid0 = df.add_vertex()
    pid0 = df.add_in_port(vid0, "in")
    df.add_out_port(vid0, "out")
    vid1 = df.add_vertex()
    pid1 = df.add_in_port(vid1, "in")
    df.add_out_port(vid1, "out")

    df.set_actor(vid0, FuncNodeSingle({}, {}, int))
    df.set_actor(vid1, FuncNodeSingle({}, {}, int))

    dfs = DataflowState(df)
    env = EvaluationEnvironment(0)
    algo = BruteEvaluation(df)

    dfs.set_data(pid0, 0)
    dfs.set_data(pid1, 1)

    assert not dfs.is_valid()
    algo.eval(env, dfs)
    assert dfs.is_valid()


def test_dataflow_evaluation_single_input_single_output():
    df = DataFlow()
    vid = df.add_vertex()
    pid0 = df.add_in_port(vid, "in1")
    pid1 = df.add_in_port(vid, "in2")
    pid2 = df.add_out_port(vid, "out")

    df.set_actor(vid, FuncNodeSingle({}, {}, operator.add))

    dfs = DataflowState(df)
    env = EvaluationEnvironment(0)
    algo = BruteEvaluation(df)

    dfs.set_data(pid0, 1)
    dfs.set_data(pid1, 2)
    algo.eval(env, dfs, vid)

    assert dfs.get_data(pid0) == 1
    assert dfs.get_data(pid1) == 2
    assert dfs.get_data(pid2) == 3


def test_dataflow_evaluation_single_input_no_output():
    df = DataFlow()
    vid = df.add_vertex()
    pid0 = df.add_in_port(vid, "in")

    df.set_actor(vid, FuncNodeRaw({}, {}, display_func))

    dfs = DataflowState(df)
    env = EvaluationEnvironment(0)
    algo = BruteEvaluation(df)

    dfs.set_data(pid0, 1)
    algo.eval(env, dfs, vid)

    assert dfs.get_data(pid0) == 1

    df.set_actor(vid, FuncNodeSingle({}, {}, int))
    dfs.reinit()
    algo.clear()

    assert_raises(EvaluationError, lambda: algo.eval(env, dfs, vid))


def test_dataflow_evaluation_no_input_two_outputs():
    df = DataFlow()
    vid = df.add_vertex()
    pid0 = df.add_out_port(vid, "out1")

    df.set_actor(vid, FuncNodeRaw({}, {}, double_fixed_function))

    dfs = DataflowState(df)
    env = EvaluationEnvironment(0)
    algo = BruteEvaluation(df)

    assert_raises(EvaluationError, lambda: algo.eval(env, dfs, vid))

    algo.clear()
    dfs.reinit()
    pid1 = df.add_out_port(vid, "out2")
    algo.eval(env, dfs, vid)
    assert dfs.get_data(pid0) == 5
    assert dfs.get_data(pid1) == 5

    algo.clear()
    dfs.reinit()
    df.add_out_port(vid, "out3")
    assert_raises(EvaluationError, lambda: algo.eval(env, dfs, vid))


def test_dataflow_evaluation_multiple_runs():
    df, (pid_in, pid_out) = get_dataflow()
    algo = BruteEvaluation(df)

    dfs = DataflowState(df)

    for i in range(3):
        dfs.reinit()
        dfs.set_data(pid_in, i)

        env = EvaluationEnvironment(i)
        algo.clear()
        algo.eval(env, dfs)
        assert dfs.is_valid()


def f_none():
    return None


def f_none_tup():
    return None,


def f1():
    return 1


def f1_tup():
    return 1,


def ftup():
    return 1, 2


def test_dataflow_evaluation_dispatch_return_values():
    ###########################
    #
    # no output
    #
    ###########################
    df = DataFlow()
    vid = df.add_vertex()

    algo = BruteEvaluation(df)
    dfs = DataflowState(df)

    env = EvaluationEnvironment(0)
    # return single value
    df.set_actor(vid, FuncNodeRaw({}, {}, f_none))
    algo.clear()
    dfs.reinit()
    algo.eval(env, dfs)

    for func in [f_none_tup, f1, f1_tup, ftup]:
        df.set_actor(vid, FuncNodeRaw({}, {}, func))
        algo.clear()
        dfs.reinit()

        assert_raises(EvaluationError, lambda: algo.eval(env, dfs) )

    ###########################
    #
    # single output
    #
    ###########################
    df = DataFlow()
    vid = df.add_vertex()
    pid = df.add_out_port(vid, "out")

    algo = BruteEvaluation(df)
    dfs = DataflowState(df)

    # return single value
    for func in [f_none, f1]:
        df.set_actor(vid, FuncNodeRaw({}, {}, func))
        algo.clear()
        dfs.reinit()
        assert_raises(EvaluationError, lambda: algo.eval(env, dfs) )

    df.set_actor(vid, FuncNodeSingle({}, {}, f_none))
    algo.clear()
    dfs.reinit()
    algo.eval(env, dfs)

    assert dfs.get_data(pid) is None

    df.set_actor(vid, FuncNodeSingle({}, {}, f1))
    algo.clear()
    dfs.reinit()
    algo.eval(env, dfs)

    assert dfs.get_data(pid) == 1

    # return tuple
    df.set_actor(vid, FuncNodeRaw({}, {}, f_none_tup))
    algo.clear()
    dfs.reinit()
    algo.eval(env, dfs)

    assert dfs.get_data(pid) is None

    df.set_actor(vid, FuncNodeRaw({}, {}, f1_tup))
    algo.clear()
    dfs.reinit()
    algo.eval(env, dfs)

    assert dfs.get_data(pid) == 1

    df.set_actor(vid, FuncNodeSingle({}, {}, ftup))
    algo.clear()
    dfs.reinit()
    algo.eval(env, dfs)

    assert dfs.get_data(pid) == (1, 2)

    df.set_actor(vid, FuncNodeRaw({}, {}, ftup))
    algo.clear()
    dfs.reinit()
    assert_raises(EvaluationError, lambda: algo.eval(env, dfs) )

    ###########################
    #
    # multiple outputs
    #
    ###########################
    df = DataFlow()
    vid = df.add_vertex()
    pid1 = df.add_out_port(vid, "out1")
    pid2 = df.add_out_port(vid, "out2")

    algo = BruteEvaluation(df)
    dfs = DataflowState(df)

    # return single value
    for func in [f_none, f_none_tup, f1, f1_tup]:
        df.set_actor(vid, FuncNodeRaw({}, {}, func))
        algo.clear()
        dfs.reinit()
        assert_raises(EvaluationError, lambda: algo.eval(env, dfs) )

    # return two values
    df.set_actor(vid, FuncNodeRaw({}, {}, ftup))
    algo.clear()
    dfs.reinit()
    algo.eval(env, dfs)

    assert dfs.get_data(pid1) == 1
    assert dfs.get_data(pid2) == 2

    df.set_actor(vid, FuncNodeSingle({}, {}, ftup))
    algo.clear()
    dfs.reinit()
    assert_raises(EvaluationError, lambda: algo.eval(env, dfs) )


def test_dataflow_evaluation_lazy():
    df, (pid_in, pid_out) = get_dataflow()
    algo = LazyEvaluation(df)

    dfs = DataflowState(df)
    env = EvaluationEnvironment(0)

    for i in range(3):
        dfs.set_data(pid_in, i)

        algo.clear()
        algo.eval(env, dfs)
        assert dfs.is_valid()


def test_df_eval_lazy_single_node_lazy():
    df = DataFlow()
    vid = df.add_vertex()
    pid0 = df.add_in_port(vid, "in")
    pid1 = df.add_out_port(vid, "out")
    df.set_actor(vid, FuncNodeSingle({}, {}, int))

    algo = LazyEvaluation(df)
    dfs = DataflowState(df)
    dfs.set_data(pid0, 1)

    assert df.actor(vid).is_lazy()
    assert dfs.has_changed(pid0)

    # first run
    env = EvaluationEnvironment(0)
    algo.clear()
    algo.eval(env, dfs)

    assert dfs.is_valid()

    t0 = dfs.task_start_time(vid)
    assert t0 is not None
    t1 = dfs.task_end_time(vid)
    assert t1 is not None
    assert dfs.get_data(pid1) == dfs.get_data(pid0)
    assert not dfs.has_changed(pid0)
    assert dfs.has_changed(pid1)

    # second run
    env = EvaluationEnvironment(1)
    algo.clear()
    algo.eval(env, dfs)

    assert dfs.is_valid()

    assert dfs.task_start_time(vid) is None
    assert dfs.task_end_time(vid) is None
    assert not dfs.has_changed(pid0)
    assert not dfs.has_changed(pid1)


def test_df_eval_lazy_single_node_non_lazy():
    df = DataFlow()
    vid = df.add_vertex()
    pid0 = df.add_in_port(vid, "in")
    pid1 = df.add_out_port(vid, "out")
    df.set_actor(vid, FuncNodeSingle({}, {}, int))
    df.actor(vid).set_lazy(False)

    algo = LazyEvaluation(df)
    dfs = DataflowState(df)
    dfs.set_data(pid0, 1)

    assert not df.actor(vid).is_lazy()
    assert dfs.has_changed(pid0)

    # first run
    env = EvaluationEnvironment(0)
    algo.clear()
    algo.eval(env, dfs)

    assert dfs.is_valid()

    t0 = dfs.task_start_time(vid)
    assert t0 is not None
    t1 = dfs.task_end_time(vid)
    assert t1 is not None
    assert dfs.get_data(pid1) == dfs.get_data(pid0)
    assert not dfs.has_changed(pid0)
    assert dfs.has_changed(pid1)

    # second run
    env = EvaluationEnvironment(1)
    algo.clear()
    algo.eval(env, dfs)

    assert dfs.is_valid()

    assert dfs.task_start_time(vid) is not None
    assert dfs.task_start_time(vid) > t0
    assert dfs.task_end_time(vid) is not None
    assert dfs.task_end_time(vid) > t1
    assert not dfs.has_changed(pid0)
    assert dfs.has_changed(pid1)


def test_df_eval_lazy_single_node_lazy_no_inports():
    df = DataFlow()
    vid = df.add_vertex()
    pid = df.add_out_port(vid, "out")
    df.set_actor(vid, FuncNodeSingle({}, {}, fixed_function))

    algo = LazyEvaluation(df)
    dfs = DataflowState(df)

    assert df.actor(vid).is_lazy()

    # first run
    env = EvaluationEnvironment(0)
    algo.clear()
    algo.eval(env, dfs)

    assert dfs.is_valid()

    t0 = dfs.task_start_time(vid)
    assert t0 is not None
    t1 = dfs.task_end_time(vid)
    assert t1 is not None
    dat = dfs.get_data(pid)
    assert dfs.has_changed(pid)

    # second run
    env = EvaluationEnvironment(1)
    algo.clear()
    algo.eval(env, dfs)

    assert dfs.is_valid()

    assert dfs.task_start_time(vid) is None
    assert dfs.task_end_time(vid) is None
    assert dfs.get_data(pid) == dat
    assert not dfs.has_changed(pid)


def test_df_eval_lazy_single_node_non_lazy_no_inports():
    df = DataFlow()
    vid = df.add_vertex()
    pid = df.add_out_port(vid, "out")
    df.set_actor(vid, FuncNodeSingle({}, {}, fixed_function))
    df.actor(vid).set_lazy(False)

    algo = LazyEvaluation(df)
    dfs = DataflowState(df)

    assert not df.actor(vid).is_lazy()

    # first run
    env = EvaluationEnvironment(0)
    algo.clear()
    algo.eval(env, dfs)

    assert dfs.is_valid()

    t0 = dfs.task_start_time(vid)
    assert t0 is not None
    t1 = dfs.task_end_time(vid)
    assert t1 is not None
    dat = dfs.get_data(pid)
    assert dfs.has_changed(pid)

    # second run
    env = EvaluationEnvironment(1)
    algo.clear()
    algo.eval(env, dfs)

    assert dfs.is_valid()

    assert dfs.task_start_time(vid) is not None
    assert dfs.task_start_time(vid) > t0
    assert dfs.task_end_time(vid) is not None
    assert dfs.task_end_time(vid) > t1
    assert dfs.has_changed(pid)


def test_df_eval_lazy_two_nodes_lazy():
    df = DataFlow()
    vid0 = df.add_vertex()
    pid0 = df.add_in_port(vid0, "in")
    pid1 = df.add_out_port(vid0, "out")
    df.set_actor(vid0, FuncNodeSingle({}, {}, int))
    vid1 = df.add_vertex()
    pid2 = df.add_in_port(vid1, "in")
    pid3 = df.add_out_port(vid1, "out")
    df.set_actor(vid1, FuncNodeSingle({}, {}, int))
    df.connect(pid1, pid2)

    algo = LazyEvaluation(df)
    dfs = DataflowState(df)
    dfs.set_data(pid0, 1)

    assert df.actor(vid0).is_lazy()
    assert df.actor(vid1).is_lazy()
    assert dfs.has_changed(pid0)

    # first run
    env = EvaluationEnvironment(0)
    algo.clear()
    algo.eval(env, dfs)

    assert dfs.is_valid()

    t0 = dfs.task_start_time(vid0)
    assert t0 is not None
    t1 = dfs.task_end_time(vid0)
    assert t1 is not None
    t2 = dfs.task_start_time(vid1)
    assert t2 is not None
    t3 = dfs.task_end_time(vid1)
    assert t3 is not None
    assert dfs.get_data(pid1) == dfs.get_data(pid0)
    assert dfs.get_data(pid3) == dfs.get_data(pid0)
    assert not dfs.has_changed(pid0)
    assert dfs.has_changed(pid1)
    assert dfs.input_has_changed(pid2)
    assert dfs.has_changed(pid3)

    # second run
    env = EvaluationEnvironment(1)
    algo.clear()
    algo.eval(env, dfs)

    assert dfs.is_valid()

    assert dfs.task_start_time(vid0) is None
    assert dfs.task_end_time(vid0) is None
    assert dfs.task_start_time(vid1) is None
    assert dfs.task_end_time(vid1) is None
    assert not dfs.has_changed(pid0)
    assert not dfs.has_changed(pid1)
    assert not dfs.input_has_changed(pid2)
    assert not dfs.has_changed(pid3)


def test_df_eval_lazy_two_nodes_up_nonlazy():
    df = DataFlow()
    vid0 = df.add_vertex()
    pid0 = df.add_in_port(vid0, "in")
    pid1 = df.add_out_port(vid0, "out")
    df.set_actor(vid0, FuncNodeSingle({}, {}, int))
    vid1 = df.add_vertex()
    pid2 = df.add_in_port(vid1, "in")
    pid3 = df.add_out_port(vid1, "out")
    df.set_actor(vid1, FuncNodeSingle({}, {}, int))
    df.connect(pid1, pid2)
    df.actor(vid0).set_lazy(False)

    algo = LazyEvaluation(df)
    dfs = DataflowState(df)
    dfs.set_data(pid0, 1)

    assert not df.actor(vid0).is_lazy()
    assert df.actor(vid1).is_lazy()
    assert dfs.has_changed(pid0)

    # first run
    env = EvaluationEnvironment(0)
    algo.clear()
    algo.eval(env, dfs)

    assert dfs.is_valid()

    t0 = dfs.task_start_time(vid0)
    assert t0 is not None
    t1 = dfs.task_end_time(vid0)
    assert t1 is not None
    t2 = dfs.task_start_time(vid1)
    assert t2 is not None
    t3 = dfs.task_end_time(vid1)
    assert t3 is not None
    assert dfs.get_data(pid1) == dfs.get_data(pid0)
    assert dfs.get_data(pid3) == dfs.get_data(pid0)
    assert not dfs.has_changed(pid0)
    assert dfs.has_changed(pid1)
    assert dfs.input_has_changed(pid2)
    assert dfs.has_changed(pid3)

    # second run
    env = EvaluationEnvironment(1)
    algo.clear()
    algo.eval(env, dfs)

    assert dfs.is_valid()

    assert dfs.task_start_time(vid0) is not None
    assert dfs.task_start_time(vid0) > t0
    assert dfs.task_end_time(vid0) is not None
    assert dfs.task_end_time(vid0) > t1
    assert dfs.task_start_time(vid1) is not None
    assert dfs.task_start_time(vid1) > t2
    assert dfs.task_end_time(vid1) is not None
    assert dfs.task_end_time(vid1) > t3
    assert not dfs.has_changed(pid0)
    assert dfs.has_changed(pid1)
    assert dfs.input_has_changed(pid2)
    assert dfs.has_changed(pid3)


def test_df_eval_lazy_two_nodes_down_nonlazy():
    df = DataFlow()
    vid0 = df.add_vertex()
    pid0 = df.add_in_port(vid0, "in")
    pid1 = df.add_out_port(vid0, "out")
    df.set_actor(vid0, FuncNodeSingle({}, {}, int))
    vid1 = df.add_vertex()
    pid2 = df.add_in_port(vid1, "in")
    pid3 = df.add_out_port(vid1, "out")
    df.set_actor(vid1, FuncNodeSingle({}, {}, int))
    df.connect(pid1, pid2)
    df.actor(vid1).set_lazy(False)

    algo = LazyEvaluation(df)
    dfs = DataflowState(df)
    dfs.set_data(pid0, 1)

    assert df.actor(vid0).is_lazy()
    assert not df.actor(vid1).is_lazy()
    assert dfs.has_changed(pid0)

    # first run
    env = EvaluationEnvironment(0)
    algo.clear()
    algo.eval(env, dfs)

    assert dfs.is_valid()

    t0 = dfs.task_start_time(vid0)
    assert t0 is not None
    t1 = dfs.task_end_time(vid0)
    assert t1 is not None
    t2 = dfs.task_start_time(vid1)
    assert t2 is not None
    t3 = dfs.task_end_time(vid1)
    assert t3 is not None
    assert dfs.get_data(pid1) == dfs.get_data(pid0)
    assert dfs.get_data(pid3) == dfs.get_data(pid0)
    assert not dfs.has_changed(pid0)
    assert dfs.has_changed(pid1)
    assert dfs.input_has_changed(pid2)
    assert dfs.has_changed(pid3)

    # second run
    env = EvaluationEnvironment(1)
    algo.clear()
    algo.eval(env, dfs)

    assert dfs.is_valid()

    assert dfs.task_start_time(vid0) is None
    assert dfs.task_end_time(vid0) is None
    assert dfs.task_start_time(vid1) is not None
    assert dfs.task_start_time(vid1) > t2
    assert dfs.task_end_time(vid1) is not None
    assert dfs.task_end_time(vid1) > t3
    assert not dfs.has_changed(pid0)
    assert not dfs.has_changed(pid1)
    assert not dfs.input_has_changed(pid2)
    assert dfs.has_changed(pid3)
