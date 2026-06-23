
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from models.product import Product
from utils.image_tools import set_photo_on_label


class ProductForm(QDialog):
    CATEGORIES = ["Электроника", "Одежда", "Канцтовары", "Бытовая техника", "Другое"]
    MANUFACTURERS = ["TechNova", "NoteCraft", "AudioMax", "KeyMaster", "GameGear", "ScreenTech", "PadWorld", "WearFit", "NetWave", "PowerUp", "Другое"]

    def __init__(self, parent=None, product: Product | None = None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование товара" if product else "Добавление товара")
        self.resize(760, 650)
        self.product = product
        self.photo_path = product.photo if product else ""
        self._build_ui()
        if product:
            self._fill_from_product(product)
        else:
            self._update_final_price()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        title = QLabel(self.windowTitle())
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()

        self.article_edit = QLineEdit()
        self.article_edit.setReadOnly(True)
        self.article_edit.setPlaceholderText("Будет создан автоматически")
        form.addRow("Артикул:", self.article_edit)

        photo_row = QHBoxLayout()
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(140, 100)
        self.photo_label.setStyleSheet("border: 1px solid #999; background: #fafafa;")
        self.photo_edit = QLineEdit()
        self.photo_button = QPushButton("Выбрать фото")
        self.photo_button.clicked.connect(self._choose_photo)
        photo_row.addWidget(self.photo_label)
        photo_row.addWidget(self.photo_edit, 1)
        photo_row.addWidget(self.photo_button)
        form.addRow("Фото:", photo_row)

        self.name_edit = QLineEdit(); form.addRow("Наименование:", self.name_edit)
        self.category_combo = QComboBox(); self.category_combo.addItems(self.CATEGORIES); form.addRow("Категория:", self.category_combo)
        self.description_edit = QTextEdit(); self.description_edit.setMinimumHeight(90); form.addRow("Описание:", self.description_edit)
        self.manufacturer_combo = QComboBox(); self.manufacturer_combo.addItems(self.MANUFACTURERS); self.manufacturer_combo.setEditable(True); form.addRow("Производитель:", self.manufacturer_combo)
        self.supplier_edit = QLineEdit(); form.addRow("Поставщик:", self.supplier_edit)
        self.price_edit = QLineEdit(); self.price_edit.setPlaceholderText("0.00"); self.price_edit.setValidator(QDoubleValidator(0.0, 999999999.0, 2)); self.price_edit.textChanged.connect(self._update_final_price); form.addRow("Цена:", self.price_edit)
        self.unit_edit = QComboBox(); self.unit_edit.addItems(["шт", "уп", "кг", "л", "м", "Другое"]); self.unit_edit.setEditable(True); form.addRow("Ед. измерения:", self.unit_edit)
        self.stock_edit = QLineEdit(); self.stock_edit.setPlaceholderText("0"); self.stock_edit.setValidator(QIntValidator(0, 999999999)); form.addRow("Количество на складе:", self.stock_edit)
        self.discount_edit = QLineEdit(); self.discount_edit.setPlaceholderText("0"); self.discount_edit.setValidator(QDoubleValidator(0.0, 100.0, 2)); self.discount_edit.textChanged.connect(self._update_final_price); form.addRow("Действующая скидка (%):", self.discount_edit)
        self.final_price_edit = QLineEdit(); self.final_price_edit.setReadOnly(True); self.final_price_edit.setStyleSheet("background: #f0f0f0;"); form.addRow("Итоговая цена:", self.final_price_edit)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        self.back_button = QPushButton("Назад")
        self.save_button = QPushButton("Сохранить")
        buttons.addWidget(self.back_button); buttons.addStretch(1); buttons.addWidget(self.save_button)
        layout.addLayout(buttons)
        self.back_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self._save)

        self.setStyleSheet("""
            QWidget { font-size: 14px; }
            #pageTitle { font-size: 22px; font-weight: 700; margin: 8px 0 16px; }
            QPushButton { padding: 8px 14px; }
            QLineEdit, QComboBox, QTextEdit { padding: 6px; }
        """)

    # Заполнение формы данными товара при редактировании
    def _fill_from_product(self, p: Product) -> None:
        self.article_edit.setText(p.article)
        self.photo_edit.setText(p.photo)
        self.name_edit.setText(p.name)
        self.category_combo.setCurrentText(p.category)
        self.description_edit.setPlainText(p.description)
        self.manufacturer_combo.setCurrentText(p.manufacturer)
        self.supplier_edit.setText(p.supplier)
        self.price_edit.setText(f"{p.price:.2f}")
        self.unit_edit.setEditText(p.unit)
        self.stock_edit.setText(str(p.stock_quantity))
        self.discount_edit.setText(str(p.discount).rstrip('0').rstrip('.'))
        set_photo_on_label(self.photo_label, p.photo, 140, 100)
        self._update_final_price()

    # Выбор изображения товара через файловый диалог
    def _choose_photo(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "Выбор изображения", str(Path.cwd()), "Images (*.png *.jpg *.jpeg *.bmp *.webp);;All files (*.*)")
        if file_name:
            self.photo_path = file_name
            self.photo_edit.setText(file_name)
            set_photo_on_label(self.photo_label, file_name, 140, 100)

    @staticmethod
    def _safe_float(value: str) -> float | None:
        value = value.replace(",", ".").strip()
        if not value:
            return 0.0
        try:
            return float(value)
        except ValueError:
            return None

    # Автоматический пересчёт итоговой цены при изменении цены или скидки
    def _update_final_price(self) -> None:
        price = self._safe_float(self.price_edit.text())
        discount = self._safe_float(self.discount_edit.text())
        if price is None or discount is None or price < 0 or discount < 0:
            self.final_price_edit.setText("")
            return
        final = max(price * (1 - discount / 100), 0)
        self.final_price_edit.setText(f"{final:.2f}")

    # Проверка корректности введённых данных перед сохранением
    def _validate(self) -> tuple[bool, str]:
        if not self.name_edit.text().strip(): return False, "Введите наименование товара."
        if not self.supplier_edit.text().strip(): return False, "Введите поставщика."
        price = self._safe_float(self.price_edit.text())
        if price is None or price < 0: return False, "Цена не может быть отрицательной."
        discount = self._safe_float(self.discount_edit.text())
        if discount is None or discount < 0: return False, "Скидка не может быть отрицательной."
        if discount > 100: return False, "Скидка не может быть больше 100%."
        try:
            stock = int(self.stock_edit.text())
        except ValueError:
            return False, "Количество на складе должно быть целым числом."
        if stock < 0: return False, "Количество на складе не может быть меньше 0."
        return True, ""

    def get_product(self, article: str) -> Product:
        return Product(
            article=article,
            photo=self.photo_edit.text().strip() or self.photo_path or "img/placeholder.jpg",
            name=self.name_edit.text().strip(),
            category=self.category_combo.currentText().strip(),
            description=self.description_edit.toPlainText().strip(),
            manufacturer=self.manufacturer_combo.currentText().strip(),
            supplier=self.supplier_edit.text().strip(),
            price=float(self.price_edit.text().replace(",", ".") or 0),
            unit=self.unit_edit.currentText().strip(),
            stock_quantity=int(self.stock_edit.text()),
            discount=float(self.discount_edit.text().replace(",", ".") or 0),
        )

    # Сохранение формы: валидация и подтверждение данных пользователем
    def _save(self) -> None:
        ok, message = self._validate()
        if not ok:
            QMessageBox.warning(self, "Ошибка ввода", message)
            return
        self.accept()
