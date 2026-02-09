"""
Monitoring tab for system resource monitoring - PyQt6 version.

Displays real-time CPU, RAM, disk, battery, and network statistics.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QProgressBar, QTextEdit, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont
from typing import Optional, Dict, Any

from src.utils.logger import get_logger
from src.core.monitoring import MonitoringService
from src.core.performance_profiler import PerformanceProfiler

logger = get_logger("monitoring_tab")

# Conversion constants
BYTES_TO_MB = 1024**2


class MonitoringTab(QWidget):
    """System monitoring tab with real-time resource display using PyQt6."""
    
    # Signals for thread-safe UI updates
    cpu_updated = pyqtSignal(dict)
    ram_updated = pyqtSignal(dict)
    disk_updated = pyqtSignal(dict)
    battery_updated = pyqtSignal(dict)
    network_updated = pyqtSignal(dict)

    def __init__(self, parent=None, main_window=None) -> None:
        """Initialize monitoring tab."""
        super().__init__(parent)
        
        self.main_window = main_window
        self.monitoring_service = MonitoringService()
        self.performance_profiler = PerformanceProfiler()
        self.is_monitoring = False

        # Create UI
        self._create_ui()

        # Connect signals to update methods
        self.cpu_updated.connect(self._update_cpu_display)
        self.ram_updated.connect(self._update_ram_display)
        self.disk_updated.connect(self._update_disk_display)
        self.battery_updated.connect(self._update_battery_display)
        self.network_updated.connect(self._update_network_display)

        # Start monitoring automatically
        self.start_monitoring()
        
        # Set initial status
        if self.main_window:
            self.main_window.update_status("Ready")

        logger.info("Monitoring tab initialized (PyQt6)")

    def _create_ui(self) -> None:
        """Create complete UI layout."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Control panel
        control_layout = self._create_control_panel()
        main_layout.addLayout(control_layout)

        # Monitoring displays in grid (2x3)
        grid_widget = self._create_monitoring_displays()
        main_layout.addWidget(grid_widget, 1)  # Stretch factor 1

    def _create_control_panel(self) -> QHBoxLayout:
        """Create control panel with start/stop buttons."""
        control_layout = QHBoxLayout()

        # Title
        title = QLabel("System Monitoring")
        title.setProperty("heading", True)
        font = title.font()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)
        control_layout.addWidget(title)

        # Spacer
        control_layout.addStretch()

        # Start/Stop button
        self.toggle_button = QPushButton("Stop Monitoring")
        self.toggle_button.setMinimumWidth(150)
        self.toggle_button.clicked.connect(self.toggle_monitoring)
        control_layout.addWidget(self.toggle_button)
        
        # Performance Profile button
        self.perf_profile_btn = QPushButton("Run Performance Profile")
        self.perf_profile_btn.setMinimumWidth(200)
        self.perf_profile_btn.clicked.connect(self._run_performance_profile)
        control_layout.addWidget(self.perf_profile_btn)

        return control_layout

    def _create_monitoring_displays(self) -> QWidget:
        """Create monitoring display panels in 2x3 grid layout."""
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(10)

        # Row 0: CPU (left) and RAM (right)
        self._create_cpu_display(grid_layout, 0, 0)
        self._create_ram_display(grid_layout, 0, 1)

        # Row 1: Disk (left) and Network (right)
        self._create_disk_display(grid_layout, 1, 0)
        self._create_network_display(grid_layout, 1, 1)

        # Row 2: Battery (left), second column can be used for future expansion
        self._create_battery_display(grid_layout, 2, 0)

        # Make columns equally sized
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        
        # Make rows equally sized
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)
        grid_layout.setRowStretch(2, 1)

        return grid_widget

    def _create_cpu_display(self, grid_layout: QGridLayout, row: int, col: int) -> None:
        """Create CPU monitoring display."""
        cpu_group = QGroupBox("CPU")
        cpu_layout = QVBoxLayout(cpu_group)

        # CPU usage
        self.cpu_usage_label = QLabel("Usage: ---%")
        font = self.cpu_usage_label.font()
        font.setPointSize(14)
        self.cpu_usage_label.setFont(font)
        cpu_layout.addWidget(self.cpu_usage_label)

        # CPU cores
        self.cpu_cores_label = QLabel("Cores: ---")
        cpu_layout.addWidget(self.cpu_cores_label)

        # CPU frequency
        self.cpu_freq_label = QLabel("Frequency: --- MHz")
        cpu_layout.addWidget(self.cpu_freq_label)

        # Progress bar
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMinimum(0)
        self.cpu_progress.setMaximum(100)
        self.cpu_progress.setValue(0)
        self.cpu_progress.setTextVisible(True)
        cpu_layout.addWidget(self.cpu_progress)

        cpu_layout.addStretch()
        grid_layout.addWidget(cpu_group, row, col)

    def _create_ram_display(self, grid_layout: QGridLayout, row: int, col: int) -> None:
        """Create RAM monitoring display."""
        ram_group = QGroupBox("RAM")
        ram_layout = QVBoxLayout(ram_group)

        # RAM usage
        self.ram_usage_label = QLabel("Usage: ---%")
        font = self.ram_usage_label.font()
        font.setPointSize(14)
        self.ram_usage_label.setFont(font)
        ram_layout.addWidget(self.ram_usage_label)

        # RAM used/total
        self.ram_details_label = QLabel("--- GB / --- GB")
        ram_layout.addWidget(self.ram_details_label)

        # Available
        self.ram_available_label = QLabel("Available: --- GB")
        ram_layout.addWidget(self.ram_available_label)

        # Progress bar
        self.ram_progress = QProgressBar()
        self.ram_progress.setMinimum(0)
        self.ram_progress.setMaximum(100)
        self.ram_progress.setValue(0)
        self.ram_progress.setTextVisible(True)
        ram_layout.addWidget(self.ram_progress)

        ram_layout.addStretch()
        grid_layout.addWidget(ram_group, row, col)

    def _create_disk_display(self, grid_layout: QGridLayout, row: int, col: int) -> None:
        """Create disk monitoring display."""
        disk_group = QGroupBox("Disk")
        disk_layout = QVBoxLayout(disk_group)

        # Disk info text
        self.disk_info_text = QTextEdit()
        self.disk_info_text.setReadOnly(True)
        self.disk_info_text.setMaximumHeight(150)
        self.disk_info_text.setPlainText("Loading disk information...")
        disk_layout.addWidget(self.disk_info_text)

        grid_layout.addWidget(disk_group, row, col)

    def _create_battery_display(self, grid_layout: QGridLayout, row: int, col: int) -> None:
        """Create battery monitoring display."""
        battery_group = QGroupBox("Battery")
        battery_layout = QVBoxLayout(battery_group)

        # Battery status
        self.battery_status_label = QLabel("Status: ---")
        font = self.battery_status_label.font()
        font.setPointSize(14)
        self.battery_status_label.setFont(font)
        battery_layout.addWidget(self.battery_status_label)

        # Battery level
        self.battery_level_label = QLabel("Level: ---%")
        battery_layout.addWidget(self.battery_level_label)

        # Time remaining
        self.battery_time_label = QLabel("Time: ---")
        battery_layout.addWidget(self.battery_time_label)

        # Progress bar
        self.battery_progress = QProgressBar()
        self.battery_progress.setMinimum(0)
        self.battery_progress.setMaximum(100)
        self.battery_progress.setValue(0)
        self.battery_progress.setTextVisible(True)
        battery_layout.addWidget(self.battery_progress)

        battery_layout.addStretch()
        grid_layout.addWidget(battery_group, row, col)

    def _create_network_display(self, grid_layout: QGridLayout, row: int, col: int) -> None:
        """Create network monitoring display."""
        network_group = QGroupBox("Network")
        network_layout = QVBoxLayout(network_group)

        # Network details text
        self.net_details_text = QTextEdit()
        self.net_details_text.setReadOnly(True)
        self.net_details_text.setPlainText("Loading network information...")
        network_layout.addWidget(self.net_details_text)

        grid_layout.addWidget(network_group, row, col)

    def start_monitoring(self) -> None:
        """Start monitoring service."""
        if self.is_monitoring:
            return

        logger.info("Starting monitoring")
        
        # Register callbacks - these will emit signals for thread-safe updates
        self.monitoring_service.register_callback("cpu", lambda data: self.cpu_updated.emit(data))
        self.monitoring_service.register_callback("ram", lambda data: self.ram_updated.emit(data))
        self.monitoring_service.register_callback("disk", lambda data: self.disk_updated.emit(data))
        self.monitoring_service.register_callback("battery", lambda data: self.battery_updated.emit(data))
        self.monitoring_service.register_callback("network", lambda data: self.network_updated.emit(data))

        # Start monitoring
        self.monitoring_service.start()
        self.is_monitoring = True
        self.toggle_button.setText("Stop Monitoring")
        
        # Update status
        if self.main_window:
            self.main_window.update_status("Monitoring active")

    def stop_monitoring(self) -> None:
        """Stop monitoring service."""
        if not self.is_monitoring:
            return

        logger.info("Stopping monitoring")
        self.monitoring_service.stop()
        self.is_monitoring = False
        self.toggle_button.setText("Start Monitoring")
        
        # Update status
        if self.main_window:
            self.main_window.update_status("Monitoring stopped")

    def toggle_monitoring(self) -> None:
        """Toggle monitoring on/off."""
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def _update_cpu_display(self, data: Dict[str, Any]) -> None:
        """Update CPU display with new data (runs in GUI thread)."""
        if "error" in data:
            return

        try:
            percent = data.get("percent", 0)
            physical_cores = data.get("physical_cores", 0)
            logical_cores = data.get("logical_cores", 0)
            freq = data.get("frequency", {}).get("current", 0)

            self.cpu_usage_label.setText(f"Usage: {percent:.1f}%")
            self.cpu_cores_label.setText(f"Cores: {physical_cores} physical, {logical_cores} logical")
            self.cpu_freq_label.setText(f"Frequency: {freq:.0f} MHz")
            self.cpu_progress.setValue(int(percent))
            
        except Exception as e:
            logger.debug(f"CPU display update error: {e}")

    def _update_ram_display(self, data: Dict[str, Any]) -> None:
        """Update RAM display with new data (runs in GUI thread)."""
        if "error" in data:
            return

        try:
            percent = data.get("percent", 0)
            used_gb = data.get("used", 0) / (1024**3)
            total_gb = data.get("total", 0) / (1024**3)
            available_gb = data.get("available", 0) / (1024**3)

            self.ram_usage_label.setText(f"Usage: {percent:.1f}%")
            self.ram_details_label.setText(f"{used_gb:.2f} GB / {total_gb:.2f} GB")
            self.ram_available_label.setText(f"Available: {available_gb:.2f} GB")
            self.ram_progress.setValue(int(percent))
            
        except Exception as e:
            logger.debug(f"RAM display update error: {e}")

    def _update_disk_display(self, data: Dict[str, Any]) -> None:
        """Update disk display with new data (runs in GUI thread)."""
        if "error" in data:
            return

        try:
            partitions = data.get("partitions", [])
            
            info_text = ""
            for partition in partitions:
                device = partition.get("device", "Unknown")
                mountpoint = partition.get("mountpoint", "")
                total_gb = partition.get("total", 0) / (1024**3)
                used_gb = partition.get("used", 0) / (1024**3)
                free_gb = partition.get("free", 0) / (1024**3)
                percent = partition.get("percent", 0)
                fstype = partition.get("fstype", "")
                
                info_text += f"{device} ({fstype})\n"
                info_text += f"  Mount: {mountpoint}\n"
                info_text += f"  Used: {used_gb:.2f} GB / {total_gb:.2f} GB ({percent:.1f}%)\n"
                info_text += f"  Free: {free_gb:.2f} GB\n\n"

            self.disk_info_text.setPlainText(info_text.strip())
            
        except Exception as e:
            logger.debug(f"Disk display update error: {e}")

    def _update_battery_display(self, data: Dict[str, Any]) -> None:
        """Update battery display with new data (runs in GUI thread)."""
        if "error" in data:
            return

        try:
            percent = data.get("percent", 0)
            power_plugged = data.get("power_plugged", False)
            secs_left = data.get("secsleft", None)

            # Status
            if power_plugged:
                status = "Plugged In (Charging)" if percent < 100 else "Plugged In (Fully Charged)"
            else:
                status = "On Battery"

            self.battery_status_label.setText(f"Status: {status}")
            self.battery_level_label.setText(f"Level: {percent:.0f}%")

            # Time remaining
            if secs_left and secs_left > 0:
                hours = secs_left // 3600
                minutes = (secs_left % 3600) // 60
                self.battery_time_label.setText(f"Time: {hours}h {minutes}m remaining")
            elif power_plugged:
                self.battery_time_label.setText("Time: Charging")
            else:
                self.battery_time_label.setText("Time: Calculating...")

            self.battery_progress.setValue(int(percent))
            
        except Exception as e:
            logger.debug(f"Battery display update error: {e}")

    def _update_network_display(self, data: Dict[str, Any]) -> None:
        """Update network display with enhanced information (runs in GUI thread)."""
        if "error" in data:
            return

        try:
            bytes_sent = data.get("bytes_sent", 0) / BYTES_TO_MB
            bytes_recv = data.get("bytes_recv", 0) / BYTES_TO_MB
            interfaces = data.get("interfaces", [])
            
            # Build detailed network info text
            info_text = "Network Statistics:\n"
            info_text += f"  Sent: {bytes_sent:.2f} MB\n"
            info_text += f"  Received: {bytes_recv:.2f} MB\n\n"
            
            # Find active interface with details
            active_interface = None
            mac_address = None
            local_ip = None
            subnet_mask = None
            
            for iface in interfaces:
                if iface.get("is_up", False):
                    active_interface = iface.get("name", "Unknown")
                    # Extract MAC address and IP info
                    for addr in iface.get("addresses", []):
                        addr_str = str(addr.get("family", ""))
                        address = addr.get("address", "")
                        
                        # MAC address
                        if "packet" in addr_str.lower() or "link" in addr_str.lower():
                            mac_address = address
                        # IPv4 address
                        elif "AF_INET" in addr_str and ":" not in address:
                            if not local_ip:
                                local_ip = address
                                subnet_mask = addr.get("netmask", "N/A")
                    
                    if active_interface:
                        break
            
            # Get additional network details
            public_ip = data.get("public_ip", "Fetching...")
            default_gateway = data.get("default_gateway", "N/A")
            dns_servers = data.get("dns_servers", [])
            dhcp_enabled = data.get("dhcp_enabled", False)
            behind_nat = data.get("behind_nat", False)
            
            if not local_ip:
                local_ip = data.get("local_ip", "N/A")
            
            info_text += "Active Interface:\n"
            if active_interface:
                info_text += f"  Name: {active_interface}\n"
                if mac_address:
                    info_text += f"  MAC: {mac_address}\n"
                
                # Find speed for this interface
                for iface in interfaces:
                    if iface.get("name") == active_interface:
                        speed = iface.get("speed", 0)
                        if speed > 0:
                            info_text += f"  Speed: {speed} Mbps\n"
                        info_text += f"  Status: Connected\n"
                        break
            else:
                info_text += "  No active interface detected\n"
            
            info_text += "\nIP Addressing:\n"
            info_text += f"  Local IP: {local_ip or 'N/A'}\n"
            info_text += f"  Public IP: {public_ip}\n"
            if subnet_mask and subnet_mask != "N/A":
                info_text += f"  Subnet Mask: {subnet_mask}\n"
            if default_gateway:
                info_text += f"  Gateway: {default_gateway}\n"
            
            info_text += "\nNetwork Configuration:\n"
            info_text += f"  DHCP: {'Enabled' if dhcp_enabled else 'Disabled/Unknown'}\n"
            
            if dns_servers:
                info_text += f"  DNS Servers:\n"
                for dns in dns_servers[:3]:
                    info_text += f"    - {dns}\n"
            else:
                info_text += f"  DNS Servers: N/A\n"
            
            info_text += f"  Network Type: {'Behind NAT' if behind_nat else 'Direct/Unknown'}\n"
            
            self.net_details_text.setPlainText(info_text)
            
        except Exception as e:
            logger.debug(f"Network display update error: {e}")

    def _run_performance_profile(self) -> None:
        """Run comprehensive performance profile."""
        logger.info("User initiated performance profiling")
        
        # Show info dialog
        QMessageBox.information(
            self,
            "Performance Profile",
            "Running performance analysis...\nThis will take a minute or two.",
            QMessageBox.StandardButton.Ok
        )
        
        # Disable button and update text
        self.perf_profile_btn.setEnabled(False)
        self.perf_profile_btn.setText("⏳ Please wait...")
        
        # Run profiling in a separate thread
        # For now, show a placeholder (full implementation would use QThread)
        QTimer.singleShot(1000, self._show_performance_placeholder)

    def _show_performance_placeholder(self) -> None:
        """Show placeholder for performance profiling (to be fully implemented)."""
        QMessageBox.information(
            self,
            "Performance Profile",
            "Performance profiling feature will be fully implemented in the next phase.\n\n"
            "This will include:\n"
            "• CPU profiling over 5 seconds\n"
            "• Memory usage analysis\n"
            "• Top processes by CPU and memory\n"
            "• System bottleneck detection\n"
            "• Detailed recommendations",
            QMessageBox.StandardButton.Ok
        )
        
        # Reset button
        self.perf_profile_btn.setEnabled(True)
        self.perf_profile_btn.setText("Run Performance Profile")
