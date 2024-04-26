import os
import urllib.parse


def main():
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # Get all directories in the parent directory
    data: dict[str, list[str]] = {}
    for d in os.listdir(os.path.join(current_dir, "..")):
        if not os.path.isdir(os.path.join(current_dir, "..", d)):
            continue
        if d.startswith("."):
            continue
            
        # Get all png files in the directory
        files = [f for f in os.listdir(os.path.join(current_dir, "..", d)) if f.endswith(".png")]
        if not files:
            continue

        data[d] = files
    
    # Generate markdown table
    columnWidth = max(len(name) for name in data.keys())

    markdown = "| Name | Image |\n"
    markdown += '|-------------------------------|--------|\n'

    for name, images in data.items():
        markdown += f"| {name.ljust(columnWidth)} | "
        for image in images:
            url = urllib.parse.quote(f"../{name}/{image}")
            markdown += f'<img src="{url}" width="100" /> '
        markdown += "|\n"
    
    print(markdown)


if __name__ == "__main__":
    main()
