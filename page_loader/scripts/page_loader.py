#!/usr/bin/env python
from page_loader.page_loader import download
import argparse


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
    print(download(args.source, dest_path=args.output))


if __name__ == '__main__':
    main()
