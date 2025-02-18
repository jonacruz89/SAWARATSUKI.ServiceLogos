from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias
from urllib.parse import quote

from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern

FolderDict: TypeAlias = dict[str, list[Path]]


@dataclass
class ReadMeInfo:
    path: Path
    locale: str


DOCS_FOLDER = Path(__file__).parent.parent
ROOT_FOLDER = DOCS_FOLDER.parent

START = "<!-- image-list: start -->"
END = "<!-- image-list: end -->"


LOCALE: dict[str, dict[str, str]] = {
    "en": {"name": "Name", "image": "Image"},
    "ja": {"name": "名前", "image": "画像"},
    "zhHans": {"name": "名称", "image": "图片"},
    "zhHant": {"name": "名稱", "image": "圖片"},
    "es": {"name": "Nombre", "image": "Imagen"},
}

GIT_IGNORE = PathSpec.from_lines(
    GitWildMatchPattern,
    [
        *(ROOT_FOLDER / ".gitignore").read_text("u8").splitlines(),
        "docs",
    ],
)


def l5(n: str | None, k: str) -> str:
    if n:
        with suppress(KeyError):
            return LOCALE[n][k]
    with suppress(KeyError):
        return LOCALE["en"][k]
    return k


def md_escape(txt: str) -> str:
    chars = ["\\", "`", "*", "_", "{", "}", "[", "]", "(", ")", "#", "+", "-", ".", "!"]
    for char in chars:
        txt = txt.replace(char, rf"\{char}")
    return txt


def to_root_relative(p: Path) -> str:
    return p.relative_to(ROOT_FOLDER).as_posix()


def is_in_gitignore(p: Path) -> bool:
    return GIT_IGNORE.match_file(p)


def find_image_folders() -> FolderDict:
    folders: FolderDict = {}

    for x in ROOT_FOLDER.iterdir():
        if (
            (not x.is_dir())
            or (is_in_gitignore(x))
            or (not (images := list(x.glob("**/*.png"))))
        ):
            continue

        # ensure matched paths are not folders ends with .png
        images = (x for x in images if not (x.is_dir() or is_in_gitignore(x)))
        for image in images:
            name = to_root_relative(image.parent)
            if name not in folders:
                folders[name] = [image]
            else:
                folders[name].append(image)

    return folders


def find_readme() -> list[ReadMeInfo]:
    return [
        ReadMeInfo(
            path=x,
            locale=(n[n.index("-") + 1 :] if "-" in (n := x.stem) else "en"),
        )
        for x in DOCS_FOLDER.glob("README*.md")
    ]


def generate_markdown(folders: FolderDict, locale: str | None = None) -> str:
    def get_image_tags(images: list[Path]) -> str:
        return " ".join(
            (
                f'<img src="../{quote(to_root_relative(x))}" '
                f'alt="{quote(x.stem)}" width="100" />'
            )
            for x in images
        )

    item_list = [
        (
            folder,
            sorted(  # move exact match to first
                images,
                key=lambda x: "\0" if x.stem == folder else x.stem.lower(),
            ),
        )
        for folder, images in sorted(folders.items(), key=lambda x: x[0].lower())
    ]
    lines = [
        f"| {l5(locale, 'name')} | {l5(locale, 'image')} |",
        "| --- | --- |",
        *(
            f"| [{md_escape(folder)}](/{quote(folder)}) | {get_image_tags(images)} |"
            for folder, images in item_list
        ),
    ]
    return "\n".join(lines)


def replace_file(content: str, inner: str) -> str:
    start_index = content.find(START)
    end_index = content.find(END)
    if start_index == -1 or end_index == -1 or start_index >= end_index:
        raise ValueError("Invalid table start or end mark")

    pfx = content[: start_index + len(START)]
    sfx = content[end_index:]
    return f"{pfx}\n\n{inner}\n\n{sfx}"


def process_file(info: ReadMeInfo, image_folders: FolderDict):
    md_table = generate_markdown(image_folders, info.locale)
    content = info.path.read_text("u8")
    try:
        replaced = replace_file(content, md_table)
    except ValueError as e:
        raise ValueError(f"Error replacing {info.path.name}") from e
    info.path.write_text(replaced, "u8")


def main():
    image_folders = find_image_folders()
    print(f"Found {len(image_folders)} image folders")
    readme_files = find_readme()
    for info in readme_files:
        print(f"Processing {info.path.name}, locale: {info.locale}")
        process_file(info, image_folders)


if __name__ == "__main__":
    main()
