import argparse
import sys
from darktheme.widget_template import DarkPalette
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QSplitter, QVBoxLayout, QTreeView, QWidget

from skyfield.api import wgs84
from spytnik import sats, sites, traces
from spytnik.widgets import map, polarplot


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SPyTnik STRF Trace Viewer")
        self.window_width, self.window_height = 1280, 960
        self.setMinimumSize(self.window_width, self.window_height)
        self.setWindowFlags(
            Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowCloseButtonHint
        )

        self.tles = None
        self.sites = None
        self.trace_groups = []

        hsplitter = QSplitter()
        hsplitter.setOrientation(Qt.Horizontal)

        top_container_layout = QVBoxLayout()
        top_container_layout.addWidget(hsplitter)

        top_container = QWidget()
        top_container.setLayout(top_container_layout)

        vsplitter = QSplitter()
        vsplitter.setOrientation(Qt.Vertical)
        vsplitter.addWidget(top_container)

        layout = QVBoxLayout()
        layout.addWidget(vsplitter)

        self.setLayout(layout)

        self.traceTreeModel = self.createTraceViewModel()
        self.traceTree = QTreeView(vsplitter)
        self.traceTree.setModel(self.traceTreeModel)
        self.mapView = map.Map(hsplitter)
        self.polarPlot = polarplot.PolarPlotWidget(hsplitter)

        vsplitter.setSizes([960, 320])

    def createTraceViewModel(self):
        model = QStandardItemModel(0, 6, self)
        model.setHeaderData(0, Qt.Horizontal, "Trace")
        model.setHeaderData(1, Qt.Horizontal, "Site")
        model.setHeaderData(2, Qt.Horizontal, "RSite")
        model.setHeaderData(3, Qt.Horizontal, "Start")
        model.setHeaderData(4, Qt.Horizontal, "End")
        model.setHeaderData(5, Qt.Horizontal, "Points")

        model.itemChanged.connect(self.render)

        return model

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        if e.key() == Qt.Key_F11:
            if self.isFullScreen():
                if self.isMaximized():
                    self.showMaximized()
                else:
                    self.showNormal()
            else:
                self.showFullScreen()

    def render(self):
        s = self.sites.get_site()
        self.mapView.init(s["latlon"].latitude.degrees, s["latlon"].longitude.degrees)
        self.polarPlot.clean()

        self.renderTraces()

        self.mapView.render()

    def renderTraces(self):
        rendered_sites = set()

        for trace_group_index, trace_group in enumerate(self.trace_groups):
            render_group = self.traceTreeModel.item(trace_group_index).checkState()

            for trace_index, trace in enumerate(trace_group.traces):
                render_trace = (
                    self.traceTreeModel.item(trace_group_index)
                    .child(trace_index)
                    .checkState()
                )

                if render_group or render_trace:
                    color = "blue" if trace.rsite is None else "red"

                    self.mapView.add_pass(
                        trace.lat,
                        trace.lon,
                        trace.start_time.utc_iso,
                        trace.end_time.utc_iso,
                        color,
                    )
                    self.polarPlot.add_curve(trace.az, trace.el)

                    if trace.site and trace.site not in rendered_sites:
                        self.renderSite(trace.site)
                        rendered_sites.add(trace.site)

                    if trace.rsite and trace.rsite not in rendered_sites:
                        self.renderSite(trace.rsite)
                        rendered_sites.add(trace.rsite)

    def renderSite(self, site=None):
        s = self.sites.get_site(site)
        self.mapView.add_site(
            s["latlon"].latitude.degrees,
            s["latlon"].longitude.degrees,
            "[{}] {} - {}".format(s["acronym"], site, s["name"]),
        )

    def loadTLEs(self, tlefile=None):
        self.tles = sats.load_sats(tlefile)

    def loadSites(self, sitefile=None):
        self.sites = sites.load_sites(sitefile)

    def addTrace(self, satid, datfile):
        sat = self.tles.sat_by_id(satid)
        trace_group = traces.load_dat_file(datfile, satid)
        trace_group.calculatePasses(sat, self.sites)

        self.trace_groups.append(trace_group)

        root = self.traceTreeModel.invisibleRootItem()

        trace_group_row = [
            QStandardItem(trace_group.name),
            None,
            None,
            QStandardItem(trace_group.start_time.utc_iso()),
            QStandardItem(trace_group.end_time.utc_iso()),
            QStandardItem(str(trace_group.num_points)),
        ]
        trace_group_row[0].setCheckable(True)
        trace_group_row[0].setCheckState(False)
        root.appendRow(trace_group_row)

        for trace in trace_group.traces:
            trace_row = [
                QStandardItem(""),
                QStandardItem(str(trace.site)),
                QStandardItem(str(trace.rsite) if trace.rsite else ""),
                QStandardItem(trace.start_time.utc_iso()),
                QStandardItem(trace.end_time.utc_iso()),
                QStandardItem(str(trace.num_points)),
            ]
            trace_row[0].setCheckable(True)
            trace_row[0].setCheckState(False)
            trace_group_row[0].appendRow(trace_row)


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", nargs="*", default=[], required=True)
    parser.add_argument("-s", "--sat_id", type=int, required=True)
    parser.add_argument("-t", "--tle", help="TLE file")
    return parser.parse_args()


def main(args=None):
    args = getArgs()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(DarkPalette())
    app.setStyleSheet(
        """
        QWidget {
            font-size: 12px;
        }
        QToolTip {
            color: #ffffff;
            background-color: grey;
            border: 1px solid white;
        }
        """
    )

    myApp = MyApp()

    myApp.loadTLEs(args.tle)
    myApp.loadSites()

    for d in args.data:
        myApp.addTrace(args.sat_id, d)

    myApp.render()
    myApp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Closing Window...")


if __name__ == "__main__":
    main()
