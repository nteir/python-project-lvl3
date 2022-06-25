#!/usr/bin/env python
from page_loader.page_loader import download, BaseOSError
import sys
import argparse
import logging


def main():
    parser = argparse.ArgumentParser(
        description='Downloads a Web page and saves it locally.'
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="destination directory path"
    )
    parser.add_argument("source")
    args = parser.parse_args()
    try:
        print(download(args.source, dest_path=args.output))
    except BaseOSError as e:
        log_str = e.message if hasattr(e, 'message') else e
        logging.debug(log_str)
        sys.exit(1)


if __name__ == '__main__':
    main()
