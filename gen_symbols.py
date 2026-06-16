#!/usr/bin/env python3
"""
gen_symbols.py - KiCad symbol generator matching the custom footprints used
                 on the Freezer Monitor board (U1 module + BT1 holder)

Version:    1.0.0
Date:       2026-06-16
Author:     Kyle Meeks (UIHC) / generated with Claude
Description:
    Emits freezer_monitor.kicad_sym containing two symbols whose pin NUMBERS
    equal the footprint PAD NAMES verbatim, so symbol<->footprint mapping
    connects through to the right pads:

      - nice_nano_teyleten : 24 pins. Pin numbers are the pad names from
        gen_nicenano_footprint.py (LEFT/RIGHT below MUST match that script).
        The three GND pads share one symbol pin numbered "GND" (KiCad maps a
        single pin to all same-named pads). Footprint field pre-set to the
        flipped variant actually on the board.

      - BAT_1011 : 2 pins numbered "P"(+) / "N"(-) to match BAT_1011.kicad_mod.

    Standard parts (R1-R3, C1, C2, J1, J2, JP1) use stock KiCad symbols - their
    pad numbers (1/2, 1/2/3, 1/2/3/4) already match the stock symbol pins.

    All pins are type 'passive' to keep ERC quiet (no power-flag chasing).
    Change types later if you want stricter ERC.

Version history:
    1.0.0  2026-06-16  Initial. Pad lists mirror gen_nicenano_footprint.py 1.1.1.
"""

# MUST stay identical to gen_nicenano_footprint.py
LEFT  = ["B-","P0.06","P0.08","GND","GND","P0.17","P0.20","P0.22",
         "P0.24","P1.00","P0.11","P1.04","P1.06"]
RIGHT = ["B+","RAW","GND","RST","VCC","P0.31","P0.29","P0.02",
         "P1.15","P1.13","P1.11","P0.09","P0.10"]

FP_U1  = "nice!nano clone:nice_nano_teyleten_usb_flipped"
FP_BAT = "nice!nano clone:BAT_1011"
PITCH  = 2.54

def dedupe(seq, seen):
    out=[]
    for n in seq:
        if n in seen: continue
        seen.add(n); out.append(n)
    return out

def pin(num, name, x, y, angle):
    return (f'\t\t\t(pin passive line (at {x:.2f} {y:.2f} {angle}) (length 2.54)\n'
            f'\t\t\t\t(name "{name}" (effects (font (size 1.27 1.27))))\n'
            f'\t\t\t\t(number "{num}" (effects (font (size 1.27 1.27))))\n'
            f'\t\t\t)\n')

def prop(key, val, x, y, hide=False):
    h = " (hide yes)" if hide else ""
    return (f'\t\t(property "{key}" "{val}"\n'
            f'\t\t\t(at {x:.2f} {y:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)){h})\n'
            f'\t\t)\n')

def nicenano_symbol():
    seen=set()
    L = dedupe(LEFT, seen)      # 12, GND kept here
    R = dedupe(RIGHT, seen)     # 12, GND already consumed
    nrows = max(len(L), len(R))
    top = (nrows-1)*PITCH/2.0
    bx = 12.7                    # body half width
    by = top + PITCH/2.0         # body half height
    s=[]
    s.append('\t(symbol "nice_nano_teyleten"\n')
    s.append('\t\t(pin_names (offset 1.016))\n')
    s.append('\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n')
    s.append(prop("Reference","U",0,by+1.5))
    s.append(prop("Value","nice_nano_teyleten",0,-by-1.5))
    s.append(prop("Footprint",FP_U1,0,0,hide=True))
    s.append(prop("Datasheet","",0,0,hide=True))
    s.append(prop("Description","Teyleten nRF52840 Pro Micro clone (B+/B- on header)",0,0,hide=True))
    s.append('\t\t(symbol "nice_nano_teyleten_0_1"\n')
    s.append(f'\t\t\t(rectangle (start {-bx:.2f} {by:.2f}) (end {bx:.2f} {-by:.2f})\n'
             '\t\t\t\t(stroke (width 0.254) (type default)) (fill (type background)))\n')
    s.append('\t\t)\n')
    s.append('\t\t(symbol "nice_nano_teyleten_1_1"\n')
    for i,nm in enumerate(L):
        s.append(pin(nm, nm, -(bx+2.54), top - i*PITCH, 0))
    for i,nm in enumerate(R):
        s.append(pin(nm, nm,  (bx+2.54), top - i*PITCH, 180))
    s.append('\t\t)\n')
    s.append('\t)\n')
    return "".join(s), len(L)+len(R)

def bat_symbol():
    s=[]
    s.append('\t(symbol "BAT_1011"\n')
    s.append('\t\t(pin_names (offset 1.016))\n')
    s.append('\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n')
    s.append(prop("Reference","BT",0,4.0))
    s.append(prop("Value","LS14250",0,-4.0))
    s.append(prop("Footprint",FP_BAT,0,0,hide=True))
    s.append(prop("Datasheet","",0,0,hide=True))
    s.append('\t\t(symbol "BAT_1011_0_1"\n')
    s.append('\t\t\t(rectangle (start -5.08 2.54) (end 5.08 -2.54)\n'
             '\t\t\t\t(stroke (width 0.254) (type default)) (fill (type background)))\n')
    s.append('\t\t)\n')
    s.append('\t\t(symbol "BAT_1011_1_1"\n')
    s.append(pin("P","+",-7.62,0,0))
    s.append(pin("N","-", 7.62,0,180))
    s.append('\t\t)\n')
    s.append('\t)\n')
    return "".join(s)

if __name__ == "__main__":
    out=[]
    out.append('(kicad_symbol_lib\n')
    out.append('\t(version 20231120)\n')
    out.append('\t(generator "gen_symbols.py")\n')
    out.append('\t(generator_version "1.0")\n')
    nn, npins = nicenano_symbol()
    out.append(nn)
    out.append(bat_symbol())
    out.append(')\n')
    txt="".join(out)
    assert txt.count("(")==txt.count(")"), "unbalanced parens!"
    need={"B+","B-","P0.24","P0.02","P0.06","P0.08","P1.06","GND"}
    have=set(LEFT)|set(RIGHT)
    print("nice!nano pins:", npins, "(24 expected: 26 pads, 3 GND -> 1)")
    print("netlist pins present:", "OK" if need<=have else f"MISSING {need-have}")
    print("BAT pins: P(+), N(-)  ->", "matches BAT_1011.kicad_mod" )
    open("freezer_monitor.kicad_sym","w").write(txt)
    print(f"paren balance OK; wrote freezer_monitor.kicad_sym ({len(txt)} bytes)")
