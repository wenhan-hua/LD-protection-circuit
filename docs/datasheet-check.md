# LD5CHA specs checked against the Wavelength datasheet

Source: [LDxCHA Series datasheet and operating guide](https://www.teamwavelength.com/download/Datasheets/LD15CHA.pdf) (read in full text form; electrical specs on p. 6, heatsink and SOA on pp. 18–19). Product page: https://www.teamwavelength.com/product/ld5cha-5-a-30-v-laser-diode-driver/

| Item (LD5CHA) | Datasheet | Status of the earlier-chat claim |
|---|---|---|
| Max output current | **5 A** | Confirmed |
| Supply V+ | 5 to 30 V | Confirmed |
| Compliance voltage | "always 2 V less than power supply voltage" (3 V at 5 V, 28 V at 30 V) | Confirmed |
| Max internal power dissipation, no airflow | **25 W** at 25 °C ambient | Confirmed |
| Max internal power dissipation, with airflow | **35 W** at 25 °C ambient, with 5.5 CFM | **New. The chat missed it.** |
| Operating temperature | 0 to 40 °C | New |
| Modulation input, CC mode | **1 A/V** (range −2 to +5 V, 2.5 kΩ input, damage at ≤ −3 V or ≥ 8 V) | Confirmed. The set, limit and output monitors are 2 A/V. |
| Bandwidth (small-signal, full current) | 1000 kHz; output rise or fall time about 0.8 µs | Confirmed, but meaningless for an inductive load |
| Max voltage on LDC | **Not specified** | Still unknown |
| Internal output clamp or flyback diode | **None documented** | The datasheet never mentions inductive loads |

## Other relevant findings
- The datasheet says the unit **requires heatsinking** to stay within its SOA. The recommended heatsink for the LD5CHA is the MULTI-HTSK (based on about 25 °C operation). It tells you to check operation with the online SOA calculator: https://www.teamwavelength.com/support/design-tools/soa-ld-calculator/
- For cables **longer than 2 feet**, the datasheet recommends a **Schottky diode (1N5818) across the load**, with its anode at LDC, as laser protection. So an external diode across the output is Wavelength's own practice, which supports adding D1. Its Figure 12 output filter also uses a Schottky plus 0.1 µF and 10 µF.
- A Schottky is fine as protection for a laser, but for a coil its leakage can add to the measured current. I'd stay with a silicon diode, unless the leakage turns out not to matter.
- The driver has brownout protection and over-voltage protection (no details on the output pin). The 5 V control supply has an undervoltage trip at 4 V and an overvoltage trip at 6 V.
- The ENABLE pin disables the output with 2–5 V applied.
