"""
Tests for Payment classes.
"""

import pytest
from datetime import datetime
from src.parking.payment import Payment, CashPayment, CardPayment, MobileMoneyPayment
from src.parking.enums import PaymentStatus


class TestPayment:
    """Test cases for Payment ABC and its subclasses."""

    def test_payment_cannot_be_instantiated_directly(self):
        """Test that Payment ABC cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Payment("PAY001", 100.0)

    def test_cash_payment_initialization(self):
        """Test cash payment initialization."""
        payment = CashPayment("PAY001", 100.0, 150.0)
        assert payment.payment_id == "PAY001"
        assert payment.amount == 100.0
        assert payment.amount_tendered == 150.0
        assert payment.payment_method == "cash"
        assert payment.payment_status == PaymentStatus.PENDING

    def test_cash_payment_process_success(self):
        """Test successful cash payment processing."""
        payment = CashPayment("PAY001", 100.0, 150.0)
        payment.process_payment()
        assert payment.is_paid() is True
        assert payment.payment_status == PaymentStatus.PAID
        assert payment.change == 50.0

    def test_cash_payment_process_insufficient_funds(self):
        """Test cash payment processing with insufficient funds."""
        payment = CashPayment("PAY001", 100.0, 50.0)
        with pytest.raises(ValueError):
            payment.process_payment()
        assert payment.payment_status == PaymentStatus.FAILED

    def test_cash_payment_exact_amount(self):
        """Test cash payment with exact amount (no change)."""
        payment = CashPayment("PAY001", 100.0, 100.0)
        payment.process_payment()
        assert payment.is_paid() is True
        assert payment.change == 0.0

    def test_card_payment_initialization(self):
        """Test card payment initialization."""
        payment = CardPayment("PAY002", 100.0, "1234")
        assert payment.payment_id == "PAY002"
        assert payment.amount == 100.0
        assert payment.last_four_digits == "1234"
        assert payment.payment_method == "card"
        assert payment.payment_status == PaymentStatus.PENDING

    def test_card_payment_process(self):
        """Test card payment processing."""
        payment = CardPayment("PAY002", 100.0, "1234")
        payment.process_payment()
        assert payment.is_paid() is True
        assert payment.payment_status == PaymentStatus.PAID

    def test_mobile_money_payment_initialization(self):
        """Test mobile money payment initialization."""
        payment = MobileMoneyPayment("PAY003", 100.0, "555-0100", "TXN12345")
        assert payment.payment_id == "PAY003"
        assert payment.amount == 100.0
        assert payment.phone_number == "555-0100"
        assert payment.transaction_reference == "TXN12345"
        assert payment.payment_method == "mobile_money"
        assert payment.payment_status == PaymentStatus.PENDING

    def test_mobile_money_payment_process(self):
        """Test mobile money payment processing."""
        payment = MobileMoneyPayment("PAY003", 100.0, "555-0100", "TXN12345")
        payment.process_payment()
        assert payment.is_paid() is True
        assert payment.payment_status == PaymentStatus.PAID

    def test_payment_is_paid_false_before_processing(self):
        """Test that is_paid returns False before processing."""
        payment = CashPayment("PAY001", 100.0, 150.0)
        assert payment.is_paid() is False

    def test_payment_receipt_generation(self):
        """Test receipt generation for payments."""
        payment = CashPayment("PAY001", 100.0, 150.0)
        payment.process_payment()
        receipt = payment.generate_receipt()

        assert receipt["payment_id"] == "PAY001"
        assert receipt["amount"] == 100.0
        assert receipt["payment_method"] == "cash"
        assert receipt["payment_status"] == "paid"
        assert "amount_tendered" in receipt
        assert "change" in receipt

    def test_card_payment_receipt(self):
        """Test card payment receipt includes card details."""
        payment = CardPayment("PAY002", 100.0, "1234")
        payment.process_payment()
        receipt = payment.generate_receipt()

        assert "card_last_four" in receipt
        assert receipt["card_last_four"] == "1234"

    def test_mobile_money_payment_receipt(self):
        """Test mobile money payment receipt includes phone and reference."""
        payment = MobileMoneyPayment("PAY003", 100.0, "555-0100", "TXN12345")
        payment.process_payment()
        receipt = payment.generate_receipt()

        assert "phone_number" in receipt
        assert receipt["phone_number"] == "555-0100"
        assert "transaction_reference" in receipt
        assert receipt["transaction_reference"] == "TXN12345"

    def test_payment_date_default(self):
        """Test that payment date defaults to current time."""
        before = datetime.now()
        payment = CashPayment("PAY001", 100.0, 150.0)
        after = datetime.now()
        assert before <= payment.payment_date <= after

    def test_payment_date_custom(self):
        """Test that custom payment date can be set."""
        custom_date = datetime(2024, 1, 1, 12, 0, 0)
        payment = CashPayment("PAY001", 100.0, 150.0, custom_date)
        assert payment.payment_date == custom_date

    def test_polymorphic_process_payment(self):
        """Test polymorphic behavior of process_payment across all types."""
        cash = CashPayment("PAY001", 100.0, 150.0)
        card = CardPayment("PAY002", 100.0, "1234")
        mobile = MobileMoneyPayment("PAY003", 100.0, "555-0100", "TXN12345")

        # All should process without isinstance checks
        cash.process_payment()
        card.process_payment()
        mobile.process_payment()

        assert cash.is_paid()
        assert card.is_paid()
        assert mobile.is_paid()
