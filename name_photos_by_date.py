#!python3

import argparse
import datetime
import logging
import os
import re
import shutil
import subprocess

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def process(args):
    try:
        os.mkdir(args.directory_output)
    except FileExistsError:
        logger.debug('output directory was already created')

    for entry in os.listdir(args.directory_input):
        extension = entry.split('.')[-1]
        full_image_name = args.directory_input + '/' + entry
        if extension.lower() in ['jpg', 'jpeg']:
            logger.debug('managing ' + entry)
            with subprocess.Popen(
                'identify -verbose {}'.format(
                    full_image_name.replace(' ', '\\ ')),
                    shell=True,
                    stdout=subprocess.PIPE,
                    universal_newlines=True) as proc:
                found = False
                for line in proc.stdout.readlines():
                    if 'DateTimeOriginal' in line:
                        logger.debug(line)
                        m = re.search(
                            r'DateTimeOriginal: (\d{4}):(\d{2}):(\d{2})\s+(\d{2}):(\d{2}):(\d{2})', line)
                        if m:
                            logger.debug('match')
                            found = True

                            date_time_original = datetime.datetime(
                                int(m.group(1)),
                                int(m.group(2)),
                                int(m.group(3)),
                                int(m.group(4)),
                                int(m.group(5)),
                                int(m.group(6)))

                            if args.add or args.substract:
                                delta = datetime.timedelta()
                                if args.day:
                                    delta += datetime.timedelta(days=args.day)
                                if args.hour:
                                    delta += datetime.timedelta(
                                        hours=args.hour)
                                if args.minute:
                                    delta += datetime.timedelta(
                                        minutes=args.minute)
                                if args.second:
                                    delta += datetime.timedelta(
                                        seconds=args.second)

                                logger.debug(
                                    'before time delta: {}'.format(
                                        date_time_original.strftime('%Y-%m-%d--%H-%M-%S')))
                                if args.add:
                                    date_time_original += delta
                                else:
                                    date_time_original -= delta
                                logger.debug(
                                    'after time delta: {}'.format(
                                        date_time_original.strftime('%Y-%m-%d--%H-%M-%S')))

                            new_file_name = date_time_original.strftime(
                                '%Y-%m-%d--%H-%M-%S')

                            count = 0
                            for entry in os.listdir(args.directory_output):
                                if new_file_name in entry:
                                    count += 1
                                    logger.info(
                                        'Two photos have the same date')

                            new_file_name += '_{}.jpg'.format(count)
                            new_file_name = args.directory_output + '/' + new_file_name
                            shutil.move(
                                full_image_name, new_file_name)
                            logger.info('created ' + new_file_name)

                if not found:
                    logger.error("Can't parse imagemagick output")


def main():
    parser = argparse.ArgumentParser(
        description="Converts images file names according to their dates")
    parser.add_argument(
        '-i',
        '--directory-input',
        help='Directory in which are the source photos',
        default='.')
    parser.add_argument(
        '-o',
        '--directory-output',
        help='Directory in which are the destination photos',
        default='CAFEDECA')
    time_delta = parser.add_argument_group('Time delta')
    time_delta.add_argument(
        '-a',
        '--add',
        help='Add time delta to date in EXIF data',
        action='store_true')
    time_delta.add_argument(
        '-s',
        '--substract',
        help='Substract time delta to date in EXIF data',
        action='store_true')
    time_delta.add_argument(
        '-d',
        '--day',
        help='Number of days in the time delta',
        type=int,
        metavar='N')
    time_delta.add_argument(
        '-H',
        '--hour',
        help='Number of hours in the time delta',
        type=int,
        metavar='N')
    time_delta.add_argument(
        '-m',
        '--minute',
        help='Number of minutes in the time delta',
        type=int,
        metavar='N')
    time_delta.add_argument(
        '-S',
        '--second',
        help='Number of seconds in the time delta',
        type=int,
        metavar='N')
    args = parser.parse_args()

    if args.directory_output == 'CAFEDECA':
        args.directory_output = args.directory_input + '/links'

    process(args)


if __name__ == "__main__":
    main()
