import locale
from pathlib import Path
from subprocess import PIPE, Popen

ENC = locale.getpreferredencoding()

NAME = {
    "A": "Added",
    "C": "Copied",
    "M": "Modified",
    "R": "Renamed",
    "D": "Deleted",
}


def decode(s: bytes) -> str:
    try:
        return s.decode()
    except UnicodeDecodeError:
        return s.decode(ENC, errors="replace")


def run(cmd: list[str]) -> str:
    out = decode(Popen(cmd, stdout=PIPE).communicate()[0])  # noqa: S603
    # print(out)
    return out  # noqa: RET504


def main():
    current_sha = run(["git", "show", "-s", "--format=%H"]).strip()
    parent_sha = run(["git", "rev-parse", f"{current_sha}^"]).strip()
    print(f"Comparing {parent_sha}..{current_sha}")

    order = list(NAME.keys())
    diff = run(
        [
            "git",
            "diff",
            "--name-status",
            "--ignore-submodules=all",
            f"--diff-filter={''.join(order)}",
            f"{parent_sha}..{current_sha}",
        ],
    )
    diff_spiltted = sorted(
        [
            splitted
            for line in diff.splitlines()
            if (
                line
                and len(splitted := line.split("\t")) > 1
                and splitted[1].endswith(".png")
            )
        ],
        key=lambda x: order.index(x[0][0]),
    )
    if not diff_spiltted:
        print("No image changes detected.")
        return

    changelog = "\n".join(
        [
            f"- **{NAME.get(status[0])}**: {' -> '.join(f'`{x}`' for x in rest)}"
            for status, *rest in diff_spiltted
        ],
    )
    print(changelog)
    Path("changelog.md").write_text(changelog, "u8")


if __name__ == "__main__":
    main()
