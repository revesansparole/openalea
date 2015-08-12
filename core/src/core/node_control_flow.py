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

    control_type = "abstract"  # id of this type of node

    def __init__(self, inputs=(), outputs=()):
        Node.__init__(self, inputs, outputs)

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

    control_type = "X"

    def __init__(self):
        inputs = ({'name': 'key', 'interface': None},
                  {'name': 'order', 'interface': IInt, 'default': 0})
        outputs = ({'name': 'out'},)

        ControlFlowNode.__init__(self, inputs, outputs)

    def perform_evaluation(self, algo, env, state, vid):
        pass


class WhileNode(ControlFlowNode):
    """ Implement a type of while on a dataflow.

    WhileNode has two input ports "test" and "task". "Task"
    is executed and its result is forwarded on the output
    of this node as long as "test" is true. Once "test" is
    False, "task" is no longer executed and the output
    of this node stays unchanged.
    """

    control_type = "while"

    def __init__(self):
        inputs = ({'name': 'test', 'interface': None},
                  {'name': 'task', 'interface': None})
        outputs = ({'name': 'out'},)

        ControlFlowNode.__init__(self, inputs, outputs)
        self.set_lazy(False)

    def perform_evaluation(self, algo, env, state, vid):
        df = algo.dataflow()
        exec_id = env.current_execution()

        pid_out = df.out_port(vid, "out")

        # find subdataflow upstream of 'test' port
        pid_test = df.in_port(vid, "test")
        sub_test = get_upstream_subdataflow(df, pid_test)
        ss_test = state.clone(sub_test)
        algo_test = algo.clone(sub_test)
        # find subdataflow upstream 'task' port
        pid_task = df.in_port(vid, "task")
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
    "task" is executed and the result is mirrored
    on the output of the node.

    Once the loop is finished, "task" is no longer
    evaluation and the output of the node stays
    unchanged on the last computed value.
    """

    control_type = "for"

    def __init__(self):
        inputs = ({'name': 'iter', 'interface': None},
                  {'name': 'task', 'interface': None})
        outputs = ({'name': 'out'},)

        ControlFlowNode.__init__(self, inputs, outputs)
        self.set_lazy(False)

    def perform_evaluation(self, algo, env, state, vid):
        df = algo.dataflow()
        exec_id = env.current_execution()

        pid_out = df.out_port(vid, "out")

        # find subdataflow upstream of 'test' port
        pid_iter = df.in_port(vid, "iter")
        sub_iter = get_upstream_subdataflow(df, pid_iter)
        ss_iter = state.clone(sub_iter)
        algo_iter = algo.clone(sub_iter)
        # find subdataflow upstream 'task' port
        pid_task = df.in_port(vid, "task")
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
