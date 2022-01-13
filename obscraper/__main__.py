"""Entry-point for command line interface."""
import argparse
import datetime
import json
import dateutil.parser

from . import scrape, serialize


class CustomHelpFormatter(argparse.HelpFormatter):
    """CLI help formatter with less repetition and more spacing."""

    def __init__(self, prog):
        super().__init__(prog, max_help_position=40, width=80)

    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return ', '.join(action.option_strings) + ' ' + args_string


def get_arg_parser():
    """Argument parser for the obscraper command line interface."""
    description = ('Download posts and write them to a file.\n'
                   'Posts can be downloaded via their URLs or their edit'
                   ' dates, or you can download all posts.\n'
                   'Datetimes are specified using the format'
                   ' YYYY-MM-DD[ hh:mm:ss[±HH]] or any other format understood'
                   ' by the flexible dateutil.parser.parse parser. (If no'
                   ' timezone is specified, datetimes are assumed to be UTC.)')

    def parse_date_with_utc_as_default(date):
        return dateutil.parser.parse(date).astimezone(datetime.timezone.utc)

    parser = argparse.ArgumentParser(prog='python -m obscraper',
                                     description=description,
                                     formatter_class=CustomHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--urls', nargs='+',
                       help='get posts by URLs', metavar='url')
    group.add_argument('-d', '--dates', nargs=2,
                       help='get posts by date',
                       metavar=('start_date', 'end_date'),
                       type=parse_date_with_utc_as_default)
    group.add_argument('-a', '--all', action='store_true',
                       help='get all posts')
    parser.add_argument('-o', '--outfile', default='outputs/posts.json',
                        help='output file path')
    return parser


def main():
    """obscraper command line interface."""
    # Collecting arguments
    parser = get_arg_parser()
    args = parser.parse_args()

    core(args.urls, args.dates, args.all, args.outfile)

    parser.exit()


def core(urls, dates, all_posts, outfile):
    """Program logic for obscraper command line interface."""
    # Keep file open the whole time - avoids write errors after lots of
    # expensive downloads
    with open(file=outfile, mode='w', encoding='utf-8') as outfile_writer:
        # Running the main program
        if isinstance(urls, list) and len(urls) > 0:
            print('Getting posts by their URLs...')
            posts = scrape.get_posts_by_urls(urls)
        elif dates is not None:
            print(('Getting posts edited between'
                   f' {dates[0]} and {dates[1]}...'))
            posts = scrape.get_posts_by_edit_date(*dates)
        elif all_posts:
            print('Getting all posts...')
            posts = scrape.get_all_posts()

        # Postprocessing
        output = [{'url': url, 'post': p} for url, p in posts.items()]

        # Writing to file
        print(f'Writing posts to {outfile}...')
        json.dump(output, outfile_writer, cls=serialize.PostEncoder, indent=4)

    print('Posts successfully written to file.')


if __name__ == '__main__':
    main()
