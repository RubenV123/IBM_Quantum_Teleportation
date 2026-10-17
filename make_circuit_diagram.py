"""Draws the hardware teleportation circuit and saves it to images/circuit.png.

Run:  python make_circuit_diagram.py
(needs:  pip install pylatexenc)
"""
from pathlib import Path

from teleportation_lab import build_hardware_circuit, normalize_state, PRESET_STATES

out_dir = Path("images")
if not out_dir.is_dir():
    out_dir.mkdir(parents=True)

# Example state |+i>. The message is shown as a "State Preparation" box.
qc = build_hardware_circuit(normalize_state(*PRESET_STATES["+i"]))

try:
    qc.draw("mpl", filename=str(out_dir / "circuit.png"))
    print("Saved images/circuit.png")
except Exception as exc:
    print(f"Could not draw the picture ({exc}).")
    print("Try:  pip install pylatexenc")
    print("\nText version of the circuit:\n")
    print(qc.draw("text"))
