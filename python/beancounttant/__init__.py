#!/usr/bin/env python3

"""
Contains primary Beancounttant class and its helper classes.
"""

from dataclasses import dataclass
from datetime import date
import json
import os
from pathlib import Path
import platform
import re
import subprocess
from typing import List
from .data import Posting, Transaction


def open_file_in_default_program(file: Path) -> None:
    """
    Opens the given file in the default program defined by the OS.
    """
    if platform.system() == 'Windows':
        os.startfile(file)
    else:
        subprocess.call(('xdg-open', file))


class DocumentData:
    """
    Contains data about parsed document files.
    """
    def __init__(self, match_data: dict) -> None:
        # Ensure date exists, then remove from dict to simplify later code.
        date_strs = match_data.get("date", None)
        if not date_strs:
            raise ValueError("Unable to find date in filename!")
        self.date = date.fromisoformat(date_strs[0])
        del match_data["date"]

        # Fix whitespace from bad group regexes by stripping all values
        self.groups = dict()
        for name, value_array in match_data.items():
            self.groups[name] = [value.strip() for value in value_array]

        id_strs = self.groups.get("identifier", None)
        if not id_strs:
            raise ValueError("Unable to find identifier in filename!")
        self.identifier = id_strs[0]


@dataclass
class PartialDirective:
    """
    Holds data that can be used to build a beancount directive.
    """
    flag: str = ""
    payee: str = ""
    narration: str = ""
    tags: List[str] = None
    metadata: dict = None
    postings: List[Posting] = None
    hide_payee: bool = False


    @classmethod
    def from_dict(cls, data: dict) -> "PartialDirective":
        """
        Constructs a PartialDirective object from data within a dictionary.
        """
        part_dir = PartialDirective()
        for attr, value in part_dir.__dict__.items():
            if attr == "postings":
                posts = data.get("postings", None)
                if posts:
                    part_dir.postings = [Posting.from_dict(datum) \
                     if isinstance(datum, dict) else Posting.from_name(datum) \
                                         for datum in posts]
            else:
                setattr(part_dir, attr, data.get(attr, value))
        return part_dir



class Beancounttant:
    """
    Contains configuration data for beancounttant.
    """
    def __init__(self,
                 default_beancount_file: str,
                 default_transaction_flag: str,
                 patterns: dict,
                 settings: dict,
                 group_directives: dict) -> None:
        self.__default_beancount_file = default_beancount_file
        self.__default_transaction_flag = default_transaction_flag
        self.__patterns = patterns
        self.__settings = settings
        self.__group_directives = group_directives


    def find_beancount_file(self, _: DocumentData) -> Path:
        """
        Returns the best beancount file to write data to for a given document.
        """
        beancount_file = self.__default_beancount_file
        return Path(beancount_file)


    def find_directive_data(self,
                            attribute: str,
                            file_data: DocumentData):
        """
        Returns a merged list of group data matching a given directive attribute
        """
        data = []
        data_dict = {}

        for group_name, group_matches in file_data.groups.items():
            group_directives = self.__group_directives.get(group_name, None)
            if group_directives:
                for match in group_matches:
                    group_directive = group_directives.get(match, None)
                    if group_directive:
                        group_attr = getattr(group_directive, attribute, None)
                        if group_attr:
                            if isinstance(group_attr, dict):
                                data_dict.update(group_attr)
                            elif isinstance(group_attr, list):
                                data.extend(group_attr)
                            else:
                                data.append(group_attr)

        # If data is a list, return the unique items without breaking sorting.
        # Code is from Netwave at https://stackoverflow.com/a/44628320
        # Posting() contains dicts (meta), making use of a set here impossible.
        lookup = list()
        return [d for d in data if d not in lookup and lookup.append(d) is None] \
            if data else data_dict


    def generate_transaction(self, data: DocumentData) -> Transaction:
        """
        Generates a beancount transaction from a document.
        """
        flag = self.find_directive_data("flag", data)
        narration = self.find_directive_data("narration", data)
        hide_payee_data = self.find_directive_data("hide_payee", data)
        hide_payee = hide_payee_data[0] if hide_payee_data else False

        return Transaction(
            date=data.date,
            flag=flag[0] if flag else self.__default_transaction_flag,
            payee=None if hide_payee else data.identifier,
            narration=narration[0] if narration else None,
            tags=self.find_directive_data("tags", data),
            links=self.find_directive_data("links", data),
            meta=self.find_directive_data("metadata", data),
            postings=self.find_directive_data("postings", data)
        )

    def parse_document_filename(self, name: str) -> DocumentData:
        """
        Parses a document's filename for beancount data.
        """
        groups = {group: re.findall(pattern, name)
                  for (group, pattern) in self.__patterns.items()}
        all_matches = [match for group in groups.values() for match in group]
        if not groups or not all_matches:
            parse_error_format = "Unable to parse document filename '{}'!"
            raise ValueError(parse_error_format.format(name))
        return DocumentData(groups)


    def get_setting(self, setting_name: str) -> bool:
        """
        Returns the value of a given setting.
        """
        return self.__settings[setting_name]


    @classmethod
    def load_config(cls, file: Path) -> "Beancounttant":
        """
        Loads beancounttant configuration from a file.
        """
        with file.open("r") as file_obj:
            config_data = json.load(file_obj)

        directives = dict()
        for group_name, group_data in config_data["groups"].items():
            directives[group_name] = {name: PartialDirective.from_dict(values)
                                      for name, values in group_data.items()}
        return Beancounttant(config_data["default_beancount_file"],
                             config_data["default_transaction_flag"],
                             config_data["patterns"],
                             config_data["settings"],
                             directives)
