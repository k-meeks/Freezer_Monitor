#!/usr/bin/env python3
"""
gen_freezer_netlist.py - KiCad netlist generator for the Freezer Monitor PCB

Version:    1.1.0
Date:       2026-06-16
Author:     Kyle Meeks (UIHC) / generated with Claude
Description:
    Emits a KiCad-importable netlist (.net) for the nRF52840 freezer-monitor
    carrier board. Connectivity is data-driven (see COMPONENTS / NETS below) so
    the netlist is regenerable and diffable in git rather than hand-entered in
    the schematic editor. Run:  python3 gen_freezer_netlist.py

Verified design facts (from bench work, 2026-06-15/16):
    - Board: Teyleten Pro Micro nRF52840 (nice!nano v2 clone), socketed.
    - I/O rail REGOUT0 = 3.285 V (measured); GPIO input ceiling 3.585 V.
    - DS18B20 powered directly from cell (B+/B-); 3-wire; data on P0.24.
    - 4.7k OneWire pull-up to VBAT; data line idles 3.56 V -> in spec.
    - Battery sense: 2x 1M divider VBAT->GND, midpoint to P0.02 (A0).
    - Cell: Saft LS14250 (Li-SOCl2, 3.6 V, 1/2 AA).
    - JP1 isolates cell for safe USB/UF2 flashing (charger footgun).
    - Serial header VCC sourced from P1.06 held HIGH (cell-safe 3.3 V ref).

Version history:
    1.0.0  2026-06-16  Initial locked design.
    1.1.0  2026-06-16  Fix: tie U1 B- to GND (separate footprint pad, was
                       floating); C1 -> aluminum-polymer radial THT footprint
                       to match the low-leakage intent (NOT plain electrolytic).

NOTE: pad names for U1 below use the nice!nano functional labels. Verify they
match the pad names in YOUR chosen module footprint before importing - that is
the one place a mismatch silently drops a connection.
"""

KICAD_NETLIST_VERSION = "E"

# ref -> (value, footprint, description)
COMPONENTS = {
    "U1":  ("nice!nano nRF52840", "Module:nice_nano_v2",
            "Teyleten clone, socketed on machine-pin headers"),
    "BT1": ("LS14250",            "BatteryHolder:Keystone_1011_1-2AA",
            "Saft Li-SOCl2 3.6V 1/2AA, polarity-keyed holder"),
    "R1":  ("1M",                 "Resistor_SMD:R_0805_2012Metric", "Divider high side"),
    "R2":  ("1M",                 "Resistor_SMD:R_0805_2012Metric", "Divider low side"),
    "R3":  ("4.7k",               "Resistor_SMD:R_0805_2012Metric", "OneWire pull-up to VBAT"),
    "C1":  ("100uF",              "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm",
            "Al-polymer radial THT, low-leakage low-ESR; size to actual part"),
    "C2":  ("10nF",               "Capacitor_SMD:C_0805_2012Metric",
            "SAADC sampling reservoir at P0.02"),
    "J1":  ("DS18B20",            "Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm",
            "Probe: 1=VDD 2=DATA 3=GND"),
    "J2":  ("SERIAL",             "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
            "Debug UART: 1=GND 2=VCC 3=TX 4=RX"),
    "JP1": ("BATT",               "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
            "Cell isolation jumper - pull before USB"),
}

# net name -> list of (ref, pad)
NETS = {
    "CELL+": [("BT1", "1"), ("JP1", "1")],
    "VBAT":  [("JP1", "2"), ("U1", "B+"), ("C1", "1"),
              ("R1", "1"), ("R3", "1"), ("J1", "1")],
    "GND":   [("BT1", "2"), ("U1", "GND"), ("U1", "B-"), ("C1", "2"),
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
    lines.append('    (source "gen_freezer_netlist.py")')
    lines.append('    (date "2026-06-16")')
    lines.append('    (tool "gen_freezer_netlist.py 1.0.0"))')
    # components
    lines.append('  (components')
    for ref in sorted(COMPONENTS):
        value, fp, desc = COMPONENTS[ref]
        lines.append('    (comp (ref "%s")' % ref)
        lines.append('      (value "%s")' % value)
        lines.append('      (footprint "%s")' % fp)
        lines.append('      (description "%s"))' % desc)
    lines.append('  )')
    # nets
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
        for ref, pad in nodes:
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
    with open("freezer_monitor.net", "w") as f:
        f.write(net)
    print("\n=== wrote freezer_monitor.net (%d bytes) ===" % len(net))
