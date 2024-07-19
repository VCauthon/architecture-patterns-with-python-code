from datetime import date
from dataclasses import dataclass
from typing import Optional, NewType, List


Quantity = NewType("Quantity", int)
Sku = NewType("Sku", str)
Reference = NewType("Reference", str)


@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    quantity: Quantity


class Batch:
    def __init__(
        self, ref: Reference, sku: Sku, qty: Quantity, eta: Optional[date] = None
    ) -> None:
        self.__reference = ref
        self.__sku = sku
        self.__available_quantity = qty
        self.__eta = eta
        self.__allocated_lines = set()

    def __gt__(self, other: 'Batch') -> bool:
        if self.__eta is None:
            return False
        elif other.__eta is None:
            return True
        return self.__eta > other.__eta

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

    def allocate(self, line: OrderLine) -> None:
        if error := self.can_allocate(line):
            raise error
        self.__available_quantity -= line.quantity
        self.__allocated_lines.add(line)

    def can_allocate(self, line: OrderLine) -> Optional[ValueError]:
        if line.sku is not self.__sku:
            return ValueError("The sku doesn't match")
        elif line.quantity > self.__available_quantity:
            return ValueError("The order line asks for more quantity than available")
        elif line in self.__allocated_lines:
            return ValueError("The line has already been allocated")

    def deallocate(self, line: OrderLine) -> None:
        if error := self.can_deallocate(line):
            raise error

        self.__available_quantity += line.quantity
        self.__allocated_lines.remove(line)

    def can_deallocate(self, line: OrderLine) -> Optional[ValueError]:
        if line not in self.__allocated_lines:
            return ValueError("The order line hasn't been allocated")


def allocate(line: OrderLine, batches: List[Batch]) -> Batch:
    sel_batch = next(
        batch for batch in sorted(batches) if not isinstance(batch.can_allocate(line), ValueError)
    )

    sel_batch.allocate(line)
    return sel_batch
