"""Validate local Markdown link targets and SVG XML without network access."""

from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


root = Path(__file__).resolve().parent.parent
tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
errors = []
checked_links = 0
checked_svg = 0

for name in filter(None, tracked):
    path = root / name
    if path.suffix == ".svg":
        try:
            document = ET.parse(path)
            if document.getroot().tag != "{http://www.w3.org/2000/svg}svg":
                errors.append(f"{name}: root must be an SVG element")
            checked_svg += 1
        except ET.ParseError as error:
            errors.append(f"{name}: {error}")
    if path.suffix != ".md":
        continue
    # Inline links are the convention in this repository. Ignore fenced examples.
    markdown = re.sub(r"```.*?```", "", path.read_text(), flags=re.S)
    for match in re.finditer(r"!?\[[^\]]*\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)", markdown):
        target = urlsplit(match.group(1).strip("<>"))
        if target.scheme or target.netloc or not target.path:
            continue
        local = (root / unquote(target.path).lstrip("/") if target.path.startswith("/")
                 else path.parent / unquote(target.path)).resolve()
        if not local.is_relative_to(root) or not local.exists():
            errors.append(f"{name}: missing local link {match.group(1)}")
        checked_links += 1

if errors:
    raise SystemExit("\n".join(errors))
print(f"Validated {checked_links} local Markdown links and {checked_svg} SVG files.")
