# Travel page: how to add a trip

The Travel tab (`/travel/`) shows one cover photo per trip, newest first.
Clicking a cover opens that trip's photo wall at `/travel/<trip-name>/`.

## 1. Add photos

From the repository folder:

```sh
python3 bin/travel_photos.py 2026-10-mexico ~/Pictures/Mexico/*.jpg --place Mexico --date 2026-10-20
```

This shrinks each photo, turns it the right way up, removes its metadata
(including GPS location), saves it to `assets/img/travel/2026-10-mexico/`,
and creates or updates `_trips/2026-10-mexico.md`.
Run it again later with more photos to add them to the same trip.

It needs Pillow (`pip install pillow`); for iPhone `.HEIC` photos also `pip install pillow-heif`.

## 2. Edit the trip file (optional)

`_trips/2026-10-mexico.md` looks like this:

```yaml
---
place: Mexico # shown on the cover as "Mexico · Oct 2026"
date: 2026-10-20 # gives the month shown and the order of trips
cover: tlaxcala.jpg # optional; defaults to the first photo
when: Oct–Nov 2026 # optional; replaces the automatic "Oct 2026"
photos:
  - file: tlaxcala.jpg
    w: 1800
    h: 1200
    caption: Morning walk before the SMM Congress # optional
  - file: tacos.jpg
    w: 1200
    h: 1800
---
```

- Photos appear in the order listed; reorder lines to rearrange the wall.
- A caption appears when someone clicks the photo. Photos without a caption
  just turn gray when clicked.
- `w` and `h` are the photo's pixel size; the script fills them in. If you add
  a photo by hand, you can leave them out and the page works them out once the
  photo loads (the layout may shift slightly while loading).
- To remove a photo, delete its lines here (and the file from `assets/img/travel/`).
