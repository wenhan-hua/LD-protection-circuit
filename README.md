# LD driver protection circuit

Protection circuit design for driving a 3D MOT coil with a Wavelength LD5CHA laser-diode driver.

- [docs/coil-estimate.md](docs/coil-estimate.md): coil L and R estimate from geometry
- [scripts/coil_estimate.py](scripts/coil_estimate.py): calculation script
- [docs/direct-drive.md](docs/direct-drive.md): preliminary schematic, LD5CHA driving the coil directly
- `LD5CHA coil driving and protection - Claude.pdf`, if added, holds the earlier design discussion

Setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- [docs/datasheet-check.md](docs/datasheet-check.md): LD5CHA specs verified against the Wavelength datasheet
- [docs/ramp-down-analysis.md](docs/ramp-down-analysis.md): ramp-down timescale versus peak voltage and heat
- [docs/ramp-speed-options.md](docs/ramp-speed-options.md): ways to speed up the ramp-down, simplest first
- [docs/chosen-design.md](docs/chosen-design.md): **chosen design** — series 2 Ω + D1 + TVS clamp
- [docs/alt-design-d1-zener.md](docs/alt-design-d1-zener.md): simpler alternative — D1 + TVS only, no series resistor
