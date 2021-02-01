import os
from contextlib import suppress
from distutils.command.build import build

from django.core import management
from setuptools import find_packages, setup

from pretix_twilio import __version__


try:
    with open(
        os.path.join(os.path.dirname(__file__), "README.rst"), encoding="utf-8"
    ) as f:
        long_description = f.read()
except Exception:
    long_description = ""


class CustomBuild(build):
    def run(self):
        with suppress(Exception):
            management.call_command("compilemessages", verbosity=1)
        build.run(self)


cmdclass = {"build": CustomBuild}


setup(
    name="pretix-twilio",
    version=__version__,
    description="Additionally to sending emails with pretix, send SMS to your customers with Twilio! Uses the built-in phone number field.",
    long_description=long_description,
    url="https://github.com/rixx/pretix-twilio",
    author="Tobias Kunze",
    author_email="r@rixx.de",
    license="Apache",
    install_requires=[
        "twilio",
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points="""
[pretix.plugin]
pretix_twilio=pretix_twilio:PretixPluginMeta
""",
)
