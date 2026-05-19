from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLayout, QFrame,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QGroupBox,
    QLabel, QPlainTextEdit, QLineEdit, QProgressBar,
    QTableWidget, QTableWidgetItem, 
    QPushButton, QComboBox,
    QDialog, QMessageBox, );
from PyQt6.QtCore import QTimer;
from PyQt6.QtGui import QSyntaxHighlighter, QColor, QTextCharFormat, QPalette, QColor, QImage, QPixmap;
import pyqtgraph; #library responsible for all the plotting
import cv2;

   

#TODO: Set card view
#Contains the overview window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__();
        
        self.setWindowTitle("TBM Manager");
    
        #stores if windows have been opened, we don't want copies of the same window
        self.navigation = None;
        self.logs = None; 
        self.componentOverview_window = None;
        
        overview_layout = QGridLayout(); #overall grid pattern for all widgets to be organized in
        
        status_frame = QFrame(self);
        status_frame.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken);
        status_layout = QVBoxLayout();
        status_frame.setLayout(status_layout);
        
        operation_status_label = QLabel(text="Status: Operationable");
        status_layout.addWidget(operation_status_label);
        fire_interlock_label = QLabel(text="Fire Suppression: Ready");
        doors_interlock_label = QLabel(text="Doors: Closed");
        estop_interlock_label = QLabel(text="E-Stop: Ready");
        proximity_interlock_label = QLabel(text="Proximity Sensors: Ready");
        navigation_status_label = QLabel(text="Navigation Status: Halted");
        
        logs_textbox = QPlainTextEdit(); #PlainTextEdit is best for efficient updating for chunks of text like logs
        logs_textbox.setMaximumBlockCount(6); #this is a log preview, so a limited size is good
        logs_textbox.setReadOnly(True);
        
        emergency_button = QPushButton(); 
        emergency_button.setText("EMERGENCY STOP!");
        emergency_button.clicked.connect(self.test_dialog);
        
        navigation_open_button = QPushButton();
        navigation_open_button.setText("Open Navigation Info");
        navigation_open_button.clicked.connect(self.navigation_open);
        logs_open_button = QPushButton();
        logs_open_button.setText("Open Logs");
        logs_open_button.clicked.connect(self.logs_window_open);
        componentOverview_open_button = QPushButton();
        componentOverview_open_button.setText("Open Component Overview");
        componentOverview_open_button.clicked.connect(self.componentOverview_open);
        
        #widget coordinates are provided in (x, y) in a x * y grid
        #TODO: fix label layout
        overview_layout.addWidget(logs_textbox, 1, 0);
        overview_layout.addWidget(navigation_open_button, 2, 0);
        overview_layout.addWidget(componentOverview_open_button, 3, 0);
        overview_layout.addWidget(logs_open_button, 4, 0);
        overview_layout.addWidget(status_frame, 0, 1);
        overview_layout.addWidget(fire_interlock_label, 1, 1);
        overview_layout.addWidget(doors_interlock_label, 2, 1);
        overview_layout.addWidget(estop_interlock_label, 3, 1);
        overview_layout.addWidget(proximity_interlock_label, 4, 1);
        overview_layout.addWidget(navigation_status_label, 5, 1);
        overview_layout.addWidget(emergency_button, 6,1);
        
        
        widget = QWidget(); # windows are empty base widgets, so make a window
        widget.setLayout(overview_layout); #set the main layout of the window
        
    
        self.setCentralWidget(widget); #make the main screen's pivot widget the window, this is only needed for main window
        
    def test_dialog(self):
        button = QMessageBox.information(self,"Emergency Stop", "Machine Halted"); #opens an information type message box
    
    def navigation_open(self):
        #opens the navigation window if it already hasn't been opened
        if self.navigation is None:
            self.navigation = NavigationWindow();
        self.navigation.show();
        
    def logs_window_open(self):
        #opens the navigation window if it already hasn't been opened
        if self.logs is None:
            self.logs = LogsWindow();
        self.logs.show();
        
    def componentOverview_open(self):
        #opens the navigation window if it already hasn't been opened
        if self.componentOverview_window is None:
            self.componentOverview_window = ComponentOverviewWindow();
        self.componentOverview_window.show();
                

#Window that shows all the navigation info of the TBM
#TODO: Complete navigation window.
class NavigationWindow(QWidget):
    def __init__(self):
        super().__init__();
        
        self.setWindowTitle("Navigation Diagnostics");
        self.cameraWindow = None;
        
        #TODO: Get test 2D plotting working
        self.test_x = [0, 1, 2, 3, 4, 5, 6];
        self.test_y = [7, 8, 9, 10, 11, 12, 13];
        
        navigation_layout = QGridLayout();
        self.setLayout(navigation_layout);
        
        navigation_status_label = QLabel("Navigation Status: Halted");  
        
        navigation_camera_button = QPushButton("Open Camera");
        navigation_camera_button.pressed.connect(self.camera_window_open);
        
        navigation_plot = pyqtgraph.PlotWidget();
        navigation_plot.setBackground("w");
        
        navigation_layout.addWidget(navigation_plot, 0, 0);
        navigation_layout.addWidget(navigation_status_label, 1, 0);
        navigation_layout.addWidget(navigation_camera_button, 2, 0);
        
        self.navigation_graph = navigation_plot.plot(self.test_x, self.test_y, pen=pyqtgraph.mkPen(255,0,0));
        
        #TODO: Get dynamic plotting working.
        #self.update_timer = QTimer();
        #self.update_timer.setInterval(600);
        #self.update_timer.timeout.connect(self.update_plot);
        #self.update_timer.start();    
    
    #def update_plot(self):
    #    self.test_x.append(self.test_x.__len__() + 1);
    #    self.test_y.append(self.test_x.__len__() + 4);
    #    self.navigation_graph.setData(self.test_x, self.test_y);
    
    def camera_window_open(self):
        #opens the navigation window if it already hasn't been opened
        if self.cameraWindow is not None:
            self.cameraWindow = None;
            
        self.cameraWindow = CameraWindow();
        self.cameraWindow.show();
        

     
class CameraWindow(QWidget):
    def __init__(self):
        super().__init__();
        self.setWindowTitle("Test Camera");
        
        camera_layout = QGridLayout();
        self.camera_label = QLabel();
        self.setLayout(camera_layout);
        camera_layout.addWidget(self.camera_label, 0, 0);
        
        self.cam = cv2.VideoCapture(0);
        
        self.cam_timer = QTimer();
        self.cam_timer.timeout.connect(self.update_frame);
        self.cam_timer.start(30);
        
    def update_frame(self):
        camera_captured, camera_frame = self.cam.read();
        if not camera_captured:
            return

        #OpenCV uses BGR readings, PyQt can only read RGB
        camera_frame = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB);

        frame_height, frame_width, frame_channels = camera_frame.shape;
        frame_bytesPerLine = frame_channels * frame_width;

        qt_image = QImage(camera_frame, frame_width, frame_height, frame_bytesPerLine, QImage.Format.Format_RGB888);
        pixmap = QPixmap.fromImage(qt_image);

        self.camera_label.setPixmap(pixmap);

    def closeEvent(self, event):
        self.cam_timer.stop();
        if self.cam is not None:
            self.cam.release();
        self.camera_label.clear();
        event.accept();

        
        

#TODO: Add text highlighting for each type of log.
class QLogsHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document);
        
    def highlightBlock(self, text):
        if "ERROR" in text:
            fmt = QTextCharFormat()
            fmt.setBackground(QColor("red"))
            self.setFormat(0, len(text), fmt)       
        else:
            fmt = QTextCharFormat()
            fmt.setBackground(QColor("yellow"))
            self.setFormat(0, len(text), fmt)
        
 
#TODO: Make the log window shared in the main screen and in the log screen. Need dynamic synchronization.        
class LogsWindow(QWidget):
    def __init__(self):
        super().__init__();
        
        self.setWindowTitle("Logs Viewer");
        
        logs_layout = QGridLayout();
        self.setLayout(logs_layout);
        logs_controls_layout = QHBoxLayout();
        logs_layout.addLayout(logs_controls_layout, 0, 0);
        
        logs_textbox = QPlainTextEdit(); #PlainTextEdit is best for efficient updating for chunks of text like logs
        logs_textbox.setReadOnly(True);
        logs_layout.addWidget(logs_textbox, 1, 0);
        
        logs_highlighter = QLogsHighlighter(logs_textbox.document());
        
        #TODO: Add widgets to a collection and enumerate to add widgets
        search_label = QLabel("Search: ");
        search_lineEdit = QLineEdit();
        filter_combobox = QComboBox();
        logs_controls_layout.addWidget(search_label);
        logs_controls_layout.addWidget(search_lineEdit);
        logs_controls_layout.addWidget(filter_combobox);
        
        logs_textbox.appendPlainText("ERROR \n Test");


class ComponentOverviewWindow(QWidget):
    def __init__(self):
        super().__init__();
        
        self.setWindowTitle("Component Overview");
        
        component_overview_layout = QGridLayout();
        top_half_layout = QHBoxLayout();
        communications_layout = QHBoxLayout();
        circuits_monitoring_layout = QGridLayout();
        power_metrics_layout = QFormLayout();
        
        component_overview_layout.addLayout(top_half_layout, 0, 0);
        component_overview_layout.addLayout(communications_layout, 3, 0)
        
        self.setLayout(component_overview_layout);
        
        circuits_monitoring_groupbox = QGroupBox(title="Circuits Monitoring");
        power_metrics_groupbox = QGroupBox(title="Power Metrics");
        circuits_monitoring_groupbox.setLayout(circuits_monitoring_layout);
        power_metrics_groupbox.setLayout(power_metrics_layout);
        
        top_half_layout.addWidget(circuits_monitoring_groupbox);
        top_half_layout.addWidget(power_metrics_groupbox);
        
        #component_overview_layout.addWidget(circuits_monitoring_groupbox, 0, 0);
        #component_overview_layout.addWidget(power_metrics_groupbox, 0, 1);
        
        control_circuit_label = QLabel("Circuit \nVoltage: 12V");
        power_circuit_label = QLabel("Circuit \nVoltage: 12V");
        lighting_circuit_label = QLabel("Circuit \nVoltage: 12V");
        sensor_circuit_label = QLabel("Circuit \nVoltage: 12V");
        actuator_circuit_label = QLabel("Circuit \nVoltage: 12V");
        communication_circuit_label = QLabel("Circuit \nVoltage: 12V");
        
        circuits_monitoring_layout.addWidget(control_circuit_label, 0, 0);
        circuits_monitoring_layout.addWidget(power_circuit_label, 0, 1);
        circuits_monitoring_layout.addWidget(lighting_circuit_label, 0, 2);
        circuits_monitoring_layout.addWidget(sensor_circuit_label, 1, 0);
        circuits_monitoring_layout.addWidget(actuator_circuit_label, 1, 1);
        circuits_monitoring_layout.addWidget(communication_circuit_label, 1, 2);
        
        supply_voltage_label = QLabel("Supply Voltage:");
        supply_current_label = QLabel("Supply Current:");
        power_draw_label = QLabel("Power Draw:");
        supply_voltage_indicator = QProgressBar();
        supply_voltage_indicator.setMaximum(15);
        supply_voltage_indicator.setValue(7);
        supply_voltage_indicator.setFormat("%v V");
        supply_current_indicator = QProgressBar();
        supply_current_indicator.setMaximum(20);
        supply_current_indicator.setValue(10);
        supply_current_indicator.setFormat("%v A");
        power_draw_indicator = QProgressBar();
        power_draw_indicator.setMaximum(20);
        power_draw_indicator.setValue(10);
        power_draw_indicator.setFormat("%v W");
        
        power_metrics_layout.addRow(supply_voltage_label, supply_voltage_indicator);
        power_metrics_layout.addRow(supply_current_label, supply_current_indicator);
        power_metrics_layout.addRow(power_draw_label, power_draw_indicator);
        
        component_selector_combobox = QComboBox();
        component_overview_layout.addWidget(component_selector_combobox, 1, 0);
        component_selector_combobox.addItems(["Circuit 1", "Sensor 1"]);
        
        component_viewer_table = QTableWidget();
        component_viewer_table.setRowCount(2);
        component_viewer_table.setColumnCount(2);
        component_overview_layout.addWidget(component_viewer_table, 2, 0);
        
        component_viewer_table.setItem(0, 0, QTableWidgetItem("Test 1"));
        component_viewer_table.setItem(0, 1, QTableWidgetItem("Test 2"));
        component_viewer_table.setItem(1, 0, QTableWidgetItem("Test 3"));
        component_viewer_table.setItem(1, 1, QTableWidgetItem("Test 4"));
        
        component_viewer_table.show();
        
        sensors_link_button = QPushButton(text = "Sensors Link");
        controllers_link_button = QPushButton(text = "Controllers Link");
        communications_layout.addWidget(sensors_link_button);
        communications_layout.addWidget(controllers_link_button);
        
        sensors_link_button.clicked.connect(self.showLinkDialog);
        controllers_link_button.clicked.connect(self.showLinkDialog);
    
    def showLinkDialog(self):
        self.linkDialog = CommunicationLinksDialog();
        self.linkDialog.show();    
        
        
class CommunicationLinksDialog(QDialog):
    def __init__(self):
        super().__init__();
        self.setWindowTitle("Link Viewer");

        link_dialog_layout = QVBoxLayout();
        self.setLayout(link_dialog_layout);

        # Create table
        link_table = QTableWidget(2, 2);
        link_table.setHorizontalHeaderLabels(["Component Name", "Detail"]);

        # Add data
        test_tabledata = [("Sensor 1", "Electrical"), ("Sensor 2", "Mechanical")];
        for row, (name, detail) in enumerate(test_tabledata):
            link_table.setItem(row, 0, QTableWidgetItem(name));
            link_table.setItem(row, 1, QTableWidgetItem(detail));
            
        link_table.show();
        link_dialog_layout.addWidget(link_table);        
                
manager_application = QApplication([]);

#Set Application-Wide Color Scheme
manager_palette = manager_application.palette();
manager_palette.setColor(QPalette.ColorRole.Window, QColor("#111827"));
manager_palette.setColor(QPalette.ColorRole.Base, QColor("#0f172a"));
manager_palette.setColor(QPalette.ColorRole.WindowText, QColor("white"));
manager_application.setPalette(manager_palette);

panel_palette = manager_application.palette();
panel_palette.setColor(QPalette.ColorRole.Window, QColor("1f2937"));


main_window = MainWindow();
main_window.show();
manager_application.exec();        