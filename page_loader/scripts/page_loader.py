#!/usr/bin/env python
from page_loader.page_loader import download, parse_args, BaseOSError
import sys
import logging


def main():
    args = parse_args()
    try:
        print(download(args.source, dest_path=args.output))
    except BaseOSError as e:
        log_str = e.message if hasattr(e, 'message') else e
        logging.debug(log_str)
        sys.exit(1)


if __name__ == '__main__':
    main()
