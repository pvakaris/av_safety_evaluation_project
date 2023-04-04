import sys

from PyQt5.QtWidgets import *
from crdesigner.ui.gui.mwindow.mwindow import MWindow


def start_gui_new(input_file: str = None, first_points_list: list = None, second_points_list: list = None):
    """
    Redirect to the main window start.
    """
    # application
    app = QApplication(sys.argv)
    if input_file and (first_points_list or second_points_list):
        # Draw the map and mark coordinates
        w = MWindow(input_file, first_points_list, second_points_list)
    else:
        w = MWindow()
    w.showMaximized()
    sys.exit(app.exec_())


if __name__ == '__main__':
    start_gui_new()
