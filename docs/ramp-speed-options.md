# Ways to speed up the ramp-down, simplest first

![options](ramp_speed_options.png)

Script: [ramp_speed_options.py](../scripts/ramp_speed_options.py). Baseline: L = 0.38 mH, R = 0.99 Ω, I0 = 2.5 A, V+ = 12 V. Times are 2.5 A → 10 %.

## The one equation behind every option

A coil only gives up its current when you put voltage across it:

> **t ≈ L·I₀ / V = 0.95 mV·s / V**

1 V gets you about 950 µs, 10 V about 95 µs, 100 V about 9.5 µs. So every solution below is really the same question twice:
1. **How many volts can I impose across the coil?**
2. **Who absorbs them — the LD5CHA's LDC pin, or something else?**

Question 2 is what separates the cheap options from the fast ones. While the coil hangs directly on LDA and LDC, every volt of clamp lands on LDC, and LDC has no published rating. A series switch breaks that link, which is why it is the only route to the tens-of-microseconds range.

## The ladder

| # | Solution | Parts to add | V on coil | t to 10 % | Peak LDC | What keeps it safe |
|---|---|---|---|---|---|---|
| 0 | **Setpoint RC, τ = 0.4 ms** | none | 0 | **920 µs** | 12 V | τ ≥ L/R means LDC never rises above V+ at all |
| 0b | **Setpoint linear ramp** | none | 6 | **143 µs** | 18 V | You pick the overshoot by choosing T; driver stays in regulation |
| 1 | **D1 freewheel diode** | 1 diode (1N5408) | 0.95 | **400 µs** | 12.9 V | Diode carries the current; LDC only 1 V above rail |
| 2 | **D1 + 6 V zener in series** | 2 leaded parts | 6.0 | **116 µs** | 18 V | Zener sets the clamp; 1.2 mJ per shot is trivial for a 1.5KE |
| 3 | **D1 + 15 V TVS in series** | 2 leaded parts | 15.9 | **49 µs** | 27.9 V | At the 28 V compliance figure — the edge of what is defensible |
| 4 | **Series 2 Ω resistor + D1 across both** | resistor + diode | 0.95 | **204 µs** | 12.9 V | Also moves ~12 W of heat out of the driver into the resistor |
| 5 | **Rewind: half the turns, 5 A** | rewind the coil | 15.9 | **23 µs** | 27.9 V | Same field, but t ∝ N at fixed clamp. Needs 5 A (driver max) |
| 6 | **Series MOSFET + 100 V TVS** | FET + isolated gate driver | 100 | **8 µs** | 12 V | FET opens first, so the 100 V lands on the FET and TVS, never on LDC |
| 7 | **Series MOSFET + 250 V TVS** | FET (250 V) + gate driver | 250 | **3.4 µs** | 12 V | Same, with a higher-voltage FET |

## Notes on each

**0 and 0b — setpoint shaping, free.** Covered in [ramp-down-analysis.md](ramp-down-analysis.md). An RC with τ ≈ 0.4 ms gives zero overshoot. A linear ramp trades overshoot for speed: T = L·I₀/ΔV, so the 143 µs figure assumes you accept LDC reaching 18 V. These only work while the driver stays in regulation, so they do nothing for an uncommanded cut.

**1 — D1 alone.** The cheapest real protection. It also covers the abrupt cases (fault trip, logic loss, unplugging) that setpoint shaping cannot. 400 µs is already faster than the no-overshoot RC, because the diode holds ~1 V across the coil the whole way down instead of ~0.

**2 and 3 — D1 plus a zener or TVS.** The natural extension: raise the clamp voltage, get proportionally faster. The series pair goes across the coil, cathode to cathode, so it blocks in normal operation. Energy per shot is 1.2 mJ, so even at 100 Hz that is 0.12 W and any 1.5KE part is oversized for it. **This is where I would stop without more information**, because option 3 puts LDC at 27.9 V, and the datasheet never rates that pin.

**4 — series resistor.** Worth knowing because it pays twice: it speeds the freewheel decay (R_total 2.99 Ω instead of 0.99 Ω) *and* it drops driver dissipation from 24 W to about 11 W by moving the heat into a resistor you can mount anywhere. The catch: the resistor burns 12.5 W continuously, and D1 must go across the coil *and* the resistor together, or the resistor is not in the freewheel loop.

**5 — rewind the coil.** The one option that changes the physics instead of working around it. At fixed ampere-turns, halving N gives L/4 and 2·I, so L·I halves and the decay halves with it. Also halves the volt-seconds the clamp has to absorb. Costs a rewind and pushes you to 5 A, which is the LD5CHA's absolute maximum with no margin.

**6 and 7 — series MOSFET.** The only way past ~50 µs. The FET sits between the coil and LDC. When it opens, the coil dumps into a high-voltage TVS while LDC is isolated and actually falls toward 0. Peak LDC is just V+. The real limit here is **not** the TVS but the **gate driver**: the Si8751 from the earlier chat is specified at roughly 46 µs turn-off (unverified), which would dominate an 8 µs decay. A conventional isolated gate driver with its own floating supply turns off in well under 1 µs and would be the right choice. Sequence matters: open the FET first, then zero the setpoint, so the driver is not left saturated against an open load.

## Things that do not help

- **Raising V+.** It speeds the ramp *up* (0.14 ms at 12 V vs 0.52 ms at 6 V) and does nothing for the ramp *down*. Current falls only when LDC rises above V+, so a higher rail just raises the bar. It also costs dissipation.
- **The ENABLE pin.** The datasheet gives a 640 µs disable fall time and a 260 µs turn-off ramp — slower than a setpoint step, so it is a safety interlock, not a speed tool.
- **A capacitor across the coil.** It rings with L rather than damping, and swings LDC negative.

## The limit that may make all of this moot

If this coil sits near a metal chamber, **eddy currents** in the mounts and walls keep the *field* alive after the *current* is gone. Those time constants are typically 100 µs to a few ms for stainless steel, and much shorter for glass cells. Chasing 8 µs in the current is pointless if the field takes 500 µs to die. Measure the field with a pickup coil or a magnetometer before buying a MOSFET.

## Suggested path

1. Fit **D1** now (option 1, 400 µs). It protects against the abrupt cases regardless of what else you do.
2. Measure the **field** decay, not just the current. That tells you whether anything faster is useful.
3. If you need faster and the field can follow, add a **zener in series with D1** (option 2, 116 µs) — two leaded parts, no rework.
4. Only go to a **series MOSFET** (option 6) if you have measured that you need sub-50 µs, and budget a fast isolated gate driver, not the Si8751.

## Caveats

- All figures are from the model, not the bench, and assume L = 0.38 mH and R = 0.99 Ω — neither has been measured on your hardware.
- The datasheet gives **no maximum LDC voltage**. The 28 V line is the maximum compliance figure used as a stand-in, so options 3 and 5 are at an unverified boundary.
- The 1N5408 forward drop is modelled as 0.95 V at 2.5 A.
