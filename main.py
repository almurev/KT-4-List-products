from __future__ import annotations
import sys
from PyQt6.QtWidgets import QApplication
from forms.main_window import MainWindow

def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("КТ4 — Учёт товаров")
    window = MainWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
