from __future__ import annotations
import csv
from pathlib import Path
from typing import List, Optional
from models.product import Product


class ProductRepository:
    def __init__(self, csv_path: str | Path):
        self.csv_path = Path(csv_path)

    def ensure_exists(self) -> None:
        if self.csv_path.exists():
            return
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        with self.csv_path.open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["article", "photo", "name", "category", "description", "manufacturer", "supplier", "price", "unit", "stock_quantity", "discount"])

    # Чтение из CSV
    def load_all(self) -> List[Product]:
        self.ensure_exists()
        products: List[Product] = []
        with self.csv_path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row:
                    products.append(Product.from_dict(row))
        return products

    # Сохранение в CSV (берёт список Product -> вызывает to_dict() -> записывает обратно в CSV)
    def save_all(self, products: List[Product]) -> None:
        self.ensure_exists()
        with self.csv_path.open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["article", "photo", "name", "category", "description", "manufacturer", "supplier", "price", "unit", "stock_quantity", "discount"])
            writer.writeheader()
            for product in products:
                writer.writerow(product.to_dict())

    def next_article(self, products: Optional[List[Product]] = None) -> str:
        if products is None:
            products = self.load_all()
        max_num = 0
        for product in products:
            if product.article.startswith("P") and product.article[1:].isdigit():
                max_num = max(max_num, int(product.article[1:]))
        return f"P{max_num + 1:03d}"

    # Метод добавления, обновления и удаления товарной записи
    def add(self, product: Product) -> None:
        products = self.load_all()
        products.append(product)
        self.save_all(products)

    def update(self, updated_product: Product) -> None:
        products = self.load_all()
        self.save_all([updated_product if p.article == updated_product.article else p for p in products])

    def delete(self, article: str) -> None:
        products = self.load_all()
        self.save_all([p for p in products if p.article != article])

    # Метод на создание артикула после добавления товара
    def get_by_article(self, article: str) -> Product | None:
        for product in self.load_all():
            if product.article == article:
                return product
        return None
