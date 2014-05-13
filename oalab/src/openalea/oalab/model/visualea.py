# -*- python -*-
#
#       OpenAlea.OALab: Multi-Paradigm GUI
#
#       Copyright 2014 INRIA - CIRAD - INRA
#
#       File author(s): Julien Coste <julien.coste@inria.fr>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################
from openalea.oalab.model.model import Model
from openalea.core.compositenode import CompositeNodeFactory


class VisualeaModel(Model):
    default_name = "Workflow"
    default_file_name = "workflow.wpy"
    pattern = "*.wpy"
    extension = "wpy"
    icon = ":/images/resources/openalealogo.png"

    def __init__(self, name="workflow.wpy", code="", inputs=[], outputs=[]):
        super(VisualeaModel, self).__init__()
        if (code is None) or (code is ""):
            self._workflow = CompositeNodeFactory(name).instantiate()
        elif isinstance(code, CompositeNodeFactory):
            self._workflow = code.instantiate()
        else:
            cnf = eval(code, globals(), locals())
            self._workflow = cnf.instantiate()

    def repr_code(self):
        """
        :return: a string representation of model to save it on disk
        """
        name = self.name

        if name[-3:] in '.py':
            name = name[-3:]
        elif name[-4:] in '.wpy':
            name = name[-4:]
        cn = self.applet._workflow
        cnf = CompositeNodeFactory(name)
        cn.to_factory(cnf)

        repr_wf = repr(cnf.get_writer())
        # hack to allow eval rather than exec...
        # TODO: change the writer

        repr_wf = (' = ').join(repr_wf.split(' = ')[1:])
        return repr_wf

    def run(self, interpreter=None):
        """
        execute model thanks to interpreter
        """
        return self._workflow.eval()

    def reset(self, interpreter=None):
        """
        go back to initial step
        """
        return self._workflow.reset()

    def step(self, interpreter=None):
        """
        execute only one step of the model
        """
        return self._workflow.eval_as_expression(step=True)

    def stop(self, interpreter=None):
        """
        stop execution
        """
        # TODO : to implement
        pass

    def animate(self, interpreter=None):
        """
        run model step by step
        """
        return self._workflow.eval()