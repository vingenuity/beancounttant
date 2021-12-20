#!/usr/bin/env python3
# pylint: disable=missing-function-docstring

"""
Contains unit tests for the module beancounttant.data.
"""

from datetime import date
from typing import List
import unittest
from beancount.core.amount import Amount
from beancount.core.number import Decimal
from beancount.core.position import CostSpec
from beancounttant.data import str_or_empty, noneless_format, str_join, \
                               cost_to_str, Posting, Transaction

class TestStrOrEmpty(unittest.TestCase):
    """
    Unit tests the beancounttant module function str_or_empty().
    """
    def test_empty(self):
        self.assertEqual(str_or_empty(''), '')

    def test_none(self):
        self.assertEqual(str_or_empty(None), '')

    def test_string(self):
        self.assertEqual(str_or_empty('string'), 'string')


class TestNonelessFormat(unittest.TestCase):
    """
    Unit tests the beancounttant module function noneless_format().
    """
    empty_fmt: str = "test {} {}"
    num_fmt: str = "test {0} {1}"

    def test_empty_fmt_all_none(self):
        self.assertEqual(noneless_format(self.empty_fmt, None, None), 'test  ')

    def test_empty_fmt_one_none(self):
        self.assertEqual(noneless_format(self.empty_fmt, None, 2), 'test  2')

    def test_empty_fmt(self):
        self.assertEqual(noneless_format(self.empty_fmt, 1, 2), 'test 1 2')

    def test_num_fmt_all_none(self):
        self.assertEqual(noneless_format(self.num_fmt, None, None), 'test  ')

    def test_num_fmt_one_none(self):
        self.assertEqual(noneless_format(self.num_fmt, None, 2), 'test  2')

    def test_num_fmt(self):
        self.assertEqual(noneless_format(self.num_fmt, 1, 2), 'test 1 2')


class TestStrJoin(unittest.TestCase):
    """
    Unit tests the beancounttant module function str_join().
    """
    iter_empty: List[str] = []
    iter_full: List[str] = ['t', 'e', 's', 't']
    iter_none: List[str] = None

    def test_iter_empty_infix_only(self):
        self.assertEqual(str_join(self.iter_empty, ' '), '')

    def test_iter_empty_all_fixes(self):
        self.assertEqual(str_join(self.iter_empty, ' ', 'at', 'ed'), '')

    def test_iter_full_infix_only(self):
        self.assertEqual(str_join(self.iter_full, ' '), 't e s t')

    def test_iter_full_infix_prefix_none(self):
        self.assertEqual(str_join(self.iter_full, ' ', None), 't e s t')

    def test_iter_full_infix_prefix(self):
        self.assertEqual(str_join(self.iter_full, ' ', 'at'), 'att e s t')

    def test_iter_full_infix_postfix_none(self):
        self.assertEqual(str_join(self.iter_full, ' ', postfix=None), 't e s t')

    def test_iter_full_infix_postfix(self):
        self.assertEqual(str_join(self.iter_full, ' ', postfix='ed'),
                         't e s ted')

    def test_iter_full_all_fixes(self):
        self.assertEqual(str_join(self.iter_full, ' ', 'at', 'ed'),
                         'att e s ted')

    def test_iter_none_infix_only(self):
        self.assertEqual(str_join(self.iter_none, ' '), '')

    def test_iter_none_all_fixes(self):
        self.assertEqual(str_join(self.iter_none, ' ', 'at', 'ed'), '')


class TestCostToStr(unittest.TestCase):
    """
    Unit tests the beancounttant module function cost_to_str().
    """
    cost_per: CostSpec = CostSpec(number_per='1.00',
                                  number_total=None,
                                  currency='USD',
                                  date=None,
                                  label=None,
                                  merge=None)
    cost_no_currency: CostSpec = CostSpec(number_per='0.00',
                                          number_total=None,
                                          currency=None,
                                          date=None,
                                          label=None,
                                          merge=None)
    cost_total: CostSpec = CostSpec(number_per=None,
                                    number_total='3.14',
                                    currency='PIE',
                                    date=None,
                                    label=None,
                                    merge=None)
    cost_per_total: CostSpec = CostSpec(number_per='2.00',
                                        number_total='3.14',
                                        currency='PIE',
                                        date=None,
                                        label=None,
                                        merge=None)

    def test_cost_none(self):
        self.assertEqual(cost_to_str(None), '')

    def test_cost_per(self):
        self.assertEqual(cost_to_str(self.cost_per), ' {1.00 USD}')

    def test_cost_no_currency(self):
        self.assertEqual(cost_to_str(self.cost_no_currency), ' {0.00}')

    def test_cost_total(self):
        self.assertEqual(cost_to_str(self.cost_total), ' {{3.14 PIE}}')

    def test_cost_per_total(self):
        self.assertEqual(cost_to_str(self.cost_per_total), ' {2.00 # 3.14 PIE}')


class TestPosting(unittest.TestCase):
    """
    Unit tests the beancounttant.Posting class.
    """
    post_amount: Posting = Posting.from_dict(
        dict(account='testy', amount='3.14', currency='PIE'))
    post_cost_per: Posting = Posting.from_dict(dict(account='cirque',
                                                    amount='3.14',
                                                    currency='PIE',
                                                    cost_per='6.28',
                                                    cost_currency='TAU'))
    post_cost_total: Posting = Posting.from_dict(dict(account='cirque',
                                                      amount='6.28',
                                                      currency='TAU',
                                                      cost_total='360.00',
                                                      cost_currency='DEG'))
    post_cost_per_total: Posting = Posting.from_dict(dict(account='alpha',
                                                          amount='1.11',
                                                          currency='AAA',
                                                          cost_per='2.22',
                                                          cost_total='3.33',
                                                          cost_currency='BBB'))
    post_name: Posting = Posting.from_name('test')

    def test_str_amount(self):
        self.assertEqual(str(self.post_amount), 'testy    3.14 PIE')

    def test_str_cost_per(self):
        self.assertEqual(str(self.post_cost_per),
                         'cirque    3.14 PIE {6.28 TAU}')

    def test_str_cost_total(self):
        self.assertEqual(str(self.post_cost_total),
                         'cirque    6.28 TAU {{360.00 DEG}}')

    def test_str_cost_per_total(self):
        self.assertEqual(str(self.post_cost_per_total),
                         'alpha    1.11 AAA {2.22 # 3.33 BBB}')

    def test_str_name(self):
        self.assertEqual(str(self.post_name), 'test    0.00 USD')

    def test_from_dict(self):
        self.assertEqual(self.post_amount,
                         Posting('testy',
                                 Amount(Decimal('3.14'), 'PIE'),
                                 cost=None,
                                 price=None,
                                 flag=None,
                                 meta=None))

    def test_from_name(self):
        self.assertEqual(self.post_name,
                         Posting('test',
                                 Amount(Decimal('0.00'), 'USD'),
                                 cost=None,
                                 price=None,
                                 flag=None,
                                 meta=None))


class TestTransaction(unittest.TestCase):
    """
    Unit tests the beancounttant.Transaction class.
    """
    trans_max = Transaction(
        date=date(2021, 1, 1),
        flag='!',
        payee='Tests',
        narration='Test transaction',
        tags=['tag1', 'tag2'],
        links=['link1', 'link2'],
        meta=dict(invoice='0122', check='33'),
        postings=[
            Posting.from_dict(dict(account='t', amount='3.14', currency='PIE')),
            Posting.from_dict(dict(account='s', amount='2.22', currency='CAD'))
        ])
    trans_min = Transaction(date=date(2021, 2, 1),
                            flag='*',
                            payee="Testy",
                            narration=None,
                            tags=None,
                            links=None,
                            meta=None,
                            postings=None)

    def test_str_max(self):
        self.assertEqual(
            str(self.trans_max),
            """2021-01-01 ! "Tests" "Test transaction" #tag1 #tag2 ^link1 ^link2
  invoice: "0122"
  check: "33"
  t    3.14 PIE
  s    2.22 CAD

""")

    def test_str_min(self):
        self.assertEqual(str(self.trans_min),
                         """2021-02-01 * "Testy"

""")


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
