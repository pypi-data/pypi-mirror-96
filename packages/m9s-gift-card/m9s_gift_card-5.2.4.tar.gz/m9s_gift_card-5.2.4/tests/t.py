# -*- coding: utf-8 -*-
import unittest
from datetime import date

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, with_transaction
from trytond.transaction import Transaction
from decimal import Decimal
from .test_base import TestBase
from trytond.exceptions import UserError
from trytond.config import config
config.set('email', 'from', 'test@ol.in')


class TestGiftCard(TestBase):
    '''
    Test Gift Card
    '''
    module = 'gift_card'

    @with_transaction()
    def test0010_create_gift_card(self):
        """
        Create gift card
        """
        GiftCard = POOL.get('gift_card.gift_card')
        Currency = POOL.get('currency.currency')

        self.usd = Currency(
            name='US Dollar', symbol='$', code='USD',
        )
        self.usd.save()

        gift_card, = GiftCard.create([{
            'currency': self.usd.id,
            'amount': Decimal('20'),
        }])

        self.assertEqual(gift_card.state, 'draft')

    @with_transaction()
    def test0015_on_change_currency(self):
        """
        Check if currency digits are changed because of currency of gift
        card
        """
        GiftCard = POOL.get('gift_card.gift_card')
        Currency = POOL.get('currency.currency')

        self.usd = Currency(
            name='US Dollar', symbol='$', code='USD', digits=3
        )
        self.usd.save()

        gift_card = GiftCard(currency=self.usd.id)

        self.assertEqual(gift_card.on_change_with_currency_digits(), 3)

        gift_card = GiftCard(currency=None)

        self.assertEqual(gift_card.on_change_with_currency_digits(), 2)

    @with_transaction()
    def test0020_gift_card_on_processing_sale(self):
        """
        Check if gift card is being created on processing sale
        """
        Sale = POOL.get('sale.sale')
        GiftCard = POOL.get('gift_card.gift_card')
        Invoice = POOL.get('account.invoice')
        InvoiceLine = POOL.get('account.invoice.line')
        Configuration = POOL.get('gift_card.configuration')
        SaleLine = POOL.get('sale.line')

        self.setup_defaults()

        gift_card_product = self.create_product(is_gift_card=True)

        with Transaction().set_context({'company': self.company.id}):

            Configuration.create([{
                'liability_account': self._get_account_by_kind('revenue').id
            }])

            gc_price, _, = gift_card_product.gift_card_prices
            sale, = Sale.create([{
                'reference': 'Sale1',
                'sale_date': date.today(),
                'invoice_address': self.party1.addresses[0].id,
                'shipment_address': self.party1.addresses[0].id,
                'party': self.party1.id,
                'lines': [
                    ('create', [{
                        'type': 'line',
                        'quantity': 2,
                        'unit': self.uom,
                        'unit_price': 200,
                        'description': 'Test description1',
                        'product': self.product.id,
                    }, {
                        'quantity': 1,
                        'unit': self.uom,
                        'unit_price': 500,
                        'description': 'Gift Card',
                        'product': gift_card_product,
                        'gc_price': gc_price,
                    }, {
                        'type': 'comment',
                        'description': 'Test line',
                    }])
                ]

            }])

            sale_line1, = SaleLine.search([
                ('sale', '=', sale.id),
                ('product', '=', gift_card_product.id),
            ])

            sale_line2, = SaleLine.search([
                ('sale', '=', sale.id),
                ('product', '=', self.product.id),
            ])

            sale_line3, = SaleLine.search([
                ('sale', '=', sale.id),
                ('product', '=', None),
            ])

            self.assertTrue(sale_line1.is_gift_card)
            self.assertFalse(sale_line2.is_gift_card)
            self.assertFalse(sale_line3.is_gift_card)

            self.assertEqual(sale_line1.gift_card_delivery_mode, 'physical')

            # Gift card line amount is included in untaxed amount
            self.assertEqual(sale.untaxed_amount, 900)

            # Gift card line amount is included in total amount
            self.assertEqual(sale.total_amount, 900)

            Sale.quote([sale])

            self.assertEqual(sale.untaxed_amount, 900)
            self.assertEqual(sale.total_amount, 900)

            Sale.confirm([sale])

            self.assertEqual(sale.untaxed_amount, 900)
            self.assertEqual(sale.total_amount, 900)

            self.assertFalse(
                GiftCard.search([('sale_line', '=', sale_line1.id)])
            )

            self.assertFalse(Invoice.search([]))

            self.SalePayment.create([{
                'sale': sale.id,
                'amount': Decimal('1000'),
                'gateway': self.create_payment_gateway('manual'),
                'credit_account': self.party1.account_receivable.id,
            }])

            Sale.process([sale])

            self.assertEqual(sale.untaxed_amount, 900)
            self.assertEqual(sale.total_amount, 900)

            self.assertTrue(
                GiftCard.search([('sale_line', '=', sale_line1.id)])
            )

            self.assertEqual(
                GiftCard.search(
                    [('sale_line', '=', sale_line1.id)], count=True
                ), 1
            )

            self.assertEqual(Invoice.search([], count=True), 1)

            gift_card, = GiftCard.search([
                ('sale_line', '=', sale_line1.id)
            ])

            invoice, = Invoice.search([])
            line, = InvoiceLine.search([
                ('invoice', '=', invoice.id),
                ('description', '=', 'Gift Card'),
            ])
            self.assertEqual(
                line.account,
                Configuration(1).liability_account
            )

            self.assertEqual(gift_card.amount, 500)
            self.assertEqual(gift_card.state, 'active')
            self.assertEqual(gift_card.sale, sale)

            self.assertEqual(invoice.untaxed_amount, 900)
            self.assertEqual(invoice.total_amount, 900)

    @with_transaction()
    def test0021_phy_gift_card_on_processing_sale(self):
        """
        Check if physical gift card is being created on processing sale when
        invoice method is shipping
        """
        Sale = POOL.get('sale.sale')
        GiftCard = POOL.get('gift_card.gift_card')
        Invoice = POOL.get('account.invoice')
        Configuration = POOL.get('gift_card.configuration')
        SaleLine = POOL.get('sale.line')

        self.setup_defaults()

        gift_card_product = self.create_product(is_gift_card=True)

        with Transaction().set_context({'company': self.company.id}):

            Configuration.create([{
                'liability_account': self._get_account_by_kind('revenue').id
            }])

            gc_price, _, = gift_card_product.gift_card_prices
            sale, = Sale.create([{
                'reference': 'Sale1',
                'sale_date': date.today(),
                'invoice_method': 'shipment',
                'invoice_address': self.party1.addresses[0].id,
                'shipment_address': self.party1.addresses[0].id,
                'party': self.party1.id,
                'lines': [
                    ('create', [{
                        'type': 'line',
                        'quantity': 2,
                        'unit': self.uom,
                        'unit_price': 200,
                        'description': 'Test description1',
                        'product': self.product.id,
                    }, {
                        'quantity': 1,
                        'unit': self.uom,
                        'unit_price': 500,
                        'description': 'Gift Card',
                        'product': gift_card_product,
                        'gc_price': gc_price,
                    }, {
                        'type': 'comment',
                        'description': 'Test line',
                    }])
                ]

            }])

            sale_line1, = SaleLine.search([
                ('sale', '=', sale.id),
                ('product', '=', gift_card_product.id),
            ])

            sale_line2, = SaleLine.search([
                ('sale', '=', sale.id),
                ('product', '=', self.product.id),
            ])

            sale_line3, = SaleLine.search([
                ('sale', '=', sale.id),
                ('product', '=', None),
            ])

            self.assertTrue(sale_line1.is_gift_card)
            self.assertFalse(sale_line2.is_gift_card)
            self.assertFalse(sale_line3.is_gift_card)

            self.assertEqual(sale_line1.gift_card_delivery_mode, 'physical')

            # Gift card line amount is included in untaxed amount
            self.assertEqual(sale.untaxed_amount, 900)

            # Gift card line amount is included in total amount
            self.assertEqual(sale.total_amount, 900)

            Sale.quote([sale])

            self.assertEqual(sale.untaxed_amount, 900)
            self.assertEqual(sale.total_amount, 900)

            Sale.confirm([sale])

            self.assertEqual(sale.untaxed_amount, 900)
            self.assertEqual(sale.total_amount, 900)

            self.assertFalse(
                GiftCard.search([('sale_line', '=', sale_line1.id)])
            )

            self.assertFalse(Invoice.search([]))

            self.SalePayment.create([{
                'sale': sale.id,
                'amount': Decimal('1000'),
                'gateway': self.create_payment_gateway('manual'),
                'credit_account': self.party1.account_receivable.id,
            }])

            Sale.process([sale])

            self.assertEqual(sale.untaxed_amount, 900)
            self.assertEqual(sale.total_amount, 900)

            self.assertTrue(
                GiftCard.search([('sale_line', '=', sale_line1.id)])
            )

            self.assertEqual(
                GiftCard.search(
                    [('sale_line', '=', sale_line1.id)], count=True
                ), 1
            )

            self.assertEqual(Invoice.search([], count=True), 0)

            gift_card, = GiftCard.search([
                ('sale_line', '=', sale_line1.id)
            ])

            self.assertEqual(gift_card.amount, 500)
            self.assertEqual(gift_card.state, 'active')
            self.assertEqual(gift_card.sale, sale)

    @with_transaction()
    def test0022_virtual_gift_card_on_processing_sale(self):
        """
        Check if virtual gift card is being created on processing sale
        """
        Sale = POOL.get('sale.sale')
        GiftCard = POOL.get('gift_card.gift_card')
        Invoice = POOL.get('account.invoice')
        InvoiceLine = POOL.get('account.invoice.line')
        Configuration = POOL.get('gift_card.configuration')
        SaleLine = POOL.get('sale.line')

        self.setup_defaults()

        gift_card_product = self.create_product(
            type='service',
            mode='virtual',
            is_gift_card=True
        )

        with Transaction().set_context({'company': self.company.id}):

            Configuration.create([{
                'liability_account': self._get_account_by_kind('revenue').id
            }])

            gc_price, _, = gift_card_product.gift_card_prices
            sale, = Sale.create([{
                'reference': 'Sale1',
                'sale_date': date.today(),
                'invoice_method': 'shipment',
                'invoice_address': self.party1.addresses[0].id,
                'shipment_address': self.party1.addresses[0].id,
                'party': self.party1.id,
                'lines': [
                    ('create', [{
                        'quantity': 1,
                        'unit': self.uom,
                        'unit_price': 500,
                        'description': 'Gift Card',
                        'product': gift_card_product,
                        'gc_price': gc_price,
                        'recipient_email': 'test@example.com',
                    }, {
                        'type': 'comment',
                        'description': 'Test line',
                    }])
                ]

            }])

            sale_line1, = SaleLine.search([
                ('sale', '=', sale.id),
                ('product', '=', gift_card_product.id),
            ])

            sale_line3, = SaleLine.search([
                ('sale', '=', sale.id),
                ('product', '=', None),
            ])

            self.assertTrue(sale_line1.is_gift_card)
            self.assertFalse(sale_line3.is_gift_card)

            self.assertEqual(sale_line1.gift_card_delivery_mode, 'virtual')

            # Gift card line amount is included in untaxed amount
            self.assertEqual(sale.untaxed_amount, 500)

            # Gift card line amount is included in total amount
            self.assertEqual(sale.total_amount, 500)

            Sale.quote([sale])

            self.assertEqual(sale.untaxed_amount, 500)
            self.assertEqual(sale.total_amount, 500)

            Sale.confirm([sale])

            self.assertEqual(sale.untaxed_amount, 500)
            self.assertEqual(sale.total_amount, 500)

            self.assertFalse(
                GiftCard.search([('sale_line', '=', sale_line1.id)])
            )

            self.assertFalse(Invoice.search([]))

            self.SalePayment.create([{
                'sale': sale.id,
                'amount': Decimal('1000'),
                'gateway': self.create_payment_gateway('manual'),
                'credit_account': self.party1.account_receivable.id,
            }])

            Sale.process([sale])

            self.assertEqual(sale.untaxed_amount, 500)
            self.assertEqual(sale.total_amount, 500)

            self.assertTrue(
                GiftCard.search([('sale_line', '=', sale_line1.id)])
            )

            self.assertEqual(
                GiftCard.search(
                    [('sale_line', '=', sale_line1.id)], count=True
                ), 1
            )

            self.assertEqual(Invoice.search([], count=True), 1)

            gift_card, = GiftCard.search([
                ('sale_line', '=', sale_line1.id)
            ])

            invoice, = Invoice.search([])
            line, = InvoiceLine.search([
                ('invoice', '=', invoice.id),
                ('description', '=', 'Gift Card'),
            ])
            self.assertEqual(
                line.account,
                Configuration(1).liability_account
            )

            self.assertEqual(gift_card.amount, 500)
            self.assertEqual(gift_card.state, 'active')
            self.assertEqual(gift_card.sale, sale)

            self.assertEqual(invoice.untaxed_amount, 500)
            self.assertEqual(invoice.total_amount, 500)

    @with_transaction()
    def test0025_create_gift_card_for_line(self):
        """
        Check if gift card is not create if sale line is of type line
        """
        Sale = POOL.get('sale.sale')
        SaleLine = POOL.get('sale.line')
        GiftCard = POOL.get('gift_card.gift_card')
        Configuration = POOL.get('gift_card.configuration')

        self.setup_defaults()

        with Transaction().set_context({'company': self.company.id}):

            Configuration.create([{
                'liability_account': self._get_account_by_kind('revenue').id
            }])
            sale, = Sale.create([{
                'reference': 'Sale1',
                'sale_date': date.today(),
                'invoice_address': self.party1.addresses[0].id,
                'shipment_address': self.party1.addresses[0].id,
                'party': self.party1.id,
            }])
            sale_line, = SaleLine.create([{
                'sale': sale.id,
                'type': 'line',
                'quantity': 2,
                'unit': self.uom,
                'unit_price': 200,
                'description': 'Test description1',
                'product': self.product.id,
            }])

            self.assertFalse(
                GiftCard.search([('sale_line', '=', sale_line.id)])
            )

            sale_line.create_gift_cards()

            # No gift card is created
            self.assertFalse(
                GiftCard.search([('sale_line', '=', sale_line.id)])
            )

            sale_line3, = SaleLine.copy([sale_line])
            self.assertFalse(sale_line3.gift_cards)

    @with_transaction()
    def test0025_gift_card_on_processing_sale_without_liability_account(self):
        """
        Check if gift card is being created on processing sale when liability
        account is missing from gift card configuration
        """
        Sale = POOL.get('sale.sale')
        GiftCard = POOL.get('gift_card.gift_card')
        Invoice = POOL.get('account.invoice')

        self.setup_defaults()

        gift_card_product = self.create_product(is_gift_card=True)

        gc_price, _, = gift_card_product.gift_card_prices

        with Transaction().set_context({'company': self.company.id}):
            sale, = Sale.create([{
                'reference': 'Sale1',
                'sale_date': date.today(),
                'invoice_address': self.party1.addresses[0].id,
                'shipment_address': self.party1.addresses[0].id,
                'party': self.party1.id,
                'lines': [
                    ('create', [{
                        'type': 'line',
                        'quantity': 2,
                        'unit': self.uom,
                        'unit_price': 200,
                        'description': 'Test description1',
                        'product': self.product.id,
                    }, {
                        'quantity': 1,
                        'unit': self.uom,
                        'unit_price': 500,
                        'description': 'Test description2',
                        'product': gift_card_product,
                        'gc_price': gc_price,
                    }])
                ]

            }])

            # Gift card line amount is included in untaxed amount
            self.assertEqual(sale.untaxed_amount, 900)

            # Gift card line amount is included in total amount
            self.assertEqual(sale.total_amount, 900)

            Sale.quote([sale])
            Sale.confirm([sale])

            self.assertFalse(
                GiftCard.search([('sale_line.sale', '=', sale.id)])
            )

            self.assertFalse(Invoice.search([]))

            with self.assertRaises(UserError):
                Sale.process([sale])

    @with_transaction()
    def test0030_check_on_change_amount(self):
        """
        Check if amount is changed with quantity and unit price
        """
        SaleLine = POOL.get('sale.line')

        self.setup_defaults()

        with Transaction().set_context({'company': self.company.id}):

            # Sale line as gift card
            sale_line = SaleLine(
                unit_price=Decimal('22.56789'),
                type='line', sale=None
            )

            sale_line.on_change_is_gift_card()
            self.assertEqual(sale_line.description, None)
            self.assertEqual(sale_line.product, None)

            sale_line.is_gift_card = True
            sale_line.on_change_is_gift_card()

            self.assertEqual(sale_line.product, None)
            self.assertEqual(sale_line.description, 'Gift Card')
            self.assertNotEqual(sale_line.unit, None)

    @with_transaction()
    def test0040_gift_card_transition(self):
        """
        Check gift card transitions
        """
        GiftCard = POOL.get('gift_card.gift_card')
        Currency = POOL.get('currency.currency')

        self.usd = Currency(
            name='US Dollar', symbol='$', code='USD',
        )
        self.usd.save()

        gift_card, = GiftCard.create([{
            'currency': self.usd.id,
            'amount': Decimal('20'),
        }])

        self.assertEqual(gift_card.state, 'draft')

        # Gift card can become active in draft state
        GiftCard.activate([gift_card])

        self.assertEqual(gift_card.state, 'active')

        # Gift card can be calcelled from active state
        GiftCard.cancel([gift_card])

        self.assertEqual(gift_card.state, 'canceled')

        # Gift card can be set back to draft state once canceled
        GiftCard.draft([gift_card])

        self.assertEqual(gift_card.state, 'draft')

        # Gift card can be canceled from draft state also
        GiftCard.cancel([gift_card])

        self.assertEqual(gift_card.state, 'canceled')

    @with_transaction()
    def test0050_gift_card_sequence(self):
        """
        Check sequence is created on activating gift card
        """
        GiftCard = POOL.get('gift_card.gift_card')
        Currency = POOL.get('currency.currency')

        self.usd = Currency(
            name='US Dollar', symbol='$', code='USD',
        )
        self.usd.save()

        gift_card, = GiftCard.create([{
            'currency': self.usd.id,
            'amount': Decimal('20'),
        }])

        self.assertTrue(gift_card.number)

        number = gift_card.number
        GiftCard.activate([gift_card])
        self.assertEqual(gift_card.number, number)

        gift_card2, = GiftCard.copy([gift_card])
        self.assertNotEqual(gift_card2.number, number)

    @with_transaction()
    def test0050_authorize_gift_card_payment_gateway_valid_card(self):
        """
        Test gift card authorization
        """
        GiftCard = POOL.get('gift_card.gift_card')
        PaymentTransaction = POOL.get('payment_gateway.transaction')

        self.setup_defaults()

        with Transaction().set_context({'company': self.company.id}):

            active_gift_card, = GiftCard.create([{
                'amount': Decimal('150'),
                'number': '45671338',
                'state': 'active',
            }])

            gateway = self.create_payment_gateway()

            # Case 1:
            # Gift card available amount (150) > amount to be paid (50)
            payment_transaction = PaymentTransaction(
                description="Pay invoice using gift card",
                party=self.party1.id,
                address=self.party1.addresses[0].id,
                amount=Decimal('50'),
                currency=self.company.currency.id,
                gateway=gateway.id,
                gift_card=active_gift_card,
                credit_account=self.party1.account_receivable.id,
            )
            payment_transaction.save()

            PaymentTransaction.authorize([payment_transaction])

            self.assertEqual(payment_transaction.state, 'authorized')

            self.assertEqual(
                active_gift_card.amount_authorized, Decimal('50')
            )

            self.assertEqual(
                active_gift_card.amount_available, Decimal('100')
            )

            # Case 2: Gift card amount (100) < amount to be paid (300)
            payment_transaction = PaymentTransaction(
                description="Pay invoice using gift card",
                party=self.party1.id,
                address=self.party1.addresses[0].id,
                amount=Decimal('300'),
                currency=self.company.currency.id,
                gateway=gateway.id,
                gift_card=active_gift_card,
                credit_account=self.party1.account_receivable.id,
            )
            payment_transaction.save()

            with self.assertRaises(UserError):
                PaymentTransaction.authorize([payment_transaction])

    @with_transaction()
    def test0055_capture_gift_card(self):
        """
        Test capturing of gift card
        """
        GiftCard = POOL.get('gift_card.gift_card')
        PaymentTransaction = POOL.get('payment_gateway.transaction')

        self.setup_defaults()

        with Transaction().set_context({'company': self.company.id}):

            active_gift_card, = GiftCard.create([{
                'amount': Decimal('200'),
                'number': '45671338',
                'state': 'active',
            }])

            gateway = self.create_payment_gateway()

            self.assertEqual(
                active_gift_card.amount_captured, Decimal('0')
            )

            self.assertEqual(
                active_gift_card.amount_authorized, Decimal('0')
            )

            self.assertEqual(
                active_gift_card.amount_available, Decimal('200')
            )

            # Capture
            # Case 1
            # Gift card available amount(200) > amount to be paid (180)
            payment_transaction = PaymentTransaction(
                description="Pay using gift card",
                party=self.party1.id,
                address=self.party1.addresses[0].id,
                amount=Decimal('100'),
                currency=self.company.currency.id,
                gateway=gateway.id,
                gift_card=active_gift_card,
                credit_account=self.party1.account_receivable.id,
            )
            payment_transaction.save()

            PaymentTransaction.capture([payment_transaction])

            self.assertEqual(payment_transaction.state, 'posted')

            self.assertEqual(
                active_gift_card.amount_captured, Decimal('100')
            )
            self.assertEqual(
                active_gift_card.amount_authorized, Decimal('0')
            )

            # 200 - 100 = 100
            self.assertEqual(
                active_gift_card.amount_available, Decimal('100')
            )

            # Case 2
            # Gift card available amount (100) = amount to be paid (100)
            payment_transaction = PaymentTransaction(
                description="Pay invoice using gift card",
                party=self.party1.id,
                address=self.party1.addresses[0].id,
                amount=Decimal('100'),
                currency=self.company.currency.id,
                gateway=gateway.id,
                gift_card=active_gift_card,
                credit_account=self.party1.account_receivable.id,
            )
            payment_transaction.save()

            PaymentTransaction.capture([payment_transaction])

            self.assertEqual(payment_transaction.state, 'posted')
            self.assertEqual(
                active_gift_card.amount_captured, Decimal('200')
            )
            self.assertEqual(
                active_gift_card.amount_authorized, Decimal('0')
            )

            # 200 - 200 = 0
            self.assertEqual(
                active_gift_card.amount_available, Decimal('0')
            )
            self.assertEqual(active_gift_card.state, 'used')

            active_gift_card, = GiftCard.create([{
                'amount': Decimal('10'),
                'number': '45671339',
                'state': 'active',
            }])

            # Case 3: Gift card amount (10) < amount to be paid (100)
            payment_transaction = PaymentTransaction(
                description="Pay invoice using gift card",
                party=self.party1.id,
                address=self.party1.addresses[0].id,
                amount=Decimal('100'),
                currency=self.company.currency.id,
                gateway=gateway.id,
                gift_card=active_gift_card,
                credit_account=self.party1.account_receivable.id,
            )
            payment_transaction.save()

            with self.assertRaises(UserError):
                PaymentTransaction.capture([payment_transaction])

    @with_transaction()
    def test0057_settle_gift_card(self):
        """
        Test settlement of gift card
        """
        GiftCard = POOL.get('gift_card.gift_card')
        PaymentTransaction = POOL.get('payment_gateway.transaction')

        self.setup_defaults()

        with Transaction().set_context({'company': self.company.id}):

            active_gift_card, = GiftCard.create([{
                'amount': Decimal('200'),
                'number': '45671338',
                'state': 'active',
            }])

            gateway = self.create_payment_gateway()

            # Authorization of gift card
            # Case 1: Gift card available amount > amount to be paid
            payment_transaction = PaymentTransaction(
                description="Pay using gift card",
                party=self.party1.id,
                address=self.party1.addresses[0].id,
                amount=Decimal('100'),
                currency=self.company.currency.id,
                gateway=gateway.id,
                gift_card=active_gift_card,
                credit_account=self.party1.account_receivable.id,
            )
            payment_transaction.save()

            PaymentTransaction.authorize([payment_transaction])

            self.assertEqual(
                active_gift_card.amount_captured, Decimal('0')
            )

            self.assertEqual(
                active_gift_card.amount_authorized, Decimal('100')
            )

            # 200 - 100 = 100
            self.assertEqual(
                active_gift_card.amount_available, Decimal('100')
            )

            # Settlement
            # Case 1: Gift card amount (100) > amount to be settled (50)
            payment_transaction = PaymentTransaction(
                description="Pay using gift card",
                party=self.party1.id,
                address=self.party1.addresses[0].id,
                amount=Decimal('50'),
                currency=self.company.currency.id,
                gateway=gateway.id,
                gift_card=active_gift_card,
                credit_account=self.party1.account_receivable.id,
            )
            payment_transaction.save()

            PaymentTransaction.authorize([payment_transaction])

            self.assertEqual(
                active_gift_card.amount_captured, Decimal('0')
            )

            self.assertEqual(
                active_gift_card.amount_authorized, Decimal('150')
            )

            # 100 - 50 = 50
            self.assertEqual(
                active_gift_card.amount_available, Decimal('50')
            )

            PaymentTransaction.settle([payment_transaction])

            self.assertEqual(payment_transaction.state, 'posted')

            self.assertEqual(
                active_gift_card.amount_captured, Decimal('50')
            )
            self.assertEqual(
                active_gift_card.amount_authorized, Decimal('100')
            )

            # 200 - 100 - 50 = 50
            self.assertEqual(
                active_gift_card.amount_available, Decimal('50')
            )

    @with_transaction()
    def test0060_payment_gateway_methods_and_providers(self):
        """
        Tests gateway methods
        """
        PaymentGateway = POOL.get('payment_gateway.gateway')

        self.setup_defaults()

        gateway = PaymentGateway(
            provider='self',
        )
        self.assertTrue(gateway.get_methods())
        self.assertTrue(('gift_card', 'Gift Card') in gateway.get_methods())

        gateway = PaymentGateway(
            provider='authorize.net',
        )
        self.assertFalse(gateway.get_methods())

    @with_transaction()
    def test0070_gift_card_amount(self):
        """
        Check authorized, captured and available amount fro gift card
        """
        GiftCard = POOL.get('gift_card.gift_card')
        PaymentTransaction = POOL.get('payment_gateway.transaction')

        self.setup_defaults()

        with Transaction().set_context({'company': self.company.id}):

            active_gift_card, = GiftCard.create([{
                'amount': Decimal('200'),
                'number': '45671338',
                'state': 'active',
            }])

            gateway = self.create_payment_gateway()

            # Payment transactions in authorized state
            payment_transaction1 = PaymentTransaction(
                description="Payment Transaction 1",
                party=self.party1.id,
                address=self.party1.addresses[0].id,
                amount=Decimal('70'),
                currency=self.company.currency.id,
                gateway=gateway.id,
                gift_card=active_gift_card,
                credit_account=self.party1.account_receivable.id,
            )
            payment_transaction1.save()

            PaymentTransaction.authorize([payment_transaction1])

            payment_transaction2 = PaymentTransaction(
                description="Payment Transaction 2",
                party=self.party1.id,
                address=self.party1.addresses[0].id,
                amount=Decimal('20'),
                currency=self.company.currency.id,
                gateway=gateway.id,
                gift_card=active_gift_card,
                credit_account=self.party1.account_receivable.id,
            )
            payment_transaction2.save()

            PaymentTransaction.authorize([payment_transaction2])

            # Payment transactions being captured
            payment_transaction3 = PaymentTransaction(
                description="Payment Transaction 3",
                party=self.party1.id,
                address=self.party1.addresses[0].id,
                amount=Decimal('10'),
                currency=self.company.currency.id,
                gateway=gateway.id,
                gift_card=active_gift_card,
                credit_account=self.party1.account_receivable.id,
            )
            payment_transaction3.save()

            PaymentTransaction.capture([payment_transaction3])

            payment_transaction4 = PaymentTransaction(
                description="Payment Transaction 4",
                party=self.party1.id,
                address=self.party1.addresses[0].id,
                amount=Decimal('20'),
                currency=self.company.currency.id,
                gateway=gateway.id,
                gift_card=active_gift_card,
                credit_account=self.party1.account_receivable.id,
            )
            payment_transaction4.save()

            PaymentTransaction.capture([payment_transaction4])

        self.assertEqual(active_gift_card.amount_authorized, 90)
        self.assertEqual(active_gift_card.amount_captured, 30)
        self.assertEqual(active_gift_card.amount_available, 80)

    @with_transaction()
    def test0080_test_gift_card_report(self):
        """
        Test Gift Card report
        """
        GiftCard = POOL.get('gift_card.gift_card')
        GiftCardReport = POOL.get('gift_card.gift_card', type='report')

        self.setup_defaults()

        with Transaction().set_context({'company': self.company.id}):

            gift_card, = GiftCard.create([{
                'amount': Decimal('200'),
                'number': '45671338',
                'state': 'active',
            }])

            val = GiftCardReport.execute([gift_card.id], {})

            self.assertTrue(val)
            # Assert report name
            self.assertEqual(val[3], 'Gift Card')

    @with_transaction()
    def test0090_test_gift_card_deletion(self):
        """
        Test that Gift Card should not be deleted in active state
        """
        GiftCard = POOL.get('gift_card.gift_card')

        self.setup_defaults()

        with Transaction().set_context({'company': self.company.id}):

            gift_card, = GiftCard.create([{
                'amount': Decimal('200'),
                'number': '45671338',
                'state': 'active',
            }])

            with self.assertRaises(Exception):
                GiftCard.delete([gift_card])

            # Try to delete gift card in some other state and it will
            # be deleted
            gift_card, = GiftCard.create([{
                'amount': Decimal('200'),
                'number': '45671339',
                'state': 'draft',
            }])

            GiftCard.delete([gift_card])

    @with_transaction()
    def test0100_send_virtual_gift_cards(self):
        """
        Check if virtual gift cards are sent through email
        """
        Sale = POOL.get('sale.sale')
        GiftCard = POOL.get('gift_card.gift_card')
        Invoice = POOL.get('account.invoice')
        Configuration = POOL.get('gift_card.configuration')
        SaleLine = POOL.get('sale.line')
        EmailQueue = POOL.get('email.queue')

        self.setup_defaults()

        gift_card_product = self.create_product(
            type='service', mode='virtual', is_gift_card=True
        )

        with Transaction().set_context({'company': self.company.id}):

            Configuration.create([{
                'liability_account': self._get_account_by_kind('revenue').id
            }])
            gc_price, _, = gift_card_product.gift_card_prices
            sale, = Sale.create([{
                'reference': 'Sale1',
                'sale_date': date.today(),
                'invoice_address': self.party1.addresses[0].id,
                'shipment_address': self.party1.addresses[0].id,
                'party': self.party1.id,
                'lines': [
                    ('create', [{
                        'type': 'line',
                        'quantity': 2,
                        'unit': self.uom,
                        'unit_price': 200,
                        'description': 'Test description1',
                        'product': self.product.id,
                    }, {
                        'quantity': 1,
                        'unit': self.uom,
                        'unit_price': 500,
                        'description': 'Gift Card',
                        'product': gift_card_product,
                        'recipient_email': 'test@gift_card.com',
                        'recipient_name': 'John Doe',
                        'gc_price': gc_price.id
                    }, {
                        'type': 'comment',
                        'description': 'Test line',
                    }])
                ]

            }])

            gift_card_line, = SaleLine.search([
                ('sale', '=', sale.id),
                ('product', '=', gift_card_product.id),
            ])

            self.assertEqual(
                gift_card_line.gift_card_delivery_mode, 'virtual'
            )

            Sale.quote([sale])

            Sale.confirm([sale])

            # No gift card yet
            self.assertFalse(
                GiftCard.search([('sale_line', '=', gift_card_line.id)])
            )

            # No Email is being sent yet
            self.assertFalse(
                EmailQueue.search([
                    ('to_addrs', '=', gift_card_line.recipient_email),
                ])
            )

            self.SalePayment.create([{
                'sale': sale.id,
                'amount': Decimal('1000'),
                'gateway': self.create_payment_gateway('manual'),
                'credit_account': self.party1.account_receivable.id,
            }])

            Sale.process([sale])

            # Gift card is created
            self.assertTrue(
                GiftCard.search([('sale_line', '=', gift_card_line.id)])
            )

            self.assertEqual(
                GiftCard.search(
                    [('sale_line', '=', gift_card_line.id)], count=True
                ), 1
            )

            self.assertEqual(Invoice.search([], count=True), 1)

            gift_card, = GiftCard.search([
                ('sale_line', '=', gift_card_line.id)
            ])

            self.assertEqual(
                gift_card.recipient_email, gift_card_line.recipient_email
            )

            self.assertEqual(
                gift_card.recipient_name, gift_card_line.recipient_name
            )

            # Email is being sent
            self.assertTrue(
                EmailQueue.search([
                    ('to_addrs', '=', gift_card_line.recipient_email),
                ])
            )

    @with_transaction()
    def test0110_test_sending_email_multiple_times(self):
        """
        Test that email should not be sent multiple times for gift card
        """
        GiftCard = POOL.get('gift_card.gift_card')
        EmailQueue = POOL.get('email.queue')
        Sale = POOL.get('sale.sale')
        SaleLine = POOL.get('sale.line')

        self.setup_defaults()

        with Transaction().set_context({'company': self.company.id}):
            gift_card_product = self.create_product(
                type='service', mode='virtual', is_gift_card=True,
            )

            gc_price, _, = gift_card_product.gift_card_prices

            sale, = Sale.create([{
                'reference': 'Sale1',
                'sale_date': date.today(),
                'invoice_address': self.party1.addresses[0].id,
                'shipment_address': self.party1.addresses[0].id,
                'party': self.party1.id,
                'lines': [
                    ('create', [{
                        'type': 'line',
                        'quantity': 2,
                        'unit': self.uom,
                        'unit_price': 200,
                        'description': 'Test description1',
                        'product': self.product.id,
                    }, {
                        'quantity': 1,
                        'unit': self.uom,
                        'unit_price': 500,
                        'description': 'Gift Card',
                        'product': gift_card_product,
                        'recipient_email': 'test@gift_card.com',
                        'recipient_name': 'John Doe',
                        'gc_price': gc_price.id,
                    }, {
                        'type': 'comment',
                        'description': 'Test line',
                    }])
                ]

            }])

            gift_card_line, = SaleLine.search([
                ('sale', '=', sale.id),
                ('product', '=', gift_card_product.id),
            ])

            gift_card, = GiftCard.create([{
                'sale_line': gift_card_line.id,
                'amount': Decimal('200'),
                'number': '45671338',
                'recipient_email': 'test@gift_card.com',
                'recipient_name': 'Jhon Doe',
            }])

            # No Email is being sent yet
            self.assertFalse(
                EmailQueue.search([
                    ('to_addrs', '=', gift_card.recipient_email),
                ])
            )
            self.assertFalse(gift_card.is_email_sent)

            # Send email by activating gift card
            GiftCard.activate([gift_card])

            # Email is being sent
            self.assertEqual(
                EmailQueue.search([
                    ('to_addrs', '=', gift_card.recipient_email),
                ], count=True), 1
            )
            self.assertTrue(gift_card.is_email_sent)

            # Try sending email again
            GiftCard.activate([gift_card])

            # Email is not sent
            self.assertEqual(
                EmailQueue.search([
                    ('to_addrs', '=', gift_card.recipient_email),
                ], count=True), 1
            )

    @with_transaction()
    def test0112_validate_product_type_and_mode(self):
        """
        Check if gift card product is service product for virtual mode and
        goods otherwise
        """
        self.setup_defaults()

        with Transaction().set_context({'company': self.company.id}):

            # Create gift card product of service type in physical mode
            with self.assertRaises(UserError):
                self.create_product(
                    type='service', mode='physical', is_gift_card=True,
                )

            # Create gift card product of service type in combined mode
            with self.assertRaises(UserError):
                self.create_product(
                    type='service', mode='combined', is_gift_card=True
                )

            # Create gift card product of goods type in virtual mode
            with self.assertRaises(UserError):
                self.create_product(
                    type='goods', mode='virtual', is_gift_card=True
                )

            # In virtual mode product can be created with service type
            # only
            service_product = self.create_product(
                type='service', mode='virtual', is_gift_card=True
            )

            self.assertTrue(service_product)

            # In physical mode product can be created with goods type
            # only
            goods_product = self.create_product(
                type='goods', mode='physical', is_gift_card=True
            )
            self.assertTrue(goods_product)

            # In combined mode product can be created with goods type only
            goods_product = self.create_product(
                type='goods', mode='combined', is_gift_card=True
            )
            self.assertTrue(goods_product)

    @with_transaction()
    def test0115_test_gc_min_max(self):
        """
        Test gift card minimum and maximum amounts on product template
        """
        self.setup_defaults()

        gift_card_product = self.create_product(
            type='service', mode='virtual', is_gift_card=True
        )

        gift_card_product.allow_open_amount = True

        with Transaction().set_context({'company': self.company.id}):

            # gc_min > gc_max
            gift_card_product.gc_min = Decimal('70')
            gift_card_product.gc_max = Decimal('60')

            with self.assertRaises(UserError):
                gift_card_product.save()

            # gc_min as negative
            gift_card_product.gc_min = Decimal('-10')
            gift_card_product.gc_max = Decimal('60')

            with self.assertRaises(UserError):
                gift_card_product.save()

            # gc_max as negative
            gift_card_product.gc_min = Decimal('10')
            gift_card_product.gc_max = Decimal('-80')

            with self.assertRaises(UserError):
                gift_card_product.save()

            # gc_min < gc_max
            gift_card_product.gc_min = Decimal('70')
            gift_card_product.gc_max = Decimal('100')

            gift_card_product.save()

    @with_transaction()
    def test0118_validate_gc_amount_on_sale_line(self):
        """
        Tests if gift card line amount lies between gc_min and gc_max defined
        on the tempalte
        """
        Sale = POOL.get('sale.sale')
        SaleLine = POOL.get('sale.line')
        Configuration = POOL.get('gift_card.configuration')

        self.setup_defaults()

        Configuration.create([{
            'liability_account': self._get_account_by_kind('revenue').id
        }])

        gift_card_product = self.create_product(
            type='goods', mode='physical', is_gift_card=True
        )

        gift_card_product.allow_open_amount = True

        gift_card_product.gc_min = Decimal('100')
        gift_card_product.gc_max = Decimal('500')

        gift_card_product.save()

        with Transaction().set_context({'company': self.company.id}):

            # gift card line amount < gc_min
            sale, = Sale.create([{
                'reference': 'Sale1',
                'sale_date': date.today(),
                'invoice_address': self.party1.addresses[0].id,
                'shipment_address': self.party1.addresses[0].id,
                'party': self.party1.id,
                'lines': [
                    ('create', [{
                        'type': 'line',
                        'quantity': 2,
                        'unit': self.uom,
                        'unit_price': 200,
                        'description': 'Test description1',
                        'product': self.product.id,
                    }, {
                        'quantity': 10,
                        'unit': self.uom,
                        'unit_price': 50,
                        'description': 'Gift Card',
                        'product': gift_card_product,
                    }, {
                        'type': 'comment',
                        'description': 'Test line',
                    }])
                ]

            }])

            Sale.quote([sale])
            Sale.confirm([sale])

            with self.assertRaises(UserError):
                Sale.process([sale])

            # gift card line amount > gc_max
            sale, = Sale.create([{
                'reference': 'Sale1',
                'sale_date': date.today(),
                'invoice_address': self.party1.addresses[0].id,
                'shipment_address': self.party1.addresses[0].id,
                'party': self.party1.id,
                'lines': [
                    ('create', [{
                        'type': 'line',
                        'quantity': 2,
                        'unit': self.uom,
                        'unit_price': 200,
                        'description': 'Test description1',
                        'product': self.product.id,
                    }, {
                        'quantity': 10,
                        'unit': self.uom,
                        'unit_price': 700,
                        'description': 'Gift Card',
                        'product': gift_card_product,
                    }, {
                        'type': 'comment',
                        'description': 'Test line',
                    }])
                ]

            }])

            Sale.quote([sale])
            Sale.confirm([sale])

            with self.assertRaises(UserError):
                Sale.process([sale])

            # gc_min <= gift card line amount <= gc_max
            sale, = Sale.create([{
                'reference': 'Sale1',
                'sale_date': date.today(),
                'invoice_address': self.party1.addresses[0].id,
                'shipment_address': self.party1.addresses[0].id,
                'party': self.party1.id,
                'lines': [
                    ('create', [{
                        'type': 'line',
                        'quantity': 2,
                        'unit': self.uom,
                        'unit_price': 200,
                        'description': 'Test description1',
                        'product': self.product.id,
                    }, {
                        'quantity': 3,
                        'unit': self.uom,
                        'unit_price': 500,
                        'description': 'Gift Card',
                        'product': gift_card_product,
                    }, {
                        'type': 'comment',
                        'description': 'Test line',
                    }])
                ]

            }])

            gift_card_line, = SaleLine.search([
                ('sale', '=', sale.id),
                ('product', '=', gift_card_product.id),
            ])

            Sale.quote([sale])
            Sale.confirm([sale])

            self.assertEqual(len(gift_card_line.gift_cards), 0)

            self.SalePayment.create([{
                'sale': sale.id,
                'amount': sale.total_amount,
                'gateway': self.create_payment_gateway('manual'),
                'credit_account': self.party1.account_receivable.id,
            }])

            Sale.process([sale])

            self.assertEqual(sale.state, 'processing')

            self.assertEqual(len(gift_card_line.gift_cards), 3)

    @with_transaction()
    def test0120_test_gift_card_prices(self):
        """
        Test gift card price
        """
        GiftCardPrice = POOL.get('product.product.gift_card.price')

        self.setup_defaults()

        gift_card_product = self.create_product(
            type='service', mode='virtual', is_gift_card=True
        )

        with self.assertRaises(UserError):
            GiftCardPrice.create([{
                'product': gift_card_product,
                'price': -90
            }])

        price, = GiftCardPrice.create([{
            'product': gift_card_product,
            'price': 90
        }])

        self.assertTrue(price)

    @with_transaction()
    def test0130_test_on_change_gc_price(self):
        """
        Tests if unit price is changed with gift card price
        """
        SaleLine = POOL.get('sale.line')

        self.setup_defaults()

        gift_card_product = self.create_product(
            type='service', mode='virtual', is_gift_card=True
        )

        gc_price, _, = gift_card_product.gift_card_prices

        sale_line = SaleLine(gc_price=gc_price)

        sale_line_ = sale_line.on_change_gc_price()

        self.assertEqual(sale_line_.unit_price, gc_price.price)

    @with_transaction()
    def test0140_pay_manually(self):
        """
        Check authorized, captured and available amount for manual method
        """
        PaymentTransaction = POOL.get('payment_gateway.transaction')

        self.setup_defaults()

        with Transaction().set_context({'company': self.company.id}):

            gateway = self.create_payment_gateway(method='manual')

            # Authorise Payment transaction
            payment_transaction = PaymentTransaction(
                description="Payment Transaction 1",
                party=self.party1.id,
                address=self.party1.addresses[0].id,
                amount=Decimal('70'),
                currency=self.company.currency.id,
                gateway=gateway.id,
                credit_account=self.party1.account_receivable.id,
            )
            payment_transaction.save()

            PaymentTransaction.authorize([payment_transaction])

            self.assertEqual(payment_transaction.state, 'authorized')

            # Settle Payment transactions
            PaymentTransaction.settle([payment_transaction])

            self.assertEqual(payment_transaction.state, 'posted')

            # Capture Payment transactions
            payment_transaction = PaymentTransaction(
                description="Payment Transaction 1",
                party=self.party1.id,
                address=self.party1.addresses[0].id,
                amount=Decimal('70'),
                currency=self.company.currency.id,
                gateway=gateway.id,
                credit_account=self.party1.account_receivable.id,
            )
            payment_transaction.save()

            PaymentTransaction.capture([payment_transaction])

            self.assertEqual(payment_transaction.state, 'posted')

    @with_transaction()
    def test0150_giftcard_redeem_wizard(self):
        """
        Tests the gift card redeem wizard.
        """
        GiftCard = POOL.get('gift_card.gift_card')
        GCRedeemWizard = POOL.get('gift_card.redeem.wizard', type='wizard')

        self.setup_defaults()

        with Transaction().set_context({'company': self.company.id}):

            active_gift_card, = GiftCard.create([{
                'amount': Decimal('150'),
                'number': '45671338',
                'state': 'draft',
            }])

            gateway = self.create_payment_gateway()

            with Transaction().set_context(
                active_ids=[active_gift_card.id]
            ):
                session_id, start_state, end_state = GCRedeemWizard.create()
                data = {
                    start_state: {
                        'name': 'start',
                        'gateway': gateway.id,
                        'description': 'This is a description.',
                        'party': self.party1.id,
                        'address': self.party1.addresses[0].id,
                        'amount': Decimal('100'),
                        'gift_card': active_gift_card.id,
                        'currency': self.usd,
                    },
                }

                # Trying to redeem GC in draft state, error is thrown.
                # Note that a domain error is thrown instead of
                # check_giftcard_state() being called.
                with self.assertRaises(UserError):
                    GCRedeemWizard.execute(session_id, data, 'redeem')

                # Test check_giftcard_state(). Draft state error is thrown.
                with self.assertRaises(UserError):
                    GCRedeemWizard(session_id).check_giftcard_state(
                        active_gift_card
                    )

                GiftCard.activate([active_gift_card])

                # Test the default_start() method.
                values = GCRedeemWizard(session_id).default_start({})
                self.assertEqual(values['gift_card'], active_gift_card.id)
                self.assertEqual(values['gateway'], gateway.id)

                # Now execute the wizard properly.
                GCRedeemWizard.execute(session_id, data, 'redeem')
                self.assertEqual(active_gift_card.state, 'active')
                self.assertEqual(
                    active_gift_card.amount_captured,
                    data[start_state]['amount']
                )

                data[start_state]['amount'] = Decimal('70')

                # Error thrown because amount available is just 50.
                with self.assertRaises(UserError):
                    GCRedeemWizard.execute(session_id, data, 'redeem')

                data[start_state]['amount'] = Decimal('-70')

                # Error thrown because amount is negative.
                with self.assertRaises(UserError):
                    GCRedeemWizard.execute(session_id, data, 'redeem')

                data[start_state]['amount'] = Decimal('50')
                GCRedeemWizard.execute(session_id, data, 'redeem')
                self.assertEqual(active_gift_card.state, 'used')
                self.assertEqual(
                    active_gift_card.amount_available, Decimal('0')
                )

                # Now the gift card has already been used, cannot run
                # wizard on it once again.
                with self.assertRaises(UserError):
                    GCRedeemWizard(session_id).check_giftcard_state(
                        active_gift_card
                    )

    @with_transaction()
    def test0200_test_sale_payment_wizard_for_gift_card(self):
        """
        Test the wizard to create sale payment for gift card
        """
        PaymentWizard = POOL.get('sale.payment.add', type="wizard")
        GiftCard = POOL.get('gift_card.gift_card')

        self.setup_defaults()

        # Active gift card
        active_gift_card, = GiftCard.create([{
            'number': 'A1234',
            'amount': Decimal('100'),
            'currency': self.company.currency.id,
            'state': 'active'
        }])

        # Inactive gift card
        inactive_gift_card, = GiftCard.create([{
            'number': 'A1567',
            'amount': Decimal('50'),
            'currency': self.company.currency.id,
            'state': 'used'
        }])

        sale, = self.Sale.create([{
            'reference': 'Test Sale',
            'currency': self.company.currency.id,
            'party': self.party1.id,
            'sale_date': date.today(),
            'company': self.company.id,
            'invoice_address': self.party1.addresses[0].id,
            'shipment_address': self.party1.addresses[0].id,
        }])

        sale_line, = self.SaleLine.create([{
            'sale': sale,
            'type': 'line',
            'quantity': 2,
            'unit': self.uom,
            'unit_price': 20000,
            'description': 'Test description',
            'product': self.product.id
        }])

        payment_wizard = PaymentWizard(PaymentWizard.create()[0])

        gift_card_gateway = self.create_payment_gateway()

        payment_wizard.payment_info.gateway = gift_card_gateway.id
        payment_wizard.payment_info.method = gift_card_gateway.method
        payment_wizard.payment_info.amount = 200
        payment_wizard.payment_info.payment_profile = None
        payment_wizard.payment_info.party = sale.party.id
        payment_wizard.payment_info.sale = sale.id
        payment_wizard.payment_info.reference = 'ref1'
        payment_wizard.payment_info.credit_account = \
            sale.party.account_receivable.id

        payment_wizard.payment_info.gift_card = active_gift_card.id
        payment_wizard.payment_info.amount = 50
        self.assertEqual(active_gift_card.amount_available, Decimal('100'))
        with Transaction().set_context(active_id=sale.id):
            payment_wizard.transition_add()

        self.assertTrue(len(sale.payments), 1)

        payment, = sale.payments
        self.assertEqual(payment.amount, Decimal('50'))
        self.assertEqual(payment.method, gift_card_gateway.method)
        self.assertEqual(payment.provider, gift_card_gateway.provider)
        self.assertEqual(payment.gift_card, active_gift_card)

    @with_transaction()
    def test0210_partial_payment_using_gift_card(self):
        """
        Check partial payment using cash, credit card and gift card
        """
        GiftCard = POOL.get('gift_card.gift_card')
        Configuration = POOL.get('gift_card.configuration')

        self.setup_defaults()

        Configuration.create([{
            'liability_account': self._get_account_by_kind('revenue').id
        }])

        # Create Active gift card
        active_gift_card, = GiftCard.create([{
            'number': 'A1234',
            'amount': Decimal('100'),
            'currency': self.company.currency.id,
            'state': 'active'
        }])

        sale, = self.Sale.create([{
            'reference': 'Test Sale',
            'currency': self.company.currency.id,
            'party': self.party1.id,
            'invoice_address': self.party1.addresses[0].id,
            'shipment_address': self.party1.addresses[0].id,
            'company': self.company.id,
            'invoice_method': 'manual',
            'shipment_method': 'manual',
            'lines': [('create', [{
                'description': 'Some item',
                'unit_price': Decimal('100'),
                'quantity': 1
            }])]
        }])

        with Transaction().set_context(use_dummy=True):
            # Create gateways
            dummy_gateway = self.create_payment_gateway(
                method='credit_card', provider='dummy'
            )
            cash_gateway = self.create_payment_gateway(
                method='manual', provider='self'
            )
            gift_card_gateway = self.create_payment_gateway(
                method='gift_card', provider='self'
            )

            # Create a payment profile
            payment_profile = self.create_payment_profile(
                self.party1, dummy_gateway
            )

            # Create sale payment for $30 in cash and $50 in card and $20
            # in gift card
            payment_gift_card, payment_cash, payment_credit_card = \
                self.SalePayment.create([{
                    'sale': sale.id,
                    'amount': Decimal('20'),
                    'gateway': gift_card_gateway,
                    'gift_card': active_gift_card.id,
                    'credit_account': self.party1.account_receivable.id,
                }, {
                    'sale': sale.id,
                    'amount': Decimal('30'),
                    'gateway': cash_gateway,
                    'credit_account': self.party1.account_receivable.id,
                }, {
                    'sale': sale.id,
                    'amount': Decimal('50'),
                    'payment_profile': payment_profile.id,
                    'gateway': dummy_gateway,
                    'credit_account': self.party1.account_receivable.id,
                }])

        self.assertTrue(
            payment_credit_card.description.startswith("Paid by Card"))
        self.assertTrue(
            payment_cash.description.startswith("Paid by Cash"))
        self.assertTrue(
            payment_gift_card.description.startswith("Paid by Gift"))

        self.assertEqual(sale.total_amount, Decimal('100'))
        self.assertEqual(sale.payment_total, Decimal('100'))
        self.assertEqual(sale.payment_available, Decimal('100'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        self.Sale.quote([sale])
        self.Sale.confirm([sale])

        with Transaction().set_context({'company': self.company.id}):
            self.Sale.proceed([sale])
            sale.process_pending_payments()

        self.assertEqual(sale.state, 'processing')
        self.assertEqual(len(sale.gateway_transactions), 3)

        self.assertEqual(sale.total_amount, Decimal('100'))
        self.assertEqual(sale.payment_total, Decimal('100'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('100'))
        self.assertEqual(sale.payment_captured, Decimal('100'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

    @with_transaction()
    def test3000_gift_card_method(self):
        """
        Check if gift card is being created according to gift card method
        """
        Sale = POOL.get('sale.sale')
        GiftCard = POOL.get('gift_card.gift_card')
        Invoice = POOL.get('account.invoice')
        Configuration = POOL.get('gift_card.configuration')

        self.setup_defaults()
        gift_card_product1 = self.create_product(is_gift_card=True)
        gift_card_product2 = self.create_product(is_gift_card=True)

        with Transaction().set_context({'company': self.company.id}):

            Configuration.create([{
                'liability_account': self._get_account_by_kind('revenue').id
            }])

            gc_price1, _, = gift_card_product1.gift_card_prices
            gc_price2, _, = gift_card_product2.gift_card_prices
            sale, = Sale.create([{
                'reference': 'Sale1',
                'sale_date': date.today(),
                'invoice_address': self.party1.addresses[0].id,
                'shipment_address': self.party1.addresses[0].id,
                'party': self.party1.id,
                'lines': [
                    ('create', [{
                        'quantity': 1,
                        'unit': self.uom,
                        'unit_price': 500,
                        'description': 'Gift Card 1',
                        'product': gift_card_product1,
                        'gc_price': gc_price1
                    }, {
                        'quantity': 1,
                        'unit': self.uom,
                        'unit_price': 500,
                        'description': 'Gift Card 2',
                        'product': gift_card_product2,
                        'gc_price': gc_price2,
                    }, {
                        'type': 'comment',
                        'description': 'Test line',
                    }])
                ]
            }])

            Sale.quote([sale])
            Sale.confirm([sale])

            self.SalePayment.create([{
                'sale': sale.id,
                'amount': Decimal('1000'),
                'gateway': self.create_payment_gateway('manual'),
                'credit_account': self.party1.account_receivable.id,
            }])

            Sale.process([sale])

            # Two giftcards should have been created and activated
            self.assertEqual(
                GiftCard.search([('state', '=', 'active')], count=True),
                2
            )

            # Trigger sale process again
            Sale.process([sale])

            # No new giftcards should have been created
            self.assertEqual(
                GiftCard.search([('state', '=', 'active')], count=True),
                2
            )

            # Now re-do sale with invoice payment
            config = self.SaleConfig(1)
            config.gift_card_method = 'invoice'
            config.save()

            sale, = Sale.create([{
                'reference': 'Sale1',
                'sale_date': date.today(),
                'invoice_address': self.party1.addresses[0].id,
                'shipment_address': self.party1.addresses[0].id,
                'party': self.party1.id,
                'lines': [
                    ('create', [{
                        'quantity': 1,
                        'unit': self.uom,
                        'unit_price': 500,
                        'description': 'Gift Card 1',
                        'product': gift_card_product1,
                        'gc_price': gc_price1
                    }, {
                        'quantity': 1,
                        'unit': self.uom,
                        'unit_price': 500,
                        'description': 'Gift Card 2',
                        'product': gift_card_product2,
                        'gc_price': gc_price2,
                    }, {
                        'type': 'comment',
                        'description': 'Test line',
                    }])
                ]
            }])

            Sale.quote([sale])
            Sale.confirm([sale])

            payment, = self.SalePayment.create([{
                'sale': sale.id,
                'amount': Decimal('1000'),
                'gateway': self.create_payment_gateway('manual'),
                'credit_account': self.party1.account_receivable.id,
            }])

            Sale.process([sale])

            # No new giftcards
            self.assertEqual(
                GiftCard.search([('state', '=', 'active')], count=True),
                2
            )

            # Post and pay the invoice
            invoice, = sale.invoices
            Invoice.post([invoice])

            invoice.pay_invoice(
                invoice.total_amount,
                self.cash_journal,
                invoice.invoice_date,
                'Payment to make invoice paid - obviously!'
            )
            Invoice.paid([invoice])

            # New giftcards
            self.assertEqual(
                GiftCard.search([('state', '=', 'active')], count=True),
                4
            )


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestGiftCard)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
