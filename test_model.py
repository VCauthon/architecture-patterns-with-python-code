from datetime import date, timedelta
import pytest

from model import Batch, OrderLine


today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


@pytest.fixture
def default_batch():
    return Batch(
        ref="dummy-batch",
        sku="product-1",
        qty=10,
        eta=tomorrow)  


def test_allocating_to_a_batch_reduces_the_available_quantity(default_batch: Batch):
    order_line = OrderLine("order-00001", sku=default_batch.sku, quantity=5)

    current_batch_quantity = default_batch.available_quantity
    default_batch.allocate(order_line)

    assert default_batch.available_quantity == (
        current_batch_quantity - order_line.quantity
    ), "Quantity doesn't match"


def test_can_allocate_if_available_greater_than_required(default_batch: Batch):
    order_line = OrderLine("order-00001", sku=default_batch.sku, quantity=5)
    assert default_batch.can_allocate(order_line) is True


def test_cannot_allocate_if_available_smaller_than_required(default_batch: Batch):
    order_line = OrderLine("order-00001", sku=default_batch.sku, quantity=default_batch.available_quantity + 1)
    assert isinstance(default_batch.can_allocate(order_line), ValueError)


def test_cannot_allocate_if_different_sku(default_batch: Batch):
    order_line = OrderLine("order-00001", sku="product-2", quantity=5)
    assert isinstance(default_batch.can_allocate(order_line), ValueError)


def test_can_allocate_if_available_equal_to_required(default_batch: Batch):
    order_line = OrderLine(
        "order-00001", sku=default_batch.sku, quantity=default_batch.available_quantity
    )
    assert default_batch.can_allocate(order_line) is True


def test_can_deallocate_allocated_lines(default_batch: Batch):
    pytest.fail("todo")


def test_allocation_is_idempotent(default_batch: Batch):
    pass


def test_prefers_warehouse_batches_to_shipments(default_batch: Batch):
    pytest.fail("todo")


def test_prefers_earlier_batches(default_batch: Batch):
    pytest.fail("todo")
