# -*- python -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(s): Jerome Chopard <revesansparole@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################
""" Collection of nodes that change the way a dataflow is evaluated.
"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "


from dataflow import PortError
from interface import IInt
from node import Node
from subdataflow import get_upstream_subdataflow


class ControlFlowNode(Node):
    """ A ControlFlowNode is used internally to evaluate a dataflow
    in a non conventional way:
        - map
        - while

    Their call method is never called, instead a perform_evaluation
    method is used.
    """

    def __init__(self, inputs=(), outputs=()):
        Node.__init__(self, inputs, outputs)

    def __call__(self, inputs=()):
        pass

    def perform_evaluation(self, algo, env, state, vid):
        """ Perform evaluation of this node and
        update outputs accordingly.

        Node is allowed to modify other nodes inputs
        and outputs.
        """
        raise NotImplementedError


class XNode(ControlFlowNode):
    """ Does nothing but allow to add arguments
    in a loop of any sort.
    """
    def __init__(self):
        inputs = ({'name': 'order', 'interface': IInt, 'default': 0},)
        outputs = ({'name': 'out'},)

        ControlFlowNode.__init__(self, inputs, outputs)

    def perform_evaluation(self, algo, env, state, vid):
        pass


class IterNode(Node):  # TODO: hack not in the right place
    """ Iterate over a sequence
    """
    def __init__(self, inputs=(), outputs=()):
        Node.__init__(self, inputs, outputs)

        self._seq = None
        self._iter = None

    def reset(self):
        Node.reset(self)
        self._seq = None
        self._iter = None

    def __call__(self, *args):
        seq, = args
        if len(seq) == 1:  # TODO: GRUUIK hack because of bad definition of list
            seq = seq[0]

        if self._seq is None:
            self._seq = seq
            self._iter = iter(self._seq)
        # elif id(seq) != id(self._seq):  # TODO: correct this bug and reintroduce this case
        #         self._seq = seq
        #         self._iter = iter(self._seq)

        return self._iter.next(),


class WhileNode(ControlFlowNode):
    """ Implement a type of while on a dataflow.

    WhileNode has two input ports "test" and "task". "Task"
    is executed and its result is stored as long as "test"
    is true. Once "test" is False the accumulated "task"s
    is forwarded on the output port.

    result will be:
    [task() while test()]
    """
    def __init__(self):
        inputs = ({'name': 'test', 'interface': None},
                  {'name': 'task', 'interface': None})
        outputs = ({'name': 'out'},)

        ControlFlowNode.__init__(self, inputs, outputs)

    def perform_evaluation(self, algo, env, state, vid):
        df = algo.dataflow()
        exec_id = env.current_execution()

        try:  # TODO: hack to work around visualea re implementation of local id
            pid_out = df.out_port(vid, "out")
        except PortError:
            pid_out = df.out_port(vid, 0)

        # find subdataflow upstream of 'test' port
        try:
            pid_test = df.in_port(vid, "test")
        except PortError:
            pid_test = df.in_port(vid, 0)
        sub_test = get_upstream_subdataflow(df, pid_test)
        ss_test = state.clone(sub_test)
        algo_test = algo.clone(sub_test)
        # find subdataflow upstream 'task' port
        try:
            pid_task = df.in_port(vid, "task")
        except PortError:
            pid_task = df.in_port(vid, 1)
        sub_task = get_upstream_subdataflow(df, pid_task)
        ss_task = state.clone(sub_task)
        algo_task = algo.clone(sub_task)

        test = True
        res = []

        while test:  # TODO: add limit number iter "and len(res) < max_nb_iter
            env.new_execution()
            # eval 'test' dataflow
            ss_test.update(ss_task)
            algo_test.clear()
            algo_test.eval(env, ss_test)
            state.update(ss_test)
            test = state.get_data(pid_test)

            if test:
                # eval "task" dataflow
                ss_task.update(ss_test)
                algo_task.clear()
                algo_task.eval(env, ss_task)
                state.update(ss_task)
                res.append(state.get_data(pid_task))

        # fill ports with result
        state.set_data(pid_out, res)

        # restore state
        env.set_current_execution(exec_id)


class ForNode(ControlFlowNode):
    """ Implement a classical python for loop.

    ForNode has two input ports, "iter" and "task".
    Evaluation will exhaust the provided iterator
    until StopIteration is raised. Each time the
    actual iter value is passed to the "task",
    "task" is executed and the result is stored.

    Once the loop is finished, result will be
    [task() for i in iter()].
    """
    def __init__(self):
        inputs = ({'name': 'iter', 'interface': None},
                  {'name': 'task', 'interface': None})
        outputs = ({'name': 'out'},)

        ControlFlowNode.__init__(self, inputs, outputs)

    def perform_evaluation(self, algo, env, state, vid):
        df = algo.dataflow()
        exec_id = env.current_execution()

        try:  # TODO: hack to work around visualea re implementation of local id
            pid_out = df.out_port(vid, "out")
        except PortError:
            pid_out = df.out_port(vid, 0)

        # find subdataflow upstream of 'iter' port
        try:
            pid_iter = df.in_port(vid, "iter")
        except PortError:
            pid_iter = df.in_port(vid, 0)
        sub_iter = get_upstream_subdataflow(df, pid_iter)
        ss_iter = state.clone(sub_iter)
        algo_iter = algo.clone(sub_iter)
        # find subdataflow upstream 'task' port
        try:
            pid_task = df.in_port(vid, "task")
        except PortError:
            pid_task = df.in_port(vid, 1)
        sub_task = get_upstream_subdataflow(df, pid_task)
        ss_task = state.clone(sub_task)
        algo_task = algo.clone(sub_task)

        res = []

        try:
            while True:
                env.new_execution()
                # eval 'iter' dataflow
                ss_iter.update(ss_task)
                algo_iter.clear()
                algo_iter.eval(env, ss_iter)
                state.update(ss_iter)

                # eval "task" dataflow
                ss_task.update(ss_iter)
                algo_task.clear()
                algo_task.eval(env, ss_task)
                state.update(ss_task)
                res.append(state.get_data(pid_task))
        except StopIteration:
            pass

        # fill ports with result
        state.set_data(pid_out, res)

        # restore state
        env.set_current_execution(exec_id)


class MapNode(ControlFlowNode):
    """ Implement a classical python 'map' loop.

    MapNode has two input ports, "func" and "seq".
    Evaluation will call 'func' for each item in seq.

    Result will be a list of [func(i) for i in seq].
    """
    def __init__(self):
        inputs = ({'name': 'func', 'interface': None},
                  {'name': 'seq', 'interface': None})
        outputs = ({'name': 'out'},)

        ControlFlowNode.__init__(self, inputs, outputs)

    def perform_evaluation(self, algo, env, state, vid):
        df = algo.dataflow()
        exec_id = env.current_execution()

        try:  # TODO: hack to work around visualea re implementation of local id
            pid_out = df.out_port(vid, "out")
        except PortError:
            pid_out = df.out_port(vid, 0)

        # find subdataflow upstream of 'func' port
        try:
            pid_func = df.in_port(vid, "func")
        except PortError:
            pid_func = df.in_port(vid, 0)
        sub_func = get_upstream_subdataflow(df, pid_func)
        ss_func = state.clone(sub_func)
        algo_func = algo.clone(sub_func)
        # xnodes = [(state.get_data(df.in_port(lvid, "order")),
        #            df.out_port(lvid, "out")) for lvid in sub_func.vertices()
        #           if isinstance(sub_func.actor(lvid), XNode)]
        # TODO: hack to replace code above in visualea
        xnodes = []
        for lvid in sub_func.vertices():
            if isinstance(sub_func.actor(lvid), XNode):
                try:
                    pout = df.out_port(lvid, "out")
                except PortError:
                    pout = df.out_port(lvid, 0)
                try:
                    pid_order = df.in_port(lvid, "order")
                except PortError:
                    pid_order = df.in_port(lvid, 0)
                xnodes.append((state.get_data(pid_order), pout))

        xnodes.sort()
        arg_pids = [pid for order, pid in xnodes]

        # find subdataflow upstream 'seq' port
        try:
            pid_seq = df.in_port(vid, "seq")
        except PortError:
            pid_seq = df.in_port(vid, 1)
        sub_seq = get_upstream_subdataflow(df, pid_seq)
        ss_seq = state.clone(sub_seq)
        algo_seq = algo.clone(sub_seq)

        # eval "seq" dataflow
        env.new_execution()
        algo_seq.eval(env, ss_seq)
        state.update(ss_seq)
        seq = state.get_data(pid_seq)

        res = []
        for item in seq:
            env.new_execution()

            # set item in value in ss_func if needed
            ss_func.update(ss_seq)
            if len(arg_pids) == 0:
                pass
            elif len(arg_pids) == 1:
                ss_func.set_data(arg_pids[0], item)
            else:
                for pid, val in zip(arg_pids, item):
                    ss_func.set_data(pid, val)

            # eval 'func' dataflow
            algo_func.clear()
            algo_func.eval(env, ss_func)
            state.update(ss_func)

            res.append(state.get_data(pid_func))

        # fill ports with result
        state.set_data(pid_out, res)

        # restore state
        env.set_current_execution(exec_id)
