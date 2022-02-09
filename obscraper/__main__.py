"""Entry-point for the obscraper command line interface."""
import argparse
import datetime
import json
import sys

import dateutil.parser

from . import _scrape, _serialize


class _CustomHelpFormatter(argparse.HelpFormatter):
    """CLI help formatter.

    CLI help formatter with less repetition and more spacing than the
    default.
    """

    def __init__(self, prog):
        super().__init__(prog, max_help_position=40, width=80)

    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return ", ".join(action.option_strings) + " " + args_string


def _main_parser():
    """Construct parser for the obscraper command line interface."""
    description = (
        "Download posts and write them to a file."
        " Posts can be downloaded via their URLs or their edit"
        " dates, or you can download all posts."
        " Datetimes are specified using the format"
        " YYYY-MM-DD[ hh:mm:ss[±HH]] or any other format understood"
        " by the flexible dateutil.parser.parse parser. (If no"
        " timezone is specified, datetimes are assumed to be UTC.)"
    )

    def parse_date_with_utc_as_default(date):
        return dateutil.parser.parse(date).astimezone(datetime.timezone.utc)

    parser = argparse.ArgumentParser(
        prog="python -m obscraper",
        description=description,
        formatter_class=_CustomHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-u", "--urls", nargs="+", help="get posts by URLs", metavar="url"
    )
    group.add_argument(
        "-d",
        "--dates",
        nargs=2,
        help="get posts by date",
        metavar=("start_date", "end_date"),
        type=parse_date_with_utc_as_default,
    )
    group.add_argument("-a", "--all", action="store_true", help="get all posts")
    parser.add_argument(
        "-o", "--outfile", default="posts.json", help="output file path"
    )
    return parser


def main(cli_args, prog=None):
    """obscraper command line interface.

    Parameters
    ----------
    cli_args : List[str]
        Command line interface arguments.
    prog : str
        Program name (to show in help text).
    """
    # Collecting arguments
    parser = _main_parser()
    if prog is not None:
        parser.prog = prog
    args = parser.parse_args(cli_args)

    # Keep file open the whole time - avoids write errors after lots of
    # expensive downloads
    with open(file=args.outfile, mode="w", encoding="utf-8") as outfile_writer:
        # Running the main program
        if isinstance(args.urls, list) and len(args.urls) > 0:
            print("Getting posts by their URLs...")
            posts = _scrape.get_posts_by_urls(args.urls)
        elif args.dates is not None:
            print(
                (
                    "Getting posts edited between"
                    f" {args.dates[0]} and {args.dates[1]}..."
                )
            )
            posts = _scrape.get_posts_by_edit_date(*args.dates)
        elif args.all:
            print("Getting all posts...")
            posts = _scrape.get_all_posts()

        # Postprocessing
        output = [{"url": url, "post": p} for url, p in posts.items()]

        # Writing to file
        print(f"Writing posts to {args.outfile}...")
        json.dump(output, outfile_writer, cls=_serialize.PostEncoder, indent=4)

    print("Posts successfully written to file.")

    parser.exit()


def entrypoint():
    """Entry point for the obscraper command line interface."""
    main(sys.argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:], "python -m obscraper")
