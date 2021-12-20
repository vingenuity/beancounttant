#!/usr/bin/env python3

"""
Generates a beancount transaction from a document.
"""

import argparse
import logging
from pathlib import Path
import sys
from typing import List
from beancounttant import Beancounttant


def main(config_file: Path,
         document: Path) -> int:
    """
    Contains the main functionality of this script.
    """
    logger = logging.getLogger()

    if not document.exists():
        logger.error("Unable to find document at '%s'!", document)

    beancounttant = Beancounttant.load_config(config_file)
    doc_data = beancounttant.parse_document_filename(document.name)

    logger.info("Generating transaction for document '%s'...", document.name)
    transaction = beancounttant.generate_transaction(doc_data)
    print(transaction)

    beancount_file = beancounttant.find_beancount_file(doc_data)
    logger.info("Writing transaction to beancount file '%s'...",
                beancount_file.name)
    with beancount_file.open("a") as beancount_file_ptr:
        beancount_file_ptr.write(str(transaction))


def parse_arguments(arguments: List[str]) -> argparse.Namespace:
    """
    Parses command-line arguments into namespace data.
    """
    parser = argparse.ArgumentParser(
        description="Generates a beancount transaction from a document."
    )
    parser.add_argument('--config-file',
                        '-c',
                        dest='config_file',
                        required=True,
                        type=Path,
                        help='File containing Beancounttant configuration.')
    parser.add_argument('--document',
                        '-d',
                        dest='document',
                        required=True,
                        type=Path,
                        help='Document for which to create a transaction.')

    return parser.parse_args(arguments)


if __name__ == "__main__":
    exit(main(**vars(parse_arguments(sys.argv[1:]))))
