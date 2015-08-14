# -*- python -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(): Jerome Chopard <revesansparole@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite: http://openalea.gforge.inria.fr
#
###############################################################################
""" This module provide algorithms to evaluate a dataflow
"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "


from node_control_flow import ControlFlowNode


class EvaluationError(Exception):
    pass

# class EvaluationException(Exception):
#
#     def __init__(self, vid, node, exception, exc_info):
#         Exception.__init__(self)
#         self.vid = vid
#         self.node = node
#         self.exception = exception
#         self.exc_info = exc_info


class AbstractEvaluation(object):
    """ Abstract evaluation algorithm
    """
    def __init__(self, dataflow):
        """ Constructor

        args:
            - dataflow (Dataflow): the dataflow to evaluate
        """
        self._dataflow = dataflow

    def dataflow(self):
        """ Testing purpose, retrieve associated dataflow
        """
        return self._dataflow

    def require_evaluation(self):
        """ Return True if the associated dataflow need to be evaluated.
        """
        raise NotImplementedError()

    def eval(self, env, state, vid=None):
        """ Evaluate associated dataflow.

        Produce a valid state from a ready_to_evaluate one.

        args:
            - env (EvaluationEnvironment): environment in which to perform
                                           the evaluation
            - state (DataflowState): must be a ready_not_evaluate state
            - vid (vid): id of vertex to start the evaluation
                         if None starts from the leaves of the dataflow
        """
        raise NotImplementedError()

    def clear(self):
        """ Clear algorithm, ready to reevaluate.
        """
        pass

    def clone(self, dataflow):  # TODO: reimplement in subclasses
        """ Create a new evaluation algorithm
        around the given dataflow.

        args:
            - dataflow (DataFlow)

        return:
            - (EvaluationAlgorithm)
        """
        return type(self)(dataflow)


class BruteEvaluation(AbstractEvaluation):
    """ For each evaluation reevaluate each node of the dataflow.
    """
    def __init__(self, dataflow):
        AbstractEvaluation.__init__(self, dataflow)

        self._evaluated = set()

    def require_evaluation(self):
        return len(self._evaluated) < self._dataflow.nb_vertices()

    def clear(self):
        AbstractEvaluation.clear(self)
        self._evaluated.clear()

    def eval(self, env, state, vid=None):
        df = self._dataflow

        if not state.is_ready_for_evaluation():
            raise EvaluationError("state not ready for evaluation")

        if env.current_execution() is None:
            raise EvaluationError("Current execution id is None")

        if vid is None:  # start evaluation from leaves in the dataflow
            leaves = [vid for vid in df.vertices() if df.nb_out_edges(vid) == 0]
            # TODO: Hack remove CompositeNodeInput and CompositeNodeInput
            from openalea.core.compositenode import (CompositeNodeInput,
                                                     CompositeNodeOutput)
            leaves = [vid for vid in leaves
                      if not isinstance(df.actor(vid), (CompositeNodeInput,
                                                        CompositeNodeOutput))]
            # TODO: sort leaves
            for vid in leaves:
                if vid not in self._evaluated:
                    self.eval_from_node(env, state, vid)
        else:
            if vid not in self._evaluated:
                self.eval_from_node(env, state, vid)

        # provenance
        if env.record_provenance():
            prov = env.provenance()
            prov.store(env.current_execution(), state)

        # change the state of data on lonely input ports
        for vid in df.vertices():
            if df.nb_in_edges(vid) == 0:
                for pid in df.in_ports(vid):
                    state.set_changed(pid, False)

    def eval_from_node(self, env, state, vid):
        """ Evaluate dataflow from a given node.

        function provided for convenience to simplify
        derivation from this algo
        """
        # add node to evaluated list to prevent
        # multiple evaluation of the same node
        self._evaluated.add(vid)

        actor = self._dataflow.actor(vid)
        if isinstance(actor, ControlFlowNode):
            return actor.perform_evaluation(self, env, state, vid)

        if actor.get_caption() == "extra":
            return env.handle_extra(self._dataflow, env, state, vid)

        # ensure that all nodes upstream of this node have been evaluated
        for nid in self._dataflow.in_neighbors(vid):
            if nid not in self._evaluated:
                self.eval_from_node(env, state, nid)

        # evaluate the node
        self.eval_node(env, state, vid)

    def eval_node(self, env, state, vid):
        """ Evaluate a single node

        Store result in state.
        Doesn't test if state is valid or if the node
        actually needs to be evaluated
        """
        df = self._dataflow

        # find input values
        inputs = [state.get_data(pid) for pid in df.in_ports(vid)]
        # # tag input values as unchanged if necessary
        # for pid in df.in_ports(vid):
        #     if df.nb_connections(pid) == 0:
        #         state.set_changed(pid, False)

        # perform computation
        state.task_started(vid)
        vals = df.actor(vid)(inputs)
        state.task_ended(vid)

        # affect return values to output ports
        pids = tuple(df.out_ports(vid))

        # TODO: hack to insert this in visualea, to remove
        from openalea.core.node import FuncNodeRaw, FuncNodeSingle
        node = df.actor(vid)
        if isinstance(node, (FuncNodeRaw, FuncNodeSingle)):
            # perfect do nothing
            pass
        else:
            if len(pids) == 1:
                try:
                    if len(vals) == 1:
                        pass
                except TypeError:
                    vals = [vals]
        # TODO: end of hack

        if len(pids) == 0:
            if vals is not None:
                msg = "function return value but node has no out port"
                raise EvaluationError(msg)
        else:
            try:
                if len(pids) == len(vals):
                    for pid, val in zip(pids, vals):
                        state.set_data(pid, val)
                else:
                    msg = "mismatch nb out port vs. function result"
                    raise EvaluationError(msg)
            except TypeError:
                msg = "Function needs to return a list of values"
                raise EvaluationError(msg)


class LazyEvaluation(BruteEvaluation):
    """ For each evaluation reevaluate a node of the dataflow
    only if its inputs have changed or if it is tagged
    as not lazy.
    """
    def __init__(self, dataflow):
        BruteEvaluation.__init__(self, dataflow)

    def eval_node(self, env, state, vid):
        """ Evaluate a single node

        call BruteEvaluation:
            - if node is not lazy
            - if node is lazy but inputs have changed
        """
        if state.last_evaluation(vid) is None:  # Node needs a first evaluation anyway
            state.set_last_evaluation(vid, env.current_execution())
            return BruteEvaluation.eval_node(self, env, state, vid)
        elif state.last_evaluation(vid) == env.current_execution():
            # node has already been evaluated at this execution
            # do nothing
            pass  # TODO: redundant with self._evaluated????
        else :
            df = self._dataflow
            node = df.actor(vid)

            if node.is_lazy():
                if any(state.input_has_changed(pid) for pid in df.in_ports(vid)):
                    state.set_last_evaluation(vid, env.current_execution())
                    return BruteEvaluation.eval_node(self, env, state, vid)
                else:  # node will not be evaluated, mark outputs as unchanged
                    # set task execution time to None
                    state.set_task_start_time(vid, None)
                    state.set_task_end_time(vid, None)

                    # mark all outputs as unchanged
                    for pid in df.out_ports(vid):
                        state.set_changed(pid, False)

                    return False
            else:
                state.set_last_evaluation(vid, env.current_execution())
                return BruteEvaluation.eval_node(self, env, state, vid)
