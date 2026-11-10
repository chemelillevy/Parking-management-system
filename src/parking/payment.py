"""
Payment classes for the Parking Management System.

Demonstrates:
- Abstraction: Payment is an abstract base class
- Inheritance: CashPayment, CardPayment, MobileMoneyPayment inherit from Payment
- Polymorphism: Each subclass overrides process_payment() with its own behavior
- Encapsulation: Private attributes with property getters
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any
from src.parking.enums import PaymentStatus


class Payment(ABC):
    """
    Abstract base class representing a payment settlement.

    Attributes:
        payment_id: Unique identifier for the payment
        amount: The amount to be paid
        payment_method: The method of payment (cash, card, mobile money)
        payment_date: When the payment was made
        payment_status: Current status of the payment
    """

    def __init__(self, payment_id: str, amount: float, payment_date: Optional[datetime] = None) -> None:
        """
        Initialize a payment.

        Args:
            payment_id: Unique identifier for the payment
            amount: The amount to be paid
            payment_date: When the payment was made (defaults to now if not provided)
        """
        self._payment_id = payment_id
        self._amount = amount
        self._payment_method = self._get_payment_method()
        self._payment_date = payment_date if payment_date is not None else datetime.now()
        self._payment_status = PaymentStatus.PENDING

    @abstractmethod
    def _get_payment_method(self) -> str:
        """
        Return the payment method for this subclass.

        Each subclass must implement this to define its method.
        """
        pass

    @abstractmethod
    def process_payment(self) -> None:
        """
        Process the payment with subclass-specific behavior.

        Each subclass implements its own payment processing logic.
        """
        pass

    @property
    def payment_id(self) -> str:
        """Get the payment ID."""
        return self._payment_id

    @property
    def amount(self) -> float:
        """Get the payment amount."""
        return self._amount

    @property
    def payment_method(self) -> str:
        """Get the payment method."""
        return self._payment_method

    @property
    def payment_date(self) -> datetime:
        """Get the payment date."""
        return self._payment_date

    @property
    def payment_status(self) -> PaymentStatus:
        """Get the payment status."""
        return self._payment_status

    def is_paid(self) -> bool:
        """
        Check if the payment has been successfully paid.

        Returns:
            True if status is PAID, False otherwise
        """
        return self._payment_status == PaymentStatus.PAID

    def generate_receipt(self) -> Dict[str, Any]:
        """
        Generate a receipt with payment details.

        Returns:
            Dictionary containing payment receipt information
        """
        return {
            "payment_id": self._payment_id,
            "amount": self._amount,
            "payment_method": self._payment_method,
            "payment_date": self._payment_date.isoformat(),
            "payment_status": self._payment_status.value,
        }

    def __repr__(self) -> str:
        """Return a string representation of the payment."""
        return f"{self.__class__.__name__}(id='{self._payment_id}', amount={self._amount}, status={self._payment_status.value})"

    def __str__(self) -> str:
        """Return a user-friendly string representation."""
        return f"{self._payment_method} payment of {self._amount} (Status: {self._payment_status.value})"


class CashPayment(Payment):
    """
    Cash payment implementation.

    Handles cash payments with amount tendered and change calculation.
    """

    def __init__(
        self,
        payment_id: str,
        amount: float,
        amount_tendered: float,
        payment_date: Optional[datetime] = None,
    ) -> None:
        """
        Initialize a cash payment.

        Args:
            payment_id: Unique identifier for the payment
            amount: The amount to be paid
            amount_tendered: The amount of cash provided by the customer
            payment_date: When the payment was made (defaults to now)
        """
        super().__init__(payment_id, amount, payment_date)
        self._amount_tendered = amount_tendered
        self._change = 0.0

    def _get_payment_method(self) -> str:
        """Return 'cash' as the payment method."""
        return "cash"

    def process_payment(self) -> None:
        """
        Process the cash payment.

        Calculates change and sets status to PAID if amount_tendered >= amount.
        Otherwise sets status to FAILED.

        Raises:
            ValueError: If amount_tendered is less than the required amount
        """
        if self._amount_tendered < self._amount:
            self._payment_status = PaymentStatus.FAILED
            raise ValueError(f"Insufficient cash tendered: {self._amount_tendered} < {self._amount}")

        self._change = self._amount_tendered - self._amount
        self._payment_status = PaymentStatus.PAID

    @property
    def amount_tendered(self) -> float:
        """Get the amount tendered."""
        return self._amount_tendered

    @property
    def change(self) -> float:
        """Get the change to be returned."""
        return self._change

    def generate_receipt(self) -> Dict[str, Any]:
        """
        Generate a receipt with cash-specific details.

        Returns:
            Dictionary containing payment receipt information including change
        """
        receipt = super().generate_receipt()
        receipt["amount_tendered"] = self._amount_tendered
        receipt["change"] = self._change
        return receipt


class CardPayment(Payment):
    """
    Card payment implementation.

    Handles card payments with last four digits tracking.
    """

    def __init__(
        self,
        payment_id: str,
        amount: float,
        last_four_digits: str,
        payment_date: Optional[datetime] = None,
    ) -> None:
        """
        Initialize a card payment.

        Args:
            payment_id: Unique identifier for the payment
            amount: The amount to be paid
            last_four_digits: Last four digits of the card used
            payment_date: When the payment was made (defaults to now)
        """
        super().__init__(payment_id, amount, payment_date)
        self._last_four_digits = last_four_digits

    def _get_payment_method(self) -> str:
        """Return 'card' as the payment method."""
        return "card"

    def process_payment(self) -> None:
        """
        Process the card payment.

        Simulates card processing and sets status to PAID.
        In a real system, this would integrate with a payment gateway.
        """
        # Simulate card processing - always succeeds in this implementation
        self._payment_status = PaymentStatus.PAID

    @property
    def last_four_digits(self) -> str:
        """Get the last four digits of the card."""
        return self._last_four_digits

    def generate_receipt(self) -> Dict[str, Any]:
        """
        Generate a receipt with card-specific details.

        Returns:
            Dictionary containing payment receipt information including card details
        """
        receipt = super().generate_receipt()
        receipt["card_last_four"] = self._last_four_digits
        return receipt


class MobileMoneyPayment(Payment):
    """
    Mobile money payment implementation.

    Handles mobile money payments with phone number and transaction reference.
    """

    def __init__(
        self,
        payment_id: str,
        amount: float,
        phone_number: str,
        transaction_reference: str,
        payment_date: Optional[datetime] = None,
    ) -> None:
        """
        Initialize a mobile money payment.

        Args:
            payment_id: Unique identifier for the payment
            amount: The amount to be paid
            phone_number: Phone number used for the payment
            transaction_reference: Transaction reference from the mobile money provider
            payment_date: When the payment was made (defaults to now)
        """
        super().__init__(payment_id, amount, payment_date)
        self._phone_number = phone_number
        self._transaction_reference = transaction_reference

    def _get_payment_method(self) -> str:
        """Return 'mobile_money' as the payment method."""
        return "mobile_money"

    def process_payment(self) -> None:
        """
        Process the mobile money payment.

        Simulates mobile money processing and sets status to PAID.
        In a real system, this would integrate with a mobile money API.
        """
        # Simulate mobile money processing - always succeeds in this implementation
        self._payment_status = PaymentStatus.PAID

    @property
    def phone_number(self) -> str:
        """Get the phone number used."""
        return self._phone_number

    @property
    def transaction_reference(self) -> str:
        """Get the transaction reference."""
        return self._transaction_reference

    def generate_receipt(self) -> Dict[str, Any]:
        """
        Generate a receipt with mobile money-specific details.

        Returns:
            Dictionary containing payment receipt information including phone and reference
        """
        receipt = super().generate_receipt()
        receipt["phone_number"] = self._phone_number
        receipt["transaction_reference"] = self._transaction_reference
        return receipt
