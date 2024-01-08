from PyQt5.QtWidgets import QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget, QLabel, QLineEdit, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
from network_scanner import start_network_scan

class ScannerThread(QThread):
    """
    Thread class to run network scanning in the background to keep the GUI responsive.
    """
    update_signal = pyqtSignal(str)

    def __init__(self, ip_range, start_port, end_port):
        super().__init__()
        self.ip_range = ip_range
        self.start_port = start_port
        self.end_port = end_port

    def run(self):
        """
        Overridden run method that executes when the thread starts. It triggers the network scan.
        """
        start_network_scan(self.ip_range, self.start_port, self.end_port, self.update_signal.emit)

class MainWindow(QMainWindow):
    """
    Main window class for the network scanner application.
    """
    def __init__(self):
        super().__init__()

        # Set main window properties
        self.setWindowTitle("Network Scanner")
        self.setGeometry(300, 300, 600, 400)

        # Initialize the layout
        layout = QVBoxLayout()

        # Initialize and configure input fields
        self.ip_range_input = QLineEdit()
        self.ip_range_input.setPlaceholderText("Enter IP Range (e.g., 192.168.1.0/24)")

        self.port_range_input = QLineEdit()
        self.port_range_input.setPlaceholderText("Enter Port Range (e.g., 1-100)")

        # Initialize and configure the scan button
        self.scan_button = QPushButton("Start Scan")
        self.scan_button.clicked.connect(self.start_scan)

        # Initialize and configure the results text area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)

        # Add widgets to the layout
        layout.addWidget(QLabel("IP Range:"))
        layout.addWidget(self.ip_range_input)
        layout.addWidget(QLabel("Port Range:"))
        layout.addWidget(self.port_range_input)
        layout.addWidget(self.scan_button)
        layout.addWidget(QLabel("Results:"))
        layout.addWidget(self.results_text)

        # Set the layout to the central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Initialize and add Save Results button
        self.save_button = QPushButton("Save Results")
        self.save_button.clicked.connect(self.save_results)
        layout.addWidget(self.save_button)

    def start_scan(self):
        """
        Starts the network scan when the scan button is clicked.
        """
        ip_range = self.ip_range_input.text()
        port_range = self.port_range_input.text()
        start_port, end_port = map(int, port_range.split('-'))

        self.scan_thread = ScannerThread(ip_range, start_port, end_port)
        self.scan_thread.update_signal.connect(self.update_results)
        self.scan_thread.start()

    def update_results(self, message):
        """
        Appends new scan results to the results text area.
        """
        self.results_text.append(message)

    def save_results(self):
        """
        Saves the scan results to a file, chosen by the user through a file dialog.
        """
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Results", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            scan_results = self.results_text.toPlainText().strip().split('\n')
            scan_results = [line.split(" is open on ") for line in scan_results if " is open on " in line]
            scan_results = [(ip_port[1], ip_port[0]) for ip_port in scan_results]  # Swap to match (ip, port) order
            self.save_results_to_file(file_name, scan_results)

    @staticmethod
    def save_results_to_file(file_name, scan_results):
        """
        Static method to save given scan results to a specified file.

        Args:
        file_name (str): The file path where results will be saved.
        scan_results (list): List of tuples containing IP and port data.
        """
        with open(file_name, 'w') as file:
            for ip, port in scan_results:
                file.write(f"{ip} open on {port}\n")
