#!/usr/bin/env python3
"""
gen_freezer_netlist_usb_flipped.py - KiCad netlist generator (USB-end flipped)

Version:    1.0.0
Date:       2026-06-16
Author:     Kyle Meeks (UIHC) / generated with Claude
Description:
    Emits a KiCad-importable netlist (.net) for the freezer-monitor carrier,
    identical electrically to gen_freezer_netlist.py but targeting a footprint
    orientation where the module's USB/B+/B- end is on the opposite end in
    board layout.

    IMPORTANT: KiCad netlists define connectivity, not XY placement/rotation.
    This script encodes the orientation choice by using an alternate U1
    footprint name that should be a flipped version of nice_nano_teyleten with
    the same pad names.

Run:
    python3 gen_freezer_netlist_usb_flipped.py

Output:
    freezer_monitor_usb_flipped.net
"""

KICAD_NETLIST_VERSION = "E"

# ref -> (value, footprint, description)
COMPONENTS = {
    "U1":  (
        "nice!nano nRF52840",
        "nice!nano clone:nice_nano_teyleten_usb_flipped",
        "Teyleten clone, socketed; flipped USB-end orientation",
    ),
    "BT1": (
        "LS14250",
        "nice!nano clone:BAT_1011",
        "Saft Li-SOCl2 3.6V 1/2AA, polarity-keyed holder",
    ),
    "R1":  ("1M", "Resistor_SMD:R_0805_2012Metric", "Divider high side"),
    "R2":  ("1M", "Resistor_SMD:R_0805_2012Metric", "Divider low side"),
    "R3":  ("4.7k", "Resistor_SMD:R_0805_2012Metric", "OneWire pull-up to VBAT"),
    "C1":  (
        "100uF",
        "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm",
        "Al-polymer radial THT, low-leakage low-ESR; size to actual part",
    ),
    "C2":  (
        "10nF",
        "Capacitor_SMD:C_0805_2012Metric",
        "SAADC sampling reservoir at P0.02",
    ),
    "J1":  (
        "DS18B20",
        "Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical",
        "Probe: 1=VDD 2=DATA 3=GND",
    ),
    "J2":  (
        "SERIAL",
        "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
        "Debug UART: 1=GND 2=VCC 3=TX 4=RX",
    ),
    "JP1": (
        "BATT",
        "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
        "Cell isolation jumper - pull before USB",
    ),
}

# net name -> list of (ref, pad)
NETS = {
    "CELL+": [("BT1", "P"), ("JP1", "1")],
    "VBAT":  [("JP1", "2"), ("U1", "B+"), ("C1", "1"),
              ("R1", "1"), ("R3", "1"), ("J1", "1")],
    "GND":   [("BT1", "N"), ("U1", "GND"), ("U1", "B-"), ("C1", "2"),
              ("R2", "2"), ("C2", "2"), ("J1", "3"), ("J2", "1")],
    "DATA":  [("U1", "P0.24"), ("R3", "2"), ("J1", "2")],
    "SENSE": [("U1", "P0.02"), ("R1", "2"), ("R2", "1"), ("C2", "1")],
    "TX":    [("U1", "P0.06"), ("J2", "3")],
    "RX":    [("U1", "P0.08"), ("J2", "4")],
    "VREF":  [("U1", "P1.06"), ("J2", "2")],
}


def emit_netlist():
    lines = []
    lines.append('(export (version "%s")' % KICAD_NETLIST_VERSION)
    lines.append('  (design')
    lines.append('    (source "gen_freezer_netlist_usb_flipped.py")')
    lines.append('    (date "2026-06-16")')
    lines.append('    (tool "gen_freezer_netlist_usb_flipped.py 1.0.0"))')

    lines.append('  (components')
    for ref in sorted(COMPONENTS):
        value, fp, desc = COMPONENTS[ref]
        lines.append('    (comp (ref "%s")' % ref)
        lines.append('      (value "%s")' % value)
        lines.append('      (footprint "%s")' % fp)
        lines.append('      (description "%s"))' % desc)
    lines.append('  )')

    lines.append('  (nets')
    for code, name in enumerate(NETS, start=1):
        lines.append('    (net (code "%d") (name "%s")' % (code, name))
        for ref, pad in NETS[name]:
            lines.append('      (node (ref "%s") (pin "%s"))' % (ref, pad))
        lines.append('    )')
    lines.append('  )')
    lines.append(')')
    return "\n".join(lines) + "\n"


def sanity_check():
    """Cross-check every pad referenced in NETS resolves to a known component,
    and report per-component pad usage so floating refs are obvious."""
    errors = []
    pad_count = {}
    for name, nodes in NETS.items():
        for ref, _pad in nodes:
            if ref not in COMPONENTS:
                errors.append("net %s references unknown component %s" % (name, ref))
            pad_count[ref] = pad_count.get(ref, 0) + 1
    for ref in COMPONENTS:
        if ref not in pad_count:
            errors.append("component %s has no connections" % ref)
    return errors, pad_count


if __name__ == "__main__":
    errs, pads = sanity_check()
    print("=== sanity check ===")
    if errs:
        for e in errs:
            print("  ERROR:", e)
    else:
        print("  OK - all net nodes resolve, all components connected")
    print("  pad usage:", ", ".join("%s=%d" % (r, pads[r]) for r in sorted(pads)))

    net = emit_netlist()
    with open("freezer_monitor_usb_flipped.net", "w") as f:
        f.write(net)
    print("\n=== wrote freezer_monitor_usb_flipped.net (%d bytes) ===" % len(net))
