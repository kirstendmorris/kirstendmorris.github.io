#!/usr/bin/env python3
"""Prepare travel photos for the website.

Usage
-----
    python3 bin/travel_photos.py <trip-name> PHOTO [PHOTO ...] [--place "Mexico"] [--date 2026-10-20]

Example
-------
    python3 bin/travel_photos.py 2026-10-mexico ~/Pictures/Mexico/*.jpg --place Mexico --date 2026-10-20

What it does, for each photo:
  * turns it the right way up (phones store rotation as a tag),
  * shrinks it so the long side is at most 1800 px (a 4 MB phone photo becomes ~300 KB),
  * removes all metadata, including GPS location, camera and timestamps,
  * saves it as a JPEG in assets/img/travel/<trip-name>/.

Then it adds the photos, with their sizes, to _trips/<trip-name>.md,
creating that file if it doesn't exist yet. Re-running with the same photos
skips the ones already there. Add captions by editing the trip file.

Needs Pillow (pip install pillow). For iPhone .HEIC photos also: pip install pillow-heif
"""

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is not installed. Run: pip install pillow")

try:
    import pillow_heif  # optional, for iPhone HEIC files

    pillow_heif.register_heif_opener()
except ImportError:
    pillow_heif = None

LONG_EDGE = 1800
QUALITY = 82
ROOT = Path(__file__).resolve().parent.parent


def slugify(text):
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text or "photo"


def prepare(src, out_dir, taken):
    name = slugify(src.stem) + ".jpg"
    stem, n = name[:-4], 2
    while name in taken:
        name = f"{stem}-{n}.jpg"
        n += 1
    dest = out_dir / name
    if dest.exists():
        with Image.open(dest) as im:
            return name, im.size, False
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        im.thumbnail((LONG_EDGE, LONG_EDGE), Image.LANCZOS)
        # no exif= argument, so no metadata (GPS included) is written
        im.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        return name, im.size, True


def entry(name, size):
    w, h = size
    return f"  - file: {name}\n    w: {w}\n    h: {h}\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("trip", help="trip name used for the folder and page address, e.g. 2026-10-mexico")
    ap.add_argument("photos", nargs="+", type=Path)
    ap.add_argument("--place", help='label on the cover, e.g. "Mexico" (new trips only)')
    ap.add_argument("--date", help="trip date YYYY-MM-DD; sets the month shown and the order (new trips only)")
    args = ap.parse_args()

    trip = slugify(args.trip)
    out_dir = ROOT / "assets" / "img" / "travel" / trip
    out_dir.mkdir(parents=True, exist_ok=True)
    trip_file = ROOT / "_trips" / f"{trip}.md"
    existing = trip_file.read_text() if trip_file.exists() else ""

    taken, new_entries = set(), []
    for src in args.photos:
        if not src.is_file():
            print(f"skip (not a file): {src}")
            continue
        try:
            name, size, made = prepare(src, out_dir, taken)
        except Exception as e:  # unreadable or unsupported format
            hint = " (install pillow-heif for HEIC)" if src.suffix.lower() == ".heic" and not pillow_heif else ""
            print(f"skip {src.name}: {e}{hint}")
            continue
        taken.add(name)
        print(f"{'saved' if made else 'exists'}: {name}  {size[0]}x{size[1]}")
        if f"file: {name}\n" not in existing:
            new_entries.append(entry(name, size))

    if not new_entries:
        print("Trip file unchanged.")
        return

    if not existing:
        date = args.date or dt.date.today().isoformat()
        place = args.place or trip.replace("-", " ").title()
        text = (
            "---\n"
            f"place: {place}\n"
            f"date: {date}\n"
            "# cover: <file name>   # optional; defaults to the first photo\n"
            "# when: Oct–Nov 2026   # optional; replaces the month shown next to the place\n"
            "photos:\n" + "".join(new_entries) + "---\n"
        )
    else:
        # front matter ends at the second '---'; photos is the last key, so append there
        start = existing.index("---")
        end = existing.index("\n---", start + 3) + 1
        head = existing[:end]
        if not head.endswith("\n"):
            head += "\n"
        text = head + "".join(new_entries) + existing[end:]

    trip_file.parent.mkdir(exist_ok=True)
    trip_file.write_text(text)
    print(f"{'Updated' if existing else 'Created'} {trip_file.relative_to(ROOT)} (+{len(new_entries)} photos)")


if __name__ == "__main__":
    main()
