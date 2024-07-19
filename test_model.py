from datetime import date, timedelta

import pytest

from model import Batch, OrderLine, allocate


today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


@pytest.fixture
def default_batch():
    return Batch(ref="dummy-batch", sku="product-1", qty=10, eta=tomorrow)


def test_allocating_to_a_batch_reduces_the_available_quantity(default_batch: Batch):
    order_line = OrderLine("order-00001", sku=default_batch.sku, quantity=5)

    current_batch_quantity = default_batch.available_quantity
    default_batch.allocate(order_line)

    assert default_batch.available_quantity == (
        current_batch_quantity - order_line.quantity
    ), "Quantity doesn't match"


def test_can_allocate_if_available_greater_than_required(default_batch: Batch):
    order_line = OrderLine("order-00001", sku=default_batch.sku, quantity=5)
    assert not isinstance(default_batch.can_allocate(order_line), ValueError)


def test_cannot_allocate_if_available_smaller_than_required(default_batch: Batch):
    order_line = OrderLine(
        "order-00001",
        sku=default_batch.sku,
        quantity=default_batch.available_quantity + 1,
    )
    assert isinstance(default_batch.can_allocate(order_line), ValueError)


def test_can_allocate_if_available_equal_to_required(default_batch: Batch):
    order_line = OrderLine(
        "order-00001", sku=default_batch.sku, quantity=default_batch.available_quantity
    )
    assert not isinstance(default_batch.can_allocate(order_line), ValueError)


def test_cannot_allocate_if_skus_do_not_match(default_batch: Batch):
    order_line = OrderLine("order-00001", sku="product-2", quantity=5)
    assert isinstance(default_batch.can_allocate(order_line), ValueError)


def test_prefers_warehouse_batches_to_shipments():
    stock_in_warehouse = Batch("batch-01", "chair", 1, None)
    stock_in_shipping = Batch("batch-02", "chair", 1, tomorrow) 
    order = OrderLine("order-01", "chair", 1)

    allocate(order, [stock_in_warehouse, stock_in_shipping])

    assert stock_in_warehouse.available_quantity == 0
    assert stock_in_shipping.available_quantity == 1


def test_prefers_earlier_batches():
    stock_arrives_today = Batch("batch-01", "chair", 1, today)
    stock_arrives_tomorrow = Batch("batch-02", "chair", 1, tomorrow)
    stock_arrives_later = Batch("batch-02", "chair", 1, later) 
    order = OrderLine("order-01", "chair", 1)

    allocate(order, [stock_arrives_today, stock_arrives_tomorrow, stock_arrives_later])

    assert stock_arrives_today.available_quantity == 0
    assert stock_arrives_tomorrow.available_quantity == 1
    assert stock_arrives_later.available_quantity == 1


def test_returns_allocated_batch_ref():
    stock_arrives_today = Batch("batch-01", "chair", 1, today)
    stock_arrives_tomorrow = Batch("batch-02", "chair", 1, tomorrow)
    stock_arrives_later = Batch("batch-02", "chair", 1, later) 
    order = OrderLine("order-01", "chair", 1)

    allocated_batch = allocate(order, [stock_arrives_today, stock_arrives_tomorrow, stock_arrives_later])

    assert allocated_batch == stock_arrives_today


def test_can_only_deallocate_allocated_lines(default_batch: Batch):
    order_line = OrderLine("order-00001", sku=default_batch.sku, quantity=5)
    assert isinstance(default_batch.can_deallocate(order_line), ValueError)
    default_batch.allocate(order_line)
    assert not isinstance(default_batch.can_deallocate(order_line), ValueError)


def test_allocation_is_idempotent(default_batch: Batch):
    order_line = OrderLine("order-00001", sku=default_batch.sku, quantity=5)
    default_batch.allocate(order_line)
    current_qty = default_batch.available_quantity
    with pytest.raises(ValueError):
        default_batch.allocate(order_line)
    assert current_qty == default_batch.available_quantity
