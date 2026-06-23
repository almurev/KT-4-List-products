from __future__ import annotations
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP

# Приводим цену к типу Decimal и округляем до 2 знаков после запятой для точного расчета денег
def _money(value: float | str | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

# Модель, хранящая данные о товаре
@dataclass
class Product:
    article: str
    photo: str
    name: str
    category: str
    description: str
    manufacturer: str
    supplier: str
    price: float
    unit: str
    stock_quantity: int
    discount: float

    @property
    def final_price(self) -> float:
        base = _money(self.price)
        discount = Decimal(str(self.discount))
        final = base * (Decimal("1") - discount / Decimal("100"))
        return float(max(final, Decimal("0.00")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    # Наличие скидки
    @property
    def has_discount(self) -> bool:
        return float(self.discount) > 0

    # Большая скидка > 15%
    @property
    def is_high_discount(self) -> bool:
        return float(self.discount) > 15

    # Нет товара если
    @property
    def is_out_of_stock(self) -> bool:
        return int(self.stock_quantity) == 0

    # Загрузка из CSV
    @classmethod
    def from_dict(cls, row: dict[str, str]) -> "Product":
        return cls(
            article=row["article"].strip(),
            photo=row["photo"].strip(),
            name=row["name"].strip(),
            category=row["category"].strip(),
            description=row["description"].strip(),
            manufacturer=row["manufacturer"].strip(),
            supplier=row["supplier"].strip(),
            price=float(row["price"]),
            unit=row["unit"].strip(),
            stock_quantity=int(row["stock_quantity"]),
            discount=float(row["discount"]),
        )

    # Сохранение в CSV
    def to_dict(self) -> dict[str, str]:
        data = asdict(self)
        data["price"] = f"{float(self.price):.2f}"
        data["discount"] = f"{float(self.discount):.2f}".rstrip("0").rstrip(".")
        data["stock_quantity"] = str(int(self.stock_quantity))
        return data
