#!/usr/bin/env python3

"""
Installs or uninstalls Beancounttant context menus.
"""

import argparse
from pathlib import Path
import sys
import traceback
from typing import List
from context_menu import menus
from beancounttant import Beancounttant, open_file_in_default_program

MENU_TITLE = 'Beancounttant'
MENU_TYPE = 'FILES'


def generate_transaction(filenames: List[str], params: str) -> None:
    """
    Generates Beancount transaction from context menu.
    """
    error_occurred = False
    try:
        beancounttant = Beancounttant.load_config(Path(params))
        pause_if_successful = beancounttant.get_setting('pause_when_successful')

        for filename in filenames:
            document = Path(filename)
            doc_name = document.name
            doc_data = beancounttant.parse_document_filename(doc_name)

            print(f"Generating transaction for document '{doc_name}'...")
            transaction = beancounttant.generate_transaction(doc_data)

            beancount_file = beancounttant.find_beancount_file(doc_data)
            print("Writing transaction to beancount file '{}'...".format(
                beancount_file.name
            ))
            with beancount_file.open('a') as beancount_file_ptr:
                beancount_file_ptr.write(str(transaction))

            if beancounttant.get_setting('open_document'):
                print('Opening document file...')
                open_file_in_default_program(document)

        if beancounttant.get_setting('open_beancount_file'):
            print('Opening beancount file...')
            open_file_in_default_program(beancount_file)
    except:  # pylint: disable= bare-except
        print("An error occurred in Beancounttant!\nDetails:")
        traceback.print_exc()
        error_occurred = True
    finally:
        if error_occurred or pause_if_successful:
            print("Press the Enter key to exit...")
            input()


def install_menus(arguments: argparse.Namespace) -> int:
    """
    Installs Beancounttant context menus.
    """
    beancounttant_menu = menus.ContextMenu(MENU_TITLE, type=MENU_TYPE)
    beancounttant_menu.add_items([
        menus.ContextCommand('Generate Transaction',
                             params=Path(arguments.config_file).as_posix(),
                             python=generate_transaction)])
    beancounttant_menu.compile()
    return 0


def uninstall_menus(_: argparse.Namespace) -> int:
    """
    Uninstalls Beancounttant context menus.
    """
    menus.removeMenu(MENU_TITLE, type=MENU_TYPE)
    return 0


def parse_arguments(arguments: List[str]) -> argparse.Namespace:
    """
    Parses command-line arguments into namespace data.
    """
    parser = argparse.ArgumentParser(
        description="Un/installs beancounttant context menus."
    )
    subparsers = parser.add_subparsers()

    install_parser = subparsers.add_parser('install',
                                           help='Installs context menus.')
    install_parser.add_argument(
        '--config-file',
        '-c',
        dest='config_file',
        required=True,
        type=Path,
        help='File containing Beancounttant configuration data.'
    )
    install_parser.set_defaults(func=install_menus)

    uninstall_parser = subparsers.add_parser('uninstall',
                                             help='Uninstalls context menus.')
    uninstall_parser.set_defaults(func=uninstall_menus)

    return parser.parse_args(arguments)


if __name__ == "__main__":
    PARSED_ARGS = parse_arguments(sys.argv[1:])
    exit(PARSED_ARGS.func(PARSED_ARGS))
