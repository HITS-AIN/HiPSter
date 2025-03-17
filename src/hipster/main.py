from typing import Optional

from jsonargparse import auto_cli

from hipster.hips_generator import HiPSGenerator


def main(
    url: str = "http://localhost:8083",
    title: str = "gaia",
    hips: Optional[HiPSGenerator] = None,
):
    print(url)


if __name__ == "__main__":
    auto_cli(main)
