"""Download TS (Transport Stream) video file from a website.

To use it:

- find the url of one of the TS file (for example, using the developer tools
  from Firefox or Chromium/Chrome)
- identify the counter in the url, and replace it with `{counter}` (this can be
  formatted if the counter must have a specific format, for example:
  `{counter:05d}`
- run the script: `python3 ts_downloader.py -o FILE.mp4 "URL_WITH_COUNTER"`

Bruno Oberle - 2002
"""

import argparse
import os
import subprocess
import tempfile
from urllib.error import URLError
from urllib.request import urlopen


def download(template_url):
    """Download the TS chunks and concatenate them in the returned string.

    `template_url` is a string containing the `{counter}` placeholder, which
    may contain formatting option (eg `{counter:05d}`).

    The urls are formed by incrementing the counter. When an error is
    encountered (eg a 404), the loop stops.

    The returned value is binary string.
    """
    binary_content = b""
    counter = 1
    while True:
        url = template_url.format(counter=counter)
        print(f"Reading {url}")
        try:
            u = urlopen(url)
        except URLError:
            print("Error encountered, quiting downloading")
            break
        else:
            binary_content += u.read()
            counter += 1
    return binary_content


def convert_ts_to_mp4(ts_path, mp4_path):
    """Convert the TS chunks to mp4 using ffmpeg.

    `ts_path` is a file containing the concatenated TS chunks.

    `mp4_path` is the output path.
    """
    print(f"Converting to mp4 using ffmpeg, output is {mp4_path}")
    subprocess.check_call(['ffmpeg', '-i', ts_path, mp4_path])


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "url_template",
        help="url template, must include {counter}"
    )
    parser.add_argument(
        "-o", dest="outfpath", required=True,
        help="output file"
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    template_url = args.url_template
    content = download(template_url)
    with tempfile.TemporaryDirectory() as tempdir:
        ts_path = os.path.join(tempdir, "concat.ts")
        with open(ts_path, 'wb') as fh:
            fh.write(content)
        convert_ts_to_mp4(ts_path, args.outfpath)


if __name__ == "__main__":
    main()
