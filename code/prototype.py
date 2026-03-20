from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLayout, 
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPlainTextEdit,
    QPushButton, QDialog, QMessageBox);
from PyQt6.QtCore import QTimer;
import pyqtgraph;

   

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__();
        
        self.setWindowTitle("TBM Manager");
        
        overview_layout = QGridLayout();
        
        self.navigation = None;
        
        
        operation_status_label = QLabel(text="Status: Operationable");
        fire_interlock_label = QLabel(text="Fire Suppression: Ready");
        doors_interlock_label = QLabel(text="Doors: Closed");
        estop_interlock_label = QLabel(text="E-Stop: Ready");
        proximity_interlock_label = QLabel(text="Proximity Sensors: Ready");
        navigation_status_label = QLabel(text="Navigation Status: Halted");
        
        logs_textbox = QPlainTextEdit();
        logs_textbox.setMaximumBlockCount(6);
        logs_textbox.setReadOnly(True);
        
        emergency_button = QPushButton();
        emergency_button.setText("EMERGENCY STOP!");
        emergency_button.clicked.connect(self.test_dialog);
        
        navigation_open_button = QPushButton();
        navigation_open_button.setText("Navigation System Open");
        navigation_open_button.clicked.connect(self.navigation_open);
        
        overview_layout.addWidget(logs_textbox, 1, 0);
        overview_layout.addWidget(navigation_open_button, 2, 0);
        overview_layout.addWidget(operation_status_label, 0, 1);
        overview_layout.addWidget(fire_interlock_label, 1, 1);
        overview_layout.addWidget(doors_interlock_label, 2, 1);
        overview_layout.addWidget(estop_interlock_label, 3, 1);
        overview_layout.addWidget(proximity_interlock_label, 4, 1);
        overview_layout.addWidget(navigation_status_label, 5, 1);
        overview_layout.addWidget(emergency_button, 6,1);
        
        
        widget = QWidget();
        widget.setLayout(overview_layout);
        
        self.setCentralWidget(widget);
        
    def test_dialog(self):
        button = QMessageBox.information(self,"Emergency Stop", "Machine Halted");
    
    def navigation_open(self):
        if self.navigation is None:
            self.navigation = NavigationWindow();
        self.navigation.show();
                

class NavigationWindow(QWidget):
    def __init__(self):
        super().__init__();
        
        self.test_x = [0, 1, 2, 3, 4, 5, 6];
        self.test_y = [7, 8, 9, 10, 11, 12, 13];
        
        navigation_layout = QGridLayout();
        
        navigation_status_label = QLabel("Navigation Status: Halted");  
        
        navigation_plot = pyqtgraph.PlotWidget();
        navigation_plot.setBackground("w");
        
        #navigation_layout.addWidget(navigation_plot, 0, 0);
        #navigation_layout.addWidget(navigation_status_label, 1, 0);
        
        self.navigation_graph = navigation_plot.plot(self.test_x, self.test_y, pen=pyqtgraph.mkPen(255,0,0));
        
        #self.update_timer = QTimer();
        #self.update_timer.setInterval(600);
        #self.update_timer.timeout.connect(self.update_plot);
        #self.update_timer.start();
        
    
    #def update_plot(self):
    #    self.test_x.append(self.test_x.__len__() + 1);
    #    self.test_y.append(self.test_x.__len__() + 4);
    #    self.navigation_graph.setData(self.test_x, self.test_y);
        
manager_application = QApplication([]);
main_window = MainWindow();
main_window.show();
manager_application.exec();        