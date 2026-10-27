# Office 2.0 · Floor Tycoon · employee game v2.4 (27 Oct 2026)

`index.html` is the whole game in one file (about 10.9 MB, everything inlined). Open it in a phone browser, or serve the folder as a static site. Add `?site=<code>` to tag results by office site.

**v2.4 = v2.3 with the approved "Soft" palette.** Nothing else changed: same V8 question set (Option 1, 32 questions, wording verbatim), same scenes, flow, layout, saving and results hook.

## What changed
- **Scene backdrops and floors** (the 23 scene images): saturation down about 35%, slightly lighter. Orange arrival floor → warm sand, lime grass → sage, rust Meals floor → clay.
- **Sprites, player figures, answer tiles, thank-you hero** (136 images): saturation down about 20%, a touch lighter, so answers still read clearly.
- **UI and scene-sign colours** (CSS and scene data): saturation down about 22% with lightness unchanged, so text contrast on the signs is the same as v2.3.

| Scene | v2.3 | v2.4 |
|---|---|---|
| 1 About me | #2F49C8 | #3751B1 |
| 2 Arriving and settling in | #E0684B | #D1745D |
| 3 The morning meeting | #5E9A1E | #689641 |
| 4 My team | #2F8F86 | #468C84 |
| 5 Where my day goes | #D9961A | #CE9A4C |
| 6 Calls and meetings | #2F6FD0 | #4172BC |
| 7 Spaces I use | #C9822F | #BE874D |
| 8 Visiting the customer site | #3B4FBF | #4155AA |
| 9 Breaks | #4F8C1E | #5A893C |
| 10 Meals | #C4572E | #B66244 |
| 11 Last word | #B0345A | #A3455D |

## How it was made
`tools/soften.py` rebuilds the palette from v2.3 in one pass (OKLab chroma scaling, near-greys and ink untouched):

```
python3 tools/soften.py office2-v8-employee-v2.3.html index.html \
  --env 0.65,0.05,0 --spr 0.80,0.03,0 --ui 0.78,0,0
```
Values are chroma,lift,warm per group (scene images, sprites, hex colours). The "Softer" option reviewed alongside used `--env 0.50,0.08,0.03 --spr 0.70,0.05,0 --ui 0.68,0,0`.

## Checked
Automated play-through in a 393×852 phone viewport, Start → Finish → thank-you screen, no script errors.
