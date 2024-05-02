import os

if os.getenv("GITHUB_ACTIONS") != "true":
    print("This script is intended to be run in GitHub Actions.")
    exit(1)

# ------

import locale
from subprocess import DEVNULL, PIPE, Popen
from typing import cast
from uuid import uuid4

from githubkit import GitHub
from githubkit.versions.v2022_11_28.models import Release

ENC = locale.getpreferredencoding()

NAME = {
    "A": "Added",
    "C": "Copied",
    "M": "Modified",
    "R": "Renamed",
    "D": "Deleted",
}

gh = GitHub(os.environ["GITHUB_TOKEN"])
gh_sha = os.environ["GITHUB_SHA"]
gh_sha_short = gh_sha[:7]
gh_ref_name = os.environ["GITHUB_REF_NAME"]
gh_repo_str = os.environ["GITHUB_REPOSITORY"]
gh_repo = cast(
    tuple[str, str],
    tuple(gh_repo_str.split("/", 1)),
)
gh_output_path = os.environ["GITHUB_OUTPUT"]

tag_suffix = f"_{gh_ref_name}"


def set_output(key: str, value: str):
    delimiter = f"ghadelimiter_{uuid4()}"
    if delimiter in value:
        raise ValueError(f"Delimiter {delimiter} found in value {value!r}")
    string = f"{key}<<{delimiter}\n{value}\n{delimiter}\n".replace("\n", os.linesep)
    with open(gh_output_path, "a", encoding="u8") as f:  # noqa: PTH123
        f.write(string)


def decode(s: bytes) -> str:
    try:
        return s.decode()
    except UnicodeDecodeError:
        return s.decode(ENC, errors="replace")


def run(cmd: list[str]) -> str:
    proc = Popen(cmd, stdin=DEVNULL, stdout=PIPE, stderr=PIPE)  # noqa: S603
    code = proc.wait()
    stdout_b, stderr_b = proc.communicate()
    stdout = decode(stdout_b)
    if code:
        stderr = decode(stderr_b)
        raise RuntimeError(
            f"Command {cmd} failed with code {code}\n"
            f"Err:\n"
            f"{stderr.rstrip()}\n"
            f"Out:\n"
            f"{stdout.rstrip()}",
        )
    return stdout.strip()


def find_parent_release() -> Release | None:
    # check latest release first
    release = gh.rest.repos.get_latest_release(*gh_repo).parsed_data
    if release.tag_name.endswith(tag_suffix):
        return release

    for page in range(1, 4):  # find 3 pages max
        release_list = gh.rest.repos.list_releases(*gh_repo, page=page).parsed_data
        if not release_list:
            break

        release = next(
            (
                release
                for release in release_list
                if release.tag_name.endswith(tag_suffix)
            ),
            None,
        )
        if release:
            return release

    return None


def main():
    print(f"Getting latest release on branch {gh_ref_name} by tag name")
    parent_release = find_parent_release()
    if parent_release:
        print(f"Latest release found: {parent_release.tag_name}")
        parent_sha = parent_release.target_commitish
    else:
        print("No release satisfied, will compare this commit with parent commit.")
        parent_sha = run(["git", "rev-parse", f"{gh_sha}^"])

    order = list(NAME.keys())
    print(f"Comparing {parent_sha}..{gh_sha}")
    try:
        diff = run(
            [
                "git",
                "diff",
                "--name-status",
                "--ignore-submodules=all",
                f"--diff-filter={''.join(order)}",
                f"{parent_sha}..{gh_sha}",
            ],
        )
    except RuntimeError as e:
        print("Failed to get difference between parent release.")
        print(e)
        exit(1)

    diff_splitted = sorted(
        (
            (splitted[0][0], *splitted[1:])
            for line in diff.splitlines()
            if (
                line
                and len(splitted := line.split("\t", maxsplit=2)) > 1
                and splitted[1].endswith(".png")
            )
        ),
        key=lambda x: order.index(x[0]),
    )
    if not diff_splitted:
        print("No image changes detected.")
        if parent_release:
            print("Parent release found but no changes detected, will exit.")
            return

    changelog = "\n".join(
        [
            f"- **{NAME.get(status)}**: {' -> '.join(f'`{x}`' for x in rest)}"
            for status, *rest in diff_splitted
        ],
    )
    if not parent_release:
        print("No parent release found, should create initial release.")
        changelog = f"Initial release.\n\n{changelog}"
    else:
        parent_sha_short = parent_sha[:7]
        changelog += (
            f"\n\n**Full Changelog**: "
            f"https://github.com/{gh_repo_str}/compare/{parent_sha_short}...{gh_sha_short}"
        )

    set_output("should_run", "true")
    set_output("name", f"Release {gh_sha_short} on {gh_ref_name}")
    set_output("tag_name", f"{gh_sha_short}{tag_suffix}")
    set_output("body", changelog)


if __name__ == "__main__":
    main()
