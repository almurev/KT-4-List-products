from __future__ import annotations
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPixmap, QIcon
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from forms.product_form import ProductForm
from models.product import Product
from services.product_repository import ProductRepository
from utils.image_tools import resolve_photo_path, create_placeholder_pixmap

# Страница списка товаров внутри главного окна.
# Отвечает только за отображение интерфейса таблицы и передачу событий в MainWindow
class ProductListPage(QWidget):
    def __init__(self, parent: "MainWindow"):
        super().__init__()
        self.main_window = parent
        self._build_ui()

    # Создаёт интерфейс страницы списка товаров: таблица, кнопки управления и настройки отображения
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        title = QLabel("Список товаров")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        top = QHBoxLayout()
        self.add_button = QPushButton("Добавить товар")
        self.refresh_button = QPushButton("Обновить")
        top.addWidget(self.add_button); top.addWidget(self.refresh_button); top.addStretch(1)
        layout.addLayout(top)

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(["Фото", "Наименование", "Категория", "Описание", "Производитель", "Поставщик", "Цена", "Ед.", "Склад / Скидка"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        self.table.cellDoubleClicked.connect(self._edit_current_row)
        layout.addWidget(self.table)

        bottom = QHBoxLayout()
        self.delete_button = QPushButton("Удалить товар")
        bottom.addWidget(self.delete_button); bottom.addStretch(1)
        layout.addLayout(bottom)

        self.add_button.clicked.connect(self.main_window.open_add_form)
        self.refresh_button.clicked.connect(self.main_window.refresh_products)
        self.delete_button.clicked.connect(self.main_window.delete_selected_product)

        self.table.setStyleSheet("QTableWidget { gridline-color: #bbb; } QHeaderView::section { background: #efefef; padding: 8px; font-weight: 600; }")

    def _edit_current_row(self, row: int, _column: int) -> None:
        item = self.table.item(row, 0)
        if item:
            self.main_window.open_edit_form(item.data(Qt.ItemDataRole.UserRole))

    def selected_article(self) -> str | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

# Главное окно приложения: отвечает за отображение списка товаров,
# взаимодействие с репозиторием и обработку всех действий пользователя (добавление, редактирование, удаление)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.repo = ProductRepository(Path(__file__).resolve().parent.parent / "products.csv")
        self.setWindowTitle("КТ4 — Учёт товаров")
        self.resize(1400, 780)
        self.list_page = ProductListPage(self)
        self.setCentralWidget(self.list_page)
        self.apply_global_style()
        self.refresh_products()

    def apply_global_style(self) -> None:
        self.setStyleSheet("""
            QMainWindow { background: white; }
            QWidget { font-size: 14px; }
            #pageTitle { font-size: 24px; font-weight: 700; margin: 8px 0 14px; }
            QPushButton { background: #f2f2f2; border: 1px solid #b7b7b7; border-radius: 8px; padding: 8px 14px; }
            QPushButton:hover { background: #e8e8e8; }
            QPushButton:pressed { background: #dcdcdc; }
        """)

    # Загружает все товары из CSV через репозиторий и обновляет таблицу
    def refresh_products(self) -> None:
        self.products = self.repo.load_all()
        table = self.list_page.table
        table.setRowCount(len(self.products))
        for row, product in enumerate(self.products):
            self._fill_row(row, product)

    # Формирует одну строку таблицы: заполняет текстовые данные и изображение товара
    def _fill_row(self, row: int, product: Product) -> None:
        table = self.list_page.table
        photo_item = QTableWidgetItem(product.article)
        photo_item.setData(Qt.ItemDataRole.UserRole, product.article)
        pix = QPixmap(str(resolve_photo_path(product.photo)))
        if pix.isNull():
            pix = create_placeholder_pixmap((120, 90), "No photo")
        photo_item.setIcon(QIcon(pix.scaled(84, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)))
        table.setItem(row, 0, photo_item)

        values = [product.name, product.category, product.description, product.manufacturer, product.supplier, f"{product.price:.2f} ₽", product.unit, f"{product.stock_quantity} / {product.discount:g}%"]
        for col, value in enumerate(values, start=1):
            item = QTableWidgetItem(value)
            item.setToolTip(value)
            table.setItem(row, col, item)

        self._apply_row_colors(row, product)
        self._apply_price_display(row, product)
        table.setRowHeight(row, 82)

    # Применяет цветовую логику строки:
    # - голубой, если товара нет на складе
    # - зелёный, если высокая скидка
    # - белый по умолчанию
    def _apply_row_colors(self, row: int, product: Product) -> None:
        table = self.list_page.table
        bg = QColor("white")
        if product.is_out_of_stock:
            bg = QColor("#ADD8E6")
        elif product.is_high_discount:
            bg = QColor("#2E8B57")
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if not item:
                item = QTableWidgetItem("")
                table.setItem(row, col, item)
            item.setBackground(QBrush(bg))
            item.setForeground(QBrush(QColor("black")))

    # Отвечает за отображение цены:
    # если есть скидка — показывает старую перечёркнутую и новую цену
    # иначе отображает обычную цену
    def _apply_price_display(self, row: int, product: Product) -> None:
        table = self.list_page.table

        if product.has_discount:
            old_price = product.price
            new_price = product.final_price

            table.takeItem(row, 6)

            price_label = QLabel(
                f"""
                <span style="color:red;text-decoration:line-through;">
                    {old_price:.2f} ₽
                </span>
                <span style="color:black;">
                    → {new_price:.2f} ₽
                </span>
                """
            )

            if product.stock_quantity == 0:
                price_label.setStyleSheet("""
                    background-color: #ADD8E6;
                """)
            elif product.discount > 15:
                price_label.setStyleSheet("""
                    background-color: #2E8B57;
                """)
            else:
                price_label.setStyleSheet("""
                    background-color: transparent;
                """)

            price_label.setContentsMargins(5, 0, 5, 0)
            table.setCellWidget(row, 6, price_label)

        else:
            table.removeCellWidget(row, 6)

            price_item = QTableWidgetItem(f"{product.price:.2f} ₽")
            table.setItem(row, 6, price_item)

    # Открывает форму добавления товара и сохраняет данные в CSV после подтверждения
    def open_add_form(self) -> None:
        form = ProductForm(self)
        if form.exec() == QDialog.DialogCode.Accepted:
            article = self.repo.next_article()
            self.repo.add(form.get_product(article))
            self.refresh_products()

    # Открывает форму редактирования выбранного товара
    # Артикул передаётся как ключ для поиска в репозитории
    def open_edit_form(self, article: str) -> None:
        product = self.repo.get_by_article(article)
        if not product:
            QMessageBox.warning(self, "Ошибка", "Товар не найден.")
            return
        form = ProductForm(self, product=product)
        form.article_edit.setText(product.article)
        if form.exec() == QDialog.DialogCode.Accepted:
            self.repo.update(form.get_product(product.article))
            self.refresh_products()

    # Удаляет выбранный товар после подтверждения пользователя
    # и обновляет таблицу
    def delete_selected_product(self) -> None:
        article = self.list_page.selected_article()
        if not article:
            QMessageBox.information(self, "Удаление", "Выберите товар для удаления.")
            return
        reply = QMessageBox.question(self, "Подтверждение", f"Удалить товар {article}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.repo.delete(article)
            self.refresh_products()
