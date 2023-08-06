#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2021 A S Lewis
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.


"""Configuration window classes."""


# Import Gtk modules
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf


# Import other modules
import os


# Import our modules
import __main__
import downloads
import formats
import mainapp
import mainwin
import media
import platform
import re
import sys
import urllib.parse
import utils
# Use same gettext translations
from mainapp import _


# Import matplotlib stuff
if mainapp.HAVE_MATPLOTLIB_FLAG:
    from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg
    from matplotlib.figure import Figure
    from matplotlib.ticker import MaxNLocator

# Classes


class GenericConfigWin(Gtk.Window):

    """Generic Python class for windows in which the user can modify various
    settings.

    Inherited by two types of window - 'preference windows' (in which changes
    are applied immediately), and 'edit windowS' (in which changes are stored
    temporarily, and only applied once the user has finished making changes.
    """


    # Standard class methods


#   def __init__():             # Provided by child object


    # Public class methods


#   def is_duplicate():         # Provided by child object


    def setup(self):

        """Called by self.__init__().

        Sets up the config window when it opens.
        """

        # Set the default window size
        self.set_default_size(
            self.app_obj.config_win_width,
            self.app_obj.config_win_height,
        )

        # Set the window's Gtk icon list
        self.set_icon_list(self.app_obj.main_win_obj.win_pixbuf_list)

        # Set up main widgets
        self.setup_grid()
        self.setup_notebook()
        self.setup_button_strip()
        self.setup_gap()

        # Set up tabs
        self.setup_tabs()

        # Procedure complete
        self.show_all()

        # Inform the main window of this window's birth (so that Tartube
        #   doesn't allow an operation to start until all configuration windows
        #   have closed)
        self.app_obj.main_win_obj.add_child_window(self)
        # Add a callback so we can inform the main window of this window's
        #   destruction
        self.connect('destroy', self.close)


    def setup_grid(self):

        """Called by self.setup().

        Sets up a Gtk.Grid, on which a notebook and a button strip will be
        placed. (Each of the notebook's tabs also has its own Gtk.Grid.)
        """

        self.grid = Gtk.Grid()
        self.add(self.grid)


    def setup_notebook(self):

        """Called by self.setup().

        Sets up a Gtk.Notebook, after which self.setup_tabs() is called to fill
        it with tabs.
        """

        self.notebook = Gtk.Notebook()
        self.grid.attach(self.notebook, 0, 1, 1, 1)
        self.notebook.set_border_width(self.spacing_size)
        # It shouldn't be necessary to scroll the notebook's tabs, but we'll
        #   make it possible anyway
        self.notebook.set_scrollable(True)


    def add_notebook_tab(self, name, border_width=None):

        """Called by various functions in the child edit/preference window.

        Adds a tab to the main Gtk.Notebook, creating a Gtk.Grid inside it, on
        which the calling function can add more widgets.

        Args:

            name (str): The name of the tab

            border_width (int): If specified, the border width for the
                Gtk.Grid contained in this tab (usually specified when an inner
                Gtk.Notebook is to be added to this tab). If not specified, a
                default width is used

        Returns:

            The tab created (in the form of a Gtk.Box) and its Gtk.Grid.

        """

        if border_width is None:
            border_width = self.spacing_size

        tab = Gtk.Box()
        self.notebook.append_page(tab, Gtk.Label.new_with_mnemonic(name))
        tab.set_hexpand(True)
        tab.set_vexpand(True)
        tab.set_border_width(self.spacing_size)

        scrolled = Gtk.ScrolledWindow()
        tab.add(scrolled)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)

        grid = Gtk.Grid()
        scrolled.add_with_viewport(grid)
        grid.set_border_width(border_width)
        grid.set_column_spacing(self.spacing_size)
        grid.set_row_spacing(self.spacing_size)

        return tab, grid


    def add_inner_notebook(self, grid):

        """Called by various functions in the child edit/preference window.

        Adds an inner Gtk.Notebook to a tab inside the main Gtk.Notebook.

        Args:

            grid (Gtk.Grid): The widget to which the notebook is added

        Returns:

            Returns the new Gtk.Notebook

        """

        inner_notebook = Gtk.Notebook()
        grid.attach(inner_notebook, 0, 1, 1, 1)
        # It shouldn't be necessary to scroll the notebook's tabs, but we'll
        #   make it possible anyway
        inner_notebook.set_scrollable(True)

        return inner_notebook


    def add_inner_notebook_tab(self, name, notebook):

        """Called by various functions in the child edit/preference window.

        A modified form of self.add_notebook_tab, for tabs to be placd in the
        inner notebook created by a call to self.add_inner_notebook.

        Adds a tab to the specified Gtk.Notebook, creating a Gtk.Grid inside
        it, on which the calling function can add more widgets.

        Args:

            name (str): The name of the tab

            notebook (Gtk.Notebook): The notebook to which the tab is added

        Returns:

            The tab created (in the form of a Gtk.Box) and its Gtk.Grid.

        """

        tab = Gtk.Box()
        notebook.append_page(tab, Gtk.Label.new_with_mnemonic(name))
        tab.set_hexpand(True)
        tab.set_vexpand(True)

        scrolled = Gtk.ScrolledWindow()
        tab.add(scrolled)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)

        grid = Gtk.Grid()
        scrolled.add_with_viewport(grid)
        grid.set_border_width(self.spacing_size)
        grid.set_column_spacing(self.spacing_size)
        grid.set_row_spacing(self.spacing_size)

        return tab, grid


#   def setup_button_strip():   # Provided by child object


    def setup_gap(self):

        """Called by self.setup().

        Adds an empty box beneath the button strip for aesthetic purposes.
        """

        hbox = Gtk.HBox()
        self.grid.attach(hbox, 0, 3, 1, 1)
        hbox.set_border_width(self.spacing_size)


    def close(self, also_self):

        """Called from callback in self.setup().

        Inform the main window that this window is closing.

        Args:

            also_self (an object inheriting from config.GenericConfigWin):
                Another copy of self

        """

        self.app_obj.main_win_obj.del_child_window(self)


    # (Add widgets)


    def add_image(self, grid, image_path, x, y, wid, hei):

        """Called by various functions in the child edit window.

        Adds a Gtk.Image to the tab's Gtk.Grid.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            image_path (str): Full path to the image file to load

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The Gtk.Frame containing the image

        """

        frame = Gtk.Frame()
        grid.attach(frame, x, y, wid, hei)

        image = Gtk.Image()
        frame.add(image)
        image.set_from_pixbuf(
            self.app_obj.file_manager_obj.load_to_pixbuf(image_path),
        )

        return frame


    def add_treeview(self, grid, x, y, wid, hei):

        """Called by various functions in the child preference/edit window.

        Adds a Gtk.Treeview to the tab's Gtk.Grid. No callback function is
        created by this function; it's up to the calling code to supply one.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            A list containing the treeview widget and liststore created

        """

        frame = Gtk.Frame()
        grid.attach(frame, x, y, wid, hei)

        scrolled = Gtk.ScrolledWindow()
        frame.add(scrolled)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)

        treeview = Gtk.TreeView()
        scrolled.add(treeview)
        treeview.set_headers_visible(False)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn(
            '',
            renderer_text,
            text=0,
        )
        treeview.append_column(column_text)

        liststore = Gtk.ListStore(str)
        treeview.set_model(liststore)

        return treeview, liststore


    # (Shared support functions)


    def add_combos_for_graphs(self, grid, row):

        """Called by tabs in ChannelPlaylistEditWin, FolderEditWin and
        SystemPrefWin.

        The tabs that draw graphs share a standard set of comboboxes, with
        which the graph is customised.

        This function is called to create the comboboxes, and to set up
        callbacks so that changes to the settings are remembered between
        windows.

        Args:

            grid (Gtk.Grid): The grid on which widgets are arranged in their
                tab

            row (int): The grid row on which these combos appear

        """

        if isinstance(self, GenericPrefWin):
            pref_win_flag = True
        else:
            pref_win_flag = False

        # Add combos to customise the graph
        combo_list = [
            [_('Downloads'), 'receive'],
            [_('Uploads'), 'upload'],
            [_('File size'), 'size'],
            [_('Duration'), 'duration'],
        ]

        if pref_win_flag:

            combo = self.add_combo_with_data(grid,
                combo_list,
                self.app_obj.graph_data_type,
                0, row, 1, 1,
            )

        else:

            combo = self.add_combo_with_data(grid,
                combo_list,
                None,
                0, row, 1, 1,
            )

            count = -1
            for mini_list in combo_list:
                count += 1
                if mini_list[1] == self.app_obj.graph_data_type:
                    combo.set_active(count)
                    break

        combo.set_hexpand(True)

        combo_list2 = [
            [_('Graph'), 'graph'],
            [_('Bar chart'), 'chart'],
        ]

        if pref_win_flag:

            combo2 = self.add_combo_with_data(grid,
                combo_list2,
                self.app_obj.graph_plot_type,
                1, row, 1, 1,
            )

        else:

            combo2 = self.add_combo_with_data(grid,
                combo_list2,
                None,
                1, row, 1, 1,
            )

            count = -1
            for mini_list in combo_list2:
                count += 1
                if mini_list[1] == self.app_obj.graph_plot_type:
                    combo2.set_active(count)
                    break

        combo2.set_hexpand(True)

        combo_list3 = [
            [_('Show decade'), 60*60*24*365*10],
            [_('Show year'), 60*60*24*365],
            [_('Show quarters'), 60*60*24*90],
            [_('Show month'), 60*60*24*30],
            [_('Show week'), 60*60*24*7],
            [_('Show day'), 60*60*24],
        ]

        if pref_win_flag:

            combo3 = self.add_combo_with_data(grid,
                combo_list3,
                self.app_obj.graph_time_period_secs,
                2, row, 1, 1,
            )

        else:

            combo3 = self.add_combo_with_data(grid,
                combo_list3,
                None,
                2, row, 1, 1,
            )

            count = -1
            for mini_list in combo_list3:
                count += 1
                if mini_list[1] == self.app_obj.graph_time_period_secs:
                    combo3.set_active(count)
                    break

        combo3.set_hexpand(True)
        if self.app_obj.graph_data_type != 'receive' \
        and self.app_obj.graph_data_type != 'upload':
            combo3.set_sensitive(False)

        combo_list4 = [
            [_('Quarters'), 60*60*24*90],
            [_('Months'), 60*60*24*30],
            [_('Weeks'), 60*60*24*7],
            [_('Days'), 60*60*24],
            [_('Hours'), 60*60],
        ]

        if pref_win_flag:

            combo4 = self.add_combo_with_data(grid,
                combo_list4,
                self.app_obj.graph_time_unit_secs,
                3, row, 1, 1,
            )

        else:

            combo4 = self.add_combo_with_data(grid,
                combo_list4,
                None,
                3, row, 1, 1,
            )

            count = -1
            for mini_list in combo_list4:
                count += 1
                if mini_list[1] == self.app_obj.graph_time_unit_secs:
                    combo4.set_active(count)
                    break

        combo4.set_hexpand(True)
        if self.app_obj.graph_data_type != 'receive' \
        and self.app_obj.graph_data_type != 'upload':
            combo4.set_sensitive(False)

        combo_list5 = [
            [_('Red'), 'red'],
            [_('Green'), 'green'],
            [_('Blue'), 'blue'],
            [_('Black'), 'black'],
            [_('White'), 'white'],
        ]

        if pref_win_flag:

            combo5 = self.add_combo_with_data(grid,
                combo_list5,
                self.app_obj.graph_ink_colour,
                4, row, 1, 1,
            )

        else:

            combo5 = self.add_combo_with_data(grid,
                combo_list5,
                None,
                4, row, 1, 1,
            )

            count = -1
            for mini_list in combo_list5:
                count += 1
                if mini_list[1] == self.app_obj.graph_ink_colour:
                    combo5.set_active(count)
                    break

        combo5.set_hexpand(True)

        # (Signal connects from above)
        combo.connect(
            'changed',
            self.on_combo_graph_changed,
            'data_type',
            combo3,
            combo4,
        )
        combo2.connect(
            'changed',
            self.on_combo_graph_changed,
            'plot_type',
            combo3,
            combo4,
        )
        combo3.connect(
            'changed',
            self.on_combo_graph_changed,
            'time_period',
            combo3,
            combo4,
        )
        combo4.connect(
            'changed',
            self.on_combo_graph_changed,
            'time_unit',
            combo3,
            combo4,
        )
        combo5.connect(
            'changed',
            self.on_combo_graph_changed,
            'ink_colour',
            combo3,
            combo4,
        )

        return combo, combo2, combo3, combo4, combo5


    def plot_graph(self, hbox, plot_type, data_type, ink_colour, x_label,
    y_label, x_list, y_list):

        """Called by self.on_button_draw_graph_clicked().

        Plots a graph, using the specified settings and data points.

        Args:

            hbox (Gtk.HBox): The container widget

            plot_type (str): 'graph' or 'chart'

            data_type (str): 'receive', 'upload', 'size' or 'duration'

            ink_colour (str): 'red', 'green', 'blue', 'black' or white'

            x_label, y_label (str): Text for each axis on the graph

            x_list (list): List of data points along the x axis

            y_list (list): List of data points along the y axis (both lists
                should contain the same number of items)

        """

        # Sanity check: when the video counts (values in y_list) are all 0,
        #   matplotlib will try to draw a y-axis with fractional values
        # Check for that, so we can prevent it
        simplify_y_axis_flag = True
        for num in y_list:
            if num:
                simplify_y_axis_flag = False
                break

        # Remove the old figure
        for child in hbox.get_children():
            hbox.remove(child)

        # Plot a new figure
        fig = Figure(dpi = 100)

        ax = fig.add_subplot(1, 1, 1)

        if plot_type == 'graph':
            ax.plot(x_list, y_list, color = ink_colour)
        else:
            ax.bar(x_list, y_list, color = ink_colour)

        # Set up the axes
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        # (Negative values are meaningless, so don't allow them to appear on
        #   the x/y axes)
        if simplify_y_axis_flag:
            ax.set_ylim([0, 1])
        else:
            ax.set_ylim(ymin=0)
        if data_type == 'receive' or data_type == 'upload':
            ax.set_xlim(xmin=0)
        # (Fractional values are also meaningless)
        ax.xaxis.set_major_locator(MaxNLocator(integer = True))
        ax.yaxis.set_major_locator(MaxNLocator(integer = True))
        # (For time graphs, reverse the X axis, to show days ago, etc)
        if data_type == 'receive' or data_type == 'upload':
            ax.set_xlim(ax.get_xlim()[::-1])
        # (For some reason, the x-axis label is drawn below the visible area.
        #   Not sure how to fix that, so move it to the top, in which there is
        #   empty space)
        ax.xaxis.set_label_position('top')
        # (Reduce wasted space around the edges)
        fig.tight_layout()

        canvas = FigureCanvasGTK3Agg(fig)  # a Gtk.DrawingArea
        hbox.add(canvas)

        self.show_all()


    # (Shared callbacks)


    def on_button_draw_graph_clicked(self, button, hbox, combo, combo2,
    combo3, combo4, combo5):

        """Called from callbacks in ChannelPlaylistEditWin,
        FolderEditWin and SystemPrefWin.

        Prepares data for a graph using the specified settings, then calls
        self.plot_graph() to actually draw it.

        Args:

            button (Gtk.Button): The widget clicked

            hbox (Gtk.HBox): The container widget for the graph

            combo, combo2, combo3, combo4, combo5 (Gtk.ComboBox): Five combos
                specifying the data to view:

                The data type ('receive' for download times, 'upload' for
                upload times, 'size' for file size, 'duration' for video
                duration)

                The type of graph to plot ('graph' for a line plot graph, or
                'chart' for a bar chart)

                The period of time used as the span of the x-axis (in seconds,
                e.g. 31536000 is the equivalent of a year)

                The time unit to use (in seconds, e.g. 604800 is the equivalent
                of a week). We count the number of videos for the time unit
                and use it as a single point on the x-axis

                The colour to use ('red', 'green', 'blue', 'black', white')

        """

        # Extract data from the combos

        # Get the data type ('receive', 'upload', 'size' or 'duration')
        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        data_name = model[tree_iter][0]
        data_type = model[tree_iter][1]

        # Get type of graph to plot ('graph' or 'chart')
        tree_iter2 = combo2.get_active_iter()
        model2 = combo2.get_model()
        plot_type = model2[tree_iter2][1]

        # Get the period of time used as the span of the x-axis, in seconds
        tree_iter3 = combo3.get_active_iter()
        model3 = combo3.get_model()
        time_period_secs = int(model3[tree_iter3][1])

        # Get the time unit to use, in seconds
        tree_iter4 = combo4.get_active_iter()
        model4 = combo4.get_model()
        time_unit = model4[tree_iter4][0]
        time_unit_secs = int(model4[tree_iter4][1])
        # The time unit must not be larger than the total period of time
        if time_unit_secs > time_period_secs:
            time_unit_secs = time_period_secs

        # Get the colour to use ('red', 'green', 'blue', 'black', white')
        tree_iter5 = combo5.get_active_iter()
        model5 = combo5.get_model()
        ink_colour = model5[tree_iter5][1]

        # Compile a dictionary of video counts
        # For 'receive' and 'upload', dictonary in the form
        #   frequency_dict[time_unit_increment] = number_of_videos
        # For 'size', dictionary in the form
        #   frequency_dict[size_category] = number_of_videos
        # For 'duration', dictionary in the form
        #   frequency_dict[duration_category] = number_of_videos
        # When called by SystemPrefWin, use the entire database
        # When called by ChannelPlaylistEditWin or FolderEditWin, use only the
        #   children of that container
        # 'size_category' and 'duration_category' are arbitrary ranges of
        #   values, chosen for aesthetic reasons
        if isinstance(self, GenericEditWin):

            if data_type == 'receive' or data_type == 'upload':

                frequency_dict = self.edit_obj.compile_all_videos_by_frequency(
                    data_type,
                    time_unit_secs,
                    {},
                )

            elif data_type == 'size':

                frequency_dict = self.edit_obj.compile_all_videos_by_size(
                    {},
                )

            elif data_type == 'duration':

                frequency_dict = self.edit_obj.compile_all_videos_by_duration(
                    {},
                )

        else:

            frequency_dict = {}

            for dbid in self.app_obj.media_name_dict.values():

                media_data_obj = self.app_obj.media_reg_dict[dbid]
                # Ignore private (system) folders, because they contain
                #   media.Video objects also stored in public folders
                if not isinstance(media_data_obj, media.Folder) \
                or not media_data_obj.priv_flag:

                    if data_type == 'receive' or data_type == 'upload':

                        frequency_dict \
                        = media_data_obj.compile_all_videos_by_frequency(
                            data_type,
                            time_unit_secs,
                            frequency_dict,
                        )

                    elif data_type == 'size':

                        frequency_dict \
                        = media_data_obj.compile_all_videos_by_size(
                            frequency_dict,
                        )

                    elif data_type == 'duration':

                        frequency_dict \
                        = media_data_obj.compile_all_videos_by_duration(
                            frequency_dict,
                        )

        # Compile two lists, with each index giving the x and y coordinates
        #   for the graph to be plotted
        if data_type == 'receive' or data_type == 'upload':

            period_list = []
            frequency_list = []

            for i in range(0, int((time_period_secs / time_unit_secs) + 1)):

                period_list.append(i)
                if i in frequency_dict:
                    frequency_list.append(frequency_dict[i])
                else:
                    frequency_list.append(0)

            # Draw the graph
            self.plot_graph(
                hbox,
                plot_type,
                data_type,
                ink_colour,
                time_unit,
                data_name,
                period_list,
                frequency_list,
            )

        else:

            # NB If these labels are changed, when the corresponding literal
            #   values in media.GenericContainer.compile_all_videos_by_size()
            #   and .compile_all_videos_by_duration() must be changed too
            if data_type == 'size':

                label_list = [
                    '10MB', '25MB', '50MB', '100MB', '250MB',
                    '500MB', '1GB', '2GB', '5GB', '5GB+',
                ]

            else:

                label_list = [
                    '10s', '1m', '5m', '10m', '20m',
                    '30m', '1h', '2h', '5h', '5h+',
                ]

            frequency_list = []
            for label in label_list:

                if label in frequency_dict:
                    frequency_list.append(frequency_dict[label])
                else:
                    frequency_list.append(0)

            # Draw the graph
            self.plot_graph(
                hbox,
                plot_type,
                data_type,
                ink_colour,
                data_name,
                _('Videos'),
                label_list,
                frequency_list,
            )


    def on_combo_graph_changed(self, combo, combo_type, combo2, combo3):

        """Called from callback in self.add_combos_for_graphs().

        Graphs are drawn with five standard combos for customising the graph.
        When the user selects a new setting in a combo, store the value.

        In some cases, one or more of the combos must be (de)sensitised.

        Args:

            combo (Gtk.ComboBox): The widget clicked

            combo_type (str): A string describing which IV to update:
                'data_type', 'plot_type', 'time_period', 'time_unit',
                'ink_colour'

            combo2, combo3 (Gtk.ComboBox): Other combos to be (de)sensitised

        """

        # Extract data from the combo
        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        value = model[tree_iter][1]
        # Update IVs
        self.app_obj.set_graph_values(combo_type, value)

        # (De)sensitise other combos, as appropriate
        if combo_type == 'data_type':

            if (value == 'receive' or value == 'upload'):
                combo2.set_sensitive(True)
                combo3.set_sensitive(True)
            else:
                combo2.set_sensitive(False)
                combo3.set_sensitive(False)


class GenericEditWin(GenericConfigWin):

    """Generic Python class for windows in which the user can modify various
    settings in a class object (such as a media.Video or an
    options.OptionsManager object).

    The modifications are stored temporarily, and only applied once the user
    has finished making changes.
    """


    # Standard class methods


#   def __init__():             # Provided by child object


    # Public class methods


    def is_duplicate(self, app_obj, edit_obj):

        """Called by self.__init__.

        Don't open this edit window, if another with the same .edit_obj is
        already open.

        Args:

            app_obj (mainapp.TartubeApp): The main application object

            edit_obj (options.OptionsManager): The object whose attributes will
                be edited in this window

        Return values:

            True if a duplicate is found, False if not

        """

        for config_win_obj in app_obj.main_win_obj.config_win_list:

            if isinstance(config_win_obj, GenericEditWin) \
            and config_win_obj.edit_obj == edit_obj:

                # Duplicate found
                config_win_obj.present()
                return True

        # Not a duplicate
        return False


#   def setup():                # Inherited from GenericConfigWin


#   def setup_grid():           # Inherited from GenericConfigWin


#   def setup_notebook():       # Inherited from GenericConfigWin


#   def add_notebook_tab():     # Inherited from GenericConfigWin


    def setup_button_strip(self):

        """Called by self.setup().

        Creates a strip of buttons at the bottom of the window. Any changes the
        user has made are applied by clicking the 'OK' or 'Apply' buttons, and
        cancelled by using the 'Reset' or 'Cancel' buttons.

        The window is closed by using the 'OK' and 'Cancel' buttons.

        If self.multi_button_flag is True, only the 'OK' button is created.
        """

        hbox = Gtk.HBox()
        self.grid.attach(hbox, 0, 2, 1, 1)

        if self.multi_button_flag:

            # 'Reset' button
            self.reset_button = Gtk.Button(_('Reset'))
            hbox.pack_start(self.reset_button, False, False, self.spacing_size)
            self.reset_button.get_child().set_width_chars(10)
            self.reset_button.set_tooltip_text(
                _('Reset changes without closing the window'),
            );
            self.reset_button.connect('clicked', self.on_button_reset_clicked)

            # 'Apply' button
            self.apply_button = Gtk.Button(_('Apply'))
            hbox.pack_start(self.apply_button, False, False, self.spacing_size)
            self.apply_button.get_child().set_width_chars(10)
            self.apply_button.set_tooltip_text(
                _('Apply changes without closing the window'),
            );
            self.apply_button.connect('clicked', self.on_button_apply_clicked)

        # 'OK' button
        self.ok_button = Gtk.Button(_('OK'))
        hbox.pack_end(self.ok_button, False, False, self.spacing_size)
        self.ok_button.get_child().set_width_chars(10)
        self.ok_button.set_tooltip_text(_('Apply changes'));
        self.ok_button.connect('clicked', self.on_button_ok_clicked)

        if self.multi_button_flag:

            # 'Cancel' button
            self.cancel_button = Gtk.Button(_('Cancel'))
            hbox.pack_end(self.cancel_button, False, False, self.spacing_size)
            self.cancel_button.get_child().set_width_chars(10)
            self.cancel_button.set_tooltip_text(_('Cancel changes'));
            self.cancel_button.connect(
                'clicked',
                self.on_button_cancel_clicked,
            )


#   def setup_gap():            # Inherited from GenericConfigWin


    # (Non-widget functions)


    def apply_changes(self):

        """Called by self.on_button_ok_clicked() and
        self.on_button_apply_clicked().

        Any changes the user has made are temporarily stored in self.edit_dict.
        Apply to those changes to the object being edited.
        """

        # Apply any changes the user has made
        for key in self.edit_dict.keys():
            setattr(self.edit_obj, key, self.edit_dict[key])

        # The changes can now be cleared
        self.edit_dict = {}


    def reset_with_new_edit_obj(self, new_edit_obj):

        """Can be called by anything.

        Resets the object whose values are being edited in this window, i.e.
        self.edit_obj, to the specified object.

        Then redraws the window itself, as if the user had clicked the 'Reset'
        button at the bottom of the window. This makes new_edit_obj's IVs
        visible in the edit window, without the need to destroy the old one and
        replace it with a new one.

        Args:

            new_edit_obj (class): The replacement edit object

        """

        self.edit_obj = new_edit_obj

        # The rest of this function is copied from
        #   self.on_button_reset_clicked()

        # Remove all existing tabs from the notebook
        number = self.notebook.get_n_pages()
        if number:

            for count in range(0, number):
                self.notebook.remove_page(0)

        # Empty self.edit_dict, destroying any changes the user has made
        self.edit_dict = {}

        # Re-draw all the tabs
        self.setup_tabs()

        # Render the changes
        self.show_all()


    def retrieve_val(self, name):

        """Can be called by anything.

        Any changes the user has made are temporarily stored in self.edit_dict.

        Each key corresponds to an attribute in the object being edited,
        self.edit_obj.

        If 'name' exists as a key in that dictionary, retrieve the
        corresponding value and return it. Otherwise, the user hasn't yet
        modified the value, so retrieve directly from the attribute in the
        object being edited.

        Args:

            name (str): The name of the attribute in the object being edited

        Returns:

            The original or modified value of that attribute.

        """

        if name in self.edit_dict:
            return self.edit_dict[name]
        else:
            attrib = getattr(self.edit_obj, name)
            if type(attrib) is list or type(attrib) is dict:
                return attrib.copy()
            else:
                return attrib


    # (Add widgets)


    def add_checkbutton(self, grid, text, prop, x, y, wid, hei):

        """Called by various functions in the child edit window.

        Adds a Gtk.CheckButton to the tab's Gtk.Grid.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            text (string or None): The text to display in the checkbutton's
                label. No label is used if 'text' is an empty string or None

            prop (string or None): The name of the attribute in self.edit_obj
                whose value will be set to the contents of this widget. If
                None, no changes are made to self.edit_dict; it's up to the
                calling function to provide a .connect()

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The checkbutton widget created

        """

        checkbutton = Gtk.CheckButton()
        grid.attach(checkbutton, x, y, wid, hei)
        checkbutton.set_hexpand(True)
        if text is not None and text != '':
            checkbutton.set_label(text)

        if prop is not None:
            checkbutton.set_active(self.retrieve_val(prop))
            checkbutton.connect('toggled', self.on_checkbutton_toggled, prop)

        return checkbutton


    def add_combo(self, grid, combo_list, prop, x, y, wid, hei):

        """Called by various functions in the child edit window.

        Adds a simple Gtk.ComboBox to the tab's Gtk.Grid.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            combo_list (list): A list of values to display in the combobox.
                This function expects a simple, one-dimensional list. For
                something more complex, see self.add_combo_with_data()

            prop (string or None): The name of the attribute in self.edit_obj
                whose value will be set to the contents of this widget. If
                None, no changes are made to self.edit_dict; it's up to the
                calling function to provide a .connect()

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The combobox widget created

        """

        store = Gtk.ListStore(str)
        for string in combo_list:
            store.append( [str(string)] )

        combo = Gtk.ComboBox.new_with_model(store)
        grid.attach(combo, x, y, wid, hei)
        renderer_text = Gtk.CellRendererText()
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, 'text', 0)
        combo.set_entry_text_column(0)

        if prop is not None:
            val = self.retrieve_val(prop)
            index = combo_list.index(val)
            combo.set_active(index)

            combo.connect('changed', self.on_combo_changed, prop)

        return combo


    def add_combo_with_data(self, grid, combo_list, prop, x, y, wid, hei):

        """Called by various functions in the child edit window.

        Adds a more complex Gtk.ComboBox to the tab's Gtk.Grid. This function
        expects a list of values in the form

            [ [val1, val2], [val1, val2], ... ]

        The combobox displays the 'val1' values. If one of them is selected,
        the corresponding 'val2' is used to set the attribute described by
        'prop'.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            combo_list (list): The list described above. For something more
                simple, see self.add_combo()

            prop (string or None): The name of the attribute in self.edit_obj
                whose value will be set to the contents of this widget. If
                None, no changes are made to self.edit_dict; it's up to the
                calling function to provide a .connect()

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The combobox widget created

        """

        store = Gtk.ListStore(str, str)

        index_list = []
        for mini_list in combo_list:
            store.append( [ str(mini_list[0]), str(mini_list[1]) ] )
            index_list.append(mini_list[1])

        combo = Gtk.ComboBox.new_with_model(store)
        grid.attach(combo, x, y, wid, hei)
        renderer_text = Gtk.CellRendererText()
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, 'text', 0)
        combo.set_entry_text_column(0)

        if prop is not None:
            val = self.retrieve_val(prop)
            index = index_list.index(val)
            combo.set_active(index)

            combo.connect('changed', self.on_combo_with_data_changed, prop)

        return combo


    def add_entry(self, grid, prop, x, y, wid, hei):

        """Called by various functions in the child edit window.

        Adds a Gtk.Entry to the tab's Gtk.Grid.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            prop (string or None): The name of the attribute in self.edit_obj
                whose value will be set to the contents of this widget. If
                None, no changes are made to self.edit_dict; it's up to the
                calling function to provide a .connect()

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The entry widget created

        """

        entry = Gtk.Entry()
        grid.attach(entry, x, y, wid, hei)
        entry.set_hexpand(True)

        if prop is not None:
            value = self.retrieve_val(prop)
            if value is not None:
                entry.set_text(str(value))

            entry.connect('changed', self.on_entry_changed, prop)

        return entry


#   def add_image               # Inherited from GenericConfigWin


    def add_label(self, grid, text, x, y, wid, hei):

        """Called by various functions in the child edit window.

        Adds a Gtk.Label to the tab's Gtk.Grid.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            text (str): Pango markup displayed in the label

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The label widget created

        """

        label = Gtk.Label()
        grid.attach(label, x, y, wid, hei)
        label.set_markup(text)
        label.set_hexpand(True)
        label.set_alignment(0, 0.5)

        return label


    def add_pixbuf(self, grid, pixbuf_name, x, y, wid, hei):

        """Called by various functions in the child edit window.

        Adds a Gtk.Image to the tab's Gtk.Grid. A modified version of
        self.add_image(), which is called with a path to an image file; this
        function is called with one of the pixbuf names specified by
        mainwin.MainWin.pixbuf_dict, e.g. 'video_both_large'.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            pixbuf_name (str): One of the keys in
                mainwin.MainWin.pixbuf_dict, e.g. 'video_both_large'.

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The Gtk.Frame containing the image

        """

        frame = Gtk.Frame()
        grid.attach(frame, x, y, wid, hei)

        image = Gtk.Image()
        frame.add(image)

        main_win_obj = self.app_obj.main_win_obj
        if pixbuf_name in main_win_obj.pixbuf_dict:
            image.set_from_pixbuf(main_win_obj.pixbuf_dict[pixbuf_name])
        else:
            # Unrecognised pixbuf name
            image.set_from_pixbuf(
                main_win_obj.pixbuf_dict['question_large'],
            )

        return frame


    def add_radiobutton(self, grid, prev_button, text, prop, value, x, y, \
    wid, hei):

        """Called by various functions in the child edit window.

        Adds a Gtk.RadioButton to the tab's Gtk.Grid.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            prev_button (Gtk.RadioButton or None): When this is the first
                radio button in the group, None. Otherwise, the previous
                radio button in the group. Use of this argument links the radio
                buttons together, ensuring that only one of them can be active
                at any time

            text (string or None): The text to display in the radiobutton's
                label. No label is used if 'text' is an empty string or None

            prop (string or None): The name of the attribute in self.edit_obj
                whose value will be set to the contents of this widget. If
                None, no changes are made to self.edit_dict; it's up to the
                calling function to provide a .connect()

            value (any): When this radiobutton becomes the active one, and if
                'prop' is not None, then 'prop' and 'value' are added as a new
                key-value pair to self.edit_dict

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The radiobutton widget created

        """

        radiobutton = Gtk.RadioButton.new_from_widget(prev_button)
        grid.attach(radiobutton, x, y, wid, hei)
        radiobutton.set_hexpand(True)
        if text is not None and text != '':
            radiobutton.set_label(text)

        if prop is not None:
            if value is not None and self.retrieve_val(prop) == value:
                radiobutton.set_active(True)

            radiobutton.connect(
                'toggled',
                self.on_radiobutton_toggled, prop, value,
            )

        return radiobutton


    def add_spinbutton(self, grid, min_val, max_val, step, prop, x, y, wid, \
    hei):

        """Called by various functions in the child edit window.

        Adds a Gtk.SpinButton to the tab's Gtk.Grid.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            min_val (int): The minimum permitted in the spinbutton

            max_val (int or None): The maximum values permitted in the
                spinbutton. If None, this function assigns a very large maximum
                value (a billion)

            step (int): Clicking the up/down arrows in the spin button
                increments/decrements the value by this much

            prop (string or None): The name of the attribute in self.edit_obj
                whose value will be set to the contents of this widget. If
                None, no changes are made to self.edit_dict; it's up to the
                calling function to provide a .connect()

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The spinbutton widget created

        """

        # If the specified value of 'max_valu' was none, just use a very big
        #   number (as Gtk.SpinButton won't accept the None argument)
        if max_val is None:
            max_val = 1000000000

        spinbutton = Gtk.SpinButton.new_with_range(min_val, max_val, step)
        grid.attach(spinbutton, x, y, wid, hei)
        spinbutton.set_hexpand(False)

        if prop is not None:
            spinbutton.set_value(self.retrieve_val(prop))
            spinbutton.connect(
                'value-changed',
                self.on_spinbutton_changed,
                prop,
            )

        return spinbutton


    def add_textview(self, grid, prop, x, y, wid, hei):

        """Called by various functions in the child edit window.

        Adds a Gtk.TextView to the tab's Gtk.Grid. The contents of the textview
        are used as a single string (perhaps including newline characters) to
        set the value of a string attribute.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            prop (string or None): The name of the attribute in self.edit_obj
                whose value will be set to the contents of this widget. The
                attribute can be an integer, string, list or tuple. If None, no
                changes are made to self.edit_dict; it's up to the calling
                function to provide a .connect()

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The textview and textbuffer widgets created

        """

        frame = Gtk.Frame()
        grid.attach(frame, x, y, wid, hei)

        scrolled = Gtk.ScrolledWindow()
        frame.add(scrolled)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)

        textview = Gtk.TextView()
        scrolled.add(textview)

        textbuffer = textview.get_buffer()

        if prop is not None:
            value = self.retrieve_val(prop)
            if value is not None:
                if type(value) is list or type(value) is tuple:
                    textbuffer.set_text(str.join('\n', value))
                else:
                    textbuffer.set_text(str(value))

            textbuffer.connect('changed', self.on_textview_changed, prop)

        return textview, textbuffer


#   def add_treeview            # Inherited from GenericConfigWin


    # Callback class methods


    def on_button_apply_clicked(self, button):

        """Called from a callback in self.setup_button_strip().

        Applies any changes made by the user and re-draws the window's tabs,
        showing their new values.

        Args:

            button (Gtk.Button): The widget clicked

        """

        # Apply any changes the user has made
        self.apply_changes()

        # Remove all existing tabs from the notebook
        number = self.notebook.get_n_pages()
        if number:

            for count in range(0, number):
                self.notebook.remove_page(0)

        # Re-draw all the tabs
        self.setup_tabs()

        # Render the changes
        self.show_all()


    def on_button_cancel_clicked(self, button):

        """Called from a callback in self.setup_button_strip().

        Destroys any changes made by the user and re-draws the window's tabs,
        showing their original values.

        Args:

            button (Gtk.Button): The widget clicked

        """

        # Destroy the window
        self.destroy()


    def on_button_ok_clicked(self, button):

        """Called from a callback in self.setup_button_strip().

        Destroys any changes made by the user and then closes the window.

        Args:

            button (Gtk.Button): The widget clicked

        """

        # Apply any changes the user has made
        self.apply_changes()

        # Destroy the window
        self.destroy()


    def on_button_reset_clicked(self, button):

        """Called from a callback in self.setup_button_strip().

        Destroys any changes made by the user and re-draws the window's tabs,
        showing their original values.

        Args:

            button (Gtk.Button): The widget clicked

        """

        # Remove all existing tabs from the notebook
        number = self.notebook.get_n_pages()
        if number:

            for count in range(0, number):
                self.notebook.remove_page(0)

        # Empty self.edit_dict, destroying any changes the user has made
        self.edit_dict = {}

        # Re-draw all the tabs
        self.setup_tabs()

        # Render the changes
        self.show_all()


    def on_checkbutton_toggled(self, checkbutton, prop):

        """Called from a callback in self.add_checkbutton().

        Adds a key-value pair to self.edit_dict, using True if the button is
        selected, False if not.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            prop (str): The attribute in self.edit_obj to modify

        """

        if not checkbutton.get_active():
            self.edit_dict[prop] = False
        else:
            self.edit_dict[prop] = True


    def on_combo_changed(self, combo, prop):

        """Called from a callback in self.add_combo().

        Temporarily stores the contents of the widget in self.edit_dict.

        Args:

            combo (Gtk.ComboBox): The widget clicked

            prop (str): The attribute in self.edit_obj to modify

        """

        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        self.edit_dict[prop] = model[tree_iter][0]


    def on_combo_with_data_changed(self, combo, prop):

        """Called from a callback in self.add_combo_with_data().

        Extracts the value visible in the widget, converts it into another
        value, and stores the later in self.edit_dict.

        Args:

            combo (Gtk.ComboBox): The widget clicked

            prop (str): The attribute in self.edit_obj to modify

        """

        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        self.edit_dict[prop] = model[tree_iter][1]


    def on_entry_changed(self, entry, prop):

        """Called from a callback in self.add_entry().

        Temporarily stores the contents of the widget in self.edit_dict.

        Args:

            entry (Gtk.Entry): The widget clicked

            prop (str): The attribute in self.edit_obj to modify

        """

        self.edit_dict[prop] = entry.get_text()


    def on_radiobutton_toggled(self, checkbutton, prop, value):

        """Called from a callback in self.add_radiobutton().

        Adds a key-value pair to self.edit_dict, but only if this radiobutton
        (from those in the group) is the selected one.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            prop (str): The attribute in self.edit_obj to modify

            value (-): The attribute's new value

        """

        if radiobutton.get_active():
            self.edit_dict[prop] = value


    def on_spinbutton_changed(self, spinbutton, prop):

        """Called from a callback in self.add_spinbutton().

        Temporarily stores the contents of the widget in self.edit_dict.

        Args:

            spinbutton (Gtk.SpinkButton): The widget clicked

            prop (str): The attribute in self.edit_obj to modify

        """

        self.edit_dict[prop] = int(spinbutton.get_value())


    def on_textview_changed(self, textbuffer, prop):

        """Called from a callback in self.add_textview().

        Temporarily stores the contents of the widget in self.edit_dict.

        Args:

            textbuffer (Gtk.TextBuffer): The widget modified

            prop (str): The attribute in self.edit_obj to modify

        """

        text = textbuffer.get_text(
            textbuffer.get_start_iter(),
            textbuffer.get_end_iter(),
            # Don't include hidden characters
            False,
        )

        old_value = self.retrieve_val(prop)

        if type(old_value) is list:
            self.edit_dict[prop] = text.split()
        elif type(old_value) is tuple:
            self.edit_dict[prop] = text.split()
        else:
             self.edit_dict[prop] = text


    # (Shared support functions)


    def add_container_properties(self, grid):

        """Called by VideoEditWin.setup_general_tab(),
        ChannelPlaylistEditWin.setup_general_tab() and
        FolderEditWin.setup_general_tab().

        Adds widgets common to those edit windows.

        Args:

            grid (Gtk.Grid): The grid on which widgets are arranged in their
                tab

        """

        entry = self.add_entry(grid,
            None,
            0, 1, 1, 1,
        )
        entry.set_text('#' + str(self.edit_obj.dbid))
        entry.set_editable(False)
        entry.set_hexpand(False)
        entry.set_width_chars(8)

        main_win_obj = self.app_obj.main_win_obj
        if isinstance(self.edit_obj, media.Video):
            icon_path = main_win_obj.icon_dict['video_small']
        elif isinstance(self.edit_obj, media.Channel):
            icon_path = main_win_obj.icon_dict['channel_small']
        elif isinstance(self.edit_obj, media.Playlist):
            icon_path = main_win_obj.icon_dict['playlist_small']
        else:

            if self.edit_obj.priv_flag:
                icon_path = main_win_obj.icon_dict['folder_red_small']
            elif self.edit_obj.temp_flag:
                icon_path = main_win_obj.icon_dict['folder_blue_small']
            elif self.edit_obj.fixed_flag:
                icon_path = main_win_obj.icon_dict['folder_green_small']
            else:
                icon_path = main_win_obj.icon_dict['folder_small']

        frame = self.add_image(grid,
            icon_path,
            1, 1, 1, 1,
        )
        # (The frame looks cramped without this. The icon itself is 16x16)
        frame.set_size_request(
            16 + (self.spacing_size * 2),
            -1,
        )

        entry2 = self.add_entry(grid,
            'name',
            2, 1, 1, 1,
        )
        entry2.set_editable(False)

        label = self.add_label(grid,
            _('Listed as'),
            0, 2, 1, 1,
        )
        label.set_hexpand(False)

        entry3 = self.add_entry(grid,
            'nickname',
            2, 2, 1, 1,
        )
        entry3.set_editable(False)

        label2 = self.add_label(grid,
            _('Contained in'),
            0, 3, 1, 1,
        )
        label2.set_hexpand(False)

        parent_obj = self.edit_obj.parent_obj
        if parent_obj:
            if isinstance(parent_obj, media.Channel):
                icon_path2 = main_win_obj.icon_dict['channel_small']
            elif isinstance(parent_obj, media.Playlist):
                icon_path2 = main_win_obj.icon_dict['playlist_small']
            else:

                if parent_obj.priv_flag:
                    icon_path2 = main_win_obj.icon_dict['folder_red_small']
                elif parent_obj.temp_flag:
                    icon_path2 = main_win_obj.icon_dict['folder_blue_small']
                elif parent_obj.fixed_flag:
                    icon_path2 = main_win_obj.icon_dict['folder_green_small']
                else:
                    icon_path2 = main_win_obj.icon_dict['folder_small']

        else:
            icon_path2 = main_win_obj.icon_dict['folder_black_small']

        frame2 = self.add_image(grid,
            icon_path2,
            1, 3, 1, 1,
        )
        frame2.set_size_request(
            16 + (self.spacing_size * 2),
            -1,
        )

        entry4 = self.add_entry(grid,
            None,
            2, 3, 1, 1,
        )
        entry4.set_editable(False)
        if parent_obj:
            entry4.set_text(parent_obj.name)


    def add_destination_properties(self, grid):

        """Called by ChannelPlaylistEditWin.setup_general_tab() and
        FolderEditWin.setup_general_tab().

        Adds widgets common to those edit windows.

        Args:

            grid (Gtk.Grid): The grid on which widgets are arranged in their
                tab

        """

        label = self.add_label(grid,
            _('Download to'),
            0, 5, 1, 1,
        )
        label.set_hexpand(False)

        main_win_obj = self.app_obj.main_win_obj
        dest_obj = self.app_obj.media_reg_dict[self.edit_obj.master_dbid]
        if isinstance(dest_obj, media.Channel):
            icon_path = main_win_obj.icon_dict['channel_small']
        elif isinstance(dest_obj, media.Playlist):
            icon_path = main_win_obj.icon_dict['playlist_small']
        else:

            if dest_obj.priv_flag:
                icon_path = main_win_obj.icon_dict['folder_red_small']
            elif dest_obj.temp_flag:
                icon_path = main_win_obj.icon_dict['folder_blue_small']
            elif dest_obj.fixed_flag:
                icon_path = main_win_obj.icon_dict['folder_green_small']
            else:
                icon_path = main_win_obj.icon_dict['folder_small']

        frame = self.add_image(grid,
            icon_path,
            1, 5, 1, 1,
        )
        frame.set_size_request(
            16 + (self.spacing_size * 2),
            -1,
        )

        entry = self.add_entry(grid,
            None,
            2, 5, 1, 1,
        )
        entry.set_editable(False)
        entry.set_text(dest_obj.name)

        label2 = self.add_label(grid,
            _('Location'),
            0, 6, 1, 1,
        )
        label2.set_hexpand(False)

        entry2 = self.add_entry(grid,
            None,
            2, 6, 1, 1,
        )
        entry2.set_editable(False)
        entry2.set_text(self.edit_obj.get_default_dir(self.app_obj))


    def add_source_properties(self, grid):

        """Called by VideoEditWin.setup_general_tab() and
        ChannelPlaylistEditWin.setup_general_tab().

        Adds widgets common to those edit windows.

        Args:

            grid (Gtk.Grid): The grid on which widgets are arranged in their
                tab

        """

        media_type = self.edit_obj.get_type()
        if media_type == 'channel':
            string = _('Channel URL')
        elif media_type == 'playlist':
            string = _('Playlist URL')
        else:
            string = _('Video URL')

        label = self.add_label(grid,
            string,
            0, 4, 1, 1,
        )
        label.set_hexpand(False)

        entry = self.add_entry(grid,
            'source',
            2, 4, 1, 1,
        )
        entry.set_editable(False)


    def setup_download_options_tab(self):

        """Called by VideoEditWin.setup_tabs(),
        ChannelPlaylistEditWin.setup_tabs() and FolderEditWin.setup_tabs().

        Sets up the 'Download options' tab.
        """

        tab, grid = self.add_notebook_tab(_('Download _options'))

        # Download options
        self.add_label(grid,
            '<u>' + _('Download options') + '</u>',
            0, 0, 2, 1,
        )

        self.apply_options_button = Gtk.Button(_('Apply download options'))
        grid.attach(self.apply_options_button, 0, 1, 1, 1)
        self.apply_options_button.connect(
            'clicked',
            self.on_button_apply_options_clicked,
        )

        self.edit_button = Gtk.Button(_('Edit download options'))
        grid.attach(self.edit_button, 1, 1, 1, 1)
        self.edit_button.connect(
            'clicked',
            self.on_button_edit_options_clicked,
        )

        self.remove_button = Gtk.Button(_('Remove download options'))
        grid.attach(self.remove_button, 1, 2, 1, 1)
        self.remove_button.connect(
            'clicked',
            self.on_button_remove_options_clicked,
        )

        if self.edit_obj.options_obj:
            self.apply_options_button.set_sensitive(False)
        else:
            self.edit_button.set_sensitive(False)
            self.remove_button.set_sensitive(False)


    # (Shared callbacks)


    def on_button_apply_options_clicked(self, button):

        """Called from callback in self.setup_download_options_tab().

        Apply download options to the media data object.

        Args:

            button (Gtk.Button): The widget clicked

        """

        if self.edit_obj.options_obj:
            return self.app_obj.system_error(
                401,
                'Download options already applied',
            )

        # Apply download options to the media data object
        self.app_obj.apply_download_options(self.edit_obj)
        # (De)sensitise buttons appropriately
        self.apply_options_button.set_sensitive(False)
        self.edit_options_button.set_sensitive(True)
        self.remove_options_button.set_sensitive(True)


    def on_button_edit_options_clicked(self, button):

        """Called from callback in self.setup_download_options_tab().

        Edit download options for the media data object.

        Args:

            button (Gtk.Button): The widget clicked

        """

        if not self.edit_obj.options_obj:
            return self.app_obj.system_error(
                402,
                'Download options not already applied',
            )

        # Open an edit window to show the options immediately
        OptionsEditWin(
            self.app_obj,
            self.edit_obj.options_obj,
        )


    def on_button_remove_options_clicked(self, button):

        """Called from callback in self.setup_download_options_tab().

        Remove download options from the media data object.

        Args:

            button (Gtk.Button): The widget clicked

        """

        if not self.edit_obj.options_obj:
            return self.app_obj.system_error(
                403,
                'Download options not already applied',
            )

        # Remove download options from the media data object
        self.app_obj.remove_download_options(self.edit_obj)
        # (De)sensitise buttons appropriately
        self.apply_options_button.set_sensitive(True)
        self.edit_options_button.set_sensitive(False)
        self.remove_options_button.set_sensitive(False)


class GenericPrefWin(GenericConfigWin):

    """Generic Python class for windows in which the user can modify various
    system settings.

    Any modifications are applied immediately (unlike in an 'edit window', in
    which the modifications are stored temporarily, and only applied once the
    user has finished making changes).
    """


    # Standard class methods


#   def __init__():             # Provided by child object


    # Public class methods


    def is_duplicate(self, app_obj):

        """Called by self.__init__.

        Don't open this preference window, if another preference window of the
        same class is already open.

        Args:

            app_obj (mainapp.TartubeApp): The main application object

        Return values:

            True if a duplicate is found, False if not

        """

        for config_win_obj in app_obj.main_win_obj.config_win_list:

            if type(self) == type(config_win_obj):

                # Duplicate found
                config_win_obj.present()
                return True

        # Not a duplicate
        return False


#   def setup():                # Inherited from GenericConfigWin


#   def setup_grid():           # Inherited from GenericConfigWin


#   def setup_notebook():       # Inherited from GenericConfigWin


#   def add_notebook_tab():     # Inherited from GenericConfigWin


    def setup_button_strip(self):

        """Called by self.setup().

        Creates a strip of buttons at the bottom of the window. For preference
        windows, there is only a single 'OK' button, which closes the window.
        """

        hbox = Gtk.HBox()
        self.grid.attach(hbox, 0, 2, 1, 1)

        # 'OK' button
        self.ok_button = Gtk.Button(_('OK'))
        hbox.pack_end(self.ok_button, False, False, self.spacing_size)
        self.ok_button.get_child().set_width_chars(10)
        self.ok_button.set_tooltip_text(_('Close this window'));
        self.ok_button.connect('clicked', self.on_button_ok_clicked)


#   def setup_gap():            # Inherited from GenericConfigWin


    # (Non-widget functions)


    def reset_window(self):

        """Can be called by anything.

        Redraws the window, without the need to destroy the old one and replace
        it with a new one.
        """

        # This code is copied from
        #   config.GenericEditWin.on_button_reset_clicked()

        # Remove all existing tabs from the notebook
        number = self.notebook.get_n_pages()
        if number:

            for count in range(0, number):
                self.notebook.remove_page(0)

        # Re-draw all the tabs
        self.setup_tabs()

        # Render the changes
        self.show_all()


    # (Add widgets)


    def add_checkbutton(self, grid, text, set_flag, mod_flag, x, y, wid, hei):

        """Called by various functions in the child preference window.

        Adds a Gtk.CheckButton to the tab's Gtk.Grid.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            text (string or None): The text to display in the checkbutton's
                label. No label is used if 'text' is an empty string or None

            set_flag (bool): True if the checkbutton is selected

            mod_flag (bool): True if the checkbutton can be toggled by the user

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The checkbutton widget created

        """

        checkbutton = Gtk.CheckButton()
        grid.attach(checkbutton, x, y, wid, hei)
        checkbutton.set_active(set_flag)
        checkbutton.set_sensitive(mod_flag)
        checkbutton.set_hexpand(True)
        if text is not None and text != '':
            checkbutton.set_label(text)

        return checkbutton


    def add_combo(self, grid, combo_list, active_val, x, y, wid, hei):

        """Called by various functions in the child preference window.

        Adds a simple Gtk.ComboBox to the tab's Gtk.Grid.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            combo_list (list): A list of values to display in the combobox.
                This function expects a simple, one-dimensional list

            active_val (string or None): If not None, a value matching one of
                the items in combo_list, that should be the active row in the
                combobox

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The combobox widget created

        """

        store = Gtk.ListStore(str)

        count = -1
        active_index = 0
        for string in combo_list:
            store.append( [string] )

            count += 1
            if active_val is not None and active_val == string:
                active_index = count

        combo = Gtk.ComboBox.new_with_model(store)
        grid.attach(combo, x, y, wid, hei)
        renderer_text = Gtk.CellRendererText()
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, 'text', 0)
        combo.set_entry_text_column(0)
        combo.set_active(active_index)

        return combo


    def add_combo_with_data(self, grid, combo_list, active_val, x, y, wid,
    hei):

        """Called by various functions in the child preference window.

        Adds a more complex Gtk.ComboBox to the tab's Gtk.Grid. This function
        expects a list of values in the form

            [ [val1, val2], [val1, val2], ... ]

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            combo_list (list): The list described above. For something more
                simple, see self.add_combo()

            active_val (string or None): If not None, a value matching a
                the second item ('val2') in one of the combo_list pairs; the
                specified pair is the active row in the combobox

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The combobox widget created

        """

        store = Gtk.ListStore(str, str)

        count = -1
        active_index = 0
        for mini_list in combo_list:
            store.append( [ str(mini_list[0]), str(mini_list[1]) ] )

            count += 1
            if active_val is not None and active_val == mini_list[1]:
                active_index = count

        combo = Gtk.ComboBox.new_with_model(store)
        grid.attach(combo, x, y, wid, hei)
        renderer_text = Gtk.CellRendererText()
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, 'text', 0)
        combo.set_entry_text_column(0)
        combo.set_active(active_index)

        return combo


    def add_entry(self, grid, text, edit_flag, x, y, wid, hei):

        """Called by various functions in the child preference window.

        Adds a Gtk.Entry to the tab's Gtk.Grid.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            text (string or None): The initial contents of the entry.

            edit_flag (bool): True if the contents of the entry can be edited

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The entry widget created

        """

        entry = Gtk.Entry()
        grid.attach(entry, x, y, wid, hei)
        entry.set_hexpand(True)

        if text is not None:
            entry.set_text(str(text))

        if not edit_flag:
            entry.set_editable(False)

        return entry


#   def add_image               # Inherited from GenericConfigWin


    def add_label(self, grid, text, x, y, wid, hei):

        """Called by various functions in the child preference window.

        Adds a Gtk.Label to the tab's Gtk.Grid.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            text (str): Pango markup displayed in the label

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The label widget created

        """

        label = Gtk.Label()
        grid.attach(label, x, y, wid, hei)
        label.set_markup(text)
        label.set_hexpand(True)
        label.set_alignment(0, 0.5)

        return label


    def add_radiobutton(self, grid, prev_button, text, x, y, wid, hei):

        """Called by various functions in the child preference window.

        Adds a Gtk.RadioButton to the tab's Gtk.Grid.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            prev_button (Gtk.RadioButton or None): When this is the first
                radio button in the group, None. Otherwise, the previous
                radio button in the group. Use of this argument links the radio
                buttons together, ensuring that only one of them can be active
                at any time

            text (string or None): The text to display in the radiobutton's
                label. No label is used if 'text' is an empty string or None

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The radiobutton widget created

        """

        radiobutton = Gtk.RadioButton.new_from_widget(prev_button)
        grid.attach(radiobutton, x, y, wid, hei)
        radiobutton.set_hexpand(True)
        if text is not None and text != '':
            radiobutton.set_label(text)

        return radiobutton


    def add_spinbutton(self, grid, min_val, max_val, step, val, x, y, wid, \
    hei):

        """Called by various functions in the child preference window.

        Adds a Gtk.SpinButton to the tab's Gtk.Grid.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            min_val (int): The minimum permitted in the spinbutton

            max_val (int or None): The maximum values permitted in the
                spinbutton. If None, this function assigns a very large maximum
                value (a billion)

            step (int): Clicking the up/down arrows in the spin button
                increments/decrements the value by this much

            val (int): The current value of the spinbutton

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The spinbutton widget created

        """

        # If the specified value of 'max_valu' was none, just use a very big
        #   number (as Gtk.SpinButton won't accept the None argument)
        if max_val is None:
            max_val = 1000000000

        spinbutton = Gtk.SpinButton.new_with_range(min_val, max_val, step)
        grid.attach(spinbutton, x, y, wid, hei)
        spinbutton.set_value(val)
        spinbutton.set_hexpand(False)

        return spinbutton


    def add_textview(self, grid, contents_list, x, y, wid, hei):

        """Called by various functions in the child preference window.

        Adds a Gtk.TextView to the tab's Gtk.Grid.

        Args:

            grid (Gtk.Grid): The grid on which this widget will be placed

            contents_list (list): The initial contents of the textview. Each
                item in the list is a line in the textview.

            x, y, wid, hei (int): Position on the grid at which the widget is
                placed

        Returns:

            The textview and textbuffer widgets created

        """

        frame = Gtk.Frame()
        grid.attach(frame, x, y, wid, hei)

        scrolled = Gtk.ScrolledWindow()
        frame.add(scrolled)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)

        textview = Gtk.TextView()
        scrolled.add(textview)

        textbuffer = textview.get_buffer()

        if contents_list:
            textbuffer.set_text(str.join('\n', contents_list))

        return textview, textbuffer


#   def add_treeview            # Inherited from GenericConfigWin


    # Callback class methods


    def on_button_ok_clicked(self, button):

        """Called from a callback in self.setup_button_strip().

        Closes the window.

        Args:

            button (Gtk.Button): The button clicked

        """

        # Destroy the window
        self.destroy()


class OptionsEditWin(GenericEditWin):

    """Python class for an 'edit window' to modify values in an
    options.OptionsManager object.

    Args:

        app_obj (mainapp.TartubeApp): The main application object

        edit_obj (options.OptionsManager): The object whose attributes will be
            edited in this window

    """


    # Standard class methods


    def __init__(self, app_obj, edit_obj):

        Gtk.Window.__init__(self, title=_('Download options'))

        if self.is_duplicate(app_obj, edit_obj):
            return

        # IV list - class objects
        # -----------------------
        # The mainapp.TartubeApp object
        self.app_obj = app_obj
        # The options.OptionManager object being edited
        self.edit_obj = edit_obj
        # The media data object which is the parent of the options manager
        #   object (None, if the object isn't attached to a media data object;
        #   set below)
        self.media_data_obj = None


        # IV list - Gtk widgets
        # ---------------------
        self.grid = None                        # Gtk.Grid
        self.notebook = None                    # Gtk.Notebook
        self.reset_button = None                # Gtk.Button
        self.apply_button = None                # Gtk.Button
        self.ok_button = None                   # Gtk.Button
        self.cancel_button = None               # Gtk.Button
        # The 'embed_subs' option appears in two different places
        self.embed_checkbutton = None           # Gtk.CheckButton
        self.embed_checkbutton2 = None          # Gtk.CheckButton
        # The Gtk.ListStore containing the user's preferred video/audio formats
        #   (which must be redrawn when self.apply_changes() is called)
        self.formats_liststore = None           # Gtk.ListStore

        # IV list - other
        # ---------------
        # Size (in pixels) of gaps between edit window widgets
        self.spacing_size = self.app_obj.default_spacing_size
        # Flag set to True if all four buttons ('Reset', 'Apply', 'Cancel' and
        #   'OK') are required, or False if just the 'OK' button is required
        self.multi_button_flag = True

        # When the user changes a value, it is not applied to self.edit_obj
        #   immediately; instead, it is stored temporarily in this dictionary
        # If the user clicks the 'OK' or 'Apply' buttons at the bottom of the
        #   window, the changes are applied to self.edit_obj
        # If the user clicks the 'Reset' or 'Cancel' buttons, the dictionary
        #   is emptied and the changes are lost
        # In this edit window, the key-value pairs directly correspond to those
        #   in options.OptionsManager.options_dict, rather than corresponding
        #   directly to attributes in the options.OptionsManager object
        # Because of that, we use our own .apply_changes() and .retrieve_val()
        #   functions, rather than relying on the generic functions
        # Key-value pairs are added to this dictionary whenever the user
        #   makes a change (so if no changes are made when the window is
        #   closed, the dictionary will still be empty)
        self.edit_dict = {}

        # IVs used to keep track of widget changes in the 'Files' tab
        # Flag set to to False when that tab's output template widgets are
        #   desensitised, True when sensitised
        self.template_flag = False
        # A list of Gtk widgets to (de)sensitise in when the flag changes
        self.template_widget_list = []

        # Code
        # ----

        # Set the parent media data object, if any
        if edit_obj.dbid is not None \
        and edit_obj.dbid in self.app_obj.media_reg_dict:
            self.media_data_obj = self.app_obj.media_reg_dict[edit_obj.dbid]

        # Set up the edit window
        self.setup()


    # Public class methods


#   def is_duplicate():         # Inherited from GenericConfigWin


#   def setup():                # Inherited from GenericConfigWin


#   def setup_grid():           # Inherited from GenericConfigWin


#   def setup_notebook():       # Inherited from GenericConfigWin


#   def add_notebook_tab():     # Inherited from GenericConfigWin


#   def setup_button_strip():   # Inherited from GenericEditWin


#   def setup_gap():            # Inherited from GenericConfigWin


    # (Non-widget functions)


    def apply_changes(self):

        """Called by self.on_button_ok_clicked() and
        self.on_button_apply_clicked().

        Any changes the user has made are temporarily stored in self.edit_dict.
        Apply to those changes to the object being edited.

        In this edit window we apply changes to self.edit_obj.options_dict
        (rather than to self.edit_obj's attributes directly, as in the generic
        function.)
        """

        # Apply any changes the user has made
        for key in self.edit_dict.keys():

            if key in self.edit_obj.options_dict:
                self.edit_obj.options_dict[key] = self.edit_dict[key]

        # The name can also be updated, if it has been changed (but it the
        #   entry was blank, keep the old name)
        if 'name' in self.edit_dict \
        and self.edit_dict['name'] != '':
            self.edit_obj.name = self.edit_dict['name']

        # The changes can now be cleared
        self.edit_dict = {}

        # The user can specify multiple video/audio formats. If a mixture of
        #   both is specified, then video formats must be listed before audio
        #   formats (or youtube-dl won't donwload them all)
        # Tell the options.OptionManager object to rearrange them, if
        #   necessary
        self.edit_obj.rearrange_formats()
        # ...then redraw the textview in the Formats tab
        self.formats_tab_redraw_list()


    def retrieve_val(self, name):

        """Can be called by anything.

        Any changes the user has made are temporarily stored in self.edit_dict.

        In the generic function, each key corresponds to an attribute in the
        object being edited, self.edit_obj. In this window, it corresponds to a
        key in self.edit_obj.options_dict.

        If 'name' exists as a key in that dictionary, retrieve the
        corresponding value and return it. Otherwise, the user hasn't yet
        modified the value, so retrieve directly from the attribute in the
        object being edited.

        Args:

            name (str): The name of the attribute in the object being edited

        Returns:

            The original or modified value of that attribute.

        """

        if name in self.edit_dict:

            return self.edit_dict[name]

        elif name == 'uid' or name == 'name' or name == 'dbid':

            return getattr(self.edit_obj, name)

        elif name in self.edit_obj.options_dict:

            return self.edit_obj.options_dict[name]

        else:

            return self.app_obj.system_error(
                404,
                'Unrecognised property name \'' + name + '\'',
            )


    # (Setup tabs)


    def setup_tabs(self):

        """Called by self.setup(), .on_button_apply_clicked() and
        .on_button_reset_clicked().

        Sets up the tabs for this edit window.
        """

        self.setup_name_tab()
        self.setup_files_tab()
        self.setup_formats_tab()
        self.setup_downloads_tab()
        if not self.app_obj.simple_options_flag:
            self.setup_post_process_tab()
        else:
            self.setup_sound_only_tab()
        self.setup_subtitles_tab()
        if not self.app_obj.simple_options_flag:
            self.setup_advanced_tab()


    def setup_name_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'General' tab.
        """

        tab, grid = self.add_notebook_tab(_('_Name'))

        grid_width = 4

        if self.media_data_obj:
            media_type = self.media_data_obj.get_type()

        label = self.add_label(grid,
            _('Name for these download options'),
            0, 0, 2, 1,
        )

        entry = self.add_entry(grid,
            'name',
            2, 0, 2, 1,
        )

        label2 = self.add_label(grid,
            _('Download options applied to'),
            0, 1, 2, 1,
        )

        if self.media_data_obj:

            entry2 = self.add_entry(grid,
                None,
                2, 1, 1, 1,
            )
            entry2.set_editable(False)
            entry2.set_hexpand(False)
            entry2.set_width_chars(8)
            entry2.set_text('#' + str(self.media_data_obj.dbid))

            entry3 = self.add_entry(grid,
                None,
                3, 1, 1, 1,
            )
            entry3.set_editable(False)
            entry3.set_hexpand(True)

            entry3.set_text(
                self.media_data_obj.get_translated_type(True) \
                + ': ' + self.media_data_obj.name,
            )

        else:

            entry2 = self.add_entry(grid,
                None,
                2, 1, 2, 1,
            )
            entry2.set_editable(False)

            if self.edit_obj == self.app_obj.general_options_obj:
                entry2.set_text(_('All channels, playlists and folders'))
            elif self.edit_obj == self.app_obj.classic_options_obj:
                entry2.set_text(_('Downloads in the Classic Mode Tab'))
            else:
                entry2.set_text(_('These options are not applied to anything'))

        self.add_label(grid,
            _(
            'Extra command line options (e.g. --help; do not use -o or' \
            + ' --output)',
            ),
            0, 2, grid_width, 1,
        )

        self.add_textview(grid,
            'extra_cmd_string',
            0, 3, grid_width, 1,
        )

        if self.app_obj.simple_options_flag:
            frame = self.add_pixbuf(grid,
                'hand_right_large',
                0, 4, 1, 1,
            )
            frame.set_hexpand(False)

        else:
            frame = self.add_pixbuf(grid,
                'hand_left_large',
                0, 4, 1, 1,
            )
            frame.set_hexpand(False)

        button = Gtk.Button()
        grid.attach(button, 1, 4, (grid_width - 1), 1)
        if not self.app_obj.simple_options_flag:
            button.set_label(_('Hide advanced download options'))
        else:
            button.set_label(_('Show advanced download options'))
        button.connect('clicked', self.on_simple_options_clicked)

        frame2 = self.add_pixbuf(grid,
            'copy_large',
            0, 5, 1, 1,
        )
        frame2.set_hexpand(False)

        button2 = Gtk.Button(
            _('Import general download options into this window'),
        )
        grid.attach(button2, 1, 5, (grid_width - 1), 1)
        button2.connect('clicked', self.on_clone_options_clicked)
        if self.edit_obj == self.app_obj.general_options_obj:
            # No point cloning the General Options Manager onto itself
            button2.set_sensitive(False)

        frame3 = self.add_pixbuf(grid,
            'warning_large',
            0, 6, 1, 1,
        )
        frame3.set_hexpand(False)

        button3 = Gtk.Button(
            _('Completely reset all download options to their default values'),
        )
        grid.attach(button3, 1, 6, (grid_width - 1), 1)
        button3.connect('clicked', self.on_reset_options_clicked)


    def setup_files_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Files' tab.
        """

        # Add this tab...
        tab, grid = self.add_notebook_tab(_('_Files'), 0)

        # ...and an inner notebook...
        inner_notebook = self.add_inner_notebook(grid)

        # ...with its own tabs
        self.setup_files_names_tab(inner_notebook)
        self.setup_files_filesystem_tab(inner_notebook)
        self.setup_files_cookies_tab(inner_notebook)
        self.setup_files_write_files_tab(inner_notebook)
        self.setup_files_keep_files_tab(inner_notebook)


    def setup_files_names_tab(self, inner_notebook):

        """Called by self.setup_files_tab().

        Sets up the 'File names' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('File _names'),
            inner_notebook,
        )

        grid_width = 4

        # File name options
        self.add_label(grid,
            '<u>' + _('File name options') + '</u>',
            0, 0, grid_width, 1,
        )

        self.add_label(grid,
            _('Format for video file names'),
            0, 1, grid_width, 1,
        )

        store = Gtk.ListStore(int, str)
        num_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        for num in num_list:
            store.append( [num, formats.FILE_OUTPUT_NAME_DICT[num]] )

        current_format = self.edit_obj.options_dict['output_format']
        current_template = formats.FILE_OUTPUT_CONVERT_DICT[current_format]
        if current_template is None:
            current_template = self.edit_obj.options_dict['output_template']

        combo = Gtk.ComboBox.new_with_model(store)
        grid.attach(combo, 0, 2, grid_width, 1)
        renderer_text = Gtk.CellRendererText()
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, "text", 1)
        combo.set_entry_text_column(1)
        combo.set_active(num_list.index(current_format))
        # (Signal connect appears below)

        self.add_label(grid,
            _('File output template'),
            0, 3, grid_width, 1,
        )

        entry = self.add_entry(grid,
            None,
            0, 4, grid_width, 1,
        )
        entry.set_text(current_template)
        # (Signal connect appears below)

        # (Signal connects from above)
        combo.connect('changed', self.on_file_tab_combo_changed, entry)
        entry.connect('changed', self.on_file_tab_entry_changed)

        # Add widgets to a list, so we can sensitise them when a custom
        #   template is selected, and desensitise them the rest of the time
        self.template_widget_list = [entry]

        self.add_label(grid,
            _('Add to template:'),
            0, 5, 1, 1,
        )

        master_list = [
            _('Video properties'),
            [
                'id',               _('Video ID'),
                'title',            _('Video title'),
                'display_id',       _('Alternative video ID'),
                'alt_title',        _('Secondary video title'),
                'url',              _('Video URL'),
                'ext',              _('Video filename extension'),
                'license',          _('Video licence'),
                'age_limit',        _('Age restriction (years)'),
                'is_live',          _('Is a livestream'),
                'autonumber',       _('Autonumber videos, starting at 0'),
            ],
            _('Creator/uploader'),
            [
                'uploader',         _('Full name of video uploader'),
                'uploader_id',      _('Uploader ID'),
                'creator',          _('Nickname/ID of video uploader'),
                'channel',          _('Channel name'),
                'channel_id',       _('Channel ID'),
                'playlist',         _('Playlist name'),
                'playlist_id',      _('Playlist ID'),
                'playlist_index',   _('Video index in playlist'),
            ],
            _('Date/time/location'),
            [
                'release_date',     _('Release date (YYYYMMDD)'),
                'timestamp',        _('Release time (UNIX timestamp)'),
                'upload_date',      _('Upload data (YYYYMMDD)'),
                'duration',         _('Video length (seconds)'),
                'location',         _('Filming location'),
            ],
            _('Video format'),
            [
                'format',           _('Video format'),
                'format_id',        _('Video format code'),
                'width',            _('Video width'),
                'height',           _('Video height'),
                'resolution',       _('Video resolution'),
                'fps',              _('Video frame rate'),
                'tbr',              _('Average video/audio bitrate (KiB/s)'),
                'vbr',              _('Average video bitrate (KiB/s)'),
                'abr',              _('Average audio bitrate (KiB/s)'),
            ],
            _('Ratings/comments'),
            [
                'view_count',       _('Number of views'),
                'like_count',       _('Number of positive ratings'),
                'dislike_count',    _('Number of negative ratings'),
                'average_rating',   _('Average rating'),
                'repost_count',     _('Number of reposts'),
                'comment_count',    _('Number of comments'),
            ],
        ]

        row_num = 4
        while master_list:

            row_num += 1

            this_title = master_list.pop(0)
            this_store_list = master_list.pop(0)

            this_store = Gtk.ListStore(str)
            # (The dictionary is used by self.on_file_tab_button_clicked() to
            #   translate the visible string into the string youtube-dl uses)
            this_store_dict = {}
            while this_store_list:
                item = this_store_list.pop(0)
                mod_item = this_store_list.pop(0)

                this_store_dict[mod_item] = item
                this_store.append( [mod_item] )

            self.add_label(grid,
                this_title,
                1, row_num, 1, 1,
            )

            this_combo = Gtk.ComboBox.new_with_model(this_store)
            grid.attach(this_combo, 2, row_num, 1, 1)
            this_renderer_text = Gtk.CellRendererText()
            this_combo.pack_start(this_renderer_text, True)
            this_combo.add_attribute(this_renderer_text, "text", 0)
            this_combo.set_entry_text_column(0)
            this_combo.set_active(0)

            this_button = Gtk.Button(_('Add'))
            grid.attach(this_button, 3, row_num, 1, 1)
            this_button.connect(
                'clicked',
                self.on_file_tab_button_clicked,
                entry,
                this_combo,
                this_store_dict,
            )

            self.template_widget_list.append(this_combo)
            self.template_widget_list.append(this_button)

        # (De)sensitise widgets in self.template_widget_list
        if current_format == 0:
            self.file_tab_sensitise_widgets(True)
        else:
            self.file_tab_sensitise_widgets(False)


    def setup_files_filesystem_tab(self, inner_notebook):

        """Called by self.setup_files_tab().

        Sets up the 'Filesystem' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Filesystem'),
            inner_notebook,
        )

        grid_width = 2

        # Filesystem options
        if not self.app_obj.simple_options_flag:

            self.add_label(grid,
                '<u>' + _('Filesystem options') + '</u>',
                0, 0, grid_width, 1,
            )

            self.add_checkbutton(grid,
                _('Restrict filenames to ASCII characters'),
                'restrict_filenames',
                0, 1, grid_width, 1,
            )

            self.add_checkbutton(grid,
                _('Use the server\'s file modification time'),
                'nomtime',
                0, 2, grid_width, 1,
            )

        # Filesystem overrides
        self.add_label(grid,
            '<u>' + _('Filesystem overrides') + '</u>',
            0, 3, grid_width, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _('Download all videos into this folder'),
            None,
            0, 4, 1, 1,
        )
        # (Signal connect appears below)

        # (Currently, only two fixed folders are elligible for this mode, so
        #   we'll just add them individually)
        store = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        pixbuf = self.app_obj.main_win_obj.pixbuf_dict['folder_green_small']
        store.append( [pixbuf, self.app_obj.fixed_misc_folder.name] )
        pixbuf = self.app_obj.main_win_obj.pixbuf_dict['folder_blue_small']
        store.append( [pixbuf, self.app_obj.fixed_temp_folder.name] )

        combo = Gtk.ComboBox.new_with_model(store)
        grid.attach(combo, 1, 4, 1, 1)
        renderer_pixbuf5 = Gtk.CellRendererPixbuf()
        combo.pack_start(renderer_pixbuf5, False)
        combo.add_attribute(renderer_pixbuf5, 'pixbuf', 0)
        renderer_text5 = Gtk.CellRendererText()
        combo.pack_start(renderer_text5, True)
        combo.add_attribute(renderer_text5, 'text', 1)
        combo.set_entry_text_column(1)
        # (Signal connect appears below)

        current_override = self.edit_obj.options_dict['use_fixed_folder']
        if current_override is None:
            checkbutton.set_active(False)
            combo.set_sensitive(False)
            combo.set_active(0)
        else:
            checkbutton.set_active(True)
            combo.set_sensitive(True)
            if current_override == self.app_obj.fixed_temp_folder.name:
                combo.set_active(1)
            else:
                # The value should be either None, 'Unsorted Videos' or
                #   'Temporary Videos'. In case the value is anything else,
                #   use 'Unsorted Videos'
                combo.set_active(0)

        # (Signal connects from above)
        checkbutton.connect('toggled', self.on_fixed_folder_toggled, combo)
        combo.connect('changed', self.on_fixed_folder_changed)


    def setup_files_cookies_tab(self, inner_notebook):

        """Called by self.setup_files_tab().

        Sets up the 'Cookies' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Cookies'),
            inner_notebook,
        )

        grid_width = 3

        # Cookies options
        self.add_label(grid,
            '<u>' + _('Cookies options') + '</u>',
            0, 0, grid_width, 1,
        )

        self.add_label(grid,
            '<i>' + _('Path to the downloader\'s cookie jar file') + '</i>',
            0, 1, 1, 1,
        )

        set_button = Gtk.Button(_('Set'))
        grid.attach(set_button, 1, 1, 1, 1)
        # (Signal connect appears below)

        reset_button = Gtk.Button(_('Reset'))
        grid.attach(reset_button, 2, 1, 1, 1)
        # (Signal connect appears below)

        entry = self.add_entry(grid,
            None,
            0, 2, grid_width, 1,
        )
        entry.set_editable(False)

        init_path = self.retrieve_val('cookies_path')
        if init_path == '':

            entry.set_text(
                os.path.abspath(
                    os.path.join(
                        self.app_obj.data_dir,
                        self.app_obj.cookie_file_name,
                    ),
                ),
            )

        else:

            entry.set_text(init_path)

        # (Signal connects from above)
        set_button.connect(
            'clicked',
            self.on_cookies_set_button_clicked,
            entry,
        )
        reset_button.connect(
            'clicked',
            self.on_cookies_reset_button_clicked,
            entry,
        )


    def setup_files_write_files_tab(self, inner_notebook):

        """Called by self.setup_files_tab().

        Sets up the 'Write files' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Write/move files'),
            inner_notebook,
        )

        grid_width = 2

        # Write other files options
        self.add_label(grid,
            '<u>' + _('File write options') + '</u>',
            0, 0, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _('Write video\'s description to a .description file'),
            'write_description',
            0, 1, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _('Write video\'s metadata to an .info.json file'),
            'write_info',
            0, 2, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _(
            'Write video\'s annotations to an .annotations.xml file',
            ),
            'write_annotations',
            0, 3, grid_width, 1,
        )

        self.add_label(grid,
            '<i>' + _(
            'Annotations are not downloaded when checking videos/channels/' \
            + 'playlists/folders'
            ) + '</i>',
            1, 4, 1, 1,
        )

        self.add_checkbutton(grid,
            _('Write the video\'s thumbnail to the same folder'),
            'write_thumbnail',
            0, 5, grid_width, 1,
        )

        # File move options
        self.add_label(grid,
            '<u>' + _('File move options') + '</u>',
            0, 6, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _('Move video\'s description file into a sub-folder'),
            'move_description',
            0, 7, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _('Write video\'s metadata file into a sub-folder'),
            'move_info',
            0, 8, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _('Write video\'s annotations file into a sub-folder'),
            'move_annotations',
            0, 9, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _('Write the video\'s thumbnail into a sub-folder'),
            'move_thumbnail',
            0, 10, grid_width, 1,
        )


    def setup_files_keep_files_tab(self, inner_notebook):

        """Called by self.setup_files_tab().

        Sets up the 'Write files' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Keep files'),
            inner_notebook,
        )

        # Options during real (not simulated) downloads
        self.add_label(grid,
            '<u>' + _('Options during real (not simulated) downloads') \
            + '</u>',
            0, 0, 1, 1,
        )

        self.add_checkbutton(grid,
            _('Keep the description file after the download has finished'),
            'keep_description',
            0, 1, 1, 1,
        )

        self.add_checkbutton(grid,
            _('Keep the metadata file after the download has finished'),
            'keep_info',
            0, 2, 1, 1,
        )

        self.add_checkbutton(grid,
            _('Keep the annotations file after the download has finished'),
            'keep_annotations',
            0, 3, 1, 1,
        )

        self.add_checkbutton(grid,
            _('Keep the thumbnail file after the download has finished'),
            'keep_thumbnail',
            0, 4, 1, 1,
        )

        # Options during simulated (not real) downloads
        self.add_label(grid,
            '<u>' + _('Options during simulated (not real) downloads') \
            + '</u>',
            0, 5, 1, 1,
        )

        self.add_checkbutton(grid,
            _('Keep the description file after the download has finished'),
            'sim_keep_description',
            0, 6, 1, 1,
        )

        self.add_checkbutton(grid,
            _('Keep the metadata file after the download has finished'),
            'sim_keep_info',
            0, 7, 1, 1,
        )

        self.add_checkbutton(grid,
            _('Keep the annotations file after the download has finished'),
            'sim_keep_annotations',
            0, 8, 1, 1,
        )

        self.add_checkbutton(grid,
            _('Keep the thumbnail file after the download has finished'),
            'sim_keep_thumbnail',
            0, 9, 1, 1,
        )


    def setup_formats_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Formats' tab.
        """

        # Add this tab...
        tab, grid = self.add_notebook_tab(_('F_ormats'), 0)

        # ...and an inner notebook...
        inner_notebook = self.add_inner_notebook(grid)

        # ...with its own tabs
        self.setup_formats_preferred_tab(inner_notebook)
        if not self.app_obj.simple_options_flag:
            self.setup_formats_advanced_tab(inner_notebook)


    def setup_formats_preferred_tab(self, inner_notebook):

        """Called by self.setup_formats_tab().

        Sets up the 'Preferred' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Preferred'),
            inner_notebook,
        )

        grid_width = 4

        # Preferred format options
        self.add_label(grid,
            '<u>' + _('Preferred format options') + '</u>',
            0, 0, 4, 1,
        )

        # Left column
        label = self.add_label(grid,
            _('Recognised video/audio formats'),
            0, 1, 2, 1,
        )

        treeview, liststore = self.add_treeview(grid,
            0, 2, 2, 1,
        )

        for key in formats.VIDEO_OPTION_LIST:
            liststore.append([key])

        button = Gtk.Button(_('Add format') + ' >>>')
        grid.attach(button, 0, 3, 2, 1)
        # (Signal connect appears below)

        # Right column
        label2 = self.add_label(grid,
            _('List of preferred formats'),
            2, 1, 2, 1,
        )

        treeview2, self.formats_liststore = self.add_treeview(grid,
            2, 2, 2, 1,
        )

        # (Need to reverse formats.VIDEO_OPTION_DICT for quick lookup)
        rev_dict = {}
        for key in formats.VIDEO_OPTION_DICT:
            rev_dict[formats.VIDEO_OPTION_DICT[key]] = key

        # There are multiple possible format options, any or all of which might
        #   be set
        self.formats_tab_redraw_list()

        button2 = Gtk.Button('<<< ' + _('Remove format'))
        grid.attach(button2, 2, 3, 2, 1)
        # (Signal connect appears below)

        button3 = Gtk.Button('^ ' + _('Move up'))
        grid.attach(button3, 2, 4, 1, 1)
        # (Signal connect appears below)

        button4 = Gtk.Button('v ' + _('Move down'))
        grid.attach(button4, 3, 4, 1, 1)
        # (Signal connect appears below)

        # (Signal connects from above)
        # 'Add format'
        button.connect(
            'clicked',
            self.on_formats_tab_add_clicked,
            button2,
            button3,
            button4,
            treeview,
        )
        # 'Remove format'
        button2.connect(
            'clicked',
            self.on_formats_tab_remove_clicked,
            button,
            button3,
            button4,
            treeview2,
        )
        # 'Move up'
        button3.connect(
            'clicked',
            self.on_formats_tab_up_clicked,
            treeview2,
        )
        # 'Move down'
        button4.connect(
            'clicked',
            self.on_formats_tab_down_clicked,
            treeview2,
        )

        # Desensitise buttons, as appropriate
        format_count = self.formats_tab_count_formats()
        if format_count == 0:
            button2.set_sensitive(False)
            button3.set_sensitive(False)
            button4.set_sensitive(False)

        self.add_label(grid,
            _(
            'If a merge is required after post-processing, output to this' \
            + ' format:',
            ),
            0, 5, grid_width, 1,
        )

        combo_list = ['', 'flv', 'mkv', 'mp4', 'ogg', 'webm']
        combo = self.add_combo(grid,
            combo_list,
            None,
            (grid_width - 1), 5, 1, 1,
        )
        combo.set_active(
            combo_list.index(self.retrieve_val('merge_output_format')),
        )
        combo.connect('changed', self.on_formats_tab_combo_changed)


    def setup_formats_advanced_tab(self, inner_notebook):

        """Called by self.setup_formats_tab().

        Sets up the 'Advanced' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Advanced'),
            inner_notebook,
        )

        grid_width = 2
        extra_row = 0

        # Multiple format options
        self.add_label(grid,
            '<u>' + _('Multiple format options') + '</u>',
            0, 0, grid_width, 1,
        )

        if self.app_obj.allow_ytdl_archive_flag:

            extra_row = 1
            self.add_label(grid,
                '<i>' + _(
                    'Multiple formats will not be downloaded, because an' \
                    + ' archive file will be created'
                ) + '\n' + _(
                    'The archive file can be disabled in the System' \
                    ' Preferences window',
                ) + '</i>',
                0, 1, grid_width, 1,
            )

        radiobutton = self.add_radiobutton(grid,
            None,
            _(
            'For each video, download the first available format from the' \
            + ' preferred list',
            ),
            None,
            None,
            0, (1 + extra_row), grid_width, 1,
        )
        if self.retrieve_val('video_format_mode') == 'single':
            radiobutton.set_active(True)
        # (Signal connect appears below)

        radiobutton2 = self.add_radiobutton(grid,
            radiobutton,
            _(
            'From the preferred list, download the first format that\'s' \
            + ' available for all videos',
            ),
            None,
            None,
            0, (2 + extra_row), grid_width, 1,
        )
        if self.retrieve_val('video_format_mode') == 'single_agree':
            radiobutton2.set_active(True)
        # (Signal connect appears below)

        radiobutton3 = self.add_radiobutton(grid,
            radiobutton2,
            _(
            'For each video, download all available formats from the' \
            + ' preferred list',
            ),
            None,
            None,
            0, (3 + extra_row), grid_width, 1,
        )
        if self.retrieve_val('video_format_mode') == 'multiple':
            radiobutton3.set_active(True)
        # (Signal connect appears below)

        radiobutton4 = self.add_radiobutton(grid,
            radiobutton2,
            _('Download all available formats for all videos'),
            None,
            None,
            0, (4 + extra_row), grid_width, 1,
        )
        if self.retrieve_val('video_format_mode') == 'all':
            radiobutton4.set_active(True)
        # (Signal connect appears below)

        # (Signal connects from above)
        radiobutton.connect(
            'toggled',
            self.on_video_format_mode_toggled,
            'single',
        )
        radiobutton2.connect(
            'toggled',
            self.on_video_format_mode_toggled,
            'single_agree',
        )
        radiobutton3.connect(
            'toggled',
            self.on_video_format_mode_toggled,
            'multiple',
        )
        radiobutton4.connect(
            'toggled',
            self.on_video_format_mode_toggled,
            'all',
        )

        # Other format options
        self.add_label(grid,
            '<u>' + _('Other format options') + '</u>',
            0, (5 + extra_row), grid_width, 1,
        )

        self.add_checkbutton(grid,
            _('Prefer free video formats, unless one is specified above'),
            'prefer_free_formats',
            0, (6 + extra_row), grid_width, 1,
        )

        self.add_checkbutton(grid,
            _('Do not download DASH-related data for YouTube videos'),
            'yt_skip_dash',
            0, (7 + extra_row), grid_width, 1,
        )


    def setup_downloads_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Downloads' tab.
        """

        # Simple options only
        if self.app_obj.simple_options_flag:

            tab, grid = self.add_notebook_tab(_('_Downloads'))

            row_count = 0

            # Download options
            self.add_label(grid,
                '<u>' + _('Download options') + '</u>',
                0, row_count, 1, 1,
            )

            row_count += 1
            row_count = self.downloads_age_widgets(grid, row_count)
            row_count = self.downloads_date_widgets(grid, row_count)
            row_count = self.downloads_views_widgets(grid, row_count)

        # All options
        else:

            # Add this tab...
            tab, grid = self.add_notebook_tab(_('_Downloads'), 0)

            # ...and an inner notebook...
            inner_notebook = self.add_inner_notebook(grid)

            # ...with its own tabs
            self.setup_downloads_general_tab(inner_notebook)
            self.setup_downloads_playlists_tab(inner_notebook)
            self.setup_downloads_size_limits_tab(inner_notebook)
            self.setup_downloads_dates_tab(inner_notebook)
            self.setup_downloads_views_tab(inner_notebook)
            self.setup_downloads_filtering_tab(inner_notebook)
            self.setup_downloads_external_tab(inner_notebook)


    def setup_downloads_general_tab(self, inner_notebook):

        """Called by self.setup_downloads_tab().

        Sets up the 'General' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab('_General', inner_notebook)

        # Download options
        self.add_label(grid,
            '<u>' + _('Download options') + '</u>',
            0, 0, 1, 1,
        )

        row_count = 1
        row_count = self.downloads_general_widgets(grid, row_count)
        row_count = self.downloads_age_widgets(grid, row_count)


    def setup_downloads_playlists_tab(self, inner_notebook):

        """Called by self.setup_downloads_tab().

        Sets up the 'Playlists' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Playlists'),
            inner_notebook,
        )

        row_count = self.downloads_playlist_widgets(grid, 0)


    def setup_downloads_size_limits_tab(self, inner_notebook):

        """Called by self.setup_downloads_tab().

        Sets up the 'Size limits' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Size limits'),
            inner_notebook,
        )

        row_count = self.downloads_size_limit_widgets(grid, 0)


    def setup_downloads_dates_tab(self, inner_notebook):

        """Called by self.setup_downloads_tab().

        Sets up the 'Dates' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(_('_Dates'), inner_notebook)

        row_count = self.downloads_date_widgets(grid, 0)


    def setup_downloads_views_tab(self, inner_notebook):

        """Called by self.setup_downloads_tab().

        Sets up the 'Views' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(_('_Views'), inner_notebook)

        row_count = self.downloads_views_widgets(grid, 0)


    def setup_downloads_filtering_tab(self, inner_notebook):

        """Called by self.setup_downloads_tab().

        Sets up the 'Filtering' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Filtering'),
            inner_notebook,
        )

        row_count = self.downloads_filtering_widgets(grid, 0)


    def setup_downloads_external_tab(self, inner_notebook):

        """Called by self.setup_downloads_tab().

        Sets up the 'External' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(_('_External'), inner_notebook)

        row_count = self.downloads_external_widgets(grid, 0)


    def setup_sound_only_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Sound Only' tab.
        """

        tab, grid = self.add_notebook_tab(_('_Sound only'))
        grid_width = 4

        # Sound only options
        self.add_label(grid,
            '<u>' + _('Sound only options') + '</u>',
            0, 0, grid_width, 1,
        )

        # (The MS Windows installer includes FFmpeg)
        text = _(
        'Download each video, extract the sound, and then discard the' \
        + ' original videos',
        )
        if os.name != 'nt':
            text += '\n' + _(
                '(requires that FFmpeg or AVConv is installed on your system)'
            )

        self.add_checkbutton(grid,
            text,
            'extract_audio',
            0, 1, grid_width, 1,
        )

        label = self.add_label(grid,
            _('Use this audio format:') + ' ',
            0, 2, 1, 1,
        )
        label.set_hexpand(False)

        combo_list = formats.AUDIO_FORMAT_LIST.copy()
        combo_list.insert(0, '')
        combo = self.add_combo(grid,
            combo_list,
            'audio_format',
            1, 2, 1, 1,
        )
        combo.set_hexpand(True)

        label2 = self.add_label(grid,
            _('Use this audio quality:') + ' ',
            2, 2, 1, 1,
        )
        label2.set_hexpand(False)

        combo2_list = [
            [_('High'), '0'],
            [_('Medium'), '5'],
            [_('Low'), '9'],
        ]

        combo2 = self.add_combo_with_data(grid,
            combo2_list,
            'audio_quality',
            3, 2, 1, 1,
        )
        combo2.set_hexpand(True)


    def setup_post_process_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Post-processing' tab.
        """

        tab, grid = self.add_notebook_tab(_('_Post-processing'))
        grid_width = 2
        grid.set_column_homogeneous(True)

        # Post-processing options
        self.add_label(grid,
            '<u>' + _('Post-processing options') + '</u>',
            0, 0, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _(
            'Post-process video files to convert them to audio-only files',
            ),
            'extract_audio',
            0, 1, grid_width, 1,
        )

        button = self.add_checkbutton(grid,
            _('Prefer AVConv over FFmpeg'),
            'prefer_avconv',
            0, 2, 1, 1,
        )
        if os.name == 'nt':
            button.set_sensitive(False)

        button2 = self.add_checkbutton(grid,
            _('Prefer FFmpeg over AVConv (default)'),
            'prefer_ffmpeg',
            1, 2, 1, 1,
        )
        if os.name == 'nt':
            button2.set_sensitive(False)

        self.add_label(grid,
            _('Audio format of the post-processed file'),
            0, 3, 1, 1,
        )

        combo_list = formats.AUDIO_FORMAT_LIST.copy()
        combo_list.insert(0, '')
        self.add_combo(grid,
            combo_list,
            'audio_format',
            1, 3, 1, 1,
        )

        self.add_label(grid,
            _('Audio quality of the post-processed file'),
            0, 4, 1, 1,
        )

        combo2_list = [
            [_('High'), '0'],
            [_('Medium'), '5'],
            [_('Low'), '9'],
        ]

        self.add_combo_with_data(grid,
            combo2_list,
            'audio_quality',
            1, 4, 1, 1,
        )

        self.add_label(grid,
            _('Encode video to another format, if necessary'),
            0, 5, 1, 1,
        )

        combo_list3 = ['', 'avi', 'flv', 'mkv', 'mp4', 'ogg', 'webm']
        self.add_combo(grid,
            combo_list3,
            'recode_video',
            1, 5, 1, 1,
        )

        self.add_label(grid,
            _('Arguments to pass to post-processor'),
            0, 6, 1, 1,
        )

        self.add_entry(grid,
            'pp_args',
            1, 6, 1, 1,
        )

        self.add_checkbutton(grid,
            _('Keep original file after processing it'),
            'keep_video',
            0, 7, 1, 1,
        )

        # (This option can also be modified in the Post-process tab)
        self.embed_checkbutton = self.add_checkbutton(grid,
            _('Merge subtitles file with video (.mp4 only)'),
            None,
            1, 7, 1, 1,
        )
        self.embed_checkbutton.set_active(self.retrieve_val('embed_subs'))
        self.embed_checkbutton.connect(
            'toggled',
            self.on_embed_checkbutton_toggled,
        )

        self.add_checkbutton(grid,
            _('Embed thumbnail in audio file as cover art'),
            'embed_thumbnail',
            0, 8, 1, 1,
        )

        self.add_checkbutton(grid,
            _('Write metadata to the video file'),
            'add_metadata',
            1, 8, 1, 1,
        )

        self.add_label(grid,
            _('Automatically correct known faults of the file'),
            0, 9, 1, 1,
        )

        combo_list4 = [
            ['', ''],
            [_('Do nothing'), 'never'],
            [_('Warn, but do nothing'), 'warn'],
            [_('Fix if possible, otherwise warn'), 'detect_or_warn'],
        ]
        self.add_combo_with_data(grid,
            combo_list4,
            'fixup_policy',
            1, 9, 1, 1,
        )


    def setup_subtitles_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Subtitles' tab.
        """

        # Add this tab...
        tab, grid = self.add_notebook_tab(_('S_ubtitles'), 0)

        # ...and an inner notebook...
        inner_notebook = self.add_inner_notebook(grid)

        # ...with its own tabs
        self.setup_subtitles_options_tab(inner_notebook)
        self.setup_subtitles_more_options_tab(inner_notebook)


    def setup_subtitles_options_tab(self, inner_notebook):

        """Called by self.setup_subtitles_tab().

        Sets up the 'Options' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(_('_Options'), inner_notebook)

        # Subtitles options
        self.add_label(grid,
            '<u>' + _('Subtitles options') + '</u>',
            0, 0, 2, 1,
        )

        radiobutton = self.add_radiobutton(grid,
            None,
            _('Don\'t download the subtitles file'),
            None,
            None,
            0, 1, 2, 1,
        )
        if self.retrieve_val('write_subs') is False:
            radiobutton.set_active(True)
        # (Signal connect appears below)

        radiobutton2 = self.add_radiobutton(grid,
            radiobutton,
            _('Download the automatic subtitles file (YouTube only)'),
            None,
            None,
            0, 2, 2, 1,
        )
        if self.retrieve_val('write_subs') is True \
        and self.retrieve_val('write_auto_subs') is True:
            radiobutton2.set_active(True)
        # (Signal connect appears below)

        radiobutton3 = self.add_radiobutton(grid,
            radiobutton2,
            _('Download all available subtitles files'),
            None,
            None,
            0, 3, 2, 1,
        )
        if self.retrieve_val('write_subs') is True \
        and self.retrieve_val('write_all_subs') is True:
            radiobutton3.set_active(True)
        # (Signal connect appears below)

        radiobutton4 = self.add_radiobutton(grid,
            radiobutton3,
            _('Download subtitles file for these languages:'),
            None,
            None,
            0, 4, 2, 1,
        )
        if self.retrieve_val('write_subs') is True \
        and self.retrieve_val('write_auto_subs') is False \
        and self.retrieve_val('write_all_subs') is False:
            radiobutton4.set_active(True)
        # (Signal connect appears below)

        treeview, liststore = self.add_treeview(grid,
            0, 5, 1, 1,
        )
        for key in formats.LANGUAGE_CODE_LIST:
            liststore.append([key])

        # We need a reverse dictionary for quick lookup
        rev_dict = {}
        for key in formats.LANGUAGE_CODE_DICT:
            val = formats.LANGUAGE_CODE_DICT[key]
            rev_dict[val] = key

        button = Gtk.Button(_('Add language') + ' >>>')
        grid.attach(button, 0, 6, 1, 1)
        # (Signal connect appears below)

        treeview2, liststore2 = self.add_treeview(grid,
            1, 5, 1, 1,
        )
        lang_list = self.retrieve_val('subs_lang_list')
        # The option stores ISO 639-1 Language Codes like 'en'; convert them to
        #   language names like 'English'
        for lang_code in lang_list:
            liststore2.append([rev_dict[lang_code]])

        button2 = Gtk.Button('<<< ' + _('Remove language'))
        grid.attach(button2, 1, 6, 1, 1)
        # (Signal connect appears below)

        # Desensitise the buttons, if the matching radiobutton isn't active
        if not radiobutton4.get_active():
            button.set_sensitive(False)
            button2.set_sensitive(False)

        # (Signal connects from above)
        button.connect(
            'clicked',
            self.on_subtitles_tab_add_clicked,
            treeview,
            liststore2,
            rev_dict,
        )
        button2.connect(
            'clicked',
            self.on_subtitles_tab_remove_clicked,
            treeview2,
            liststore2,
            rev_dict,
        )
        radiobutton.connect(
            'toggled',
            self.on_subtitles_toggled,
            button, button2,
            'write_subs',
        )
        radiobutton2.connect(
            'toggled',
            self.on_subtitles_toggled,
            button, button2,
            'write_auto_subs',
        )
        radiobutton3.connect(
            'toggled',
            self.on_subtitles_toggled,
            button, button2,
            'write_all_subs',
        )
        radiobutton4.connect(
            'toggled',
            self.on_subtitles_toggled,
            button, button2,
            'subs_lang',
        )


    def setup_subtitles_more_options_tab(self, inner_notebook):

        """Called by self.setup_subtitles_tab().

        Sets up the 'Format' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_More options'),
            inner_notebook,
        )

        # Subtitle format options
        self.add_label(grid,
            '<u>' + _('Subtitle format options') + '</u>',
            0, 0, 1, 1,
        )

        self.add_label(grid,
            _(
            'Preferred subtitle format(s), e.g. \'srt\', \'vtt\',' \
            + ' \'srt/ass/vtt/lrc/best\'',
            ),
            0, 1, 1, 1,
        )

        self.add_entry(grid,
            'subs_format',
            0, 2, 1, 1,
        )

        # Post-processing options
        self.add_label(grid,
            '<u>' + _('Post-processing options') + '</u>',
            0, 3, 1, 1,
        )

        self.add_label(grid,
            '<i>' + _('Applies to .mp4 videos only; requires FFmpeg/AVConv') \
            + '</i>',
            0, 4, 1, 1,
        )

        # (This option can also be modified in the Post-process tab)
        self.embed_checkbutton2 = self.add_checkbutton(grid,
            _('During post-processing, merge subtitles file with video'),
            None,
            0, 5, 1, 1,
        )
        self.embed_checkbutton2.set_active(self.retrieve_val('embed_subs'))
        self.embed_checkbutton2.connect(
            'toggled',
            self.on_embed_checkbutton_toggled,
        )


    def setup_advanced_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Advanced' tab.
        """

        # Add this tab...
        tab, grid = self.add_notebook_tab(_('_Advanced'), 0)

        # ...and an inner notebook...
        inner_notebook = self.add_inner_notebook(grid)

        # ...with its own tabs
        self.setup_advanced_authentication_tab(inner_notebook)
        self.setup_advanced_network_tab(inner_notebook)
        self.setup_advanced_georestrict_tab(inner_notebook)
        self.setup_advanced_workaround_tab(inner_notebook)


    def setup_advanced_authentication_tab(self, inner_notebook):

        """Called by self.setup_advanced_tab().

        Sets up the 'Authentication' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Authentication'),
            inner_notebook,
        )

        grid_width = 2

        # Authentication options
        self.add_label(grid,
            '<u>' + _('Authentication options') + '</u>',
            0, 0, grid_width, 1,
        )

        self.add_label(grid,
            _('Username with which to log in'),
            0, 1, 1, 1,
        )

        self.add_entry(grid,
            'username',
            1, 1, 1, 1,
        )

        self.add_label(grid,
            _('Password with which to log in'),
            0, 2, 1, 1,
        )

        self.add_entry(grid,
            'password',
            1, 2, 1, 1,
        )

        self.add_label(grid,
            _('Password required for this URL'),
            0, 3, 1, 1,
        )

        self.add_entry(grid,
            'video_password',
            1, 3, 1, 1,
        )

        self.add_label(grid,
            _('Two-factor authentication code'),
            0, 4, 1, 1,
        )

        self.add_entry(grid,
            'two_factor',
            1, 4, 1, 1,
        )

        self.add_checkbutton(grid,
            _('Use .netrc authentication data'),
            'force_ipv4',
            0, 5, grid_width, 1,
        )


    def setup_advanced_network_tab(self, inner_notebook):

        """Called by self.setup_advanced_tab().

        Sets up the 'Network' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(_('_Network'), inner_notebook)

        grid_width = 2

        # Network options
        self.add_label(grid,
            '<u>' + _('Network options') + '</u>',
            0, 0, grid_width, 1,
        )

        self.add_label(grid,
            _(
            'Use this HTTP/HTTPS proxy (if set, overrides the proxies in' \
            + ' Tartube\'s preferences window',
            ),
            0, 1, grid_width, 1,
        )

        self.add_entry(grid,
            'proxy',
            0, 2, grid_width, 1,
        )

        self.add_label(grid,
            _('Time to wait for socket connection, before giving up'),
            0, 3, 1, 1,
        )

        self.add_entry(grid,
            'socket_timeout',
            1, 3, 1, 1,
        )

        self.add_label(grid,
            _('Bind with this Client-side IP address'),
            0, 4, 1, 1,
        )

        self.add_entry(grid,
            'source_address',
            1, 4, 1, 1,
        )

        self.add_checkbutton(grid,
            _('Connect using IPv4 only'),
            'force_ipv4',
            0, 5, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _('Connect using IPv6 only'),
            'force_ipv6',
            0, 6, grid_width, 1,
        )


    def setup_advanced_georestrict_tab(self, inner_notebook):

        """Called by self.setup_advanced_tab().

        Sets up the 'Geo-restriction' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Geo-restriction'),
            inner_notebook,
        )

        grid_width = 2

        # Geo-restriction options
        self.add_label(grid,
            '<u>' + _('Geo-restriction options') + '</u>',
            0, 0, grid_width, 1,
        )

        self.add_label(grid,
            _('Use this proxy to verify IP address'),
            0, 1, 1, 1,
        )

        self.add_entry(grid,
            'geo_verification_proxy',
            1, 1, 1, 1,
        )

        self.add_checkbutton(grid,
            _('Bypass using fake X-Forwarded-For HTTP header'),
            'geo_bypass',
            0, 2, 1, 1,
        )

        self.add_checkbutton(grid,
            _('Don\'t bypass using fake HTTP header'),
            'no_geo_bypass',
            1, 2, 1, 1,
        )

        self.add_label(grid,
            _('Bypass geo-restriction with ISO 3166-2 country code'),
            0, 3, 1, 1,
        )

        self.add_entry(grid,
            'geo_bypass_country',
            1, 3, 1, 1,
        )

        self.add_label(grid,
            _('Bypass with explicit IP block in CIDR notation'),
            0, 4, 1, 1,
        )

        self.add_entry(grid,
            'geo_bypass_ip_block',
            1, 4, 1, 1,
        )


    def setup_advanced_workaround_tab(self, inner_notebook):

        """Called by self.setup_advanced_tab().

        Sets up the 'Workaround' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab('_Workaround', inner_notebook)

        grid_width = 2

        # Workaround options
        self.add_label(grid,
            '<u>' + _('Workaround options') + '</u>',
            0, 0, grid_width, 1,
        )

        self.add_label(grid,
            _('Custom user agent'),
            0, 1, 1, 1,
        )

        self.add_entry(grid,
            'user_agent',
            1, 1, 1, 1,
        )

        self.add_label(grid,
            _('Custom referer if video access has restricted domain'),
            0, 2, 1, 1,
        )

        self.add_entry(grid,
            'referer',
            1, 2, 1, 1,
        )

        self.add_label(grid,
            _('Minimum seconds to sleep before each download'),
            0, 3, 1, 1,
        )

        spinbutton = self.add_spinbutton(grid,
            0, 3600, 1,
            None,
            1, 3, 1, 1
        )
        # (Signal connect appears below)

        self.add_label(grid,
            _('Maximum seconds to sleep before each download'),
            0, 4, 1, 1,
        )

        spinbutton2 = self.add_spinbutton(grid,
            0, 3600, 1,
            'max_sleep_interval',
            1, 4, 1, 1
        )
        if self.edit_obj.options_dict['min_sleep_interval'] == 0:
            spinbutton2.set_sensitive(False)

        # (Signal connect from above)
        spinbutton.connect(
            'value-changed',
            self.on_sleep_button_changed,
            spinbutton2,
        )

        self.add_label(grid,
            _('Force this encoding (experimental)'),
            0, 5, 1, 1,
        )

        self.add_entry(grid,
            'force_encoding',
            1, 5, 1, 1,
        )

        self.add_checkbutton(grid,
            _('Suppress HTTPS certificate validation'),
            'no_check_certificate',
            0, 6, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _(
            'Use an unencrypted connection to retrieve information about' \
            + ' videos (YouTube only)',
            ),
            'prefer_insecure',
            0, 7, grid_width, 1,
        )


    # (Tab support functions - general)


    def file_tab_sensitise_widgets(self, flag):

        """Called by self.setup_files_names_tab() and
        self.on_file_tab_combo_changed().

        Sensitises or desensitises a list of widgets in response to the user's
        interactions with widgets on that tab.

        Args:

            flag (bool): True to sensitise the widgets, False to desensitise
                them

        """

        self.template_flag = flag
        for widget in self.template_widget_list:
            widget.set_sensitive(flag)


    def formats_tab_count_formats(self):

        """Called by several parts of self.setup_formats_tab().

        Counts the number of video/audio formats that are set.

        Returns:

            An integer in the range 0-3

        """

        format_list = self.retrieve_val('video_format_list')

        return len(format_list)


    def formats_tab_redraw_list(self):

        """Called by self.setup_formats_tab() and then again by
        self.apply_changes().

        Update the Gtk.ListStore containing the user's preferrerd video/audio
        formats.
        """

        # Empty the treeview
        self.formats_liststore.clear()

        # (Need to reverse formats.VIDEO_OPTION_DICT for quick lookup)
        rev_dict = {}
        for key in formats.VIDEO_OPTION_DICT:
            rev_dict[formats.VIDEO_OPTION_DICT[key]] = key

        # Refill the treeview
        format_list = self.retrieve_val('video_format_list')
        for item in format_list:
            self.formats_liststore.append([rev_dict[item]])


    # (Tab support functions - Downloads tab)


    def downloads_general_widgets(self, grid, row_count):

        """Called by various parts of the Downloads tabs."""

        grid_width = 3

        self.add_checkbutton(grid,
            _('Prefer HLS (HTTP Live Streaming)'),
            'native_hls',
            0, row_count, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _('Prefer FFMpeg over native HLS downloader'),
            'hls_prefer_ffmpeg',
            0, (row_count + 1), grid_width, 1,
        )

        self.add_checkbutton(grid,
            _('Include advertisements (experimental feature)'),
            'include_ads',
            0, (row_count + 2), grid_width, 1,
        )

        self.add_checkbutton(grid,
            _('Ignore errors and continue the download operation'),
            'ignore_errors',
            0, (row_count + 3), grid_width, 1,
        )

        self.add_label(grid,
            _('Number of retries'),
            0, (row_count + 4), 1, 1,
        )

        self.add_spinbutton(grid,
            1, 99, 1,
            'retries',
            1, (row_count + 4), 1, 1,
        )

        return row_count + 5


    def downloads_age_widgets(self, grid, row_count):

        """Called by various parts of the Downloads tabs."""

        grid_width = 3

        self.add_label(grid,
            _('Download videos suitable for this age'),
            0, row_count, 1, 1,
        )

        self.add_entry(grid,
            'age_limit',
            1, row_count, 1, 1,
        )

        return row_count + 2


    def downloads_playlist_widgets(self, grid, row_count):

        """Called by various parts of the Downloads tabs."""

        grid_width = 2

        # Playlist options
        self.add_label(grid,
            '<u>' + _('Playlist options') + '</u>',
            0, row_count, grid_width, 1,
        )

        self.add_label(grid,
            '<i>' + _(
                'Channels and playlists are handled in the same way, so' \
                + ' these options can be used with both',
            ) + '</i>',
            0, (row_count + 1), grid_width, 1,
        )

        self.add_label(grid,
            _('Start downloading playlist from index'),
            0, (row_count + 2), 1, 1,
           )

        self.add_spinbutton(grid,
            1, None, 1,
            'playlist_start',
            1, (row_count + 2), 1, 1,
        )

        self.add_label(grid,
            _('Stop downloading playlist at index'),
            0, (row_count + 3), 1, 1,
        )

        self.add_spinbutton(grid,
            0, None, 1,
            'playlist_end',
            1, (row_count + 3), 1, 1,
        )

        self.add_label(grid,
            _('Abort operation after downloading this many videos'),
            0, (row_count + 4), 1, 1,
        )

        self.add_spinbutton(grid,
            0, None, 1,
            'max_downloads',
            1, (row_count + 4), 1, 1,
        )

        self.add_checkbutton(grid,
            _('Abort downloading the playlist if an error occurs'),
            'abort_on_error',
            0, (row_count + 5), grid_width, 1,
        )

        self.add_checkbutton(grid,
            _('Download playlist in reverse order'),
            'playlist_reverse',
            0, (row_count + 6), grid_width, 1,
        )

        self.add_checkbutton(grid,
            _('Download playlist in random order'),
            'playlist_random',
            0, (row_count + 7), grid_width, 1,
        )

        return row_count + 7


    def downloads_size_limit_widgets(self, grid, row_count):

        """Called by various parts of the Downloads tabs."""

        grid_width = 3

        self.add_label(grid,
            '<u>' + _('Video size limit options') + '</u>',
            0, row_count, grid_width, 1,
        )

        self.add_label(grid,
            _('Minimum file size for video downloads'),
            0, (row_count + 1), (grid_width - 2), 1,
        )

        self.add_spinbutton(grid,
            0, None, 1,
            'min_filesize',
               (grid_width - 2), (row_count + 1), 1, 1,
        )

        self.add_combo_with_data(grid,
            formats.FILE_SIZE_UNIT_LIST,
            'min_filesize_unit',
            (grid_width - 1), (row_count + 1), 1, 1,
        )

        self.add_label(grid,
            _('Maximum file size for video downloads'),
            0, (row_count + 2), (grid_width - 2), 1,
        )

        self.add_spinbutton(grid,
            0, None, 1,
            'max_filesize',
            (grid_width - 2), (row_count + 2), 1, 1,
        )

        self.add_combo_with_data(grid,
            formats.FILE_SIZE_UNIT_LIST,
            'max_filesize_unit',
            (grid_width - 1), (row_count + 2), 1, 1,
        )

        return row_count + 3


    def downloads_date_widgets(self, grid, row_count):

        """Called by various parts of the Downloads tabs."""

        grid_width = 3

        # Video date options
        self.add_label(grid,
            '<u>' + _('Video date options') + '</u>',
            0, row_count, grid_width, 1,
        )

        self.add_label(grid,
            _('Only videos uploaded on this date'),
            0, (row_count + 1), (grid_width - 2), 1,
        )

        entry = self.add_entry(grid,
            'date',
            (grid_width - 2), (row_count + 1), 1, 1,
        )
        entry.set_editable(False)

        button = Gtk.Button(_('Set'))
        grid.attach(button, (grid_width - 1), (row_count + 1), 1, 1)
        button.connect(
            'clicked',
            self.on_button_set_date_clicked,
            entry,
            'date',
        )

        self.add_label(grid,
            _('Only videos uploaded before this date'),
            0, (row_count + 2), (grid_width - 2), 1,
        )

        entry2 = self.add_entry(grid,
            'date_before',
            (grid_width - 2), (row_count + 2), 1, 1,
        )
        entry2.set_editable(False)

        button2 = Gtk.Button(_('Set'))
        grid.attach(button2, (grid_width - 1), (row_count + 2), 1, 1)
        button2.connect(
            'clicked',
            self.on_button_set_date_clicked,
            entry2,
            'date_before',
        )

        self.add_label(grid,
            _('Only videos uploaded after this date'),
            0, (row_count + 3), (grid_width - 2), 1,
        )

        entry3 = self.add_entry(grid,
            'date_after',
            (grid_width - 2), (row_count + 3), 1, 1,
        )
        entry3.set_editable(False)

        button3 = Gtk.Button(_('Set'))
        grid.attach(button3, (grid_width - 1), (row_count + 3), 1, 1)
        button3.connect(
            'clicked',
            self.on_button_set_date_clicked,
            entry3,
            'date_after',
        )

        return row_count + 4


    def downloads_views_widgets(self, grid, row_count):

        """Called by various parts of the Downloads tabs."""

        grid_width = 3

        # Video views options
        self.add_label(grid,
            '<u>' + _('Video views options') + '</u>',
            0, row_count, grid_width, 1,
        )

        self.add_label(grid,
            _('Minimum number of views'),
            0, (row_count + 1), (grid_width - 2), 1,
        )

        spinbutton = self.add_spinbutton(grid,
            0, None, 1,
            'min_views',
            (grid_width - 2), (row_count + 1), 1, 1,
        )

        self.add_label(grid,
            _('Maximum number of views'),
            0, (row_count + 2), (grid_width - 2), 1,
        )

        spinbutton2 = self.add_spinbutton(grid,
            0, None, 1,
            'max_views',
            (grid_width - 2), (row_count + 2), 1, 1,
        )

        # (This improves layout a little)
        if not self.app_obj.simple_options_flag:
            spinbutton.set_hexpand(True)
            spinbutton2.set_hexpand(True)

        return row_count + 3


    def downloads_filtering_widgets(self, grid, row_count):

        """Called by various parts of the Downloads tabs."""

        grid_width = 3

        self.add_label(grid,
            '<u>' + _('Video filtering options') + '</u>',
            0, row_count, grid_width, 1,
        )

        self.add_label(grid,
            _('Download only matching titles (regex or caseless substring)'),
            0, (row_count + 1), grid_width, 1,
        )

        self.add_textview(grid,
            'match_title_list',
            0, (row_count + 2), grid_width, 1,
        )

        self.add_label(grid,
            _(
            'Don\'t download only matching titles (regex or caseless' \
            + ' substring)',
            ),
            0, (row_count + 3), grid_width, 1,
        )

        self.add_textview(grid,
            'reject_title_list',
            0, (row_count + 4), grid_width, 1,
        )

        self.add_label(grid,
            _('Generic video filter, for example:') + ' like_count > 100',
            0, (row_count + 5), grid_width, 1,
        )

        self.add_entry(grid,
            'match_filter',
            0, (row_count + 6), grid_width, 1,
        )

        return row_count + 7


    def downloads_external_widgets(self, grid, row_count):

        """Called by various parts of the Downloads tabs."""

        grid_width = 2

        # External downloader options
        self.add_label(grid,
            '<u>' + _('External downloader options') + '</u>',
            0, row_count, grid_width, 1,
        )

        self.add_label(grid,
            _('Use this external downloader'),
            0, (row_count + 1), 1, 1,
        )

        ext_list = [
            '', 'aria2c', 'avconv', 'axel', 'curl', 'ffmpeg', 'httpie',
            'wget',
        ]

        combo = self.add_combo(grid,
            ext_list,
            'external_downloader',
            1, (row_count + 1), 1, 1,
        )
        combo.set_hexpand(True)

        self.add_label(grid,
            _('Arguments to pass to external downloader'),
            0, (row_count + 2), grid_width, 1,
        )

        self.add_entry(grid,
            'external_arg_string',
            0, (row_count + 3), grid_width, 1,
        )

        return row_count + 4


    # Callback class methods


    def on_button_set_date_clicked(self, button, entry, prop):

        """Called by callback in self.downloads_date_widgets().

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Another widget to be modified by this function

            prop (str): The attribute in self.edit_dict to modify

        """

        # Prompt the user for a new calendar date
        dialogue_win = mainwin.CalendarDialogue(
            self,
            self.retrieve_val(prop),
        )

        response = dialogue_win.run()

        # Retrieve user choices from the dialogue window, before destroying it
        if response == Gtk.ResponseType.OK:
            date_tuple = dialogue_win.calendar.get_date()

        dialogue_win.destroy()

        if response == Gtk.ResponseType.OK and date_tuple:

            year = str(date_tuple[0])           # e.g. 2011
            month = str(date_tuple[1] + 1)      # Values in range 0-11
            day = str(date_tuple[2])            # Values in range 1-31

            entry.set_text(
                year.zfill(4) + month.zfill(2) + day.zfill(2)
            )

        else:

            entry.set_text('')


    def on_clone_options_clicked(self, button):

        """Called by callback in self.setup_name_tab().

        Args:

            button (Gtk.Button): The widget clicked

        """

        self.app_obj.dialogue_manager_obj.show_msg_dialogue(
            _(
            'This procedure cannot be reversed. Are you sure you want to' \
            + ' continue?',
            ),
            'question',
            'yes-no',
            self,           # Parent window is this window
            {
                'yes': 'clone_download_options_from_window',
                'data': [self, self.edit_obj],
            },
        )


    def on_cookies_set_button_clicked(self, button, entry):

        """Called by callback in self.setup_files_cookies_tab().

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Another widget to be modified by this function

        """

        # Prompt the user for a new file
        dialogue_win = self.app_obj.dialogue_manager_obj.show_file_chooser(
            _('Select the cookie jar file'),
            self,
            'open',
        )

        cookie_path = self.retrieve_val('cookies_path')

        if cookie_path == '':
            cookie_dir = self.app_obj.data_dir
        else:
            cookie_dir, cookie_file = os.path.split(cookie_path)

        dialogue_win.set_current_folder(cookie_dir)

        # Get the user's response
        response = dialogue_win.run()
        if response == Gtk.ResponseType.OK:
            new_path = dialogue_win.get_filename()

        dialogue_win.destroy()
        if response == Gtk.ResponseType.OK:

            self.edit_dict['cookies_path'] = new_path
            entry.set_text(new_path)


    def on_cookies_reset_button_clicked(self, button, entry):

        """Called by callback in self.setup_files_cookies_tab().

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Another widget to be modified by this function

        """

        self.edit_dict['cookies_path'] = ''
        entry.set_text(
            os.path.abspath(
                os.path.join(
                    self.app_obj.data_dir,
                    self.app_obj.cookie_file_name,
                ),
            ),
        )


    def on_embed_checkbutton_toggled(self, checkbutton):

        """Called by callback in self.setup_post_process_tab() or
        setup_subtitles_more_options_tab().

        The 'embed_subs' option appears in both the Formats and Subtitles tabs.
        When one widget is modified, we need to set the other widgets to match
        without starting an infinite loop of signal connects.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        prop = 'embed_subs'

        if checkbutton == self.embed_checkbutton2 \
        and self.embed_checkbutton is None:

            # An easy case; the Formats tab isn't visible, so there is only one
            #   widget to think about
            if not checkbutton.get_active():
                self.edit_dict[prop] = False
            else:
                self.edit_dict[prop] = True

        else:

            # We get around the infinite loop problem by setting the other
            #   checkbutton, if it's in the opposite state to this checkbutton
            flag = checkbutton.get_active()

            if checkbutton == self.embed_checkbutton:

                if self.embed_checkbutton2.get_active() != flag:
                    self.embed_checkbutton2.set_active(flag)
                elif not checkbutton.get_active():
                    self.edit_dict[prop] = False
                else:
                    self.edit_dict[prop] = True

            else:

                if self.embed_checkbutton.get_active() != flag:
                    self.embed_checkbutton.set_active(flag)
                elif not checkbutton.get_active():
                    self.edit_dict[prop] = False
                else:
                    self.edit_dict[prop] = True


    def on_fixed_folder_changed(self, combo):

        """Called by callback in self.setup_files_filesystem_tab().

        Args:

            combo (Gtk.ComboBox): The widget clicked

        """

        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        pixbuf, name = model[tree_iter][:2]
        self.edit_dict['use_fixed_folder'] = name


    def on_fixed_folder_toggled(self, checkbutton, combo):

        """Called by callback in self.setup_files_filesystem_tab().

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            combo (Gtk.ComboBox): Another widget to be modified by this
                function

        """

        if not checkbutton.get_active():
            self.edit_dict['use_fixed_folder'] = None
            combo.set_sensitive(False)

        else:

            tree_iter = combo.get_active_iter()
            model = combo.get_model()
            pixbuf, name = model[tree_iter][:2]
            self.edit_dict['use_fixed_folder'] = name
            combo.set_sensitive(True)


    def on_file_tab_button_clicked(self, button, entry, combo, trans_dict):

        """Called by callback in self.setup_files_names_tab().

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Another widget to be modified by this function

            combo (Gtk.ComboBox): Another widget to be modified by this
                function

            trans_dict (dict): Converts a translated string into the string
                used by youtube-dl

        """

        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        label = trans_dict[model[tree_iter][0]]

        # (Code adapted from youtube-dl-gui's GeneralTab._on_template)
        if label == "ext":
            prefix = '.'
        else:
            prefix = '-'

        # If the output template is empty or ends with a file path separator,
        #   remove the prefix
        output_template = self.retrieve_val('output_template')
        if not output_template or output_template[-1] == os.sep:
            prefix = ''

        formatted = '{0}%({1})s'.format(prefix, label)
        # (Setting the entry updates self.edit_dict)
        entry.set_text(output_template + formatted)


    def on_file_tab_combo_changed(self, combo, entry):

        """Called by callback in self.setup_files_names_tab().

        Args:

            combo (Gtk.ComboBox): The widget clicked

            entry (Gtk.Entry): Another widget to be modified by this function

        """

        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        row_id, name = model[tree_iter][:2]

        self.edit_dict['output_format'] = row_id

        # The custom template is associated with the index 0
        if row_id == 0:
            self.file_tab_sensitise_widgets(True)
            entry.set_text(self.retrieve_val('output_template'))

        else:
            self.file_tab_sensitise_widgets(False)
            entry.set_text(formats.FILE_OUTPUT_CONVERT_DICT[row_id])


    def on_file_tab_entry_changed(self, entry):

        """Called by callback in self.setup_files_names_tab().

        Args:

            entry (Gtk.Entry): The widget clicked

        """

        # Only set 'output_template' when option 3 is selected, which is when
        #   the entry is sensitised
        if self.template_flag:
            self.edit_dict['output_template'] = entry.get_text()


    def on_formats_tab_add_clicked(self, add_button, remove_button, \
    up_button, down_button, treeview):

        """Called by callback in self.setup_formats_tab().

        Args:

            add_button (Gtk.Button): The widget clicked

            remove_button, up_button, down_button (Gtk.Button): Other widgets
                to be modified by this function

            treeview (Gtk.TreeView): The treeview on the left side of the tab

        """

        selection = treeview.get_selection()
        (model, iter) = selection.get_selected()
        if iter is None:

            # Nothing selected
            return

        else:

            name = model[iter][0]
            # Convert string e.g. 'mp4 [360p]' to the extractor code e.g. '18'
            extract_code = formats.VIDEO_OPTION_DICT[name]

        # Update the option
        format_list = self.retrieve_val('video_format_list')
        if extract_code in format_list:
            return
        else:
            format_list.append(extract_code)
            self.edit_dict['video_format_list'] = format_list

        # Update the other treeview, adding the format to it (and don't modify
        #   this treeview)
        self.formats_liststore.append([name])

        # Update other widgets, as required
        remove_button.set_sensitive(True)
        up_button.set_sensitive(True)
        down_button.set_sensitive(True)


    def on_formats_tab_combo_changed(self, combo):

        """Called by callback in self.setup_formats_preferred_tab().

        Args:

            combo (Gtk.ComboBox): The widget clicked

        """

        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        val = model[tree_iter][0]

        self.edit_dict['merge_output_format'] = val

        # For some reason, this youtube-dl download option doesn't work if the
        #   specified format (e.g. 'mp4') isn't also specified in the list of
        #   preferred formats
        # Warn the user about that, where appropriate
        format_list = self.retrieve_val('video_format_list')
        if val != '' and not val in format_list:

            self.app_obj.dialogue_manager_obj.show_msg_dialogue(
                _(
                'This option won\'t work unless the format is also added to' \
                + ' the list of preferred formats above',
                ),
                'warning',
                'ok',
                self,           # Parent window is this window
            )


    def on_formats_tab_down_clicked(self, down_button, treeview):

        """Called by callback in self.setup_formats_tab().

        Args:

            down_button (Gtk.Button): The widget clicked

            treeview (Gtk.TreeView): Another widget to be modified by this
                function

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        if not path_list:

            # Nothing selected
            return

        else:

            this_iter = model.get_iter(path_list[0])
            name = model[this_iter][0]
            # Convert string e.g. 'mp4 [360p]' to the extractor code e.g. '18'
            extract_code = formats.VIDEO_OPTION_DICT[name]

        # Update the option
        format_list = self.retrieve_val('video_format_list')
        if extract_code in format_list:

            index = format_list.index(extract_code)
            if index < (len(format_list) - 1):
                format_list.remove(extract_code)
                format_list.insert((index + 1), extract_code)

                self.edit_dict['video_format_list'] = format_list

                # Update the other treeview
                this_path = path_list[0]
                next_path = this_path[0]+1
                model.move_after(
                    model.get_iter(this_path),
                    model.get_iter(next_path),
                )


    def on_formats_tab_remove_clicked(self, remove_button, add_button, \
    up_button, down_button, other_treeview):

        """Called by callback in self.setup_formats_tab().

        Args:

            remove_button (Gtk.Button): The widget clicked

            add_button, up_button, down_button (Gtk.Button): Other widgets to
                be modified by this function

            other_treeview (Gtk.TreeView): The treeview on the right side of
                the tab

        """

        selection = other_treeview.get_selection()
        (model, iter) = selection.get_selected()
        if iter is None:

            # Nothing selected
            return

        else:

            name = model[iter][0]
            # Convert string e.g. 'mp4 [360p]' to the extractor code e.g. '18'
            extract_code = formats.VIDEO_OPTION_DICT[name]

        # Update the option
        format_list = self.retrieve_val('video_format_list')
        if extract_code in format_list:
            format_list.remove(extract_code)

            self.edit_dict['video_format_list'] = format_list

            # Update the right-hand side treeview
            model.remove(iter)

            # Update other widgets, as required
            add_button.set_sensitive(True)
            if not format_list:

                # No formats left to remove
                remove_button.set_sensitive(False)
                up_button.set_sensitive(False)
                down_button.set_sensitive(False)


    def on_formats_tab_up_clicked(self, up_button, treeview):

        """Called by callback in self.setup_formats_tab().

        Args:

            button (Gtk.Button): The widget clicked

            treeview (Gtk.TreeView): Another widget to be modified by this
                function

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        if not path_list:

            # Nothing selected
            return

        else:

            this_iter = model.get_iter(path_list[0])
            name = model[this_iter][0]
            # Convert string e.g. 'mp4 [360p]' to the extractor code e.g. '18'
            extract_code = formats.VIDEO_OPTION_DICT[name]

        # Update the option
        format_list = self.retrieve_val('video_format_list')
        if extract_code in format_list:

            index = format_list.index(extract_code)
            if index > 0:
                format_list.remove(extract_code)
                format_list.insert((index - 1), extract_code)

                self.edit_dict['video_format_list'] = format_list

                # Update the other treeview
                this_path = path_list[0]
                prev_path = this_path[0]-1
                model.move_before(
                    model.get_iter(this_path),
                    model.get_iter(prev_path),
                )


    def on_reset_options_clicked(self, button):

        """Called by callback in self.setup_name_tab().

        Args:

            button (Gtk.Button): The widget clicked

        """

        self.app_obj.dialogue_manager_obj.show_msg_dialogue(
            _(
            'This procedure cannot be reversed. Are you sure you want to' \
            + ' continue?',
            ),
            'question',
            'yes-no',
            self,           # Parent window is this window
            {
                'yes': 'reset_download_options',
                # (Reset this edit window, if the user clicks 'yes')
                'data': [self],
            },
        )


    def on_simple_options_clicked(self, button):

        """Called by callback in self.setup_general_tab().

        Args:

            button (Gtk.Button): The widget clicked

        """

        if not self.app_obj.simple_options_flag:

            self.app_obj.set_simple_options_flag(True)

            if not self.edit_dict:
                # User has not changed any options, so redraw the window to
                #   show the same options.OptionsManager object
                self.reset_with_new_edit_obj(self.edit_obj)

            else:
                # User has already changed some options. We don't want to lose
                #   them, so wait for the window to close and be re-opened,
                #   before switching between simple/advanced options
                self.app_obj.dialogue_manager_obj.show_msg_dialogue(
                    _(
                    'Fewer download options will be visible when you click' \
                    + ' the \'Apply\' or \'Reset\' buttons (or when you' \
                    + ' close and then re-open the window)',
                    ),
                    'info',
                    'ok',
                    self,           # Parent window is this window
                )

                button.set_label(
                    _('Show advanced download options (when window re-opens)'),
                )

        else:

            self.app_obj.set_simple_options_flag(False)

            if not self.edit_dict:
                self.reset_with_new_edit_obj(self.edit_obj)

            else:
                self.app_obj.dialogue_manager_obj.show_msg_dialogue(
                    _(
                    'More download options will be visible when you click' \
                    + ' the \'Apply\' or \'Reset\' buttons (or when you' \
                    + ' close and then re-open the window)',
                    ),
                    'info',
                    'ok',
                    self,           # Parent window is this window
                )

                button.set_label(
                    _('Hide advanced download options (when window re-opens)'),
                )


    def on_sleep_button_changed(self, spinbutton, spinbutton2):

        """Called by callback in self.setup_advanced_workaround_tab().

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

            spinbutton2 (Gtk.SpinButton2): Another widget to update

        """

        value = int(spinbutton.get_value())

        self.edit_dict['min_sleep_interval'] = value
        if value == 0:
            spinbutton2.set_value(0)
            spinbutton2.set_sensitive(False)
        else:
            spinbutton2.set_sensitive(True)


    def on_subtitles_tab_add_clicked(self, button, treeview, other_liststore,
    rev_dict):

        """Called by callback in self.setup_subtitles_options_tab().

        Args:

            button (Gtk.Button): The widget clicked

            treeview (Gtk.TreeView): The treeview on the left side of the tab

            other_liststore (Gtk.ListStore): The liststore belonging to the
                treeview on the right side of the tab

            rev_dict (dict): A reversed formats.LANGUAGE_CODE_DICT

        """

        selection = treeview.get_selection()
        (model, iter) = selection.get_selected()
        if iter is None:

            # Nothing selected
            return

        else:

            lang_name = model[iter][0]
            # Convert a language to its ISO 639-1 Language Code, e.g. convert
            #   'English' to 'en'
            lang_code = formats.LANGUAGE_CODE_DICT[lang_name]

            # Retrieve the existing list of languages
            lang_code_list = self.retrieve_val('subs_lang_list')
            if not lang_code in lang_code_list:

                lang_code_list.append(lang_code)

            # Sort by language name, not by language code
            lang_list = []
            mod_code_list = []
            for this_code in lang_code_list:
                lang_list.append(rev_dict[this_code])

            lang_list.sort()
            for this_lang in lang_list:
                mod_code_list.append(formats.LANGUAGE_CODE_DICT[this_lang])

            # Update the option...
            self.edit_dict['subs_lang_list'] = mod_code_list
            # ...and the textview
            other_liststore.clear()
            for this_lang in lang_list:
                other_liststore.append([this_lang])


    def on_subtitles_tab_remove_clicked(self, button, other_treeview,
    other_liststore, rev_dict):

        """Called by callback in self.setup_subtitles_options_tab().

        Args:

            button (Gtk.Button): The widget clicked

            other_treeview (Gtk.TreeView): The treeview on the right side of
                the tab

            other_liststore (Gtk.ListStore): The liststore belonging to that
                treeview

            rev_dict (dict): A reversed formats.LANGUAGE_CODE_DICT

        """

        selection = other_treeview.get_selection()
        (model, iter) = selection.get_selected()
        if iter is None:

            # Nothing selected
            return

        else:

            lang_name = model[iter][0]
            # Convert a language to its ISO 639-1 Language Code, e.g. convert
            #   'English' to 'en'
            lang_code = formats.LANGUAGE_CODE_DICT[lang_name]

            # Retrieve the existing list of languages
            lang_code_list = self.retrieve_val('subs_lang_list')
            if lang_code in lang_code_list:

                lang_code_list.remove(lang_code)

            # Sort by language name, not by language code
            lang_list = []
            mod_code_list = []
            for this_code in lang_code_list:
                lang_list.append(rev_dict[this_code])

            lang_list.sort()
            for this_lang in lang_list:
                mod_code_list.append(formats.LANGUAGE_CODE_DICT[this_lang])

            # Update the option...
            self.edit_dict['subs_lang_list'] = mod_code_list
            # ...and the textview
            other_liststore.clear()
            for this_lang in lang_list:
                other_liststore.append([this_lang])


    def on_subtitles_toggled(self, radiobutton, button, button2, prop):

        """Called by callback in self.setup_subtitles_options_tab().

        Args:

            radiobutton (Gtk.RadioButton): The widget clicked

            button, button2 (Gtk.Button): Other widgets to be modified by this
                function

            prop (str): The attribute in self.edit_dict to modify

        """

        if radiobutton.get_active():

            if prop == 'write_subs':
                self.edit_dict['write_subs'] = False
                self.edit_dict['write_auto_subs'] = False
                self.edit_dict['write_all_subs'] = False
                button.set_sensitive(False)
                button2.set_sensitive(False)

            elif prop == 'write_auto_subs':
                self.edit_dict['write_subs'] = True
                self.edit_dict['write_auto_subs'] = True
                self.edit_dict['write_all_subs'] = False
                button.set_sensitive(False)
                button2.set_sensitive(False)

            elif prop == 'write_all_subs':
                self.edit_dict['write_subs'] = True
                self.edit_dict['write_auto_subs'] = False
                self.edit_dict['write_all_subs'] = True
                button.set_sensitive(False)
                button2.set_sensitive(False)

            elif prop == 'subs_lang':
                self.edit_dict['write_subs'] = True
                self.edit_dict['write_auto_subs'] = False
                self.edit_dict['write_all_subs'] = False
                button.set_sensitive(True)
                button2.set_sensitive(True)


    def on_video_format_mode_toggled(self, radiobutton, value):

        """Called by callback in self.setup_formats_advanced_tab().

        Args:

            radiobutton (Gtk.RadioButton): The widget clicked

            prop (str): The attribute in self.edit_dict to modify

        """

        if radiobutton.get_active():
            self.edit_dict['video_format_mode'] = value


class FFmpegOptionsEditWin(GenericEditWin):

    """Python class for an 'edit window' to modify values in an
    ffmpeg_tartube.FFmpegOptionsManager object.

    Adapted from FFmpeg Command Line Wizard, by AndreKR
        (https://github.com/AndreKR/ffmpeg-command-line-wizard).

    Args:

        app_obj (mainapp.TartubeApp): The main application object

        edit_obj (ffmpeg_tartube.FFmpegOptionsManager): The object whose
            attributes will be edited in this window

        video_list (list): An optional list of media.Video objects. If not
            empty, when the edit window closes, a process operation will
            start, using the FFmpeg options specified by 'edit_obj' to process
            all the videos in the list. If empty, no operation is started; the
            modified FFmpeg options are just updated as normal

    """


    # Standard class methods


    def __init__(self, app_obj, edit_obj, video_list=[]):

        Gtk.Window.__init__(self, title=_('FFmpeg options'))

        if self.is_duplicate(app_obj, edit_obj):
            return

        # IV list - class objects
        # -----------------------
        # The mainapp.TartubeApp object
        self.app_obj = app_obj
        # The ffmpeg_tartube.FFmpegOptionsManager object being edited
        self.edit_obj = edit_obj
        # An optional list of media.Video objects. If not empty, when the edit
        #   window closes, a process operation will start, using the FFmpeg
        #   options specified by 'edit_obj' to process all the videos in the
        #   list. If empty, no operation is started; the modified FFmpeg
        #   options are just updated as normal
        self.video_list = video_list


        # IV list - Gtk widgets
        # ---------------------
        self.grid = None                        # Gtk.Grid
        self.notebook = None                    # Gtk.Notebook
        self.reset_button = None                # Gtk.Button
        self.apply_button = None                # Gtk.Button
        self.ok_button = None                   # Gtk.Button
        self.cancel_button = None               # Gtk.Button
        # (Because of the need to (de)sensitise widgets so often, more of them
        #   than usual have their own IVs)
        # (Name tab)
        self.extra_cmd_string_textview = None   # Gtk.TextView
        self.extra_cmd_string_textbuffer = None # Gtk.TextBuffer
        self.result_textview = None             # Gtk.TextView
        self.results_textbuffer = None          # Gtk.TextBuffer
        # (File tab)
        self.add_end_filename_entry = None      # Gtk.Entry
        self.regex_match_filename_entry = None  # Gtk.Entry
        self.regex_apply_subst_entry = None     # Gtk.Entry
        self.rename_both_flag_checkbutton = None
                                                # Gtk.CheckButton
        self.change_file_ext_entry = None       # Gtk.Entry
        self.delete_original_flag_checkbutton = None
                                                # Gtk.CheckButton
        # (Settings tab)
        self.input_mode_radiobutton = None      # Gtk.RadioButton
        self.input_mode_radiobutton2 = None     # Gtk.RadioButton
        self.audio_flag_checkbutton = None      # Gtk.CheckButton
        self.output_mode_radiobutton = None     # Gtk.RadioButton
        self.output_mode_radiobutton2 = None    # Gtk.RadioButton
        self.output_mode_radiobutton3 = None    # Gtk.RadioButton
        self.output_mode_radiobutton4 = None    # Gtk.RadioButton
        self.h264_grid = None                   # Gtk.Grid
        self.gif_grid = None                    # Gtk.Grid
        self.merge_grid = None                  # Gtk.Grid
        self.thumb_grid = None                  # Gtk.Grid
        # (Settings tab, H.264 grid)
        self.audio_bitrate_spinbutton = None    # Gtk.SpinButton
        self.quality_mode_radiobutton = None    # Gtk.RadioButton
        self.quality_mode_radiobutton2 = None   # Gtk.RadioButton
        self.rate_factor_scale = None           # Gtk.Scale
        self.dummy_file_combo = None            # Gtk.ComboBox
        self.patience_preset_combo = None       # Gtk.ComboBox
        self.gpu_encoding_combo = None          # Gtk.ComboBox
        self.hw_accel_combo = None              # Gtk.ComboBox
        # (Settings tab, GIF grid)
        self.palette_mode_radiobutton = None    # Gtk.RadioButton
        self.palette_mode_radiobutton2 = None   # Gtk.RadioButton
        # (Optimise tab)
        self.seek_flag_checkbutton = None       # Gtk.CheckButton
        self.tuning_film_flag_checkbutton = None
                                                # Gtk.CheckButton
        self.tuning_animation_flag_checkbutton = None
                                                # Gtk.CheckButton
        self.tuning_grain_flag_checkbutton = None
                                                # Gtk.CheckButton
        self.tuning_still_image_flag_checkbutton = None
                                                # Gtk.CheckButton
        self.tuning_fast_decode_flag_checkbutton = None
                                                # Gtk.CheckButton
        self.profile_flag_checkbutton = None    # Gtk.CheckButton
        self.fast_start_flag_checkbutton = None # Gtk.CheckButton
        self.tuning_zero_latency_flag_checkbutton = None
                                                # Gtk.CheckButton
        self.limit_flag_checkbutton = None      # Gtk.CheckButton
        self.limit_mbps_spinbutton = None       # Gtk.SpinButton
        self.limit_buffer_spinbutton = None     # Gtk.SpinButton
        # (Videox tab)
        self.video_liststore = None              # Gtk.ListStore

        # IV list - other
        # ---------------
        # Size (in pixels) of gaps between edit window widgets
        self.spacing_size = self.app_obj.default_spacing_size
        # Flag set to True if all four buttons ('Reset', 'Apply', 'Cancel' and
        #   'OK') are required, or False if just the 'OK' button is required
        self.multi_button_flag = True

        # When the user changes a value, it is not applied to self.edit_obj
        #   immediately; instead, it is stored temporarily in this dictionary
        # If the user clicks the 'OK' or 'Apply' buttons at the bottom of the
        #   window, the changes are applied to self.edit_obj
        # If the user clicks the 'Reset' or 'Cancel' buttons, the dictionary
        #   is emptied and the changes are lost
        # In this edit window, the key-value pairs directly correspond to those
        #   in ffmpeg_tartube.FFmpegOptionsManager.options_dict, rather than
        #   corresponding directly to attributes in the
        #   ffmpeg_tartube.FFmpegOptionsManager object
        # Because of that, we use our own .apply_changes() and .retrieve_val()
        #   functions, rather than relying on the generic functions
        # Key-value pairs are added to this dictionary whenever the user
        #   makes a change (so if no changes are made when the window is
        #   closed, the dictionary will still be empty)
        self.edit_dict = {}


        # Code
        # ----

        # Set up the edit window
        self.setup()


    # Public class methods


#   def is_duplicate():         # Inherited from GenericConfigWin


#   def setup():                # Inherited from GenericConfigWin


#   def setup_grid():           # Inherited from GenericConfigWin


#   def setup_notebook():       # Inherited from GenericConfigWin


#   def add_notebook_tab():     # Inherited from GenericConfigWin


#   def setup_button_strip():   # Inherited from GenericEditWin


#   def setup_gap():            # Inherited from GenericConfigWin


    # (Non-widget functions)


    def apply_changes(self, apply_button_flag=False):

        """Called by self.on_button_ok_clicked() and
        self.on_button_apply_clicked().

        Any changes the user has made are temporarily stored in self.edit_dict.
        Apply to those changes to the object being edited.

        In this edit window we apply changes to self.edit_obj.options_dict
        (rather than to self.edit_obj's attributes directly, as in the generic
        function.)

        Args:

            apply_button_flag (bool): True when self.apply_button was clicked,
                False when self.ok_button was clicked. When True, we do not
                start a process operation

        """

        # For 'change_file_ext', remove the initial . (e.g. in '.mp4', if
        #   specified
        if 'change_file_ext' in self.edit_dict:
            self.edit_dict['change_file_ext'] = re.sub(
                '^\.',
                '',
                self.edit_dict['change_file_ext'],
            )

        # Apply any changes the user has made
        for key in self.edit_dict.keys():

            if key in self.edit_obj.options_dict:
                self.edit_obj.options_dict[key] = self.edit_dict[key]

        # The name can also be updated, if it has been changed (but it the
        #   entry was blank, keep the old name)
        if 'name' in self.edit_dict \
        and self.edit_dict['name'] != '':
            self.edit_obj.name = self.edit_dict['name']

        # The changes can now be cleared
        self.edit_dict = {}

        # If a list of videos was supplied, start a process operation
        if self.video_list and not apply_button_flag:

            # Check that every media.Video object still exists, eliminating any
            #   that don't
            mod_list = []
            for video_obj in self.video_list:

                # (Special case: 'dummy' video objects (those downloaded in the
                #   Classic Mode tab) use different IVs)
                if video_obj.dummy_flag \
                or (
                    video_obj.dbid in self.app_obj.media_reg_dict \
                    and self.app_obj.media_reg_dict[video_obj.dbid] \
                    == video_obj
                ):
                    mod_list.append(video_obj)

            if mod_list:

                self.app_obj.process_manager_start(
                    self.edit_obj,
                    mod_list,
                )


    def retrieve_val(self, name):

        """Can be called by anything.

        Any changes the user has made are temporarily stored in self.edit_dict.

        In the generic function, each key corresponds to an attribute in the
        object being edited, self.edit_obj. In this window, it corresponds to a
        key in self.edit_obj.options_dict.

        If 'name' exists as a key in that dictionary, retrieve the
        corresponding value and return it. Otherwise, the user hasn't yet
        modified the value, so retrieve directly from the attribute in the
        object being edited.

        Args:

            name (str): The name of the attribute in the object being edited

        Returns:

            The original or modified value of that attribute.

        """

        if name in self.edit_dict:

            return self.edit_dict[name]

        elif name == 'uid' or name == 'name':

            return getattr(self.edit_obj, name)

        elif name in self.edit_obj.options_dict:

            return self.edit_obj.options_dict[name]

        else:

            return self.app_obj.system_error(
                405,
                'Unrecognised property name \'' + name + '\'',
            )


    # (Setup tabs)


    def setup_tabs(self):

        """Called by self.setup(), .on_button_apply_clicked() and
        .on_button_reset_clicked().

        Sets up the tabs for this edit window.
        """

        self.setup_name_tab()
        self.setup_file_tab()

        if not self.app_obj.ffmpeg_simple_options_flag:
            self.setup_settings_tab()
            self.setup_optimise_tab()

        self.setup_videos_tab()

        # Unusual step: if a list of media.Video objects to be processed has
        #   been supplied, use a different label for the OK button
        if self.video_list:

            self.ok_button.set_label(_('Process files'))
            self.ok_button.set_tooltip_text(
                _('Process the files with FFmpeg'),
            )
            self.ok_button.get_child().set_width_chars(15)


    def setup_name_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Name' tab.
        """

        tab, grid = self.add_notebook_tab(_('_Name'))

        grid_width = 4

        self.add_label(grid,
            _('Name for these FFmpeg options'),
            0, 0, 2, 1,
        )

        entry = self.add_entry(grid,
            'name',
            2, 0, 2, 1,
        )

        self.add_label(grid,
            _('Extra command line options (e.g. --help)'),
            0, 1, grid_width, 1,
        )

        self.extra_cmd_string_textview, \
        self.extra_cmd_string_textbuffer = self.add_textview(grid,
            'extra_cmd_string',
            0, 2, grid_width, 1,
        )

        self.add_label(grid,
            _('System command, based on all FFmpeg options in this window:'),
            0, 3, grid_width, 1,
        )

        self.result_textview, self.results_textbuffer = self.add_textview(grid,
            None,
            0, 4, grid_width, 1,
        )
        self.result_textview.set_editable(False)
        self.result_textview.set_can_focus(False)
        self.result_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        # (Set the system command, as it stands)
        self.update_system_cmd()

        if self.app_obj.simple_options_flag:
            frame = self.add_pixbuf(grid,
                'hand_right_large',
                0, 5, 1, 1,
            )
            frame.set_hexpand(False)

        else:
            frame = self.add_pixbuf(grid,
                'hand_left_large',
                0, 5, 1, 1,
            )
            frame.set_hexpand(False)

        button = Gtk.Button()
        grid.attach(button, 1, 5, (grid_width - 1), 1)
        if not self.app_obj.ffmpeg_simple_options_flag:
            button.set_label(_('Show fewer FFmpeg options'))
        else:
            button.set_label(_('Show more FFmpeg options'))
        button.connect('clicked', self.on_simple_options_clicked)

        frame2 = self.add_pixbuf(grid,
            'copy_large',
            0, 6, 1, 1,
        )
        frame2.set_hexpand(False)

        button2 = Gtk.Button(
            _('Import current FFmpeg options into this window'),
        )
        grid.attach(button2, 1, 6, (grid_width - 1), 1)
        button2.connect('clicked', self.on_clone_options_clicked)
        if self.edit_obj == self.app_obj.ffmpeg_options_obj:
            # No point cloning the current options manager into itself
            button2.set_sensitive(False)

        frame3 = self.add_pixbuf(grid,
            'warning_large',
            0, 7, 1, 1,
        )
        frame3.set_hexpand(False)

        button3 = Gtk.Button(
            _('Completely reset all FFmpeg options to their default values'),
        )
        grid.attach(button3, 1, 7, (grid_width - 1), 1)
        button3.connect('clicked', self.on_reset_options_clicked)


    def setup_file_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'File' tab.
        """

        tab, grid = self.add_notebook_tab(_('_File'))

        self.add_label(grid,
            _('Add to end of filename:'),
            0, 0, 1, 1,
        )

        self.add_end_filename_entry = self.add_entry(grid,
            'add_end_filename',
            1, 0, 1, 1,
        )

        self.add_label(grid,
            _('If regex matches filename:'),
            0, 1, 1, 1,
        )

        self.regex_match_filename_entry = self.add_entry(grid,
            None,
            1, 1, 1, 1,
        )
        self.regex_match_filename_entry.set_text(
            self.retrieve_val('regex_match_filename'),
        )
        # (Signal connect appears below)

        self.add_label(grid,
            _('...then apply substitution:'),
            0, 2, 1, 1,
        )

        self.regex_apply_subst_entry = self.add_entry(grid,
            'regex_apply_subst',
            1, 2, 1, 1,
        )
        if self.retrieve_val('regex_match_filename') == '':
            self.regex_apply_subst_entry.set_sensitive(False)

        self.rename_both_flag_checkbutton = self.add_checkbutton(grid,
            _(
            'If the video/audio file is renamed, also rename the thumbnail' \
            + ' (but not vice-versa)',
            ),
            'rename_both_flag',
            0, 3, 2, 1,
        )
        if self.retrieve_val('add_end_filename') == '' \
        and self.retrieve_val('regex_match_filename') == '':
            self.rename_both_flag_checkbutton.set_sensitive(False)

        self.add_label(grid,
            _('Change file extension:'),
            0, 4, 1, 1,
        )

        self.change_file_ext_entry = self.add_entry(grid,
            None,
            1, 4, 1, 1,
        )
        self.change_file_ext_entry.set_text(
            self.retrieve_val('change_file_ext'),
        )
        # (Signal connect appears below)

        self.delete_original_flag_checkbutton = self.add_checkbutton(grid,
            _('After changing the file extension, delete the original file'),
            'delete_original_flag',
            0, 5, 1, 1,
        )
        if self.retrieve_val('change_file_ext') == '':
            self.delete_original_flag_checkbutton.set_sensitive(False)

        # (Signal connects from above)
        self.regex_match_filename_entry.connect(
            'changed',
            self.on_regex_match_filename_entry_changed,
        )

        self.change_file_ext_entry.connect(
            'changed',
            self.on_change_file_ext_entry_changed,
        )


    def setup_settings_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Settings' tab.
        """

        tab, grid = self.add_notebook_tab(_('_Settings'))

        grid_width = 6
        self.settings_grid = grid

        # Input mode
        label = self.add_label(grid,
            '<u>' + _('Source file') + '</u>',
            0, 0, 1, 1,
        )
        label.set_hexpand(False)

        self.input_mode_radiobutton = self.add_radiobutton(grid,
            None,
            _('Downloaded video/audio'),
            None,
            None,
            1, 0, 2, 1,
        )
        self.input_mode_radiobutton.set_hexpand(False)
        # (Signal connect appears below)

        self.audio_flag_checkbutton = self.add_checkbutton(grid,
            _('with audio'),
            None,
            3, 0, 1, 1,
        )
        self.audio_flag_checkbutton.set_hexpand(False)
        if self.retrieve_val('audio_flag'):
            self.audio_flag_checkbutton.set_active(True)
        if self.retrieve_val('input_mode') != 'video':
            self.audio_flag_checkbutton.set_sensitive(False)
        # (Signal connect appears below)

        self.input_mode_radiobutton2 = self.add_radiobutton(grid,
            self.input_mode_radiobutton,
            _('Video thumbnail'),
            None,
            None,
            4, 0, 1, 1,
        )
        self.input_mode_radiobutton2.set_hexpand(False)
        if self.retrieve_val('input_mode') == 'thumb':
            self.input_mode_radiobutton2.set_active(True)
        # (Signal connect appears below)

        # (Empty label for spacing)
        label2 = self.add_label(grid,
            '',
            5, 0, 1, 1,
        )
        label2.set_hexpand(True)

        # Output mode
        label3 = self.add_label(grid,
            '<u>' + _('Output file') + '</u>',
            0, 1, 1, 1,
        )
        label3.set_hexpand(False)

        self.output_mode_radiobutton = self.add_radiobutton(grid,
            None,
            'H.264',
            None,
            None,
            1, 1, 1, 1,
        )
        self.output_mode_radiobutton.set_hexpand(False)
        # (Signal connect appears below)

        self.output_mode_radiobutton2 = self.add_radiobutton(grid,
            self.output_mode_radiobutton,
            'GIF',
            None,
            None,
            2, 1, 1, 1,
        )
        self.output_mode_radiobutton2.set_hexpand(False)
        if self.retrieve_val('output_mode') == 'gif':
            self.output_mode_radiobutton2.set_active(True)
        # (Signal connect appears below)

        self.output_mode_radiobutton3 = self.add_radiobutton(grid,
            self.output_mode_radiobutton2,
            'Merge video/audio',
            None,
            None,
            3, 1, 1, 1,
        )
        self.output_mode_radiobutton3.set_hexpand(False)
        if self.retrieve_val('output_mode') == 'merge':
            self.output_mode_radiobutton3.set_active(True)
        # (Signal connect appears below)

        self.output_mode_radiobutton4 = self.add_radiobutton(grid,
            self.output_mode_radiobutton3,
            'Video thumbnail',
            None,
            None,
            4, 1, 1, 1,
        )
        self.output_mode_radiobutton4.set_hexpand(False)
        if self.retrieve_val('output_mode') == 'thumb':
            self.output_mode_radiobutton4.set_active(True)
        # (Signal connect appears below)

        # Supplementary grids: one for each 'output_mode'
        # Only one of them is visible at any time (this saves a lot of time
        #   (de)sensitising widgets
        self.h264_grid = self.setup_settings_tab_h264_grid(2, grid_width)
        self.gif_grid = self.setup_settings_tab_gif_grid(2, grid_width)
        self.merge_grid = self.setup_settings_tab_merge_grid(2, grid_width)
        self.thumb_grid = self.setup_settings_tab_thumb_grid(2, grid_width)

        # (Signal connects from above)
        self.input_mode_radiobutton.connect(
            'toggled',
            self.on_input_mode_radiobutton_toggled,
        )
        self.audio_flag_checkbutton.connect(
            'toggled',
            self.on_audio_flag_checkbutton_toggled,
        )
        self.input_mode_radiobutton2.connect(
            'toggled',
            self.on_input_mode_radiobutton_toggled,
        )

        self.output_mode_radiobutton.connect(
            'toggled',
            self.on_output_mode_radiobutton_toggled,
            grid_width,
        )
        self.output_mode_radiobutton2.connect(
            'toggled',
            self.on_output_mode_radiobutton_toggled,
            grid_width,
        )
        self.output_mode_radiobutton3.connect(
            'toggled',
            self.on_output_mode_radiobutton_toggled,
            grid_width,
        )
        self.output_mode_radiobutton4.connect(
            'toggled',
            self.on_output_mode_radiobutton_toggled,
            grid_width,
        )


    def setup_settings_tab_h264_grid(self, row, outer_width):

        """Called by self.setup_settings_tab().

        Creates a supplementary grid, within the tab's outer grid, which can be
        swapped in and out as the 'output_mode' option is changed.

        This supplementary grid is visible when 'output_mode' is 'h264'.

        Args:

            row (int): The row on the tab's outer grid, on which the
                supplementary grid is to be placed

            outer_width (int): The width of the tab's outer grid

        Return values:

            The new Gtk.Grid().

        """

        grid = Gtk.Grid()
        if self.retrieve_val('output_mode') == 'h264':
            self.settings_grid.attach(grid, 0, row, outer_width, 1)
        grid.set_border_width(self.spacing_size)
        grid.set_column_spacing(self.spacing_size)
        grid.set_row_spacing(self.spacing_size)

        inner_width = 3

        self.add_label(grid,
            _('Audio bitrate'),
            0, 0, 1, 1,
        )

        self.audio_bitrate_spinbutton = self.add_spinbutton(grid,
            16, None, 16,
            'audio_bitrate',
            1, 0, 1, 1,
        )
        if self.retrieve_val('input_mode') != 'video' \
        or not self.retrieve_val('audio_flag'):
            self.audio_bitrate_spinbutton.set_sensitive(False)

        label = self.add_label(grid,
            _('How to set the quality') + ' ⓘ',
            0, 1, 1, 1,
        )
        label.set_tooltip_text(
            _(
            'FFmpeg always encodes according to a Rate Factor that specifies' \
            + ' the quality of the result.',
            ) + '\n\n' + _(
            'Instead of directly specifying the Rate Factor, an average bit' \
            + ' rate can be specified. FFmpeg will then determine the' \
            + ' optimal Rate Factor in a first pass.',
            ) + '\n\n' + _(
            'In fact the first pass is only used for determining the Rate' \
            + ' Factor, no other data is carried over into the second pass.',
            ) + '\n\n' + _(
            'Specifying an average bitrate but running only one pass is' \
            + ' possible, but not recommended. FFmpeg would then encode the' \
            + ' beginning of the video with a random Rate Factor and then' \
            + ' change it near the end of the video to eventually reach the' \
            + ' target bitrate.',
            ),
        )

        # N.B. In the original 'FFmpeg command line wizard', the second of this
        #   pair of radiobuttons are disabled (for unknown reasons); here it is
        #   enabled
        self.quality_mode_radiobutton = self.add_radiobutton(grid,
            None,
            _('Manual rate factor'),
            None,
            None,
            1, 1, (inner_width - 1), 1,
        )
        # (Signal connect appears below)

        self.quality_mode_radiobutton2 = self.add_radiobutton(grid,
            self.quality_mode_radiobutton,
            _('Determine from target bitrate (2-Pass)'),
            None,
            None,
            1, 2, (inner_width - 1), 1,
        )
        if self.retrieve_val('quality_mode') == 'abr':
            self.quality_mode_radiobutton2.set_active(True)
        # (Signal connect appears below)

        self.add_label(grid,
            _('Rate factor'),
            0, 3, 1, 1,
        )

        # (Use yet another grid to avoid messing up the surrounding layout)
        grid2 = Gtk.Grid()
        grid.attach(grid2, 1, 3, (inner_width - 1), 1)
        grid2.set_border_width(self.spacing_size)
        grid2.set_column_spacing(self.spacing_size)
        grid2.set_row_spacing(self.spacing_size)

        label2 = self.add_label(grid2,
            _('Lossless') + '\n' + _('Large file'),
            0, 0, 1, 1,
        )
        label2.set_hexpand(False)

        self.rate_factor_scale = Gtk.Scale().new_with_range(
            Gtk.Orientation.HORIZONTAL,
            0,
            51,
            1,
        )
        grid2.attach(self.rate_factor_scale, 1, 0, 1, 1)
        self.rate_factor_scale.set_draw_value(True)
        self.rate_factor_scale.set_value(
            self.retrieve_val('rate_factor'),
        )
        self.rate_factor_scale.set_hexpand(True)
        if self.retrieve_val('quality_mode') == 'abr':
            self.rate_factor_scale.set_sensitive(False)
        # (Signal connect appears below)

        label3 = self.add_label(grid2,
            _('Bad quality') + '\n' + _('Small file'),
            2, 0, 1, 1,
        )
        label3.set_hexpand(False)
        # (End of the yet another grid)

        label4 = self.add_label(grid,
            _('Name of dummy file') + ' ⓘ',
            0, 4, 1, 1,
        )
        label4.set_tooltip_text(
            _('A dummy file is created during the first pass.'),
        )

        combo_list = [
            [_('Use the output file'), 'output'],
            [_('Dummy'), 'dummy'],
            [_('/dev/null (Linux)'), '/dev/null'],
            [_('NUL (MS Windows)'), 'NUL'],
        ]

        self.dummy_file_combo = self.add_combo_with_data(grid,
            combo_list,
            'dummy_file',
            1, 4, (inner_width - 1), 1,
        )
        if self.retrieve_val('quality_mode') != 'abr':
            self.dummy_file_combo.set_sensitive(False)

        self.add_label(grid,
            _('Patience preset'),
            0, 5, 1, 1,
        )

        combo_list2 = [
            [_('Ultra fast'), 'ultrafast'],
            [_('Super fast'), 'superfast'],
            [_('Very fast'), 'veryfast'],
            [_('Faster'), 'faster'],
            [_('Fast'), 'fast'],
            [_('Medium (default)'), 'medium'],
            [_('Slow (file about 5-10% smaller than medium)'), 'slow'],
            [_('Slower (file about 15% smaller than medium)'), 'slower'],
            [_('Very slow (file about 17% smaller than medium)'), 'veryslow'],
        ]

        self.patience_preset_combo = self.add_combo_with_data(grid,
            combo_list2,
            'patience_preset',
            1, 5, (inner_width - 1), 1,
        )
        self.patience_preset_combo.set_hexpand(False)

        self.add_label(grid,
            _('GPU encoding'),
            0, 6, 1, 1,
        )

        combo_list3 = [
            'libx264', 'libx265', 'h264_amf', 'hevc_amf', 'h264_nvenc',
            'hevc_nvenc',
        ]

        self.gpu_encoding_combo = self.add_combo(grid,
            combo_list3,
            'gpu_encoding',
            1, 6, (inner_width - 1), 1,
        )

        self.add_label(grid,
            _('Hardware acceleration'),
            0, 7, 1, 1,
        )

        combo_list4 = ['none', 'auto', 'vdpau', 'dxva2', 'vaapi', 'qsv']

        self.hw_accel_combo = self.add_combo(grid,
            combo_list4,
            'hw_accel',
            1, 7, (inner_width - 1), 1,
        )

        # (Signal connects from above)
        self.quality_mode_radiobutton.connect(
            'toggled',
            self.on_quality_mode_radiobutton_toggled,
        )
        self.quality_mode_radiobutton2.connect(
            'toggled',
            self.on_quality_mode_radiobutton_toggled,
        )

        self.rate_factor_scale.connect(
            'value-changed',
            self.on_rate_factor_scale_changed,
        )

        return grid


    def setup_settings_tab_gif_grid(self, row, outer_width):

        """Called by self.setup_settings_tab().

        Creates a supplementary grid, within the tab's outer grid, which can be
        swapped in and out as the 'output_mode' option is changed.

        This supplementary grid is visible when 'output_mode' is 'gif'.

        Args:

            row (int): The row on the tab's outer grid, on which the
                supplementary grid is to be placed

            outer_width (int): The width of the tab's outer grid

        Return values:

            The new Gtk.Grid().

        """

        grid = Gtk.Grid()
        if self.retrieve_val('output_mode') == 'gif':
            self.settings_grid.attach(grid, 0, row, outer_width, 1)
        grid.set_border_width(self.spacing_size)
        grid.set_column_spacing(self.spacing_size)
        grid.set_row_spacing(self.spacing_size)

        self.add_label(grid,
            _('Palette:'),
            0, 0, 1, 1,
        )

        self.palette_mode_radiobutton = self.add_radiobutton(grid,
            None,
            _('Faster') + '\n' \
            + _('Uses dithering to a standard palette provided by FFmpeg') \
            + '\n' + _('Can cause dithering artefacts and slight banding'),
            None,
            None,
            1, 0, 1, 1,
        )
        # (Signal connect appears below)

        self.palette_mode_radiobutton2 = self.add_radiobutton(grid,
            self.palette_mode_radiobutton,
            _('Better') + '\n' \
            + _('Determines an optimized palette for the video') + '\n' \
            + _('Uses two passes and a temporary file for the palette'),
            None,
            None,
            1, 1, 1, 1,
        )
        if self.retrieve_val('palette_mode') == 'better':
            self.palette_mode_radiobutton2.set_active(True)
        # (Signal connect appears below)

        # (Signal connects from above)
        self.palette_mode_radiobutton.connect(
            'toggled',
            self.on_palette_mode_radiobutton_toggled,
        )
        self.palette_mode_radiobutton2.connect(
            'toggled',
            self.on_palette_mode_radiobutton_toggled,
        )

        return grid


    def setup_settings_tab_merge_grid(self, row, outer_width):

        """Called by self.setup_settings_tab().

        Creates a supplementary grid, within the tab's outer grid, which can be
        swapped in and out as the 'output_mode' option is changed.

        This supplementary grid is visible when 'output_mode' is 'merge'.

        Args:

            row (int): The row on the tab's outer grid, on which the
                supplementary grid is to be placed

            outer_width (int): The width of the tab's outer grid

        Return values:

            The new Gtk.Grid().

        """

        grid = Gtk.Grid()
        if self.retrieve_val('output_mode') == 'merge':
            self.settings_grid.attach(grid, 0, row, outer_width, 1)
        grid.set_border_width(self.spacing_size)
        grid.set_column_spacing(self.spacing_size)
        grid.set_row_spacing(self.spacing_size)

        self.add_label(grid,
            '<i>' + _(
                'This merges a video and audio file with the same name' \
                + ' into a single video file,\nusing the extension' \
                + ' specified in the File tab',
            ) + '</i>',
            0, 0, 1, 1,
        )

        return grid


    def setup_settings_tab_thumb_grid(self, row, outer_width):

        """Called by self.setup_settings_tab().

        Creates a supplementary grid, within the tab's outer grid, which can be
        swapped in and out as the 'output_mode' option is changed.

        This supplementary grid is visible when 'output_mode' is 'thumb'.

        Args:

            row (int): The row on the tab's outer grid, on which the
                supplementary grid is to be placed

            outer_width (int): The width of the tab's outer grid

        Return values:

            The new Gtk.Grid().

        """

        grid = Gtk.Grid()
        if self.retrieve_val('output_mode') == 'thumb':
            self.settings_grid.attach(grid, 0, row, outer_width, 1)
        grid.set_border_width(self.spacing_size)
        grid.set_column_spacing(self.spacing_size)
        grid.set_row_spacing(self.spacing_size)

        self.add_label(grid,
            '<i>' + _(
                'The thumbnail\'s format can be changed in the File tab',
            ) + '</i>',
            0, 0, 1, 1,
        )

        return grid


    def setup_optimise_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Optimisations' tab.
        """

        tab, grid = self.add_notebook_tab(_('_Optimisations'))

        grid_width = 2

        self.seek_flag_checkbutton = self.add_checkbutton(grid,
            _(
                'Optimise for fast seeking (shorter keyframe interval, about' \
                + ' 10% larger file)',
            ),
            'seek_flag',
            0, 0, grid_width, 1,
        )

        self.tuning_film_flag_checkbutton = self.add_checkbutton(grid,
            _('Input video is a high-quality movie'),
            'tuning_film_flag',
            0, 1, grid_width, 1,
        )

        self.tuning_animation_flag_checkbutton = self.add_checkbutton(grid,
            _('Input video is an animated movie'),
            'tuning_animation_flag',
            0, 2, grid_width, 1,
        )

        self.tuning_grain_flag_checkbutton = self.add_checkbutton(grid,
            _('Input video contains film grain'),
            'tuning_grain_flag',
            0, 3, grid_width, 1,
        )

        self.tuning_still_image_flag_checkbutton = self.add_checkbutton(grid,
            _('Input video is an image slideshow'),
            'tuning_still_image_flag',
            0, 4, grid_width, 1,
        )

        self.tuning_fast_decode_flag_checkbutton = self.add_checkbutton(grid,
            _('Optimise for really weak CPU playback devices'),
            'tuning_fast_decode_flag',
            0, 5, grid_width, 1,
        )

        self.profile_flag_checkbutton = self.add_checkbutton(grid,
            _(
                'Optimise for really old devices (requires rate factor' \
                + ' above 0)',
            ),
            'profile_flag',
            0, 6, grid_width, 1,
        )
        if not self.retrieve_val('rate_factor'):
            self.profile_flag_checkbutton.set_sensitive(False)

        self.fast_start_flag_checkbutton = self.add_checkbutton(grid,
            _(
                'Move headers to beginning of file (so it can play while' \
                + ' still downloading)',
            ),
            'fast_start_flag',
            0, 7, grid_width, 1,
        )

        self.tuning_zero_latency_flag_checkbutton = self.add_checkbutton(grid,
            _('Fast encoding and low latency streaming'),
            'tuning_zero_latency_flag',
            0, 8, grid_width, 1,
        )

        self.limit_flag_checkbutton = self.add_checkbutton(grid,
            _('Limit bitrate (Mbit/s)'),
            None,
            0, 9, 1, 1,
        )
        if self.retrieve_val('limit_flag'):
            self.limit_flag_checkbutton.set_active(True)
        # (Signal connect appears below)

        self.limit_mbps_spinbutton = self.add_spinbutton(grid,
            0, None, 0.2,
            'limit_mbps',
            1, 9, 1, 1,
        )
        if not self.retrieve_val('limit_flag'):
            self.limit_mbps_spinbutton.set_sensitive(False)

        self.add_label(grid,
            '          ' + _('Assuming a receiving buffer (seconds)'),
            0, 10, 1, 1,
        )

        self.limit_buffer_spinbutton = self.add_spinbutton(grid,
            0, None, 0.2,
            'limit_buffer',
            1, 10, 1, 1,
        )
        if not self.retrieve_val('limit_flag'):
            self.limit_buffer_spinbutton.set_sensitive(False)

        # (De)sensitise all of these widgets, depending on the value of the
        #   'output_mode' setting
        if self.retrieve_val('output_mode') == 'h264':
            self.setup_optimise_tab_set_sensitive(True)
        else:
            self.setup_optimise_tab_set_sensitive(False)

        # (Signal connects from above)
        self.limit_flag_checkbutton.connect(
            'toggled',
            self.on_limit_flag_checkbutton_toggled,
        )


    def setup_optimise_tab_set_sensitive(self, sens_flag):

        """Called by self.setup_optimise_tab() and various callbacks.

        (De)sensitises all widgets in the tab, as required.

        Args:

            sens_flag (bool): True to sensitise widgets, False to desensitise
                them

        """

        self.seek_flag_checkbutton.set_sensitive(sens_flag)
        self.tuning_film_flag_checkbutton.set_sensitive(sens_flag)
        self.tuning_animation_flag_checkbutton.set_sensitive(sens_flag)
        self.tuning_grain_flag_checkbutton.set_sensitive(sens_flag)
        self.tuning_still_image_flag_checkbutton.set_sensitive(sens_flag)
        self.tuning_fast_decode_flag_checkbutton.set_sensitive(sens_flag)

        if not self.retrieve_val('rate_factor'):
            self.profile_flag_checkbutton.set_sensitive(False)
        else:
            self.profile_flag_checkbutton.set_sensitive(sens_flag)

        self.fast_start_flag_checkbutton.set_sensitive(sens_flag)

        self.limit_flag_checkbutton.set_sensitive(sens_flag)
        self.tuning_zero_latency_flag_checkbutton.set_sensitive(sens_flag)

        if not self.retrieve_val('limit_flag'):
            self.limit_mbps_spinbutton.set_sensitive(False)
        else:
            self.limit_mbps_spinbutton.set_sensitive(sens_flag)

        if not self.retrieve_val('limit_flag'):
            self.limit_buffer_spinbutton.set_sensitive(False)
        else:
            self.limit_buffer_spinbutton.set_sensitive(sens_flag)


    def setup_videos_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Videos' tab.
        """

        tab, grid = self.add_notebook_tab(_('_Videos'))

        # List of videos to be processed
        self.add_label(grid,
            '<u>' + _('List of videos to be processed') + '</u>',
            0, 0, 1, 1,
        )

        # (GenericConfigWin.add_treeview() doesn't support multiple columns, so
        #   we'll do everything ourselves)
        frame = Gtk.Frame()
        grid.attach(frame, 0, 1, 1, 1)

        scrolled = Gtk.ScrolledWindow()
        frame.add(scrolled)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)

        treeview = Gtk.TreeView()
        scrolled.add(treeview)
        treeview.set_headers_visible(True)

        for i, column_title in enumerate(
            [ '#', _('Video'), _('Thumbnail'), _('Name') ]
        ):
            if i == 1 or i == 2:
                renderer_toggle = Gtk.CellRendererToggle()
                column_toggle = Gtk.TreeViewColumn(
                    column_title,
                    renderer_toggle,
                    active=i,
                )
                treeview.append_column(column_toggle)
                column_toggle.set_resizable(False)
            else:
                renderer_text = Gtk.CellRendererText()
                column_text = Gtk.TreeViewColumn(
                    column_title,
                    renderer_text,
                    text=i,
                )
                treeview.append_column(column_text)
                column_text.set_resizable(True)

        self.video_liststore = Gtk.ListStore(str, bool, bool, str)
        treeview.set_model(self.video_liststore)

        # Allow drag and drop from the Video Catalogue, or an external
        #   application, hoping to receive full paths to a video/audio file
        #   and/or URLs, which are associated with a media.Video object
        scrolled.connect(
            'drag-data-received',
            self.on_video_drag_data_received,
        )
        # (Without this line, we get Gtk warnings on some systems)
        scrolled.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        # (Continuing)
        scrolled.drag_dest_set_target_list(None)
        scrolled.drag_dest_add_text_targets()

        # Initialise the list
        self.setup_videos_tab_update_treeview()

        # Add editing buttons
        button = Gtk.Button()
        grid.attach(button, 0, 2, 1, 1)
        button.set_label(_('Remove video from list'))
        button.connect(
            'clicked',
            self.on_video_remove_button_clicked,
            treeview,
        )


    def setup_videos_tab_update_treeview(self):

        """Called by self.setup_videos_tab().

        Fills or updates the treeview.

        """

        self.video_liststore.clear()

        # Sort the video list by .dbid (so the Videos tab looks nice)
        self.video_list.sort(key=lambda x: x.dbid)

        # Add a row for each video in the list
        for video_obj in self.video_list:
            self.setup_videos_tab_add_row(video_obj)


    def setup_videos_tab_add_row(self, video_obj):

        """Called by self.setup_videos_tab_update_treeview().

        Adds a row to the treeview for a specified media.Video object.

        Args:

            video_obj (media.Video): The video to add

        """

        if utils.find_thumbnail(self.app_obj, video_obj):
            thumb_flag = True
        else:
            thumb_flag = True

        if video_obj.dummy_flag:

            # Special case: 'dummy' video objects (those downloaded in the
            #   Classic Mode tab) use different IVs
            if video_obj.dummy_path is not None \
            and os.path.isfile(video_obj.dummy_path):
                dl_flag = True
            else:
                dl_flag = False

            self.video_liststore.append(
                [
                    'n/a',
                    dl_flag,
                    thumb_flag,
                    video_obj.dummy_path,
                ],
            )

        else:

            # All other media.Video objects
            self.video_liststore.append(
                [
                    str(video_obj.dbid),
                    video_obj.dl_flag,
                    thumb_flag,
                       video_obj.name,
                ],
            )


    # (Tab support functions)


    def update_system_cmd(self):

        """Called after any widget is manipulated.

        Updates the contents of the textview showing a specimen system command,
        incorporating the modified value.

        """

        # This particular call returns a list inside a tuple, for no obvious
        #   reason (and an identical call from ProcessManager.process_video()
        #   does not)
        # Don't know why, but the FFmpeg system command, as a list, is at
        #   [0][2])
        result_list = self.edit_obj.get_system_cmd(
            self.app_obj,
            None,           # Use a specimen source file
            self.edit_dict,
        ),

        if result_list:
            self.results_textbuffer.set_text(' '.join(result_list[0][2]))
        else:
            self.results_textbuffer.set_text('')


    # Callback class methods


    def on_audio_flag_checkbutton_toggled(self, checkbutton):

        """Called by callback in self.setup_settings_tab().

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if not checkbutton.get_active():

            self.edit_dict['audio_flag'] = False

            self.audio_bitrate_spinbutton.set_sensitive(False)

        else:

            self.edit_dict['audio_flag'] = True

            if self.retrieve_val('input_mode') == 'video':
                self.audio_bitrate_spinbutton.set_sensitive(True)
            else:
                self.audio_bitrate_spinbutton.set_sensitive(False)

        # Update the system command in the 'Name' tab
        self.update_system_cmd()


    def on_change_file_ext_entry_changed(self, entry):

        """Called by callback in self.setup_file_tab().

        Args:

            entry (Gtk.Entry): The widget clicked

        """

        value = entry.get_text()

        self.edit_dict['change_file_ext'] = value
        if value == '':

            self.delete_original_flag_checkbutton.set_active(False)
            self.delete_original_flag_checkbutton.set_sensitive(False)

        else:
            self.delete_original_flag_checkbutton.set_sensitive(True)


        # Update the system command in the 'Name' tab
        self.update_system_cmd()


    def on_clone_options_clicked(self, button):

        """Called by callback in self.setup_name_tab().

        Args:

            button (Gtk.Button): The widget clicked

        """

        self.app_obj.dialogue_manager_obj.show_msg_dialogue(
            _(
            'This procedure cannot be reversed. Are you sure you want to' \
            + ' continue?',
            ),
            'question',
            'yes-no',
            self,           # Parent window is this window
            {
                'yes': 'clone_ffmpeg_options_from_window',
                'data': [self, self.edit_obj],
            },
        )


    def on_input_mode_radiobutton_toggled(self, radiobutton):

        """Called by callback in self.setup_settings_tab().

        Args:

            radiobutton (Gtk.RadioButton): The widget clicked

        """

        if self.input_mode_radiobutton.get_active():

            self.edit_dict['input_mode'] = 'video'

            self.output_mode_radiobutton.set_active(True)
            self.output_mode_radiobutton.set_sensitive(True)
            self.output_mode_radiobutton2.set_sensitive(True)
            self.output_mode_radiobutton3.set_sensitive(True)
            self.output_mode_radiobutton4.set_sensitive(False)

            self.audio_flag_checkbutton.set_sensitive(True)
            if not self.retrieve_val('audio_flag'):
                self.audio_bitrate_spinbutton.set_sensitive(False)
            else:
                self.audio_bitrate_spinbutton.set_sensitive(True)

        else:

            self.edit_dict['input_mode'] = 'thumb'

            self.output_mode_radiobutton4.set_active(True)
            self.output_mode_radiobutton.set_sensitive(False)
            self.output_mode_radiobutton2.set_sensitive(False)
            self.output_mode_radiobutton3.set_sensitive(False)
            self.output_mode_radiobutton4.set_sensitive(True)

            self.audio_flag_checkbutton.set_sensitive(False)
            self.audio_bitrate_spinbutton.set_sensitive(False)

        # Update the system command in the 'Name' tab
        self.update_system_cmd()


    def on_limit_flag_checkbutton_toggled(self, checkbutton):

        """Called by callback in self.setup_optimise_tab().

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if not checkbutton.get_active():

            self.edit_dict['limit_flag'] = False

            self.limit_mbps_spinbutton.set_sensitive(False)
            self.limit_buffer_spinbutton.set_sensitive(False)

        else:

            self.edit_dict['audio_flag'] = True

            self.limit_mbps_spinbutton.set_sensitive(True)
            self.limit_buffer_spinbutton.set_sensitive(True)

        # Update the system command in the 'Name' tab
        self.update_system_cmd()


    def on_output_mode_radiobutton_toggled(self, radiobutton, grid_width):

        """Called by callback in self.setup_settings_tab().

        Args:

            radiobutton (Gtk.RadioButton): The widget clicked

            grid_width (int): The width of self.settings_grid

        """

        old_value = self.retrieve_val('output_mode')
        if old_value == 'h264':
            self.settings_grid.remove(self.h264_grid)
        elif old_value == 'gif':
            self.settings_grid.remove(self.gif_grid)
        elif old_value == 'merge':
            self.settings_grid.remove(self.merge_grid)
        else:
            self.settings_grid.remove(self.thumb_grid)

        if self.output_mode_radiobutton.get_active():

            self.edit_dict['output_mode'] = 'h264'

            self.settings_grid.attach(self.h264_grid, 0, 2, grid_width, 1)
            self.setup_optimise_tab_set_sensitive(True)

        elif self.output_mode_radiobutton2.get_active():

            self.edit_dict['output_mode'] = 'gif'

            self.settings_grid.attach(self.gif_grid, 0, 2, grid_width, 1)
            self.setup_optimise_tab_set_sensitive(False)

        elif self.output_mode_radiobutton3.get_active():

            self.edit_dict['output_mode'] = 'merge'

            self.settings_grid.attach(self.merge_grid, 0, 2, grid_width, 1)
            self.setup_optimise_tab_set_sensitive(False)

        elif self.output_mode_radiobutton4.get_active():

            self.edit_dict['output_mode'] = 'thumb'

            self.settings_grid.attach(self.thumb_grid, 0, 2, grid_width, 1)
            self.setup_optimise_tab_set_sensitive(False)

        self.show_all()

        # Update the system command in the 'Name' tab
        self.update_system_cmd()


    def on_palette_mode_radiobutton_toggled(self, radiobutton):

        """Called by callback in self.setup_settings_tab_gif_grid().

        Args:

            radiobutton (Gtk.RadioButton): The widget clicked

        """

        if self.palette_mode_radiobutton.get_active():
            self.edit_dict['palette_mode'] = 'faster'
        else:
            self.edit_dict['palette_mode'] = 'better'

        # Update the system command in the 'Name' tab
        self.update_system_cmd()


    def on_quality_mode_radiobutton_toggled(self, radiobutton):

        """Called by callback in self.setup_settings_tab_h264_grid().

        Args:

            radiobutton (Gtk.RadioButton): The widget clicked

        """

        if self.quality_mode_radiobutton.get_active():

            self.edit_dict['quality_mode'] = 'crf'

            self.rate_factor_scale.set_sensitive(True)
            self.dummy_file_combo.set_sensitive(False)

        else:

            self.edit_dict['quality_mode'] = 'abr'

            self.rate_factor_scale.set_sensitive(False)
            self.dummy_file_combo.set_sensitive(True)

        # Update the system command in the 'Name' tab
        self.update_system_cmd()


    def on_rate_factor_scale_changed(self, scale):

        """Called by callback in self.setup_settings_tab_h264_grid().

        Args:

            scale (Gtk.Scale): The widget clicked

        """

        value = int(self.rate_factor_scale.get_value())

        self.edit_dict['rate_factor'] = value

        if not value:
            self.profile_flag_checkbutton.set_sensitive(False)
        else:
            self.profile_flag_checkbutton.set_sensitive(True)

        # Update the system command in the 'Name' tab
        self.update_system_cmd()


    def on_regex_match_filename_entry_changed(self, entry):

        """Called by callback in self.setup_file_tab().

        Args:

            entry (Gtk.Entry): The widget clicked

        """

        value = entry.get_text()

        self.edit_dict['regex_match_filename'] = value
        if value == '':

            self.regex_apply_subst_entry.set_text('')
            self.regex_apply_subst_entry.set_sensitive(False)

        else:

            self.regex_apply_subst_entry.set_sensitive(True)

        # Update the system command in the 'Name' tab
        self.update_system_cmd()


    def on_reset_options_clicked(self, button):

        """Called by callback in self.setup_name_tab().

        Args:

            button (Gtk.Button): The widget clicked

        """

        self.app_obj.dialogue_manager_obj.show_msg_dialogue(
            _(
            'This procedure cannot be reversed. Are you sure you want to' \
            + ' continue?',
            ),
            'question',
            'yes-no',
            self,           # Parent window is this window
            {
                'yes': 'reset_ffmpeg_options',
                # (Reset this edit window, if the user clicks 'yes')
                'data': [self],
            },
        )


    def on_simple_options_clicked(self, button):

        """Called by callback in self.setup_name_tab().

        Args:

            button (Gtk.Button): The widget clicked

        """

        redraw_flag = False
        if not self.app_obj.ffmpeg_simple_options_flag:

            self.app_obj.set_ffmpeg_simple_options_flag(True)

            if not self.edit_dict:

                # User has not changed any options, so redraw the window to
                #   show the same options.OptionsManager object
                self.reset_with_new_edit_obj(self.edit_obj)

            else:

                # User has already changed some options. We don't want to lose
                #   them, so wait for the window to close and be re-opened,
                #   before switching between simple/advanced options
                redraw_flag = True

                self.app_obj.dialogue_manager_obj.show_msg_dialogue(
                    _(
                    'Fewer FFmpeg options will be visible when you click the' \
                    + ' \'Apply\' or \'Reset\' buttons (or when you close' \
                    + ' and then re-open the window)',
                    ),
                    'info',
                    'ok',
                    self,           # Parent window is this window
                )

                button.set_label(
                    _('Show more FFmpeg options (when window re-opens)'),
                )

        else:

            self.app_obj.set_ffmpeg_simple_options_flag(False)

            if not self.edit_dict:

                self.reset_with_new_edit_obj(self.edit_obj)

            else:

                redraw_flag = True

                self.app_obj.dialogue_manager_obj.show_msg_dialogue(
                    _(
                    'More FFmpeg options will be visible when you click the' \
                    + ' \'Apply\' or \'Reset\' buttons (or when you close' \
                    + ' and then re-open the window)',
                    ),
                    'info',
                    'ok',
                    self,           # Parent window is this window
                )

                button.set_label(
                    _('Show fewer FFmpeg options (when window re-opens)'),
                )

        if redraw_flag:

            # Discard the list of videos, so that this becomes an ordinary
            #   edit window, with an 'OK' button that stores changes (and no
            #   'Process files' button that starts a process operation)
            self.video_list = []

            self.ok_button.set_label(_('OK'))
            self.ok_button.get_child().set_width_chars(10)
            self.ok_button.set_tooltip_text(
                _('Apply changes'),
            )


    def on_video_drag_data_received(self, widget, context, x, y, data, info,
    time):

        """Called from callback in self.setup_videos_tab().

        This function is required for detecting when the user drags and drops
        data into the Videos Tab.

        If the data contains full paths to a video/audio file and/or URLs,
        then we can search the media data registry, looking for matching
        media.Video objects.

        Those objects can then be added to self.video_list.

        Args:

            widget (mainwin.MainWin): The widget into which something has been
                dragged

            drag_context (GdkX11.X11DragContext): Data from the drag procedure

            x, y (int): Where the drop happened

            data (Gtk.SelectionData): The object to be filled with drag data

            info (int): Info that has been registered with the target in the
                Gtk.TargetList

            time (int): A timestamp

        """

        text = None
        if info == 0:
            text = data.get_text()

        if text is not None:

            # Hopefully, 'text' contains one or more valid URLs or paths to
            #   video/audio files
            line_list = text.split('\n')
            mod_list = []

            for line in line_list:
                mod_line = utils.strip_whitespace(urllib.parse.unquote(line))
                if mod_line != '':

                    # On Linux, URLs are received as expected, but paths to
                    #   media data files are received as 'file://PATH'
                    match = re.search('^file\:\/\/(.*)', mod_line)
                    if match:
                        mod_list.append(match.group(1))
                    else:
                        mod_list.append(mod_line)

            # The True argument means to include 'dummy' media.Videos from the
            #   Classic Mode Tab in the search
            video_list = self.app_obj.retrieve_videos_from_db(mod_list, True)

            # (Remember if the video list is currently empty, or not)
            old_size = len(self.video_list)

            # Add videos to the list, but don't add duplicates
            for video_obj in video_list:

                if not video_obj in self.video_list:
                    self.video_list.append(video_obj)

            # Redraw the whole video list by calling this function, which also
            #   sorts self.video_list nicely
            self.setup_videos_tab_update_treeview()

            if old_size == 0 and self.video_list:

                # Replace the 'OK' button with a 'Process files' button
                self.ok_button.set_label(_('Process files'))
                self.ok_button.set_tooltip_text(
                    _('Process the files with FFmpeg'),
                )
                self.ok_button.get_child().set_width_chars(15)

        # Without this line, the user's cursor is permanently stuck in drag
        #   and drop mode
        context.finish(True, False, time)


    def on_video_remove_button_clicked(self, button, treeview):

        """Called from callback in self.setup_videos_tab().

        Removes a video from the list of videos to be processed by FFmpeg.

        If there are no videos left, this edit window reverts to its default
        state, in which we just save any changes to the FFmpeg options.

        Args:

            button (Gtk.Button): The widget clicked

            treeview (Gtk.TreeView): The treeview to be updated

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        if not path_list:

            return

        # (Multiple selection is not enabled)
        this_iter = model.get_iter(path_list[0])
        if this_iter is None:

            return

        dbid = int(model[this_iter][0])
        for video_obj in self.video_list:

            if video_obj.dbid == dbid:
                self.video_list.remove(video_obj)
                break

        # Update the visible list
        self.setup_videos_tab_update_treeview()
        # If all videos have been removed, restore the OK button
        if not self.video_list:

            self.ok_button.set_label(_('OK'))
            self.ok_button.get_child().set_width_chars(10)
            self.ok_button.set_tooltip_text(
                _('Apply changes'),
            )


    # (Redefined button strip callbacks)


    def on_button_apply_clicked(self, button):

        """Called from a callback in self.setup_button_strip().

        Applies any changes made by the user and re-draws the window's tabs,
        showing their new values.

        Args:

            button (Gtk.Button): The widget clicked

        """

        # Apply any changes the user has made. The True argument identifies
        #   this function as the caller, and prevents a process operation from
        #   starting
        self.apply_changes(True)

        # Remove all existing tabs from the notebook
        number = self.notebook.get_n_pages()
        if number:

            for count in range(0, number):
                self.notebook.remove_page(0)

        # Re-draw all the tabs
        self.setup_tabs()

        # Render the changes
        self.show_all()


    # (Redefined generic callbacks)


    def on_checkbutton_toggled(self, checkbutton, prop):

        """Modified form of the GenericEditWin callback, in which we
        automatically update the system command visible in the 'Name' tab.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            prop (str): The attribute in self.edit_obj to modify

        """

        if not checkbutton.get_active():
            self.edit_dict[prop] = False
        else:
            self.edit_dict[prop] = True

        # Update the system command in the 'Name' tab
        self.update_system_cmd()


    def on_combo_with_data_changed(self, combo, prop):

        """Modified form of the GenericEditWin callback, in which we
        automatically update the system command visible in the 'Name' tab.

        Args:

            combo (Gtk.ComboBox): The widget clicked

            prop (str): The attribute in self.edit_obj to modify

        """

        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        self.edit_dict[prop] = model[tree_iter][1]

        # Update the system command in the 'Name' tab
        self.update_system_cmd()


    def on_entry_changed(self, entry, prop):

        """Modified form of the GenericEditWin callback, in which we
        automatically update the system command visible in the 'Name' tab.

        Args:

            entry (Gtk.Entry): The widget clicked

            prop (str): The attribute in self.edit_obj to modify

        """

        self.edit_dict[prop] = entry.get_text()

        # (De)sensitise the checkbutton for 'rename_both_flag', if required
        if entry == self.add_end_filename_entry \
        or entry == self.regex_match_filename_entry:

            if self.retrieve_val('add_end_filename') == '' \
            and self.retrieve_val('regex_match_filename') == '':
                self.rename_both_flag_checkbutton.set_active(False)
                self.rename_both_flag_checkbutton.set_sensitive(False)
            else:
                self.rename_both_flag_checkbutton.set_sensitive(True)

        # Update the system command in the 'Name' tab
        self.update_system_cmd()


    def on_spinbutton_changed(self, spinbutton, prop):

        """Modified form of the GenericEditWin callback, in which we
        automatically update the system command visible in the 'Name' tab.

        Args:

            spinbutton (Gtk.SpinkButton): The widget clicked

            prop (str): The attribute in self.edit_obj to modify

        """

        self.edit_dict[prop] = int(spinbutton.get_value())

        # Update the system command in the 'Name' tab
        self.update_system_cmd()


    def on_textview_changed(self, textbuffer, prop):

        """Modified form of the GenericEditWin callback, in which we
        automatically update the system command visible in the 'Name' tab.

        Args:

            textbuffer (Gtk.TextBuffer): The widget modified

            prop (str): The attribute in self.edit_obj to modify

        """

        text = textbuffer.get_text(
            textbuffer.get_start_iter(),
            textbuffer.get_end_iter(),
            # Don't include hidden characters
            False,
        )

        old_value = self.retrieve_val(prop)

        if type(old_value) is list:
            self.edit_dict[prop] = text.split()
        elif type(old_value) is tuple:
            self.edit_dict[prop] = text.split()
        else:
             self.edit_dict[prop] = text

        # Update the system command in the 'Name' tab
        self.update_system_cmd()


class VideoEditWin(GenericEditWin):

    """Python class for an 'edit window' to modify values in a media.Video
    object.

    Args:

        app_obj (mainapp.TartubeApp): The main application object

        edit_obj (media.Video): The object whose attributes will be edited in
            this window

    """


    # Standard class methods


    def __init__(self, app_obj, edit_obj):

        Gtk.Window.__init__(self, title=_('Video properties'))

        if self.is_duplicate(app_obj, edit_obj):
            return

        # IV list - class objects
        # -----------------------
        # The mainapp.TartubeApp object
        self.app_obj = app_obj
        # The media.Video object being edited
        self.edit_obj = edit_obj


        # IV list - Gtk widgets
        # ---------------------
        self.grid = None                        # Gtk.Grid
        self.notebook = None                    # Gtk.Notebook
        self.reset_button = None                # Gtk.Button
        self.apply_button = None                # Gtk.Button
        self.ok_button = None                   # Gtk.Button
        self.cancel_button = None               # Gtk.Button
        # (Non-standard widgets)
        self.apply_options_button = None        # Gtk.Button
        self.edit_options_button = None         # Gtk.Button
        self.remove_options_button = None       # Gtk.Button


        # IV list - other
        # ---------------
        # Size (in pixels) of gaps between edit window widgets
        self.spacing_size = self.app_obj.default_spacing_size
        # Flag set to True if all four buttons ('Reset', 'Apply', 'Cancel' and
        #   'OK') are required, or False if just the 'OK' button is required
        self.multi_button_flag = False

        # When the user changes a value, it is not applied to self.edit_obj
        #   immediately; instead, it is stored temporarily in this dictionary
        # If the user clicks the 'OK' or 'Apply' buttons at the bottom of the
        #   window, the changes are applied to self.edit_obj
        # If the user clicks the 'Reset' or 'Cancel' buttons, the dictionary
        #   is emptied and the changes are lost
        # The key-value pairs in the dictionary correspond directly to the
        #   names of attributes, and their values in self.edit_obj
        # Key-value pairs are added to this dictionary whenever the user makes
        #   a change (so if no changes are made when the window is closed, the
        #   dictionary will still be empty)
        self.edit_dict = {}

        # String identifying the media type
        self.media_type = 'video'


        # Code
        # ----

        # Set up the edit window
        self.setup()


    # Public class methods


#   def is_duplicate():         # Inherited from GenericConfigWin


#   def setup():                # Inherited from GenericConfigWin


#   def setup_grid():           # Inherited from GenericConfigWin


#   def setup_notebook():       # Inherited from GenericConfigWin


#   def add_notebook_tab():     # Inherited from GenericConfigWin


#   def setup_button_strip():   # Inherited from GenericEditWin


#   def setup_gap():            # Inherited from GenericConfigWin


    # (Non-widget functions)


#   def apply_changes():        # Inherited from GenericEditWin


#   def retrieve_val():         # Inherited from GenericConfigWin


    # (Setup tabs)


    def setup_tabs(self):

        """Called by self.setup(), .on_button_apply_clicked() and
        .on_button_reset_clicked().

        Sets up the tabs for this edit window.
        """

        self.setup_general_tab()
        self.setup_download_options_tab()
        self.setup_livestream_tab()
        self.setup_descrip_tab()
        self.setup_errors_warnings_tab()


    def setup_general_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'General' tab.
        """

        tab, grid = self.add_notebook_tab(_('_General'))

        self.add_label(grid,
            '<u>' + _('General properties') + '</u>',
            0, 0, 3, 1,
        )

        # The first sets of widgets are shared by multiple edit windows
        self.add_container_properties(grid)
        self.add_source_properties(grid)

        label = self.add_label(grid,
            _('File'),
            0, 5, 1, 1,
        )
        label.set_hexpand(False)

        if not self.app_obj.show_custom_icons_flag:
            button = Gtk.Button.new_from_icon_name(
                Gtk.STOCK_FILE,
                Gtk.IconSize.BUTTON,
            )
        else:
            button = Gtk.Button.new()
            button.set_image(
                Gtk.Image.new_from_pixbuf(self.pixbuf_dict['stock_file']),
            )

        grid.attach(button, 1, 5, 1, 1)
        button.set_tooltip_text(_('Set the file (if this is the wrong one)'))
        # (Signal connect appears below)

        entry = self.add_entry(grid,
            None,
            2, 5, 1, 1,
        )
        entry.set_editable(False)
        if self.edit_obj.file_name:
            entry.set_text(self.edit_obj.get_actual_path(self.app_obj))

        # To avoid messing up the neat format of the rows above, add another
        #   grid, and put the next set of widgets inside it
        grid2 = Gtk.Grid()
        grid.attach(grid2, 0, 6, 3, 1)
        grid2.set_vexpand(False)
        grid2.set_column_spacing(self.spacing_size)
        grid2.set_row_spacing(self.spacing_size)

        checkbutton = self.add_checkbutton(grid2,
            _('Always simulate download of this video'),
            'dl_sim_flag',
            0, 0, 2, 1,
        )
        checkbutton.set_sensitive(False)

        label2 = self.add_label(grid2,
            _('Duration'),
            2, 0, 1, 1,
        )
        label2.set_hexpand(False)

        entry2 = self.add_entry(grid2,
            None,
            3, 0, 1, 1,
        )
        entry2.set_editable(False)
        if self.edit_obj.duration is not None:
            entry2.set_text(
                utils.convert_seconds_to_string(self.edit_obj.duration),
            )

        checkbutton2 = self.add_checkbutton(grid2,
            _('Video has been downloaded'),
            'dl_flag',
            0, 1, 2, 1,
        )
        checkbutton2.set_sensitive(False)

        label3 = self.add_label(grid2,
            _('File size'),
            2, 1, 1, 1,
        )
        label3.set_hexpand(False)

        entry3 = self.add_entry(grid2,
            None,
            3, 1, 1, 1,
        )
        entry3.set_editable(False)
        if self.edit_obj.file_size is not None:
            entry3.set_text(self.edit_obj.get_file_size_string())

        checkbutton3 = self.add_checkbutton(grid2,
            _('Video is marked as unwatched'),
            'new_flag',
            0, 2, 2, 1,
        )
        checkbutton3.set_sensitive(False)

        label4 = self.add_label(grid2,
            _('Upload time'),
            2, 2, 1, 1,
        )
        label4.set_hexpand(False)

        entry4 = self.add_entry(grid2,
            None,
            3, 2, 1, 1,
        )
        entry4.set_editable(False)
        if self.edit_obj.upload_time is not None:
            entry4.set_text(self.edit_obj.get_upload_time_string())

        checkbutton4 = self.add_checkbutton(grid2,
            _('Video is archived'),
            'archive_flag',
            0, 3, 1, 1,
        )
        checkbutton4.set_sensitive(False)

        checkbutton5 = self.add_checkbutton(grid2,
            _('Video is bookmarked'),
            'bookmark_flag',
            1, 3, 1, 1,
        )
        checkbutton5.set_sensitive(False)

        label5 = self.add_label(grid2,
            _('Receive time'),
            2, 3, 1, 1,
        )
        label5.set_hexpand(False)

        entry5 = self.add_entry(grid2,
            None,
            3, 3, 1, 1,
        )
        entry5.set_editable(False)
        if self.edit_obj.receive_time is not None:
            entry5.set_text(self.edit_obj.get_receive_time_string())

        checkbutton6 = self.add_checkbutton(grid2,
            _('Video is favourite'),
            'fav_flag',
            0, 4, 1, 1,
        )
        checkbutton6.set_sensitive(False)

        checkbutton7 = self.add_checkbutton(grid2,
            _('Video is in waiting list'),
            'waiting_flag',
            1, 4, 1, 1,
        )
        checkbutton7.set_sensitive(False)

        # (Signal connect from above)
        button.connect(
            'clicked',
            self.on_file_button_clicked,
            entry,
            entry2,
            entry3,
        )


#   def setup_download_options_tab():   # Inherited from GenericConfigWin


    def setup_livestream_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Livestream' tab.
        """

        tab, grid = self.add_notebook_tab(_('_Livestream'))

        grid_width = 2

        # Livestream properties
        self.add_label(grid,
            '<u>' + _('Livestream properties') + '</u>',
            0, 0, grid_width, 1,
        )

        label = self.add_label(grid,
            _('Livestream status'),
            0, 1, 1, 1,
        )
        label.set_hexpand(False)

        entry = self.add_entry(grid,
            None,
            1, 1, 1, 1,
        )
        entry.set_editable(False)
        if self.edit_obj.live_mode == 1:
            entry.set_text(_('Waiting to start'))
        elif self.edit_obj.live_mode == 2:
            entry.set_text(_('Stream has started'))
        else:
            entry.set_text(_('Not a livestream'))

        label2 = self.add_label(grid,
            _('Livestream message'),
            0, 2, 1, 1,
        )
        label2.set_hexpand(False)

        entry2 = self.add_entry(grid,
            None,
            1, 2, 1, 1,
        )
        entry2.set_text(self.edit_obj.live_msg)
        entry2.set_editable(False)

        checkbutton = Gtk.CheckButton()
        grid.attach(checkbutton, 0, 3, grid_width, 1)
        checkbutton.set_label(
            _('Video is pre-recorded'),
        )
        if self.edit_obj.live_debut_flag:
            checkbutton.set_active(True)
        checkbutton.set_sensitive(False)

        self.add_label(grid,
            '<u>' + _('Livestream actions') + '</u>',
            0, 4, grid_width, 1,
        )

        if self.edit_obj.live_mode:

            checkbutton2 = Gtk.CheckButton()
            grid.attach(checkbutton2, 0, 5, grid_width, 1)
            checkbutton2.set_label(
                _('When the livestream starts, show a desktop notification'),
            )
            if self.edit_obj.dbid in self.app_obj.media_reg_auto_notify_dict:
                checkbutton2.set_active(True)
            checkbutton2.set_sensitive(False)

            checkbutton3 = Gtk.CheckButton()
            grid.attach(checkbutton3, 0, 6, grid_width, 1)
            checkbutton3.set_label(
                _('When the livestream starts, play an alarm'),
            )
            if self.edit_obj.dbid in self.app_obj.media_reg_auto_alarm_dict:
                checkbutton3.set_active(True)
            checkbutton3.set_sensitive(False)

            checkbutton4 = Gtk.CheckButton()
            grid.attach(checkbutton4, 0, 7, grid_width, 1)
            checkbutton4.set_label(
                _(
                'When the livestream starts, open it in the system\'s web' \
                + ' browser',
                ),
            )
            if self.edit_obj.dbid in self.app_obj.media_reg_auto_open_dict:
                checkbutton4.set_active(True)
            checkbutton4.set_sensitive(False)

            checkbutton5 = Gtk.CheckButton()
            grid.attach(checkbutton5, 0, 8, grid_width, 1)
            checkbutton5.set_label(
                _(
                'When the livestream starts, begin downloading it immediately',
                ),
            )
            if self.edit_obj.dbid in self.app_obj.media_reg_auto_dl_start_dict:
                checkbutton5.set_active(True)
            checkbutton5.set_sensitive(False)

            checkbutton6 = Gtk.CheckButton()
            grid.attach(checkbutton6, 0, 9, grid_width, 1)
            checkbutton6.set_label(
                _(
                'When a livestream stops, download it (overwriting any' \
                + ' earlier file)',
                ),
            )
            if self.edit_obj.dbid in self.app_obj.media_reg_auto_dl_stop_dict:
                checkbutton6.set_active(True)
            checkbutton6.set_sensitive(False)


    def setup_descrip_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Description' tab.
        """

        tab, grid = self.add_notebook_tab(_('_Description'))

        # Video description
        self.add_label(grid,
            '<u>' + _('Video description') + '</u>',
            0, 0, 1, 1,
        )

        textview, textbuffer = self.add_textview(grid,
            'descrip',
            0, 1, 1, 1,
        )
        textview.set_editable(False)


    def setup_errors_warnings_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Errors / Warnings' tab.
        """

        tab, grid = self.add_notebook_tab(_('_Errors / Warnings'))

        self.add_label(grid,
            '<u>' + _('Errors / Warnings') + '</u>',
            0, 0, 1, 1,
        )

        self.add_label(grid,
            '<i>' + _(
                'Error messages produced the last time this video was' \
                + ' checked/downloaded',
            ) + '</i>',
            0, 1, 1, 1,
        )

        textview, textbuffer = self.add_textview(grid,
            'error_list',
            0, 2, 1, 1,
        )
        textview.set_editable(False)
        textview.set_wrap_mode(Gtk.WrapMode.WORD)

        self.add_label(grid,
            '<i>' + _(
                'Warning messages produced the last time this video was' \
                + ' checked/downloaded',
            ) + '</i>',
            0, 3, 1, 1,
        )

        textview2, textbuffer2 = self.add_textview(grid,
            'warning_list',
            0, 4, 1, 1,
        )
        textview2.set_editable(False)
        textview2.set_wrap_mode(Gtk.WrapMode.WORD)


    # Callback class methods


#   def on_button_apply_options_clicked():  # Inherited from GenericConfigWin


#   def on_button_edit_options_clicked():   # Inherited from GenericConfigWin


#   def on_button_remove_options_clicked(): # Inherited from GenericConfigWin


    def on_file_button_clicked(self, button, entry, entry2, entry3):

        """Called from a callback in self.setup_general_tab().

        Prompts the user to choose a new video/audio file. If a valid one is
        selected, update the media.Video object to use it

        Args:

            button (Gtk.Button): The widget clicked

            entry, entry2, entry3 (Gtk.Entry): Other widgets to update

        """

        # Prompt the user for a new file
        dialogue_win = self.app_obj.dialogue_manager_obj.show_file_chooser(
            _('Select the correct video/audio file'),
            self,
            'open',
        )

        if self.edit_obj.file_name is not None:
            old_path = self.edit_obj.get_actual_path(self.app_obj)
            old_dir, old_name = os.path.split(old_path)
            dialogue_win.set_current_folder(old_dir)

        # Get the user's response
        response = dialogue_win.run()
        if response == Gtk.ResponseType.OK:
            new_path = dialogue_win.get_filename()

        dialogue_win.destroy()
        if response == Gtk.ResponseType.OK:

            # The user must not set a video that's in a different directory
            file_dir, file_name = os.path.split(new_path)
            parent_obj = self.edit_obj.parent_obj
            if file_dir != parent_obj.get_actual_dir(self.app_obj) \
            and file_dir != parent_obj.get_default_dir(self.app_obj):

                self.app_obj.dialogue_manager_obj.show_msg_dialogue(
                    _(
                    'The replacement video/audio file must be in the same' \
                    + ' channel, playlist or folder',
                    ),
                    'error',
                    'ok',
                    self,           # Parent window is this window
                 )

                return

            # The new file must be in a recognised video/audio format
            file_name, file_ext = os.path.splitext(new_path)
            short_ext = file_ext[1:]

            if not short_ext in formats.VIDEO_FORMAT_LIST \
            and not short_ext in formats.AUDIO_FORMAT_LIST:

                self.app_obj.dialogue_manager_obj.show_msg_dialogue(
                    _('You must select a valid video/audio file'),
                    'error',
                    'ok',
                    self,           # Parent window is this window
                )

                return

            # Set the new file path
            self.edit_obj.set_file_from_path(new_path)

            # Set the new file's size, duration, and so on. The True argument
            #   instructs the function to override existing values
            self.app_obj.update_video_from_filesystem(
                self.edit_obj,
                new_path,
                True,
            )

            # Update the entry boxes
            entry.set_text(self.edit_obj.get_actual_path(self.app_obj))
            if self.edit_obj.duration is not None:

                entry2.set_text(
                    utils.convert_seconds_to_string(self.edit_obj.duration),
                )

            else:

                entry2.set_text('')

            if self.edit_obj.file_size is not None:
                entry3.set_text(self.edit_obj.get_file_size_string())
            else:
                entry3.set_text('')

            # If the video exists, then we can mark it as downloaded
            if not self.edit_obj.dl_flag:
                self.app_obj.mark_video_downloaded(self.edit_obj, True)

            # Redraw the video in the Video Catalogue straight away
            self.app_obj.main_win_obj.video_catalogue_update_video(
                self.edit_obj,
            )


class ChannelPlaylistEditWin(GenericEditWin):

    """Python class for an 'edit window' to modify values in a media.Channel or
    media.Playlist object.

    Args:

        app_obj (mainapp.TartubeApp): The main application object

        edit_obj (media.Channel, media.Playlist): The object whose attributes
            will be edited in this window

    """


    # Standard class methods


    def __init__(self, app_obj, edit_obj):

        if isinstance(edit_obj, media.Channel):
            media_type = 'channel'
            win_title = _('Channel properties')
        else:
            media_type = 'playlist'
            win_title = _('Playlist properties')

        Gtk.Window.__init__(self, title=win_title)

        if self.is_duplicate(app_obj, edit_obj):
            return

        # IV list - class objects
        # -----------------------
        # The mainapp.TartubeApp object
        self.app_obj = app_obj
        # The media.Channel or media.Playlist object being edited
        self.edit_obj = edit_obj


        # IV list - Gtk widgets
        # ---------------------
        self.grid = None                        # Gtk.Grid
        self.notebook = None                    # Gtk.Notebook
        self.reset_button = None                # Gtk.Button
        self.apply_button = None                # Gtk.Button
        self.ok_button = None                   # Gtk.Button
        self.cancel_button = None               # Gtk.Button
        # (Non-standard widgets)
        self.apply_options_button = None        # Gtk.Button
        self.edit_options_button = None         # Gtk.Button
        self.remove_options_button = None       # Gtk.Button


        # IV list - other
        # ---------------
        # Size (in pixels) of gaps between edit window widgets
        self.spacing_size = self.app_obj.default_spacing_size
        # Flag set to True if all four buttons ('Reset', 'Apply', 'Cancel' and
        #   'OK') are required, or False if just the 'OK' button is required
        self.multi_button_flag = False

        # When the user changes a value, it is not applied to self.edit_obj
        #   immediately; instead, it is stored temporarily in this dictionary
        # If the user clicks the 'OK' or 'Apply' buttons at the bottom of the
        #   window, the changes are applied to self.edit_obj
        # If the user clicks the 'Reset' or 'Cancel' buttons, the dictionary
        #   is emptied and the changes are lost
        # The key-value pairs in the dictionary correspond directly to
        #   the names of attributes, and their balues in self.edit_obj
        # Key-value pairs are added to this dictionary whenever the user
        #   makes a change (so if no changes are made when the window is
        #   closed, the dictionary will still be empty)
        self.edit_dict = {}

        # String set to 'channel' or 'playlist'
        self.media_type = media_type


        # Code
        # ----

        # Set up the edit window
        self.setup()


    # Public class methods


#   def is_duplicate():         # Inherited from GenericConfigWin


#   def setup():                # Inherited from GenericConfigWin


#   def setup_grid():           # Inherited from GenericConfigWin


#   def setup_notebook():       # Inherited from GenericConfigWin


#   def add_notebook_tab():     # Inherited from GenericConfigWin


#   def setup_button_strip():   # Inherited from GenericEditWin


#   def setup_gap():            # Inherited from GenericConfigWin


    # (Non-widget functions)


#   def apply_changes():        # Inherited from GenericEditWin


#   def retrieve_val():         # Inherited from GenericConfigWin


    # (Setup tabs)


    def setup_tabs(self):

        """Called by self.setup(), .on_button_apply_clicked() and
        .on_button_reset_clicked().

        Sets up the tabs for this edit window.
        """

        self.setup_general_tab()
        self.setup_download_options_tab()
        if mainapp.HAVE_MATPLOTLIB_FLAG:
            self.setup_history_tab()
        self.setup_rss_feed_tab()
        self.setup_errors_warnings_tab()


    def setup_general_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'General' tab.
        """

        tab, grid = self.add_notebook_tab(_('_General'))

        self.add_label(grid,
            '<u>' + _('General properties') + '</u>',
            0, 0, 3, 1,
        )

        # The first sets of widgets are shared by multiple edit windows
        self.add_container_properties(grid)
        self.add_source_properties(grid)
        self.add_destination_properties(grid)

        # To avoid messing up the neat format of the rows above, add another
        #   grid, and put the next set of widgets inside it
        grid2 = Gtk.Grid()
        grid.attach(grid2, 0, 7, 3, 1)
        grid2.set_vexpand(False)
        grid2.set_column_spacing(self.spacing_size)
        grid2.set_row_spacing(self.spacing_size)

        if self.media_type == 'channel':
            string = _('Always simulate download of videos in this channel')
        else:
            string = _('Always simulate download of videos in this playlist')

        checkbutton = self.add_checkbutton(grid2,
            string,
            'dl_sim_flag',
            0, 0, 1, 1,
        )
        checkbutton.set_sensitive(False)

        if self.media_type == 'channel':
            string = _('Disable checking/downloading for this channel')
        else:
            string = _('Disable checking/downloading for this playlist')

        checkbutton2 = self.add_checkbutton(grid2,
            string,
            'dl_disable_flag',
            0, 1, 1, 1,
        )
        checkbutton2.set_sensitive(False)

        if self.media_type == 'channel':
            string = _('This channel is marked as a favourite')
        else:
            string = _('This playlist is marked as a favourite')

        checkbutton3 = self.add_checkbutton(grid2,
            string,
            'fav_flag',
            0, 2, 1, 1,
        )
        checkbutton3.set_sensitive(False)

        self.add_label(grid2,
            _('Total videos'),
            1, 0, 1, 1,
        )
        entry = self.add_entry(grid2,
            'vid_count',
            2, 0, 1, 1,
        )
        entry.set_editable(False)
        entry.set_width_chars(8)
        entry.set_hexpand(False)

        self.add_label(grid2,
            _('New videos'),
            1, 1, 1, 1,
        )
        entry2 = self.add_entry(grid2,
            'new_count',
            2, 1, 1, 1,
        )
        entry2.set_editable(False)
        entry2.set_width_chars(8)
        entry2.set_hexpand(False)

        self.add_label(grid2,
            _('Favourite videos'),
            1, 2, 1, 1,
        )
        entry3 = self.add_entry(grid2,
            'fav_count',
            2, 2, 1, 1,
        )
        entry3.set_editable(False)
        entry3.set_width_chars(8)
        entry3.set_hexpand(False)

        self.add_label(grid2,
            _('Downloaded videos'),
            1, 3, 1, 1,
        )
        entry4 = self.add_entry(grid2,
            'dl_count',
            2, 3, 1, 1,
        )
        entry4.set_editable(False)
        entry4.set_width_chars(8)
        entry4.set_hexpand(False)


#   def setup_download_options_tab():   # Inherited from GenericConfigWin


    def setup_history_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'History' tab.
        """

        tab, grid = self.add_notebook_tab(_('_History'))

        grid_width = 6

        self.add_label(grid,
            '<u>' + _('Download history') + '</u>',
            0, 0, grid_width, 1,
        )

        # Add combos to customise the graph
        combo, combo2, combo3, combo4, combo5 = self.add_combos_for_graphs(
            grid,
            1,
        )

        # Add a button which, when clicked, draws the graph using the
        #   customisation options specified by the combos
        button = Gtk.Button()
        grid.attach(button, 5, 1, 1, 1)
        button.set_label(_('Draw'))
        # (Signal connect appears below)

        # Add a box, inside which we draw graphs
        hbox = Gtk.HBox()
        grid.attach(hbox, 0, 2, grid_width, 1)
        hbox.set_hexpand(True)
        hbox.set_vexpand(True)

        # (Signal connects from above)
        button.connect(
            'clicked', self.on_button_draw_graph_clicked,
            hbox,
            combo,
            combo2,
            combo3,
            combo4,
            combo5,
        )


    def setup_rss_feed_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'RSS feed' tab.
        """

        tab, grid = self.add_notebook_tab(_('_RSS feed'))

        self.add_label(grid,
            '<u>' + _('RSS feed') + '</u>',
            0, 0, 1, 1,
        )

        if self.media_type == 'channel':
            string = _(
                'If Tartube cannot detect the channel\'s RSS feed, you' \
                + ' can enter the URL here',
            )
        else:
            string = _(
                'If Tartube cannot detect the playlist\'s RSS feed, you' \
                + ' can enter the URL here',
            )

        string2 = _(
            '(The feed is used to detect livestreams on compatible websites)',
        )

        self.add_label(grid,
            '<i>' + string + '\n' + string2 + '</i>',
            0, 1, 1, 1,
        )

        entry = self.add_entry(grid,
            'rss',
            0, 2, 1, 1,
        )
        entry.set_editable(True)
        entry.set_hexpand(True)


    def setup_errors_warnings_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Errors / Warnings' tab.
        """

        tab, grid = self.add_notebook_tab(_('_Errors / Warnings'))

        self.add_label(grid,
            '<u>' + _('Errors / Warnings') + '</u>',
            0, 0, 1, 1,
        )

        if self.media_type == 'channel':
            string = _(
                'Error messages produced the last time this channel was' \
                + ' checked/downloaded',
            )
        else:
            string = _(
                'Error messages produced the last time this playlist was' \
                + ' checked/downloaded',
            )

        self.add_label(grid,
            '<i>' + string + '</i>',
            0, 1, 1, 1,
        )

        textview, textbuffer = self.add_textview(grid,
            'error_list',
            0, 2, 1, 1,
        )
        textview.set_editable(False)
        textview.set_wrap_mode(Gtk.WrapMode.WORD)

        if self.media_type == 'channel':
            string = _(
                'Warning messages produced the last time this channel was' \
                + ' checked/downloaded',
            )
        else:
            string = _(
                'Warning messages produced the last time this playlist was' \
                + ' checked/downloaded',
            )

        self.add_label(grid,
            '<i>' + string + '</i>',
            0, 3, 1, 1,
        )

        textview2, textbuffer2 = self.add_textview(grid,
            'warning_list',
            0, 4, 1, 1,
        )
        textview2.set_editable(False)
        textview2.set_wrap_mode(Gtk.WrapMode.WORD)


    # (Support functions)


#   def add_combos_for_graphs():            # Inherited from GenericConfigWin


#   def plot_graph():                       # Inherited from GenericConfigWin


    # Callback class methods


#   def on_button_apply_options_clicked():  # Inherited from GenericConfigWin


#   def on_button_edit_options_clicked():   # Inherited from GenericConfigWin


#   def on_button_remove_options_clicked(): # Inherited from GenericConfigWin


    def never_called_func(self):

        """Function that is never called, but which makes this class object
        collapse neatly in my IDE."""

        pass


class FolderEditWin(GenericEditWin):

    """Python class for an 'edit window' to modify values in a media.Folder
    object.

    Args:

        app_obj (mainapp.TartubeApp): The main application object

        edit_obj (media.Folder): The object whose attributes will be edited in
            this window

    """


    # Standard class methods


    def __init__(self, app_obj, edit_obj):

        Gtk.Window.__init__(self, title=_('Folder properties'))

        if self.is_duplicate(app_obj, edit_obj):
            return

        # IV list - class objects
        # -----------------------
        # The mainapp.TartubeApp object
        self.app_obj = app_obj
        # The media.Folder object being edited
        self.edit_obj = edit_obj


        # IV list - Gtk widgets
        # ---------------------
        self.grid = None                        # Gtk.Grid
        self.notebook = None                    # Gtk.Notebook
        self.reset_button = None                # Gtk.Button
        self.apply_button = None                # Gtk.Button
        self.ok_button = None                   # Gtk.Button
        self.cancel_button = None               # Gtk.Button
        # (Non-standard widgets)
        self.apply_options_button = None        # Gtk.Button
        self.edit_options_button = None         # Gtk.Button
        self.remove_options_button = None       # Gtk.Button


        # IV list - other
        # ---------------
        # Size (in pixels) of gaps between edit window widgets
        self.spacing_size = self.app_obj.default_spacing_size
        # Flag set to True if all four buttons ('Reset', 'Apply', 'Cancel' and
        #   'OK') are required, or False if just the 'OK' button is required
        self.multi_button_flag = False

        # When the user changes a value, it is not applied to self.edit_obj
        #   immediately; instead, it is stored temporarily in this dictionary
        # If the user clicks the 'OK' or 'Apply' buttons at the bottom of the
        #   window, the changes are applied to self.edit_obj
        # If the user clicks the 'Reset' or 'Cancel' buttons, the dictionary
        #   is emptied and the changes are lost
        # The key-value pairs in the dictionary correspond directly to
        #   the names of attributes, and their balues in self.edit_obj
        # Key-value pairs are added to this dictionary whenever the user
        #   makes a change (so if no changes are made when the window is
        #   closed, the dictionary will still be empty)
        self.edit_dict = {}

        # String identifying the media type
        self.media_type = 'folder'


        # Code
        # ----

        # Set up the edit window
        self.setup()


    # Public class methods


#   def is_duplicate():         # Inherited from GenericConfigWin


#   def setup():                # Inherited from GenericConfigWin


#   def setup_grid():           # Inherited from GenericConfigWin


#   def setup_notebook():       # Inherited from GenericConfigWin


#   def add_notebook_tab():     # Inherited from GenericConfigWin


#   def setup_button_strip():   # Inherited from GenericEditWin


#   def setup_gap():            # Inherited from GenericConfigWin


    # (Non-widget functions)


#   def apply_changes():        # Inherited from GenericEditWin


#   def retrieve_val():         # Inherited from GenericConfigWin


    # (Setup tabs)


    def setup_tabs(self):

        """Called by self.setup(), .on_button_apply_clicked() and
        .on_button_reset_clicked().

        Sets up the tabs for this edit window.
        """

        self.setup_general_tab()
        self.setup_statistics_tab()
        if mainapp.HAVE_MATPLOTLIB_FLAG:
            self.setup_history_tab()
        self.setup_download_options_tab()


    def setup_general_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'General' tab.
        """

        tab, grid = self.add_notebook_tab(_('_General'))

        self.add_label(grid,
            '<u>' + _('General properties') + '</u>',
            0, 0, 3, 1,
        )

        # The first sets of widgets are shared by multiple edit windows
        self.add_container_properties(grid)
        self.add_destination_properties(grid)

        # To avoid messing up the neat format of the rows above, add another
        #   grid, and put the next set of widgets inside it
        grid2 = Gtk.Grid()
        grid.attach(grid2, 0, 7, 3, 1)
        grid2.set_border_width(self.spacing_size)
        grid2.set_column_spacing(self.spacing_size)
        grid2.set_row_spacing(self.spacing_size)

        checkbutton = self.add_checkbutton(grid2,
            _('Always simulate download of videos'),
            'dl_sim_flag',
            0, 0, 1, 1,
        )
        checkbutton.set_sensitive(False)

        checkbutton2 = self.add_checkbutton(grid2,
            _('Disable checking/downloading for this folder'),
            'dl_disable_flag',
            0, 1, 1, 1,
        )
        checkbutton2.set_sensitive(False)

        checkbutton3 = self.add_checkbutton(grid2,
            _('This folder is marked as a favourite'),
            'fav_flag',
            0, 2, 1, 1,
        )
        checkbutton3.set_sensitive(False)

        checkbutton4 = self.add_checkbutton(grid2,
            _('This folder is hidden'),
            'hidden_flag',
            0, 3, 1, 1,
        )
        checkbutton4.set_sensitive(False)

        checkbutton5 = self.add_checkbutton(grid2,
            _('This folder can\'t be deleted by the user'),
            'fixed_flag',
            1, 0, 1, 1,
        )
        checkbutton5.set_sensitive(False)

        checkbutton6 = self.add_checkbutton(grid2,
            _('This is a system-controlled folder'),
            'priv_flag',
            1, 1, 1, 1,
        )
        checkbutton6.set_sensitive(False)

        checkbutton7 = self.add_checkbutton(grid2,
            _('Only videos can be added to this folder'),
            'restrict_flag',
            1, 2, 1, 1,
        )
        checkbutton7.set_sensitive(False)

        checkbutton8 = self.add_checkbutton(grid2,
            _('All contents deleted when Tartube shuts down'),
            'temp_flag',
            1, 3, 1, 1,
        )
        checkbutton8.set_sensitive(False)


    def setup_statistics_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Statistics' tab.
        """

        tab, grid = self.add_notebook_tab(_('_Statistics'))

        grid_width = 4

        self.add_label(grid,
            '<u>' + _('Statistics') + '</u>',
            0, 0, grid_width, 1,
        )

        self.add_label(grid,
            _('This folder contains:'),
            0, 1, grid_width, 1,
        )

        self.add_label(grid,
            _('Videos'),
            0, 2, 1, 1,
        )

        entry = self.add_entry(grid,
            None,
            1, 2, 1, 1,
        )
        entry.set_editable(False)

        self.add_label(grid,
            _('Downloaded'),
            0, 3, 1, 1,
        )

        entry2 = self.add_entry(grid,
            None,
            1, 3, 1, 1,
        )
        entry2.set_editable(False)

        self.add_label(grid,
            _('Other'),
            0, 4, 1, 1,
        )

        entry3 = self.add_entry(grid,
            None,
            1, 4, 1, 1,
        )
        entry3.set_editable(False)

        self.add_label(grid,
            _('Channels'),
            2, 2, 1, 1,
        )

        entry4 = self.add_entry(grid,
            None,
            3, 2, 1, 1,
        )
        entry4.set_editable(False)

        self.add_label(grid,
            _('Playlists'),
            2, 3, 1, 1,
        )

        entry5 = self.add_entry(grid,
            None,
            3, 3, 1, 1,
        )
        entry5.set_editable(False)

        self.add_label(grid,
            _('Sub-folders'),
            2, 4, 1, 1,
        )

        entry6 = self.add_entry(grid,
            None,
            3, 4, 1, 1,
        )
        entry6.set_editable(False)

        # Initialise the entries
        self.setup_statistics_tab_recalculate(
            entry,
            entry2,
            entry3,
            entry4,
            entry5,
            entry6,
        )

        button = Gtk.Button()
        grid.attach(button, 3, 5, 1, 1)
        button.set_label(_('Recalculate'))
        button.connect(
            'clicked',
            self.on_button_recalculate_clicked,
            entry,
            entry2,
            entry3,
            entry4,
            entry5,
            entry6,
        )


    def setup_statistics_tab_recalculate(self, entry, entry2, entry3, entry4,
    entry5, entry6):

        """Called by self.setup_statistics_tab and
        .on_recalculate_button_clicked().

        Args:

            entry, entry2, entry3, entry4, entry5, entry6 (Gtk.Entry): The
                entry boxes to update

        """

        # Get number of videos, channels, playlists and sub-folders
        total_count, video_count, channel_count, playlist_count, \
        folder_count = self.edit_obj.count_descendants( [0, 0, 0, 0, 0] )

        # Calculate downloaded/not downloaded videos
        dl_count = 0
        not_dl_count = 0
        child_list = self.edit_obj.compile_all_videos( [] )

        for video_obj in child_list:

            if video_obj.dl_flag:
                dl_count += 1
            else:
                not_dl_count += 1

        entry.set_text(str(video_count))
        entry2.set_text(str(dl_count))
        entry3.set_text(str(not_dl_count))
        entry4.set_text(str(channel_count))
        entry5.set_text(str(playlist_count))
        entry6.set_text(str(folder_count))


    def setup_history_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'History' tab.
        """

        tab, grid = self.add_notebook_tab(_('_History'))

        grid_width = 6

        self.add_label(grid,
            '<u>' + _('Download history') + '</u>',
            0, 0, grid_width, 1,
        )

        # Add combos to customise the graph
        combo, combo2, combo3, combo4, combo5 = self.add_combos_for_graphs(
            grid,
            1,
        )

        # Add a button which, when clicked, draws the graph using the
        #   customisation options specified by the combos
        button = Gtk.Button()
        grid.attach(button, 5, 1, 1, 1)
        button.set_label(_('Draw'))
        # (Signal connect appears below)

        # Add a box, inside which we draw graphs
        hbox = Gtk.HBox()
        grid.attach(hbox, 0, 2, grid_width, 1)
        hbox.set_hexpand(True)
        hbox.set_vexpand(True)

        # (Signal connects from above)
        button.connect(
            'clicked', self.on_button_draw_graph_clicked,
            hbox,
            combo,
            combo2,
            combo3,
            combo4,
            combo5,
        )


#   def setup_download_options_tab():       # Inherited from GenericConfigWin


    # (Support functions)


#   def add_combos_for_graphs():            # Inherited from GenericConfigWin


#   def plot_graph():                       # Inherited from GenericConfigWin


    # Callback class methods


#   def on_button_apply_options_clicked():  # Inherited from GenericConfigWin


#   def on_button_edit_options_clicked():   # Inherited from GenericConfigWin


#   def on_button_remove_options_clicked(): # Inherited from GenericConfigWin


#   def on_button_draw_graph_clicked():     # Inherited from GenericConfigWin


    def on_button_recalculate_clicked(self, button, entry, entry2, entry3,
    entry4, entry5, entry6):

        """Called from callback in self.setup_statistics_tab().

        Recalculates the number of child media data objects, and updates the
        entry boxes.

        Args:

            button (Gtk.Button): The widget clicked

            entry, entry2, entry3, entry4, entry5, entry6 (Gtk.Entry): The
                entry boxes to update

        """

        self.setup_statistics_tab_recalculate(
            entry,
            entry2,
            entry3,
            entry4,
            entry5,
            entry6,
        )


class ScheduledEditWin(GenericEditWin):

    """Python class for an 'edit window' to modify values in a media.Scheduled
    object.

    Args:

        app_obj (mainapp.TartubeApp): The main application object

        edit_obj (media.Scheduled): The object whose attributes will be edited
            in this window

    """


    # Standard class methods


    def __init__(self, app_obj, edit_obj):

        Gtk.Window.__init__(self, title=_('Scheduled download'))

        if self.is_duplicate(app_obj, edit_obj):
            return

        # IV list - class objects
        # -----------------------
        # The mainapp.TartubeApp object
        self.app_obj = app_obj
        # The media.Scheduled object being edited
        self.edit_obj = edit_obj


        # IV list - Gtk widgets
        # ---------------------
        self.grid = None                        # Gtk.Grid
        self.notebook = None                    # Gtk.Notebook
        self.reset_button = None                # Gtk.Button
        self.apply_button = None                # Gtk.Button
        self.ok_button = None                   # Gtk.Button
        self.cancel_button = None               # Gtk.Button
        # (IVs used to handle widget changes in the 'Media' tab)
        self.radiobutton = None                 # Gtk.RadioButton
        self.radiobutton2 = None                # Gtk.RadioButton

        # IV list - other
        # ---------------
        # Size (in pixels) of gaps between edit window widgets
        self.spacing_size = self.app_obj.default_spacing_size
        # Flag set to True if all four buttons ('Reset', 'Apply', 'Cancel' and
        #   'OK') are required, or False if just the 'OK' button is required
        self.multi_button_flag = False

        # When the user changes a value, it is not applied to self.edit_obj
        #   immediately; instead, it is stored temporarily in this dictionary
        # If the user clicks the 'OK' or 'Apply' buttons at the bottom of the
        #   window, the changes are applied to self.edit_obj
        # If the user clicks the 'Reset' or 'Cancel' buttons, the dictionary
        #   is emptied and the changes are lost
        # The key-value pairs in the dictionary correspond directly to
        #   the names of attributes, and their balues in self.edit_obj
        # Key-value pairs are added to this dictionary whenever the user
        #   makes a change (so if no changes are made when the window is
        #   closed, the dictionary will still be empty)
        self.edit_dict = {}

        # String identifying the media type
        self.media_type = 'scheduled'


        # Code
        # ----

        # Set up the edit window
        self.setup()


    # Public class methods


#   def is_duplicate():         # Inherited from GenericConfigWin


#   def setup():                # Inherited from GenericConfigWin


#   def setup_grid():           # Inherited from GenericConfigWin


#   def setup_notebook():       # Inherited from GenericConfigWin


#   def add_notebook_tab():     # Inherited from GenericConfigWin


#   def setup_button_strip():   # Inherited from GenericEditWin


#   def setup_gap():            # Inherited from GenericConfigWin


    # (Non-widget functions)


    def apply_changes(self):

        """Called by self.on_button_ok_clicked() and
        self.on_button_apply_clicked().

        Any changes the user has made are temporarily stored in self.edit_dict.
        Apply to those changes to the object being edited.
        """

        # Apply any changes the user has made
        for key in self.edit_dict.keys():
            setattr(self.edit_obj, key, self.edit_dict[key])

        # The changes can now be cleared
        self.edit_dict = {}

        # Since the edit window opened, channels/playlists/folders may have
        #   been deleted. Check that any items in the .media_list IV still
        #   exist
        for name in self.edit_obj.media_list:

            if not name in self.app_obj.media_name_dict:
                self.edit_obj.media_list.remove(name)

        # Update the parent preference window's list of scheduled downloads
        for win_obj in self.app_obj.main_win_obj.config_win_list:

            if isinstance(win_obj, SystemPrefWin):

                win_obj.setup_scheduling_start_tab_update_treeview()


#   def retrieve_val():         # Inherited from GenericConfigWin


    # (Setup tabs)


    def setup_tabs(self):

        """Called by self.setup(), .on_button_apply_clicked() and
        .on_button_reset_clicked().

        Sets up the tabs for this edit window.
        """

        self.setup_general_tab()
        self.setup_media_tab()


    def setup_general_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'General' tab.
        """

        tab, grid = self.add_notebook_tab(_('_General'))

        grid_width = 3

        self.add_label(grid,
            '<u>' + _('General properties') + '</u>',
            0, 0, grid_width, 1,
        )

        self.add_label(grid,
            _('Scheduled download name'),
            0, 1, 1, 1,
        )

        entry = self.add_entry(grid,
            None,
            1, 1, (grid_width - 1), 1,
        )
        entry.set_text(self.edit_obj.name)
        entry.set_editable(False)

        self.add_label(grid,
            _('Download mode'),
            0, 2, 1, 1,
        )

        combo_list = [
            [_('Check channels, playlist and folders'), 'sim'],
            [_('Download channels, playlists and folders'), 'real'],
            [_('Perform a custom download'), 'custom'],
        ]

        combo = self.add_combo_with_data(grid,
            combo_list,
            'dl_mode',
            1, 2, (grid_width - 1), 1,
        )
        combo.set_hexpand(True)

        self.add_label(grid,
            _('Start mode'),
            0, 3, 1, 1,
        )

        combo2_list = [
            [_('Perform this download at regular intervals'), 'scheduled'],
            [_('Perform this download when Tartube starts'), 'start'],
            [_('Disable this scheduled download'), 'none'],
        ]

        combo2 = self.add_combo_with_data(grid,
            combo2_list,
            None,
            1, 3, (grid_width - 1), 1,
        )
        combo2.set_hexpand(True)
        # (Signal connect appears below)

        self.add_label(grid,
            _('Time between scheduled downloads'),
            0, 4, 1, 1,
        )

        spinbutton = self.add_spinbutton(grid,
            1, None, 1,
            'wait_value',
            1, 4, 1, 1,
        )

        combo3_list = []
        for unit in formats.TIME_METRIC_LIST:
            if unit != 'seconds':
                combo3_list.append(
                    [ formats.TIME_METRIC_TRANS_DICT[unit], unit ],
                )

        combo3 = self.add_combo_with_data(grid,
            combo3_list,
            'wait_unit',
            2, 4, 1, 1,
        )
        combo3.set_hexpand(True)

        if self.edit_obj.start_mode == 'start':
            combo2.set_active(1)
            spinbutton.set_sensitive(False)
            combo3.set_sensitive(False)
        elif self.edit_obj.start_mode == 'none':
            combo2.set_active(2)
            spinbutton.set_sensitive(False)
            combo3.set_sensitive(False)
        else:
            combo2.set_active(0)

        # (Signal connect from above)
        combo2.connect(
            'changed',
            self.on_start_mode_combo_changed,
            spinbutton,
            combo3,
        )

        self.add_label(grid,
            _('If another scheduled download is running:'),
            0, 5, grid_width, 1,
        )

        combo4_list = [
            [
                _(
                'Add channels, playlists and folders to the end of the queue',
                ),
                'join',
            ],
            [
                _(
                'Add channels, playlists and folders to the beginning of the' \
                + ' queue',
                ),
                'priority',
            ],
            [
                _(
                'Do nothing, just wait until the next scheduled download' \
                + ' time',
                ),
                'skip',
            ],
        ]

        combo4 = self.add_combo_with_data(grid,
            combo4_list,
            'join_mode',
            0, 6, grid_width, 1,
        )
        combo4.set_hexpand(True)

        self.add_checkbutton(grid,
            _('This scheduled download takes priority over others') \
            + '\n' \
            + _(
            'Other scheduled downloads won\'t start until this one is' \
            + ' finished',
            ),
            'exclusive_flag',
            0, 7, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _(
            'Ignore time-saving preferences, and check/download the whole' \
            + ' channel/playlist/folder',
            ),
            'ignore_limits_flag',
            0, 8, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _('Shut down Tartube when this scheduled download has finished'),
            'shutdown_flag',
            0, 9, grid_width, 1,
        )


    def setup_media_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'General' tab.
        """

        tab, grid = self.add_notebook_tab(_('_Media'))

        grid_width = 4

        self.add_label(grid,
            '<u>' + _('Media to download') + '</u>',
            0, 0, grid_width, 1,
        )

        self.radiobutton = self.add_radiobutton(grid,
            None,
            _('Check/download everything'),
            None,
            None,
            0, 1, grid_width, 1,
        )

        self.radiobutton2 = self.add_radiobutton(grid,
            self.radiobutton,
            _('Only check/download the media below'),
            None,
            None,
            0, 2, grid_width, 1,
        )
        if not self.edit_obj.all_flag:
            self.radiobutton2.set_active(True)
        self.radiobutton2.connect(
            'toggled',
            self.on_all_flag_toggled,
        )

        self.add_label(grid,
            '<i>' + _(
            'Hint: you can drag and drop channels, playlists and your own' \
            + ' folders here',
            ) + '</i>',
            0, 3, grid_width, 1,
        )

        treeview, liststore = self.add_treeview(grid,
            0, 4, grid_width, 1,
        )
        treeview.set_hexpand(True)

        # Initialise the treeview
        self.setup_media_tab_update_treeview(liststore)

        # Set up drag and drop into the treeview
        drag_target_list = [('video index', 0, 0)]
        treeview.enable_model_drag_dest(
            # Table of targets the drag procedure supports, and array length
            drag_target_list,
            # Bitmask of possible actions for a drag from this widget
            Gdk.DragAction.DEFAULT,
        )
        treeview.connect('drag-drop',
            self.on_video_index_drag_drop,
        )
        treeview.connect(
            'drag-data-received',
            self.on_video_index_drag_data_received,
        )

        # Editing widgets
        combo_list = []
        for dbid in self.app_obj.media_name_dict.values():
            media_data_obj = self.app_obj.media_reg_dict[dbid]

            if not isinstance(media_data_obj, media.Folder) \
            or not media_data_obj.fixed_flag:
                combo_list.append(media_data_obj.name)

        combo_list.sort()
        combo = self.add_combo(grid,
            combo_list,
            None,
            0, 5, 1, 1,
        )
        combo.set_active(0)

        button = Gtk.Button()
        grid.attach(button, 1, 5, 1, 1)
        button.set_label(_('Add'))
        button.connect(
            'clicked',
            self.on_add_button_clicked,
            combo,
            liststore,
        )

        button2 = Gtk.Button()
        grid.attach(button2, 2, 5, 1, 1)
        button2.set_label(_('Remove'))
        button2.connect(
            'clicked',
            self.on_remove_button_clicked,
            combo,
            treeview,
        )

        button3 = Gtk.Button()
        grid.attach(button3, 3, 5, 1, 1)
        button3.set_label(_('Clear list'))
        button3.connect('clicked', self.on_clear_button_clicked, liststore)


    def setup_media_tab_update_treeview(self, liststore):

        """Called by self.setup_media_tab().

        Updates the treeview to display the media.Scheduled object's
        .media_list IV, first checking that any specified media data objects
        still exist.

        Args:

            liststore (Gtk.ListStore): The treeview's model

        """

        liststore.clear()

        media_list = self.retrieve_val('media_list')
        for name in media_list:

            # This media data object may be deleted while the window is open
            #   (but the .media_list IV is checked, when the 'Save' or 'Apply'
            #   buttons are clicked)
            if name in self.app_obj.media_name_dict:
                liststore.append([name])


    # Callback class methods


#   def on_button_apply_options_clicked():  # Inherited from GenericConfigWin


#   def on_button_edit_options_clicked():   # Inherited from GenericConfigWin


#   def on_button_remove_options_clicked(): # Inherited from GenericConfigWin


    def on_add_button_clicked(self, button, combo, liststore):

        """Called by callback in self.setup_media_tab().

        Args:

            button (Gtk.Button): The widget clicked

            combo (Gtk.ComboBox): A combo in which the user has selected a new
                media data object

            liststore (Gtk.ListStore): The treeview's model

        """

        combo_iter = combo.get_active_iter()
        combo_model = combo.get_model()
        name = combo_model[combo_iter][0]

        # Check the media data object hasn't already been added to the list,
        #   and that is still exists in the media data registry
        media_list = self.retrieve_val('media_list')

        if not (name in media_list) \
        and name in self.app_obj.media_name_dict:

            media_list.append(name)
            self.edit_dict['media_list'] = media_list

            self.radiobutton2.set_active(True)

            # Update the treeview
            self.setup_media_tab_update_treeview(liststore)


    def on_all_flag_toggled(self, radiobutton):

        """Called from callback in self.setup_media_tab().

        Enables/disables checking/downloading all media.

        Args:

            radiobutton (Gtk.RadioButton): The widget clicked

        """

        if radiobutton.get_active():
            self.edit_obj.all_flag = False
        else:
            self.edit_obj.all_flag = True


    def on_clear_button_clicked(self, button, liststore):

        """Called by callback in self.setup_media_tab().

        Args:

            button (Gtk.Button): The widget clicked

            liststore (Gtk.ListStore): The treeview's model

        """

        # Update the IV
        self.edit_dict['media_list'] = []
        # Update widgets
        liststore.clear()
        self.radiobutton.set_active(True)


    def on_remove_button_clicked(self, button, combo, treeview):

        """Called by callback in self.setup_media_tab().

        Args:

            button (Gtk.Button): The widget clicked

            combo (Gtk.ComboBox): A combo in which the user has selected a new
                media data object

            treeview (Gtk.TreeView): The list of media data objects

        """

        selection = treeview.get_selection()
        (model, iter) = selection.get_selected()
        if iter is None:

            # Nothing selected
            return

        else:

            name = model[iter][0]

        # Check the media data object exists in the list and in the media data
        #   registry
        media_list = self.retrieve_val('media_list')

        if name in media_list \
        and name in self.app_obj.media_name_dict:

            media_list.remove(name)
            self.edit_dict['media_list'] = media_list

            # Update widgets
            self.setup_media_tab_update_treeview(treeview.get_model())
            if not media_list:
                self.radiobutton.set_active(True)


    def on_start_mode_combo_changed(self, combo, spinbutton, combo2):

        """Called from callback in self.setup_general_tab().

        Sets the IV, and (de)sensitises other widgets.

        Args:

            combo (Gtk.ComboBox): The widget clicked

            spinbutton (Gtk.SpinButton): Another widget to update

            combo2 (Gtk.ComboBox): Another widget to update

        """

        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        self.edit_dict['start_mode'] = model[tree_iter][1]

        if self.edit_dict['start_mode'] == 'scheduled':
            spinbutton.set_sensitive(True)
            combo2.set_sensitive(True)
        else:
            spinbutton.set_sensitive(False)
            combo2.set_sensitive(False)


    def on_video_index_drag_drop(self, treeview, drag_context, x, y, time):

        """Called from callback in self.setup_media_tab().

        Override the usual Gtk handler, and allow
        self.on_video_index_drag_data_received() to collect the results of the
        drag procedure.

        Args:

            treeview (Gtk.TreeView): This tab's treeview

            drag_context (GdkX11.X11DragContext): Data from the drag procedure

            x, y (int): Cell coordinates in the treeview

            time (int): A timestamp

        """

        # Must override the usual Gtk handler
        treeview.stop_emission('drag_drop')

        # The second of these lines cause the 'drag-data-received' signal to be
        #   emitted
        target_list = drag_context.list_targets()
        treeview.drag_get_data(drag_context, target_list[-1], time)


    def on_video_index_drag_data_received(self, treeview, drag_context, x, y, \
    selection_data, info, timestamp):

        """Called from callback in self.setup_media_tab().

        Retrieve the media data object being dragged. update the
        media.Scheduled object, and update the treeview itself.

        Args:

            treeview (Gtk.TreeView): This tab's treeview

            drag_context (GdkX11.X11DragContext): Data from the drag procedure

            x, y (int): Cell coordinates in the treeview

            selection_data (Gtk.SelectionData): Data from the dragged row

            info (int): Ignored

            timestamp (int): Ignored

        """

        # Must override the usual Gtk handler
        treeview.stop_emission('drag_data_received')

        # Get the dragged media data object
        old_selection \
        = self.app_obj.main_win_obj.video_index_treeview.get_selection()
        (model, start_iter) = old_selection.get_selected()
        if start_iter is not None:

            drag_name = model[start_iter][1]

            # Check the media data object hasn't already been added to the
            #   list, and that is still exists in the media data registry
            media_list = self.retrieve_val('media_list')
            if not (drag_name in media_list) \
            and drag_name in self.app_obj.media_name_dict:

                # (System folders can't be dragged here)
                dbid = self.app_obj.media_name_dict[drag_name]
                media_data_obj = self.app_obj.media_reg_dict[dbid]

                if not isinstance(media_data_obj, media.Folder) \
                or not media_data_obj.fixed_flag:

                    media_list.append(drag_name)
                    self.edit_dict['media_list'] = media_list

                    self.radiobutton2.set_active(True)

                    # Update the treeview
                    self.setup_media_tab_update_treeview(treeview.get_model())


class SystemPrefWin(GenericPrefWin):

    """Python class for a 'preference window' to modify various system
    settings.

    Args:

        app_obj (mainapp.TartubeApp): The main application object

        init_mode (str or None): 'db' to open the tab with options for
            switching the Tartube database, 'paths' to open the tab with
            youtube-dl paths, 'live' to open the tab with livestream options,
            'options' to open the tab with the list of download options,
            'custom_dl' to open the tab with custom download preferences. Any
            other value is ignored

    """


    # Standard class methods


    def __init__(self, app_obj, init_mode=None):

        Gtk.Window.__init__(self, title=_('System preferences'))

        if self.is_duplicate(app_obj, init_mode):
            return

        # IV list - class objects
        # -----------------------
        # The mainapp.TartubeApp object
        self.app_obj = app_obj


        # IV list - Gtk widgets
        # ---------------------
        self.grid = None                        # Gtk.Grid
        self.notebook = None                    # Gtk.Notebook
        self.ok_button = None                   # Gtk.Button
        # (IVs used to handle widget changes in the 'General' tab)
        self.radiobutton = None                 # Gtk.RadioButton
        self.radiobutton2 = None                # Gtk.RadioButton
        self.radiobutton3 = None                # Gtk.RadioButton
        self.spinbutton = None                  # Gtk.SpinButton
        self.spinbutton2 = None                 # Gtk.SpinButton
        # (IVs used to handle widget changes in the 'Filesystem' tab)
        self.entry = None                       # Gtk.Entry
        self.entry2 = None                      # Gtk.Entry
        # (IVs used to handle widget changes in the 'Downloader' tab)
        self.path_liststore = None              # Gtk.ListStore
        self.cmd_liststore = None               # Gtk.ListStore
        # (IVs used to handle widget changes in the 'Scheduling' tab)
        self.schedule_liststore = None          # Gtk.ListStore
        # (IVs used to handle widget changes in the 'Options' tab)
        self.options_liststore = None           # Gtk.ListStore
        self.ffmpeg_liststore = None            # Gtk.ListStore
        # (IVs used to open the window at a particular tab)
        self.filesinner_notebook = None         # Gtk.Notebook
        self.operations_inner_notebook = None   # Gtk.Notebook


        # IV list - other
        # ---------------
        # Size (in pixels) of gaps between preference window widgets
        self.spacing_size = self.app_obj.default_spacing_size

        # Code
        # ----

        # Set up the preference window
        self.setup()

        # Automatically open a particular tab, if required
        self.select_tab(init_mode)


    # Public class methods


    def is_duplicate(self, app_obj, init_mode=None):

        """Called by self.__init__.

        Don't open this preference window, if another preference window of the
        same class is already open.

        If 'init_mode' is specified, switch the visible tab in the existing
        preference window (if any)

        Args:

            app_obj (mainapp.TartubeApp): The main application object

            init_mode (str or None): 'db' to open the tab with options for
                switching the Tartube database, 'paths' to open the tab with
                youtube-dl paths, 'live' to open the tab with livestream
                options, 'options' to open the tab with the list of download
                options, 'custom_dl' to open the tab with custom download
                preferences. Any other value is ignored

        Return values:

            True if a duplicate is found, False if not

        """

        for config_win_obj in app_obj.main_win_obj.config_win_list:

            if type(self) == type(config_win_obj):

                # Duplicate found. Make it prominent...
                config_win_obj.present()
                # ...and switch to a particular tab, if required
                config_win_obj.select_tab(init_mode)

                return True

        # Not a duplicate
        return False


#   def setup():                # Inherited from GenericConfigWin


#   def setup_grid():           # Inherited from GenericConfigWin


#   def setup_notebook():       # Inherited from GenericConfigWin


#   def add_notebook_tab():     # Inherited from GenericConfigWin


#   def setup_button_strip():   # Inherited from GenericPrefWin


#   def setup_gap():            # Inherited from GenericConfigWin


    def select_tab(self, init_mode=None):

        """Called by self.__init__().

        On startup, automatically open a particular tab, if required.

        Args:

            init_mode (str): 'db' to open the tab with options for switching
                the Tartube database, 'paths' to open the tab with youtube-dl
                paths, 'live' to open the tab with livestream options,
                'options' to open the tab with the list of download options,
                'custom_dl' to open the tab with custom download preferences.
                Any other value is ignored

        """

        if init_mode is not None:

            if init_mode == 'db':
                self.select_switch_db_tab()
            elif init_mode == 'paths':
                self.select_paths_tab()
            elif init_mode == 'live':
                self.select_livestream_tab()
            elif init_mode == 'options':
                self.select_options_tab()
            elif init_mode == 'custom_dl':
                self.select_custom_dl_tab()


    def select_switch_db_tab(self):

        """Can be called by anything.

        Makes the visible tab the one on which the user can set Tartube's
        data directory (which contains the Tartube database file).
        """

        self.notebook.set_current_page(1)
        self.files_inner_notebook.set_current_page(1)


    def select_paths_tab(self):

        """Can be called by anything.

        Makes the visible tab the one on which the user can set youtube-dl
        options.
        """

        self.notebook.set_current_page(5)


    def select_livestream_tab(self):

        """Can be called by anything.

        Makes the visible tab the one on which the user can set livestream
        options.
        """

        self.notebook.set_current_page(4)
        self.operations_inner_notebook.set_current_page(4)


    def select_options_tab(self):

        """Can be called by anything.

        Makes the visible tab the one on which the a list of download options
        is displayed.
        """

        self.notebook.set_current_page(6)


    def select_custom_dl_tab(self):

        """Can be called by anything.

        Makes the visible tab the one on which the custom download preferences
        are displayed.
        """

        self.notebook.set_current_page(4)
        self.operations_inner_notebook.set_current_page(3)


    # (Setup tabs)


    def setup_tabs(self):

        """Called by self.setup(), .on_button_apply_clicked() and
        .on_button_reset_clicked().

        Sets up the tabs for this preference window.
        """

        self.setup_general_tab()
        self.setup_files_tab()
        self.setup_windows_tab()
        self.setup_scheduling_tab()
        self.setup_operations_tab()
        self.setup_downloader_tab()
        self.setup_options_tab()
        self.setup_output_tab()


    def setup_general_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'General' tab.
        """

        # Add this tab...
        tab, grid = self.add_notebook_tab(_('_General'), 0)

        # ...and an inner notebook...
        inner_notebook = self.add_inner_notebook(grid)

        # ...with its own tabs
        self.setup_general_language_tab(inner_notebook)
        self.setup_general_stability_tab(inner_notebook)
        self.setup_general_modules_tab(inner_notebook)
        self.setup_general_debug_tab(inner_notebook)


    def setup_general_language_tab(self, inner_notebook):

        """Called by self.setup_general_tab().

        Sets up the 'Language' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(_('_Language'), inner_notebook)
        grid_width = 2

        # Language preferences
        self.add_label(grid,
            '<u>' + _('Language preferences') + '</u>',
            0, 0, grid_width, 1,
        )

        label = self.add_label(grid,
            _('Language'),
            0, 1, 1, 1,
        )
        label.set_hexpand(False)

        store = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        for locale in formats.LOCALE_LIST:
            pixbuf = self.app_obj.main_win_obj.pixbuf_dict['flag_' + locale]
            store.append(
                [ pixbuf, formats.LOCALE_DICT[locale] ],
            )

        combo = Gtk.ComboBox.new_with_model(store)
        grid.attach(combo, 1, 1, (grid_width - 1), 1)
        combo.set_hexpand(False)

        renderer_pixbuf = Gtk.CellRendererPixbuf()
        combo.pack_start(renderer_pixbuf, False)
        combo.add_attribute(renderer_pixbuf, 'pixbuf', 0)

        renderer_text = Gtk.CellRendererText()
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, 'text', 1)

        combo.set_active(formats.LOCALE_LIST.index(self.app_obj.custom_locale))
        combo.connect('changed', self.on_locale_combo_changed, grid)


    def setup_general_stability_tab(self, inner_notebook):

        """Called by self.setup_general_tab().

        Sets up the 'Stability' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Stability'),
            inner_notebook,
        )

        grid_width = 2
        label_length \
        = self.app_obj.main_win_obj.exceedingly_long_string_max_len

        # Gtk library
        self.add_label(grid,
            '<u>' + _('Gtk library') + '</u>',
            0, 0, grid_width, 1,
        )

        self.add_label(grid,
            _('Current version of the system\'s Gtk library'),
            0, 1, 1, 1
        )

        entry = self.add_entry(grid,
            'v' + str(self.app_obj.gtk_version_major) + '.' \
            + str(self.app_obj.gtk_version_minor) + '.' \
            + str(self.app_obj.gtk_version_micro),
            False,
            1, 1, 1, 1,
        )
        entry.set_sensitive(False)

        # Gtk stability
        self.add_label(grid,
            '<u>' + _('Gtk stability') + '</u>',
            0, 2, grid_width, 1,
        )

        frame = Gtk.Frame()
        grid.attach(frame, 0, 3, grid_width, 1)
        frame.set_border_width(self.spacing_size)

        vbox = Gtk.VBox()
        frame.add(vbox)

        label = Gtk.Label()
        vbox.pack_start(label, True, True, self.spacing_size)
#        label.set_markup(
#            utils.tidy_up_long_string(
#                _(
#                    'Tartube uses the Gtk graphics library. This library is' \
#                    + ' notoriously unreliable and may even causes crashes.',
#                ),
#                label_length,
#            ) + '\n\n' \
#            + utils.tidy_up_long_string(
#                _(
#                    'If stability is a problem, you can disable some minor' \
#                    + ' cosmetic features.',
#                ),
#                label_length,
#            ) + '\n\n' \
#            + utils.tidy_up_long_string(
#                _(
#                    'Tartube\'s functionality is not affected. You can do' \
#                    + ' anything, even when cosmetic features are disabled.',
#                ),
#                label_length,
#            ),
#        )
        label.set_markup(
            utils.tidy_up_long_string(
                _(
                    'Tartube uses the Gtk graphics library. This library is' \
                    + ' notoriously unreliable and may even causes crashes.',
                ),
                label_length,
            ) + '\n\n' \
            + utils.tidy_up_long_string(
                _(
                    'By default, some cosmetic features are disabled (for' \
                    + ' example, in the Videos tab, the list of videos is' \
                    + ' not updated until the end of a download operation).',
                ),
                label_length,
            ) + '\n\n' \
            + utils.tidy_up_long_string(
                _(
                    'If you think that your system Gtk has been fixed (or' \
                    + ' if you want to test Gtk stability), you can' \
                    + ' re-enable the cosmetic features.',
                ),
                label_length,
            ),
        )

        checkbutton = self.add_checkbutton(grid,
            _(
                'Disable some cosmetic features to prevent crashes and' \
                + ' other issues',
            ),
            self.app_obj.gtk_emulate_broken_flag,
            True,               # Can be toggled by user
            0, 4, grid_width, 1,
        )
        checkbutton.set_hexpand(False)
        checkbutton.connect('toggled', self.on_gtk_emulate_button_toggled)


    def setup_general_modules_tab(self, inner_notebook):

        """Called by self.setup_general_tab().

        Sets up the 'Modules' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(_('_Modules'), inner_notebook)
        grid_width = 2

        # Module availability
        self.add_label(grid,
            '<u>' + _('Module availability') + '</u>',
            0, 0, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _(
            'feedparser module is available (required for detecting' \
            + ' livestreams)',
            ),
            mainapp.HAVE_FEEDPARSER_FLAG,
            False,                      # Can't be toggled by user
            0, 1, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _('matplotlib module is available (draws graphs)'),
            mainapp.HAVE_MATPLOTLIB_FLAG,
            False,                      # Can't be toggled by user
            0, 2, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _(
            'moviepy module is available (finds the length of videos, if' \
            + ' unknown)',
            ),
            mainapp.HAVE_MOVIEPY_FLAG,
            False,                      # Can't be toggled by user
            0, 3, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _(
            'playsound module is available (sound an alarm when a livestream' \
            + ' starts)',
            ),
            mainapp.HAVE_PLAYSOUND_FLAG,
            False,                      # Can't be toggled by user
            0, 4, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _(
            'XDG module is available (saves the config file in the standard' \
            + ' location)',
            ),
            mainapp.HAVE_XDG_FLAG,
            False,                      # Can't be toggled by user
            0, 5, grid_width, 1,
        )

        self.add_checkbutton(grid,
            _(
            'Notify module is available (shows desktop notifications; Linux/' \
            + '*BSD only)',
            ),
            mainapp.HAVE_NOTIFY_FLAG,
            False,                      # Can't be toggled by user
            0, 6, grid_width, 1,
        )

        # Module preferences
        self.add_label(grid,
            '<u>' + _('Module preferences') + '</u>',
            0, 7, grid_width, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _(
            'Use \'moviepy\' module to get a video\'s duration, if not known'
            + ' (may be slow)',
            ),
            self.app_obj.use_module_moviepy_flag,
            True,                   # Can be toggled by user
            0, 8, grid_width, 1,
        )
        checkbutton.connect('toggled', self.on_moviepy_button_toggled)
        if not mainapp.HAVE_MOVIEPY_FLAG:
            checkbutton.set_sensitive(False)

        self.add_label(grid,
            _('Timeout applied when moviepy checks a video file'),
            0, 9, 1, 1,
        )

        spinbutton = self.add_spinbutton(grid,
            0,
            60,
            1,                  # Step
            self.app_obj.refresh_moviepy_timeout,
            1, 9, 1, 1,
        )
        spinbutton.connect(
            'value-changed',
            self.on_moviepy_timeout_spinbutton_changed,
        )


    def setup_general_debug_tab(self, inner_notebook):

        """Called by self.setup_general_tab().

        Sets up the 'Debug' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Debugging'),
            inner_notebook,
        )

        grid_width = 2

        # Debugging preferences
        self.add_label(grid,
            '<u>' + _('Debugging preferences') + '</u>',
            0, 0, grid_width, 1,
        )

        self.add_label(grid,
            '<i>' + _(
            'Debug messages are only visible in the terminal window (these' \
            + ' settings are not saved)',
            ) + '</i>',
            0, 1, grid_width, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _('Enable application debug messages (code in mainapp.py)'),
            mainapp.DEBUG_FUNC_FLAG,
            True,                   # Can be toggled by user
            0, 2, grid_width, 1,
        )
        checkbutton.set_active(mainapp.DEBUG_FUNC_FLAG)
        # (Signal connect appears below)

        checkbutton2 = self.add_checkbutton(grid,
            _('...but don\'t show timer debug messages'),
            mainapp.DEBUG_NO_TIMER_FUNC_FLAG,
            True,                   # Can be toggled by user
            1, 3, 1, 1,
        )
        checkbutton2.set_active(mainapp.DEBUG_NO_TIMER_FUNC_FLAG)
        if not mainapp.DEBUG_FUNC_FLAG:
            checkbutton2.set_sensitive(False)
        # (Signal connect appears below)

        checkbutton3 = self.add_checkbutton(grid,
            _('Enable main winddow debug messages (code in mainwin.py)'),
            mainwin.DEBUG_FUNC_FLAG,
            True,                   # Can be toggled by user
            0, 4, grid_width, 1,
        )
        checkbutton3.set_active(mainwin.DEBUG_FUNC_FLAG)
        # (Signal connect appears below)

        checkbutton4 = self.add_checkbutton(grid,
            _('...but don\'t show timer debug messages'),
            mainwin.DEBUG_NO_TIMER_FUNC_FLAG,
            True,                   # Can be toggled by user
            1, 5, 1, 1,
        )
        checkbutton4.set_active(mainwin.DEBUG_NO_TIMER_FUNC_FLAG)
        if not mainwin.DEBUG_FUNC_FLAG:
            checkbutton4.set_sensitive(False)
        # (Signal connect appears below)

        checkbutton5 = self.add_checkbutton(grid,
            _('Enabled downloader debug messages (code in downloads.py)'),
            downloads.DEBUG_FUNC_FLAG,
            True,                   # Can be toggled by user
            0, 6, grid_width, 1,
        )
        checkbutton5.set_active(downloads.DEBUG_FUNC_FLAG)
        # (Signal connect appears below)

        # (Signal connects from above)
        checkbutton.connect(
            'toggled', self.on_system_debug_toggled,
            'main_app',
            checkbutton2,
        )
        checkbutton2.connect(
            'toggled',
            self.on_system_debug_toggled,
            'main_app_no_timer',
        )
        checkbutton3.connect(
            'toggled', self.on_system_debug_toggled,
            'main_win',
            checkbutton4,
        )
        checkbutton4.connect(
            'toggled',
            self.on_system_debug_toggled,
            'main_win_no_timer',
        )
        checkbutton5.connect(
            'toggled',
            self.on_system_debug_toggled,
            'downloads',
        )

        # debug.txt
        self.add_label(grid,
            '<u>debug.txt</u>',
            0, 7, grid_width, 1,
        )

        self.add_label(grid,
            '<i>' + _(
            'Debugging messages are also visible if an empty file called' \
            + ' debug.txt exists here:',
            ) + '</i>',
            0, 8, grid_width, 1,
        )

        self.entry = self.add_entry(grid,
            os.path.abspath(os.path.join(sys.path[0], 'debug.txt')),
            False,
            0, 9, grid_width, 1,
        )
        self.entry.set_sensitive(False)


    def setup_files_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Files' tab.
        """

        # Add this tab...
        tab, grid = self.add_notebook_tab(_('_Files'), 0)

        # ...and an inner notebook...
        self.files_inner_notebook = self.add_inner_notebook(grid)

        # ...with its own tabs
        self.setup_files_device_tab(self.files_inner_notebook)
        self.setup_files_database_tab(self.files_inner_notebook)
        self.setup_files_backups_tab(self.files_inner_notebook)
        self.setup_files_videos_tab(self.files_inner_notebook)
        self.setup_files_temp_folders_tab(self.files_inner_notebook)
        self.setup_files_statistics_tab(self.files_inner_notebook)
        if mainapp.HAVE_MATPLOTLIB_FLAG:
            self.setup_files_history_tab(self.files_inner_notebook)


    def setup_files_device_tab(self, inner_notebook):

        """Called by self.setup_files_tab().

        Sets up the 'Device' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(_('_Device'), inner_notebook)
        grid_width = 3

        # Device preferences
        self.add_label(grid,
            '<u>' + _('Device preferences') + '</u>',
            0, 0, grid_width, 1,
        )

        self.add_label(grid,
            _('Size of device (in Mb)'),
            0, 3, 1, 1,
        )

        self.entry = self.add_entry(grid,
            str(utils.disk_get_total_space(self.app_obj.data_dir)),
            False,
            1, 3, 2, 1,
        )
        self.entry.set_sensitive(False)

        self.add_label(grid,
            _('Free space on device (in Mb)'),
            0, 4, 1, 1,
        )

        self.entry2 = self.add_entry(grid,
            str(utils.disk_get_free_space(self.app_obj.data_dir)),
            False,
            1, 4, 2, 1,
        )
        self.entry2.set_sensitive(False)

        checkbutton = self.add_checkbutton(grid,
            _('Warn user if disk space is less than'),
            self.app_obj.disk_space_warn_flag,
            True,                   # Can be toggled by user
            0, 5, 1, 1,
        )
        # (Signal connect appears below)

        spinbutton = self.add_spinbutton(grid,
            0, None,
            self.app_obj.disk_space_increment,
            self.app_obj.disk_space_warn_limit,
            1, 5, 2, 1,
        )
        if not self.app_obj.disk_space_warn_flag:
            spinbutton.set_sensitive(False)
        # (Signal connect appears below)

        checkbutton2 = self.add_checkbutton(grid,
            _('Halt downloads if disk space is less than'),
            self.app_obj.disk_space_stop_flag,
            True,                   # Can be toggled by user
            0, 6, 1, 1,
        )
        # (Signal connect appears below)

        spinbutton2 = self.add_spinbutton(grid,
            0, None,
            self.app_obj.disk_space_increment,
            self.app_obj.disk_space_stop_limit,
            1, 6, 2, 1,
        )
        if not self.app_obj.disk_space_stop_flag:
            spinbutton2.set_sensitive(False)
        # (Signal connect appears below)

        # (Signal connects from above)
        checkbutton.connect(
            'toggled',
            self.on_disk_warn_button_toggled,
            spinbutton,
        )
        spinbutton.connect(
            'value-changed',
            self.on_disk_warn_spinbutton_changed,
        )
        checkbutton2.connect(
            'toggled',
            self.on_disk_stop_button_toggled,
            spinbutton2,
        )
        spinbutton2.connect(
            'value-changed',
            self.on_disk_stop_spinbutton_changed,
        )

        # Configuration preferences
        self.add_label(grid,
            '<u>' + _('Configuration preferences') + '</u>',
            0, 7, grid_width, 1,
        )

        self.add_label(grid,
            _('Tartube configuration file loaded from:'),
            0, 8, grid_width, 1,
        )

        entry3 = self.add_entry(grid,
            self.app_obj.get_config_path(),
            False,
            0, 9, grid_width, 1,
        )
        entry3.set_sensitive(False)


    def setup_files_database_tab(self, inner_notebook):

        """Called by self.setup_files_tab().

        Sets up the 'Database' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(_('D_atabase'), inner_notebook)

        grid_width = 6

        # Database preferences
        self.add_label(grid,
            '<u>' + _('Database preferences') + '</u>',
            0, 0, grid_width, 1,
        )

        label = self.add_label(grid,
            _('Tartube data folder'),
            0, 1, 1, 1,
        )
        label.set_hexpand(False)

        entry = self.add_entry(grid,
            self.app_obj.data_dir,
            False,
            1, 1, (grid_width - 1), 1,
        )
        entry.set_sensitive(False)

        button = Gtk.Button(_('Add new database'))
        grid.attach(button, 1, 2, 2, 1)
        button.set_tooltip_text(_('Change to a different data folder'))
        button.connect(
            'clicked',
            self.on_data_dir_change_button_clicked,
            entry,
        )

        button2 = Gtk.Button(_('Check and repair database'))
        grid.attach(button2, 3, 2, 3, 1)
        button2.set_tooltip_text(
            _('Check for inconsistencies, and repair them'),
        )
        button2.connect('clicked', self.on_data_check_button_clicked)

        label = self.add_label(grid,
            _('Recent data folders'),
            0, 3, 1, 1,
        )
        label.set_hexpand(False)

        treeview, liststore = self.add_treeview(grid,
            1, 3, (grid_width - 1), 1,
        )
        treeview.set_vexpand(False)
        for item in self.app_obj.data_dir_alt_list:
            liststore.append([item])

        button3 = Gtk.Button(_('Switch'))
        grid.attach(button3, 1, 4, 1, 1)
        button3.set_tooltip_text(_('Switch to the selected data folder'))
        button3.set_sensitive(False)
        button3.connect(
            'clicked',
            self.on_data_dir_switch_button_clicked,
            button,
            treeview,
            entry,
        )

        button4 = Gtk.Button(_('Forget'))
        grid.attach(button4, 2, 4, 1, 1)
        button4.set_tooltip_text(
            _('Remove the selected data folder from the list'),
        )
        button4.set_sensitive(False)
        button4.connect(
            'clicked',
            self.on_data_dir_forget_button_clicked,
            treeview,
        )

        button5 = Gtk.Button(_('Forget all'))
        grid.attach(button5, 3, 4, 1, 1)
        button5.set_tooltip_text(
            _('Forget every folder in this list (except the current one)'),
        )
        if len(self.app_obj.data_dir_alt_list) <= 1:
            button5.set_sensitive(False)
        button5.connect(
            'clicked',
            self.on_data_dir_forget_all_button_clicked,
            treeview,
        )

        button6 = Gtk.Button(_('Move up'))
        grid.attach(button6, 4, 4, 1, 1)
        button6.set_tooltip_text(
            _('Move the selected folder up the list'),
        )
        button6.set_sensitive(False)
        # (Signal connect appears below)

        button7 = Gtk.Button(_('Move down'))
        grid.attach(button7, 5, 4, 1, 1)
        button7.set_tooltip_text(
            _('Move the selected folder down the list'),
        )
        button7.set_sensitive(False)
        # (Signal connect appears below)

        # (Signal connects from above)
        button6.connect(
            'clicked',
            self.on_data_dir_move_up_button_clicked,
            treeview,
            liststore,
            button7,
        )
        button7.connect(
            'clicked',
            self.on_data_dir_move_down_button_clicked,
            treeview,
            liststore,
            button6,
        )

        # (Add a second grid, so widget positioning on the first one isn't
        #   messed up)
        grid2 = Gtk.Grid()
        grid.attach(grid2, 0, 5, grid_width, 1)

        checkbutton = self.add_checkbutton(grid2,
            _(
            'On startup, load the first database on the list (not the most' \
            + ' recently-use one)',
            ),
            self.app_obj.data_dir_use_first_flag,
            True,               # Can be toggled by user
            0, 0, 2, 1,
        )
        checkbutton.connect('toggled', self.on_use_first_button_toggled)

        checkbutton2 = self.add_checkbutton(grid2,
            _('If one database is in use, try to load others'),
            self.app_obj.data_dir_use_list_flag,
            True,               # Can be toggled by user
            0, 1, 1, 1,
        )
        checkbutton2.connect('toggled', self.on_use_list_button_toggled)

        checkbutton3 = self.add_checkbutton(grid2,
            _('Add new data directories to this list'),
            self.app_obj.data_dir_add_from_list_flag,
            True,               # Can be toggled by user
            1, 1, 1, 1,
        )
        checkbutton3.connect('toggled', self.on_add_from_list_button_toggled)

        # Everything must be desensitised, if load/save is disabled
        if self.app_obj.disable_load_save_flag:
            button.set_sensitive(False)
            button2.set_sensitive(False)
            button3.set_sensitive(False)
            button4.set_sensitive(False)
            button5.set_sensitive(False)
            button6.set_sensitive(False)
            button7.set_sensitive(False)
            checkbutton.set_sensitive(False)
            checkbutton2.set_sensitive(False)
            checkbutton3.set_sensitive(False)

        # (More signal connects from above)
        treeview.connect(
            'cursor-changed',
            self.on_data_dir_cursor_changed,
            button3,    # Switch
            button4,    # Forget
            button5,    # Forget all
            button6,    # Move up
            button7,    # Move down
        )


    def setup_files_backups_tab(self, inner_notebook):

        """Called by self.setup_files_tab().

        Sets up the 'Backups' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(_('_Backups'), inner_notebook)

        # Backup preferences
        self.add_label(grid,
            '<u>' + _('Backup preferences') + '</u>',
            0, 0, 1, 1,
        )
        self.add_label(grid,
            '<i>' + _(
                'When saving a database file, Tartube makes a backup copy of' \
                + ' it (in case something goes wrong)',
            ) + '</i>',
            0, 1, 1, 1,
        )

        radiobutton = self.add_radiobutton(grid,
            None,
            _(
            'Delete the backup file as soon as the save procedure is' \
            + ' finished',
            ),
            0, 2, 1, 1,
        )
        # (Signal connect appears below)

        radiobutton2 = self.add_radiobutton(grid,
            radiobutton,
            _(
            'Keep the backup file, replacing any previous backup file',
            ),
            0, 3, 1, 1,
        )
        if self.app_obj.db_backup_mode == 'single':
            radiobutton2.set_active(True)
        # (Signal connect appears below)

        radiobutton3 = self.add_radiobutton(grid,
            radiobutton2,
            _(
            'Make a new backup file once per day, after the day\'s first' \
            + ' save procedure',
            ),
            0, 4, 1, 1,
        )
        if self.app_obj.db_backup_mode == 'daily':
            radiobutton3.set_active(True)
        # (Signal connect appears below)

        radiobutton4 = self.add_radiobutton(grid,
            radiobutton3,
            _('Make a new backup file for every save procedure'),
            0, 5, 1, 1,
        )
        if self.app_obj.db_backup_mode == 'always':
            radiobutton4.set_active(True)
        # (Signal connect appears below)

        # (Signal connects from above)
        radiobutton.connect(
            'toggled',
            self.on_backup_button_toggled,
            'default',
        )

        radiobutton2.connect(
            'toggled',
            self.on_backup_button_toggled,
            'single',
        )

        radiobutton3.connect(
            'toggled',
            self.on_backup_button_toggled,
            'daily',
        )

        radiobutton4.connect(
            'toggled',
            self.on_backup_button_toggled,
            'always',
        )


    def setup_files_videos_tab(self, inner_notebook):

        """Called by self.setup_files_tab().

        Sets up the 'Videos' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Videos'),
            inner_notebook,
        )

        grid_width = 3

        # Automatic video deletion preferences
        self.add_label(grid,
            '<u>' + _('Automatic video deletion preferences') + '</u>',
            0, 0, grid_width, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _('Automatically delete downloaded videos after this many days'),
            self.app_obj.auto_delete_flag,
            True,               # Can be toggled by user
            0, 1, (grid_width - 1), 1,
        )
        # (Signal connect appears below)

        spinbutton = self.add_spinbutton(grid,
            1, 999, 1, self.app_obj.auto_delete_days,
            2, 1, 1, 1,
        )
        # (Signal connect appears below)

        checkbutton2 = self.add_checkbutton(grid,
            _('...but only delete videos which have been watched'),
            self.app_obj.auto_delete_watched_flag,
            True,               # Can be toggled by user
            0, 2, grid_width, 1,
        )
        # (Signal connect appears below)
        if not self.app_obj.auto_delete_flag:
            checkbutton2.set_sensitive(False)

        # (Signal connects from above)
        checkbutton.connect(
            'toggled',
            self.on_auto_delete_button_toggled,
            spinbutton,
            checkbutton2,
        )
        spinbutton.connect(
            'value-changed',
            self.on_auto_delete_spinbutton_changed,
        )
        checkbutton2.connect('toggled', self.on_delete_watched_button_toggled)

        # Video matching preferences
        self.add_label(grid,
            '<u>' + _('Video matching preferences') + '</u>',
            0, 3, grid_width, 1,
        )

        self.add_label(grid,
            _('When matching videos on the filesystem:'),
            0, 4, grid_width, 1,
        )

        self.radiobutton = self.add_radiobutton(grid,
            None,
            _('The video names must match exactly'),
            0, 5, grid_width, 1,
        )
        # (Signal connect appears below)

        self.radiobutton2 = self.add_radiobutton(grid,
            self.radiobutton,
            _('The first # characters must match exactly'),
            0, 6, (grid_width - 1), 1,
        )
        # (Signal connect appears below)

        self.spinbutton = self.add_spinbutton(grid,
            1, 999, 1, self.app_obj.match_first_chars,
            2, 6, 1, 1,
        )
        # (Signal connect appears below)

        self.radiobutton3 = self.add_radiobutton(grid,
            self.radiobutton2,
            _(
            'Ignore the last # characters; the remaining name must match' \
            + ' exactly',
            ),
            0, 7, (grid_width - 1), 1,
        )
        # (Signal connect appears below)

        self.spinbutton2 = self.add_spinbutton(grid,
            1, 999, 1, self.app_obj.match_ignore_chars,
            2, 7, 1, 1,
        )
        # (Signal connect appears below)

        # (Widgets are sensitised/desensitised, based on the radiobutton)
        if self.app_obj.match_method == 'exact_match':
            self.spinbutton.set_sensitive(False)
            self.spinbutton2.set_sensitive(False)
        elif self.app_obj.match_method == 'match_first':
            self.radiobutton2.set_active(True)
            self.spinbutton2.set_sensitive(False)
        else:
            self.radiobutton3.set_active(True)
            self.spinbutton.set_sensitive(False)

        # (Signal connects from above)
        self.radiobutton.connect('toggled', self.on_match_button_toggled)
        self.radiobutton2.connect('toggled', self.on_match_button_toggled)
        self.radiobutton3.connect('toggled', self.on_match_button_toggled)
        self.spinbutton.connect(
            'value-changed',
            self.on_match_spinbutton_changed,
        )
        self.spinbutton2.connect(
            'value-changed',
            self.on_match_spinbutton_changed,
        )


    def setup_files_temp_folders_tab(self, inner_notebook):

        """Called by self.setup_files_tab().

        Sets up the 'Temporary folders' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Temporary folders'),
            inner_notebook,
        )

        # Temporary folder preferences
        self.add_label(grid,
            '<u>' + _('Temporary folder preferences') + '</u>',
            0, 0, 1, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _('Empty temporary folders when Tartube shuts down'),
            self.app_obj.delete_on_shutdown_flag,
            True,               # Can be toggled by user
            0, 1, 1, 1,
        )
        # (Signal connect appears below)

        self.add_label(grid,
            '<i>' + _(
                '(N.B. Temporary folders are always emptied when Tartube' \
                + ' starts up)',
            ) + '</i>',
            0, 2, 1, 1,
        )

        checkbutton2 = self.add_checkbutton(grid,
            _(
            'Open temporary folders (on the desktop) when Tartube shuts down',
            ),
            self.app_obj.open_temp_on_desktop_flag,
            True,               # Can be toggled by user
            0, 3, 1, 1,
        )
        checkbutton2.connect('toggled', self.on_open_desktop_button_toggled)
        if self.app_obj.delete_on_shutdown_flag:
            checkbutton2.set_sensitive(False)

        # (Signal connects from above)
        checkbutton.connect(
            'toggled',
            self.on_delete_shutdown_button_toggled,
            checkbutton2,
        )


    def setup_files_statistics_tab(self, inner_notebook):

        """Called by self.setup_files_tab().

        Sets up the 'Statistics' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Statistics'),
            inner_notebook,
        )

        grid_width = 4

        self.add_label(grid,
            '<u>' + _('Statistics') + '</u>',
            0, 0, grid_width, 1,
        )

        self.add_label(grid,
            _('The Tartube database contains:'),
            0, 1, grid_width, 1,
        )

        self.add_label(grid,
            _('Videos'),
            0, 2, 1, 1,
        )

        entry = self.add_entry(grid,
            None,
            False,
            1, 2, 1, 1,
        )

        self.add_label(grid,
            _('Downloaded'),
            0, 3, 1, 1,
        )

        entry2 = self.add_entry(grid,
            None,
            False,
            1, 3, 1, 1,
        )

        self.add_label(grid,
            _('Other'),
            0, 4, 1, 1,
        )

        entry3 = self.add_entry(grid,
            None,
            False,
            1, 4, 1, 1,
        )

        self.add_label(grid,
            _('Channels'),
            2, 2, 1, 1,
        )

        entry4 = self.add_entry(grid,
            None,
            False,
            3, 2, 1, 1,
        )

        self.add_label(grid,
            _('Playlists'),
            2, 3, 1, 1,
        )

        entry5 = self.add_entry(grid,
            None,
            False,
            3, 3, 1, 1,
        )

        self.add_label(grid,
            _('Custom folders'),
            2, 4, 1, 1,
        )

        entry6 = self.add_entry(grid,
            None,
            False,
            3, 4, 1, 1,
        )

        # Initialise the entries. Commented out so that the preference window
        #   will still appear quickly for enormous databases
#        self.setup_files_statistics_tab_recalculate(
#            entry,
#            entry2,
#            entry3,
#            entry4,
#            entry5,
#            entry6,
#        )

        button = Gtk.Button()
        grid.attach(button, 3, 5, 1, 1)
        button.set_label(_('Calculate'))
        button.connect(
            'clicked',
            self.on_recalculate_stats_button_clicked,
            entry,
            entry2,
            entry3,
            entry4,
            entry5,
            entry6,
        )


    def setup_files_statistics_tab_recalculate(self, entry, entry2, entry3,
    entry4, entry5, entry6):

        """Called by self.setup_files_statistics_tab and
        .on_recalculate_stats_button_clicked().

        Args:

            entry, entry2, entry3, entry4, entry5, entry6 (Gtk.Entry): The
                entry boxes to update

        """

        video_count = 0
        dl_count = 0
        not_dl_count = 0
        channel_count = 0
        playlist_count = 0
        folder_count = 0

        # Get number of videos, channels, playlists and sub-folders, and also
        #   downloaded/not downloaded videos
        # Ignore fixed (system) folders
        for media_data_obj in self.app_obj.media_reg_dict.values():

            if isinstance(media_data_obj, media.Video):

                video_count += 1

                if media_data_obj.dl_flag:
                    dl_count += 1
                else:
                    not_dl_count += 1

            elif isinstance(media_data_obj, media.Channel):

                channel_count += 1

            elif isinstance(media_data_obj, media.Playlist):

                playlist_count += 1

            elif isinstance(media_data_obj, media.Folder) \
            and not media_data_obj.fixed_flag:

                folder_count += 1

        entry.set_text(str(video_count))
        entry2.set_text(str(dl_count))
        entry3.set_text(str(not_dl_count))
        entry4.set_text(str(channel_count))
        entry5.set_text(str(playlist_count))
        entry6.set_text(str(folder_count))


    def setup_files_history_tab(self, inner_notebook):

        """Called by self.setup_files_tab().

        Sets up the 'History' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_History'),
            inner_notebook,
        )

        grid_width = 6

        self.add_label(grid,
            '<u>' + _('Download history') + '</u>',
            0, 0, grid_width, 1,
        )

        # Add combos to customise the graph
        combo, combo2, combo3, combo4, combo5 = self.add_combos_for_graphs(
            grid,
            1,
        )

        # Add a button which, when clicked, draws the graph using the
        #   customisation options specified by the combos
        button = Gtk.Button()
        grid.attach(button, 5, 1, 1, 1)
        button.set_label(_('Draw'))
        # (Signal connect appears below)

        # Add a box, inside which we draw graphs
        hbox = Gtk.HBox()
        grid.attach(hbox, 0, 2, grid_width, 1)
        hbox.set_hexpand(True)
        hbox.set_vexpand(True)

        # (Signal connects from above)
        button.connect(
            'clicked', self.on_button_draw_graph_clicked,
            hbox,
            combo,
            combo2,
            combo3,
            combo4,
            combo5,
        )


    def setup_windows_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Window' tab.
        """

        # Add this tab...
        tab, grid = self.add_notebook_tab(_('_Windows'), 0)

        # ...and an inner notebook...
        inner_notebook = self.add_inner_notebook(grid)

        # ...with its own tabs
        self.setup_windows_main_window_tab(inner_notebook)
        self.setup_windows_videos_tab(inner_notebook)
        self.setup_windows_drag_tab(inner_notebook)
        self.setup_windows_system_tray_tab(inner_notebook)
        self.setup_windows_dialogues_tab(inner_notebook)
        self.setup_windows_errors_warnings_tab(inner_notebook)
        self.setup_windows_websites_tab(inner_notebook)


    def setup_windows_main_window_tab(self, inner_notebook):

        """Called by self.setup_windows_tab().

        Sets up the 'Main Window' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Main window'),
            inner_notebook,
        )

        # Main window preferences
        self.add_label(grid,
            '<u>' + _('Main window preferences') + '</u>',
            0, 0, 1, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _('Remember the size of the main window when shutting down'),
            self.app_obj.main_win_save_size_flag,
            True,                   # Can be toggled by user
            0, 1, 1, 1,
        )
        # (Signal connect appears below)

        checkbutton2 = self.add_checkbutton(grid,
            _('Also remember the position of main window sliders'),
            self.app_obj.main_win_save_slider_flag,
            True,                   # Can be toggled by user
            0, 2, 1, 1,
        )
        checkbutton2.connect('toggled', self.on_remember_slider_button_toggled)
        if not self.app_obj.main_win_save_size_flag:
            checkbutton2.set_sensitive(False)

        # (Signal connect from above)
        checkbutton.connect(
            'toggled',
            self.on_remember_size_button_toggled,
            checkbutton2,
        )

        checkbutton3 = self.add_checkbutton(grid,
            _('Don\'t show the main window toolbar'),
            self.app_obj.toolbar_hide_flag,
            True,                   # Can be toggled by user
            0, 3, 1, 1,
        )
        # (Signal connect appears below)

        checkbutton4 = self.add_checkbutton(grid,
            _('Don\'t show labels in the main window toolbar'),
            self.app_obj.toolbar_squeeze_flag,
            True,                   # Can be toggled by user
            0, 4, 1, 1,
        )
        checkbutton4.connect('toggled', self.on_squeeze_button_toggled)
        if self.app_obj.toolbar_hide_flag:
            checkbutton4.set_sensitive(False)

        # (Signal connect from above)
        checkbutton3.connect(
            'toggled',
            self.on_hide_toolbar_button_toggled,
            checkbutton4,
        )

        checkbutton5 = self.add_checkbutton(grid,
            _(
            'Replace stock icons with custom icons (in case stock icons' \
            + ' are not visible)',
            ),
            self.app_obj.show_custom_icons_flag,
            True,                   # Can be toggled by user
            0, 5, 1, 1,
        )
        checkbutton5.connect('toggled', self.on_show_custom_icons_toggled)

        checkbutton6 = self.add_checkbutton(grid,
            _('Show tooltips for videos, channels, playlists and folders'),
            self.app_obj.show_tooltips_flag,
            True,                   # Can be toggled by user
            0, 6, 1, 1,
        )
        # (Signal connect appears below)

        checkbutton7 = self.add_checkbutton(grid,
            _('Show errors/warnings in tooltips (but not in the Videos tab)'),
            self.app_obj.show_tooltips_extra_flag,
            True,                   # Can be toggled by user
            0, 7, 1, 1,
        )
        checkbutton7.connect('toggled', self.on_show_tooltips_extra_toggled)
        if not self.app_obj.show_tooltips_flag:
            checkbutton7.set_sensitive(False)

        # (Signal connect from above)
        checkbutton6.connect(
            'toggled',
            self.on_show_tooltips_toggled,
            checkbutton7,
        )

        checkbutton8 = self.add_checkbutton(grid,
            _(
            'Disable the \'Download all\' buttons in the toolbar and the' \
            + ' Videos Tab',
            ),
            self.app_obj.disable_dl_all_flag,
            True,                   # Can be toggled by user
            0, 8, 1, 1,
        )
        checkbutton8.connect('toggled', self.on_disable_dl_all_toggled)

        checkbutton9 = self.add_checkbutton(grid,
            _(
            'In the Progress Tab, hide finished videos / channels / playlists',
            ),
            self.app_obj.progress_list_hide_flag,
            True,                   # Can be toggled by user
            0, 9, 1, 1,
        )
        checkbutton9.connect('toggled', self.on_hide_button_toggled)

        checkbutton10 = self.add_checkbutton(grid,
            _('In the Progress Tab, show results in reverse order'),
            self.app_obj.results_list_reverse_flag,
            True,                   # Can be toggled by user
            0, 10, 1, 1,
        )
        checkbutton10.connect('toggled', self.on_reverse_button_toggled)

        checkbutton11 = self.add_checkbutton(grid,
            _('When Tartube starts, automatically open the Classic Mode tab'),
            self.app_obj.show_classic_tab_on_startup_flag,
            True,               # Can be toggled by user
            0, 11, 1, 1,
        )
        checkbutton11.connect(
            'toggled',
            self.on_show_classic_mode_button_toggled,
        )
        if __main__.__pkg_no_download_flag__:
            checkbutton11.set_sensitive(False)

        checkbutton12 = self.add_checkbutton(grid,
            _(
            'In the Classic Mode Tab, when adding URLs, remove duplicates' \
            + ' rather than retaining them',
            ),
            self.app_obj.classic_duplicate_remove_flag,
            True,                   # Can be toggled by user
            0, 12, 1, 1,
        )
        checkbutton12.connect(
            'toggled',
            self.on_remove_duplicate_button_toggled,
        )

        checkbutton13 = self.add_checkbutton(grid,
            _(
            'In the Errors/Warnings Tab, don\'t reset the tab text when' \
            + ' it is clicked',
            ),
            self.app_obj.system_msg_keep_totals_flag,
            True,                   # Can be toggled by user
            0, 13, 1, 1,
        )
        checkbutton13.connect('toggled', self.on_system_keep_button_toggled)


    def setup_windows_videos_tab(self, inner_notebook):

        """Called by self.setup_windows_tab().

        Sets up the 'Tabs' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(_('_Videos'), inner_notebook)

        grid_width = 2

        # Video Index preferences
        self.add_label(grid,
            '<u>' + _('Video Index (left side of the Videos Tab)') + '</u>',
            0, 0, grid_width, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _(
            'Show smaller icons in the Video Index',
            ),
            self.app_obj.show_small_icons_in_index_flag,
            True,                   # Can be toggled by user
            0, 2, grid_width, 1,
        )
        checkbutton.connect('toggled', self.on_show_small_icons_toggled)

        checkbutton2 = self.add_checkbutton(grid,
            _(
            'In the Video Index, show detailed statistics about the videos' \
            + ' in each channel / playlist / folder',
            ),
            self.app_obj.complex_index_flag,
            True,               # Can be toggled by user
            0, 3, grid_width, 1,
        )
        checkbutton2.connect('toggled', self.on_complex_button_toggled)

        checkbutton3 = self.add_checkbutton(grid,
            _(
            'After clicking on a folder, automatically expand/collapse the' \
            + ' tree around it',
            ),
            self.app_obj.auto_expand_video_index_flag,
            True,                   # Can be toggled by user
            0, 4, grid_width, 1,
        )
        # (Signal connect appears below)

        checkbutton4 = self.add_checkbutton(grid,
            _(
            'Expand the whole tree, not just the level beneath the clicked' \
            + ' folder',
            ),
            self.app_obj.full_expand_video_index_flag,
            True,                   # Can be toggled by user
            0, 5, grid_width, 1,
        )
        if not self.app_obj.auto_expand_video_index_flag:
            checkbutton4.set_sensitive(False)
        # (Signal connect appears below)

        # (Signal connects from above)
        checkbutton3.connect(
            'toggled',
            self.on_expand_tree_toggled,
            checkbutton4,
        )
        checkbutton4.connect('toggled', self.on_expand_full_tree_toggled)

        # Video Catalogue preferences
        self.add_label(grid,
            '<u>' + _('Video Catalogue (right side of the Videos Tab)') \
            + '</u>',
            0, 6, grid_width, 1,
        )

        checkbutton5 = self.add_checkbutton(grid,
            _(
            'Show \'today\' and \'yesterday\' as the date, when possible',
            ),
            self.app_obj.show_pretty_dates_flag,
            True,                   # Can be toggled by user
            0, 7, grid_width, 1,
        )
        checkbutton5.connect('toggled', self.on_pretty_date_button_toggled)

        checkbutton6 = self.add_checkbutton(grid,
            _(
            'Draw a frame around each video',
            ),
            self.app_obj.catalogue_draw_frame_flag,
            True,                   # Can be toggled by user
            0, 8, grid_width, 1,
        )
        checkbutton6.connect('toggled', self.on_draw_frame_button_toggled)

        checkbutton7 = self.add_checkbutton(grid,
            _(
            'Draw status icons for each video',
            ),
            self.app_obj.catalogue_draw_icons_flag,
            True,                   # Can be toggled by user
            0, 9, grid_width, 1,
        )
        checkbutton7.connect('toggled', self.on_draw_icons_button_toggled)

        self.add_label(grid,
            _('Thumbnail size (when videos are displayed on a grid)'),
            0, 10, 1, 1,
        )

        store = Gtk.ListStore(str, str)
        thumb_size_list = self.app_obj.thumb_size_list.copy()
        while thumb_size_list:
            store.append( [ thumb_size_list.pop(0), thumb_size_list.pop(0)] )

        combo = Gtk.ComboBox.new_with_model(store)
        grid.attach(combo, 1, 10, 1, 1)
        combo.set_hexpand(True)

        renderer_text = Gtk.CellRendererText()
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, 'text', 0)

        # (IV is in groups of two, in the form [translation, actual value])
        combo.set_active(
            int(
                self.app_obj.thumb_size_list.index(
                    self.app_obj.thumb_size_custom,
                ) / 2,
            ),
        )
        combo.connect('changed', self.on_thumb_size_combo_changed)

        checkbutton8 = self.add_checkbutton(grid,
            _('Show livestreams with a different background colour'),
            self.app_obj.livestream_use_colour_flag,
            True,                   # Can be toggled by user
            0, 11, grid_width, 1,
        )
        # (Signal connect appears below)

        checkbutton9 = self.add_checkbutton(grid,
            _('Use same background colours for livestream and debut videos'),
            self.app_obj.livestream_simple_colour_flag,
            True,                   # Can be toggled by user
            0, 12, grid_width, 1,
        )
        if not self.app_obj.livestream_use_colour_flag:
            checkbutton9.set_sensitive(False)
        # (Signal connect appears below)

        # (Signal connects from above)
        checkbutton8.connect(
            'toggled',
            self.on_livestream_colour_button_toggled,
            checkbutton9,
        )
        checkbutton9.connect(
            'toggled',
            self.on_livestream_simple_button_toggled,
        )


    def setup_windows_drag_tab(self, inner_notebook):

        """Called by self.setup_windows_tab().

        Sets up the 'Drag' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(_('_Drag'), inner_notebook)

        # Drag and drop preferences
        self.add_label(grid,
            '<u>' + _('Drag and drop preferences') + '</u>',
            0, 0, 1, 1,
        )

        self.add_label(grid,
            '<i>' + _(
            'When dragging and dropping videos to an external application...',
            ) + '</i>',
            0, 1, 1, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _('Transfer the video\'s full file path'),
            self.app_obj.drag_video_path_flag,
            True,                   # Can be toggled by user
            0, 2, 1, 1,
        )
        checkbutton.connect('toggled', self.on_drag_path_button_toggled)

        checkbutton2 = self.add_checkbutton(grid,
            _('Transfer the video\'s source URL'),
            self.app_obj.drag_video_source_flag,
            True,                   # Can be toggled by user
            0, 3, 1, 1,
        )
        checkbutton2.connect('toggled', self.on_drag_source_button_toggled)

        checkbutton3 = self.add_checkbutton(grid,
            _('Transfer the video\'s name'),
            self.app_obj.drag_video_name_flag,
            True,                   # Can be toggled by user
            0, 4, 1, 1,
        )
        checkbutton3.connect('toggled', self.on_drag_name_button_toggled)

        checkbutton4 = self.add_checkbutton(grid,
            _('Transfer the thumbnail\'s full file path'),
            self.app_obj.drag_thumb_path_flag,
            True,                   # Can be toggled by user
            0, 5, 1, 1,
        )
        checkbutton4.connect('toggled', self.on_drag_thumb_button_toggled)


    def setup_windows_system_tray_tab(self, inner_notebook):

        """Called by self.setup_windows_tab().

        Sets up the 'System tray' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_System tray'),
            inner_notebook,
        )

        # System tray preferences
        self.add_label(grid,
            '<u>' + _('System tray preferences') + '</u>',
            0, 0, 1, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _('Show icon in system tray'),
            self.app_obj.show_status_icon_flag,
            True,               # Can be toggled by user
            0, 1, 1, 1,
        )
        checkbutton.set_hexpand(False)
        # (Signal connect appears below)

        checkbutton2 = self.add_checkbutton(grid,
            _('Close to the tray, rather than closing the application'),
            self.app_obj.close_to_tray_flag,
            True,               # Can be toggled by user
            0, 12, 1, 1,
        )
        checkbutton2.set_hexpand(False)
        checkbutton2.connect('toggled', self.on_close_to_tray_toggled)
        if not self.app_obj.show_status_icon_flag:
            checkbutton2.set_sensitive(False)

        # (Signal connect from above)
        checkbutton.connect(
            'toggled',
            self.on_show_status_icon_toggled,
            checkbutton2,
        )


    def setup_windows_dialogues_tab(self, inner_notebook):

        """Called by self.setup_windows_tab().

        Sets up the 'Dialogues' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('D_ialogues'),
            inner_notebook,
        )

        # Dialogue window preferences
        self.add_label(grid,
            '<u>' + _('Dialogue window preferences') + '</u>',
            0, 0, 1, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _('When adding channels/playlists, keep the dialogue window open'),
            self.app_obj.dialogue_keep_open_flag,
            True,               # Can be toggled by user
            0, 1, 1, 1,
        )
        checkbutton.set_hexpand(False)
        # (Signal connect appears below)

        checkbutton2 = self.add_checkbutton(grid,
            _(
            'When the dialogue window opens, add URLs from the system' \
            + ' clipboard',
            ),
            self.app_obj.dialogue_copy_clipboard_flag,
            True,               # Can be toggled by user
            0, 2, 1, 1,
        )
        checkbutton2.set_hexpand(False)
        checkbutton2.connect('toggled', self.on_clipboard_button_toggled)
        if self.app_obj.dialogue_keep_open_flag:
            checkbutton2.set_sensitive(False)

        # (Signal connect from above)
        checkbutton.connect(
            'toggled',
            self.on_keep_open_button_toggled,
            checkbutton2,
        )


    def setup_windows_errors_warnings_tab(self, inner_notebook):

        """Called by self.setup_windows_tab().

        Sets up the 'Errors/Warnings' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Errors/Warnings'),
            inner_notebook,
        )

        grid_width = 2

        # Errors/Warnings tab preferences
        self.add_label(grid,
            '<u>' + _('Errors/Warnings tab preferences') + '</u>',
            0, 0, grid_width, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _('Show Tartube error messages'),
            self.app_obj.system_error_show_flag,
            True,                   # Can be toggled by user
            0, 1, 1, 1,
        )
        checkbutton.connect('toggled', self.on_system_error_button_toggled)

        checkbutton2 = self.add_checkbutton(grid,
            _('Show Tartube warning messages'),
            self.app_obj.system_warning_show_flag,
            True,                   # Can be toggled by user
            0, 2, 1, 1,
        )
        checkbutton2.connect('toggled', self.on_system_warning_button_toggled)

        checkbutton3 = self.add_checkbutton(grid,
            _('Show server error messages'),
            self.app_obj.operation_error_show_flag,
            True,                   # Can be toggled by user
            1, 1, 1, 1,
        )
        checkbutton3.connect(
            'toggled',
            self.on_operation_error_button_toggled,
        )

        checkbutton4 = self.add_checkbutton(grid,
            _('Show server warning messages'),
            self.app_obj.operation_warning_show_flag,
            True,                   # Can be toggled by user
            1, 2, 1, 1,
        )
        checkbutton4.connect(
            'toggled',
            self.on_operation_warning_button_toggled,
        )

        # Downloader error/warning preferences
        self.add_label(grid,
            '<u>' + _('Downloader error/warning preferences') + '</u>',
            0, 3, 1, 1,
        )

        translate_note = _(
            'TRANSLATOR\'S NOTE: These error messages are always in English',
        )

        checkbutton5 = self.add_checkbutton(grid,
            _('Ignore \'Child process exited with non-zero code\' errors'),
            self.app_obj.ignore_child_process_exit_flag,
            True,                   # Can be toggled by user
            0, 4, grid_width, 1,
        )
        checkbutton5.connect('toggled', self.on_child_process_button_toggled)

        checkbutton6 = self.add_checkbutton(grid,
            _(
            'Ignore \'Unable to download video data\' and \'Unable to' \
            + ' extract video data\' errors',
            ),
            self.app_obj.ignore_http_404_error_flag,
            True,                   # Can be toggled by user
            0, 5, grid_width, 1,
        )
        checkbutton6.connect('toggled', self.on_http_404_button_toggled)

        checkbutton7 = self.add_checkbutton(grid,
            _('Ignore \'Did not get any data blocks\' errors'),
            self.app_obj.ignore_data_block_error_flag,
            True,                   # Can be toggled by user
            0, 6, grid_width, 1,
        )
        checkbutton7.connect('toggled', self.on_data_block_button_toggled)

        checkbutton8 = self.add_checkbutton(grid,
            _(
            'Ignore \'Requested formats are incompatible for merge\' warnings',
            ),
            self.app_obj.ignore_merge_warning_flag,
            True,                   # Can be toggled by user
            0, 7, grid_width, 1,
        )
        checkbutton8.connect('toggled', self.on_merge_button_toggled)

        checkbutton9 = self.add_checkbutton(grid,
            _('Ignore \'No video formats found\' errors'),
            self.app_obj.ignore_missing_format_error_flag,
            True,                   # Can be toggled by user
            0, 8, grid_width, 1,
        )
        checkbutton9.connect('toggled', self.on_missing_format_button_toggled)

        checkbutton10 = self.add_checkbutton(grid,
            _('Ignore \'There are no annotations to write\' warnings'),
            self.app_obj.ignore_no_annotations_flag,
            True,                   # Can be toggled by user
            0, 9, grid_width, 1,
        )
        checkbutton10.connect('toggled', self.on_no_annotations_button_toggled)

        checkbutton11 = self.add_checkbutton(grid,
            _('Ignore \'Video doesn\'t have subtitles\' warnings'),
            self.app_obj.ignore_no_subtitles_flag,
            True,                   # Can be toggled by user
            0, 10, grid_width, 1,
        )
        checkbutton11.connect('toggled', self.on_no_subtitles_button_toggled)


    def setup_windows_websites_tab(self, inner_notebook):

        """Called by self.setup_windows_tab().

        Sets up the 'Websites' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Websites'),
            inner_notebook,
        )

        grid_width = 2

        # YouTube error/warning preferences
        self.add_label(grid,
            '<u>' + _('YouTube error/warning preferences') + '</u>',
            0, 0, grid_width, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _('Ignore YouTube copyright errors'),
            self.app_obj.ignore_yt_copyright_flag,
            True,                   # Can be toggled by user
            0, 1, 1, 1,
        )
        checkbutton.connect('toggled', self.on_copyright_button_toggled)

        checkbutton2 = self.add_checkbutton(grid,
            _('Ignore YouTube age-restriction errors'),
            self.app_obj.ignore_yt_age_restrict_flag,
            True,                   # Can be toggled by user
            0, 2, 1, 1,
        )
        checkbutton2.connect('toggled', self.on_age_restrict_button_toggled)

        checkbutton3 = self.add_checkbutton(grid,
            _('Ignore YouTube deletion by uploader errors'),
            self.app_obj.ignore_yt_uploader_deleted_flag,
            True,                   # Can be toggled by user
            1, 1, 1, 1,
        )
        checkbutton3.connect('toggled', self.on_uploader_button_toggled)

        checkbutton4 = self.add_checkbutton(grid,
            _('Ignore YouTube payment errors'),
            self.app_obj.ignore_yt_payment_flag,
            True,                   # Can be toggled by user
            1, 2, 1, 1,
        )
        checkbutton4.connect('toggled', self.on_payment_button_toggled)

        # Custom error/warning preferences
        self.add_label(grid,
            '<u>' + _('General preferences') + '</u>',
            0, 4, grid_width, 1,
        )

        self.add_label(grid,
            '<i>' + _(
                'Ignore any errors/warnings which match lines in this list' \
                + ' (applies to all websites)',
            ) + '</i>',
            0, 5, grid_width, 1,
        )

        textview, textbuffer = self.add_textview(grid,
            self.app_obj.ignore_custom_msg_list,
            0, 6, grid_width, 1
        )
        # (Signal connect appears below)

        radiobutton = self.add_radiobutton(grid,
            None,
            _('These are ordinary strings'),
            0, 7, 1, 1,
        )
        # (Signal connect appears below)

        radiobutton2 = self.add_radiobutton(grid,
            radiobutton,
            _('These are regular expressions (regexes)'),
            1, 7, 1, 1,
        )
        if self.app_obj.ignore_custom_regex_flag:
            radiobutton2.set_active(True)
        # (Signal connect appears below)

        # (Signal connects from above)
        textbuffer.connect('changed', self.on_custom_textview_changed)
        radiobutton.connect(
            'toggled',
            self.on_regex_button_toggled,
            False,
        )
        radiobutton2.connect(
            'toggled',
            self.on_regex_button_toggled,
            True,
        )


    def setup_scheduling_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Scheduling' tab.
        """

        # Add this tab...
        tab, grid = self.add_notebook_tab(_('_Scheduling'), 0)

        # ...and an inner notebook...
        inner_notebook = self.add_inner_notebook(grid)

        # ...with its own tabs
        self.setup_scheduling_start_tab(inner_notebook)
        self.setup_scheduling_stop_tab(inner_notebook)


    def setup_scheduling_start_tab(self, inner_notebook):

        """Called by self.setup_scheduling_tab().

        Sets up the 'Start' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(_('_Start'), inner_notebook)

        grid_width = 5

        # Scheduled download preferences
        self.add_label(grid,
            '<u>' + _('Scheduled download preferences') + '</u>',
            0, 0, grid_width, 1,
        )

        # (GenericConfigWin.add_treeview() doesn't support multiple columns, so
        #   we'll do everything ourselves)
        frame = Gtk.Frame()
        grid.attach(frame, 0, 1, grid_width, 1)

        scrolled = Gtk.ScrolledWindow()
        frame.add(scrolled)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)

        treeview = Gtk.TreeView()
        scrolled.add(treeview)
        treeview.set_headers_visible(True)

        for i, column_title in enumerate(
            [
                _('Name'), _('Download'), _('Start mode'), _('Time'),
                _('Priority'), _('Whole'), _('Shutdown'), _('D/L All'),
                _('Join mode'),
            ]
        ):
            if i >= 4 and i <= 7:
                renderer_toggle = Gtk.CellRendererToggle()
                column_toggle = Gtk.TreeViewColumn(
                    column_title,
                    renderer_toggle,
                    active=i,
                )
                treeview.append_column(column_toggle)
                column_toggle.set_resizable(False)
            else:
                renderer_text = Gtk.CellRendererText()
                column_text = Gtk.TreeViewColumn(
                    column_title,
                    renderer_text,
                    text=i,
                )
                treeview.append_column(column_text)
                column_text.set_resizable(True)

        self.schedule_liststore = Gtk.ListStore(
            str, str, str, str, bool, bool, bool, bool, str,
        )
        treeview.set_model(self.schedule_liststore)

        # Initialise the list
        self.setup_scheduling_start_tab_update_treeview()

        # Add editing widgets
        label = self.add_label(grid,
            _('Scheduled download name'),
            0, 2, 1, 1,
        )
        label.set_hexpand(False)

        entry = self.add_entry(grid,
            None,
            True,
            1, 2, (grid_width - 2), 1,
        )

        button = Gtk.Button()
        grid.attach(button, (grid_width - 1), 2, 1, 1)
        button.set_label(_('Add'))
        button.connect(
            'clicked',
            self.on_scheduled_add_button_clicked,
            entry,
        )

        button2 = Gtk.Button()
        grid.attach(button2, 1, 3, 1, 1)
        button2.set_label(_('Edit'))
        button2.connect(
            'clicked',
            self.on_scheduled_edit_button_clicked,
            treeview,
        )

        button3 = Gtk.Button()
        grid.attach(button3, 2, 3, 1, 1)
        button3.set_label(_('Move up'))
        button3.connect(
            'clicked',
            self.on_scheduled_move_up_button_clicked,
            treeview,
        )

        button4 = Gtk.Button()
        grid.attach(button4, 3, 3, 1, 1)
        button4.set_label(_('Move down'))
        button4.connect(
            'clicked',
            self.on_scheduled_move_down_button_clicked,
            treeview,
        )

        button5 = Gtk.Button()
        grid.attach(button5, 4, 3, 1, 1)
        button5.set_label(_('Delete'))
        button5.connect(
            'clicked',
            self.on_scheduled_delete_button_clicked,
            treeview,
        )


    def setup_scheduling_start_tab_update_treeview(self):

        """ Called by self.setup_scheduling_start_tab() and
        mainapp.TartubeApp.del_scheduled_list().

        Fills or updates the treeview.

        """

        self.schedule_liststore.clear()

        for scheduled_obj in self.app_obj.scheduled_list:
            self.setup_scheduling_start_tab_add_row(scheduled_obj)


    def setup_scheduling_start_tab_add_row(self, scheduled_obj):

        """Called by self.setup_scheduling_start_tab_update_treeview() and
        .on_scheduled_add_button_clicked().

        Adds a row to the treeview.

        Args:

            scheduled_obj (media.Scheduled) - The scheduled download object to
                display on this row

        """

        row_list = []

        row_list.append(scheduled_obj.name)

        if scheduled_obj.dl_mode == 'sim':
            row_list.append('check')
        elif scheduled_obj.dl_mode == 'real':
            row_list.append('download')
        else:
            row_list.append('custom')

        row_list.append(scheduled_obj.start_mode)
        row_list.append(
            str(scheduled_obj.wait_value) + ' ' + scheduled_obj.wait_unit
        )
        row_list.append(scheduled_obj.exclusive_flag)
        row_list.append(scheduled_obj.ignore_limits_flag)
        row_list.append(scheduled_obj.shutdown_flag)
        row_list.append(scheduled_obj.all_flag)
        row_list.append(scheduled_obj.join_mode)

        self.schedule_liststore.append(row_list)


    def setup_scheduling_stop_tab(self, inner_notebook):

        """Called by self.setup_scheduling_tab().

        Sets up the 'Stop' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(_('S_top'), inner_notebook)

        grid_width = 3

        # Scheduled stop preferences
        self.add_label(grid,
            '<u>' + _('Scheduled stop preferences') + '</u>',
            0, 0, grid_width, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _('Stop all download operations after this much time'),
            self.app_obj.autostop_time_flag,
            True,                   # Can be toggled by user
            0, 1, 1, 1,
        )
        # (Signal connect appears below)

        spinbutton = self.add_spinbutton(grid,
            1, None, 1, self.app_obj.autostop_time_value,
            1, 1, 1, 1,
        )
        if not self.app_obj.autostop_time_flag:
            spinbutton.set_sensitive(False)

        store = Gtk.ListStore(str, str)
        for string in formats.TIME_METRIC_LIST:
            store.append( [string, formats.TIME_METRIC_TRANS_DICT[string]] )

        combo = Gtk.ComboBox.new_with_model(store)
        grid.attach(combo, 2, 1, 1, 1)

        renderer_text = Gtk.CellRendererText()
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, 'text', 1)
        combo.set_entry_text_column(1)
        combo.set_active(
            formats.TIME_METRIC_LIST.index(
                self.app_obj.autostop_time_unit,
            )
        )
        if not self.app_obj.autostop_time_flag:
            combo.set_sensitive(False)
        # (Signal connect appears below)

        # (Signal connects from above)
        checkbutton.connect(
            'toggled',
            self.on_autostop_time_button_toggled,
            spinbutton,
            combo,
        )
        spinbutton.connect(
            'value-changed',
            self.on_autostop_time_spinbutton_changed,
        )
        combo.connect('changed', self.on_autostop_time_combo_changed)

        checkbutton2 = self.add_checkbutton(grid,
            _('Stop all download operations after this many videos'),
            self.app_obj.autostop_videos_flag,
            True,                   # Can be toggled by user
            0, 2, 1, 1,
        )
        # (Signal connect appears below)

        spinbutton2 = self.add_spinbutton(grid,
            1, None, 1, self.app_obj.autostop_videos_value,
            1, 2, 1, 1,
        )
        if not self.app_obj.autostop_videos_flag:
            spinbutton2.set_sensitive(False)
        # (Signal connect appears below)

        # (Signal connects from above)
        checkbutton2.connect(
            'toggled',
            self.on_autostop_videos_button_toggled,
            spinbutton2,
        )
        spinbutton2.connect(
            'value-changed',
            self.on_autostop_videos_spinbutton_changed,
        )

        checkbutton3 = self.add_checkbutton(grid,
            _('Stop all download operations after this much disk space'),
            self.app_obj.autostop_size_flag,
            True,                   # Can be toggled by user
            0, 3, 1, 1,
        )
        # (Signal connect appears below)

        spinbutton3 = self.add_spinbutton(grid,
            1, None, 1, self.app_obj.autostop_size_value,
            1, 3, 1, 1,
        )
        if not self.app_obj.autostop_size_flag:
            spinbutton3.set_sensitive(False)

        combo3 = self.add_combo(grid,
            formats.FILESIZE_METRIC_LIST,
            None,
            2, 3, 1, 1,
        )
        combo3.set_active(
            formats.FILESIZE_METRIC_LIST.index(
                self.app_obj.autostop_size_unit,
            )
        )
        if not self.app_obj.autostop_size_flag:
            combo3.set_sensitive(False)
        # (Signal connect appears below)

        # (Signal connects from above)
        checkbutton3.connect(
            'toggled',
            self.on_autostop_size_button_toggled,
            spinbutton3,
            combo3,
        )
        spinbutton3.connect(
            'value-changed',
            self.on_autostop_size_spinbutton_changed,
        )
        combo3.connect('changed', self.on_autostop_size_combo_changed)

        self.add_label(grid,
            '<i>' + _(
                'N.B. Disk space is estimated. This setting does not apply' \
                + ' to simulated downloads',
            ) + '</i>',
            0, 4, grid_width, 1,
        )


    def setup_operations_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Operations' tab.
        """

        # Add this tab...
        tab, grid = self.add_notebook_tab(_('_Operations'), 0)

        # ...and an inner notebook...
        self.operations_inner_notebook = self.add_inner_notebook(grid)

        # ...with its own tabs
        self.setup_operations_performance_tab(self.operations_inner_notebook)
        self.setup_operations_prefs_tab(self.operations_inner_notebook)
        self.setup_operations_downloads_tab(self.operations_inner_notebook)
        self.setup_operations_custom_tab(self.operations_inner_notebook)
        self.setup_operations_livestreams_tab(self.operations_inner_notebook)
        self.setup_operations_proxies_tab(self.operations_inner_notebook)
        self.setup_operations_actions_tab(self.operations_inner_notebook)


    def setup_operations_performance_tab(self, inner_notebook):

        """Called by self.setup_operations_tab().

        Sets up the 'Performance' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Performance'),
            inner_notebook,
        )

        grid_width = 3

        # Performance limits
        self.add_label(grid,
            '<u>' + _('Performance limits') + '</u>',
            0, 0, grid_width, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _('Limit simultaneous downloads to'),
            self.app_obj.num_worker_apply_flag,
            True,               # Can be toggled by user
            0, 1, 1, 1,
        )
        checkbutton.set_hexpand(False)
        checkbutton.connect('toggled', self.on_worker_button_toggled)

        spinbutton = self.add_spinbutton(grid,
            self.app_obj.num_worker_min,
            self.app_obj.num_worker_max,
            1,                  # Step
            self.app_obj.num_worker_default,
            1, 1, 1, 1,
        )
        spinbutton.connect('value-changed', self.on_worker_spinbutton_changed)

        checkbutton2 = self.add_checkbutton(grid,
            _('Limit download speed to'),
            self.app_obj.bandwidth_apply_flag,
            True,               # Can be toggled by user
            0, 2, 1, 1,
        )
        checkbutton2.set_hexpand(False)
        checkbutton2.connect('toggled', self.on_bandwidth_button_toggled)

        spinbutton2 = self.add_spinbutton(grid,
            self.app_obj.bandwidth_min,
            self.app_obj.bandwidth_max,
            1,                  # Step
            self.app_obj.bandwidth_default,
            1, 2, 1, 1,
        )
        spinbutton2.connect(
            'value-changed',
            self.on_bandwidth_spinbutton_changed,
        )

        self.add_label(grid,
            'KiB/s',
            2, 2, 1, 1,
        )

        checkbutton3 = self.add_checkbutton(grid,
            _('Overriding video format options, limit video resolution to'),
            self.app_obj.video_res_apply_flag,
            True,               # Can be toggled by user
            0, 3, 1, 1,
        )
        checkbutton3.set_hexpand(False)
        checkbutton3.connect('toggled', self.on_video_res_button_toggled)

        combo = self.add_combo(grid,
            formats.VIDEO_RESOLUTION_LIST,
            None,
            1, 3, 1, 1,
        )
        combo.set_active(
            formats.VIDEO_RESOLUTION_LIST.index(
                self.app_obj.video_res_default,
            )
        )
        combo.connect('changed', self.on_video_res_combo_changed)

        # Time-saving settings
        self.add_label(grid,
            '<u>' + _('Time-saving settings') + '</u>',
            0, 4, grid_width, 1,
        )

        checkbutton4 = self.add_checkbutton(grid,
            _(
            'Stop checking/downloading a channel/playlist when it starts' \
            + ' sending videos you already have',
            ),
            self.app_obj.operation_limit_flag,
            True,               # Can be toggled by user
            0, 5, grid_width, 1,
        )
        checkbutton4.set_hexpand(False)
        # (Signal connect appears below)

        self.add_label(grid,
            _('Stop after this many videos (when checking)'),
            0, 6, 1, 1,
        )

        entry = self.add_entry(grid,
            self.app_obj.operation_check_limit,
            True,
            1, 6, 1, 1,
        )
        entry.set_width_chars(4)
        entry.connect('changed', self.on_check_limit_changed)
        if not self.app_obj.operation_limit_flag:
            entry.set_sensitive(False)

        self.add_label(grid,
            _('Stop after this many videos (when downloading)'),
            0, 7, 1, 1,
        )

        entry2 = self.add_entry(grid,
            self.app_obj.operation_download_limit,
            True,
            1, 7, 1, 1,
        )
        entry2.set_width_chars(4)
        entry2.connect('changed', self.on_dl_limit_changed)
        if not self.app_obj.operation_limit_flag:
            entry2.set_sensitive(False)

        # (Signal connect from above)
        checkbutton4.connect(
            'toggled',
            self.on_limit_button_toggled,
            entry,
            entry2,
        )


    def setup_operations_prefs_tab(self, inner_notebook):

        """Called by self.setup_operations_tab().

        Sets up the 'Preferences' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('P_references'),
            inner_notebook,
        )

        grid_width = 2

        # URL flexibility preferences
        self.add_label(grid,
            '<u>' + _('URL flexibility preferences') + '</u>',
            0, 0, grid_width, 1,
        )

        radiobutton = self.add_radiobutton(grid,
            None,
            _(
            'If a video\'s URL represents a channel/playlist, not a video,' \
            + ' don\'t download it',
            ),
            0, 1, grid_width, 1,
        )
        # (Signal connect appears below)

        radiobutton2 = self.add_radiobutton(grid,
            radiobutton,
            _('...or, download multiple videos into the containing folder'),
            0, 2, grid_width, 1,
        )
        if self.app_obj.operation_convert_mode == 'multi':
            radiobutton2.set_active(True)
        # (Signal connect appears below)

        radiobutton3 = self.add_radiobutton(grid,
            radiobutton2,
            _(
            '...or, create a new channel, and download the videos into that',
            ),
            0, 3, grid_width, 1,
        )
        if self.app_obj.operation_convert_mode == 'channel':
            radiobutton3.set_active(True)
        # (Signal connect appears below)

        radiobutton4 = self.add_radiobutton(grid,
            radiobutton3,
            _(
            '...or, create a new playlist, and download the videos into that',
            ),
            0, 4, grid_width, 1,
        )
        if self.app_obj.operation_convert_mode == 'playlist':
            radiobutton4.set_active(True)
        # (Signal connect appears below)

        # (Signal connects from above)
        radiobutton.connect(
            'toggled',
            self.on_convert_from_button_toggled,
            'disable',
        )
        radiobutton2.connect(
            'toggled',
            self.on_convert_from_button_toggled,
            'multi',
        )
        radiobutton3.connect(
            'toggled',
            self.on_convert_from_button_toggled,
            'channel',
        )
        radiobutton4.connect(
            'toggled',
            self.on_convert_from_button_toggled,
            'playlist',
        )

        # Missing video preferences
        self.add_label(grid,
            '<u>' + _('Missing video preferences') + '</u>',
            0, 5, grid_width, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _(
            'Add videos which have been removed from a channel/playlist to' \
            + ' the Missing Videos folder',
            ),
            self.app_obj.track_missing_videos_flag,
            True,                   # Can be toggled by user
            0, 6, grid_width, 1,
        )
        # (Signal connect appears below)

        checkbutton2 = self.add_checkbutton(grid,
            _(
            'Only add videos that were uploaded within this many days',
            ),
            self.app_obj.track_missing_time_flag,
            True,                   # Can be toggled by user
            0, 7, 1, 1,
        )
        if not self.app_obj.track_missing_videos_flag:
            checkbutton2.set_sensitive(False)
        # (Signal connect appears below)

        spinbutton = self.add_spinbutton(grid,
            0,
            365,
            1,                  # Step
            self.app_obj.track_missing_time_days,
            1, 7, 1, 1,
        )
        if not self.app_obj.track_missing_videos_flag \
        or not self.app_obj.track_missing_time_flag:
            spinbutton.set_sensitive(False)
        # (Signal connect appears below)

        # (Signal connects from above)
        checkbutton.connect(
            'toggled',
            self.on_missing_videos_button_toggled,
            checkbutton2,
            spinbutton,
        )
        checkbutton2.connect(
            'toggled',
            self.on_missing_time_button_toggled,
            spinbutton,
        )
        spinbutton.connect(
            'value-changed',
            self.on_missing_time_spinbutton_changed,
        )

        # Invidious mirror
        self.add_label(grid,
            '<u>' + _('Invidious mirror') + '</u>',
            0, 8, grid_width, 1,
        )

        self.add_label(grid,
            _(
                'To find an updated list of Invidious mirrors, use any' \
                + ' search engine!',
            ),
            0, 9, grid_width, 1,
        )

        entry = self.add_entry(grid,
            self.app_obj.custom_invidious_mirror,
            True,
            0, 10, grid_width, 1,
        )
        entry.connect('changed', self.on_invidious_mirror_changed)

        msg = _('Type the exact text that replaces youtube.com e.g.')
        msg = re.sub('youtube.com', '   <b>youtube.com</b>   ', msg)

        self.add_label(grid,
            '<i>' + msg + '   <b>' + self.app_obj.default_invidious_mirror \
            + '</b></i>',
            0, 11, grid_width, 1,
        )


    def setup_operations_downloads_tab(self, inner_notebook):

        """Called by self.setup_operations_tab().

        Sets up the 'Downloads' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Downloads'),
            inner_notebook,
        )

        grid_width = 2

        # Download operation preferences
        self.add_label(grid,
            '<u>' + _('Download operation preferences') + '</u>',
            0, 0, grid_width, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _(
            'Automatically update downloader before every download operation',
            ),
            self.app_obj.operation_auto_update_flag,
            True,                   # Can be toggled by user
            0, 1, grid_width, 1,
        )
        checkbutton.connect('toggled', self.on_auto_update_button_toggled)
        if __main__.__pkg_strict_install_flag__:
            checkbutton.set_sensitive(False)

        checkbutton2 = self.add_checkbutton(grid,
            _(
            'Automatically save files at the end of all operations',
            ),
            self.app_obj.operation_save_flag,
            True,                   # Can be toggled by user
            0, 2, grid_width, 1,
        )
        checkbutton2.connect('toggled', self.on_save_button_toggled)

        checkbutton3 = self.add_checkbutton(grid,
            _(
            'For simulated downloads, don\'t check a video in a folder' \
            + ' more than once',
            ),
            self.app_obj.operation_sim_shortcut_flag,
            True,                   # Can be toggled by user
            0, 3, grid_width, 1,
        )
        checkbutton3.connect('toggled', self.on_operation_sim_button_toggled)

        checkbutton4 = self.add_checkbutton(grid,
            _(
            'If a download stalls, restart it after this many minutes',
            ),
            self.app_obj.operation_auto_restart_flag,
            True,                   # Can be toggled by user
            0, 4, 1, 1,
        )
        # (Signal connect appears below)

        spinbutton = self.add_spinbutton(grid,
            1,
            None,
            1,                     # Step
            self.app_obj.operation_auto_restart_time,
            1, 4, 1, 1,
        )
        # (Signal connect appears below)
        if not self.app_obj.operation_auto_restart_flag:
            spinbutton.set_sensitive(False)

        checkbutton5 = self.add_checkbutton(grid,
            _(
            'If a network problem is detected, restart the download' \
            + ' immediately',
            ),
            self.app_obj.operation_auto_restart_network_flag,
            True,                   # Can be toggled by user
            0, 5, 1, 1,
        )
        # (Signal connect appears below)

        self.add_label(grid,
            '     ' \
            + _(
            'Maximum restarts after a stalled download (0 for no maximum)',
            ),
            0, 6, 1, 1,
        )

        spinbutton2 = self.add_spinbutton(grid,
            0,
            None,
            1,                     # Step
            self.app_obj.operation_auto_restart_max,
            1, 6, 1, 1,
        )
        # (Signal connect appears below)
        if not self.app_obj.operation_auto_restart_flag:
            spinbutton2.set_sensitive(False)

        # (Signal connects from above)
        checkbutton4.connect(
            'toggled',
            self.on_auto_restart_button_toggled,
            checkbutton5,
            spinbutton,
            spinbutton2,
        )
        checkbutton5.connect(
            'toggled',
            self.on_auto_restart_network_button_toggled,
            checkbutton4,
            spinbutton2,
        )
        spinbutton.connect(
            'value-changed',
            self.on_auto_restart_time_spinbutton_changed,
        )
        spinbutton2.connect(
            'value-changed',
            self.on_auto_restart_max_spinbutton_changed,
        )

        checkbutton6 = self.add_checkbutton(grid,
            _(
            'Allow downloader to create its own archive file (so deleted' \
            + ' videos are not re-downloaded)',
            ),
            self.app_obj.allow_ytdl_archive_flag,
            True,                   # Can be toggled by user
            0, 7, grid_width, 1,
        )
        checkbutton6.connect('toggled', self.on_archive_button_toggled)

        checkbutton7 = self.add_checkbutton(grid,
            _(
            'Also create an archive file when downloading from the Classic' \
            + ' Mode tab (not recommended)',
            ),
            self.app_obj.classic_ytdl_archive_flag,
            True,                   # Can be toggled by user
            0, 8, grid_width, 1,
        )
        checkbutton7.connect('toggled', self.on_archive_classic_button_toggled)

        checkbutton8 = self.add_checkbutton(grid,
            _(
            'When checking videos, apply a 60-second timeout',
            ),
            self.app_obj.apply_json_timeout_flag,
            True,                   # Can be toggled by user
            0, 9, grid_width, 1,
        )
        checkbutton8.connect('toggled', self.on_json_button_toggled)

        checkbutton9 = self.add_checkbutton(grid,
            _(
            'Convert .webp thumbnails into .jpg thumbnails (using FFmpeg)' \
            + ' after downloading them',
            ),
            self.app_obj.ffmpeg_convert_webp_flag,
            True,                   # Can be toggled by user
            0, 10, grid_width, 1,
        )
        checkbutton9.connect('toggled', self.on_ffmpeg_convert_flag_toggled)


    def setup_operations_custom_tab(self, inner_notebook):

        """Called by self.setup_operations_tab().

        Sets up the 'Custom' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(_('_Custom'), inner_notebook)
        grid_width = 2

        # Custom download preferences
        self.add_label(grid,
            '<u>' + _('Custom download preferences') + '</u>',
            0, 0, grid_width, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _(
            'In custom downloads, download each video independently of its' \
            + ' channel or playlist',
            ),
            self.app_obj.custom_dl_by_video_flag,
            True,                   # Can be toggled by user
            0, 1, grid_width, 1,
        )
        # (Signal connect appears below)

        checkbutton2 = self.add_checkbutton(grid,
            _(
            'In custom downloads, apply a delay after each video/channel/' \
            + 'playlist is download',
            ),
            self.app_obj.custom_dl_delay_flag,
            True,                   # Can be toggled by user
            0, 2, grid_width, 1,
        )
        # (Signal connect appears below)

        self.add_label(grid,
            _('Maximum delay to apply (in minutes)'),
            0, 3, 1, 1,
        )

        spinbutton = self.add_spinbutton(grid,
            0.2,
            None,
            0.2,                    # Step
            self.app_obj.custom_dl_delay_max,
            1, 3, 1, 1,
        )
        # (Signal connect appears below)
        if not self.app_obj.custom_dl_delay_flag:
            spinbutton.set_sensitive(False)

        self.add_label(grid,
            _(
            'Minimum delay to apply (in minutes; randomises the actual' \
            + ' delay)',
            ),
            0, 4, 1, 1,
        )

        spinbutton2 = self.add_spinbutton(grid,
            0,
            self.app_obj.custom_dl_delay_max,
            0.2,                    # Step
            self.app_obj.custom_dl_delay_min,
            1, 4, 1, 1,
        )
        spinbutton2.connect(
            'value-changed',
            self.on_delay_min_spinbutton_changed,
        )
        if not self.app_obj.custom_dl_delay_flag:
            spinbutton2.set_sensitive(False)

        radiobutton = self.add_radiobutton(grid,
            None,
            _(
            'In custom downloads, obtain a YouTube video from the original' \
            + ' website',
            ),
            0, 5, grid_width, 1,
        )
        # (Signal connect appears below)

        radiobutton2 = self.add_radiobutton(grid,
            radiobutton,
            _(
            'In custom downloads, obtain the video from HookTube rather' \
            + ' than YouTube',
            ),
            0, 6, grid_width, 1,
        )
        if self.app_obj.custom_dl_divert_mode == 'hooktube':
            radiobutton2.set_active(True)
        # (Signal connect appears below)

        radiobutton3 = self.add_radiobutton(grid,
            radiobutton2,
            _(
            'In custom downloads, obtain the video from Invidious rather' \
            + ' than YouTube',
            ),
            0, 7, grid_width, 1,
        )
        if self.app_obj.custom_dl_divert_mode == 'invidious':
            radiobutton3.set_active(True)
        # (Signal connect appears below)

        radiobutton4 = self.add_radiobutton(grid,
            radiobutton3,
            _(
            'In custom downloads, obtain the video from the YouTube' \
            + ' front-end specified below',
            ),
            0, 8, grid_width, 1,
        )
        if self.app_obj.custom_dl_divert_mode == 'other':
            radiobutton4.set_active(True)
        # (Signal connect appears below)

        entry = self.add_entry(grid,
            self.app_obj.custom_dl_divert_website,
            True,
            0, 9, grid_width, 1,
        )
        entry.connect('changed', self.on_alt_website_changed)
        if not self.app_obj.custom_dl_divert_mode == 'other':
            entry.set_sensitive(False)

        msg = _('Type the exact text that replaces youtube.com e.g.')
        msg = re.sub('youtube.com', '   <b>youtube.com</b>   ', msg)

        self.add_label(grid,
            '<i>' + msg + '   <b>hooktube.com</b></i>',
            0, 10, grid_width, 1,
        )

        if not self.app_obj.custom_dl_by_video_flag:
            radiobutton.set_sensitive(False)
            radiobutton2.set_sensitive(False)
            radiobutton3.set_sensitive(False)
            radiobutton4.set_sensitive(False)
            entry.set_sensitive(False)

        # (Signal connects from above)
        checkbutton.connect(
            'toggled',
            self.on_custom_video_button_toggled,
            radiobutton, radiobutton2, radiobutton3, radiobutton4,
            entry,
        )

        checkbutton2.connect(
            'toggled',
            self.on_custom_delay_button_toggled,
            spinbutton,
            spinbutton2,
        )

        spinbutton.connect(
            'value-changed',
            self.on_delay_max_spinbutton_changed,
            spinbutton2,
        )

        radiobutton.connect(
            'toggled',
            self.on_custom_divert_button_toggled,
            entry,
            'default',
        )

        radiobutton2.connect(
            'toggled',
            self.on_custom_divert_button_toggled,
            entry,
            'hooktube',
        )

        radiobutton3.connect(
            'toggled',
            self.on_custom_divert_button_toggled,
            entry,
            'invidious',
        )

        radiobutton4.connect(
            'toggled',
            self.on_custom_divert_button_toggled,
            entry,
            'other',
        )


    def setup_operations_livestreams_tab(self, inner_notebook):

        """Called by self.setup_scheduling_tab().

        Sets up the 'Streams' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Livestreams'),
            inner_notebook,
        )

        grid_width = 2

        # Livestream preferences
        self.add_label(grid,
            '<u>' + _(
                'Livestream preferences (compatible websites only)',
            ) + '</u>',
            0, 0, grid_width, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _('Detect livestreams announced within this many days'),
            self.app_obj.enable_livestreams_flag,
            True,                   # Can be toggled by user
            0, 1, 1, 1,
        )
        # (Signal connect appears below)
        spinbutton = self.add_spinbutton(grid,
            0, None, 1, self.app_obj.livestream_max_days,
            1, 1, 1, 1,
        )
        if not self.app_obj.enable_livestreams_flag:
            spinbutton.set_sensitive(False)
        # (Signal connect appears below)

        checkbutton2 = self.add_checkbutton(grid,
            _('How often to check the status of livestreams (in minutes)'),
            self.app_obj.scheduled_livestream_flag,
            True,                   # Can be toggled by user
            0, 2, 1, 1,
        )
        if not self.app_obj.enable_livestreams_flag:
            checkbutton2.set_sensitive(False)
        # (Signal connect appears below)

        spinbutton2 = self.add_spinbutton(grid,
            1, None, 1, self.app_obj.scheduled_livestream_wait_mins,
            1, 2, 1, 1,
        )
        if not self.app_obj.enable_livestreams_flag \
        or not self.app_obj.scheduled_livestream_flag:
            spinbutton2.set_sensitive(False)
        # (Signal connect appears below)

        checkbutton3 = self.add_checkbutton(grid,
            _('Check more frequently when a livestream is due to start'),
            self.app_obj.scheduled_livestream_extra_flag,
            True,                   # Can be toggled by user
            0, 3, grid_width, 1,
        )
        if not self.app_obj.enable_livestreams_flag \
        or not self.app_obj.scheduled_livestream_flag:
            checkbutton3.set_sensitive(False)
        checkbutton3.connect(
            'toggled',
            self.on_extra_livestreams_button_toggled,
        )

        # (Signal connects from above)
        checkbutton.connect(
            'toggled',
            self.on_enable_livestreams_button_toggled,
            checkbutton2,
            checkbutton3,
            spinbutton,
            spinbutton2,
        )

        spinbutton.connect(
            'value-changed',
            self.on_livestream_max_days_spinbutton_changed,
        )

        checkbutton2.connect(
            'toggled',
            self.on_scheduled_livestreams_button_toggled,
            checkbutton3,
            spinbutton2,
        )

        spinbutton2.connect(
            'value-changed',
            self.on_scheduled_livestreams_spinbutton_changed,
        )

        # Broadcast preferences
        self.add_label(grid,
            '<u>' + _(
                'Broadcast preferences (compatible websites only)',
            ) + '</u>',
            0, 4, grid_width, 1,
        )

        checkbutton4 = self.add_checkbutton(grid,
            _(
                'Use Youtube Stream Capture to download broadcasting' \
                + ' livestreams (requires aria2)',
            ),
            self.app_obj.ytsc_priority_flag,
            True,                   # Can be toggled by user
            0, 5, grid_width, 1,
        )
        # (Signal connect appears below)

        self.add_label(grid,
            _('Timeout after this many minutes of inactivity'),
            0, 6, 1, 1,
        )

        spinbutton3 = self.add_spinbutton(grid,
            1, None, 0.2,
            self.app_obj.ytsc_wait_time,
            1, 6, 1, 1,
        )
        if not self.app_obj.ytsc_priority_flag:
            spinbutton3.set_sensitive(False)
        # (Signal connect appears below)

        self.add_label(grid,
            _('Number of restarts after a timeout'),
            0, 7, 1, 1,
        )

        spinbutton4 = self.add_spinbutton(grid,
            0, None, 1,
            self.app_obj.ytsc_restart_max,
            1, 7, 1, 1,
        )
        if not self.app_obj.ytsc_priority_flag:
            spinbutton4.set_sensitive(False)
        # (Signal connect appears below)

        checkbutton5 = self.add_checkbutton(grid,
            _(
            'Bypass usual limits on simultaneous downloads, so that' \
            + ' all broadcasts can be downloaded',
            ),
            self.app_obj.num_worker_bypass_flag,
            True,                   # Can be toggled by user
            0, 8, grid_width, 1,
        )
        if not self.app_obj.ytsc_priority_flag:
            checkbutton5.set_sensitive(False)
        # (Signal connect appears below)

        # (Signal connects from above)
        checkbutton4.connect(
            'toggled',
            self.on_ytsc_priority_button_toggled,
            spinbutton3,
            spinbutton4,
            checkbutton5,
        )
        spinbutton3.connect(
            'value-changed',
            self.on_ytsc_wait_time_spinbutton_changed,
        )
        spinbutton4.connect(
            'value-changed',
            self.on_ytsc_restart_max_spinbutton_changed,
        )
        checkbutton5.connect(
            'toggled',
            self.on_worker_bypass_button_toggled,
        )


    def setup_operations_proxies_tab(self, inner_notebook):

        """Called by self.setup_scheduling_tab().

        Sets up the 'Proxies' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Proxies'),
            inner_notebook,
        )

        # Proxies
        self.add_label(grid,
            '<u>' + _('Proxies') + '</u>',
            0, 0, 1, 1,
        )

        self.add_label(grid,
            '<i>' \
            + _(
            'During a download operation, Tartube will cycle betwween the' \
            + ' proxies in this list',
            ) + '</i>',
            0, 1, 1, 1,
        )

        textview, textbuffer = self.add_textview(grid,
            self.app_obj.dl_proxy_list,
            0, 2, 1, 1
        )
        textbuffer.connect('changed', self.on_proxy_textview_changed)


    def setup_operations_actions_tab(self, inner_notebook):

        """Called by self.setup_scheduling_tab().

        Sets up the 'Actions' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Actions'),
            inner_notebook,
        )

        grid_width = 3

        # Livestream actions
        self.add_label(grid,
            '<u>' + _(
                'Livestream actions (can be toggled for individual videos)',
            ) + '</u>',
            0, 0, grid_width, 1,
        )

        # Currently disabled on MS Windows
        if os.name == 'nt':
            string = ' ' + _('(currently disabled on MS Windows)')
        else:
            string = ''

        checkbutton = self.add_checkbutton(grid,
            _('When a livestream starts, show a desktop notification') \
            + string,
            self.app_obj.livestream_auto_notify_flag,
            True,                   # Can be toggled by user
            0, 1, grid_width, 1,
        )
        checkbutton.connect(
            'toggled',
            self.on_livestream_auto_notify_button_toggled,
        )
        if os.name == 'nt':
            checkbutton.set_sensitive(False)

        checkbutton2 = self.add_checkbutton(grid,
            _('When a livestream starts, sound an alarm'),
            self.app_obj.livestream_auto_alarm_flag,
            True,                   # Can be toggled by user
            0, 2, 1, 1,
        )
        if not mainapp.HAVE_PLAYSOUND_FLAG:
            checkbutton2.set_sensitive(False)
        checkbutton2.connect(
            'toggled',
            self.on_livestream_auto_alarm_button_toggled,
        )

        combo = self.add_combo(grid,
            self.app_obj.sound_list,
            self.app_obj.sound_custom,
            1, 2, 1, 1,
        )
        combo.connect('changed', self.on_sound_custom_changed)
        if not mainapp.HAVE_PLAYSOUND_FLAG:
            combo.set_sensitive(False)

        button = Gtk.Button(_('Test'))
        grid.attach(button, 2, 2, 1, 1)
        button.set_tooltip_text(_('Plays the selected sound effect'))
        button.connect('clicked', self.on_test_sound_clicked, combo)
        if not mainapp.HAVE_PLAYSOUND_FLAG:
            button.set_sensitive(False)

        checkbutton3 = self.add_checkbutton(grid,
            _(
            'When a livestream starts, open it in the system\'s web browser',
            ),
            self.app_obj.livestream_auto_open_flag,
            True,                   # Can be toggled by user
            0, 3, grid_width, 1,
        )
        checkbutton3.connect(
            'toggled',
            self.on_livestream_auto_open_button_toggled,
        )

        checkbutton4 = self.add_checkbutton(grid,
            _('When a livestream starts, begin downloading it immediately'),
            self.app_obj.livestream_auto_dl_start_flag,
            True,                   # Can be toggled by user
            0, 4, grid_width, 1,
        )
        checkbutton4.connect(
            'toggled',
            self.on_livestream_auto_dl_start_button_toggled,
        )

        checkbutton5 = self.add_checkbutton(grid,
            _(
            'When a livestream stops, download it (overwriting any earlier' \
            + ' file)',
            ),
            self.app_obj.livestream_auto_dl_stop_flag,
            True,                   # Can be toggled by user
            0, 5, grid_width, 1,
        )
        checkbutton5.connect(
            'toggled',
            self.on_livestream_auto_dl_stop_button_toggled,
        )

        # Desktop notification preferences
        self.add_label(grid,
            '<u>' + _('Desktop notification preferences') + '</u>',
            0, 6, 1, 1,
        )

        radiobutton = self.add_radiobutton(grid,
            None,
            _(
            'Show a dialogue window at the end of an operation',
            ),
            0, 7, 1, 1,
        )
        # (Signal connect appears below)

        if platform.system() != 'Windows' and platform.system() != 'Darwin':
            text = 'Show a desktop notification at the end of an operation'
        else:
            text = 'Show a desktop notification (Linux/*BSD only)'

        radiobutton2 = self.add_radiobutton(grid,
            radiobutton,
            _(text),
            0, 8, 1, 1,
        )
        if self.app_obj.operation_dialogue_mode == 'desktop':
            radiobutton2.set_active(True)
        if platform.system() == 'Windows' or platform.system() == 'Darwin':
            radiobutton2.set_sensitive(False)
        # (Signal connect appears below)

        radiobutton3 = self.add_radiobutton(grid,
            radiobutton2,
            _(
            'Don\'t notify the user at the end of an operation',
            ),
            0, 9, 1, 1,
        )
        if self.app_obj.operation_dialogue_mode == 'default':
            radiobutton3.set_active(True)
        # (Signal connect appears below)

        # (Signal connects from above)
        radiobutton.connect(
            'toggled',
            self.on_dialogue_button_toggled,
            'dialogue',
        )
        radiobutton2.connect(
            'toggled',
            self.on_dialogue_button_toggled,
            'desktop',
        )
        radiobutton3.connect(
            'toggled',
            self.on_dialogue_button_toggled,
            'default',
        )


    def setup_downloader_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'youtube-dl' tab.
        """

        # Add this tab...
        tab, grid = self.add_notebook_tab('_Downloaders')

        # ...and an inner notebook...
        inner_notebook = self.add_inner_notebook(grid)

        # ...with its own tabs
        self.setup_downloader_forks_tab(inner_notebook)
        self.setup_downloader_paths_tab(inner_notebook)
        self.setup_downloader_ffmpeg_tab(inner_notebook)
        self.setup_downloader_ytsc_tab(inner_notebook)


    def setup_downloader_forks_tab(self, inner_notebook):

        """Called by self.setup_downloader_tab().

        Sets up the 'Forks' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Forks'),
            inner_notebook,
        )

        # Forks of youtube-dl
        self.add_label(grid,
            '<u>' + _('Forks of youtube-dl') + '</u>',
            0, 0, 1, 1,
        )

        # yt-dlp. Use an event box so the downloader can be selected by
        #   clicking anywhere in the frame
        event_box = Gtk.EventBox()
        grid.attach(event_box, 0, 1, 1, 1)
        # (Signal connect appears below)

        frame = Gtk.Frame()
        event_box.add(frame)
        frame.set_border_width(self.spacing_size)

        grid2 = Gtk.Grid()
        frame.add(grid2)
        grid2.set_border_width(self.spacing_size)

        self.add_label(grid2,
            utils.tidy_up_long_string(
                '<b>yt-dlp</b>: <i>' \
                + self.app_obj.ytdl_fork_descrip_dict['yt-dlp'] \
                + '</i>',
            ),
            0, 0, 1, 1,
        )

        radiobutton = self.add_radiobutton(grid2,
            None,
            '   ' + _('Use yt-dlp'),
            0, 1, 1, 1,
        )
        # (Signal connect appears below)

        # youtube-dl
        event_box2 = Gtk.EventBox()
        grid.attach(event_box2, 0, 2, 1, 1)
        # (Signal connect appears below)

        frame2 = Gtk.Frame()
        event_box2.add(frame2)
        frame2.set_border_width(self.spacing_size)

        grid3 = Gtk.Grid()
        frame2.add(grid3)
        grid3.set_border_width(self.spacing_size)

        self.add_label(grid3,
            utils.tidy_up_long_string(
                '<b>youtube-dl</b>: <i>' \
                + self.app_obj.ytdl_fork_descrip_dict['youtube-dl'] \
                + '</i>',
            ),
            0, 0, 1, 1,
        )

        radiobutton2 = self.add_radiobutton(grid3,
            radiobutton,
            '   ' + _('Use youtube-dl'),
            0, 1, 1, 1,
        )
        # (Signal connect appears below)

        # Any other fork
        event_box3 = Gtk.EventBox()
        grid.attach(event_box3, 0, 3, 1, 1)
        # (Signal connect appears below)

        frame3 = Gtk.Frame()
        event_box3.add(frame3)
        frame3.set_border_width(self.spacing_size)

        grid4 = Gtk.Grid()
        frame3.add(grid4)
        grid4.set_border_width(self.spacing_size)
        grid4.set_row_spacing(self.spacing_size)

        self.add_label(grid4,
            '<i>' + utils.tidy_up_long_string(
                self.app_obj.ytdl_fork_descrip_dict['custom'],
            ) + '</i>',
            0, 0, 2, 1,
        )

        radiobutton3 = self.add_radiobutton(grid4,
            radiobutton2,
            '   ' + _('Use a different fork of youtube-dl:'),
            0, 1, 1, 1,
        )
        # (Signal connect appears below)

        entry = self.add_entry(grid4,
            None,
            True,
            1, 1, 1, 1,
        )
        entry.set_sensitive(True)
        # (Signal connect appears below)

        # Set widgets initial state
        if self.app_obj.ytdl_fork is None \
        or self.app_obj.ytdl_fork == 'youtube-dl':
            radiobutton2.set_active(True)
            entry.set_sensitive(False)
        elif self.app_obj.ytdl_fork == 'yt-dlp':
            radiobutton.set_active(True)
            entry.set_sensitive(False)
        else:
            radiobutton3.set_active(True)
            if self.app_obj.ytdl_fork is not None:
                entry.set_text(self.app_obj.ytdl_fork)
            else:
                entry.set_text('')
            entry.set_sensitive(True)

        # (Signal connects from above)
        event_box.connect(
            'button-press-event',
            self.on_ytdl_fork_frame_clicked,
            radiobutton,
        )
        event_box2.connect(
            'button-press-event',
            self.on_ytdl_fork_frame_clicked,
            radiobutton2,
        )
        event_box3.connect(
            'button-press-event',
            self.on_ytdl_fork_frame_clicked,
            radiobutton3,
        )
        radiobutton.connect(
            'toggled',
            self.on_ytdl_fork_button_toggled,
            entry,
            'yt-dlp',
        )
        radiobutton2.connect(
            'toggled',
            self.on_ytdl_fork_button_toggled,
            entry,
            'youtube-dl',
        )
        radiobutton3.connect(
            'toggled',
            self.on_ytdl_fork_button_toggled,
            entry,
        )
        entry.connect(
            'changed',
            self.on_ytdl_fork_changed,
            radiobutton3,
        )


    def setup_downloader_paths_tab(self, inner_notebook):

        """Called by self.setup_downloader_tab().

        Sets up the 'File Paths' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_File paths'),
            inner_notebook,
        )
        grid_width = 3

        # Downloader file paths
        self.add_label(grid,
            '<u>' + _('Downloader file paths') + '</u>',
            0, 0, grid_width, 1,
        )

        # youtube-dl file paths
        self.add_label(grid,
            _('Path to the executable'),
            0, 1, 1, 1,
        )

        combo_list = [
            [
                _('Use default path') + ' (' + self.app_obj.ytdl_path_default \
                + ')',
                self.app_obj.ytdl_path_default,
            ],
            [
                _('Use local path') + ' (' + self.app_obj.ytdl_bin + ')',
                self.app_obj.ytdl_bin,
            ],
            [
                _('Use custom path'),
                None,       # Set by the callback
            ],
        ]
        if os.name != 'nt':

            combo_list.append(
                [
                    _('Use PyPI path') + ' (' + self.app_obj.ytdl_path_pypi \
                    + ')',
                    self.app_obj.ytdl_path_pypi,
                ],
            )

        self.path_liststore = Gtk.ListStore(str, str)
        for mini_list in combo_list:
            self.path_liststore.append( [ mini_list[0], mini_list[1] ] )

        combo = Gtk.ComboBox.new_with_model(self.path_liststore)
        grid.attach(combo, 1, 1, (grid_width - 1), 1)
        renderer_text = Gtk.CellRendererText()
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, 'text', 0)
        combo.set_entry_text_column(0)
        # (Signal connect appears below)

        entry = self.add_entry(grid,
            None,
            False,
            1, 2, 1, 1,
        )

        button = Gtk.Button(_('Set'))
        grid.attach(button, 2, 2, 1, 1)
        # (Signal connect appears below)

        # Set up those widgets
        if self.app_obj.ytdl_path_custom_flag:
            combo.set_active(2)
        elif self.app_obj.ytdl_path == self.app_obj.ytdl_path_default:
            combo.set_active(0)
        elif self.app_obj.ytdl_path == self.app_obj.ytdl_path_pypi:
            combo.set_active(3)
        else:
            combo.set_active(1)

        if self.app_obj.ytdl_path_custom_flag:

            # (If this window is loaded due to
            #   mainapp.TartubeApp.debug_open_pref_win_flag, this value will be
            #   None)
            if self.app_obj.ytdl_path:
                entry.set_text(self.app_obj.ytdl_path)

        else:
            button.set_sensitive(False)

        # Now set up the next combo
        self.add_label(grid,
            _('Command for update operations'),
            0, 3, 1, 1,
        )

        self.cmd_liststore = Gtk.ListStore(str, str)
        for item in self.app_obj.ytdl_update_list:
            self.cmd_liststore.append( [item, formats.YTDL_UPDATE_DICT[item]] )

        combo2 = Gtk.ComboBox.new_with_model(self.cmd_liststore)
        grid.attach(combo2, 1, 3, (grid_width - 1), 1)

        renderer_text = Gtk.CellRendererText()
        combo2.pack_start(renderer_text, True)
        combo2.add_attribute(renderer_text, 'text', 1)
        combo2.set_entry_text_column(1)

        combo2.set_active(
            self.app_obj.ytdl_update_list.index(
                self.app_obj.ytdl_update_current,
            ),
        )
        if __main__.__pkg_strict_install_flag__:
            combo2.set_sensitive(False)
        # (Signal connect appears below)

        # Update the combos, so that the youtube-dl fork, rather than
        #   youtube-dl itself, is visible (if applicable)
        self.update_ytdl_combos()

        # (Signal connects from above)
        combo.connect(
            'changed',
            self.on_ytdl_path_combo_changed,
            entry,
            button,
        )
        button.connect('clicked', self.on_ytdl_path_button_clicked, entry)
        combo2.connect('changed', self.on_update_combo_changed)


    def setup_downloader_ffmpeg_tab(self, inner_notebook):

        """Called by self.setup_downloader_tab().

        Sets up the 'FFmpeg / AVConv' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_FFmpeg / AVConv'),
            inner_notebook,
        )

        grid_width = 4

        # Post-processor file paths
        self.add_label(grid,
            '<u>' + _('Post-processing file paths') + '</u>',
            0, 0, grid_width, 1,
        )
        self.add_label(grid,
            '<i>' + _(
            'You only need to set these paths if Tartube cannot find' \
            + ' FFmpeg / AVConv automatically'
            ) + '</i>',
            0, 1, grid_width, 1,
        )

        self.add_label(grid,
            _('Path to the FFmpeg executable'),
            0, 2, 1, 1,
        )

        button = Gtk.Button(_('Set'))
        grid.attach(button, 1, 2, 1, 1)
        # (Signal connect appears below)

        button2 = Gtk.Button(_('Reset'))
        grid.attach(button2, 2, 2, 1, 1)
        # (Signal connect appears below)

        button3 = Gtk.Button(_('Use default path'))
        grid.attach(button3, 3, 2, 1, 1)
        # (Signal connect appears below)

        entry = self.add_entry(grid,
            self.app_obj.ffmpeg_path,
            False,
            0, 3, grid_width, 1,
        )
        entry.set_sensitive(False)
        entry.set_editable(False)
        entry.set_hexpand(True)

        if os.name == 'nt':
            entry.set_sensitive(False)
            entry.set_text(_('Install from main menu'))
            button.set_sensitive(False)
            button2.set_sensitive(False)
            button3.set_sensitive(False)

        # (Signal connects from above)
        button.connect('clicked', self.on_set_ffmpeg_button_clicked, entry)
        button2.connect('clicked', self.on_reset_ffmpeg_button_clicked, entry)
        button3.connect(
            'clicked',
            self.on_default_ffmpeg_button_clicked, entry,
        )

        self.add_label(grid,
            _('Path to the AVConv executable'),
            0, 4, 1, 1,
        )

        button4 = Gtk.Button(_('Set'))
        grid.attach(button4, 1, 4, 1, 1)
        # (Signal connect appears below)

        button5 = Gtk.Button(_('Reset'))
        grid.attach(button5, 2, 4, 1, 1)
        # (Signal connect appears below)

        button6 = Gtk.Button(_('Use default path'))
        grid.attach(button6, 3, 4, 1, 1)
        # (Signal connect appears below)

        entry2 = self.add_entry(grid,
            self.app_obj.ffmpeg_path,
            False,
            0, 5, grid_width, 1,
        )
        entry2.set_sensitive(False)
        entry2.set_editable(False)
        entry2.set_hexpand(True)

        if os.name == 'nt':
            entry2.set_sensitive(False)
            entry2.set_text(_('Not supported on MS Windows'))
            button4.set_sensitive(False)
            button5.set_sensitive(False)
            button6.set_sensitive(False)

        # (Signal connects from above)
        button4.connect('clicked', self.on_set_avconv_button_clicked, entry2)
        button5.connect('clicked', self.on_reset_avconv_button_clicked, entry2)
        button6.connect(
            'clicked',
            self.on_default_avconv_button_clicked,
            entry2,
        )


    def setup_downloader_ytsc_tab(self, inner_notebook):

        """Called by self.setup_downloader_tab().

        Sets up the 'Stream Capture' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Stream Capture'),
            inner_notebook,
        )

        grid_width = 4

        # Youtube Stream Capture file path
        self.add_label(grid,
            '<u>' + _('Youtube Stream Capture file path') + '</u>',
            0, 0, grid_width, 1,
        )
        self.add_label(grid,
            '<i>' + _(
            'Tartube includes a copy of this script, but you can use a' \
            + ' different copy, if you want',
            ) + '</i>',
            0, 1, grid_width, 1,
        )

        self.add_label(grid,
            _('Path to the YT Stream Capture executable'),
            0, 2, 1, 1,
        )

        button = Gtk.Button(_('Set'))
        grid.attach(button, 1, 2, 1, 1)
        # (Signal connect appears below)

        button2 = Gtk.Button(_('Reset'))
        grid.attach(button2, 2, 2, 1, 1)
        # (Signal connect appears below)

        button3 = Gtk.Button(_('Use default path'))
        grid.attach(button3, 3, 2, 1, 1)
        # (Signal connect appears below)

        entry = self.add_entry(grid,
            self.app_obj.ytsc_path,
            False,
            0, 3, grid_width, 1,
        )
        entry.set_sensitive(False)
        entry.set_editable(False)
        entry.set_hexpand(True)

        # (Signal connects from above)
        button.connect('clicked', self.on_set_ytsc_button_clicked, entry)
        button2.connect('clicked', self.on_reset_ytsc_button_clicked, entry)
        button3.connect('clicked', self.on_default_ytsc_button_clicked, entry)


    def setup_options_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Options' tab.
        """

        # Add this tab...
        tab, grid = self.add_notebook_tab('O_ptions')

        # ...and an inner notebook...
        inner_notebook = self.add_inner_notebook(grid)

        # ...with its own tabs
        self.setup_options_dl_list_tab(inner_notebook)
        self.setup_options_dl_prefs_tab(inner_notebook)
        self.setup_options_ffmpeg_list_tab(inner_notebook)


    def setup_options_dl_list_tab(self, inner_notebook):

        """Called by self.setup_options_tab().

        Sets up the 'Download options' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Download options'),
            inner_notebook,
        )
        grid_width = 4

        # List of download options managers
        self.add_label(grid,
            '<u>' + _('List of download options managers') + '</u>',
            0, 0, grid_width, 1,
        )

        # (GenericConfigWin.add_treeview() doesn't support multiple columns, so
        #   we'll do everything ourselves)
        frame = Gtk.Frame()
        grid.attach(frame, 0, 1, grid_width, 1)

        scrolled = Gtk.ScrolledWindow()
        frame.add(scrolled)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)

        treeview = Gtk.TreeView()
        scrolled.add(treeview)
        treeview.set_headers_visible(True)

        for i, column_title in enumerate(
            [
                '#', _('Name'), _('Default'), _('Classic Mode'),
                _('Applied to media'),
            ]
        ):
            if i == 2 or i == 3:
                renderer_toggle = Gtk.CellRendererToggle()
                column_toggle = Gtk.TreeViewColumn(
                    column_title,
                    renderer_toggle,
                    active=i,
                )
                treeview.append_column(column_toggle)
                column_toggle.set_resizable(False)
            else:
                renderer_text = Gtk.CellRendererText()
                column_text = Gtk.TreeViewColumn(
                    column_title,
                    renderer_text,
                    text=i,
                )
                treeview.append_column(column_text)
                column_text.set_resizable(True)

        self.options_liststore = Gtk.ListStore(int, str, bool, bool, str)
        treeview.set_model(self.options_liststore)

        # Initialise the list
        self.setup_options_dl_list_tab_update_treeview()

        # Add editing buttons
        self.add_label(grid,
            'Manager name',
            0, 2, 1, 1,
        )

        entry = self.add_entry(grid,
            None,
            True,
            1, 2, 1, 1,
        )

        button = Gtk.Button()
        grid.attach(button, 2, 2, 1, 1)
        button.set_label(_('Add'))
        button.connect(
            'clicked',
            self.on_options_add_button_clicked,
            entry,
        )

        button2 = Gtk.Button()
        grid.attach(button2, 3, 2, 1, 1)
        button2.set_label(_('Import'))
        button2.connect(
            'clicked',
            self.on_options_import_button_clicked,
            entry,
        )

        # (Use a separate Gtk.Grid on the row below those buttons, so we don't
        #   mess up the formatting)
        grid2 = Gtk.Grid()
        grid.attach(grid2, 0, 3, grid_width, 1)

        button3 = Gtk.Button()
        grid2.attach(button3, 0, 0, 1, 1)
        button3.set_label(_('Edit'))
        button3.connect(
            'clicked',
            self.on_options_edit_button_clicked,
            treeview,
        )

        button4 = Gtk.Button()
        grid2.attach(button4, 1, 0, 1, 1)
        button4.set_label(_('Export'))
        button4.connect(
            'clicked',
            self.on_options_export_button_clicked,
            treeview,
        )

        button5 = Gtk.Button()
        grid2.attach(button5, 2, 0, 1, 1)
        button5.set_label(_('Clone'))
        button5.connect(
            'clicked',
            self.on_options_clone_button_clicked,
            treeview,
        )

        button6 = Gtk.Button()
        grid2.attach(button6, 3, 0, 1, 1)
        button6.set_label(_('Use in Classic Mode tab'))
        button6.connect(
            'clicked',
            self.on_options_use_classic_button_clicked,
            treeview,
        )

        button7 = Gtk.Button()
        grid2.attach(button7, 4, 0, 1, 1)
        button7.set_label(_('Delete'))
        button7.connect(
            'clicked',
            self.on_options_delete_button_clicked,
            treeview,
        )

        # (Use an empty label for spacing)
        label = self.add_label(grid2,
            '',
            5, 0, 1, 1,
        )
        label.set_hexpand(True)

        button8 = Gtk.Button()
        grid2.attach(button8, 6, 0, 1, 1)
        button8.set_label(_('Refresh list'))
        button8.connect(
            'clicked',
            self.setup_options_dl_list_tab_update_treeview,
        )


    def setup_options_dl_list_tab_update_treeview(self):

        """Can be called by anything.

        Fills or updates the treeview.

        """

        self.options_liststore.clear()

        for uid in sorted(self.app_obj.options_reg_dict):
            self.setup_options_dl_list_tab_add_row(
                self.app_obj.options_reg_dict[uid],
            )


    def setup_options_dl_list_tab_add_row(self, options_obj):

        """Can be called by anything.

        Adds a row to the treeview.

        Args:

            options_obj (options.OptionsManager) - The options manager object
                to display on this row

        """

        row_list = []

        row_list.append(options_obj.uid)
        row_list.append(
            utils.tidy_up_long_string(
                options_obj.name,
                self.app_obj.main_win_obj.short_string_max_len,
            ),
        )

        if self.app_obj.general_options_obj \
        and self.app_obj.general_options_obj == options_obj:
            row_list.append(True)
        else:
            row_list.append(False)

        if self.app_obj.classic_options_obj \
        and self.app_obj.classic_options_obj == options_obj:
            row_list.append(True)
        else:
            row_list.append(False)

        if options_obj.dbid is None:

            row_list.append('')

        else:

            media_data_obj = self.app_obj.media_reg_dict[options_obj.dbid]
            row_list.append(
                media_data_obj.get_translated_type(True) \
                + ': ' + media_data_obj.name,
            )

        self.options_liststore.append(row_list)


    def setup_options_dl_prefs_tab(self, inner_notebook):

        """Called by self.setup_downloader_tab().

        Sets up the 'Preferences' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Preferences'),
            inner_notebook,
        )
        grid_width = 2

        # Download options preferences
        self.add_label(grid,
            '<u>' + _('Download options preferences') + '</u>',
            0, 0, 1, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _(
            'When applying download options to something, clone the general' \
            + ' download options',
            ),
            self.app_obj.auto_clone_options_flag,
            True,                   # Can be toggled by user
            0, 1, 1, 1,
        )
        checkbutton.connect('toggled', self.on_auto_clone_button_toggled)

        checkbutton = self.add_checkbutton(grid,
            _(
            'After downloading a video, destroy its download options',
            ),
            self.app_obj.auto_delete_options_flag,
            True,                   # Can be toggled by user
            0, 2, 1, 1,
        )
        checkbutton.connect('toggled', self.on_auto_delete_button_toggled)


    def setup_options_ffmpeg_list_tab(self, inner_notebook):

        """Called by self.setup_options_tab().

        Sets up the 'FFmpeg options' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_FFmpeg options'),
            inner_notebook,
        )
        grid_width = 4

        # List of FFmpeg options managers
        self.add_label(grid,
            '<u>' + _('List of FFmpeg options managers') + '</u>',
            0, 0, grid_width, 1,
        )

        # (GenericConfigWin.add_treeview() doesn't support multiple columns, so
        #   we'll do everything ourselves)
        frame = Gtk.Frame()
        grid.attach(frame, 0, 1, grid_width, 1)

        scrolled = Gtk.ScrolledWindow()
        frame.add(scrolled)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)

        treeview = Gtk.TreeView()
        scrolled.add(treeview)
        treeview.set_headers_visible(True)

        # (Fourth column is empty, to keep the 3rd column at a minimum width)
        for i, column_title in enumerate(
            [ '#', _('Name'), _('Current'), '' ]
        ):
            if i == 2:
                renderer_toggle = Gtk.CellRendererToggle()
                column_toggle = Gtk.TreeViewColumn(
                    column_title,
                    renderer_toggle,
                    active=i,
                )
                treeview.append_column(column_toggle)
                column_toggle.set_resizable(False)
            else:
                renderer_text = Gtk.CellRendererText()
                column_text = Gtk.TreeViewColumn(
                    column_title,
                    renderer_text,
                    text=i,
                )
                treeview.append_column(column_text)
                column_text.set_resizable(True)

        self.ffmpeg_liststore = Gtk.ListStore(int, str, bool, str)
        treeview.set_model(self.ffmpeg_liststore)

        # Initialise the list
        self.setup_options_ffmpeg_list_tab_update_treeview()

        # Add editing buttons
        self.add_label(grid,
            'Manager name',
            0, 2, 1, 1,
        )

        entry = self.add_entry(grid,
            None,
            True,
            1, 2, 1, 1,
        )

        button = Gtk.Button()
        grid.attach(button, 2, 2, 1, 1)
        button.set_label(_('Add'))
        button.connect(
            'clicked',
            self.on_ffmpeg_add_button_clicked,
            entry,
        )

        button2 = Gtk.Button()
        grid.attach(button2, 3, 2, 1, 1)
        button2.set_label(_('Import'))
        button2.connect(
            'clicked',
            self.on_ffmpeg_import_button_clicked,
            entry,
        )

        # (Use a separate Gtk.Grid on the row below those buttons, so we don't
        #   mess up the formatting)
        grid2 = Gtk.Grid()
        grid.attach(grid2, 0, 3, grid_width, 1)

        button3 = Gtk.Button()
        grid2.attach(button3, 0, 0, 1, 1)
        button3.set_label(_('Edit'))
        button3.connect(
            'clicked',
            self.on_ffmpeg_edit_button_clicked,
            treeview,
        )

        button4 = Gtk.Button()
        grid2.attach(button4, 1, 0, 1, 1)
        button4.set_label(_('Export'))
        button4.connect(
            'clicked',
            self.on_ffmpeg_export_button_clicked,
            treeview,
        )

        button5 = Gtk.Button()
        grid2.attach(button5, 2, 0, 1, 1)
        button5.set_label(_('Clone'))
        button5.connect(
            'clicked',
            self.on_ffmpeg_clone_button_clicked,
            treeview,
        )

        button6 = Gtk.Button()
        grid2.attach(button6, 3, 0, 1, 1)
        button6.set_label(_('Use these options'))
        button6.connect(
            'clicked',
            self.on_ffmpeg_use_button_clicked,
            treeview,
        )

        button7 = Gtk.Button()
        grid2.attach(button7, 4, 0, 1, 1)
        button7.set_label(_('Delete'))
        button7.connect(
            'clicked',
            self.on_ffmpeg_delete_button_clicked,
            treeview,
        )

        # (Use an empty label for spacing)
        label = self.add_label(grid2,
            '',
            5, 0, 1, 1,
        )
        label.set_hexpand(True)

        button8 = Gtk.Button()
        grid2.attach(button8, 6, 0, 1, 1)
        button8.set_label(_('Refresh list'))
        button8.connect(
            'clicked',
            self.setup_options_ffmpeg_list_tab_update_treeview,
        )


    def setup_options_ffmpeg_list_tab_update_treeview(self):

        """Can be called by anything.

        Fills or updates the treeview.

        """

        self.ffmpeg_liststore.clear()

        for uid in sorted(self.app_obj.ffmpeg_reg_dict):
            self.setup_options_ffmpeg_list_tab_add_row(
                self.app_obj.ffmpeg_reg_dict[uid],
            )


    def setup_options_ffmpeg_list_tab_add_row(self, options_obj):

        """Can be called by anything.

        Adds a row to the treeview.

        Args:

            options_obj (ffmpeg_tartube.FFmpegOptionsManager): The FFmpeg
                options manager object to display on this row

        """

        row_list = []

        row_list.append(options_obj.uid)
        row_list.append(
            utils.tidy_up_long_string(
                options_obj.name,
                self.app_obj.main_win_obj.short_string_max_len,
            ),
        )

        if self.app_obj.ffmpeg_options_obj \
        and self.app_obj.ffmpeg_options_obj == options_obj:
            row_list.append(True)
        else:
            row_list.append(False)

        # (Fourth column is empty, to keep the 3rd column at a minimum width)
        row_list.append('')

        self.ffmpeg_liststore.append(row_list)


    def setup_output_tab(self):

        """Called by self.setup_tabs().

        Sets up the 'Output' tab.
        """

        # Add this tab...
        tab, grid = self.add_notebook_tab(_('O_utput'), 0)

        # ...and an inner notebook...
        inner_notebook = self.add_inner_notebook(grid)

        # ...with its own tabs
        self.setup_output_outputtab_tab(inner_notebook)
        self.setup_output_terminal_window_tab(inner_notebook)
        self.setup_output_both_tab(inner_notebook)


    def setup_output_outputtab_tab(self, inner_notebook):

        """Called by self.setup_output_tab().

        Sets up the 'Output Tab' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Output Tab'),
            inner_notebook,
        )

        grid_width = 2

        # Output Tab preferences
        self.add_label(grid,
            '<u>' + _('Output Tab preferences') + '</u>',
            0, 0, grid_width, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _('Display downloader system commands in the Output Tab'),
            self.app_obj.ytdl_output_system_cmd_flag,
            True,               # Can be toggled by user
            0, 1, grid_width, 1,
        )
        checkbutton.set_hexpand(False)
        checkbutton.connect('toggled', self.on_output_system_button_toggled)

        checkbutton2 = self.add_checkbutton(grid,
            _('Display output from downloader\'s STDOUT in the Output Tab'),
            self.app_obj.ytdl_output_stdout_flag,
            True,               # Can be toggled by user
            0, 2, grid_width, 1,
        )
        checkbutton2.set_hexpand(False)
        # (Signal connect appears below)

        checkbutton3 = self.add_checkbutton(grid,
            _('...but don\'t write each video\'s JSON data'),
            self.app_obj.ytdl_output_ignore_json_flag,
            True,               # Can be toggled by user
            0, 3, grid_width, 1,
        )
        checkbutton3.set_hexpand(False)
        checkbutton3.connect('toggled', self.on_output_json_button_toggled)
        if not self.app_obj.ytdl_output_stdout_flag:
            checkbutton3.set_sensitive(False)

        checkbutton4 = self.add_checkbutton(grid,
            _('...but don\'t write each video\'s download progress'),
            self.app_obj.ytdl_output_ignore_progress_flag,
            True,               # Can be toggled by user
            0, 4, grid_width, 1,
        )
        checkbutton4.set_hexpand(False)
        checkbutton4.connect('toggled', self.on_output_progress_button_toggled)
        if not self.app_obj.ytdl_output_stdout_flag:
            checkbutton4.set_sensitive(False)

        # (Signal connect from above)
        checkbutton2.connect(
            'toggled',
            self.on_output_stdout_button_toggled,
            checkbutton3,
            checkbutton4,
        )

        checkbutton5 = self.add_checkbutton(grid,
            _('Display output from downloader\'s STDERR in the Output Tab'),
            self.app_obj.ytdl_output_stderr_flag,
            True,               # Can be toggled by user
            0, 5, grid_width, 1,
        )
        checkbutton5.set_hexpand(False)
        checkbutton5.connect('toggled', self.on_output_stderr_button_toggled)

        checkbutton6 = self.add_checkbutton(grid,
            _('Limit the size of Output Tab pages to'),
            self.app_obj.output_size_apply_flag,
            True,               # Can be toggled by user
            0, 6, 1, 1,
        )
        checkbutton6.set_hexpand(False)
        checkbutton6.connect('toggled', self.on_output_size_button_toggled)

        spinbutton = self.add_spinbutton(grid,
            self.app_obj.output_size_min,
            self.app_obj.output_size_max,
            1,                  # Step
            self.app_obj.output_size_default,
            1, 6, 1, 1,
        )
        spinbutton.connect(
            'value-changed',
            self.on_output_size_spinbutton_changed,
        )

        checkbutton7 = self.add_checkbutton(grid,
            _('Empty pages in the Output Tab at the start of every operation'),
            self.app_obj.ytdl_output_start_empty_flag,
            True,               # Can be toggled by user
            0, 7, grid_width, 1,
        )
        checkbutton7.set_hexpand(False)
        checkbutton7.connect('toggled', self.on_output_empty_button_toggled)

        checkbutton8 = self.add_checkbutton(grid,
            _(
            'Show a summary of active threads (changes are applied when' \
            + ' Tartube restarts)',
            ),
            self.app_obj.ytdl_output_show_summary_flag,
            True,               # Can be toggled by user
            0, 8, grid_width, 1,
        )
        checkbutton8.set_hexpand(False)
        checkbutton8.connect('toggled', self.on_output_summary_button_toggled)

        checkbutton9 = self.add_checkbutton(grid,
            _(
            'During an update operation, automatically switch to the Output' \
            + ' tab',
            ),
            self.app_obj.auto_switch_output_flag,
            True,                   # Can be toggled by user
            0, 9, grid_width, 1,
        )
        checkbutton9.connect('toggled', self.on_auto_switch_button_toggled)

        checkbutton10 = self.add_checkbutton(grid,
            _(
            'During a refresh operation, show all matching videos in the' \
            + ' Output Tab',
            ),
            self.app_obj.refresh_output_videos_flag,
            True,               # Can be toggled by user
            0, 10, grid_width, 1,
        )
        checkbutton10.set_hexpand(False)
        # (Signal connect appears below)

        checkbutton11 = self.add_checkbutton(grid,
            _('...also show all non-matching videos'),
            self.app_obj.refresh_output_verbose_flag,
            True,               # Can be toggled by user
            0, 11, grid_width, 1,
        )
        checkbutton11.set_hexpand(False)
        checkbutton11.connect(
            'toggled',
            self.on_refresh_verbose_button_toggled,
        )
        if not self.app_obj.refresh_output_videos_flag:
            checkbutton10.set_sensitive(False)

        # (Signal connect from above)
        checkbutton10.connect(
            'toggled',
            self.on_refresh_videos_button_toggled,
            checkbutton11,
        )


    def setup_output_terminal_window_tab(self, inner_notebook):

        """Called by self.setup_output_tab().

        Sets up the 'Terminal window' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(
            _('_Terminal window'),
            inner_notebook,
        )

        # Terminal window preferences
        self.add_label(grid,
            '<u>' + _('Terminal window preferences') + '</u>',
            0, 0, 1, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _('Write downloader system commands to the terminal window'),
            self.app_obj.ytdl_write_system_cmd_flag,
            True,               # Can be toggled by user
            0, 1, 1, 1,
        )
        checkbutton.set_hexpand(False)
        checkbutton.connect('toggled', self.on_terminal_system_button_toggled)

        checkbutton2 = self.add_checkbutton(grid,
            _('Write output from downloader\'s STDOUT to the terminal window'),
            self.app_obj.ytdl_write_stdout_flag,
            True,               # Can be toggled by user
            0, 2, 1, 1,
        )
        checkbutton2.set_hexpand(False)
        # (Signal connect appears below)

        checkbutton3 = self.add_checkbutton(grid,
            _('...but don\'t write each video\'s JSON data'),
            self.app_obj.ytdl_write_ignore_json_flag,
            True,               # Can be toggled by user
            0, 3, 1, 1,
        )
        checkbutton3.set_hexpand(False)
        checkbutton3.connect('toggled', self.on_terminal_json_button_toggled)
        if not self.app_obj.ytdl_write_stdout_flag:
            checkbutton3.set_sensitive(False)

        checkbutton4 = self.add_checkbutton(grid,
            _('...but don\'t write each video\'s download progress'),
            self.app_obj.ytdl_write_ignore_progress_flag,
            True,               # Can be toggled by user
            0, 4, 1, 1,
        )
        checkbutton4.set_hexpand(False)
        checkbutton4.connect(
            'toggled',
            self.on_terminal_progress_button_toggled,
        )
        if not self.app_obj.ytdl_write_stdout_flag:
            checkbutton4.set_sensitive(False)

        # (Signal connect from above)
        checkbutton2.connect(
            'toggled',
            self.on_terminal_stdout_button_toggled,
            checkbutton3,
            checkbutton4,
        )

        checkbutton5 = self.add_checkbutton(grid,
            _('Write output from downloader\'s STDERR to the terminal window'),
            self.app_obj.ytdl_write_stderr_flag,
            True,               # Can be toggled by user
            0, 5, 1, 1,
        )
        checkbutton5.set_hexpand(False)
        checkbutton5.connect(
            'toggled',
            self.on_terminal_stderr_button_toggled,
        )


    def setup_output_both_tab(self, inner_notebook):

        """Called by self.setup_output_tab().

        Sets up the 'Both' inner notebook tab.
        """

        tab, grid = self.add_inner_notebook_tab(_('_Both'), inner_notebook)

        # Special preferences
        self.add_label(grid,
            '<u>' + _(
                'Special preferences (applies to both the Output Tab and the' \
                + ' terminal window)',
            ) + '</u>',
            0, 0, 1, 1,
        )

        checkbutton = self.add_checkbutton(grid,
            _('Downloader writes verbose output (youtube-dl debugging mode)'),
            self.app_obj.ytdl_write_verbose_flag,
            True,               # Can be toggled by user
            0, 1, 1, 1,
        )
        checkbutton.set_hexpand(False)
        checkbutton.connect('toggled', self.on_ytdl_verbose_button_toggled)

        checkbutton = self.add_checkbutton(grid,
            _('Youtube Stream Capture writes verbose output'),
            self.app_obj.ytsc_write_verbose_flag,
            True,               # Can be toggled by user
            0, 2, 1, 1,
        )
        checkbutton.set_hexpand(False)
        checkbutton.connect('toggled', self.on_ytsc_verbose_button_toggled)


    # Callback class methods


    def on_add_from_list_button_toggled(self, checkbutton):

        """Called from callback in self.setup_files_database_tab().

        Enables/disables automatic adding of new Tartube data directories to
        the list of recent directories.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.data_dir_add_from_list_flag:
            self.app_obj.set_data_dir_add_from_list_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.data_dir_add_from_list_flag:
            self.app_obj.set_data_dir_add_from_list_flag(False)


    def on_age_restrict_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_websites_tab().

        Enables/disables ignoring of YouTube age-restriction error messages.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ignore_yt_age_restrict_flag:
            self.app_obj.set_ignore_yt_age_restrict_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ignore_yt_age_restrict_flag:
            self.app_obj.set_ignore_yt_age_restrict_flag(False)


    def on_alt_website_changed(self, entry):

        """Called from callback in self.setup_operations_custom_tab().

        Sets the YouTube alternative front end to use.

        Args:

            entry (Gtk.Entry): The widget changed

        """

        self.app_obj.set_custom_dl_divert_website(entry.get_text())


    def on_archive_button_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_downloads_tab().

        Enables/disables creation of youtube-dl's archive file,
        ytdl-archive.txt.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.allow_ytdl_archive_flag:
            self.app_obj.set_allow_ytdl_archive_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.allow_ytdl_archive_flag:
            self.app_obj.set_allow_ytdl_archive_flag(False)


    def on_archive_classic_button_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_downloads_tab().

        Enables/disables creation of youtube-dl's archive file,
        ytdl-archive.txt, when downloading from the Classic Mode tab.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.classic_ytdl_archive_flag:
            self.app_obj.set_classic_ytdl_archive_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.classic_ytdl_archive_flag:
            self.app_obj.set_classic_ytdl_archive_flag(False)


    def on_auto_clone_button_toggled(self, checkbutton):

        """Called from callback in self.setup_options_prefs().

        Enables/disables auto-cloning of the General Options Manager.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.auto_clone_options_flag:
            self.app_obj.set_auto_clone_options_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.auto_clone_options_flag:
            self.app_obj.set_auto_clone_options_flag(False)


    def on_auto_delete_button_toggled(self, checkbutton):

        """Called from callback in self.setup_options_prefs().

        Enables/disables auto-deleting of download options applied to a
        media.Video, after it has been downloaded.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.auto_delete_options_flag:
            self.app_obj.set_auto_delete_options_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.auto_delete_options_flag:
            self.app_obj.set_auto_delete_options_flag(False)


    def on_auto_delete_button_toggled(self, checkbutton, spinbutton,
    checkbutton2):

        """Called from callback in self.setup_files_video_deletion_tab().

        Enables/disables automatic deletion of downloaded videos.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            spinbutton (Gtk.SpinButton): A widget to be (de)sensitised

            checkbutton2 (Gtk.CheckButton): Another widget to be
                (de)sensitised

        """

        if checkbutton.get_active() \
        and not self.app_obj.auto_delete_flag:
            self.app_obj.set_auto_delete_flag(True)
            spinbutton.set_sensitive(True)
            checkbutton2.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.auto_delete_flag:
            self.app_obj.set_auto_delete_flag(False)
            spinbutton.set_sensitive(False)
            checkbutton2.set_sensitive(False)


    def on_auto_delete_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_files_video_deletion_tab().

        Sets the number of days after which downloaded videos should be
        deleted.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.set_auto_delete_days(spinbutton.get_value())


    def on_auto_restart_button_toggled(self, checkbutton, checkbutton2,
    spinbutton, spinbutton2):

        """Called from callback in self.setup_operations_downloads_tab().

        Enables/disables restarting a stalled download operation.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            checkbutton2 (Gtk.CheckButton): Another widget to check

            spinbutton, spinbutton2 (Gtk.SpinButton): Other widgets to modify

        """

        if checkbutton.get_active() \
        and not self.app_obj.operation_auto_restart_flag:
            self.app_obj.set_operation_auto_restart_flag(True)
            spinbutton.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.operation_auto_restart_flag:
            self.app_obj.set_operation_auto_restart_flag(False)
            spinbutton.set_sensitive(False)

        if checkbutton.get_active() or checkbutton2.get_active():
            spinbutton2.set_sensitive(False)
        else:
            spinbutton2.set_sensitive(True)


    def on_auto_restart_network_button_toggled(self, checkbutton, checkbutton2,
    spinbutton):

        """Called from callback in self.setup_operations_downloads_tab().

        Enables/disables restarting a stalled download operation.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            checkbutton2 (Gtk.CheckButton): Another widget to check

            spinbutton (Gtk.SpinButton): Another widget to modify

        """

        if checkbutton.get_active() \
        and not self.app_obj.operation_auto_restart_network_flag:
            self.app_obj.set_operation_auto_restart_network_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.operation_auto_restart_network_flag:
            self.app_obj.set_operation_auto_restart_network_flag(False)

        if checkbutton.get_active() or checkbutton2.get_active():
            spinbutton.set_sensitive(True)
        else:
            spinbutton.set_sensitive(False)


    def on_auto_restart_max_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_operations_downloads_tab().

        Sets the maximum number of restarts after a stalled download.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.set_operation_auto_restart_max(spinbutton.get_value())


    def on_auto_restart_time_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_operations_downloads_tab().

        Sets the time after which a stalled download job is restarted.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.set_operation_auto_restart_time(spinbutton.get_value())


    def on_auto_switch_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_main_window_tab().

        Enables/disables automatically switching to the Output tab when an
        update operation starts.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.auto_switch_output_flag:
            self.app_obj.set_auto_switch_output_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.auto_switch_output_flag:
            self.app_obj.set_auto_switch_output_flag(False)


    def on_auto_update_button_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_downloads_tab().

        Enables/disables automatic update operation before every download
        operation.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.operation_auto_update_flag:
            self.app_obj.set_operation_auto_update_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.operation_auto_update_flag:
            self.app_obj.set_operation_auto_update_flag(False)


    def on_autostop_size_button_toggled(self, checkbutton, spinbutton, combo):

        """Called from callback in self.setup_scheduling_stop_tab().

        Enables/disables auto-stopping a download operation after a certain
        amount of disk space.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            spinbutton (Gtk.SpinButton): Another widget to modify

            combo (Gtk.ComboBox): Another widget to modify

        """

        if checkbutton.get_active() \
        and not self.app_obj.autostop_size_flag:
            self.app_obj.set_autostop_size_flag(True)
            spinbutton.set_sensitive(True)
            combo.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.autostop_size_flag:
            self.app_obj.set_autostop_size_flag(False)
            spinbutton.set_sensitive(False)
            combo.set_sensitive(False)


    def on_autostop_size_combo_changed(self, combo):

        """Called from a callback in self.setup_scheduling_stop_tab().

        Sets the disk space unit at which a download operation is auto-stopped.

        Args:

            combo (Gtk.ComboBox): The widget clicked

        """

        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        self.app_obj.set_autostop_size_unit(model[tree_iter][0])


    def on_autostop_size_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_scheduling_stop_tab().

        Sets the disk space value at which a download operation is
        auto-stopped.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.set_autostop_size_value(spinbutton.get_value())


    def on_autostop_time_button_toggled(self, checkbutton, spinbutton, combo):

        """Called from callback in self.setup_scheduling_stop_tab().

        Enables/disables auto-stopping a download operation after a certain
        time.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            spinbutton (Gtk.SpinButton): Another widget to modify

            combo (Gtk.ComboBox): Another widget to modify

        """

        if checkbutton.get_active() \
        and not self.app_obj.autostop_time_flag:
            self.app_obj.set_autostop_time_flag(True)
            spinbutton.set_sensitive(True)
            combo.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.autostop_time_flag:
            self.app_obj.set_autostop_time_flag(False)
            spinbutton.set_sensitive(False)
            combo.set_sensitive(False)


    def on_autostop_time_combo_changed(self, combo):

        """Called from a callback in self.setup_scheduling_stop_tab().

        Sets the time unit at which a download operation is auto-stopped.

        Args:

            combo (Gtk.ComboBox): The widget clicked

        """

        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        self.app_obj.set_autostop_time_unit(model[tree_iter][0])


    def on_autostop_time_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_scheduling_stop_tab().

        Sets the time value at which a download operation is auto-stopped.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.set_autostop_time_value(spinbutton.get_value())


    def on_autostop_videos_button_toggled(self, checkbutton, spinbutton):

        """Called from callback in self.setup_scheduling_stop_tab().

        Enables/disables auto-stopping a download operation after a certain
        number of videos.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            spinbutton (Gtk.SpinButton): Another widget to modify

        """

        if checkbutton.get_active() \
        and not self.app_obj.autostop_videos_flag:
            self.app_obj.set_autostop_videos_flag(True)
            spinbutton.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.autostop_videos_flag:
            self.app_obj.set_autostop_videos_flag(False)
            spinbutton.set_sensitive(False)


    def on_autostop_videos_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_scheduling_stop_tab().

        Sets the number of videos at which a download operation is
        auto-stopped.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.set_autostop_videos_value(spinbutton.get_value())


    def on_backup_button_toggled(self, radiobutton, value):

        """Called from callback in self.setup_files_backups_tab().

        Updates IVs in the main application.

        Args:

            radiobutton (Gtk.RadioButton): The widget clicked

            value (str): The new value of the IV

        """

        if radiobutton.get_active():
            self.app_obj.set_db_backup_mode(value)


    def on_bandwidth_button_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_performance_tab().

        Enables/disables the download speed limit. Toggling the corresponding
        Gtk.CheckButton in the Progress Tab sets the IV (and makes sure the two
        checkbuttons have the same status).

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        other_flag \
        = self.app_obj.main_win_obj.bandwidth_checkbutton.get_active()

        if (checkbutton.get_active() and not other_flag):
            self.app_obj.main_win_obj.bandwidth_checkbutton.set_active(True)
        elif (not checkbutton.get_active() and other_flag):
            self.app_obj.main_win_obj.bandwidth_checkbutton.set_active(False)


    def on_bandwidth_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_operations_performance_tab().

        Sets the simultaneous download limit. Setting the value of the
        corresponding Gtk.SpinButton in the Progress Tab sets the IV (and
        makes sure the two spinbuttons have the same value).

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.main_win_obj.bandwidth_spinbutton.set_value(
            spinbutton.get_value(),
        )


    def on_check_limit_changed(self, entry):

        """Called from callback in self.setup_operations_time_saving_tab().

        Sets the limit at which a download operation will stop checking a
        channel or playlist.

        Args:

            entry (Gtk.Entry): The widget changed

        """

        text = entry.get_text()
        if text.isdigit() and int(text) >= 0:
            self.app_obj.set_operation_check_limit(int(text))


    def on_child_process_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_errors_warnings_tab().

        Enables/disables ignoring of child process exit error messages.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ignore_child_process_exit_flag:
            self.app_obj.set_ignore_child_process_exit_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ignore_child_process_exit_flag:
            self.app_obj.set_ignore_child_process_exit_flag(False)


    def on_clipboard_button_toggled(self, checkbutton):

        """Called from a callback in self.setup_windows_dialogues_tab().

        Enables/disables copying from the system clipboard in various dialogue
        windows.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.dialogue_copy_clipboard_flag:
            self.app_obj.set_dialogue_copy_clipboard_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.dialogue_copy_clipboard_flag:
            self.app_obj.set_dialogue_copy_clipboard_flag(False)


    def on_close_to_tray_toggled(self, checkbutton):

        """Called from a callback in self.setup_windows_system_tray_tab().

        Enables/disables closing to the system tray, rather than closing the
        application.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.close_to_tray_flag:
            self.app_obj.set_close_to_tray_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.close_to_tray_flag:
            self.app_obj.set_close_to_tray_flag(False)


    def on_complex_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_videos_tab().

        Switches between simple/complex views in the Video Index.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        redraw_flag = False
        if checkbutton.get_active() and not self.app_obj.complex_index_flag:
            self.app_obj.set_complex_index_flag(True)
            redraw_flag = True
        elif not checkbutton.get_active() and self.app_obj.complex_index_flag:
            self.app_obj.set_complex_index_flag(False)
            redraw_flag = True

        if redraw_flag:
            # Redraw the Video Index and the Video Catalogue (since nothing in
            #   the Video Index will be selected)
            self.app_obj.main_win_obj.video_index_catalogue_reset()


    def on_convert_from_button_toggled(self, radiobutton, mode):

        """Called from callback in self.setup_operations_prefs_tab().

        Set what happens when downloading a media.Video object whose URL
        represents a channel/playlist.

        Args:

            radiobutton (Gtk.RadioButton): The widget clicked

            mode (str): The new value for the IV: 'disable', 'multi',
                'channel' or 'playlist'

        """

        if radiobutton.get_active():
            self.app_obj.set_operation_convert_mode(mode)


    def on_copyright_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_websites_tab().

        Enables/disables ignoring of YouTube copyright errors messages.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ignore_yt_copyright_flag:
            self.app_obj.set_ignore_yt_copyright_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ignore_yt_copyright_flag:
            self.app_obj.set_ignore_yt_copyright_flag(False)


    def on_custom_delay_button_toggled(self, checkbutton, spinbutton,
    spinbutton2):

        """Called from callback in self.setup_operations_custom_tab().

        Enables/disables a delay after downloads of a media data object
        (during custom downloads).

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            spinbutton, spinbutton2 (Gtk.SpinButton): Other widgets to be
                (de)sensitised

        """

        if checkbutton.get_active() \
        and not self.app_obj.custom_dl_delay_flag:
            self.app_obj.set_custom_dl_delay_flag(True)
            spinbutton.set_sensitive(True)
            spinbutton2.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.custom_dl_delay_flag:
            self.app_obj.set_custom_dl_delay_flag(False)
            spinbutton.set_sensitive(False)
            spinbutton2.set_sensitive(False)


    def on_custom_divert_button_toggled(self, radiobutton, entry, value):

        """Called from callback in self.setup_operations_custom_tab().

        Enables/disables diverting downloads of YouTube videos to HookTube or
        Invidious.

        Args:

            radiobutton (Gtk.RadioButton): The widget clicked

            entry (Gtk.Entry): Another widget to be modified

            value (str): The new value of the IV

        """

        if radiobutton.get_active():
            self.app_obj.set_custom_dl_divert_mode(value)

        if value == 'other':
            entry.set_sensitive(True)
        else:
            entry.set_text('')
            entry.set_sensitive(False)


    def on_custom_textview_changed(self, textbuffer):

        """Called from callback in self.setup_windows_websites_tab().

        Sets the custom of list of ignorable error messages.

        Args:

            textbuffer (Gtk.TextBuffer): The buffer belonging to the textview
                whose contents has been modified

        """

        text = textbuffer.get_text(
            textbuffer.get_start_iter(),
            textbuffer.get_end_iter(),
            # Don't include hidden characters
            False,
        )

        # Filter out empty lines
        line_list = text.split("\n")
        mod_list = []
        for line in line_list:
            if re.search(r'\S', line):
                mod_list.append(line)

        # Apply the changes
        self.app_obj.set_ignore_custom_msg_list(mod_list)


    def on_custom_video_button_toggled(self, checkbutton, radiobutton,
        radiobutton2, radiobutton3, radiobutton4, entry):

        """Called from callback in self.setup_operations_custom_tab().

        Enables/disables downloading videos independently of its channel/
        playlist.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            radiobutton, radiobutton2, radiobutton3, radiobutton4
                (Gtk.RadioButton): Other widgets to update

            entry (Gtk.Entry): Another widget to update

        """

        if checkbutton.get_active() \
        and not self.app_obj.custom_dl_by_video_flag:

            self.app_obj.set_custom_dl_by_video_flag(True)
            radiobutton.set_sensitive(True)
            radiobutton2.set_sensitive(True)
            radiobutton3.set_sensitive(True)
            radiobutton4.set_sensitive(True)
            entry.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.custom_dl_by_video_flag:

            self.app_obj.set_custom_dl_by_video_flag(False)
            radiobutton.set_sensitive(False)
            radiobutton2.set_sensitive(False)
            radiobutton3.set_sensitive(False)
            radiobutton4.set_sensitive(False)
            entry.set_sensitive(False)


    def on_data_block_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_errors_warnings_tab().

        Enables/disables ignoring of data block error messages.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ignore_data_block_error_flag:
            self.app_obj.set_ignore_data_block_error_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ignore_data_block_error_flag:
            self.app_obj.set_ignore_data_block_error_flag(False)


    def on_data_check_button_clicked(self, button):

        """Called from callback in self.setup_files_database_tab().

        Checks the Tartube database for inconsistencies, and fixes them.

        Args:

            button (Gtk.Button): The widget clicked

        """

        self.app_obj.check_integrity_db(
            False,      # Don't run silently; prompt the user before repairing
            self,       # This window, not the main window, is the parent
        )


    def on_data_dir_change_button_clicked(self, button, entry):

        """Called from callback in self.setup_files_database_tab().

        Opens a window in which the user can select Tartube's data directoy.
        If the user actually selects it, call the main application to take
        action.

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Additional widget to be modified by this
                function

        """

        dialogue_win = self.app_obj.dialogue_manager_obj.show_file_chooser(
            _('Please select Tartube\'s data folder'),
            self,
            'folder',
        )

        response = dialogue_win.run()
        if response == Gtk.ResponseType.OK:
            new_path = dialogue_win.get_filename()

        dialogue_win.destroy()

        if response == Gtk.ResponseType.OK:

            dialogue_manager_obj = self.app_obj.dialogue_manager_obj

            # In the past, I accidentally created a new database directory
            #   just inside an existing one, rather than switching to the
            #   existing one
            # If no database file exists, prompt the user to create a new one
            db_path = os.path.abspath(
                os.path.join(new_path, self.app_obj.db_file_name),
            )

            if not os.path.isfile(db_path):

                dialogue_manager_obj.show_msg_dialogue(
                    _(
                        'Are you sure you want to create a new database at' \
                        + ' this location?',
                    ) + '\n\n' + new_path,
                    'question',
                    'yes-no',
                    self,           # Parent window is this window
                    {
                        'yes': 'switch_db',
                        'data': [new_path, self],
                    },
                )

            else:

                # Database file already exists, so try to load it now
                self.try_switch_db(new_path, button)


    def on_data_dir_cursor_changed(self, treeview, button2, button3, button4,
    button5, button6):

        """Called by self.setup_files_database_tab().

        When a data directory in the list is selected, (de)sensitise buttons
        in response.

        Args:

            treeview (Gtk.TreeView): The widget in which a line was selected.

            button2, button3, button4, button5, button6 (Gtk.Button): Other
                widgets to be modified

        """

        selection = treeview.get_selection()
        (model, iter) = selection.get_selected()
        if iter is not None and not self.app_obj.disable_load_save_flag:

            data_dir = model[iter][0]

            if data_dir != self.app_obj.data_dir:
                button2.set_sensitive(True)
                button3.set_sensitive(True)
            else:
                button2.set_sensitive(False)
                button3.set_sensitive(False)

            posn = self.app_obj.data_dir_alt_list.index(data_dir)
            if posn > 0:
                button5.set_sensitive(True)
            else:
                button5.set_sensitive(False)

            if posn < (len(self.app_obj.data_dir_alt_list) - 1):
                button6.set_sensitive(True)
            else:
                button6.set_sensitive(False)

        else:

            button2.set_sensitive(False)
            button3.set_sensitive(False)
            button5.set_sensitive(False)
            button6.set_sensitive(False)

        if len(self.app_obj.data_dir_alt_list) <= 1 \
        or self.app_obj.disable_load_save_flag:
            button4.set_sensitive(False)
        else:
            button4.set_sensitive(True)


    def on_data_dir_forget_button_clicked(self, button, treeview):

        """Called from callback in self.setup_files_database_tab().

        Removes the selected the data directory from the list of alternative
        data directories.

        Args:

            button (Gtk.Button): The widget that was clicked

            treeview (Gtk.TreeView): The widget in which a line was selected.

        """

        selection = treeview.get_selection()
        (model, iter) = selection.get_selected()
        if iter is None:

            # Nothing selected
            return

        else:

            data_dir = model[iter][0]

        # Should not be possible to click the button, when the current
        #   directory is selected, but we'll check anyway
        if data_dir == self.app_obj.data_dir:
            return

        # Prompt the user for confirmation. If the user confirms, this window
        #   is reset to update the treeview
        self.app_obj.dialogue_manager_obj.show_msg_dialogue(
            _('Are you sure you want to forget this database?'),
            'question',
            'yes-no',
            self,           # Parent window is this window
            {
                'yes': 'forget_db',
                'data': [data_dir, self],
            },
        )


    def on_data_dir_forget_all_button_clicked(self, button, treeview):

        """Called from callback in self.setup_files_database_tab().

        Removes all data directories from the list of alternatives, except for
        the current one.

        Args:

            button (Gtk.Button): The widget that was clicked

            treeview (Gtk.TreeView): The widget in which a line was selected.

        """

        # Should not be possible to click the button, when the list contains
        #   no alternatives but the current one, but we'll check anyway
        if len(self.app_obj.data_dir_alt_list) <= 1:
            return

        # Prompt the user for confirmation. If the user confirms, this window
        #   is reset to update the treeview
        self.app_obj.dialogue_manager_obj.show_msg_dialogue(
            _(
            'Are you sure you want to forget all databases except the' \
            + ' current one?',
            ),
            'question',
            'yes-no',
            self,           # Parent window is this window
            {
                'yes': 'forget_all_db',
                'data': self,
            },
        )


    def on_data_dir_move_down_button_clicked(self, button, treeview, \
    liststore, button2):

        """Called from callback in self.setup_files_database_tab().

        Moves the selected data directory down one position in the list of
        alternative data directories.

        Args:

            button (Gtk.Button): The widget that was clicked (the down button)

            treeview (Gtk.TreeView): The widget in which a line was selected

            liststore (Gtk.ListStore): The treeview's liststore

            button2 (Gtk.Button): The up button

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        if not path_list:

            # Nothing selected
            return

        # (Keeping track of the first/last selected items helps us to
        #   (de)sensitise buttons, in a moment)
        first_item = None
        last_item = None

        path_list.reverse()

        for path in path_list:

            this_iter = model.get_iter(path)
            last_item = model[this_iter][0]
            if first_item is None:
                first_item = model[this_iter][0]

            if model.iter_next(this_iter):

                liststore.move_after(
                    this_iter,
                    model.iter_next(this_iter),
                )

            else:

                # If the first item won't move up, then successive items will
                #   be moved above this one (which is not what we want)
                break

        # Update the IV
        dir_list = []
        for row in liststore:
            dir_list.append(row[0])

        self.app_obj.set_data_dir_alt_list(dir_list)

        # (De)sensitise the button(s), if required
        if dir_list.index(first_item) == 0:
            button2.set_sensitive(False)
        else:
            button2.set_sensitive(True)

        if dir_list.index(last_item) == (len(dir_list) - 1):
            button.set_sensitive(False)
        else:
            button.set_sensitive(True)


    def on_data_dir_move_up_button_clicked(self, button, treeview, liststore,
    button2):

        """Called from callback in self.setup_files_database_tab().

        Moves the selected data directory up one position in the list of
        alternative data directories.

        Args:

            button (Gtk.Button): The widget that was clicked (the up button)

            treeview (Gtk.TreeView): The widget in which a line was selected

            liststore (Gtk.ListStore): The treeview's liststore

            button2 (Gtk.Button): The down button

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        if not path_list:

            # Nothing selected
            return

        # (Keeping track of the first/last selected items helps us to
        #   (de)sensitise buttons, in a moment)
        first_item = None
        last_item = None

        # Move the selected items up
        for path in path_list:

            this_iter = model.get_iter(path)
            last_item = model[this_iter][0]
            if first_item is None:
                first_item = model[this_iter][0]

            if model.iter_previous(this_iter):

                liststore.move_before(
                    this_iter,
                    model.iter_previous(this_iter),
                )

            else:

                # If the first item won't move up, then successive items will
                #   be moved above this one (which is not what we want)
                break

        # Update the IV
        dir_list = []
        for row in liststore:
            dir_list.append(row[0])

        self.app_obj.set_data_dir_alt_list(dir_list)

        # (De)sensitise the button(s), if required
        if dir_list.index(first_item) == 0:
            button.set_sensitive(False)
        else:
            button.set_sensitive(True)

        if dir_list.index(last_item) == (len(dir_list) - 1):
            button2.set_sensitive(False)
        else:
            button2.set_sensitive(True)


    def on_data_dir_switch_button_clicked(self, button, button2, treeview, \
    entry):

        """Called from callback in self.setup_files_database_tab().

        Changes the Tartube data directory to the one selected in the
        textview.

        Args:

            button (Gtk.Button): The widget clicked

            button2 (Gtk.Button): Another button to be possibly desensitised

            treeview (Gtk.TreeView): A widget in which one file path is
                selected (maybe)

            entry (Gtk.Entry): Another widget to be modified

        """

        selection = treeview.get_selection()
        (model, iter) = selection.get_selected()
        if iter is None:

            # Nothing selected
            return

        else:

            data_dir = model[iter][0]

        # Should not be possible to click the button, when the current
        #   directory is selected, but we'll check anyway
        if data_dir == self.app_obj.data_dir:
            return

        # If no database file exists, prompt the user to create a new one
        db_path = os.path.abspath(
            os.path.join(data_dir, self.app_obj.db_file_name),
        )

        if not os.path.isfile(db_path):

            self.app_obj.dialogue_manager_obj.show_msg_dialogue(
                _(
                    'No database exists at this location:',
                ) + '\n\n' + data_dir + '\n\n' + _(
                    'Do you want to create a new one?',
                ),
                'question',
                'yes-no',
                self,           # Parent window is this window
                {
                    'yes': 'switch_db',
                    'data': [data_dir, self],
                },
            )

        else:

            # Database file already exists, so try to load it now
            self.try_switch_db(data_dir, button2)


    def on_default_avconv_button_clicked(self, button, entry):

        """Called from callback in self.setup_downloader_ffmpeg_tab().

        Sets the path to the avconv binary to the default path.

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Another widget to be modified by this function

        """

        self.app_obj.set_avconv_path(self.app_obj.default_avconv_path)
        entry.set_text(self.app_obj.avconv_path)


    def on_default_ffmpeg_button_clicked(self, button, entry):

        """Called from callback in self.setup_downloader_ffmpeg_tab().

        Sets the path to the ffmpeg binary to the default path.

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Another widget to be modified by this function

        """

        self.app_obj.set_ffmpeg_path(self.app_obj.default_ffmpeg_path)
        entry.set_text(self.app_obj.ffmpeg_path)


    def on_default_ytsc_button_clicked(self, button, entry):

        """Called from callback in self.setup_downloader_ytsc_tab().

        Sets the path to the Youtube Stream Capture binary to the default path.

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Another widget to be modified by this function

        """

        self.app_obj.set_ytsc_path(self.app_obj.default_ytsc_path)
        entry.set_text(self.app_obj.ytsc_path)


    def on_delay_max_spinbutton_changed(self, spinbutton, spinbutton2):

        """Called from callback in self.setup_operations_custom_tab().

        Sets the maximum delay between media data object downloads during a
        custom download.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

            spinbutton2 (Gtk.SpinButton): Another widget to be modified

        """

        value = spinbutton.get_value()

        self.app_obj.set_custom_dl_delay_max(value)
        # Adjust the other spinbutton, so that the minimum value never exceeds
        #   the maximum value
        spinbutton2.set_range(0, value)
        if value < self.app_obj.custom_dl_delay_min:
            spinbutton2.set_value(value)


    def on_delay_min_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_operations_custom_tab().

        Sets the minimum delay between media data object downloads during a
        custom download.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.set_custom_dl_delay_min(spinbutton.get_value())


    def on_delete_shutdown_button_toggled(self, checkbutton, checkbutton2):

        """Called from callback in self.setup_files_temp_folders_tab().

        Enables/disables emptying temporary folders when Tartube shuts down.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            checkbutton2 (Gtk.CheckButton): Another widget to be modified

        """

        if checkbutton.get_active() \
        and not self.app_obj.delete_on_shutdown_flag:
            self.app_obj.set_delete_on_shutdown_flag(True)
            checkbutton2.set_sensitive(False)

        elif not checkbutton.get_active() \
        and self.app_obj.delete_on_shutdown_flag:
            self.app_obj.set_delete_on_shutdown_flag(False)
            checkbutton2.set_sensitive(True)


    def on_delete_watched_button_toggled(self, checkbutton):

        """Called from callback in self.setup_files_video_deletion_tab().

        Enables/disables automatic deletion of videos, but only those that have
        been watched.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.auto_delete_watched_flag:
            self.app_obj.set_auto_delete_watched_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.auto_delete_watched_flag:
            self.app_obj.set_auto_delete_watched_flag(False)


    def on_dialogue_button_toggled(self, radiobutton, mode):

        """Called from callback in self.setup_operations_actions_tab().

        Sets whether a desktop notification, dialogue window or neither should
        be shown to the user at the end of a download/update/refresh/info/tidy
        operation.

        Args:

            radiobutton (Gtk.RadioButton): The widget clicked

            mode (str): The new value for the IV: 'default', 'desktop' or
                'dialogue'

        """

        if radiobutton.get_active():
            self.app_obj.set_operation_dialogue_mode(mode)


    def on_disable_dl_all_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_main_window_tab().

        Enables/disables the 'Download all' buttons in the main window toolbar
        and in the Videos Tab.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.disable_dl_all_flag:
            self.app_obj.set_disable_dl_all_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.disable_dl_all_flag:
            self.app_obj.set_disable_dl_all_flag(False)


    def on_disk_stop_button_toggled(self, checkbutton, spinbutton):

        """Called from a callback in self.setup_files_device_tab().

        Enables/disables halting a download operation when the system is
        running out of disk space.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            spinbutton (Gtk.CheckButton): Another widget to be (de)sensitised

        """

        if checkbutton.get_active() \
        and not self.app_obj.disk_space_stop_flag:
            self.app_obj.set_disk_space_stop_flag(True)
            spinbutton.set_sensitive(True)
        elif not checkbutton.get_active() \
        and self.app_obj.disk_space_stop_flag:
            self.app_obj.set_disk_space_stop_flag(False)
            spinbutton.set_sensitive(False)


    def on_disk_stop_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_files_device_tab().

        Sets the amount of free disk space below which download operations
        will be halted.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.set_disk_space_stop_limit(spinbutton.get_value())


    def on_disk_warn_button_toggled(self, checkbutton, spinbutton):

        """Called from a callback in self.setup_files_device_tab().

        Enables/disables warnings when the system is running out of disk space.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            spinbutton (Gtk.CheckButton): Another widget to be (de)sensitised

        """

        if checkbutton.get_active() \
        and not self.app_obj.disk_space_warn_flag:
            self.app_obj.set_disk_space_warn_flag(True)
            spinbutton.set_sensitive(True)
        elif not checkbutton.get_active() \
        and self.app_obj.disk_space_warn_flag:
            self.app_obj.set_disk_space_warn_flag(False)
            spinbutton.set_sensitive(False)


    def on_disk_warn_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_files_device_tab().

        Sets the amount of free disk space below which a warning will be
        issued.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.set_disk_space_warn_limit(spinbutton.get_value())


    def on_dl_limit_changed(self, entry):

        """Called from callback in self.setup_operations_time_saving_tab().

        Sets the limit at which a download operation will stop downloading a
        channel or playlist.

        Args:

            entry (Gtk.Entry): The widget changed

        """

        text = entry.get_text()
        if text.isdigit() and int(text) >= 0:
            self.app_obj.set_operation_download_limit(int(text))


    def on_drag_name_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_drag_tab().

        Enables/disables transferring the video's name when dragging and
        dropping to an external application.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.drag_video_name_flag:
            self.app_obj.set_drag_video_name_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.drag_video_name_flag:
            self.app_obj.set_drag_video_name_flag(False)


    def on_drag_path_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_drag_tab().

        Enables/disables transferring the video's path when dragging and
        dropping to an external application.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.drag_video_path_flag:
            self.app_obj.set_drag_video_path_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.drag_video_path_flag:
            self.app_obj.set_drag_video_path_flag(False)


    def on_drag_source_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_drag_tab().

        Enables/disables transferring the video's source URL when dragging and
        dropping to an external application.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.drag_video_source_flag:
            self.app_obj.set_drag_video_source_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.drag_video_source_flag:
            self.app_obj.set_drag_video_source_flag(False)


    def on_drag_thumb_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_drag_tab().

        Enables/disables transferring the video thumbnail's path when dragging
        and dropping to an external application.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.drag_thumb_path_flag:
            self.app_obj.set_drag_thumb_path_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.drag_thumb_path_flag:
            self.app_obj.set_drag_thumb_path_flag(False)


    def on_draw_frame_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_videos_tab().

        Enables/disables drawing a frame around videos in the Video Catalogue.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        # (Changing the checkbutton in the Video Catalogue's toolbar sets the
        #   IV)
        self.app_obj.main_win_obj.catalogue_frame_button.set_active(
            checkbutton.get_active(),
        )


    def on_draw_icons_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_videos_tab().

        Enables/disables drawing status icons besides videos in the Video
        Catalogue.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        # (Changing the checkbutton in the Video Catalogue's toolbar sets the
        #   IV)
        self.app_obj.main_win_obj.catalogue_icons_button.set_active(
            checkbutton.get_active(),
        )


    def on_enable_livestreams_button_toggled(self, checkbutton, checkbutton2,
    checkbutton3, spinbutton, spinbutton2):

        """Called from callback in self.setup_operations_livestreams_tab().

        Enables/disables livestream detection.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            checkbutton2, checkbutton3 (Gtk.CheckButton): Other widgets to
                sensitise/desensitise, according to the new value of the flag

            spinbutton, spinbutton2 (Gtk.SpinButton): Another widget to
                sensitise/desensitise, according to the new value of the flag

        """

        if checkbutton.get_active() \
        and not self.app_obj.enable_livestreams_flag:
            self.app_obj.set_enable_livestreams_flag(True)
            checkbutton2.set_sensitive(True)
            checkbutton3.set_sensitive(True)
            spinbutton.set_sensitive(True)
            spinbutton2.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.enable_livestreams_flag:
            self.app_obj.set_enable_livestreams_flag(False)
            checkbutton2.set_active(False)
            checkbutton2.set_sensitive(False)
            checkbutton3.set_active(False)
            checkbutton3.set_sensitive(False)
            spinbutton.set_sensitive(False)
            spinbutton2.set_sensitive(False)


    def on_expand_tree_toggled(self, checkbutton, checkbutton2):

        """Called from callback in self.setup_windows_videos_tab().

        Enables/disables auto-expansion of the Video Index after a folder is
        selected (clicked).

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            checkbutton2 (Gtk.CheckButton): Another widget that must be
                modified

        """

        if checkbutton.get_active() \
        and not self.app_obj.auto_expand_video_index_flag:
            self.app_obj.set_auto_expand_video_index_flag(True)
            checkbutton2.set_sensitive(True)
        elif not checkbutton.get_active() \
        and self.app_obj.auto_expand_video_index_flag:
            self.app_obj.set_auto_expand_video_index_flag(False)
            checkbutton2.set_sensitive(False)


    def on_expand_full_tree_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_videos_tab().

        Enables/disables full auto-expansion of the Video Index after a folder
        is selected (clicked).

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.full_expand_video_index_flag:
            self.app_obj.set_full_expand_video_index_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.full_expand_video_index_flag:
            self.app_obj.set_full_expand_video_index_flag(False)


    def on_extra_livestreams_button_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_livestreams_tab().

        Enables/disables performing more frequent livestream operations when a
        livestream is due to start.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.scheduled_livestream_extra_flag:
            self.app_obj.set_scheduled_livestream_extra_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.scheduled_livestream_extra_flag:
            self.app_obj.set_scheduled_livestream_extra_flag(False)


    def on_ffmpeg_add_button_clicked(self, button, entry):

        """Called from callback in self.setup_options_ffmpeg_list_tab().

        Adds a new ffmpeg_tartube.FFmpegOptionsManager object.

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Widget providiing a name for the new object

        """

        new_obj = self.app_obj.create_ffmpeg_options(entry.get_text())

        # Update the treeview
        self.setup_options_ffmpeg_list_tab_update_treeview()
        # Empty the entry box
        entry.set_text('')

        # All other widgets for creating an options manager object open its
        #   edit window, so we'll do the same here
        FFmpegOptionsEditWin(self.app_obj, new_obj)


    def on_ffmpeg_clone_button_clicked(self, button, treeview):

        """Called from callback in self.setup_options_ffmpeg_list_tab().

        Clones the selected offmpeg_tartube.FFmpegOptionsManager object .

        Args:

            button (Gtk.Button): The widget clicked

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        if path_list:

            # (Multiple selection is not enabled)
            this_iter = model.get_iter(path_list[0])
            if this_iter is not None:

                uid = model[this_iter][0]
                if uid in self.app_obj.ffmpeg_reg_dict:

                    new_obj = self.app_obj.clone_ffmpeg_options(
                        self.app_obj.ffmpeg_reg_dict[uid],
                    )

                    # Open an edit window, so the user can set the cloned
                    #   object's name
                    FFmpegOptionsEditWin(self.app_obj, new_obj)


    def on_ffmpeg_convert_flag_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_downloads_tab().

        Enables/disables conversion of .webp thumbnails into .jpg thumbnails.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ffmpeg_convert_webp_flag:
            self.app_obj.set_ffmpeg_convert_webp_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ffmpeg_convert_webp_flag:
            self.app_obj.set_ffmpeg_convert_webp_flag(False)


    def on_ffmpeg_delete_button_clicked(self, button, treeview):

        """Called from callback in self.setup_options_ffmpeg_list_tab().

        Deletes the selected ffmpeg_tartube.FFmpegOptionsManager object, if
        allowed.

        Args:

            button (Gtk.Button): The widget clicked

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        if not path_list:

            return

        # (Multiple selection is not enabled)
        this_iter = model.get_iter(path_list[0])
        if this_iter is None:

            return

        uid = model[this_iter][0]
        if not uid in self.app_obj.ffmpeg_reg_dict:
            return

        options_obj = self.app_obj.ffmpeg_reg_dict[uid]
        if self.app_obj.ffmpeg_options_obj \
        and self.app_obj.ffmpeg_options_obj == options_obj:

            return self.app_obj.dialogue_manager_obj.show_msg_dialogue(
                _('The current options manager cannot be deleted'),
                'error',
                'ok',
                self,           # Parent window is this window
            )

        # Prompt for confirmation
        self.app_obj.dialogue_manager_obj.show_msg_dialogue(
            _('Are you sure you want to delete this options manager?'),
            'question',
            'yes-no',
            self,           # Parent window is this window
            {
                'yes': 'delete_ffmpeg_options',
                # Specified options
                'data': options_obj,
            },
        )


    def on_ffmpeg_edit_button_clicked(self, button, treeview):

        """Called from callback in self.setup_options_ffmpeg_list_tab().

        Opens an edit window for the selected
        ffmpeg_tartube.FFmpegOptionsManager.

        Args:

            button (Gtk.Button): The widget clicked

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        if path_list:

            # (Multiple selection is not enabled)
            this_iter = model.get_iter(path_list[0])
            if this_iter is not None:

                uid = model[this_iter][0]
                if uid in self.app_obj.ffmpeg_reg_dict:

                    FFmpegOptionsEditWin(
                        self.app_obj,
                        self.app_obj.ffmpeg_reg_dict[uid],
                    )


    def on_ffmpeg_export_button_clicked(self, button, treeview):

        """Called from callback in self.setup_options_ffmpeg_list_tab().

        Exports the selected offmpeg_tartube.FFmpegOptionsManager object to a
        JSON file.

        Args:

            button (Gtk.Button): The widget clicked

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        if path_list:

            # (Multiple selection is not enabled)
            this_iter = model.get_iter(path_list[0])
            if this_iter is not None:

                uid = model[this_iter][0]
                if uid in self.app_obj.ffmpeg_reg_dict:

                    self.app_obj.export_ffmpeg_options(
                        self.app_obj.ffmpeg_reg_dict[uid],
                    )


    def on_ffmpeg_import_button_clicked(self, button, entry):

        """Called from callback in self.setup_options_ffmpeg_list_tab().

        Imports a JSON file and creates a new
        ffmpeg_tartube.FFmpegOptionsManager for it.

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Widget providiing a name for the new object.
                If the entry is empty, then the name specified by the JSON file
                itself is used

        """

        self.app_obj.import_ffmpeg_options(entry.get_text())

        # Update the treeview
        self.setup_options_ffmpeg_list_tab_update_treeview()
        # Empty the entry box
        entry.set_text('')


    def on_ffmpeg_use_button_clicked(self, button, treeview):

        """Called from callback in self.setup_options_ffmpeg_list_tab().

        Sets the selected ffmpeg_tartube.FFmpegOptionsManager object as the
        current one.

        Args:

            button (Gtk.Button): The widget clicked

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        if path_list:

            # (Multiple selection is not enabled)
            this_iter = model.get_iter(path_list[0])
            if this_iter is not None:

                uid = model[this_iter][0]
                if uid in self.app_obj.ffmpeg_reg_dict:

                    self.app_obj.set_ffmpeg_options_obj(
                        self.app_obj.ffmpeg_reg_dict[uid],
                    )

        # Update the treeview
        self.setup_options_ffmpeg_list_tab_update_treeview()


    def on_gtk_emulate_button_toggled(self, checkbutton):

        """Called from callback in self.setup_general_stability_tab().

        Enables/disables emulation of a broken Gtk library.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.gtk_emulate_broken_flag:
            self.app_obj.set_gtk_emulate_broken_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.gtk_emulate_broken_flag:
            self.app_obj.set_gtk_emulate_broken_flag(False)


    def on_hide_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_main_window_tab().

        Enables/disables hiding finishe media data objects in the Progress
        List.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        main_win_obj = self.app_obj.main_win_obj
        other_flag = main_win_obj.hide_finished_checkbutton.get_active()

        if (checkbutton.get_active() and not other_flag):
            main_win_obj.hide_finished_checkbutton.set_active(True)
        elif (not checkbutton.get_active() and other_flag):
            main_win_obj.hide_finished_checkbutton.set_active(False)


    def on_hide_toolbar_button_toggled(self, checkbutton, checkbutton2):

        """Called from callback in self.setup_windows_main_window_tab().

        Enables/disables hiding the main window's main toolbar.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            checkbutton2 (Gtk.CheckButton): Another checkbutton to modify

        """

        if checkbutton.get_active() \
        and not self.app_obj.toolbar_hide_flag:
            self.app_obj.set_toolbar_hide_flag(True)
            checkbutton2.set_sensitive(False)

        elif not checkbutton.get_active() \
        and self.app_obj.toolbar_hide_flag:
            self.app_obj.set_toolbar_hide_flag(False)

        self.app_obj.dialogue_manager_obj.show_msg_dialogue(
            _('The new setting will be applied when Tartube restarts'),
            'info',
            'ok',
            self,           # Parent window is this window
        )


    def on_http_404_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_errors_warnings_tab().

        Enables/disables ignoring of HTTP 404 error messages.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ignore_http_404_error_flag:
            self.app_obj.set_ignore_http_404_error_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ignore_http_404_error_flag:
            self.app_obj.set_ignore_http_404_error_flag(False)


    def on_invidious_mirror_changed(self, entry):

        """Called from callback in self.setup_operations_prefs_tab().

        Sets the Invidious mirror to use.

        Args:

            entry (Gtk.Entry): The widget changed

        """

        self.app_obj.set_custom_invidious_mirror(entry.get_text())


    def on_json_button_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_downloads_tab().

        Enables/disables applying a 60-second timeout when fetching a video's
        JSON data.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.apply_json_timeout_flag:
            self.app_obj.set_apply_json_timeout_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.apply_json_timeout_flag:
            self.app_obj.set_apply_json_timeout_flag(False)


    def on_keep_open_button_toggled(self, checkbutton, checkbutton2):

        """Called from a callback in self.setup_windows_dialogues_tab().

        Enables/disables keeping the dialogue window open when adding channels/
        playlists/folders.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            checkbutton2 (Gtk.CheckButton): Another checkbutton to sensitise/
                desensitise, according to the new value of the flag

        """

        if checkbutton.get_active() \
        and not self.app_obj.dialogue_keep_open_flag:
            self.app_obj.set_dialogue_keep_open_flag(True)
            checkbutton2.set_sensitive(False)

        elif not checkbutton.get_active() \
        and self.app_obj.dialogue_keep_open_flag:
            self.app_obj.set_dialogue_keep_open_flag(False)
            checkbutton2.set_sensitive(True)


    def on_limit_button_toggled(self, checkbutton, entry, entry2):

        """Called from callback in self.setup_operations_time_saving_tab().

        Sets the limit at which a download operation will stop downloading a
        channel or playlist.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            entry, entry2 (Gtk.Entry): The entry boxes which must be
                sensitised/desensitised, according to the new setting of the IV

        """

        if checkbutton.get_active() and not self.app_obj.operation_limit_flag:
            self.app_obj.set_operation_limit_flag(True)
            entry.set_sensitive(True)
            entry2.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.operation_limit_flag:
            self.app_obj.set_operation_limit_flag(False)
            entry.set_sensitive(False)
            entry2.set_sensitive(False)


    def on_livestream_auto_alarm_button_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_actions_tab().

        Enables/disables sounding an alarm when a livestream starts.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.livestream_auto_alarm_flag:
            self.app_obj.set_livestream_auto_alarm_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.livestream_auto_alarm_flag:
            self.app_obj.set_livestream_auto_alarm_flag(False)


    def on_livestream_auto_dl_start_button_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_actions_tab().

        Enables/disables downloading a livestream as soon as it starts.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.livestream_auto_dl_start_flag:
            self.app_obj.set_livestream_auto_dl_start_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.livestream_auto_dl_start_flag:
            self.app_obj.set_livestream_auto_dl_start_flag(False)


    def on_livestream_auto_dl_stop_button_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_actions_tab().

        Enables/disables downloading a livestream as soon as it stops.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.livestream_auto_dl_stop_flag:
            self.app_obj.set_livestream_auto_dl_stop_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.livestream_auto_dl_stop_flag:
            self.app_obj.set_livestream_auto_dl_stop_flag(False)


    def on_livestream_auto_notify_button_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_actions_tab().

        Enables/disables desktop notifications when a livestream starts.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.livestream_auto_notify_flag:
            self.app_obj.set_livestream_auto_notify_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.livestream_auto_notify_flag:
            self.app_obj.set_livestream_auto_notify_flag(False)


    def on_livestream_auto_open_button_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_actions_tab().

        Enables/disables opening a livestream in the system's web browser when
        it starts.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.livestream_auto_open_flag:
            self.app_obj.set_livestream_auto_open_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.livestream_auto_open_flag:
            self.app_obj.set_livestream_auto_open_flag(False)


    def on_livestream_colour_button_toggled(self, checkbutton, checkbutton2):

        """Called from callback in self.setup_windows_videos_tab().

        Enables/disables coloured backgrounds for livestream videos in the
        Video Catalogue.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            checkbutton2 (Gtk.CheckButton): Another widget to modify

        """

        if checkbutton.get_active() \
        and not self.app_obj.livestream_use_colour_flag:
            self.app_obj.set_livestream_use_colour_flag(True)
            checkbutton2.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.livestream_use_colour_flag:
            self.app_obj.set_livestream_use_colour_flag(False)
            checkbutton2.set_sensitive(False)

        # Redraw the Video Catalogue, at its current page, to update the
        #   backgrounds
        main_win_obj = self.app_obj.main_win_obj
        main_win_obj.video_catalogue_redraw_all(
            main_win_obj.video_index_current,
            main_win_obj.catalogue_toolbar_current_page,
        )


    def on_livestream_max_days_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_operations_livestreams_tab().

        Sets the time (in days) at which Tartube stops looking for livestreams.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.set_livestream_max_days(
            spinbutton.get_value(),
        )


    def on_livestream_simple_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_videos_tab().

        Enables/disables using the same background colour for livestream and
        debut videos.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.livestream_simple_colour_flag:
            self.app_obj.set_livestream_simple_colour_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.livestream_simple_colour_flag:
            self.app_obj.set_livestream_simple_colour_flag(False)

        # Redraw the Video Catalogue, at its current page, to update the
        #   backgrounds
        main_win_obj = self.app_obj.main_win_obj
        main_win_obj.video_catalogue_redraw_all(
            main_win_obj.video_index_current,
            main_win_obj.catalogue_toolbar_current_page,
        )


    def on_locale_combo_changed(self, combo, grid):

        """Called from a callback in self.setup_general_language_tab().

        Sets the custom locale for Tartube.

        Args:

            combo (Gtk.ComboBox): The widget clicked

            grid (Gtk.Grid): The grid on which this tab's widgets are
                arranged

        """

        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        language = model[tree_iter][1]

        for key in formats.LOCALE_DICT:
            if formats.LOCALE_DICT[key] == language:

                self.app_obj.set_custom_locale(key)

                # Add some more widgets to tell the user to restart Tartube.
                #   As the user might not know the language, show an icon as
                #   well as some text
                # Use an extra grid to avoid messing up the layout of widgets
                #   above
                grid2 = Gtk.Grid()
                grid.attach(grid2, 0, 2, 2, 1)
                grid2.set_border_width(self.spacing_size * 2)
                grid2.set_column_spacing(self.spacing_size)
                grid2.set_row_spacing(self.spacing_size)

                frame = self.add_image(grid2,
                    self.app_obj.main_win_obj.icon_dict['warning_large'],
                    0, 2, 1, 1,
                )
                # (The frame looks cramped without this. The icon itself is
                #   32x32)
                frame.set_size_request(
                    32 + (self.spacing_size * 2),
                    32 + (self.spacing_size * 2),
                )

                self.add_label(grid2,
                    '<i>' + _(
                        'The new setting will be applied when Tartube' \
                        + ' restarts',
                    ) + '</i>',
                    1, 2, 1, 1,
                )

                self.show_all()


    def on_match_button_toggled(self, radiobutton):

        """Called from callback in self.setup_files_video_deletion_tab().

        Updates IVs in the main application and sensities/desensities widgets.

        Args:

            radiobutton (Gtk.RadioButton): The widget clicked

        """

        default_val = self.app_obj.match_default_chars

        if radiobutton.get_active():

            if radiobutton == self.radiobutton:
                self.app_obj.set_match_method('exact_match')
                # (Changing the contents of the widgets automatically updates
                #   mainapp.TartubeApp IVs)
                self.spinbutton.set_value(default_val)
                self.spinbutton.set_sensitive(False)
                self.spinbutton2.set_value(default_val)
                self.spinbutton2.set_sensitive(False)

            elif radiobutton == self.radiobutton2:
                self.app_obj.set_match_method('match_first')
                self.spinbutton.set_sensitive(True)
                self.spinbutton2.set_value(default_val)
                self.spinbutton2.set_sensitive(False)

            else:
                self.app_obj.set_match_method('ignore_last')
                self.spinbutton.set_value(default_val)
                self.spinbutton.set_sensitive(False)
                self.spinbutton2.set_sensitive(True)


    def on_match_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_files_video_deletion_tab().

        Updates IVs in the main application and sensities/desensities widgets.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        if spinbutton == self.spinbutton:
            self.app_obj.set_match_first_chars(spinbutton.get_value())
        else:
            self.app_obj.set_match_ignore_chars(spinbutton.get_value())


    def on_merge_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_errors_warnings_tab().

        Enables/disables ignoring of 'Requested formats are incompatible for
        merge and will be merged into mkv' warning messages.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ignore_merge_warning_flag:
            self.app_obj.set_ignore_merge_warning_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ignore_merge_warning_flag:
            self.app_obj.set_ignore_merge_warning_flag(False)


    def on_missing_format_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_errors_warnings_tab().

        Enables/disables ignoring of missing format error messages.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ignore_missing_format_error_flag:
            self.app_obj.set_ignore_missing_format_error_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ignore_missing_format_error_flag:
            self.app_obj.set_ignore_missing_format_error_flag(False)


    def on_missing_time_button_toggled(self, checkbutton, spinbutton):

        """Called from callback in self.setup_operations_prefs_tab().

        Enables/disables a time limit when tracking videos missing from a
        channel/playlist.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            spinbutton (Gtk.SpinButton): Another widget to modify

        """

        if checkbutton.get_active() \
        and not self.app_obj.track_missing_time_flag:

            self.app_obj.set_track_missing_time_flag(True)
            spinbutton.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.track_missing_time_flag:
            self.app_obj.set_track_missing_time_flag(False)
            spinbutton.set_sensitive(False)


    def on_missing_time_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_operations_prefs_tab().

        Sets a time limit when tracking videos missing from a channel/playlist.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.set_track_missing_time_days(
            spinbutton.get_value(),
        )


    def on_missing_videos_button_toggled(self, checkbutton, checkbutton2, \
    spinbutton):

        """Called from callback in self.setup_operations_prefs_tab().

        Enables/disables tracking videos missing from a channel/playlist.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            checkbutton2 (Gtk.CheckButton): Another widget to modify

            spinbutton (Gtk.SpinButton): Another widget to modify

        """

        if checkbutton.get_active() \
        and not self.app_obj.track_missing_videos_flag:

            self.app_obj.set_track_missing_videos_flag(True)
            checkbutton2.set_sensitive(True)
            if self.app_obj.track_missing_time_flag:
                spinbutton.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.track_missing_videos_flag:
            checkbutton2.set_active(False)
            self.app_obj.set_track_missing_videos_flag(False)
            checkbutton2.set_sensitive(False)
            spinbutton.set_sensitive(False)


    def on_moviepy_button_toggled(self, checkbutton):

        """Called from callback in self.setup_general_modules_tab().

        Enables/disables use of the moviepy.editor module.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.use_module_moviepy_flag:
            self.app_obj.set_use_module_moviepy_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.use_module_moviepy_flag:
            self.app_obj.set_use_module_moviepy_flag(False)


    def on_moviepy_timeout_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_general_modules_tab().

        Sets the timeout to apply to threads using the moviepy module.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.set_refresh_moviepy_timeout(
            spinbutton.get_value(),
        )


    def on_no_annotations_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_errors_warnings_tab().

        Enables/disables ignoring of the 'no annotations' warning messages.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ignore_no_annotations_flag:
            self.app_obj.set_ignore_no_annotations_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ignore_no_annotations_flag:
            self.app_obj.set_ignore_no_annotations_flag(False)


    def on_no_subtitles_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_errors_warnings_tab().

        Enables/disables ignoring of the 'no subtitles' warning messages.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ignore_no_subtitles_flag:
            self.app_obj.set_ignore_no_subtitles_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ignore_no_subtitles_flag:
            self.app_obj.set_ignore_no_subtitles_flag(False)


    def on_open_desktop_button_toggled(self, checkbutton):

        """Called from callback in self.setup_files_temp_folders_tab().

        Enables/disables opening temporary folders on the desktop when Tartube
        shuts down.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.open_temp_on_desktop_flag:
            self.app_obj.set_open_temp_on_desktop_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.open_temp_on_desktop_flag:
            self.app_obj.set_open_temp_on_desktop_flag(False)


    def on_operation_error_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_errors_warnings_tab().

        Enables/disables opeartion errors in the 'Errors/Warnings' tab.
        Toggling the corresponding Gtk.CheckButton in the Errors/Warnings tab
        sets the IV (and makes sure the two checkbuttons have the same status).

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        main_win_obj = self.app_obj.main_win_obj
        other_flag = main_win_obj.show_operation_error_checkbutton.get_active()

        main_win_obj = self.app_obj.main_win_obj
        if (checkbutton.get_active() and not other_flag):
            main_win_obj.show_operation_error_checkbutton.set_active(True)
        elif (not checkbutton.get_active() and other_flag):
            main_win_obj.show_operation_error_checkbutton.set_active(False)


    def on_operation_sim_button_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_downloads_tab().

        Enables/disables ignoring already-checked videos whose parent is a
        media.Folder, if the videos have already been checked.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.operation_sim_shortcut_flag:
            self.app_obj.set_operation_sim_shortcut_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.operation_sim_shortcut_flag:
            self.app_obj.set_operation_sim_shortcut_flag(False)


    def on_operation_warning_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_errors_warnings_tab().

        Enables/disables opeartion warnings in the 'Errors/Warnings' tab.
        Toggling the corresponding Gtk.CheckButton in the Errors/Warnings tab
        sets the IV (and makes sure the two checkbuttons have the same status).

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        main_win_obj = self.app_obj.main_win_obj
        other_flag \
        = main_win_obj.show_operation_warning_checkbutton.get_active()

        if (checkbutton.get_active() and not other_flag):
            main_win_obj.show_operation_warning_checkbutton.set_active(True)
        elif (not checkbutton.get_active() and other_flag):
            main_win_obj.show_operation_warning_checkbutton.set_active(False)


    def on_options_add_button_clicked(self, button, entry):

        """Called from callback in self.setup_options_dl_list_tab().

        Adds a new options.OptionsManager object.

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Widget providiing a name for the new object

        """

        new_obj = self.app_obj.create_download_options(entry.get_text())

        # If required, clone download options from the General Options Manager
        #   into the new object
        if self.app_obj.auto_clone_options_flag:
            new_obj.clone_options(self.app_obj.general_options_obj)

        # On the assumption that objects created here will be applied (mostly)
        #   in the Classic Mode tab, disable downloading the description,
        #   annotations (etc) files
        new_obj.set_classic_mode_options()

        # Update the treeview
        self.setup_options_dl_list_tab_update_treeview()
        # Empty the entry box
        entry.set_text('')

        # All other widgets for creating an options manager object open its
        #   edit window, so we'll do the same here
        OptionsEditWin(self.app_obj, new_obj)


    def on_options_clone_button_clicked(self, button, treeview):

        """Called from callback in self.setup_options_dl_list_tab().

        Clones the selected options.OptionsManager object.

        Args:

            button (Gtk.Button): The widget clicked

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        if path_list:

            # (Multiple selection is not enabled)
            this_iter = model.get_iter(path_list[0])
            if this_iter is not None:

                uid = model[this_iter][0]
                if uid in self.app_obj.options_reg_dict:

                    new_obj = self.app_obj.clone_download_options(
                        self.app_obj.options_reg_dict[uid],
                    )

                    # Open an edit window, so the user can set the cloned
                    #   object's name
                    OptionsEditWin(self.app_obj, new_obj)


    def on_options_delete_button_clicked(self, button, treeview):

        """Called from callback in self.setup_options_dl_list_tab().

        Deletes the selected options.OptionsManager object, if allowed.

        Args:

            button (Gtk.Button): The widget clicked

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        if not path_list:

            return

        # (Multiple selection is not enabled)
        this_iter = model.get_iter(path_list[0])
        if this_iter is None:

            return

        uid = model[this_iter][0]
        if not uid in self.app_obj.options_reg_dict:
            return

        options_obj = self.app_obj.options_reg_dict[uid]
        if self.app_obj.general_options_obj \
        and self.app_obj.general_options_obj == options_obj:

            return self.app_obj.dialogue_manager_obj.show_msg_dialogue(
                _('The default options manager cannot be deleted'),
                'error',
                'ok',
                self,           # Parent window is this window
            )

        # Prompt for confirmation
        self.app_obj.dialogue_manager_obj.show_msg_dialogue(
            _('Are you sure you want to delete this options manager?'),
            'question',
            'yes-no',
            self,           # Parent window is this window
            {
                'yes': 'delete_download_options',
                # Specified options
                'data': options_obj,
            },
        )


    def on_options_edit_button_clicked(self, button, treeview):

        """Called from callback in self.setup_options_dl_list_tab().

        Opens an edit window for the selected options.OptionsManager object.

        Args:

            button (Gtk.Button): The widget clicked

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        if path_list:

            # (Multiple selection is not enabled)
            this_iter = model.get_iter(path_list[0])
            if this_iter is not None:

                uid = model[this_iter][0]
                if uid in self.app_obj.options_reg_dict:

                    OptionsEditWin(
                        self.app_obj,
                        self.app_obj.options_reg_dict[uid],
                    )


    def on_options_export_button_clicked(self, button, treeview):

        """Called from callback in self.setup_options_dl_list_tab().

        Exports the selected options.OptionsManager object to a JSON file.

        Args:

            button (Gtk.Button): The widget clicked

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        if path_list:

            # (Multiple selection is not enabled)
            this_iter = model.get_iter(path_list[0])
            if this_iter is not None:

                uid = model[this_iter][0]
                if uid in self.app_obj.options_reg_dict:

                    self.app_obj.export_download_options(
                        self.app_obj.options_reg_dict[uid],
                    )


    def on_options_import_button_clicked(self, button, entry):

        """Called from callback in self.setup_options_dl_list_tab().

        Imports a JSON file and creates a new options.OptionsManager for it.

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Widget providiing a name for the new object.
                If the entry is empty, then the name specified by the JSON file
                itself is used

        """

        self.app_obj.import_download_options(entry.get_text())

        # Update the treeview
        self.setup_options_dl_list_tab_update_treeview()
        # Empty the entry box
        entry.set_text('')


    def on_options_use_classic_button_clicked(self, button, treeview):

        """Called from callback in self.setup_options_dl_list_tab().

        Applies the selected options.OptionsManager object to the Classic Mode
        tab.

        Args:

            button (Gtk.Button): The widget clicked

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        if path_list:

            # (Multiple selection is not enabled)
            this_iter = model.get_iter(path_list[0])
            if this_iter is not None:

                uid = model[this_iter][0]
                if uid in self.app_obj.options_reg_dict:

                    options_obj = self.app_obj.options_reg_dict[uid]

                    # If this is already the options manager for the Classic
                    #   Mode tab, then remove it (but don't delete the object
                    #   itself)
                    if self.app_obj.classic_options_obj \
                    and self.app_obj.classic_options_obj == options_obj:

                        self.app_obj.disapply_classic_download_options()

                    else:

                        self.app_obj.apply_classic_download_options(
                            self.app_obj.options_reg_dict[uid],
                        )

        # Update the treeview
        self.setup_options_dl_list_tab_update_treeview()


    def on_output_empty_button_toggled(self, checkbutton):

        """Called from a callback in self.setup_output_outputtab_tab().

        Enables/disables emptying pages in the Output Tab at the start of every
        operation.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ytdl_output_start_empty_flag:
            self.app_obj.set_ytdl_output_start_empty_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ytdl_output_start_empty_flag:
            self.app_obj.set_ytdl_output_start_empty_flag(False)


    def on_output_json_button_toggled(self, checkbutton):

        """Called from a callback in self.setup_output_outputtab_tab().

        Enables/disables writing output from youtube-dl's STDOUT to the Output
        Tab.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ytdl_output_ignore_json_flag:
            self.app_obj.set_ytdl_output_ignore_json_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ytdl_output_ignore_json_flag:
            self.app_obj.set_ytdl_output_ignore_json_flag(False)


    def on_output_progress_button_toggled(self, checkbutton):

        """Called from a callback in self.setup_output_outputtab_tab().

        Enables/disables writing output from youtube-dl's STDOUT to the Output
        Tab.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ytdl_output_ignore_progress_flag:
            self.app_obj.set_ytdl_output_ignore_progress_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ytdl_output_ignore_progress_flag:
            self.app_obj.set_ytdl_output_ignore_progress_flag(False)


    def on_output_stderr_button_toggled(self, checkbutton):

        """Called from a callback in self.setup_output_outputtab_tab().

        Enables/disables writing output from youtube-dl's STDERR to the Output
        Tab.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ytdl_output_stderr_flag:
            self.app_obj.set_ytdl_output_stderr_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ytdl_output_stderr_flag:
            self.app_obj.set_ytdl_output_stderr_flag(False)


    def on_output_stdout_button_toggled(self, checkbutton, checkbutton2, \
    checkbutton3):

        """Called from a callback in self.setup_output_outputtab_tab().

        Enables/disables writing output from youtube-dl's STDOUT to the Output
        Tab.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            checkbutton2, checkbutton3 (Gtk.CheckButton): Additional
                checkbuttons to sensitise/desensitise, according to the new
                value of the flag

        """

        if checkbutton.get_active() \
        and not self.app_obj.ytdl_output_stdout_flag:
            self.app_obj.set_ytdl_output_stdout_flag(True)
            checkbutton2.set_sensitive(True)
            checkbutton3.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.ytdl_output_stdout_flag:
            self.app_obj.set_ytdl_output_stdout_flag(False)
            checkbutton2.set_sensitive(False)
            checkbutton3.set_sensitive(False)


    def on_output_summary_button_toggled(self, checkbutton):

        """Called from a callback in self.setup_output_outputtab_tab().

        Enables/disables displaying a summary page in the Output Tab.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ytdl_output_show_summary_flag:
            self.app_obj.set_ytdl_output_show_summary_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ytdl_output_show_summary_flag:
            self.app_obj.set_ytdl_output_show_summary_flag(False)


    def on_output_size_button_toggled(self, checkbutton):

        """Called from callback in self.setup_output_outputtab_tab().

        Enables/disables applying a maximum size to the Output Tab pages.
        Toggling the corresponding Gtk.CheckButton in the Output Tab sets the
        IV (and makes sure the two checkbuttons have the same status).

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        other_flag \
        = self.app_obj.main_win_obj.output_size_checkbutton.get_active()

        if (checkbutton.get_active() and not other_flag):
            self.app_obj.main_win_obj.output_size_checkbutton.set_active(True)
        elif (not checkbutton.get_active() and other_flag):
            self.app_obj.main_win_obj.output_size_checkbutton.set_active(False)


    def on_output_size_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_output_outputtab_tab().

        Sets the maximum size of the Output Tab pages. Setting the value of the
        corresponding Gtk.SpinButton in the Output Tab sets the IV (and
        makes sure the two spinbuttons have the same value).

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.main_win_obj.output_size_spinbutton.set_value(
            spinbutton.get_value(),
        )


    def on_output_system_button_toggled(self, checkbutton):

        """Called from a callback in self.setup_output_outputtab_tab().

        Enables/disables writing youtube-dl system commands to the Output Tab.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ytdl_output_system_cmd_flag:
            self.app_obj.set_ytdl_output_system_cmd_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ytdl_output_system_cmd_flag:
            self.app_obj.set_ytdl_output_system_cmd_flag(False)


    def on_payment_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_websites_tab().

        Enables/disables ignoring of payment required error messages.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ignore_yt_payment_flag:
            self.app_obj.set_ignore_yt_payment_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ignore_yt_payment_flag:
            self.app_obj.set_ignore_yt_payment_flag(False)


    def on_pretty_date_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_videos_tab().

        Enables/disables 'today' and 'yesterday' rather than a numerical date
        in the Videos Tab.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.show_pretty_dates_flag:
            self.app_obj.set_show_pretty_dates_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.show_pretty_dates_flag:
            self.app_obj.set_show_pretty_dates_flag(False)


    def on_proxy_textview_changed(self, textbuffer):

        """Called from callback in self.setup_operations_proxies_tab().

        Sets the list of proxies.

        Args:

            textbuffer (Gtk.TextBuffer): The buffer belonging to the textview
                whose contents has been modified

        """

        text = textbuffer.get_text(
            textbuffer.get_start_iter(),
            textbuffer.get_end_iter(),
            # Don't include hidden characters
            False,
        )

        # Filter out empty lines
        line_list = text.split("\n")
        mod_list = []
        for line in line_list:
            if re.search(r'\S', line):
                mod_list.append(line)

        # Apply the changes
        self.app_obj.set_dl_proxy_list(mod_list)


    def on_recalculate_stats_button_clicked(self, button, entry, entry2,
    entry3, entry4, entry5, entry6):

        """Called from callback in self.setup_files_statistics_tab().

        Recalculates the number of media data objects in the Tartube database,
        and updates the entry boxes.

        Args:

            button (Gtk.Button): The widget clicked

            entry, entry2, entry3, entry4, entry5, entry6 (Gtk.Entry): The
                entry boxes to update

        """

        self.setup_files_statistics_tab_recalculate(
            entry,
            entry2,
            entry3,
            entry4,
            entry5,
            entry6,
        )


    def on_refresh_verbose_button_toggled(self, checkbutton):

        """Called from a callback in self.setup_output_outputtab_tab().

        Enables/disables displaying non-matching videos in the Output Tab
        during a refresh operation.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.refresh_output_verbose_flag:
            self.app_obj.set_refresh_output_verbose_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.refresh_output_verbose_flag:
            self.app_obj.set_refresh_output_verbose_flag(False)


    def on_refresh_videos_button_toggled(self, checkbutton, checkbutton2):

        """Called from a callback in self.setup_output_outputtab_tab().

        Enables/disables displaying matching videos in the Output Tab during a
        refresh operation.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            checkbutton2 (Gtk.CheckButton): A different checkbutton to
                sensitise/desensitise, according to the new value of the flag

        """

        if checkbutton.get_active() \
        and not self.app_obj.refresh_output_videos_flag:
            self.app_obj.set_refresh_output_videos_flag(True)
            checkbutton2.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.refresh_output_videos_flag:
            self.app_obj.set_refresh_output_videos_flag(False)
            checkbutton2.set_sensitive(False)


    def on_regex_button_toggled(self, radiobutton, flag):

        """Called from callback in self.setup_windows_websites_tab().

        Sets whether mainapp.TartubeApp.ignore_custom_msg_list contains
        ordinary strings or regexes.

        Args:

            radiobutton (Gtk.RadioButton): The widget clicked

            flag (bool): False for ordinary strings, True for regexes

        """

        if radiobutton.get_active():
            self.app_obj.set_ignore_custom_regex_flag(flag)


    def on_remember_size_button_toggled(self, checkbutton, checkbutton2):

        """Called from callback in self.setup_windows_main_window_tab().

        Enables/disables remembering the size of the main window.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            checkbutton2 (Gtk.CheckButton): Another widget to be modified

        """

        if checkbutton.get_active() \
        and not self.app_obj.main_win_save_size_flag:
            self.app_obj.set_main_win_save_size_flag(True)
            checkbutton2.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.main_win_save_size_flag:
            self.app_obj.set_main_win_save_size_flag(False)
            checkbutton2.set_sensitive(False)
            checkbutton2.set_active(False)


    def on_remember_slider_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_main_window_tab().

        Enables/disables remembering the position of sliders in the main
        window.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.main_win_save_slider_flag:
            self.app_obj.set_main_win_save_slider_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.main_win_save_slider_flag:
            self.app_obj.set_main_win_save_slider_flag(False)


    def on_remove_duplicate_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_main_window_tab().

        Enables/disables removeing duplicate URLs from the Classic Mode Tab,
        after the 'Add URLs' button is clicked.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.classic_duplicate_remove_flag:
            self.app_obj.set_classic_duplicate_remove_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.classic_duplicate_remove_flag:
            self.app_obj.set_classic_duplicate_remove_flag(False)


    def on_reset_avconv_button_clicked(self, button, entry):

        """Called from callback in self.setup_ytdl_avconv_tab().

        Resets the path to the avconv binary.

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Another widget to be modified by this function

        """

        self.app_obj.set_avconv_path(None)
        entry.set_text('')


    def on_reset_ffmpeg_button_clicked(self, button, entry):

        """Called from callback in self.setup_downloader_ffmpeg_tab().

        Resets the path to the FFmpeg binary.

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Another widget to be modified by this function

        """

        self.app_obj.set_ffmpeg_path(None)
        entry.set_text('')


    def on_reset_ytsc_button_clicked(self, button, entry):

        """Called from callback in self.setup_downloader_ytsc_tab().

        Resets the path to the Youtube Stream Capture binary.

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Another widget to be modified by this function

        """

        self.app_obj.set_ytsc_path(None)
        entry.set_text('')


    def on_reverse_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_main_window_tab().

        Enables/disables display of videos in the Results List in the reverse
        order.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        main_win_obj = self.app_obj.main_win_obj
        other_flag = main_win_obj.reverse_results_checkbutton.get_active()

        if (checkbutton.get_active() and not other_flag):
            main_win_obj.reverse_results_checkbutton.set_active(True)
        elif (not checkbutton.get_active() and other_flag):
            main_win_obj.reverse_results_checkbutton.set_active(False)


    def on_save_button_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_downloads_tab().

        Enables/disables automatic saving of files at the end of a download/
        update/refresh/info/tidy operation.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() and not self.app_obj.operation_save_flag:
            self.app_obj.set_operation_save_flag(True)
        elif not checkbutton.get_active() and self.app_obj.operation_save_flag:
            self.app_obj.set_operation_save_flag(False)


    def on_scheduled_add_button_clicked(self, button, entry):

        """Called from callback in self.setup_scheduling_start_tab().

        Adds a new media.Scheduled object, adds it to the treeview, and opens
        an edit window for it.

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): An entry containing the new object's name

        """

        # Check the specified name is valid
        name = entry.get_text()
        if name == '':
            return

        for this_obj in self.app_obj.scheduled_list:
            if this_obj.name == name:

                self.app_obj.dialogue_manager_obj.show_msg_dialogue(
                    _('There is already a scheduled download with that name'),
                    'error',
                    'ok',
                    self,           # Parent window is this window
                )

                return

        # Create a new scheduled download object
        new_obj = media.Scheduled(name, 'real', 'scheduled')
        self.app_obj.add_scheduled_list(new_obj)

        # Add it to the treeview
        self.setup_scheduling_start_tab_add_row(new_obj)
        # Open an edit window for it
        ScheduledEditWin(self.app_obj, new_obj)
        # Reset the entry
        entry.set_text('')


    def on_scheduled_delete_button_clicked(self, button, treeview):

        """Called from callback in self.setup_scheduling_start_tab().

        Prompts the user, and then deletes the selected media.Scheduled object.

        Args:

            button (Gtk.Button): The widget clicked

            treeview (Gtk.TreeView): The treeview with a selected line

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        for path in path_list:

            this_iter = model.get_iter(path)
            name = model[this_iter][0]

            for scheduled_obj in self.app_obj.scheduled_list:
                if scheduled_obj.name == name:

                    # Prompt the user
                    self.app_obj.dialogue_manager_obj.show_msg_dialogue(
                        _(
                        'Are you sure you want to delete this scheduled' \
                        + ' download?',
                        ),
                        'question',
                        'yes-no',
                        self,           # Parent window is this window
                        {
                            'yes': 'del_scheduled_list',
                            'data': [scheduled_obj, self],
                        },
                    )


    def on_scheduled_edit_button_clicked(self, button, treeview):

        """Called from callback in self.setup_scheduling_start_tab().

        Opens an edit window for the selected media.Scheduled object.

        Args:

            button (Gtk.Button): The widget clicked

            treeview (Gtk.TreeView): The treeview with a selected line

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        for path in path_list:

            this_iter = model.get_iter(path)
            name = model[this_iter][0]

            for scheduled_obj in self.app_obj.scheduled_list:
                if scheduled_obj.name == name:
                    ScheduledEditWin(self.app_obj, scheduled_obj)
                    break


    def on_scheduled_move_down_button_clicked(self, button, treeview):

        """Called from callback in self.setup_scheduling_start_tab().

        Moves the selected media.Scheduled object down one position in the
        list.

        Args:

            button (Gtk.Button): The widget clicked

            treeview (Gtk.TreeView): The treeview with a selected line

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        for path in path_list:

            this_iter = model.get_iter(path)
            if model.iter_next(this_iter):

                name = model[this_iter][0]
                self.app_obj.move_scheduled_list(name, True)

                model.move_after(
                    this_iter,
                    model.iter_next(this_iter),
                )


    def on_scheduled_move_up_button_clicked(self, button, treeview):

        """Called from callback in self.setup_scheduling_start_tab().

        Moves the selected media.Scheduled object up one position in the list.

        Args:

            button (Gtk.Button): The widget clicked

            treeview (Gtk.TreeView): The treeview with a selected line

        """

        selection = treeview.get_selection()
        (model, path_list) = selection.get_selected_rows()
        for path in path_list:

            this_iter = model.get_iter(path)
            if this_iter is not None:

                name = model[this_iter][0]
                self.app_obj.move_scheduled_list(name, False)

                model.move_before(
                    this_iter,
                    model.iter_previous(this_iter),
                )


    def on_scheduled_livestreams_button_toggled(self, checkbutton,
    checkbutton2, spinbutton):

        """Called from callback in self.setup_operations_livestreams_tab().

        Enables starting the livestream task periodically to check videos
        marked as livestreams.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            checkbutton2 (Gtk.CheckButton): Another widget to sensitise/
                desensitise, according to the new value of the flag

            spinbutton (Gtk.SpinButton): Another widget to sensitise/
                desensitise, according to the new value of the flag

        """

        if checkbutton.get_active() \
        and not self.app_obj.scheduled_livestream_flag:
            self.app_obj.set_scheduled_livestream_flag(True)
            spinbutton.set_sensitive(True)
            checkbutton2.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.scheduled_livestream_flag:
            self.app_obj.set_scheduled_livestream_flag(False)
            spinbutton.set_sensitive(False)
            checkbutton2.set_sensitive(False)
            checkbutton2.set_active(False)


    def on_scheduled_livestreams_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_operations_livestreams_tab().

        Sets the time (in minutes) between scheduled livestream operations.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.set_scheduled_livestream_wait_mins(
            spinbutton.get_value(),
        )


    def on_set_avconv_button_clicked(self, button, entry):

        """Called from callback in self.setup_downloader_ffmpeg_tab().

        Opens a window in which the user can select the avconv binary, if it is
        installed (and if the user wants it).

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Another widget to be modified by this function

        """

        dialogue_win = self.app_obj.dialogue_manager_obj.show_file_chooser(
            _('Please select the AVConv executable'),
            self,
            'open',
        )

        response = dialogue_win.run()
        if response == Gtk.ResponseType.OK:
            new_path = dialogue_win.get_filename()

        dialogue_win.destroy()

        if response == Gtk.ResponseType.OK and new_path:

            self.app_obj.set_avconv_path(new_path)
            entry.set_text(self.app_obj.avconv_path)


    def on_set_ffmpeg_button_clicked(self, button, entry):

        """Called from callback in self.setup_downloader_ffmpeg_tab().

        Opens a window in which the user can select the FFmpeg binary, if it is
        installed (and if the user wants it).

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Another widget to be modified by this function

        """

        dialogue_win = self.app_obj.dialogue_manager_obj.show_file_chooser(
            _('Please select the FFmpeg executable'),
            self,
            'open',
        )

        response = dialogue_win.run()
        if response == Gtk.ResponseType.OK:
            new_path = dialogue_win.get_filename()

        dialogue_win.destroy()

        if response == Gtk.ResponseType.OK and new_path:

            self.app_obj.set_ffmpeg_path(new_path)
            entry.set_text(self.app_obj.ffmpeg_path)


    def on_set_ytsc_button_clicked(self, button, entry):

        """Called from callback in self.setup_downloader_ytsc_tab().

        Opens a window in which the user can select the Youtube Stream Capture
        binary, if it is installed (and if the user wants it).

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Another widget to be modified by this function

        """

        dialogue_win = self.app_obj.dialogue_manager_obj.show_file_chooser(
            _('Please select the Youtube Stream Capture executable'),
            self,
            'open',
        )

        response = dialogue_win.run()
        if response == Gtk.ResponseType.OK:
            new_path = dialogue_win.get_filename()

        dialogue_win.destroy()

        if response == Gtk.ResponseType.OK and new_path:

            self.app_obj.set_ytsc_path(new_path)
            entry.set_text(self.app_obj.ytsc_path)


    def on_show_classic_mode_button_toggled(self, checkbutton):

        """Called from a callback in self.setup_windows_main_window_tab().

        Enables/disables automatically opening the Classic Mode tab on startup.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.show_classic_tab_on_startup_flag:
            self.app_obj.set_show_classic_tab_on_startup_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.show_classic_tab_on_startup_flag:
            self.app_obj.set_show_classic_tab_on_startup_flag(False)


    def on_show_custom_icons_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_main_window_tab().

        Enables/disables replacing stock icons with custom icons.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.show_custom_icons_flag:
            self.app_obj.set_show_custom_icons_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.show_custom_icons_flag:
            self.app_obj.set_show_custom_icons_flag(False)

        self.app_obj.dialogue_manager_obj.show_msg_dialogue(
            _('The new setting will be applied when Tartube restarts'),
            'info',
            'ok',
            self,           # Parent window is this window
        )


    def on_show_small_icons_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_videos_tab().

        Enables/disables smaller icons in the Video Index.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.show_small_icons_in_index_flag:
            self.app_obj.set_show_small_icons_in_index_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.show_small_icons_in_index_flag:
            self.app_obj.set_show_small_icons_in_index_flag(False)


    def on_show_status_icon_toggled(self, checkbutton, checkbutton2):

        """Called from a callback in self.setup_windows_system_tray_tab().

        Shows/hides the status icon in the system tray.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            checkbutton2 (Gtk.CheckButton): Another checkbutton to sensitise/
                desensitise, according to the new value of the flag

        """

        if checkbutton.get_active() \
        and not self.app_obj.show_status_icon_flag:
            self.app_obj.set_show_status_icon_flag(True)
            checkbutton2.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.show_status_icon_flag:
            self.app_obj.set_show_status_icon_flag(False)
            checkbutton2.set_sensitive(False)


    def on_show_tooltips_toggled(self, checkbutton, checkbutton2):

        """Called from callback in self.setup_windows_main_window_tab().

        Enables/disables tooltips for videos/channels/playlists/folders.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            checkbutton2 (Gtk.CheckButton): Another widget to be modified

        """

        if checkbutton.get_active() \
        and not self.app_obj.show_tooltips_flag:
            self.app_obj.set_show_tooltips_flag(True)
            checkbutton2.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.show_tooltips_flag:
            self.app_obj.set_show_tooltips_flag(False)
            checkbutton2.set_sensitive(False)
            checkbutton2.set_active(False)


    def on_show_tooltips_extra_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_videos_tab().

        Enables/disables errors/warnings in tooltips.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.show_tooltips_extra_flag:
            self.app_obj.set_show_tooltips_extra_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.show_tooltips_extra_flag:
            self.app_obj.set_show_tooltips_extra_flag(False)


    def on_sound_custom_changed(self, combo):

        """Called from callback in self.setup_operations_actions_tab().

        Sets the user's preferred sound effect for livestream alarms.

        Args:

            combo (Gtk.ComboBox): The widget clicked

        """

        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        self.app_obj.set_sound_custom(model[tree_iter][0])


    def on_squeeze_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_main_window_tab().

        Enables/disables labels in the main window's main toolbar.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.toolbar_squeeze_flag:
            self.app_obj.set_toolbar_squeeze_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.toolbar_squeeze_flag:
            self.app_obj.set_toolbar_squeeze_flag(False)


    def on_system_debug_toggled(self, checkbutton, debug_type, \
    checkbutton2=None):

        """Called from callback in self.setup_general_debug_tab().

        Enables/disables system debug messages.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            debug_type (str): Which debug flag to set; one of the strings
                'main_app', 'main_app_no_timer', 'main_win',
                'main_win_no_timer', 'downloads'

            checkbutton2 (Gtk.CheckButton or None): If specified, this
                checkbutton is (de)sensitised, depending on the state of
                the first checkbutton

        """

        flag = checkbutton.get_active()
        if not flag:
            flag = False
        else:
            flag = True

        if debug_type == 'main_app':
            mainapp.DEBUG_FUNC_FLAG = flag
        elif debug_type == 'main_app_no_timer':
            mainapp.DEBUG_NO_TIMER_FUNC_FLAG = flag
        elif debug_type == 'main_win':
            mainwin.DEBUG_FUNC_FLAG = flag
        elif debug_type == 'main_win_no_timer':
            mainwin.DEBUG_NO_TIMER_FUNC_FLAG = flag
        elif debug_type == 'downloads':
            downloads.DEBUG_FUNC_FLAG = flag

        if checkbutton2:

            if flag:
                checkbutton2.set_sensitive(True)
            else:
                checkbutton2.set_active(False)
                checkbutton2.set_sensitive(False)


    def on_system_error_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_errors_warnings_tab().

        Enables/disables system errors in the 'Errors/Warnings' tab. Toggling
        the corresponding Gtk.CheckButton in the Errors/Warnings tab sets the
        IV (and makes sure the two checkbuttons have the same status).

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        main_win_obj = self.app_obj.main_win_obj
        other_flag = main_win_obj.show_system_error_checkbutton.get_active()

        if (checkbutton.get_active() and not other_flag):
            main_win_obj.show_system_error_checkbutton.set_active(True)
        elif (not checkbutton.get_active() and other_flag):
            main_win_obj.show_system_error_checkbutton.set_active(False)


    def on_system_keep_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_main_window_tab().

        Enables/disables keeping the total number of system messages in the tab
        label until the clear button is explicitly clicked.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.system_msg_keep_totals_flag:
            self.app_obj.set_system_msg_keep_totals_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.system_msg_keep_totals_flag:
            self.app_obj.set_system_msg_keep_totals_flag(False)


    def on_system_warning_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_errors_warnings_tab().

        Enables/disables system warnings in the 'Errors/Warnings' tab. Toggling
        the corresponding Gtk.CheckButton in the Errors/Warnings tab sets the
        IV (and makes sure the two checkbuttons have the same status).

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        main_win_obj = self.app_obj.main_win_obj
        other_flag = main_win_obj.show_system_warning_checkbutton.get_active()

        if (checkbutton.get_active() and not other_flag):
            main_win_obj.show_system_warning_checkbutton.set_active(True)
        elif (not checkbutton.get_active() and other_flag):
            main_win_obj.show_system_warning_checkbutton.set_active(False)


    def on_terminal_json_button_toggled(self, checkbutton):

        """Called from a callback in self.setup_output_terminal_window_tab().

        Enables/disables writing output from youtube-dl's STDOUT to the
        terminal.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ytdl_write_ignore_json_flag:
            self.app_obj.set_ytdl_write_ignore_json_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ytdl_write_ignore_json_flag:
            self.app_obj.set_ytdl_write_ignore_json_flag(False)


    def on_terminal_progress_button_toggled(self, checkbutton):

        """Called from a callback in self.setup_output_terminal_window_tab().

        Enables/disables writing output from youtube-dl's STDOUT to the
        terminal.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ytdl_write_ignore_progress_flag:
            self.app_obj.set_ytdl_write_ignore_progress_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ytdl_write_ignore_progress_flag:
            self.app_obj.set_ytdl_write_ignore_progress_flag(False)


    def on_terminal_stderr_button_toggled(self, checkbutton):

        """Called from a callback in self.setup_output_terminal_window_tab().

        Enables/disables writing output from youtube-dl's STDERR to the
        terminal.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ytdl_write_stderr_flag:
            self.app_obj.set_ytdl_write_stderr_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ytdl_write_stderr_flag:
            self.app_obj.set_ytdl_write_stderr_flag(False)


    def on_terminal_stdout_button_toggled(self, checkbutton, checkbutton2, \
    checkbutton3):

        """Called from a callback in self.setup_output_terminal_window_tab().

        Enables/disables writing output from youtube-dl's STDOUT to the
        terminal.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            checkbutton2, checkbutton3 (Gtk.CheckButton): Additional
                checkbuttons to sensitise/desensitise, according to the new
                value of the flag

        """

        if checkbutton.get_active() \
        and not self.app_obj.ytdl_write_stdout_flag:
            self.app_obj.set_ytdl_write_stdout_flag(True)
            checkbutton2.set_sensitive(True)
            checkbutton3.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.ytdl_write_stdout_flag:
            self.app_obj.set_ytdl_write_stdout_flag(False)
            checkbutton2.set_sensitive(False)
            checkbutton3.set_sensitive(False)


    def on_terminal_system_button_toggled(self, checkbutton):

        """Called from a callback in self.setup_output_terminal_window_tab().

        Enables/disables writing youtube-dl system commands to the terminal.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ytdl_write_system_cmd_flag:
            self.app_obj.set_ytdl_write_system_cmd_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ytdl_write_system_cmd_flag:
            self.app_obj.set_ytdl_write_system_cmd_flag(False)


    def on_test_sound_clicked(self, button, combo):

        """Called from callback in self.setup_operations_actions_tab().

        Plays the sound effect selected in the combobox.

        Args:

            button (Gtk.Button): The widget that was clicked

            combo (Gtk.ComboBox): The widget in which a sound effect is
                selected.

        """

        self.app_obj.play_sound()


    def on_thumb_size_combo_changed(self, combo):

        """Called from a callback in self.setup_windows_videos_tab().

        Sets the size of thumbanils in the Video Catalogue grid.

        Args:

            combo (Gtk.ComboBox): The widget clicked

        """

        # (Changing the combo in the Video Catalogue's toolbar sets the IV)
        self.app_obj.main_win_obj.catalogue_thumb_combo.set_active(
            combo.get_active(),
        )


    def on_update_combo_changed(self, combo):

        """Called from a callback in self.setup_downloader_paths_tab().

        Extracts the value visible in the combobox, converts it into another
        value, and uses that value to update the main application's IV.

        Args:

            combo (Gtk.ComboBox): The widget clicked

        """

        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        self.app_obj.set_ytdl_update_current(model[tree_iter][0])


    def on_uploader_button_toggled(self, checkbutton):

        """Called from callback in self.setup_windows_websites_tab().

        Enables/disables ignoring of deletion by uploader error messages.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ignore_yt_uploader_deleted_flag:
            self.app_obj.set_ignore_yt_uploader_deleted_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ignore_yt_uploader_deleted_flag:
            self.app_obj.set_ignore_yt_uploader_deleted_flag(False)


    def on_use_first_button_toggled(self, checkbutton):

        """Called from callback in self.setup_files_database_tab().

        Enables/disables automatic loading of the first database file in the
        list.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.data_dir_use_first_flag:
            self.app_obj.set_data_dir_use_first_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.data_dir_use_first_flag:
            self.app_obj.set_data_dir_use_first_flag(False)


    def on_use_list_button_toggled(self, checkbutton):

        """Called from callback in self.setup_files_database_tab().

        Enables/disables automatic loading of an alternative database file, if
        the default one is locked.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.data_dir_use_list_flag:
            self.app_obj.set_data_dir_use_list_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.data_dir_use_list_flag:
            self.app_obj.set_data_dir_use_list_flag(False)


    def on_ytdl_fork_frame_clicked(self, event_box, event_button, radiobutton):

        """Called from a callback in self.setup_downloader_forks_tab().

        Enables/disables selecting a downloader by clicking anywhere in its
        containing frame.

        Args:

            event_box (Gtk.EventBox): Ignored

            event_button (Gdk.EventButton): Ignored

            radiobutton (Gtk.RadioButton): The radiobutton inside the clicked
                frame, which should be made active

        """

        if not radiobutton.get_active():
            radiobutton.set_active(True)


    def on_ytdl_verbose_button_toggled(self, checkbutton):

        """Called from a callback in self.setup_output_both_tab().

        Enables/disables writing verbose output (youtube-dl debugging mode).

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ytdl_write_verbose_flag:
            self.app_obj.set_ytdl_write_verbose_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ytdl_write_verbose_flag:
            self.app_obj.set_ytdl_write_verbose_flag(False)


    def on_ytsc_verbose_button_toggled(self, checkbutton):

        """Called from a callback in self.setup_output_both_tab().

        Enables/disables writing verbose output for Youtube Stream Capture.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.ytsc_write_verbose_flag:
            self.app_obj.set_ytsc_write_verbose_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.ytsc_write_verbose_flag:
            self.app_obj.set_ytsc_write_verbose_flag(False)


    def on_worker_button_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_performance_tab().

        Enables/disables the simultaneous download limit. Toggling the
        corresponding Gtk.CheckButton in the Progress Tab sets the IV (and
        makes sure the two checkbuttons have the same status).

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        other_flag \
        = self.app_obj.main_win_obj.num_worker_checkbutton.get_active()

        if (checkbutton.get_active() and not other_flag):
            self.app_obj.main_win_obj.num_worker_checkbutton.set_active(True)
        elif (not checkbutton.get_active() and other_flag):
            self.app_obj.main_win_obj.num_worker_checkbutton.set_active(False)


    def on_worker_bypass_button_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_livestreams_tab().

        Enables/disables bypassing the maximum simultaneous downloads limit
        when downloading broadcasting livestreams.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        if checkbutton.get_active() \
        and not self.app_obj.num_worker_bypass_flag:
            self.app_obj.setnum_worker_bypass_flag(True)
        elif not checkbutton.get_active() \
        and self.app_obj.num_worker_bypass_flag:
            self.app_obj.set_num_worker_bypass_flag(False)


    def on_worker_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_operations_performance_tab().

        Sets the simultaneous download limit. Setting the value of the
        corresponding Gtk.SpinButton in the Progress Tab sets the IV (and
        makes sure the two spinbuttons have the same value).

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.main_win_obj.num_worker_spinbutton.set_value(
            spinbutton.get_value(),
        )


    def on_video_res_button_toggled(self, checkbutton):

        """Called from callback in self.setup_operations_performance_tab().

        Enables/disables the video resolution limit. Toggling the corresponding
        Gtk.CheckButton in the Progress Tab sets the IV (and makes sure the two
        checkbuttons have the same status).

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

        """

        other_flag \
        = self.app_obj.main_win_obj.video_res_checkbutton.get_active()

        if (checkbutton.get_active() and not other_flag):
            self.app_obj.main_win_obj.video_res_checkbutton.set_active(True)
        elif (not checkbutton.get_active() and other_flag):
            self.app_obj.main_win_obj.video_res_checkbutton.set_active(False)


    def on_video_res_combo_changed(self, combo):

        """Called from a callback in self.setup_operations_performance_tab().

        Extracts the value visible in the combobox, converts it into another
        value, and uses that value to update the main application's IV.

        Args:

            combo (Gtk.ComboBox): The widget clicked

        """

        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        self.app_obj.main_win_obj.set_video_res(model[tree_iter][0])


    def on_ytdl_fork_button_toggled(self, radiobutton, entry, fork_type=None):

        """Called from callback in self.setup_downloader_forks_tab().

        Sets the youtube-dl fork to be used. See also
        self.on_ytdl_fork_changed().

        Args:

            radiobutton (Gtk.Radiobutton): The widget clicked

            entry (Gtk.Entry): Another widget to be updated

            fork_type (str): 'yt-dlp', 'youtube-dl', or None for any other fork

        """

        if radiobutton.get_active():

            if fork_type is None:

                fork_name = entry.get_text()
                # (If the 'other fork' option is selected, but nothing is
                #   entered in the entry box, use youtube-dl as the downloader)
                if fork_name == '':
                    self.app_obj.set_ytdl_fork(None)
                else:
                    self.app_obj.set_ytdl_fork(fork_name)

                entry.set_sensitive(True)

            elif fork_type == 'youtube-dl':

                self.app_obj.set_ytdl_fork(None)
                entry.set_text('')
                entry.set_sensitive(False)

            elif fork_type == 'yt-dlp':

                self.app_obj.set_ytdl_fork(fork_type)
                entry.set_text('')
                entry.set_sensitive(False)

        self.update_ytdl_combos()


    def on_ytdl_fork_changed(self, entry, radiobutton):

        """Called from callback in self.setup_downloader_forks_tab().

        Sets the youtube-dl fork to be used. See also
        self.on_ytdl_fork_button_toggled().

        Args:

            entry (Gtk.Entry): The widget changed

        """

        if radiobutton.get_active():

            text = utils.strip_whitespace(entry.get_text())
            if text == '':
                self.app_obj.set_ytdl_fork(None)
            else:
                self.app_obj.set_ytdl_fork(text)

            self.update_ytdl_combos()


    def on_ytdl_path_button_clicked(self, button, entry):

        """Called from callback in self.setup_downloader_paths_tab().

        Sets a custom path to the youtube-dl(c) executable.

        Args:

            button (Gtk.Button): The widget clicked

            entry (Gtk.Entry): Another widget to update

        """

        # Prompt the user for the new youtube-dl(c) executable
        dialogue_win = self.app_obj.dialogue_manager_obj.show_file_chooser(
            _('Select the youtube-dl-compatible executable'),
            self,
            'open',
        )

        # (When the user first selects a custom path, using the combobox, the
        #   default youtube-dl(c) path is used until they have selected a new
        #   path)
        if self.app_obj.ytdl_path != self.app_obj.ytdl_path_default:
            dialogue_win.set_current_folder(self.app_obj.ytdl_path)

        # Get the user's response
        response = dialogue_win.run()
        if response == Gtk.ResponseType.OK:
            new_path = dialogue_win.get_filename()

        dialogue_win.destroy()
        if response == Gtk.ResponseType.OK:

            self.app_obj.set_ytdl_path(new_path)
            self.app_obj.ytdl_update_dict['ytdl_update_custom_path'] \
            = ['python3', self.app_obj.ytdl_path, '-U']

            entry.set_text(new_path)


    def on_ytdl_path_combo_changed(self, combo, entry, button):

        """Called from a callback in self.setup_downloader_paths_tab().

        Extracts the value visible in the combobox, converts it into another
        value, and uses that value to update the main application's IV.

        Args:

            combo (Gtk.ComboBox): The widget clicked

            entry (Gtk.Entry): Another entry to check

            button (Gtk.Button): Another widget to modify

        """

        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        ytdl_path = model[tree_iter][1]

        if ytdl_path is not None:

            self.app_obj.set_ytdl_path(ytdl_path)
            self.app_obj.set_ytdl_path_custom_flag(False)
            entry.set_text('')
            button.set_sensitive(False)

        else:

            # Custom youtube-dl(c) path, set by the entry/button
            # Until the user has selected their own executable, use the default
            #   one
            self.app_obj.set_ytdl_path(self.app_obj.ytdl_path_default)
            self.app_obj.ytdl_update_dict['ytdl_update_custom_path'] \
            = ['python3', self.app_obj.ytdl_path, '-U']
            self.app_obj.set_ytdl_path_custom_flag(True)

            entry.set_text(self.app_obj.ytdl_path)
            button.set_sensitive(True)


    def on_ytsc_priority_button_toggled(self, checkbutton, spinbutton,
    spinbutton2, checkbutton2):

        """Called from callback in self.setup_operations_livestreams_tab().

        Enables/disables desktop notifications when a livestream starts.

        Args:

            checkbutton (Gtk.CheckButton): The widget clicked

            spinbutton, spinbutton2 (Gtk.SpinButton): Other widgets to modify

            checkbutton2 (Gtk.CheckButton): Another widget to modify

        """

        if checkbutton.get_active() \
        and not self.app_obj.ytsc_priority_flag:

            self.app_obj.set_ytsc_priority_flag(True)
            spinbutton.set_sensitive(True)
            spinbutton2.set_sensitive(True)
            checkbutton2.set_sensitive(True)

        elif not checkbutton.get_active() \
        and self.app_obj.ytsc_priority_flag:
            self.app_obj.set_ytsc_priority_flag(False)
            spinbutton.set_sensitive(False)
            spinbutton2.set_sensitive(False)
            checkbutton2.set_sensitive(False)
            checkbutton2.set_active(False)


    def on_ytsc_restart_max_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_operations_livestreams_tab().

        Sets the maximum number of restarts for YTSC stream captures.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.set_ytsc_restart_max(
            spinbutton.get_value(),
        )


    def on_ytsc_wait_time_spinbutton_changed(self, spinbutton):

        """Called from callback in self.setup_operations_livestreams_tab().

        Sets the timeout (in minutes) for YTSC stream captures.

        Args:

            spinbutton (Gtk.SpinButton): The widget clicked

        """

        self.app_obj.set_ytsc_wait_time(
            spinbutton.get_value(),
        )


    # (Callback support functions)


    def try_switch_db(self, data_dir, button):

        """Called by self.on_data_dir_change_button_clicked() and
        .on_data_dir_switch_button_clicked().

        Having confirmed that a database directory specified by the user
        actually exists, attempt to load the database file inside it.

        Args:

            data_dir (str): The full path to the data directory

            button (Gtk.Button): A button to be possibly desensitised

        """

        dialogue_manager_obj = self.app_obj.dialogue_manager_obj

        # Database file already exists, so try to load it now
        if not self.app_obj.switch_db([data_dir, self]):

            # Load failed, and the user chose to shut down Tartube
            if self.app_obj.disable_load_save_lock_flag:

                return self.app_obj.stop()

            # Load failed for any other reason
            elif self.app_obj.disable_load_save_flag:

                button.set_sensitive(False)

                if not self.app_obj.disable_load_save_lock_flag:

                    if self.app_obj.disable_load_save_msg is not None:

                        dialogue_win = dialogue_manager_obj.show_msg_dialogue(
                            self.app_obj.disable_load_save_msg,
                            'error',
                            'ok',
                            self,           # Parent window is this window
                        )

                    else:

                        dialogue_win = dialogue_manager_obj.show_msg_dialogue(
                            _('Database file not loaded'),
                            'error',
                            'ok',
                            self,           # Parent window is this window
                        )

                # When load/save is disabled, this preference window can't be
                #   opened
                # Therefore, if load/save has just been disabled, close this
                #   window after the dialogue window closes
                dialogue_win.set_modal(True)
                dialogue_win.run()
                dialogue_win.destroy()
                if self.app_obj.disable_load_save_flag:
                    self.destroy()

            # Load not attempted
            else:

                dialogue_win = dialogue_manager_obj.show_msg_dialogue(
                    _('Did not try to load the database file'),
                    'error',
                    'ok',
                    self,           # Parent window is this window
                )

        else:

            # Load succeeded. Redraw the preference window, opening it at the
            #   same tab
            self.reset_window()
            self.select_switch_db_tab()

            if self.app_obj.disable_load_save_msg is not None:

                dialogue_manager_obj.show_msg_dialogue(
                    self.app_obj.disable_load_save_msg,
                    'info',
                    'ok',
                    self,           # Parent window is this window
                )

            else:

                dialogue_manager_obj.show_msg_dialogue(
                    _('Database file loaded'),
                    'info',
                    'ok',
                    self,           # Parent window is this window
                )


    def update_ytdl_combos(self):

        """Called initially by self.setup_downloader_paths_tab(), then by
        self.on_ytdl_fork_changed().

        Updates the contents of the two comboboxes in the tab, so that the
        youtube-dl fork is visible, rather than yotube-dl itself (if
        applicable).

        """

        fork = standard = 'youtube-dl'
        if self.app_obj.ytdl_fork is not None:
            fork = self.app_obj.ytdl_fork

        ytdl_path_default = re.sub(
            standard,
            fork,
            self.app_obj.ytdl_path_default,
        )

        # First combo: Path to the youtube-dl executable
        self.path_liststore.set(
            self.path_liststore.get_iter(Gtk.TreePath(0)),
            0,
            _('Use default path') + ' (' + ytdl_path_default + ')',
        )

        ytdl_bin = re.sub(
            standard,
            fork,
            self.app_obj.ytdl_bin,
        )

        self.path_liststore.set(
            self.path_liststore.get_iter(Gtk.TreePath(1)),
            0,
            _('Use local path') + ' (' + ytdl_bin + ')',
        )

        if os.name != 'nt':

            ytdl_path_pypi = re.sub(
                standard,
                fork,
                self.app_obj.ytdl_path_pypi,
            )

            self.path_liststore.set(
                self.path_liststore.get_iter(Gtk.TreePath(3)),
                0,
                _('Use PyPI path') + ' (' + ytdl_path_pypi + ')',
            )

        # Second combo: Command for update operations
        count = -1
        for item in self.app_obj.ytdl_update_list:

            count += 1
            descrip = re.sub(standard, fork, formats.YTDL_UPDATE_DICT[item])
            self.cmd_liststore.set(
                self.cmd_liststore.get_iter(Gtk.TreePath(count)),
                1,
                descrip,
            )

