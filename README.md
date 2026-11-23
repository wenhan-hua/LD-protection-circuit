# LD driver protection circuit

Protection circuit design for driving a 3D MOT coil with a Wavelength LD5CHA laser-diode driver.

- [docs/coil-estimate.md](docs/coil-estimate.md): coil L and R estimate from geometry
- [scripts/coil_estimate.py](scripts/coil_estimate.py): calculation script
- [docs/direct-drive.md](docs/direct-drive.md): preliminary schematic, LD5CHA driving the coil directly
- `LD5CHA coil driving and protection - Claude.pdf`, if added, holds the earlier design discussion

Setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
