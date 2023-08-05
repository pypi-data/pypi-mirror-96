import distutils.cmd
import sys
import os
from enum import Enum

from pkg_resources import DistributionNotFound, Requirement, get_distribution


class Env(Enum):
    INSTALL = "install"
    TESTS = "tests"
    DEVELOP = "develop"

    @property
    def path(self):
        return f"./.pip-pin/{self.value}.txt"

class Command(distutils.cmd.Command):
    user_options = [
        ("install", "i", "Use install dependencies"),
        ("tests", "t", "Use test dependencies"),
        ("develop", "d", "Use develop dependencies"),
    ]

    def initialize_options(self):
        self.install = False
        self.tests = False
        self.develop = False

    def finalize_options(self):
        self.install = self.install or not any([self.tests, self.develop])

    @property
    def envs(self):
        if self.tests:
            yield Env.TESTS

        if self.develop:
            yield Env.DEVELOP

        if self.install:
            yield Env.INSTALL

    @property
    def reqs(self):
        def parse(reqs):
            return [Requirement.parse(r) for r in reqs]

        return {
            Env.INSTALL: parse(self.distribution.install_requires),
            Env.TESTS: parse(self.distribution.tests_require),
            Env.DEVELOP: parse(self.distribution.develop_requires),
        }


class Sync(Command):
    description = "Pippin sync"

    def initialize_options(self):
        super().initialize_options()

    def run(self):
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
        ]

        for env in self.envs:
            self.announce(f"{env.value}: -r {env.path}")
            self.spawn(
                cmd + ["-r", os.path.abspath(env.path)]
            )


class Pin(Command):
    description = "Pippin pin"

    def walk(self, req, pins):
        # don't pin setuptools
        if req.name == 'setuptools':
            return

        dist = get_distribution(req.name)

        pins.update({self.walk(r, pins) for r in dist.requires(extras=req.extras)})

        # ignore version if req specifies a direct url
        req.specifier = dist.as_requirement().specifier if req.url is None else None
        req.marker = None
        return req

    def run(self):
        for env in self.envs:
            pins = set()

            for r in self.reqs[env]:
                pins.add(self.walk(r, pins))

            self.announce(f"# {env.path}")

            pins = list(sorted(set(str(pin) for pin in pins if pin)))
            for pin in pins:
                self.announce(pin)

            if self.dry_run:
                sys.stderr.write(f"# {env.path}\n")
                sys.stderr.write("\n".join(pins))
                sys.stderr.write("\n")
                continue

            try:
                os.mkdir(os.path.dirname(env.path))
            except FileExistsError:
                pass

            with open(env.path, "w") as f:
                if env == Env.TESTS:
                    f.write(f"-r install.txt\n-c install.txt\n")
                if env == Env.DEVELOP:
                    f.write(f"-r tests.txt\n-c tests.txt\n")

                f.write("\n".join(pins))
                f.write("\n")


def validate_develop_requires(*args):
    pass
