#!/usr/bin/env python3

"""
Contains enhanced versions of Beancount classes for Beancounttant.
"""

from typing import Iterable
from beancount.core.amount import Amount
import beancount.core.data as beandata
from beancount.core.number import Decimal
from beancount.core.position import CostSpec


def str_or_empty(string: str) -> str:
    """
    Ensures None or '' strings are output as an empty string.
    """
    return "" if not string else string


def noneless_format(format_str: str, *args) -> str:
    """
    Formats a string, ensuring that all Falsy strings are emptied.
    Keyword argument formatting is not currently supported.
    """
    return format_str.format(*map(str_or_empty, args))


def str_join(iterable: Iterable,
             infix: str,
             prefix: str = '',
             postfix: str = '') -> str:
    """
    Joins an iterable into a string with an optional prefix and postfix.
    Similar to str.join(), prefix and postfix won't appear if string is Falsy.
    """
    if iterable is None:
        return ''

    join_str = infix.join(iterable)
    return noneless_format("{0}{1}{2}", prefix, join_str, postfix) if join_str \
        else ''

def cost_to_str(cost: CostSpec) -> str:
    """
    Converts a cost value into a string.
    """
    if not cost:
        return ''

    cost_fmt = None
    cost_strs = []
    if cost.number_per is not None:
        cost_fmt = " {{{}}}"
        cost_strs.append(str(cost.number_per))
        if cost.number_total:
            cost_strs.append('#')
            cost_strs.append(str(cost.number_total))
    elif cost.number_total is not None:
        cost_fmt = " {{{{{}}}}}"
        cost_strs.append(str(cost.number_total))
    else:
        raise AssertionError("Cost not None, but total and per are None!")
    if cost.currency:
        cost_strs.append(cost.currency)

    return cost_fmt.format(' '.join(cost_strs))


class Posting(beandata.Posting):
    """
    Extends beancount's Posting class to provide easier init & printing.
    """
    format_str = "{account}    {units}{cost}"

    def __str__(self) -> str:
        if self.meta and self.meta.get("hide_amt", False):
            return self.account
        else:
            return self.format_str.format(account=self.account,
                                          units=self.units,
                                          cost=cost_to_str(self.cost))

    @classmethod
    def from_dict(cls, data: dict) -> "Posting":
        """
        Constructs a Beancount posting from data within a dictionary.
        """
        costs = (data.get("cost_per", None), data.get("cost_total", None))
        cost_data = None if all(cost is None for cost in costs) \
            else CostSpec(
                None if costs[0] is None else Decimal(costs[0]),
                None if costs[1] is None else Decimal(costs[1]),
                data.get("cost_currency", "USD"),
                date=None,
                label=None,
                merge=None)
        post_meta = dict(hide_amt=True) if data.get("hide_amt", None) else None
        return Posting(data["account"],
                       Amount(Decimal(data.get("amount", "0.00")),
                              data.get("currency", "USD")),
                       cost=cost_data,
                       price=None,
                       flag=None,
                       meta=post_meta)

    @classmethod
    def from_name(cls, account: str) -> "Posting":
        """
        Constructs a default Beancount posting from an account name.
        """
        return Posting(account,
                       Amount(Decimal("0.00"), "USD"),
                       cost=None,
                       price=None,
                       flag=None,
                       meta=None)


class Transaction(beandata.Transaction):  # pylint: disable=inherit-non-class
    """
    Extends beancount's Transaction class to provide easier printing.
    """
    format_str = """{date} {flag}{payee}{narrate}{tags}{links}{meta}{posts}

"""

    def __str__(self) -> str:
        payee_str = " \"{}\"".format(self.payee) if self.payee else ''
        narrate_str = " \"{}\"".format(self.narration) if self.narration else ''
        tag_strs = str_join(self.tags, prefix=' #', infix=' #')
        link_strs = str_join(self.links, prefix=' ^', infix=' ^')
        meta_strs = str_join(
            ["  {0}: \"{1}\"".format(nm, val) for nm, val in self.meta.items()]\
                if self.meta else None,
            prefix='\n',
            infix='\n')
        posting_strs = str_join(["  {}".format(post) for post in self.postings]\
                                    if self.postings else None,
                                prefix='\n',
                                infix='\n')
        return self.format_str.format(date=self.date,
                                      flag=self.flag if self.flag else "*",
                                      payee=payee_str,
                                      narrate=narrate_str,
                                      tags=tag_strs,
                                      links=link_strs,
                                      meta=meta_strs,
                                      posts=posting_strs)
