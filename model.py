from datetime import date
from dataclasses import dataclass
from typing import Optional, Union


@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    quantity: int


class Batch:
    def __init__(
        self, ref: str, sku: str, qty: int, eta: Optional[date] = None
    ) -> None:
        self.__reference = ref
        self.__sku = sku
        self.__eta = eta
        self.__available_quantity = qty

    @property
    def reference(self):
        return self.__reference

    @property
    def sku(self):
        return self.__sku

    @property
    def eta(self):
        return self.__eta

    @property
    def available_quantity(self):
        return self.__available_quantity

    def can_allocate(self, line: OrderLine) -> Union[ValueError, bool]:
        if line.sku is not self.sku:
            return ValueError("The sku doesn't match")
        elif line.quantity > self.available_quantity:
            return ValueError("The order line asks for more quantity than available")
        return True

    def allocate(self, line: OrderLine) -> int:
        if error := self.can_allocate(line) is not True:
            raise error
        self.__available_quantity -= line.quantity
