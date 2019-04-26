from django.test import TestCase

from wifiportal.forms import CustomerForm
from wifiportal.tests import create_test_org


class TestCustomerForm(TestCase):
    def setUp(self):
        self.organization = create_test_org(name="Test", location='Test')

    def test_phone_number_validation_uae_number(self):
        customer_form = CustomerForm(data=dict(name="Hira lal Jawari", phone_number="0547584939", organization=self.organization.id))
        form_validity = customer_form.is_valid()
        self.assertEqual(form_validity, True)

        customer = customer_form.save()
        self.assertEqual(customer.name, 'Hira lal Jawari')

    def test_phone_number_validation_nepal_number(self):
        customer_form = CustomerForm(data=dict(name="33 kilo sun", phone_number='9857465654', organization=self.organization.id))
        form_validity = customer_form.is_valid()
        self.assertEqual(form_validity, True)

        customer = customer_form.save()
        self.assertEqual(customer.name, '33 kilo sun')

    def test_phone_number_validation_invalid_length(self):
        customer_form = CustomerForm(data=dict(name="samosa chat", phone_number="054", organization=self.organization.id))
        self.assertEqual(customer_form.is_valid(), False)
        self.assertIn('phone_number', customer_form.errors)

        customer_form = CustomerForm(data=dict(name="aalu chat", phone_number="985443544232", organization=self.organization.id))
        self.assertEqual(customer_form.is_valid(), False)
        self.assertIn('phone_number', customer_form.errors)

    def test_phone_number_validation_invalid_sequence(self):
        customer_form = CustomerForm(
            data=dict(name="Futsal kumar", phone_number="8457463432", organization=self.organization.id))
        self.assertEqual(customer_form.is_valid(), False)
        self.assertIn('phone_number', customer_form.errors)
