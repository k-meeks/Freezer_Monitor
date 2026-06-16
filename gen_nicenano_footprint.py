#!/usr/bin/env python3
"""
gen_nicenano_footprint.py - KiCad footprint generator for the Teyleten
                                                        nRF52840 Pro Micro (nice!nano-form clone)

Version:    1.1.1
Date:       2026-06-16
Author:     Kyle Meeks (UIHC) / generated with Claude
Description:
        Emits through-hole .kicad_mod footprints for the *specific* Teyleten
        nRF52840 board (NOT a generic nice!nano - this clone brings B+/B- out to
        the edge header, which the genuine module does not).

        This script writes both:
            - nice_nano_teyleten.kicad_mod
            - nice_nano_teyleten_usb_flipped.kicad_mod

        The flipped variant keeps identical pad names and applies a true 180deg
        rotation mapping (swap left/right + reverse top/bottom order) so the
        USB/B+/B- end is at the opposite end of the board layout.

        Geometry is parametric. Verify ROW_SPACING against the physical board
        (outside-edge of a left pad to outside-edge of the opposite right pad,
        minus one pad width ~0.63 mm) before ordering.

Measured (2026-06-16):
        - Board: 32.93 x 17.84 mm
        - 13 pins/row, outside pin1->pin13 = 31 mm, pin = 0.64 mm square (0.025")
            => pitch = (31 - 0.63) / 12 = 2.53 ~= 2.54 mm (standard 0.1")
        - ROW_SPACING assumed 0.6" (15.24 mm) - VERIFY.

        Center pads (P1.01/P1.02/P1.07 + SWD VDD/DIO/CLK/GND) are omitted: unused
        by this design and not positionable from a photo. Add by measurement if
        ever needed.

Version history:
        1.0.0  2026-06-16  Initial, from physical board photos + calipers.
        1.1.0  2026-06-16  Emit both normal + USB-flipped footprint variants.
    1.1.1  2026-06-16  Fix flipped variant to true 180deg rotation
               (not top/bottom mirror only).
"""

# --- parameters --------------------------------------------------------------
NAME        = "nice_nano_teyleten"
FLIPPED_NAME = "nice_nano_teyleten_usb_flipped"
PITCH       = 2.54     # mm, locked
ROW_SPACING = 15.24    # mm (0.6") - VERIFY against board
PINS        = 13
PAD_DIA     = 1.70     # mm pad outer diameter
DRILL       = 1.00     # mm (fits machine-pin socket tails; match your socket)
BOARD_L     = 32.93    # mm (USB-to-tail, Y)
BOARD_W     = 17.84    # mm (X)

# pin 1 = USB end (top). Order top -> bottom.
LEFT  = ["B-","P0.06","P0.08","GND","GND","P0.17","P0.20","P0.22",
         "P0.24","P1.00","P0.11","P1.04","P1.06"]
RIGHT = ["B+","RAW","GND","RST","VCC","P0.31","P0.29","P0.02",
         "P1.15","P1.13","P1.11","P0.09","P0.10"]
# -----------------------------------------------------------------------------

def pin_y(n):
    span = (PINS - 1) * PITCH
    return -span / 2.0 + n * PITCH   # n = 0..PINS-1, pin1 at top (-Y)

def pad(name, x, y, shape):
    return (
        f'\t(pad "{name}" thru_hole {shape}\n'
        f'\t\t(at {x:.3f} {y:.3f})\n'
        f'\t\t(size {PAD_DIA} {PAD_DIA})\n'
        f'\t\t(drill {DRILL})\n'
        f'\t\t(layers "*.Cu" "*.Mask")\n'
        f'\t)\n'
    )

def line(x1, y1, x2, y2, layer, w=0.12):
    return (f'\t(fp_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f})\n'
            f'\t\t(stroke (width {w}) (type solid)) (layer "{layer}"))\n')

def build(name, left_pads, right_pads):
    hx, hy = BOARD_W / 2.0, BOARD_L / 2.0
    cx, cy = hx + 0.25, hy + 0.25   # courtyard margin
    out = []
    out.append(f'(footprint "{name}"\n')
    out.append('\t(version 20240108)\n')
    out.append('\t(generator "gen_nicenano_footprint.py")\n')
    out.append('\t(generator_version "1.1.1")\n')
    out.append('\t(layer "F.Cu")\n')
    out.append('\t(attr through_hole)\n')
    out.append(f'\t(fp_text reference "U**" (at 0 {-hy-1.2:.3f}) (layer "F.SilkS")\n'
               '\t\t(effects (font (size 1 1) (thickness 0.15))))\n')
    out.append(f'\t(fp_text value "{name}" (at 0 {hy+1.2:.3f}) (layer "F.Fab")\n'
               '\t\t(effects (font (size 1 1) (thickness 0.15))))\n')
    # fab + silk outline
    for layer, w in (("F.Fab", 0.10), ("F.SilkS", 0.12)):
        out.append(line(-hx, -hy,  hx, -hy, layer, w))
        out.append(line( hx, -hy,  hx,  hy, layer, w))
        out.append(line( hx,  hy, -hx,  hy, layer, w))
        out.append(line(-hx,  hy, -hx, -hy, layer, w))
    # courtyard
    out.append(line(-cx, -cy,  cx, -cy, "F.CrtYd", 0.05))
    out.append(line( cx, -cy,  cx,  cy, "F.CrtYd", 0.05))
    out.append(line( cx,  cy, -cx,  cy, "F.CrtYd", 0.05))
    out.append(line(-cx,  cy, -cx, -cy, "F.CrtYd", 0.05))
    # pin-1 style marker: place triangle by B- so it's meaningful in both
    # normal and rotated variants.
    if "B-" in left_pads:
        bminus_y = pin_y(left_pads.index("B-"))
        mx = -ROW_SPACING/2.0 - PAD_DIA/2.0 - 0.4
        out.append(line(mx-0.5, bminus_y-0.5, mx-0.5, bminus_y+0.5, "F.SilkS"))
        out.append(line(mx-0.5, bminus_y-0.5, mx+0.3, bminus_y,     "F.SilkS"))
        out.append(line(mx-0.5, bminus_y+0.5, mx+0.3, bminus_y,     "F.SilkS"))
    else:
        bminus_y = pin_y(right_pads.index("B-"))
        mx = ROW_SPACING/2.0 + PAD_DIA/2.0 + 0.4
        out.append(line(mx+0.5, bminus_y-0.5, mx+0.5, bminus_y+0.5, "F.SilkS"))
        out.append(line(mx+0.5, bminus_y-0.5, mx-0.3, bminus_y,     "F.SilkS"))
        out.append(line(mx+0.5, bminus_y+0.5, mx-0.3, bminus_y,     "F.SilkS"))
    # pads
    xL = -ROW_SPACING / 2.0
    xR =  ROW_SPACING / 2.0
    for i, nm in enumerate(left_pads):
        shape = "rect" if nm == "B-" else "circle"
        out.append(pad(nm, xL, pin_y(i), shape))
    for i, nm in enumerate(right_pads):
        shape = "rect" if nm == "B-" else "circle"
        out.append(pad(nm, xR, pin_y(i), shape))
    out.append(')\n')
    return "".join(out)

if __name__ == "__main__":
    derived_pitch = (31 - 0.63) / 12
    print(f"derived pitch from calipers: {derived_pitch:.3f} mm  (using {PITCH})")
    print(f"row spacing (VERIFY): {ROW_SPACING} mm")
    print(f"pads: left={len(LEFT)} right={len(RIGHT)} total={len(LEFT)+len(RIGHT)}")
    names = LEFT + RIGHT
    need = {"B+","B-","P0.24","P0.02","P0.06","P0.08","P1.06","GND"}
    missing = need - set(names)
    print("netlist pins present:", "OK" if not missing else f"MISSING {missing}")
    normal = build(NAME, LEFT, RIGHT)
    flipped = build(FLIPPED_NAME, list(reversed(RIGHT)), list(reversed(LEFT)))

    assert normal.count("(") == normal.count(")"), "normal footprint has unbalanced parens!"
    assert flipped.count("(") == flipped.count(")"), "flipped footprint has unbalanced parens!"

    open(f"{NAME}.kicad_mod", "w").write(normal)
    open(f"{FLIPPED_NAME}.kicad_mod", "w").write(flipped)

    print(f"paren balance OK; wrote {NAME}.kicad_mod ({len(normal)} bytes)")
    print(f"paren balance OK; wrote {FLIPPED_NAME}.kicad_mod ({len(flipped)} bytes)")
