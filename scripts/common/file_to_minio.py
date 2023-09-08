from minio import Minio
from minio.error import S3Error
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep
from queue import Empty, Queue
import time
import socket
import argparse
import sys

_BAR_SIZE = 20
_KILOBYTE = 1024
_FINISHED_BAR = "#"
_REMAINING_BAR = "-"

_UNKNOWN_SIZE = "?"
_STR_MEGABYTE = " MB"

_HOURS_OF_ELAPSED = "%d:%02d:%02d"
_MINUTES_OF_ELAPSED = "%02d:%02d"

_RATE_FORMAT = "%5.2f"
_PERCENTAGE_FORMAT = "%3d%%"
_HUMANINZED_FORMAT = "%0.2f"

_DISPLAY_FORMAT = "|%s| %s/%s %s [elapsed: %s left: %s, %s MB/sec]"

_REFRESH_CHAR = "\r"

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
HOST_IP = s.getsockname()[0]
s.close()

parser = argparse.ArgumentParser(
    description="File to minio",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)


parser.add_argument(
    "--mnip",
    dest="MINIO_IP",
    help="Minio ip",
    required=False,
)

parser.add_argument(
    "-f",
    "--file",
    dest="FILE",
    help="File path",
    required=False,
)

parser.add_argument(
    "-b",
    "--bucket",
    dest="BUCKET",
    help="Bucket destination",
    required=False,
)


args = parser.parse_args()

MINIO_IP = args.MINIO_IP or HOST_IP


class Progress(Thread):
    """
    Constructs a :class:`Progress` object.
    :param interval: Sets the time interval to be displayed on the screen.
    :param stdout: Sets the standard output
    :return: :class:`Progress` object
    """

    def __init__(self, interval=1, stdout=sys.stdout):
        Thread.__init__(self)
        self.daemon = True
        self.total_length = 0
        self.interval = interval
        self.object_name = None

        self.last_printed_len = 0
        self.current_size = 0

        self.display_queue = Queue()
        self.initial_time = time.time()
        self.stdout = stdout
        self.start()

    def set_meta(self, total_length, object_name):
        """
        Metadata settings for the object. This method called before uploading
        object
        :param total_length: Total length of object.
        :param object_name: Object name to be showed.
        """
        self.total_length = total_length
        self.object_name = object_name
        self.prefix = self.object_name + ": " if self.object_name else ""

    def run(self):
        displayed_time = 0
        while True:
            try:
                # display every interval secs
                task = self.display_queue.get(timeout=self.interval)
            except Empty:
                elapsed_time = time.time() - self.initial_time
                if elapsed_time > displayed_time:
                    displayed_time = elapsed_time
                continue

            current_size, total_length = task
            displayed_time = time.time() - self.initial_time
            self.print_status(
                current_size=current_size,
                total_length=total_length,
                displayed_time=displayed_time,
                prefix=self.prefix,
            )
            self.display_queue.task_done()
            if current_size == total_length:
                self.done_progress()

    def update(self, size):
        """
        Update object size to be showed. This method called while uploading
        :param size: Object size to be showed. The object size should be in
                     bytes.
        """
        if not isinstance(size, int):
            raise ValueError(
                "{} type can not be displayed. "
                "Please change it to Int.".format(type(size))
            )

        self.current_size += size
        self.display_queue.put((self.current_size, self.total_length))

    def done_progress(self):
        self.total_length = 0
        self.object_name = None
        self.last_printed_len = 0
        self.current_size = 0

    def print_status(self, current_size, total_length, displayed_time, prefix):
        formatted_str = prefix + format_string(
            current_size, total_length, displayed_time
        )
        self.stdout.write(
            _REFRESH_CHAR
            + formatted_str
            + " " * max(self.last_printed_len - len(formatted_str), 0)
        )
        self.stdout.flush()
        self.last_printed_len = len(formatted_str)


def seconds_to_time(seconds):
    """
    Consistent time format to be displayed on the elapsed time in screen.
    :param seconds: seconds
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, m = divmod(minutes, 60)
    if hours:
        return _HOURS_OF_ELAPSED % (hours, m, seconds)
    else:
        return _MINUTES_OF_ELAPSED % (m, seconds)


def format_string(current_size, total_length, elapsed_time):
    """
    Consistent format to be displayed on the screen.
    :param current_size: Number of finished object size
    :param total_length: Total object size
    :param elapsed_time: number of seconds passed since start
    """

    n_to_mb = current_size / _KILOBYTE / _KILOBYTE
    elapsed_str = seconds_to_time(elapsed_time)

    rate = _RATE_FORMAT % (n_to_mb / elapsed_time) if elapsed_time else _UNKNOWN_SIZE
    frac = float(current_size) / total_length
    bar_length = int(frac * _BAR_SIZE)
    bar = _FINISHED_BAR * bar_length + _REMAINING_BAR * (_BAR_SIZE - bar_length)
    percentage = _PERCENTAGE_FORMAT % (frac * 100)
    left_str = (
        seconds_to_time(elapsed_time / current_size * (total_length - current_size))
        if current_size
        else _UNKNOWN_SIZE
    )

    humanized_total = (
        _HUMANINZED_FORMAT % (total_length / _KILOBYTE / _KILOBYTE) + _STR_MEGABYTE
    )
    humanized_n = _HUMANINZED_FORMAT % n_to_mb + _STR_MEGABYTE

    return _DISPLAY_FORMAT % (
        bar,
        humanized_n,
        humanized_total,
        percentage,
        elapsed_str,
        left_str,
        rate,
    )


def main():
    client = Minio(
        f"{MINIO_IP}:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False,
    )

    result = client.fput_object(
        f"{args.BUCKET or 'annotateddata'}",
        f"{args.FILE}",
        f"{args.FILE}",
        progress=Progress(),
    )
    print(
        "\ncreated {0} object; etag: {1}, version-id: {2}".format(
            result.object_name,
            result.etag,
            result.version_id,
        ),
    )


if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)
