# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
'''

    Dummy Payment Gateway Transaction

    Untested code is broken code. Testing web services are painful, testing
    payment gateways are even more painful. This module adds a dummy
    credit card processor for unit and integrations tests to use.

    In production use this payment provider does not appear. To enable the
    dummy provider in your tests, add 'use_dummy'=True to the transaction
    context.

    .. code-block:: python

        with Transaction().set_context(use_dummy=True):
            PaymentGateway.create([{
                'name': 'A dummy gateway',
                'journal': journal_cash,
                'account': expense,
                'provider': 'dummy',
                'method': 'credit_card',
            }])
'''
from trytond.model import fields
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta


class PaymentGatewayDummy(metaclass=PoolMeta):
    "A Dummy Credit Card Processor for writing tests"
    __name__ = 'payment_gateway.gateway'

    @classmethod
    def get_providers(cls, values=None):
        """
        Downstream modules can add to the list
        """
        rv = super(PaymentGatewayDummy, cls).get_providers()
        self_record = ('dummy', 'Dummy')
        if Transaction().context.get('use_dummy') and self_record not in rv:
            rv.append(self_record)
        return rv

    @fields.depends('provider')
    def get_methods(self):
        if self.provider == 'dummy':
            return [
                ('dummy', 'Dummy Credit Card Processor'),
            ]
        return super(PaymentGatewayDummy, self).get_methods()


class DummyTransaction(metaclass=PoolMeta):
    """
    Implement the authorize and capture methods
    """
    __name__ = 'payment_gateway.transaction'

    def authorize_dummy(self, card_info=None):
        """
        Authorize with a dummy card
        """
        succeed = Transaction().context.get('dummy_succeed', True)

        if succeed:
            self.state = 'authorized'
        else:
            self.state = 'failed'
        self.save()

    def settle_dummy(self):
        """
        Settle a dummy transaction
        """
        succeed = Transaction().context.get('dummy_succeed', True)

        if succeed:
            self.state = 'completed'
            self.save()
            self.safe_post()
        else:
            self.state = 'failed'
            self.save()

    def capture_dummy(self):
        """
        Capture a dummy transaction
        """
        succeed = Transaction().context.get('dummy_succeed', True)

        if succeed:
            self.state = 'completed'
            self.save()
            self.safe_post()
        else:
            self.state = 'failed'
            self.save()

    def cancel_dummy(self):
        """
        Cancel a dummy transaction
        """
        if self.state != 'authorized':
            self.raise_user_error('cancel_only_authorized')

        succeed = Transaction().context.get('dummy_succeed', True)

        if succeed:
            self.state = 'cancel'
            self.save()


class AddPaymentProfileViewDummy(metaclass=PoolMeta):
    __name__ = 'party.payment_profile.add_view'

    @classmethod
    def get_providers(cls):
        """
        Return the list of providers who support credit card profiles.
        """
        res = super(AddPaymentProfileViewDummy, cls).get_providers()
        if Transaction().context.get('use_dummy'):
            res.append(('dummy', 'Dummy Gateway'))
        return res


class AddPaymentProfileDummy(metaclass=PoolMeta):
    """
    Add a payment profile
    """
    __name__ = 'party.party.payment_profile.add'

    def transition_add_dummy(self):
        """
        Handle the case if the profile should be added for dummy
        """
        succeed = Transaction().context.get('dummy_succeed', True)

        if succeed:
            return self.create_profile(self.card_info.csc)
