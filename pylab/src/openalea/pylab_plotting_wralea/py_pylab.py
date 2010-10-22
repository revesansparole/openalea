###############################################################################
# -*- python -*-
#
#       Copyright or (C) or Copr. 2010 INRIA - CIRAD - INRA
#
#       File author(s): Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################

__doc__="""Pylab plotting nodes for VisuAlea"""
__revision__ = " $Revision$ "
__author__ = "$Author$"
__date__ = "$Date$"


from openalea.core import Node
from openalea.core import Factory, IFileStr, IInt, IBool, IFloat, \
    ISequence, IEnumStr, IStr, IDirStr, ITuple3, IDict, ITuple

from openalea.core.external import add_docstring

from openalea.pylab import tools



class Plotting(Node):
    """This class provides common connector to plotting nodes that are defined in this module.

    Classes that inherits from `Plotting` are ensured to inherits from `Node` and to have a common 
    API where :

        * the first input connector is reserved for connecting a pylab axes
        * the first output connector is reserved for connecting a pylab axes
        * the last input connector is reseverd to set the pylab.figure number

    It also provides several methods that check validity of input axes, update the figure and so on.


    """
    ERROR_NOXDATA = 'No data connected to the x connector. Connect a line2D, an array or a list of line2Ds or arrays'
    ERROR_FAILURE = 'Failed to generate the image. check your entries.'

    def __init__(self,  inputs={}):
        Node.__init__(self)
        self.axe = None
        self.fig = None

        self.add_input(name="axes")
        for input in inputs:
            self.add_input(**input)

        self.add_input(name="figure", interface=IInt(1,100,1), value=1)
        self.add_output(name='axes')

    def figure(self):
        """calls pylab.figure() taking care of existing figure


        If a node is executed for the first time, the figure object is stored. This is
        useful in cases where thre user kills the figure manually. In such case, 
        we clean the axes that are left in memory before creating a new figure.


         """
        from pylab import figure
        assert type(self.get_input('figure')) == int
        if self.fig == None:
            fig = figure(self.get_input('figure'))
            self.fig = fig
        else:
            fig = figure(self.get_input('figure'))
            if fig == self.fig:
                #print 'figure exist already, nothing to do'
                pass
            else:
                print 'figure not found. Maybe it was closed !!! consider reloading this node.'

                self.fig = fig
                del self.axe
                self.axe = None
                #raise ValueError('figure not found. Maybe it was closed !!! consider reloading this node.')

        return self.fig

    def axes(self):
        """If no axes is connected to the first input connector, this method checks if an 
        axes was already created. If so, we clean it otherwise, we create a new one.

        If an axes is provided, the current axe is the input one. Therefore the input axe is used 
        to superimpose new data. 

        """
        #sometimes, we want to add data to existing axe provided as an input argument. In such case, we do not want to clean
        # the axe and create a new one.
        if self.get_input('axes') != None:
            print 'Input axes found. Using it (%s)'  % self.get_input('axes')
            axes = self.get_input('axes')
            import matplotlib
            assert axes.__module__ in [matplotlib.axes.__name__,matplotlib.projections.polar.__name__], 'input must be a valid axes from matplotlib.axes %s given for %s' % (type(axes), axes)
            self.axe = axes
            self.axe.hold(True)
            return
        #if an axe already exist, no need to create a new one: we simply clean it
        if self.axe:
            from pylab import sca, cla
            print 'No input axe, but axes already set. Clear it. %s' % self.axe, self.axe.__str__
            self.axe.clear()
            self.axe.get_figure().canvas.draw()
            sca(self.axe)
        #else, we need to create a new axe. Note, the use of label. Indeed, if same position is used, and same default label then
        # no new axes is created. See add_axes help. Our label is the number of axes.
        else:
            print 'No input axe and not axes set. Creating a new one.'
            label='axe' + str(len(self.fig.get_axes()))
            self.axe = self.fig.add_axes([.1,.1,.8,.8], label=label)


    def update_figure(self):
        """This method updates the figure using pylab.figure.canvas.draw and pylab.show methods"""
        #self.legend()
        self.fig.canvas.draw()
        self.fig.show()




class PlotxyInterface():
    """A base class common to some plotting functions

    The plotting functions that uses this base class are those that plot 2D curves (xy). For instance:

        * plot
        * loglog
        * semilogx, semilogy
        * csd, psd, specgram
        * stem
        * step
        * fill

    This is used to manage the different possible x and y inputs. See :class:`PyLabPlot` for more explanation.

    For more tunable colors and linestyles, use the :class:`Line2D` convertor before passing
    the data to a node.

    This class provides a method :meth:`call` that manage the inputs data and arguments smoothly.

    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    ERROR_NOXDATA = 'No data connected to the x connector. Connect a line2D, an array or a list of line2Ds or arrays'
    ERROR_FAILURE = 'Failed to generate the image. check your entries.'

    def __init__(self):
        pass


    def call(self, plottype, kwds):
        """Function used to call the plot specified by`plottype`

        :param plottype: must be one of plot, loglog, semilogx, semilogy, csd, psd, specgram, step, stem, fill

        if several x are provided, different colors will be used for the markers cycling over the available :class:`Colors`
        """
        from pylab import hold, Line2D
        if plottype=='plot':
            from pylab import plot as plot
        elif plottype=='loglog':
            from pylab import loglog as plot
        elif plottype=='semilogx':
            from pylab import semilogx as plot
        elif plottype=='semilogy':
            from pylab import semilogy as plot
        elif plottype=='csd':
            from pylab import csd as plot
        elif plottype=='psd':
            from pylab import psd as plot
        elif plottype=='specgram':
            from pylab import specgram as plot
        elif plottype=='stem':
            from pylab import stem as plot
        elif plottype=='step':
            from pylab import step as plot
        elif plottype=='fill':
            from pylab import fill as plot
        elif plottype=='hist':
            from pylab import hist as plot
        elif plottype=='polar':
            from pylab import polar as plot

        try:
            xinputs = self.get_input("x")
            yinputs = self.get_input("y")
        except:
            xinputs = self.get_input("theta")
            yinputs = self.get_input("r")

        # convert x and y inputs into lists
        if xinputs == None:
            raise ValueError(self.ERROR_NOXDATA)
        if type(xinputs)!=list:
            xinputs = [xinputs]
        if type(yinputs)!=list:
            yinputs = [yinputs]

        output = None
        # case of an x input without y input. line2D are all manage in this if statement
        if yinputs[0]==None:
            #plot(line2D) and plot([line2D, line2D])
            if type(xinputs[0])==Line2D:
                for x in xinputs:
                    print kwds
                    line2dkwds = tools.get_kwds_from_line2d(line2d=x, input_kwds=kwds, type=plottype)
                    #print line2dkwds
                    #returns the processed data ?
                    if plottype in ['specgram', 'psd']:
                        output = plot(x.get_ydata(orig=False), **line2dkwds)
                    else:
                        try:
                            output = plot(x.get_xdata(orig=False), x.get_ydata(orig=False), **line2dkwds)
                        except:
                            #print kwds
                            #print line2dkwds
                            pass
                    hold(True)
            #plot([x1,None,x2,None, ...) and plot(x1)
            else:
                c = enumerate(tools.colors)
                for x in xinputs:
                    try:
                        color = c.next()
                        kwds['color']=color[1]
                    except:
                        print 'no more colors'
                    try:
                        output = plot(x, **kwds)
                    except:
                        raise ValueError("plot failed")
                    hold(True)

        else:
            if len(xinputs)==1 and len(yinputs)!=1:
                # plot(x,y) and plot(x, [y1,y2])
                c = enumerate(tools.colors)
                for y in yinputs:
                    try:
                        color = c.next()
                        kwds['color']=color[1]
                    except:
                        print 'no more colors'
                    try:
                        output = plot(xinputs[0], y, **kwds)
                    except:
                        raise ValueError("plot failed")
                    hold(True)
            else:
                if len(xinputs)!=len(yinputs):
                    print 'warning more x inputs than y inputs. correct the connectors'
                for x,y in zip(xinputs, yinputs):
                    try:
                        output = plot(x, y, **kwds)
                    except:
                        #print kwds
                        raise ValueError("plot failed")
        return output


class PyLabPlot(Plotting, PlotxyInterface):
    """Plot lines. See pylab.plot help for details.

    The x connector must be connected. It must be in one of the following format:

        * a 1-D array.
            * If nothing is connected to `y`, then `x` is used as `y` (similarly to pylab.plot behaviour)
            * A 1-D array of same length may be connected to `y`.
            * Several 1-D arrays of same length as `x` may be connected to `y`. Therefore,
              these arrays have the same `x` data
        * a Line2D object (see :ref:`Line2D`). `y` must  be empty in such case.
        * a list of Line2D objects. `y` must be empty in such case

    In order to customize the input data at will, it is necesserary to convert the xy data into a
    :class:`PyLabLine2D` object and to pass it to the `x` connector. In such case, the y connector
    becomes useless.

    :param x: one  or several arrays, or one or several PyLabLine2D objects.
    :param y: one  or several arrays, or one or several PyLabLine2D objects.
    :param marker:
    :param markersize:
    :param linestyle:
    :param color:
    :param scalex:
    :param scaley:
    :param kwargs: a :class:`PyLabLine2D` object to fully tune the lines.
    :param figure: figure id

    :return: the axes in which the data are plotted.


    :Example:

    .. dataflow:: openalea.pylab.test plot
        :width: 50%

        **The `openalea.pylab.test.plot` dataflow.** The input data is a normal
        distribution (openalea.numpy.ran) passed to the `PyLabLogLog` node, which
        calls pylab.loglog.

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'plot'),{},pm=pm)

    .. seealso:: in VisuAlea, see "plot demos" in openalea.pylab.demo


    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    def __init__(self):
        PlotxyInterface.__init__(self)
        inputs = [
                    {'name':'x',          'interface':None,                           'value':None},
                    {'name':'y',          'interface':None,                           'value':None},
                    {'name':'marker',     'interface':IEnumStr(tools.markers.keys()),  'value':'circle'},
                    {'name':'markersize', 'interface':IFloat,                         'value':10},
                    {'name':'linestyle',  'interface':IEnumStr(tools.linestyles.keys()),    'value':'solid'},
                    {'name':'color',      'interface':IEnumStr(tools.colors.keys()),   'value':'blue'},
                    {'name':'scalex',     'interface':IBool, 'value':True},
                    {'name':'scaley',     'interface':IBool, 'value':True},
                    {'name':'kwargs',     'interface':IDict, 'value':{'label':None}},
        ]
        Plotting.__init__(self, inputs)
        self.add_output(name="output")

    def __call__(self, inputs):
        #todo label must be cast into string
        kwds = {}
        for key,value in self.get_input('kwargs').iteritems():
            kwds[key] = value
        kwds['markersize']=self.get_input("markersize")
        kwds['marker']=tools.markers[self.get_input("marker")]
        kwds['linestyle']=tools.linestyles[self.get_input("linestyle")]
        kwds['color']=tools.get_valid_color(self.get_input("color"))
        kwds['scaley']=self.get_input("scaley")
        kwds['scalex']=self.get_input("scalex")

        self.figure()
        self.axes()
        output = self.call('plot', kwds)
        self.update_figure()

        return self.axe, output



class PyLabLogLog(Plotting, PlotxyInterface):
    """Make a plot with log scaling. See pylab.loglog for details.


    :param x: one  or several arrays, or one or several PyLabLine2D objects.
    :param y: one  or several arrays, or one or several PyLabLine2D objects.
    :param marker:
    :param markersize:
    :param linestyle:
    :param color:
    :param kwargs: a :class:`PyLabLine2D` object to fully tune the lines.
    :param figure: figure id

    :return: the axes in which the data are plotted.

    :Example:

    .. dataflow:: openalea.pylab.test loglog
        :width: 50%

        **The `openalea.pylab.test.loglog` dataflow.** The input data is a normal
        distribution (openalea.numpy.randn) passed to the `PyLabLogLog` node, which
        calls pylab.loglog.

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'loglog'),{},pm=pm)

    .. seealso:: See :class:`PyLabPlot` for details about the x and y connector.

    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    def __init__(self):
        self.__doc__ = PyLabPlot.__doc__
        PlotxyInterface.__init__(self)
        inputs = [
                    {'name':'x',            'interface':None,                           'value':None},
                    {'name':'y',            'interface':None,                           'value':None},
                    {'name':'marker',       'interface':IEnumStr(tools.markers.keys()),       'value':'circle'},
                    {'name':'markersize',   'interface':IFloat,                         'value':10},
                    {'name':'linestyle',    'interface':IEnumStr(tools.linestyles.keys()),    'value':'solid'},
                    {'name':'color',        'interface':IEnumStr(tools.colors.keys()),        'value':'blue'},
        ]
        Plotting.__init__(self, inputs)
        self.add_input(name='kwargs', interface=IDict, value={'label':None})
        self.add_output(name="output")

    def __call__(self, inputs):
        kwds = {}
        for key,value in self.get_input('kwargs').iteritems():
            kwds[key] = value
        kwds['markersize']=self.get_input("markersize")
        kwds['marker']=tools.markers[self.get_input("marker")]
        kwds['linestyle']=tools.linestyles[self.get_input("linestyle")]
        kwds['color']=tools.colors[self.get_input("color")]

        self.figure()
        self.axes()
        self.call('loglog', kwds)
        self.update_figure()

        return self.axe, None

class PyLabSemiLogy(Plotting, PlotxyInterface):
    """Make a plot with log scaling on y-axis. See pylab.semilogy for details.


    :param x: one  or several arrays, or one or several PyLabLine2D objects.
    :param y: one  or several arrays, or one or several PyLabLine2D objects.
    :param marker:
    :param markersize:
    :param linestyle:
    :param color:
    :param kwargs: a :class:`PyLabLine2D` object to fully tune the lines.
    :param figure: figure id

    :return: the axes in which the data are plotted.

    :Example:

    .. dataflow:: openalea.pylab.test semilogy
        :width: 50%

        **The `openalea.pylab.test.semilogy` dataflow.**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'semilogy'),{},pm=pm)

    .. seealso:: See :class:`PyLabPlot` for details about the x and y connector.

    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    def __init__(self):
        PlotxyInterface.__init__(self)
        inputs = [
                    {'name':'x',            'interface':None,                           'value':None},
                    {'name':'y',            'interface':None,                           'value':None},
                    {'name':'marker',       'interface':IEnumStr(tools.markers.keys()),       'value':'circle'},
                    {'name':'markersize',   'interface':IFloat,                         'value':10},
                    {'name':'linestyle',    'interface':IEnumStr(tools.linestyles.keys()),    'value':'solid'},
                    {'name':'color',        'interface':IEnumStr(tools.colors.keys()),        'value':'blue'},
        ]
        Plotting.__init__(self, inputs)
        self.add_input(name='kwargs', interface=IDict, value={'label':None})
        self.add_output(name="output")

    def __call__(self, inputs):
        kwds = {}
        for key,value in self.get_input('kwargs').iteritems():
            kwds[key] = value
        kwds['markersize'] = self.get_input("markersize")
        kwds['marker'] = tools.markers[self.get_input("marker")]
        kwds['linestyle'] = tools.linestyles[self.get_input("linestyle")]
        kwds['color'] = tools.colors[self.get_input("color")]

        self.figure()
        self.axes()
        self.call('semilogy', kwds)
        self.update_figure()

        return self.axe, None


class PyLabSemiLogx(Plotting, PlotxyInterface):
    """Make a plot with log scaling on x-axis. See pylab.semilogx for details.

    :param x: one  or several arrays, or one or several PyLabLine2D objects.
    :param y: one  or several arrays, or one or several PyLabLine2D objects.
    :param marker:
    :param markersize:
    :param linestyle:
    :param color:
    :param kwargs: a :class:`PyLabLine2D` object to fully tune the lines.
    :param figure: figure id

    :return: the axes in which the data are plotted.

    :Example:

    .. dataflow:: openalea.pylab.test semilogx
        :width: 50%

        **The `openalea.pylab.test.semilogx` dataflow.**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'semilogx'),{},pm=pm)

    .. seealso:: See :class:`PyLabPlot` for details about the x and y connector.

    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    def __init__(self):
        self.__doc__ = PyLabPlot.__doc__
        PlotxyInterface.__init__(self)
        inputs = [
                    {'name':'x',            'interface':None,                           'value':None},
                    {'name':'y',            'interface':None,                           'value':None},
                    {'name':'marker',       'interface':IEnumStr(tools.markers.keys()),       'value':'circle'},
                    {'name':'markersize',   'interface':IFloat,                         'value':10},
                    {'name':'linestyle',    'interface':IEnumStr(tools.linestyles.keys()),    'value':'solid'},
                    {'name':'color',        'interface':IEnumStr(tools.colors.keys()),        'value':'blue'},
        ]
        Plotting.__init__(self, inputs)
        self.add_input(name='kwargs', interface=IDict, value={'label':None})
        self.add_output(name="output")

    def __call__(self, inputs):
        kwds = {}
        for key,value in self.get_input('kwargs').iteritems():
            kwds[key] = value
        kwds['markersize']=self.get_input("markersize")
        kwds['marker']=tools.markers[self.get_input("marker")]
        kwds['linestyle']=tools.linestyles[self.get_input("linestyle")]
        kwds['color']=tools.colors[self.get_input("color")]

        self.figure()
        self.axes()
        self.call('semilogx', kwds)
        self.update_figure()

        return self.axe, None


class PyLabHist(Plotting):
    """Compute and draw the histogram of *x*. See pylab.hist for details.


    :param x: the input data (1D array)
    :param bins: binning number (default is 10)
    :param facecolor: (default is blue)
    :param normed: draw normalised histogram (default False)
    :param cumulative: draw cumulated histogram (default False)
    :param histtype: The type of histogram to draw  [ 'bar' | 'barstacked' | 'step' | 'stepfilled' ]
    :param align: Controls how the histogram is plotted ['left' | 'mid' | 'right' ]
    :param orientation: horizontal or vertical (default vertical)
    :param log: logarithmic scale (default is False)
    :param label: a text label for the legend
    :param kwargs: a :class:`~openalea.pylab_plotting_wralea.py_pylab.PyLabLine2D` object
    :param figure: figure id

    :returns:
        * The first connector is the current axe.
        * The second connector is the output of pylab.hist that is a tuple (lags, c, linecol, b)

    .. dataflow:: openalea.pylab.test hist
        :width: 50%

        **The `openalea.pylab.test.hist` dataflow.**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'hist'),{},pm=pm)

    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """

    def __init__(self):

        inputs = [
            {'name':'x'},
            {'name':'bins',         'interface':IInt, 'value':10},
            {'name':'facecolor',    'interface':IEnumStr(tools.colors.keys()), 'value':'blue'},
            {'name':'normed',       'interface':IBool, 'value':False},
            {'name':'cumulative',   'interface':IBool, 'value':False},
            {'name':'histtype',     'interface':IEnumStr(tools.histtype.keys()), 'value':'bar'},
            {'name':'align',        'interface':IEnumStr(tools.align.keys()), 'value':'mid'},
            {'name':'orientation',  'interface':IEnumStr(tools.orientations.keys()), 'value':'vertical'},
            {'name':'log',          'interface':IBool,  'value':False},
            {'name':'label',        'interface':IStr,  'value':''}
        ]
        Plotting.__init__(self, inputs)

        self.add_input(name="kwargs", interface = IDict, value={'alpha':1., 'animated':False})

        self.add_output(name="axes")
        self.add_output(name="position")
        self.add_output(name="counts")

    def __call__(self, inputs):
        from pylab import cla, hold, hist, Line2D
        self.figure()
        self.axes()
        #cla()
        kwds={}
        kwds['bins']=self.get_input("bins")
        kwds['normed']=self.get_input("normed")
        kwds['facecolor']=tools.get_valid_color(self.get_input("facecolor"))
        kwds['label']=self.get_input("label")
        kwds['log']=self.get_input("log")
        kwds['orientation']=tools.orientations[self.get_input("orientation")]
        kwds['figure']=self.get_input("figure")
        kwds['histtype']=tools.histtype[self.get_input("histtype")]
        kwds['align']=tools.align[self.get_input("align")]
        kwds['cumulative']=self.get_input("cumulative")
        #!! facecolor is alrady in the Hist node, so override it if available in kwargs dict
        for key,value in self.get_input('kwargs').iteritems():
            kwds[key] = value

        xinputs = self.get_input('x')
        if type(xinputs)!=list:
            xinputs = [xinputs]
        try:
            for x in xinputs:
                if type(x)==Line2D:
                    line2dkwds = tools.get_kwds_from_line2d(x, kwds, type='hist')
                    res = self.axe.hist(x.get_ydata(orig=False),**line2dkwds)
                else:
                    res = self.axe.hist(x,**kwds)
            hold(True)
        except ValueError, e:
            res = (None, None)
            print e
            raise ValueError('tttt')

        hold(False)
        self.update_figure()
        return (self.axe,res, res[1],res[0])


class PyLabAcorr(Plotting):
    r"""Plot the autocorrelation of *x*. See pylab.acorr for details.

    :param axes: an optional input axes where to plot the results
    :param x: the input data
    :param maxlags:  a positive integer detailing the number of lags
        to show.  The default value of *None* will return all
        :math:`2 \times \mathrm{len}(x) - 1` lags. (default 10).

    :param normed: (default False)
    :param usevlines: If *True*, :meth:`~matplotlib.axes.Axes.vlines`
        rather than :meth:`~matplotlib.axes.Axes.plot` is used to draw
        vertical lines from the origin to the acorr.  Otherwise, the
        plot style is determined by the kwargs, which are
        :class:`~matplotlib.lines.Line2D` properties. (default True)

    :param detrend: (default None)
    :param kwargs:  Connect a PyLabLine2D to customize the output.
    :param figure: figure id

    :returns:

        - The first connector is the current axe.
        - The second connector is the output of pylab.acorr that is a tuple (*lags*, *c*, *linecol*, *b*)

    .. seealso:: in VisuAlea, see pylab/test/acorr composite node.
        :class:`~~openalea.pylab_plotting_wralea.py_pylab.PyLabXcorr`

    :Example:

    .. dataflow:: openalea.pylab.test acorr
        :width: 50%

        **openalea.pylab.test.acorr dataflow**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'acorr'),{},pm=pm)

    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """

    def __init__(self):
        inputs = [
                    {'name':'x', 'interface':None, 'value':None},
                    {'name':"maxlags",   'interface':IInt,  'value':10},
                    {'name':"normed",    'interface':IBool, 'value':False},
                    {'name':"usevlines", 'interface':IBool, 'value':True},
                    {'name':'detrend', 'interface':IEnumStr(tools.detrends.keys()), 'value':'none'},
                    {'name':"kwargs(line2d)",    'interface':IDict, 'value':{}}
                ]
        Plotting.__init__(self, inputs)
        self.add_output(name='output', interface=ITuple, value=())
    def __call__(self, inputs):
        from pylab import clf, hold, acorr, Line2D, gca
        import pylab
        self.figure()
        self.axes()

        kwds = {}
        line2d = self.get_input('kwargs(line2d)')
        if type(line2d)==Line2D:
            kwds = line2d.properties()
            if self.get_input("usevlines") is False:
                for x in ['axes', 'children',  'path','xdata', 'ydata', 'data','transform',
                          'xydata','transformed_clip_path_and_affine',
                          ]:

                    del kwds[x]
            else:
                for x in ['axes', 'markerfacecoloralt','marker',
                          'children', 'markeredgecolor',
                          'dash_capstyle','solid_joinstyle','markeredgewidth',
                          'markerfacecolor','markevery','path',
                          'fillstyle','solid_capstyle',
                          'xdata','ydata','markersize',
                          'data','drawstyle','dash_joinstyle',
                          'xydata','transformed_clip_path_and_affine',
                          'transform']:
                    del kwds[x]


        else:
            for key,value in self.get_input('kwargs(line2d)').iteritems():
                kwds[key] = value

        #print kwds
        kwds['maxlags'] = self.get_input("maxlags")
        kwds['normed'] = self.get_input("normed")
        kwds['usevlines'] = self.get_input("usevlines")
        kwds['detrend'] = getattr(pylab, 'detrend_'+self.get_input('detrend'))

        res = None
        xinputs=self.get_input('x')
        if type(xinputs)!=list:
            xinputs = [xinputs]

        #line2dkwds = get_kwds_from_line2d(x, self.get_input('kwargs'), type='linecollection')
        #returns the processed data ?
        for x in xinputs:
            res =  acorr(x, **kwds)
            hold(True)
        self.update_figure()


        return self.get_input('axes'), res


class PyLabXcorr(Plotting):
    r"""Plot the crosscorrelation of *x* with *y*. See pylab.xcorr for details.

    x and y inputs must be of same length. If N arrays are connected to x, then
    the y connector expects N arrays as well and the xcross function will be called
    N times.

    :param axes: an optional input axes where to plot the results
    :param x: the *x* input data
    :param y: the *y* input data
    :param maxlags:  a positive integer detailing the number of lags
        to show.  The default value of *None* will return all
        :math:`2 \times \mathrm{len}(x) - 1` lags. (default 10).
    :param normed: (default False)
    :param usevlines: If *True*, :meth:`~matplotlib.axes.Axes.vlines`
        rather than :meth:`~matplotlib.axes.Axes.plot` is used to draw
        vertical lines from the origin to the acorr.  Otherwise, the
        plot style is determined by the kwargs, which are
        :class:`~matplotlib.lines.Line2D` properties. (default True)
    :param detrend: (default None)
    :param kwargs:  Connect a PyLabLine2D to customize the output.
    :param figure: figure id

    :returns:

        - The first connector is the current axe.
        - The second connector is the output of pylab.acorr that is a tuple (*lags*, *c*, *linecol*, *b*)

    .. seealso:: in VisuAlea, see pylab/test/acorr composite node.
        :class:`~~openalea.pylab_plotting_wralea.py_pylab.PyLabAcorr`

    :Example:

    .. dataflow:: openalea.pylab.test xcorr
        :width: 50%

        **The `openalea.pylab.test.xcorr` dataflow.**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'xcorr'),{},pm=pm)

    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """

    def __init__(self):
        inputs = [
                    {'name':'x', 'interface':None, 'value':None},
                    {'name':'y', 'interface':None, 'value':None},
                    {'name':"maxlags",   'interface':IInt,  'value':10},
                    {'name':"normed",    'interface':IBool, 'value':False},
                    {'name':"usevlines", 'interface':IBool, 'value':True},
                    {'name':'detrend', 'interface':IEnumStr(tools.detrends.keys()), 'value':'none'},
                    {'name':"kwargs(line2d)",    'interface':IDict, 'value':{}}
                ]
        Plotting.__init__(self, inputs)
        self.add_output(name='output', interface=ITuple, value=())
    def __call__(self, inputs):
        from pylab import clf, hold, xcorr, Line2D, gca
        import pylab
        self.figure()
        self.axes()

        kwds = {}
        line2d = self.get_input('kwargs(line2d)')
        if type(line2d)==Line2D:
            kwds = line2d.properties()
            if self.get_input("usevlines") is False:
                for x in ['axes', 'children',  'path','xdata', 'ydata', 'data','transform',
                          'xydata','transformed_clip_path_and_affine',
                          ]:

                    del kwds[x]
            else:
                for x in ['axes', 'markerfacecoloralt','marker',
                          'children', 'markeredgecolor',
                          'dash_capstyle','solid_joinstyle','markeredgewidth',
                          'markerfacecolor','markevery','path',
                          'fillstyle','solid_capstyle',
                          'xdata','ydata','markersize',
                          'data','drawstyle','dash_joinstyle',
                          'xydata','transformed_clip_path_and_affine',
                          'transform']:
                    del kwds[x]


        else:
            for key,value in self.get_input('kwargs(line2d)').iteritems():
                kwds[key] = value

        kwds['maxlags'] = self.get_input("maxlags")
        kwds['normed'] = self.get_input("normed")
        kwds['usevlines'] = self.get_input("usevlines")
        kwds['detrend'] = getattr(pylab, 'detrend_'+self.get_input('detrend'))

        res = None
        xinputs=self.get_input('x')
        yinputs=self.get_input('y')

        if type(xinputs)!=list:
            xinputs = [xinputs]
        if type(yinputs)!=list:
            yinputs = [yinputs]

        #line2dkwds = get_kwds_from_line2d(x, self.get_input('kwargs'), type='linecollection')
        #returns the processed data ?
        for x, y in zip(xinputs,yinputs):
            res =  xcorr(x, y, **kwds)
            hold(True)
        self.update_figure()


        return self.get_input('axes'), res

class PyLabScatter(Plotting):
    """See pylab.scatter for details

    create a scatter plot of the x-y input data


    :param x: a x-data array
    :param y: a y-data array
    :param label: None by default
    :param marker: circle marker by default
    :param linestyle: solid line by default
    :param color: blue by default
    :param xlabel: none by default
    :param ylabel: none by default
    :param title: none by default
    :param figure: figure number

    :returns:

        - The first connector is the current axe.
        - The second connector is the output of pylab.scatter

    .. todo:: deal with several multiple x-y data sets (e.g., line 2D?)

    .. todo:: add vmin/vmax, cmap

    :Example:

    .. dataflow:: openalea.pylab.test scatter
        :width: 50%

        **caption**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'scatter'),{},pm=pm)

    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    def __init__(self):
        inputs = [
            {'name':'x',        'value':None},
            {'name':'y',        'value':None},
            {'name':'sizes',    'value':20},
            {'name':"color",    'interface':IEnumStr(tools.colors.keys()),  'value':'blue'},
            {'name':"marker",   'interface':IEnumStr(tools.markers.keys()), 'value' : 'circle'},
            {'name':"cmap",   'interface':IEnumStr(tools.cmaps.keys()), 'value' : 'jet'},
            {'name':"norm",   'interface':IFloat, 'value' : None},
            {'name':"vmin",   'interface':IFloat, 'value' : None},
            {'name':"vmax",   'interface':IFloat, 'value' : None},
            {'name':"alpha", 'interface':IFloat(0,1,0.1), 'value':1.0},
            {'name':"faceted",   'interface':IBool, 'value' : True},
            {'name':"linewidths",    'interface':None,     'value' : None},
            {'name':"verts",    'interface':None,     'value' : None},
            {'name':"kwargs",    'interface':IDict,     'value' : {'edgecolors':'none', 'facecolors':'none'}},
        ]

        Plotting.__init__(self, inputs)
        self.add_output(name='output')

    def __call__(self, inputs):
        from pylab import scatter
        x = self.get_input("x")
        y = self.get_input("y")
        sizes = self.get_input("sizes")
        try:
            color = tools.get_valid_color(self.get_input("color"))
        except:
            color = self.get_input('color')
        marker = tools.markers[self.get_input('marker')]
        cmap = tools.cmaps[self.get_input('cmap')]
        norm = self.get_input('norm')
        vmin = self.get_input('vmin')
        vmax = self.get_input('vmax')
        if vmin == vmax:
            vmin = None
            vmax = None
        alpha = self.get_input('alpha')
        faceted = self.get_input('faceted')

        linewidths = self.get_input('linewidths')
        verts = self.get_input('verts')

        kwds = {}
        for key, value in self.get_input('kwargs').iteritems():
            kwds[key] = value

        self.figure()
        self.axes()

        res = scatter(x,y, s=sizes,c=color,
                marker=marker,norm=norm, vmin=vmin,vmax=vmax,
                alpha=alpha, cmap=cmap, faceted=faceted, linewidths=linewidths,
                verts=verts)
        self.update_figure()


        return self.axe, res




class PyLabBoxPlot(Plotting):
    """Make a box and whisker plot. See pylab.boxplot help for detailled help.

    :param x: data
    :param notch: (default 0)
    :param sym: '+'
    :param vert: 1
    :param whis: 1.5,
    :param positions: None
    :param widths: None
    :param figure: figure number

    .. seealso:: in VisuAlea, see pylab/test/boxplot composite node.

    :Example:

    .. dataflow:: openalea.pylab.test boxplot
        :width: 50%

        **The `openalea.pylab.test.boxplot` dataflow.**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'boxplot'),{},pm=pm)




    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>

    """
    def __init__(self):
        inputs = [
            {'name':"x"},
            {'name':"notch",    'interface':IEnumStr({'0':0,'1':1}), 'value':0},
            {'name':"marker",      'interface':IEnumStr(tools.markers.keys()), 'value':'plus'},
            {'name':"color",      'interface':IEnumStr(tools.colors.keys()), 'value':'blue'},
            {'name':"vert",     'interface':IEnumStr({'0':0,'1':1}), 'value':1},
            {'name':"whis",     'interface':IFloat,  'value':1.5},
            {'name':"positions",'interface':ISequence,  'value':None},
            {'name':"widths",   'interface':IFloat,     'value':None},
            {'name':"hold",     "interface":IBool,      'value':True},
            {'name':"bootstrap",     "interface":IInt,      'value':None},
            {'name':"patch_artist",     'interface':IBool,  'value':False},
        ]
        Plotting.__init__(self, inputs)
        #self.__doc__+=plot.__doc__
        self.add_output(name='output')

    def __call__(self, inputs):
        from pylab import boxplot, hold

        self.figure()
        self.axes()
        x = self.get_input("x")
        res = boxplot(x,
                sym=tools.markers[self.get_input("marker")]+tools.colors[self.get_input("color")],
                vert=self.get_input("vert"),
                notch=self.get_input("notch"),
                whis=self.get_input("whis"),
                positions=self.get_input('positions'),
                widths=self.get_input('widths'),
                hold =self.get_input('hold'),
                bootstrap =self.get_input('bootstrap'),
                patch_artist =self.get_input('patch_artist'),
                )
        self.update_figure()
        return self.get_input('axes'), res


class PyLabLine2D(Node):
    """Convert x and y inputs into a pylab.Line2D objects.

    :param xdata: a x array
    :param ydata: a y array of same length as x
    :param linestyle: a valid pylab linestyle
    :param color: a valid pylab color
    :param marker: a valid pylab marker
    :param markersize:
    :param markeredgewidth:
    :param markercolor:
    :param linewidth:
    :param fillstyle:
    :param label: a label that will be used when legend() is called
    :param alpha: transparency
    :param kwargs: all other valid Line2D properties (key/value)

    :return: a Line2D object that can be connected to some of the OpenAlea.PyLab nodes.

    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    def __init__(self):
        Node.__init__(self)

        self.add_input(name="xdata", value=[])
        self.add_input(name="ydata", value=[])
        self.add_input(name="linestyle", interface=IEnumStr(tools.linestyles.keys()), value='solid')
        self.add_input(name="color", interface=IEnumStr(tools.colors.keys()),value='blue')
        self.add_input(name="marker", interface=IEnumStr(tools.markers.keys()),value='circle')
        self.add_input(name="markersize", interface=IInt, value=10)
        self.add_input(name="markeredgewidth", interface=IFloat(0.,10,0.1) , value=None)
        self.add_input(name="markeredgecolor", interface=IEnumStr(tools.colors.keys()), value='None')
        self.add_input(name="linewidth", interface=IFloat, value=1.)
        self.add_input(name="fillstyle", interface=IEnumStr(tools.fillstyles), value='full')
        self.add_input(name="label", interface=IStr, value=None)
        self.add_input(name="alpha", interface=IFloat(0.,1., step=0.1), value=1.0)
        self.add_input(name="kwargs", interface=IDict, value={})

        self.add_output(name="line2d")

    def __call__(self, inputs):
        from pylab import Line2D

        kwds = {}
        for key, value in self.get_input('kwargs').iteritems():
            kwds[key] = value

        xdata=self.get_input('xdata')
        ydata=self.get_input('ydata')
        #why?
        if ydata == None or len(ydata)==0:
            ydata = xdata
            xdata = range(0, len(ydata))
        output = Line2D(
            xdata=xdata,
            ydata=ydata,
            linestyle=tools.linestyles[self.get_input('linestyle')],
            color=tools.colors[self.get_input('color')],
            marker=tools.markers[self.get_input('marker')],
            label=self.get_input('label'),
            markersize=self.get_input('markersize'),
            markeredgecolor=tools.colors[self.get_input('markeredgecolor')],
            markeredgewidth=self.get_input('markeredgewidth'),
            linewidth=self.get_input('linewidth'),
            fillstyle=self.get_input('fillstyle'),
            alpha=self.get_input('alpha'),**kwds
        )
        return (output, )


class PyLabPolar(Plotting, PlotxyInterface):
    """See pylab.polar for details.
    :Example:

    .. dataflow:: openalea.pylab.test polar
        :width: 50%

        **The `openalea.pylab.test.polar` dataflow.**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'polar'),{},pm=pm )

    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    def __init__(self):

        PlotxyInterface.__init__(self)
        inputs = [
                  {'name':"theta"},
                  {'name':"r"},
                  {'name':"kwargs(line2d)", 'interface':IDict, 'value':{}}
                  ]
        Plotting.__init__(self, inputs)
        self.add_output(name='output')

    def __call__(self, inputs):
        from pylab import polar, gca, sca, cla

        self.figure()
        #do not use that method that is not appropriate to a polar axe
        #self.axes()

        kwds = {}
        for key, value in self.get_input('kwargs(line2d)').iteritems():
            kwds[key] = value
        try:
            del kwds['facecolor']
        except:
            pass

        if self.get_input('axes') is not None:
            sca(self.get_input('axes'))
            self.axe = gca()
        else:
            if self.axe != None:
                sca(self.axe)
                cla()


        output = self.call('polar', kwds)

        self.axe = gca()

        self.update_figure()
        return self.axe, output



class PyLabPie(Plotting):
    """See pylab.pie for details.

    :Example:

    .. dataflow:: openalea.pylab.test pie
        :width: 50%

        **The `openalea.pylab.test.pie` dataflow.**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'pie'),{},pm=pm )



    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    def __init__(self):
        inputs = [
            { 'name':'x'},
            {'name':'colors',       'interface':IStr,   'value':None},
            {'name':'labels',       'interface':ISequence, 'value':None},
            {'name':'explode',      'interface':ISequence, 'value':None},
            {'name':'pctdistance',  'interface':IFloat, 'value':0.6},
            {'name':'labeldistance','interface':IFloat, 'value':1.1},
            {'name':'shadow',       'interface':IBool,  'value':False},
            {'name':'autopct',      'interface':IStr,   'value':None},
            {'name':'hold',      'interface':IBool,   'value':True}
        ]
        Plotting.__init__(self, inputs)
        self.add_output(name='output')

    def __call__(self, inputs):
        from pylab import pie
        self.figure()
        self.axes()

        kwds = {}
        kwds['explode'] = self.get_input('explode')
        kwds['colors'] = self.get_input('colors')
        kwds['labels'] = self.get_input('labels')
        kwds['pctdistance'] = self.get_input('pctdistance')
        kwds['labeldistance'] = self.get_input('labeldistance')
        kwds['shadow'] = self.get_input('shadow')
        kwds['autopct'] = self.get_input('autopct')
        #hold is not valid when calling axe.pie but is valid is calling pylab.pie
        #kwds['hold'] = self.get_input('hold')

        res = self.axe.pie(self.get_input('x'), **kwds)

        self.update_figure()
        return self.axe, res


class PyLabBar(Plotting):
    """See pylab.bar for details.

    .. todo:: !!!!!!!!!! this node is not yet completed.


    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    def __init__(self):
        inputs = [
            {'name':'left', 'interface':ISequence, 'value':[]},
            {'name':'height', 'interface':ISequence, 'value':[]}
        ]
        Plotting.__init__(self, inputs)


    def __call__(self, inputs):
        from pylab import bar, hold, cla

        self.figure()
        self.axes()
        cla()
        left = self.get_input('left')
        height = self.get_input('height')

        if type(left)!=list:
            left = [left]


        res = None
        if type(left[0])==float:
            width = left[1] - left[0]
            res = bar(left[1:], height, width=width)
        else:
            c = enumerate(tools.colors)
            for x,y in zip(left, height):
                color = c.next()
                #width = x[1]-x[0]
                width=0.1
                res = bar(x[1:],y, width=width, color=color[1], alpha=0.5)
                hold(True)
        self.update_figure()

        return self.axe, res



class PyLabCohere(Plotting):
    """See pylab.cohere for details.

    A function or a vector of length *NFFT*. To create window
          vectors see :func:`window_hanning`, :func:`window_none`,
          :func:`numpy.blackman`, :func:`numpy.hamming`,
          :func:`numpy.bartlett`, :func:`scipy.signal`,
          :func:`scipy.signal.get_window`, etc. The default is
          :func:`window_hanning`.  If a function is passed as the
          argument, it must take a data segment as an argument and
          return the windowed version of the segment.

    :Example:

    .. dataflow:: openalea.pylab.test cohere
        :width: 50%

        **The `openalea.pylab.test.cohere` dataflow.**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'cohere'),{},pm=pm )

    .. todo:: kwargs does not yet accept the node Line2D

    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    def __init__(self):
        inputs = [
            {'name':'x',            'interface':None,   'value':None},
            {'name':'y',            'interface':None,   'value':None},
            {'name':'NFFT',         'interface':IInt,   'value':256},
            {'name':'Fs',           'interface':IFloat, 'value':2.},
            {'name':'Fc',           'interface':IFloat, 'value':0},
            {'name':'detrend',      'interface':IEnumStr(tools.detrends.keys()), 'value':'none'},
            {'name':'window',       'interface':IEnumStr(tools.windows.keys()), 'value':'hanning'},
            {'name':'noverlap',     'interface':IInt,   'value':0},
            {'name':'pad_to',       'interface':IInt,   'value':None},
            {'name':'sides',        'interface':IEnumStr(tools.sides), 'value':'default'},
            {'name':'scale_by_freq','interface':IBool,  'value':True},
            {'name':'kwargs(line2d)','interface':IDict,  'value':{}},
            ]
        Plotting.__init__(self, inputs)
        self.add_output(name='output')

    def __call__(self, inputs):
        from pylab import cohere, detrend_none, detrend_linear, detrend_mean, hold, Line2D
        import pylab

        self.figure()
        self.axes()

        kwds = {}
        line2d = self.get_input('kwargs(line2d)')
        if type(line2d)==Line2D:
            kwds = line2d.properties()
        else:
            for key,value in self.get_input('kwargs(line2d)').iteritems():
                kwds[key] = value
        for x in ['children',  'path','xydata','transformed_clip_path_and_affine' ]:
            try:
                del kwds[x]
            except:
                pass

        NFFT = self.get_input('NFFT')
        Fs = self.get_input('Fs')
        Fc = self.get_input('Fc')
        detrend = getattr(pylab, 'detrend_'+self.get_input('detrend'))
        try:
            window = tools.windows[self.get_input('window')]
        except:
            window = self.get_input('window')
        noverlap = self.get_input('noverlap')
        pad_to = self.get_input('pad_to')
        sides = self.get_input('sides')
        scale_by_freq = self.get_input('scale_by_freq')

        cxy = None
        freq = None
        #scale_by_freq not used due to a wierd behaviour, not understood
        try:

            cxy, freq = cohere(self.get_input('x'), self.get_input('y'),
                               NFFT=NFFT, Fs=Fs, Fc=Fc, detrend=detrend,
                               window=window, noverlap=noverlap, pad_to=pad_to,
                               sides=sides, **kwds)

        except:
            xinputs=self.get_input('x')
            if type(xinputs)!=list:
                xinputs = [xinputs]
            if type(xinputs[0])==Line2D:
                for x in xinputs:
                    line2dkwds = tools.get_kwds_from_line2d(x, kwds)
                    for this in ['facecolor', 'children',  'path','xydata','transformed_clip_path_and_affine' ]:
                        try:
                            del line2dkwds[this]
                        except:
                            pass
                    #returns the processed data ?
                    cxy, freq = cohere(x.get_xdata(orig=False), x.get_ydata(orig=False),
                                       NFFT=NFFT, Fs=Fs, Fc=Fc, detrend=detrend,
                               window=window, noverlap=noverlap, pad_to=pad_to,
                               sides=sides, **line2dkwds)
                    hold(True)

        self.update_figure()
        return self.get_input('axes'), (cxy, freq)



class PyLabHexBin(Plotting):
    """See pylab.boxplot help for detailed help.


     .. todo:: tohis documentation

    see pylab.hexbin for details

    :param x: a 1d array
    :param y: a 1d array
    :param C: If *C* is specified, it specifies values at the coordinate (x[i],y[i])

    ..todo:: norm/extent/reduce_c_function

    :Example:

    .. dataflow:: openalea.pylab.test hexbin
        :width: 50%

        **The `openalea.pylab.test.hexbin` dataflow.**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'hexbin'),{},pm=pm )


    the kwargs can be : matplotlib.collections.Collection().properties()
    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """

    def __init__(self):
        import numpy as np
        inputs = [
            {'name':"x"},
            {'name':"y"},
            {'name':"C", 'interface':None, 'value':None},
            {'name':"gridsize", 'interface':IInt, 'value':100},
            {'name':"bins", 'interface':IInt, 'value':None},
            {'name':"xscale", 'interface':IEnumStr(tools.scale.keys()), 'value':'linear'},
            {'name':"yscale", 'interface':IEnumStr(tools.scale.keys()), 'value':'linear'},
            {'name':"cmap", 'interface':IEnumStr(tools.cmaps.keys()), 'value':'jet'},
            {'name':"norm", 'interface':None, 'value':None},
            {'name':"vmin", 'interface':IFloat, 'value':None},
            {'name':"vmax", 'interface':IFloat, 'value':None},
            {'name':"alpha", 'interface':IFloat(0,1,0.1), 'value':1.0},
            {'name':"linewidths", 'interface':IFloat(0,10,1), 'value':None},
            {'name':"edgecolors", 'interface':IEnumStr(tools.colors.keys()), 'value':'None'},
            {'name':"reduce_C_function", 'interface':None, 'value':np.mean},
            {'name':"mincnt", 'interface':IInt, 'value':None},
            {'name':"marginals", 'interface':IBool, 'value':True},
            {'name':"extent", 'interface':None, 'value':None},
            {'name':"kwargs(collection)", 'interface':IDict, 'value':{}},
        ]

        """         reduce_C_function = np.mean, """
        Plotting.__init__(self, inputs)
        self.add_output(name='output')

    def __call__(self, inputs):
        from pylab import hexbin

        x = self.get_input('x')
        y = self.get_input('y')
        C = self.get_input('C')
        gridsize = self.get_input('gridsize')
        bins = self.get_input('bins')

        xscale = self.get_input('xscale')
        yscale = self.get_input('yscale')
        cmap = self.get_input('cmap')
        norm = self.get_input('norm')
        vmin = self.get_input('vmin')
        vmax = self.get_input('vmax')
        alpha = self.get_input('alpha')
        linewidths = self.get_input('linewidths')
        edgecolors = tools.colors[self.get_input('edgecolors')]
        reduce_C_function = self.get_input('reduce_C_function')
        mincnt = self.get_input('mincnt')
        marginals = self.get_input('marginals')
        extent = self.get_input('extent')

        kwds={}
        for key, value in self.get_input('kwargs(collection)'):
            kwds[key] = value

        self.figure()
        self.axes()

        output = hexbin(x, y, C=C, gridsize=gridsize, bins=bins,
                        xscale=xscale, yscale=yscale,
                        cmap=cmap, norm=norm, vmin=vmin, vmax=vmax,
                        alpha=alpha, linewidths=linewidths, edgecolors=edgecolors,
                        reduce_C_function=reduce_C_function,
                        marginals=marginals, extent=extent,
                        mincnt=mincnt,
                        **kwds)

        self.update_figure()
        return self.axe, output


class PyLabCLabel(Node):
    """This is used by PyLabContour to set the label of isocontours

    .. seealso:: PyLabContour
    """

    def __init__(self):
        Node.__init__(self)
        self.add_input(name='axes')
        self.add_input(name='CS')
        self.add_input(name='v')
        self.add_input(name='fontsize', interface=IInt, value=10)
        self.add_input(name='colors', interface=IEnumStr(tools.colors.keys()), value='None')
        self.add_input(name='inline', interface=IBool, value=True)
        self.add_input(name='inline_spacing', interface=IInt, value=5)
        self.add_input(name='fmt', interface=IStr, value='%1.3f')
        self.add_input(name='manual', interface=IBool, value=False)
        self.add_input(name='rightside_up', interface=IBool, value=True)
        self.add_input(name='use_clabeltext', interface=IBool, value=False)
        self.add_output(name='axes')
        self.add_output(name='output')

    def __call__(self, inputs):
        from pylab import clabel
        kwds = {}
        kwds['fontsize'] = self.get_input('fontsize')
        kwds['inline'] = self.get_input('inline')
        kwds['rightside_up'] = self.get_input('rightside_up')
        kwds['inline_spacing'] = self.get_input('inline_spacing')
        kwds['fmt'] = self.get_input('fmt')
        kwds['colors'] = tools.colors[self.get_input('colors')]
        kwds['manual'] = self.get_input('manual')
        kwds['rightside_up'] = self.get_input('rightside_up')
        kwds['use_clabeltext'] = self.get_input('use_clabeltext')

        CS = self.get_input('CS')
        v = self.get_input('v')
        if v:
            res = clabel(CS, v, **kwds)
        else:
            res = clabel(CS, **kwds)

        from pylab import gca
        gca().get_figure().canvas.draw()

        return self.get_input('axes'), res







#class PyLabPcolormesh(Plotting, PcolorInterface): is exactly the same as pcolor but the color optio does not exist.
class PyLabPcolor(Plotting):
    """See pylab.pcolor for details

    :Example:

    .. dataflow:: openalea.pylab.test pcolor
        :width: 50%

        **The `openalea.pylab.test.pcolor` dataflow.**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'pcolor'),{},pm=pm )

    .. todo:: tohis documentation

    .. note:: pcolormesh is equivalent to pcolor.

    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    def __init__(self):
        Node.__init__(self)
        inputs = [
            {'name':"X"},
            {'name':"Y"},
            {'name':"Z"},
            {'name':'cmap', 'interface':IEnumStr(tools.cmaps.keys()), 'value':'jet'},
            {'name':"norm", 'interface':None, 'value':None},
            {'name':"vmin",   'interface':IFloat, 'value' : None},
            {'name':"vmax",   'interface':IFloat, 'value' : None},
            {'name':"alpha", 'interface':IFloat(0,1,0.1), 'value':1.0},
            {'name':"shading",   'interface':IEnumStr(tools.shadings.keys()), 'value' : 'flat'},
            {'name':"kwargs(polycollection)",    'interface':IDict,     'value' : {}},
        ]

        Plotting.__init__(self, inputs)
        self.add_output(name='output')

    def __call__(self, inputs):
        from pylab import pcolor, cla
        self.figure()
        self.axes()

        kwds = {}
        X = self.get_input('X')
        Y = self.get_input('Y')
        Z = self.get_input('Z')
        cmap = self.get_input('cmap')
        norm = self.get_input('norm')
        vmin = self.get_input('vmin')
        vmax = self.get_input('vmax')
        alpha = self.get_input('alpha')
        shading = self.get_input('shading')
        kwds = {}
        for key, value in self.get_input('kwargs(polycollection)').iteritems():
            kwds[key] = value

        if X is not None and Y is not None:
            output = pcolor(X, Y, Z, cmap=cmap, norm=norm, vmin=vmin, vmax=vmax, alpha=alpha, shading=shading, **kwds)
        elif Z is not None:
            output = pcolor(Z, cmap=cmap, norm=norm, vmin=vmin, vmax=vmax, alpha=alpha, shading=shading, **kwds)
        else:
            raise ValueError('Z is compulsary. If X provided, Y must be provided as well.')

        self.update_figure()
        return self.axe, output




class PyLabContour(Plotting):
    """See pylab.contour for details.

    :Example:

    .. dataflow:: openalea.pylab.test contour
        :width: 50%

        **The `openalea.pylab.test.contour` dataflow.**


    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'contour'),{},pm=pm )



    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    def __init__(self):

        inputs = [
            {'name':"X"},
            {'name':"Y"},
            {'name':"Z"},
            {'name':"N or V"},

            # specific to contour
            {'name':"linewidths", 'interface':IFloat, 'value':None},
            {'name':"linestyles", 'interface':IEnumStr(tools.linestyles.keys()), 'value':'solid'},
            {'name':"colors", 'interface':IEnumStr(tools.colors.keys()), 'value':'None'},
            {'name':"alpha", 'interface':IFloat(0,1,0.1), 'value':1.0},
            {'name':"cmap", 'interface':None, 'value':None},
            {'name':"norm", 'interface':None, 'value':None},
            {'name':"levels", 'interface':ISequence, 'value':[]},
            {'name':"origin", 'interface':IEnumStr(tools.origins.keys()), 'value':'None'},
            {'name':"extent", 'interface':None, 'value':None},
            {'name':"locator", 'interface':None, 'value':None},
            {'name':"extend", 'interface':IEnumStr(tools.extends.keys()), 'value':'neither'},
            {'name':"xunits", 'interface':None, 'value':None},
            {'name':"yunits", 'interface':None, 'value':None},
            {'name':"filled", 'interface':IBool, 'value':False},
        ]
        Plotting.__init__(self, inputs)
        self.add_output(name='output')

    def __call__(self, inputs):
        from pylab import contour, contourf, hold

        kwds={}
        X = self.get_input('X')
        Y = self.get_input('Y')
        Z = self.get_input('Z')
        if Z == None:
            raise ValueError('Z must be connected to a 2D array at least!')

        NV = self.get_input('N or V')
        if type(NV)==int and NV<=0:
            NV = None

        kwds['linewidths']=self.get_input('linewidths')
        kwds['alpha']=self.get_input('alpha')
        kwds['colors']=tools.colors[self.get_input('colors')]
        kwds['xunits']=self.get_input('xunits')
        kwds['yunits']=self.get_input('yunits')
        kwds['norm']=self.get_input('norm')
        kwds['levels']=self.get_input('levels')
        kwds['origin']=tools.origins[self.get_input('origin')]
        kwds['extent']=self.get_input('extent')
        kwds['extend']=tools.extends[self.get_input('extend')]
        if self.get_input('linestyles') in [None, 'None']:
            kwds['linestyles']='solid'
        else:
            kwds['linestyles']=tools.linestyles[self.get_input('linestyles')]
        if self.get_input('cmap'):
            kwds['cmap']=self.get_input('cmap')

        self.figure()
        self.axes()



        if X == None and Y == None:
            if NV == None:
                if self.get_input('filled')==True:
                    c = kwds['colors']
                    kwds['colors'] = None
                    contourf(Z, **kwds)
                    hold(True)
                    kwds['colors'] = c
                    CS = contour(Z, **kwds)
                else:
                    CS = contour(Z, **kwds)
            else:
                if self.get_input('filled')==True:
                    c = kwds['colors']
                    kwds['colors'] = None
                    contourf(Z, NV, **kwds)
                    hold(True)
                    kwds['colors'] = c
                    CS = contour(Z, NV, **kwds)
                else:
                    CS = contour(Z, NV, **kwds)
        else: #X,Y,Z case
            if NV == None:
                if self.get_input('filled')==True:
                    c = kwds['colors']
                    kwds['colors'] = None
                    contourf(X, Y, Z, **kwds)
                    hold(True)
                    kwds['colors'] = c
                    CS = contour(X, Y, Z, **kwds)
                else:
                    CS = contour(X, Y, Z, **kwds)
            else:
                if self.get_input('filled')==True:
                    c = kwds['colors']
                    kwds['colors'] = None
                    contourf(X, Y, Z, NV,  **kwds)
                    hold(True)
                    kwds['colors'] = c
                    CS = contour(X, Y, Z, NV, **kwds)
                else:
                    CS = contour(X, Y, Z, NV, **kwds)

        from pylab import  gca
        gca().get_figure().canvas.draw()
        self.update_figure()
        return self.get_input('axes'), CS



class PyLabPsd(Plotting):
    """See pylab.psd for details.


    VisuAlea version of pylab.psd

    :param x: the signal to analyse (a 1D- array)
    :param NFFT: The number of data points used in each block for
        the FFT. The default is 256.
    :param Fs:  The sampling frequency. The default is 2.
    :param Fc:   The center frequency of *x*. Default is 0.
    :param noverlap: The number of points of overlap between blocks.
        The default value is 0.
    :param sides: Specifies which sides of the PSD to return. Default is 'default'.
    :param pad_to:  The number of points to which the data segment is padded when
          performing the FFT. The default is None.
    :param detrend:  The function applied to each segment before fft-ing,
          designed to remove the mean or linear trend (default is 'none')
    :param scale_by_freq:   (default is True)
    :param window: function or a vector of length *NFFT*. default is hanning window
        To create other window, use the :class:`~openalea.pylab_text_wralea.py_pylab.PyLabWindow` node.

    :Example:

    .. dataflow:: openalea.pylab.test psd
        :width: 50%

        **The `openalea.pylab.test.psd` dataflow.** T



    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'psd'),{},pm=pm )



    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    def __init__(self):
        inputs = [
            {'name':'x'},
            {'name':'NFFT',         'interface':IInt,   'value':256},
            {'name':'Fs',           'interface':IFloat, 'value':2.},
            {'name':'Fc',           'interface':IFloat, 'value':0},
            {'name':'detrend',      'interface':IEnumStr(tools.detrends.keys()), 'value':'none'},
            {'name':'window',       'interface':IEnumStr(tools.windows.keys()), 'value':'hanning'},
            {'name':'noverlap',     'interface':IInt,   'value':0},
            {'name':'pad_to',       'interface':IInt,   'value':None},
            {'name':'sides',        'interface':IEnumStr(tools.sides), 'value':'default'},
            {'name':'scale_by_freq','interface':IBool,  'value':None},
            {'name':'kwargs(line2d)','interface':IDict,  'value':{}},
        ]
        Plotting.__init__(self, inputs)
        self.add_output(name='output')


    def __call__(self, inputs):

        from pylab import  psd, Line2D
        self.figure()
        self.axes()

        kwds = {}
        line2d = self.get_input('kwargs(line2d)')
        if type(line2d)==Line2D:
            kwds = line2d.properties()
        else:
            for key,value in self.get_input('kwargs(line2d)').iteritems():
                kwds[key] = value
        for this in ['axes', 'children', 'path','data','ydata','xdata',
                     'xydata','transformed_clip_path_and_affine', 'transform' ]:
            try:
                del kwds[this]
            except:
                pass

        x = self.get_input('x')


        NFFT = self.get_input('NFFT')
        Fs = self.get_input('Fs')
        Fc = self.get_input('Fc')
        import pylab
        from pylab import detrend_none, detrend_mean, detrend_mean
        detrend = getattr(pylab, 'detrend_'+self.get_input('detrend'))

        try:
            window = tools.windows[self.get_input('window')]
        except:
            window = self.get_input('window')

        noverlap = self.get_input('noverlap')
        pad_to = self.get_input('pad_to')
        sides = self.get_input('sides')
        scale_by_freq = self.get_input('scale_by_freq')


        res = psd(x, NFFT=NFFT, Fs=Fs, Fc=Fc, detrend=detrend,
                  window=window, noverlap=noverlap, pad_to=pad_to,
                  sides=sides, scale_by_freq=scale_by_freq, **kwds)


        self.update_figure()
        return self.axe, res


class PyLabCsd(Plotting):
    """See pylab.csd for details


    VisuAlea version of pylab.csd

    :param x: the signal to analyse (a 1D- array)
    :param y: the signal to analyse (a 1D- array)
    :param NFFT: The number of data points used in each block for
        the FFT. The default is 256.
    :param Fs:  The sampling frequency. The default is 2.
    :param Fc:   The center frequency of *x*. Default is 0.
    :param noverlap: The number of points of overlap between blocks.
        The default value is 0.
    :param sides: Specifies which sides of the PSD to return. Default is 'default'.
    :param pad_to:  The number of points to which the data segment is padded when
          performing the FFT. The default is None.
    :param detrend:  The function applied to each segment before fft-ing,
          designed to remove the mean or linear trend (default is 'none')
    :param scale_by_freq:   (default is True)
    :param window: function or a vector of length *NFFT*. default is hanning window
        To create other window, use the :class:`~openalea.pylab_text_wralea.py_pylab.PyLabWindow` node.


    :Example:

    .. dataflow:: openalea.pylab.test csd
        :width: 50%

        **The `openalea.pylab.test.csd` dataflow.** The input data (test_image.npy)

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'csd'),{},pm=pm )


    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """

    def __init__(self):
        inputs = [
            {'name':'x'},
            {'name':'y'},
            {'name':'NFFT',         'interface':IInt,   'value':256},
            {'name':'Fs',           'interface':IFloat, 'value':2.},
            {'name':'Fc',           'interface':IFloat, 'value':0},
            {'name':'detrend',      'interface':IEnumStr(tools.detrends.keys()), 'value':'none'},
            {'name':'window',       'interface':IEnumStr(tools.windows.keys()), 'value':'hanning'},
            {'name':'noverlap',     'interface':IInt,   'value':0},
            {'name':'pad_to',       'interface':IInt,   'value':None},
            {'name':'sides',        'interface':IEnumStr(tools.sides), 'value':'default'},
            {'name':'scale_by_freq','interface':IBool,  'value':None},
            {'name':'kwargs(line2d)','interface':IDict,  'value':{}},
        ]
        Plotting.__init__(self, inputs)
        self.add_output(name='output')



    def __call__(self, inputs):

        from pylab import  csd, Line2D
        self.figure()
        self.axes()

        kwds = {}
        line2d = self.get_input('kwargs(line2d)')
        if type(line2d)==Line2D:
            kwds = line2d.properties()
        else:
            for key,value in self.get_input('kwargs(line2d)').iteritems():
                kwds[key] = value
        for this in ['axes', 'children', 'path','data','ydata','xdata',
                     'xydata','transformed_clip_path_and_affine', 'transform' ]:
            try:
                del kwds[this]
            except:
                pass

        x = self.get_input('x')
        y = self.get_input('y')

        NFFT = self.get_input('NFFT')
        Fs = self.get_input('Fs')
        Fc = self.get_input('Fc')
        import pylab
        from pylab import detrend_none, detrend_mean, detrend_mean
        detrend = getattr(pylab, 'detrend_'+self.get_input('detrend'))

        try:
            window = tools.windows[self.get_input('window')]
        except:
            window = self.get_input('window')

        noverlap = self.get_input('noverlap')
        pad_to = self.get_input('pad_to')
        sides = self.get_input('sides')
        scale_by_freq = self.get_input('scale_by_freq')


        res = csd(x, y, NFFT=NFFT, Fs=Fs, Fc=Fc, detrend=detrend,
                  window=window, noverlap=noverlap, pad_to=pad_to,
                  sides=sides, scale_by_freq=scale_by_freq, **kwds)


        self.update_figure()
        return self.axe, res




class PyLabSpecgram(Plotting):
    """See pylab.specgram for details.


    VisuAlea version of pylab.specgram

    :param x: the signal to analyse (a 1D- array)
    :param NFFT: The number of data points used in each block for
        the FFT. The default is 128.
    :param Fs:  The sampling frequency. The default is 2.
    :param Fc:   The center frequency of *x*. Default is 0.
    :param noverlap: The number of points of overlap between blocks.
        The default value is 128.
    :param sides: Specifies which sides of the PSD to return. Default is 'default'.
    :param pad_to:  The number of points to which the data segment is padded when
          performing the FFT. The default is None.
    :param detrend:  The function applied to each segment before fft-ing,
          designed to remove the mean or linear trend (default is 'none')
    :param scale_by_freq:   (default is True)
    :param window: function or a vector of length *NFFT*. default is hanning window
        To create other window, use the :class:`~openalea.pylab_text_wralea.py_pylab.PyLabWindow` node.


    :Example:

    .. dataflow:: openalea.pylab.test specgram
        :width: 50%

        **The `openalea.pylab.test.specgram` dataflow.**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'specgram'),{},pm=pm )


    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """

    def __init__(self):


        inputs = [
            {'name':'x'},
            {'name':'NFFT',         'interface':IInt,   'value':256},
            {'name':'Fs',           'interface':IFloat, 'value':2.},
            {'name':'Fc',           'interface':IFloat, 'value':0},
            {'name':'detrend',      'interface':IEnumStr(tools.detrends.keys()), 'value':'none'},
            {'name':'window',       'interface':IEnumStr(tools.windows.keys()), 'value':'hanning'},
            {'name':'noverlap',     'interface':IInt,   'value':128},
            {'name':'xextent',     'interface':IInt,   'value':None},
            {'name':'cmap',     'interface':IEnumStr(tools.cmaps.keys()),   'value':'jet'},
            {'name':'pad_to',       'interface':IInt,   'value':None},
            {'name':'sides',        'interface':IEnumStr(tools.sides), 'value':'default'},
            {'name':'scale_by_freq','interface':IBool,  'value':True},
            {'name':'kwargs(line2d)','interface':IDict,  'value':{}},
        ]
        Plotting.__init__(self, inputs)
        self.add_output(name='output')
        #         xextent=None,

    def __call__(self, inputs):
        from pylab import  specgram, Line2D
        self.figure()
        self.axes()

        kwds = {}
        line2d = self.get_input('kwargs(line2d)')
        if type(line2d)==Line2D:
            kwds = line2d.properties()
        else:
            for key,value in self.get_input('kwargs(line2d)').iteritems():
                kwds[key] = value
        for x in ['children',  'path','data','ydata','xdata','xydata','transformed_clip_path_and_affine' ]:
            try:
                del kwds[x]
            except:
                pass

        x = self.get_input('x')

        NFFT = self.get_input('NFFT')
        Fs = self.get_input('Fs')
        Fc = self.get_input('Fc')
        import pylab
        from pylab import detrend_none, detrend_mean, detrend_linear
        detrend = getattr(pylab, 'detrend_'+self.get_input('detrend'))
        try:
            window = tools.windows[self.get_input('window')]
        except:
            window = self.get_input('window')
        noverlap = self.get_input('noverlap')
        pad_to = self.get_input('pad_to')
        sides = self.get_input('sides')
        scale_by_freq = self.get_input('scale_by_freq')
        cmap = self.get_input('cmap')

        res = specgram(x, NFFT=NFFT, Fs=Fs, Fc=Fc, detrend=detrend,
                               window=window, noverlap=noverlap, pad_to=pad_to,
                               sides=sides, cmap=cmap,**kwds)

        self.update_figure()
        return self.axe, res


class PyLabStem(Plotting, PlotxyInterface):
    """See pylab.stem for details.

    VisuAlea version of pylab.stem

    :param x: 1D array
    :param y: 1D array
    :param marker_color: color of the marker (see :ref:`colors`)
    :param line_color: color of the line (see :ref:`colors`)
    :param base_color: color of the base line (see ref:`colors`)
    :param marker_style:
    :param line_style:
    :param base_style:

    :return: a axes object

    :Example:

    .. dataflow:: openalea.pylab.test stem
        :width: 50%

        **The `openalea.pylab.test.stem` dataflow.**
    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'stem'),{},pm=pm )


    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """

    def __init__(self):
        PlotxyInterface.__init__(self)
        inputs = [
            {'name': 'x'},
            {'name': 'y'},
            {'name':'marker_color', 'interface':IEnumStr(tools.colors.keys()), 'value':'blue'},
            {'name':'line_color', 'interface':IEnumStr(tools.colors.keys()), 'value':'blue'},
            {'name':'base_color', 'interface':IEnumStr(tools.colors.keys()), 'value':'red'},
            {'name':'marker_style', 'interface':IEnumStr(tools.markers.keys()), 'value':'circle'},
            {'name':'line_style', 'interface':IEnumStr(tools.linestyles.keys()), 'value':'solid'},
            {'name':'base_style', 'interface':IEnumStr(tools.linestyles.keys()), 'value':'solid'},
        ]
        Plotting.__init__(self, inputs)
        self.add_output(name='output')

    def __call__(self, inputs):

        self.figure()
        self.axes()
        kwds = {}
        kwds['markerfmt'] = tools.colors[self.get_input('marker_color')]+ tools.markers[self.get_input('marker_style')]
        kwds['basefmt'] = tools.colors[self.get_input('base_color')]+ tools.linestyles[self.get_input('base_style')]
        kwds['linefmt'] = tools.colors[self.get_input('line_color')]+ tools.linestyles[self.get_input('line_style')]
        c = self.call('stem', kwds)
        self.update_figure()
        return self.axe, c


class PyLabStep(Plotting, PlotxyInterface):
    """See pylab.step for details.

    VisuAlea version of pylab.step

    :param x: 1D array
    :param y: 1D array
    :param marker: marker (see :ref:`markers`)
    :param markersize:  (default is 10)
    :param color: (see ref:`colors`)

    :return: a axes object

    .. todo:: where parameter

    :Example:

    .. dataflow:: openalea.pylab.test step
        :width: 50%

        **The `openalea.pylab.test.step` dataflow.**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'step'),{},pm=pm )


    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    def __init__(self):
        PlotxyInterface.__init__(self)
        inputs = [
                    {'name':'x', 'interface':None, 'value':None},
                    {'name':'y', 'interface':None, 'value':None},
                    {'name':'where', 'interface':IEnumStr(['post','pre','mid']), 'value':'pre'},
                    {'name':'marker', 'interface':IEnumStr(tools.markers.keys()), 'value':'circle'},
                    {'name':'markersize', 'interface':IFloat, 'value':10},
                    {'name':'color', 'interface':IEnumStr(tools.colors.keys()), 'value':'blue'},
                    {'name':'kwargs', 'interface':IDict, 'value':{}}
        ]
        Plotting.__init__(self, inputs)
        self.add_output(name='output')

    def __call__(self, inputs):
        from pylab import cla, gcf

        self.figure()
        self.axes()

        kwds = {}
        kwds['markersize']=self.get_input("markersize")
        kwds['marker']=tools.markers[self.get_input("marker")]
        kwds['color']=tools.colors[self.get_input("color")]
        kwds['where'] = self.get_input('where')
        #todo add kwargs
        c = self.call('step', kwds)
        gcf().canvas.draw()
        self.update_figure()

        return self.axe, c




class PyLabQuiver(Plotting):
    """See pylab.quiver for details.


    :Example:

    .. dataflow:: openalea.pylab.test quiver
        :width: 50%

        **The `openalea.pylab.test.quiver` dataflow.**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'quiver'),{},pm=pm )

    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """

    def __init__(self):

        inputs = [
                    {'name':'X',            'interface':None,                           'value':None},
                    {'name':'Y',            'interface':None,                           'value':None},
                    {'name':'U',            'interface':None,                           'value':None},
                    {'name':'V',            'interface':None,                           'value':None},
                    {'name':'C',            'interface':None,                           'value':None},
                    {'name':'units',        'interface':IEnumStr(tools.units),           'value':'width'},
                    {'name':'angles',       'interface':IEnumStr(tools.angles),          'value':'uv'},
                    {'name':'scale',        'interface':IFloat,                         'value':None},
                    {'name':'width',        'interface':IFloat(0.005, 1, 0.005),      'value':None},
                    {'name':'headwidth',    'interface':IFloat,                         'value':3},
                    {'name':'headlength',   'interface':IFloat,                         'value':5},
                    {'name':'headaxislength','interface':IFloat,                        'value':4.5},
                    {'name':'minshaft',     'interface':IFloat,                         'value':1},
                    {'name':'minlength',    'interface':IFloat,                         'value':1},
                    {'name':'pivot',        'interface':IEnumStr(tools.pivots),               'value':'tail'},
                    {'name':'color',        'interface':IEnumStr(tools.colors.keys()),        'value':'None'},
                    {'name':'polycollection', 'interface':IDict,        'value':{}},
        ]
        Plotting.__init__(self, inputs)
        self.add_output(name='output')

    def __call__(self, inputs):
        from pylab import quiver, cla

        self.figure()
        self.axes()
        cla()

        X = self.get_input('X')
        Y = self.get_input('Y')
        U = self.get_input('U')
        V = self.get_input('V')
        C = self.get_input('C')
        kwds = {}

        for key in ['units', 'angles', 'scale', 'width', 'headwidth', 'headlength', 'headaxislength', 'minshaft', 'minlength']:
            kwds[key]=self.get_input(key)
        if self.get_input('color')!='None':
            kwds['color']=tools.colors[self.get_input('color')]
        for key, value in self.get_input('polycollection').iteritems():
            kwds[key]=value

        if X is None and Y is None and C is None and U is not None and V is not None:
            c = quiver(U, V, **kwds)
        elif X is None and Y is None and C is not None and U is not None and V is not None:
            c = quiver(U, V, C, **kwds)
        elif X is not None and Y is not None and C is None and U is not None and V is not None:
            c = quiver(X, Y, U, V, **kwds)
        elif X is not None and Y is not None and C is not None and U is not None and V is not None:
            c = quiver(X, Y, U, V, C, **kwds)
        else:
            raise SyntaxError('Wrong usage. See documentation. ')

        self.update_figure()
        return self.axe, c


class PyLabFill(Plotting, PlotxyInterface):
    """See pylab.fill for details.




    :param x: 1D array
    :param y: 1D array
    :param linewidth:
    :param facecolor:
    :param patch: connect a :class:`~openalea.pylab_patches.wralea.py_pylab.Patch`.

    :return: a axes object

    :Example:

    .. dataflow:: openalea.pylab.test fill
        :width: 50%

        **The `openalea.pylab.test.fill` dataflow.**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'fill'),{},pm=pm )

    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """

    def __init__(self):
        PlotxyInterface.__init__(self)
        inputs = [
                    {'name':'x'},
                    {'name':'y'},
                    {'name':'linewidth', 'interface':IFloat, 'value':1},
                    {'name':'facecolor', 'interface':IEnumStr(tools.colors.keys()), 'value':'blue'},
                    {'name':'kwargs (Patch)','interface':IDict, 'value':{}},
        ]
        Plotting.__init__(self, inputs)
        self.add_output(name='output')
        #todo : as many patch as x/y

    def __call__(self, inputs):

        self.figure()
        self.axes()
        kwds = self.get_input('kwargs (Patch)')
        kwds['facecolor'] = tools.colors[self.get_input('facecolor')]
        kwds['linewidth'] = self.get_input('linewidth')

        c = self.call('fill', kwds)

        self.update_figure()
        return self.axe, c


class PyLabFillBetween(Plotting, PlotxyInterface):
    """See pylab.fillbetween for details.




    :param x: 1D array
    :param y1: 1D array
    :param y2: 1D array
    :param where:
    :param patch: connect a :class:`~openalea.pylab_patches.wralea.py_pylab.Patch`.

    :return: a axes object

    :Example:

    .. dataflow:: openalea.pylab.demo fill_between
        :width: 50%

        **The `openalea.pylab.demo.fill_between` dataflow.**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.demo', 'fill_between'),{},pm=pm )


    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    def __init__(self):
        PlotxyInterface.__init__(self)
        inputs = [
                    {'name':'x'},
                    {'name':'y1'},
                    {'name':'y2'},
                    {'name':'where', 'interface':IStr, 'value':'None'},
                    {'name':'interpolate', 'interface':IBool, 'value':False},
                    {'name':'kwargs (Patch)','interface':IDict, 'value':{}},
        ]
        Plotting.__init__(self, inputs)
        self.add_output(name='output')


    def __call__(self, inputs):
        from pylab import fill_between

        self.figure()
        self.axes()

        kwds = self.get_input('kwargs (Patch)')
        try:
            del kwds['fill']
        except:
            pass

        x = self.get_input('x')
        y1 = self.get_input('y1')
        y2 = self.get_input('y2')
        where = eval(str(self.get_input('where')))
        interpolate = self.get_input('interpolate')

        c = self.axe.fill_between(x, y1, y2, where=where, interpolate=interpolate, **kwds)

        self.update_figure()
        return self.axe, c







class PyLabErrorBar(Plotting, PlotxyInterface):
    """See pylab.errorbar for details.

    :param x: 1D array
    :param y: 1D array
    :param xerr: 1D array
    :param yerr: 1D array (optional)
    :param ecolor: color of the error bars
    :param elinewidth: width of the errorbars
    :param Patch: a node to provide :class:`Patch` arguments

    .. todo:: fmt='-', capsize=3, barsabove=False, lolims=False, uplims=False, xlolims=False, xuplims=False)

    :param patch: connect a :class:`~openalea.pylab_patches.wralea.py_pylab.Patch`.

    :return: a axes object

    :Example:

    .. dataflow:: openalea.pylab.test errorbar
        :width: 50%

        **The `openalea.pylab.test.errorbar` dataflow.**

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'errorbar'),{},pm=pm )


    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """

    def __init__(self):
        PlotxyInterface.__init__(self)
        inputs = [
                    {'name':'x'},
                    {'name':'y'},
                    {'name':'xerr', 'value':None},
                    {'name':'yerr', 'value':None},
                    {'name':'fmt', 'interface':IEnumStr(tools.linestyles.keys()), 'value':'solid'},
                    {'name':'ecolor', 'interface':IEnumStr(tools.colors.keys()), 'value':'blue'},
                    {'name':'elinewidth', 'interface':IFloat, 'value':None},
                    {'name':'capsize', 'interface':IInt, 'value':3},
                    {'name':'barsabove', 'interface':IBool, 'value':False},
                    {'name':'lolims', 'interface':IBool, 'value':False},
                    {'name':'uplims', 'interface':IBool, 'value':False},
                    {'name':'xuplims', 'interface':IBool, 'value':False},
                    {'name':'xlolims', 'interface':IBool, 'value':False},
                    {'name':'hold', 'interface':IBool, 'value':None},
                    {'name':'kwargs(line2d)','interface':IDict, 'value':{}},

        ]
        Plotting.__init__(self, inputs)
        #todo : as many patch as x/y
        self.add_output(name="output")

    def __call__(self, inputs):
        from pylab import errorbar, Line2D

        self.figure()
        self.axes()

        if type(self.get_input('kwargs(line2d)')) == Line2D:
            kwds = tools.line2d2kwds(self.get_input('kwargs(line2d)'))
            for this in ['axes', 'children',  'path', 'data', 'xdata', 'ydata',
                         'xydata','transform', 'transformed_clip_path_and_affine',]:
                    try:
                        del kwds[this]
                    except:
                        pass
        else:
            kwds = self.get_input('kwargs(line2d)')

        x = self.get_input('x')
        y = self.get_input('y')
        xerr = self.get_input('xerr')
        yerr = self.get_input('yerr')
        fmt = tools.linestyles[self.get_input('fmt')]
        ecolor = tools.colors[self.get_input('ecolor')]
        elinewidth = self.get_input('elinewidth')
        capsize = self.get_input('capsize')
        barsabove = self.get_input('barsabove')
        lolims = self.get_input('lolims')
        uplims = self.get_input('uplims')
        xlolims = self.get_input('xlolims')
        xuplims = self.get_input('xuplims')

        c = errorbar(x, y, xerr=xerr, yerr=yerr,
                     fmt=fmt, ecolor=ecolor,elinewidth=elinewidth,
                     capsize=capsize, uplims=uplims, lolims=lolims,
                     xuplims = xuplims, xlolims=xlolims, **kwds)

        self.update_figure()
        return self.get_input('axes'), c


class PyLabImshow(Plotting):
    """Display the image in *X* to current axes. See pylab.imshow for details.


    :param X: the input image data
    :param cmap: a colormap  (default jet). You can also connect a
        :class:`~openalea.pylab_axes_wralea.py_lab.PyLabColoMap` node
    :param interpolation: (default None)
    :param aspect: changes the image aspect ratio with respect to the axes.
    :param alpha: transparency (default 1)
    :param vmin: used to scale a luminance image to 0-1 (default None)
    :param vmax: used to scale a luminance image to 0-1 (default None)
    :param origin: todo
    :param extent: todo
    :param shape: todo
    :param filternorm: todo
    :param filterrad: todo
    :param arrangment: non-pylab option. See below
    :param kwargs: extra arguments if required



    :additional argument:

        * arrangment a tuple/;ist of 2 integers: If N images are connected to
        the input, the default behaviour is to use pylab.subplot to create a
        n x m grid such that n is close to m.

        You can overwrite this arbitrary layout by setting yourself the n and m
        values using the arrangment but then n x m must be equal to N.

    .. note:: if you set vmin or vmax, you cannot get back its original value (None)
        To reset them, either you need to reload the whole node, or set them to equal values
        like 0 and 0


    :returns:
        * The first connector is the current axe.
        * The second connector is the output of pylab.imshow


    :Example:

    .. dataflow:: openalea.pylab.test imshow
        :width: 50%

        **The `openalea.pylab.test.imshow` dataflow.** The input data (test_image.npy)
        is read 4 times by the *load* node (openalea.numpy). Thus 4 images data sets
        are connected to the `PyLabImshow` node, which arrange the 4 images automatically.

    .. plot::
        :width: 50%

        from openalea.core.alea import *
        pm = PackageManager()
        run_and_display(('openalea.pylab.test', 'imshow'),{},pm=pm )


    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    """
    #@add_docstring(pylab.imshow)
    def __init__(self):
        inputs = [
                    {'name':'X', 'interface':None},
                    {'name':"cmap", 'interface':IEnumStr(tools.cmaps.keys()), 'value':'jet'},
                    {'name':"interpolation", 'interface':IEnumStr(tools.interpolations.keys()), 'value':'None'},
                    {'name':"aspect", 'interface':IEnumStr(tools.aspects.keys()), 'value':'None'},
                    {'name':"alpha", 'interface':IFloat(0., 1., 0.01), 'value':1},
                    {'name':"vmin", 'interface':IFloat, 'value':None},
                    {'name':"vmax", 'interface':IFloat, 'value':None},
                    {'name':"origin", 'interface':None, 'value':None},
                    {'name':"extent", 'interface':None, 'value':None},
                    {'name':"shape", 'interface':None, 'value':None},
                    {'name':"filternorm", 'interface':None, 'value':None},
                    {'name':"filterrad", 'interface':None, 'value':None},
                    {'name':'arrangment','interface':ITuple, 'value':(1,1)},
                    {'name':'kwargs','interface':IDict, 'value':{}},
        ]
        #norm is not implemented: use vmin/vmax instead
        Plotting.__init__(self, inputs)
        self.add_output(name='output')


    def __call__(self, inputs):
        from pylab import imshow, hold, subplot, show

        self.figure()
        #self.axes()

        axes = []
        kwds = self.get_input('kwargs')

        X = self.get_input('X')
        if type(X)!=list:
            X = [X]

        cmap = self.get_input('cmap')
        alpha = self.get_input('alpha')
        vmin = self.get_input('vmin')
        vmax = self.get_input('vmax')
        if vmin==vmax:
            vmin = None
            vmax = None
        interpolation = tools.interpolations[self.get_input('interpolation')]
        aspect = tools.aspects[self.get_input('aspect')]

        #create the proper grid
        try:
            row = self.get_input('arrangment')[0]
            column = self.get_input('arrangment')[1]
            if row*column != len(X):
                assert False
        except:
            from pylab import ceil, floor, sqrt
            row, column  = int(ceil(sqrt(len(X)))), int(floor(sqrt(len(X))))
            if row*column < len(X):
                row, column  = int(ceil(sqrt(len(X)))), int(ceil(sqrt(len(X))))

        count = 0
        for r in range(1, row+1):
            for c in range(1, column+1):
                count+=1
                if count > len(X):
                    break
                axe = subplot(row,column,count)
                axes.append(axe)

                im = imshow(X[count-1], cmap=cmap, interpolation=interpolation,
                                aspect=aspect, vmin=vmin, vmax=vmax,**kwds)

        self.update_figure()
        return axes, im

    """
      *extent*: [ None | scalars (left, right, bottom, top) ]
        Data limits for the axes.  The default assigns zero-based row,
        column indices to the *x*, *y* centers of the pixels.
      *shape*: [ None | scalars (columns, rows) ]
        For raw buffer images
      *filternorm*:
        A parameter for the antigrain image resize filter.  From the
        antigrain documentation, if *filternorm* = 1, the filter normalizes
        integer values and corrects the rounding errors. It doesn't do
        anything with the source floating point values, it corrects only
        integers according to the rule of 1.0 which means that any sum of
        pixel weights must be equal to 1.0.  So, the filter function must
        produce a graph of the proper shape.
      *filterrad*:
        The filter radius for filters that have a radius
        parameter, i.e. when interpolation is one of: 'sinc',
        'lanczos' or 'blackman'

    """


class PyLabColorBar(Node):
    """See pylab.colorbar for details

    :author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>

    :Example:

    .. dataflow:: openalea.pylab.test colorbar
        :width: 50%

        **The `openalea.pylab.test.colorbar` dataflow.**

    """
    def __init__(self):

        Node.__init__(self)
        self.add_input(name='ax')
        self.add_input(name='cax')
        self.add_input(name='orientation', interface=IEnumStr(tools.orientations.keys()), value='vertical')
        self.add_input(name='fraction', interface=IFloat(0.,1,0.01), value=0.15)
        self.add_input(name='pad', interface=IFloat(0.,1,0.01), value=0.05)
        self.add_input(name='shrink', interface=IFloat(0.,1,0.01), value=1)
        self.add_input(name='aspect', interface=IFloat(1,100,0.01), value=20)
        self.add_input(name='extend', interface=IEnumStr(tools.extends.keys()), value='neither')
        self.add_input(name='spacing', interface=IEnumStr(tools.spacings.keys()), value='uniform')
        self.add_input(name='ticks', interface=None, value=None)
        self.add_input(name='format', interface=IStr, value=None)
        self.add_input(name='drawedges', interface=IBool, value=False)
        self.add_input(name='cmap', interface=IEnumStr(tools.cmaps.keys()), value='jet')
        self.add_input(name='kwargs', interface=IDict, value={})

        self.add_output(name='axes')
        self.add_output(name='output')

        self.colorbar = []

    def __call__(self, inputs):
        from pylab import colorbar, gcf

        # cleanup the colorbars
        if len(self.colorbar) != 0:
            for this_colorbar in self.colorbar:
                f = this_colorbar.ax.get_figure()
                f.delaxes(this_colorbar.ax)
            self.colorbar = []

        ax = self.get_input('ax')
        if type(ax) != list:
            ax = [ax]

        cax = self.get_input('cax')

        kwds = {}
        kwds['fraction'] = self.get_input('fraction')
        kwds['orientation'] = self.get_input('orientation') #no need for dictionary conversion since key==value
        kwds['pad'] = self.get_input('pad')
        kwds['shrink'] = self.get_input('shrink')
        kwds['aspect'] = self.get_input('aspect')
        kwds['drawedges'] = self.get_input('drawedges')
        #if len(self.get_input('ticks'))>0:
        #    kwds['ticks'] = self.get_input('ticks')
        kwds['format'] = self.get_input('format')

        cmap = self.get_input('cmap')

        for this_ax in ax:
            c = colorbar(ax=this_ax, cax=cax, cmap=cmap,**kwds)
            self.colorbar.append(c)

        gcf().canvas.draw()

        return ax, self.colorbar


