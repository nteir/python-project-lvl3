#!/usr/bin/env python
import page_loader.page_loader as pl
import sys
import logging


def main():
    args = pl.parse_arguments()
    try:
        print(pl.download(args.source, dest_path=args.output))
    # except BaseOSError as e:
    #     log_str = e.message if hasattr(e, 'message') else e
    #     logging.debug(log_str)
    #     sys.exit(1)
    except pl.ResourceDownloadError as e:
        log_str = e.message if hasattr(e, 'message') else e
        logging.debug(log_str)
    except (pl.FileSystemError, pl.PageDownloadError) as e:
        log_str = e.message if hasattr(e, 'message') else e
        logging.debug(log_str)
        sys.exit(1)


if __name__ == '__main__':
    main()
