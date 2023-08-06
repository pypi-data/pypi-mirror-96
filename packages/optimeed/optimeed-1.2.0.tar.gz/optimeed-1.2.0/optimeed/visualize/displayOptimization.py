from optimeed.core.linkDataGraph import LinkDataGraph, HowToPlotGraph
from optimeed.core import Option_class, printIfShown, SHOW_WARNING
from optimeed.visualize.gui.gui_mainWindow import gui_mainWindow
from optimeed.visualize.gui.widgets.widget_graphs_visual import widget_graphs_visual
from optimeed.visualize import start_qt_mainloop, stop_qt_mainloop, process_qt_events
from optimeed.visualize.gui.widgets.graphsVisualWidget.examplesActionOnClick.on_click_showinfo import on_graph_click_showInfo
from optimeed.visualize.gui.widgets.graphsVisualWidget.smallGui import guiPyqtgraph
from threading import Thread
from threading import Timer
from PyQt5 import QtCore
import queue
import os
import traceback


def check_if_must_plot(elem):
    constraints = elem.constraints
    for constraint in constraints:
        if constraint > 0:
            return False
    return True


class OptimizationDisplayer(Option_class):
    """Class used to display optimization process in real time"""
    signal_optimization_over = QtCore.pyqtSignal()

    SHOW_CONSTRAINTS = 0

    def __init__(self, thePipeOpti, listOfObjectives, theOptimizer, additionalWidgets=None):
        """

        :param thePipeOpti: :class:`~optimeed.optimize.optimizer.PipeOptimization`
        :param listOfObjectives: list of :class:`~optimeed.optimize.objAndCons.interfaceObjCons.InterfaceObjCons`
        :param theOptimizer: :class:`~optimeed.optimize.optimizer.Optimizer`
        :param additionalWidgets: list of QtWidgets (instantiated)
        """
        super().__init__()
        self.add_option(self.SHOW_CONSTRAINTS, "Display out of constraint elements", True)
        self.thePipeOpti = thePipeOpti
        self.listOfObjectives = listOfObjectives
        self.theOptimizer = theOptimizer
        if additionalWidgets is None:
            self.additionalWidgets = list()
        else:
            self.additionalWidgets = additionalWidgets

        self.theActionsOnClick = None
        self.theDataLink = None
        self.myWidgetGraphsVisuals = None
        self.id_logOpti = None
        self.windowOpti = None
        self.windowConvergence = None
        self.timer_autorefresh = None

    def set_actionsOnClick(self, theList):
        """Set actions to perform on click, list of :class:`~optimeed.visualize.gui.widgets.widget_graphs_visual.on_graph_click_interface`"""
        self.theActionsOnClick = theList

    def generate_optimizationGraphs(self):
        """Generates the optimization graphs.
       :return: :class:`~optimeed.core.graphs.Graphs`, :class:`~optimeed.core.linkDataGraph.LinkDataGraph`, :class:'~optimeed.visulaize.gui.widgets.widget_graphs_visual.widget_graphs_visual"""

        collection_devices = self.thePipeOpti.get_historic().get_devices()
        collection_logOpti = self.thePipeOpti.get_historic().get_logopti()

        theDataLink = LinkDataGraph()
        id_logOpti = theDataLink.add_collection(collection_logOpti)
        id_devices = theDataLink.add_collection(collection_devices)
        theDataLink.link_collection_to_graph_collection(id_logOpti, id_devices)  # Link the devices to the logopti

        check_plot = None if self.get_optionValue(self.SHOW_CONSTRAINTS) else check_if_must_plot

        if len(self.listOfObjectives) == 2:
            x_label = self.listOfObjectives[0].get_name()
            y_label = self.listOfObjectives[1].get_name()
            howToPlot = HowToPlotGraph('objectives[0]', 'objectives[1]', {'x_label': x_label, 'y_label': y_label, 'is_scattered': True}, check_if_plot_elem=check_plot)
            theDataLink.add_graph(howToPlot)
            howToPlot.exclude_col(id_devices)
        elif len(self.listOfObjectives) == 3:
            for i, objective in enumerate(self.listOfObjectives):
                i_plus_1 = i+1 if i != 2 else 2
                curr_i = i if i != 2 else 0
                x_label = self.listOfObjectives[curr_i].get_name()
                y_label = self.listOfObjectives[i_plus_1].get_name()
                howToPlot = HowToPlotGraph('objectives[{}]'.format(curr_i), 'objectives[{}]'.format(i_plus_1), {'x_label': x_label, 'y_label': y_label, 'is_scattered': True}, check_if_plot_elem=check_plot)
                theDataLink.add_graph(howToPlot)
                howToPlot.exclude_col(id_devices)
        else:
            for i, objective in enumerate(self.listOfObjectives):
                x_label = 'Time [s]'
                y_label = self.listOfObjectives[i].get_name()
                howToPlot = HowToPlotGraph('time', 'objectives[{}]'.format(i), {'x_label': x_label, 'y_label': y_label, 'is_scattered': True}, check_if_plot_elem=check_plot)
                theDataLink.add_graph(howToPlot)
                howToPlot.exclude_col(id_devices)

        theGraphs = theDataLink.createGraphs()
        self.theDataLink = theDataLink
        self.id_logOpti = id_logOpti

        """Generate live graph for the optimization"""
        # Set actions on graph click ...
        if self.theActionsOnClick is None:
            self.theActionsOnClick = list()
            self.theActionsOnClick.append(on_graph_click_showInfo(theDataLink))

        self.myWidgetGraphsVisuals = widget_graphs_visual(theGraphs, highlight_last=True, refresh_time=-1)
        self.__set_graphs_disposition()
        return theGraphs, theDataLink, widget_graphs_visual

    def __change_appearance_violate_constraints(self):
        graphs, theCol = self.theDataLink.get_graph_and_trace_from_collection(self.id_logOpti)
        all_constraints = theCol.get_list_attributes("constraints")
        violate_constraint_indices = list()
        for index, constraints in enumerate(all_constraints):
            for constraint in constraints:
                if constraint > 0:
                    violate_constraint_indices.append(index)  # Index in data
        for graph, trace in graphs:
            theTrace = self.myWidgetGraphsVisuals.get_graph(graph).get_trace(trace)
            theTrace.set_brushes(violate_constraint_indices, (250, 0, 0))

    def __refresh(self):
        self.theDataLink.update_graphs()
        if self.get_optionValue(self.SHOW_CONSTRAINTS):
            self.__change_appearance_violate_constraints()
        self.myWidgetGraphsVisuals.update_graphs()

    def start_autorefresh(self, timer_autosave):
        self.__refresh()
        if timer_autosave > 0:
            self.timer_autorefresh = Timer(timer_autosave, lambda: self.start_autorefresh(timer_autosave))
            self.timer_autorefresh.daemon = True
            self.timer_autorefresh.start()

    def stop_autorefresh(self):
        if self.timer_autorefresh is not None:
            self.timer_autorefresh.cancel()

    def __set_graphs_disposition(self):
        """Set nicely the graphs disposition"""
        allGraphs = self.myWidgetGraphsVisuals.get_all_graphsVisual()
        row = 1
        col = 1
        maxNbrRow = 1
        currRow = 1
        for idGraph in allGraphs:
            self.myWidgetGraphsVisuals.set_graph_disposition(idGraph, row, col)
            if currRow >= maxNbrRow:
                row = 1
                col += 1
            else:
                row += 1
            currRow = row

    def launch_optimization(self, refresh_time=0.1):
        """Perform the optimization and spawn the convergence graphs afterwards.

        :param refresh_time: float indicating the refresh time of the graphs. If it becomes laggy -> use a higher one."""

        self.create_main_window()  # Create the gui

        # Launch optimization in a separate thread
        self.start_autorefresh(refresh_time)

        que = queue.Queue()  # Put results in queue
        threadOpti = Thread(target=lambda: que.put(self.__callback_optimization()))
        threadOpti.start()

        start_qt_mainloop()  # Automatically stops at the end of the optimization

        threadOpti.join()  # This means stop_qt_mainloop has been called (opti finished)
        self.stop_autorefresh()
        resultsOpti, convergence = que.get()

        # noinspection PyBroadException
        try:
            self.windowConvergence, theWidgetGraphsVisuals = self.display_graphs(convergence.get_graphs())
            process_qt_events()

            # Save graphs:
            path_results = self.thePipeOpti.get_historic().foldername
            path_results = os.path.join(path_results, "results")
            os.makedirs(path_results)
            self.myWidgetGraphsVisuals.exportGraphs(os.path.join(path_results, "logopti"))
            theWidgetGraphsVisuals.exportGraphs(os.path.join(path_results, "convergence"))
        except Exception:
            traceback.print_exc()

        return resultsOpti, convergence

    def __callback_optimization(self):
        resultsOpti, convergence = self.theOptimizer.run_optimization()
        stop_qt_mainloop()
        return resultsOpti, convergence

    def close_windows(self):
        if self.windowOpti is not None:
            self.windowOpti.close()

        if self.windowConvergence is not None:
            self.windowConvergence.close()

    @staticmethod
    def display_graphs(theGraphs):
        myWidgetGraphsVisuals = widget_graphs_visual(theGraphs, highlight_last=False, refresh_time=-1)
        guiPyqtgraph(myWidgetGraphsVisuals)  # Add GUI to change action easily and export graphs
        myWindow = gui_mainWindow([myWidgetGraphsVisuals], actionOnWindowClosed=lambda *args: stop_qt_mainloop())
        if not theGraphs.is_empty():
            myWindow.run(False)
        return myWindow, myWidgetGraphsVisuals

    def create_main_window(self):
        """From the widgets and the actions on click, spawn a window and put a gui around widgetsGraphsVisual."""
        guiPyqtgraph(self.myWidgetGraphsVisuals, actionsOnClick=self.theActionsOnClick)  # Add GUI to change action easily and export graphs

        # Add additional widgets to the visualisation
        listOfWidgets = self.additionalWidgets
        listOfWidgets.append(self.myWidgetGraphsVisuals)
        myWindow = gui_mainWindow(listOfWidgets, actionOnWindowClosed=lambda *args: stop_qt_mainloop())
        myWindow.run(False)
        self.windowOpti = myWindow
