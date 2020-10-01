#!/usr/bin/env python
import sys
from pathlib import Path
import os
import subprocess

from prompt_toolkit import print_formatted_text as print, HTML
from prompt_toolkit.styles import NAMED_COLORS, ANSI_COLOR_NAMES, Style

INTERNET_TEST_URL = "archlinux.org"

style = Style.from_dict({"error": "fg:ansibrightred"})


def print_error(text):
    print(HTML(f"<error>{text}</error>"), file=sys.stderr, style=style)


def is_uefi() -> bool:
    return os.path.exists("/sys/firmware/efi/efivars")


def is_internet_accessible() -> bool:
    ping_success = (
        subprocess.run(["ping", "-c", "1", INTERNET_TEST_URL]).returncode == 0
    )
    return ping_success


def enable_ntp():
    """
    Enables NTP if possible.
    :raises: subprocess.CalledProcessError if NTP could not be enabled.
    """
    return subprocess.run(["timesdatectl", "set-ntp", "true"], check=True)


def get_installation_disk_choices():
    excluded_device_types = [
        7, # loop
        11, # cd_rom
        230, # zfs zvols
    ]

    disk_entries = (
        subprocess.run(
            [
                "lsblk",
                "--paths",
                "--nodeps" "--noheadings",
                "--list",
                "--exclude",
                ",".join(str(e) for e in excluded_device_types),
                # Not passing in -S since that seems to exclude NVMe devices
            ],
            stdout=subprocess.PIPE,
        )
        .stdout.decode()
        .split("\n")
    )


def main():
    print_error("Starting")
    if not is_uefi():
        print_error("EFI not detected. This script only works with EFI systems.")
        sys.exit(1)

    if not is_internet_accessible():
        print_error(
            "Internet inaccessible. Internet access is required for installation"
        )
        sys.exit(1)

    try:
        enable_ntp()
    except subprocess.CalledProcessError:
        print_error("Unable to enable NTP. Accurate time is required for installation")
        sys.exit(1)


if __name__ == "__main__":
    main()
