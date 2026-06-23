from __future__ import annotations
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPixmap
from PyQt6.QtWidgets import QLabel

# Получение корневой папки проекта (нужно для корректных путей к файлам)
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent

# Преобразует относительный путь к изображению в абсолютный используется для корректной загрузки фото из CSV
def resolve_photo_path(photo: str) -> Path:
    path = Path(photo)
    return path if path.is_absolute() else project_root() / path

# Создаёт заглушку изображения, если файл фото отсутствует отображает серый прямоугольник с текстом "No photo"
def create_placeholder_pixmap(size: tuple[int, int] = (120, 90), text: str = "No photo") -> QPixmap:
    w, h = size
    pixmap = QPixmap(w, h)
    pixmap.fill(QColor("#E0E0E0"))
    painter = QPainter(pixmap)
    painter.setPen(QColor("#555555"))
    painter.drawRect(0, 0, w - 1, h - 1)
    painter.drawText(pixmap.rect(), int(Qt.AlignmentFlag.AlignCenter), text)
    painter.end()
    return pixmap

# Устанавливает изображение товара в QLabel если файл отсутствует — подставляется заглушка
def set_photo_on_label(label: QLabel, photo: str, width: int = 120, height: int = 90) -> None:
    path = resolve_photo_path(photo)
    pixmap = QPixmap(str(path))
    if pixmap.isNull():
        pixmap = create_placeholder_pixmap((width, height))
    else:
        pixmap = pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    label.setPixmap(pixmap)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
