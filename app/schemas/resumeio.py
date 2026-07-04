"""Resume.io schemas - Shakkar Daddy."""

__author__ = "Shakkar Daddy"

from enum import Enum


class Extension(str, Enum):
    jpeg = "jpeg"
    png = "png"
    webp = "webp"
