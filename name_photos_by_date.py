import argparse
import datetime
import hashlib
import os
import pathlib
import re
import shutil
import subprocess
from multiprocessing import Pool

import simplelogging

logger = simplelogging.get_logger(console_level=simplelogging.INFO)


def compute_sha1(filepath):
    BUF_SIZE = 65536
    sha1 = hashlib.sha1()
    with open(filepath, "rb") as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def extract_date(filepath):
    date = None
    if filepath.lower().endswith((".jpg", ".jpeg")):
        date = extract_date_image(filepath)
    if date:
        return date
    else:
        m = re.search(
            r"\D(\d{4})[-_]?(\d{2})[-_]?(\d{2})[-_](\d{2})[-_]?(\d{2})[-_]?(\d{2})\D",
            filepath,
        )
        if m and m.group(1).startswith("20"):
            return datetime.datetime(
                int(m.group(1)),
                int(m.group(2)),
                int(m.group(3)),
                int(m.group(4)),
                int(m.group(5)),
                int(m.group(6)),
            )
        m = re.search(r"\D(\d{4})(\d{2})(\d{2})-WA", filepath)
        if m and m.group(1).startswith("20"):
            return datetime.datetime(
                int(m.group(1)),
                int(m.group(2)),
                int(m.group(3)),
                0,
                0,
                0,
            )
    if filepath.lower().endswith(".mp4"):
        date = extract_date_mp4_thm(filepath)
        return date


def extract_date_mp4_thm(filepath):
    path = pathlib.Path(filepath)
    thm = path.parent / (path.stem + ".THM")
    if thm.exists():
        return extract_date_image(str(thm))


def extract_date_image(filepath):
    with subprocess.Popen(
        "identify -verbose {}".format(filepath.replace(" ", "\\ ")),
        shell=True,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    ) as proc:
        for line in proc.stdout.readlines():
            if "DateTimeOriginal" in line:
                logger.debug(line)
                m = re.search(
                    r"DateTimeOriginal: (\d{4}):(\d{2}):(\d{2})\s+(\d{2}):(\d{2}):(\d{2})",
                    line,
                )
                if m:
                    logger.debug("match")
                    return datetime.datetime(
                        int(m.group(1)),
                        int(m.group(2)),
                        int(m.group(3)),
                        int(m.group(4)),
                        int(m.group(5)),
                        int(m.group(6)),
                    )
        logger.error(f"Can't parse imagemagick output for {filepath[-30:]}")


def correct_date(date, args):
    if args.add or args.substract:
        delta = datetime.timedelta()
        if args.day:
            delta += datetime.timedelta(days=args.day)
        if args.hour:
            delta += datetime.timedelta(hours=args.hour)
        if args.minute:
            delta += datetime.timedelta(minutes=args.minute)
        if args.second:
            delta += datetime.timedelta(seconds=args.second)

        logger.debug(
            "before time delta: {}".format(date.strftime("%Y-%m-%d--%H-%M-%S"))
        )
        if args.add:
            date += delta
        else:
            date -= delta
        logger.debug("after time delta: {}".format(date.strftime("%Y-%m-%d--%H-%M-%S")))
    return date


def rename_an_image(filepath):
    logger.debug("managing " + filepath)
    date_time_original = extract_date(filepath)
    if date_time_original:
        extension = filepath.split(".")[-1]
        date = correct_date(date_time_original, args)
        date = date.strftime("%Y-%m-%d--%H-%M-%S")
        sha1 = compute_sha1(filepath)
        new_file_name = f"{args.directory_output}/{date}_{sha1}.{extension}"
        shutil.move(filepath, new_file_name)
        logger.info("created " + new_file_name)


def process(args):
    try:
        os.mkdir(args.directory_output)
    except FileExistsError:
        logger.debug("output directory was already created")

    images = []
    for entry in os.listdir(args.directory_input):
        extension = entry.split(".")[-1].lower()
        full_image_name = args.directory_input + "/" + entry
        if extension in ("jpg", "jpeg", "mp4", "3gp"):
            images.append(full_image_name)

    pool = Pool(processes=16)
    pool.map(rename_an_image, images, 10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Converts images file names according to their dates"
    )
    parser.add_argument(
        "-i",
        "--directory-input",
        help="Directory in which are the source photos",
        default=".",
    )
    parser.add_argument(
        "-o",
        "--directory-output",
        help="Directory in which are the destination photos",
        default="CAFEDECA",
    )
    time_delta = parser.add_argument_group("Time delta")
    time_delta.add_argument(
        "-a",
        "--add",
        help="Add time delta to date in EXIF data",
        action="store_true",
    )
    time_delta.add_argument(
        "-s",
        "--substract",
        help="Substract time delta to date in EXIF data",
        action="store_true",
    )
    time_delta.add_argument(
        "-d",
        "--day",
        help="Number of days in the time delta",
        type=int,
        metavar="N",
    )
    time_delta.add_argument(
        "-H",
        "--hour",
        help="Number of hours in the time delta",
        type=int,
        metavar="N",
    )
    time_delta.add_argument(
        "-m",
        "--minute",
        help="Number of minutes in the time delta",
        type=int,
        metavar="N",
    )
    time_delta.add_argument(
        "-S",
        "--second",
        help="Number of seconds in the time delta",
        type=int,
        metavar="N",
    )
    args = parser.parse_args()

    if args.directory_output == "CAFEDECA":
        args.directory_output = args.directory_input + "/links"

    process(args)
