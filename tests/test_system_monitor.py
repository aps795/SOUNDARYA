"""Unit tests for System Hardware Telemetry Monitor."""

import unittest
from app.system.monitor import system_monitor, SystemMetrics


class TestSystemMonitor(unittest.TestCase):
    def test_system_metrics_reading(self) -> None:
        metrics = system_monitor.get_metrics()
        self.assertIsInstance(metrics, SystemMetrics)
        self.assertGreaterEqual(metrics.cpu_percent, 0)
        self.assertLessEqual(metrics.cpu_percent, 100)
        self.assertGreaterEqual(metrics.ram_percent, 0)
        self.assertLessEqual(metrics.ram_percent, 100)
        self.assertGreater(metrics.ram_total_gb, 0)
        self.assertGreaterEqual(metrics.disk_free_gb, 0)
        self.assertGreaterEqual(metrics.uptime_hours, 0)

    def test_system_summary_speech(self) -> None:
        summary_hinglish = system_monitor.get_summary_text(language="Hinglish")
        self.assertIn("System status", summary_hinglish)
        self.assertIn("CPU", summary_hinglish)

        summary_english = system_monitor.get_summary_text(language="English")
        self.assertIn("System status is normal", summary_english)


if __name__ == "__main__":
    unittest.main()
