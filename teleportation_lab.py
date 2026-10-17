"""
QUANTUM TELEPORTATION VERIFICATION LAB
Qiskit + Bloch Sphere Visualization + Six-State Benchmark + Real IBM Hardware

Features:
1. Teleport a user-selected quantum state.
2. Compare Alice's and Bob's states using Bloch spheres.
3. Calculate teleportation fidelity.
4. Test six standard quantum states.
5. Plot a fidelity comparison graph.
6. Display the original teleportation circuit.
7. Run the six states on a REAL IBM quantum computer and plot the
   error-probability graph (the API key is typed in and never saved).
"""

import numpy as np
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import StatePreparation
from qiskit.quantum_info import (
    Statevector,
    DensityMatrix,
    partial_trace,
    state_fidelity
)
from qiskit_aer import AerSimulator

# Extra imports used only by option 3 (real hardware)
import getpass
import json
import warnings
from datetime import datetime
from pathlib import Path


# ============================================================
# 1. SIX STANDARD QUANTUM STATES
# ============================================================

S = 1 / np.sqrt(2)

PRESET_STATES = {
    "0":  (1, 0),
    "1":  (0, 1),
    "+":  (S, S),
    "-":  (S, -S),
    "+i": (S, 1j * S),
    "-i": (S, -1j * S)
}


# ============================================================
# 2. VALIDATE AND NORMALIZE THE INPUT STATE
# ============================================================

def normalize_state(alpha, beta):
    norm = np.sqrt(abs(alpha)**2 + abs(beta)**2)

    if np.isclose(norm, 0):
        raise ValueError("Alpha and beta cannot both be zero.")

    if not np.isclose(norm, 1):
        print("Note: Normalizing the input amplitudes.")

    return np.array([alpha, beta], dtype=complex) / norm


# ============================================================
# 3. BUILD THE QUANTUM TELEPORTATION CIRCUIT
# ============================================================

def build_teleportation_circuit(state, save_state=True):
    qr = QuantumRegister(3, name="q")
    cr = ClassicalRegister(2, name="c")

    qc = QuantumCircuit(qr, cr, name="teleportation")

    # Prepare Alice's original message state
    qc.append(StatePreparation(state), [qr[0]])
    qc.barrier(label="State Prep")

    # Create an entangled Bell pair between Alice and Bob
    qc.h(qr[1])
    qc.cx(qr[1], qr[2])
    qc.barrier(label="Entanglement")

    # Alice performs the Bell measurement
    qc.cx(qr[0], qr[1])
    qc.h(qr[0])

    qc.measure(qr[1], cr[0])
    qc.measure(qr[0], cr[1])
    qc.barrier(label="Measurement")

    # Bob applies corrections using Alice's classical bits
    with qc.if_test((cr[0], 1)):
        qc.x(qr[2])

    with qc.if_test((cr[1], 1)):
        qc.z(qr[2])

    qc.barrier(label="Correction")

    # Save final state for simulation-based verification
    if save_state:
        qc.save_statevector(label="final_state")

    return qc


# ============================================================
# 4. CONVERT A QUBIT STATE INTO A BLOCH VECTOR
# ============================================================

def get_bloch_vector(state):
    """
    Return the x, y, z coordinates of a single-qubit state.
    Works with a Statevector or a one-qubit DensityMatrix.
    """

    rho = DensityMatrix(state).data

    x = 2 * np.real(rho[0, 1])
    y = -2 * np.imag(rho[0, 1])
    z = np.real(rho[0, 0] - rho[1, 1])

    return float(x), float(y), float(z)


# ============================================================
# 5. DRAW ALICE AND BOB'S BLOCH SPHERES SIDE BY SIDE
# ============================================================


def plot_bloch_comparison(alice_state, bob_state, fidelity):
    """Neon-themed comparison of Alice's and Bob's Bloch spheres."""

    import numpy as np
    import matplotlib.pyplot as plt
    from qiskit.quantum_info import DensityMatrix

    # Neon theme colours
    BACKGROUND = "#080D1B"
    SPHERE_COLOR = "#163451"
    CYAN = "#00E5FF"
    PURPLE = "#C084FC"
    GRID_COLOR = "#52627A"
    TEXT_COLOR = "#E6F0FF"

    # Convert a quantum state into Bloch coordinates.
    def get_coordinates(state):
        rho = DensityMatrix(state).data

        x = 2 * np.real(rho[0, 1])
        y = -2 * np.imag(rho[0, 1])
        z = np.real(rho[0, 0] - rho[1, 1])

        return np.real(np.array([x, y, z]))

    alice_xyz = get_coordinates(alice_state)
    bob_xyz = get_coordinates(bob_state)

    # Generate the sphere surface.
    angles = np.linspace(0, 2 * np.pi, 70)
    elevations = np.linspace(0, np.pi, 50)

    sphere_x = np.outer(np.cos(angles), np.sin(elevations))
    sphere_y = np.outer(np.sin(angles), np.sin(elevations))
    sphere_z = np.outer(np.ones_like(angles), np.cos(elevations))

    # Create a dark-themed figure.
    fig = plt.figure(figsize=(13, 7), facecolor=BACKGROUND)

    fig.suptitle(
        "QUANTUM TELEPORTATION LAB",
        fontsize=18,
        fontweight="bold",
        color=CYAN,
        y=0.97
    )

    fig.text(
        0.5, 0.91,
        f"State Fidelity: {fidelity:.4f}",
        ha="center",
        fontsize=13,
        color=PURPLE
    )

    spheres = [
        (alice_xyz, "ALICE | ORIGINAL STATE", CYAN),
        (bob_xyz, "BOB | TELEPORTED STATE", PURPLE)
    ]

    for index, (xyz, title, vector_color) in enumerate(spheres, start=1):
        ax = fig.add_subplot(1, 2, index, projection="3d")
        ax.set_facecolor(BACKGROUND)

        # Draw a transparent neon-blue sphere.
        ax.plot_surface(
            sphere_x, sphere_y, sphere_z,
            color=SPHERE_COLOR,
            alpha=0.38,
            edgecolor=CYAN,
            linewidth=0.22,
            rstride=3,
            cstride=3,
            shade=False
        )

        # Draw the X, Y and Z axes.
        ax.plot(
            [-1, 1], [0, 0], [0, 0],
            color=GRID_COLOR, linewidth=1
        )
        ax.plot(
            [0, 0], [-1, 1], [0, 0],
            color=GRID_COLOR, linewidth=1
        )
        ax.plot(
            [0, 0], [0, 0], [-1, 1],
            color=GRID_COLOR, linewidth=1
        )

        # Label the axes.
        ax.text(1.12, 0, 0, "X", color=CYAN, fontsize=11)
        ax.text(0, 1.12, 0, "Y", color=CYAN, fontsize=11)
        ax.text(0, 0, 1.12, "Z", color=CYAN, fontsize=11)

        # Draw the qubit's state vector.
        ax.quiver(
            0, 0, 0,
            xyz[0], xyz[1], xyz[2],
            color=vector_color,
            linewidth=3,
            arrow_length_ratio=0.16
        )

        # Highlight the tip of the vector.
        ax.scatter(
            [xyz[0]], [xyz[1]], [xyz[2]],
            color=vector_color,
            s=65,
            depthshade=False
        )

        # Style titles, ticks and panes.
        ax.set_title(
            title,
            color=vector_color,
            fontsize=12,
            fontweight="bold",
            pad=18
        )

        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_zlim(-1.2, 1.2)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=22, azim=35)

        for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
            axis.set_pane_color((0.03, 0.05, 0.10, 1.0))
            axis.line.set_color(GRID_COLOR)
            axis.set_tick_params(colors=TEXT_COLOR, labelsize=8)

        # Keep subtle grid lines.
        ax.xaxis._axinfo["grid"]["color"] = GRID_COLOR
        ax.yaxis._axinfo["grid"]["color"] = GRID_COLOR
        ax.zaxis._axinfo["grid"]["color"] = GRID_COLOR

        # Display numerical Bloch coordinates.
        ax.text2D(
            0.03, 0.02,
            f"X: {xyz[0]:+.3f}\n"
            f"Y: {xyz[1]:+.3f}\n"
            f"Z: {xyz[2]:+.3f}",
            transform=ax.transAxes,
            fontsize=10,
            color=vector_color,
            family="monospace",
            bbox=dict(
                facecolor="#101A30",
                edgecolor=vector_color,
                alpha=0.95,
                boxstyle="round,pad=0.5"
            )
        )

    fig.text(
        0.5, 0.025,
        "Alice's original qubit  |  Bob's reconstructed qubit",
        ha="center",
        color=TEXT_COLOR,
        fontsize=10
    )

    plt.tight_layout(rect=[0.02, 0.07, 0.98, 0.87])
    plt.show()


def run_quantum_teleportation(
    alpha,
    beta,
    show_circuit=False,
    show_bloch=True
):
    state = normalize_state(alpha, beta)

    qc = build_teleportation_circuit(state)

    if show_circuit:
        print("\nQUANTUM TELEPORTATION CIRCUIT\n")
        print(qc.draw("text", fold=100))

    target_state = Statevector(state)

    simulator = AerSimulator(method="statevector")
    compiled = transpile(qc, simulator)

    result = simulator.run(compiled, shots=1).result()

    final_state = Statevector(result.data(0)["final_state"])
    outcome = result.get_counts()

    # Trace out Alice's two qubits to obtain Bob's state
    bob_state = partial_trace(final_state, [0, 1])

    # Compare the original state with Bob's recovered state
    fidelity = float(state_fidelity(target_state, bob_state))

    print("\n----------------------------------------")
    print("QUANTUM TELEPORTATION RESULTS")
    print("----------------------------------------")
    print(f"Original alpha: {state[0]}")
    print(f"Original beta : {state[1]}")
    print(f"Measurement   : {outcome}")
    print(f"Fidelity      : {fidelity:.6f}")

    if np.isclose(fidelity, 1.0, atol=1e-6):
        print("Verification  : PASS")
    else:
        print("Verification  : CHECK RESULT")

    if show_bloch:
        plot_bloch_comparison(
            target_state,
            bob_state,
            fidelity
        )

    return fidelity


# ============================================================
# 7. SIX-STATE TELEPORTATION CHALLENGE
# ============================================================

def run_six_state_benchmark():
    labels = list(PRESET_STATES.keys())
    fidelities = []

    print("\n========================================")
    print(" SIX-STATE TELEPORTATION CHALLENGE")
    print("========================================")

    for label, (alpha, beta) in PRESET_STATES.items():
        print(f"\nTesting input state: |{label}>")

        fidelity = run_quantum_teleportation(
            alpha,
            beta,
            show_circuit=False,
            show_bloch=False
        )

        fidelities.append(fidelity)

    # Plot the six actual fidelity results using the neon theme
    BACKGROUND = "#080D1B"
    CYAN = "#00E5FF"
    PURPLE = "#C084FC"
    GRID_COLOR = "#52627A"
    TEXT_COLOR = "#E6F0FF"

    fig, ax = plt.subplots(figsize=(10, 5.8), facecolor=BACKGROUND)
    ax.set_facecolor(BACKGROUND)

    # Alternate cyan and purple bars
    bar_colors = [CYAN, PURPLE, CYAN, PURPLE, CYAN, PURPLE]

    bars = ax.bar(
        labels,
        fidelities,
        color=bar_colors,
        edgecolor=TEXT_COLOR,
        linewidth=0.7,
        width=0.62,
        zorder=3
    )

    # Ideal fidelity reference line
    ax.axhline(
        y=1.0,
        linestyle="--",
        color=CYAN,
        linewidth=1.6,
        label="Ideal fidelity = 1.0",
        zorder=2
    )

    ax.set_ylim(0, 1.12)
    ax.set_xlabel(
        "Input quantum state",
        color=TEXT_COLOR,
        labelpad=10
    )
    ax.set_ylabel(
        "Teleportation fidelity",
        color=TEXT_COLOR,
        labelpad=10
    )

    ax.set_title(
        "SIX-STATE TELEPORTATION VERIFICATION",
        color=CYAN,
        fontsize=15,
        fontweight="bold",
        pad=18
    )

    # Style the axes and background grid
    ax.tick_params(axis="x", colors=TEXT_COLOR, labelsize=11)
    ax.tick_params(axis="y", colors=TEXT_COLOR, labelsize=10)

    ax.yaxis.grid(
        True,
        color=GRID_COLOR,
        linestyle=":",
        alpha=0.55,
        zorder=0
    )
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)

    ax.legend(
        facecolor="#101A30",
        edgecolor=PURPLE,
        labelcolor=TEXT_COLOR,
        framealpha=1
    )

    # Display each fidelity score above its bar
    for bar, score, label_color in zip(bars, fidelities, bar_colors):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.025,
            f"{score:.4f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color=label_color
        )

    fig.text(
        0.5, 0.015,
        "Higher fidelity means Bob's recovered state is closer to Alice's original state",
        ha="center",
        color=TEXT_COLOR,
        fontsize=9
    )

    plt.tight_layout(rect=[0.02, 0.06, 0.98, 0.98])
    plt.show()

    print("\n========== FINAL BENCHMARK REPORT ==========")

    for label, score in zip(labels, fidelities):
        print(f"State |{label}> : {score:.6f}")

    average = float(np.mean(fidelities))
    print(f"\nAverage fidelity: {average:.6f}")

    if all(np.isclose(f, 1.0, atol=1e-6) for f in fidelities):
        print("Overall result: ALL SIX STATES PASSED")
    else:
        print("Overall result: SOME RESULTS NEED INVESTIGATION")

    return fidelities


# ============================================================
# 8. INPUT HELPERS
# ============================================================

def read_amplitude(prompt):
    """
    Accept inputs such as:
    0.6, 1/sqrt(2), 1j/sqrt(2), -0.5j
    """

    allowed = {
        "__builtins__": {},
        "sqrt": np.sqrt,
        "pi": np.pi
    }

    while True:
        raw = input(prompt).strip()

        try:
            return complex(eval(raw, allowed, {}))
        except Exception:
            print("Invalid input. Example: 0.6, 1/sqrt(2), 1j/sqrt(2)")


def choose_state():
    print("\nAvailable states: 0, 1, +, -, +i, -i")
    print("Enter 'c' for a custom state.")

    while True:
        choice = input("Choose a state: ").strip().lower()

        if choice in PRESET_STATES:
            return PRESET_STATES[choice]

        if choice == "c":
            alpha = read_amplitude("Enter alpha: ")
            beta = read_amplitude("Enter beta: ")
            return alpha, beta

        print("Please enter a listed state or 'c'.")


# ============================================================
# 9. REAL IBM QUANTUM HARDWARE: ERROR PROBABILITY GRAPH (OPTION 3)
# ============================================================
#
# Notes
# - The hardware circuit is a "hardware-safe" version of teleportation.
#   Bob's corrections are wired in as cx / cz gates (deferred measurement),
#   so no mid-circuit classical feed-forward is needed.
# - Verification trick: after teleporting, we undo the message on Bob's
#   qubit. A perfect run leaves Bob at |0>, so measuring 1 is an ERROR.
# - Nothing in this section uses Qiskit Aer.
# - The API key is typed with hidden input and is never saved or printed.

HW_SHOTS = 1024
HW_IMAGES_DIR = Path("images")
HW_RESULTS_DIR = Path("results")


def build_hardware_circuit(state):
    """Teleportation circuit that can run on real hardware."""
    q = QuantumRegister(3, "q")
    bob = ClassicalRegister(1, "bob")
    qc = QuantumCircuit(q, bob, name="teleport_hw")

    # Alice's secret message on q0
    qc.append(StatePreparation(state), [q[0]])

    # Entangled pair: q1 (Alice) and q2 (Bob)
    qc.h(q[1])
    qc.cx(q[1], q[2])

    # Alice's Bell-basis "translation"
    qc.cx(q[0], q[1])
    qc.h(q[0])

    # Bob's corrections (deferred measurement)
    qc.cx(q[1], q[2])   # X correction
    qc.cz(q[0], q[2])   # Z correction

    # Verification: undo the message on Bob's qubit, then measure it
    qc.append(StatePreparation(state).inverse(), [q[2]])
    qc.measure(q[2], bob[0])
    return qc


def _make_folder(path):
    """Create a folder if needed (skips mkdir if it already exists)."""
    path = Path(path)
    if path.is_dir():
        return True
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False


def _error_probability(counts):
    """Fraction of shots in which Bob measured 1 (the error outcome)."""
    total = sum(counts.values())
    return counts.get("1", 0) / total if total else 0.0


def _connect_to_ibm(token, instance):
    """Connect to IBM Quantum with a typed-in key. Returns a service or None."""
    from qiskit_ibm_runtime import QiskitRuntimeService

    kwargs = {"token": token}
    if instance:
        kwargs["instance"] = instance

    errors = []
    for extra in ({"channel": "ibm_quantum_platform"}, {}):
        try:
            return QiskitRuntimeService(**extra, **kwargs)
        except Exception as exc:
            errors.append(str(exc).replace(token, "***"))

    print("\nCould not connect to IBM Quantum.")
    print("Check that the API key is correct and that your account is active.")
    print(f"Details: {errors[-1][:300]}")
    return None


def _ideal_baseline(circuits):
    """Noise-free results from Qiskit's built-in pure-Python simulator."""
    try:
        from qiskit.providers.basic_provider import BasicSimulator

        sim = BasicSimulator()
        compiled = [transpile(c, sim) for c in circuits]
        result = sim.run(compiled, shots=HW_SHOTS, seed_simulator=1234).result()
        return [_error_probability(result.get_counts(i)) for i in range(len(compiled))]
    except Exception:
        return None


def plot_error_probability_graph(labels, hw_err, ideal_err, backend_name, job_id):
    """Neon-themed bar chart: error probability per teleported state."""
    BACKGROUND = "#080D1B"
    CYAN = "#00E5FF"
    PURPLE = "#C084FC"
    GRID_COLOR = "#52627A"
    TEXT_COLOR = "#E6F0FF"

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(11, 6), facecolor=BACKGROUND)
    ax.set_facecolor(BACKGROUND)

    # Statistical uncertainty of each hardware measurement
    hw_sigma = [float(np.sqrt(p * (1 - p) / HW_SHOTS)) for p in hw_err]

    if ideal_err is not None:
        width = 0.36
        ideal_bars = ax.bar(
            x - width / 2, ideal_err, width,
            color=CYAN, edgecolor=TEXT_COLOR, linewidth=0.7, zorder=3,
            label="Ideal simulator (no noise)"
        )
        hw_bars = ax.bar(
            x + width / 2, hw_err, width, yerr=hw_sigma, capsize=4,
            color=PURPLE, edgecolor=TEXT_COLOR, linewidth=0.7, zorder=3,
            error_kw={"ecolor": TEXT_COLOR, "elinewidth": 1.2},
            label=f"REAL hardware: {backend_name}"
        )
        for bar, v in zip(ideal_bars, ideal_err):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.003,
                    f"{v:.3f}", ha="center", va="bottom", fontsize=9,
                    fontweight="bold", color=CYAN)
    else:
        width = 0.55
        hw_bars = ax.bar(
            x, hw_err, width, yerr=hw_sigma, capsize=4,
            color=PURPLE, edgecolor=TEXT_COLOR, linewidth=0.7, zorder=3,
            error_kw={"ecolor": TEXT_COLOR, "elinewidth": 1.2},
            label=f"REAL hardware: {backend_name}"
        )

    for bar, v, s in zip(hw_bars, hw_err, hw_sigma):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + s + 0.003,
                f"{v:.3f}", ha="center", va="bottom", fontsize=9,
                fontweight="bold", color=PURPLE)

    ax.set_xticks(x)
    ax.set_xticklabels([f"|{l}>" for l in labels], color=TEXT_COLOR, fontsize=11)
    ax.tick_params(axis="y", colors=TEXT_COLOR, labelsize=10)
    ax.set_xlabel("Teleported state", color=TEXT_COLOR, labelpad=10)
    ax.set_ylabel("Error probability (Bob measured 1)", color=TEXT_COLOR, labelpad=10)
    ax.set_title(
        "TELEPORTATION ERROR PROBABILITY ON REAL QUANTUM HARDWARE",
        color=CYAN, fontsize=14, fontweight="bold", pad=18
    )
    ax.set_ylim(0, max(0.05, max(hw_err) * 1.5))
    ax.yaxis.grid(True, color=GRID_COLOR, linestyle=":", alpha=0.55, zorder=0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    ax.legend(facecolor="#101A30", edgecolor=PURPLE, labelcolor=TEXT_COLOR, framealpha=1)

    when = datetime.now().strftime("%Y-%m-%d %H:%M")
    fig.text(
        0.5, 0.012,
        f"Backend: {backend_name} | shots per state: {HW_SHOTS} | job: {job_id} | {when} "
        f"| error bars = statistical uncertainty",
        ha="center", color=TEXT_COLOR, fontsize=8
    )
    plt.tight_layout(rect=[0.02, 0.05, 0.98, 0.98])

    if _make_folder(HW_IMAGES_DIR):
        out = HW_IMAGES_DIR / "noise_graph.png"
        try:
            fig.savefig(out, dpi=200, facecolor=fig.get_facecolor())
            print(f"Graph saved to {out}")
        except OSError as exc:
            print(f"Could not save the graph image ({exc}).")
    else:
        print("Could not create the 'images' folder, so the graph was not saved.")

    plt.show()


def run_hardware_error_graph():
    """Menu option 3: run the six states on real IBM hardware and plot errors."""
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    print("\n========================================")
    print(" REAL IBM QUANTUM HARDWARE RUN")
    print("========================================")
    print("This sends the six teleportation circuits to a real quantum computer.")
    print("It uses your free IBM quantum minutes and may wait in a queue.")
    print("You need an IBM Quantum Platform account (quantum.cloud.ibm.com).")
    print("Your API key is typed with hidden input and is never saved.\n")

    token = getpass.getpass("Enter your IBM Quantum API key (typing is hidden): ").strip()
    if not token:
        print("No key entered. Returning to the menu.")
        return

    instance = input("Instance name or CRN (press Enter to skip): ").strip() or None

    try:
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        from qiskit_ibm_runtime import SamplerV2 as Sampler
    except ImportError:
        print("\nqiskit-ibm-runtime is not installed. Run:  pip install qiskit-ibm-runtime")
        return

    print("\nConnecting to IBM Quantum ...")
    service = _connect_to_ibm(token, instance)
    if service is None:
        return

    labels = list(PRESET_STATES.keys())
    circuits = [
        build_hardware_circuit(normalize_state(*PRESET_STATES[label]))
        for label in labels
    ]

    existing_id = input(
        "\nExisting Job ID to fetch (press Enter to submit a NEW job): "
    ).strip()

    try:
        if existing_id:
            job = service.job(existing_id)
            backend = job.backend()
            job_id = existing_id
            print(f"Fetching job {job_id} from {backend.name} ...")
        else:
            backend = service.least_busy(
                operational=True, simulator=False, min_num_qubits=3
            )
            print(f"Least busy backend: {backend.name}")

            go = input("Submit the job now? This uses quantum minutes (y/n): ").strip().lower()
            if go != "y":
                print("Cancelled. Returning to the menu.")
                return

            pass_manager = generate_preset_pass_manager(
                optimization_level=3, backend=backend
            )
            compiled = [pass_manager.run(c) for c in circuits]

            job = Sampler(mode=backend).run(compiled, shots=HW_SHOTS)
            job_id = job.job_id()
            print(f"Job submitted. Job ID: {job_id}")
            print("Save this ID. If you stop waiting, you can fetch the result later "
                  "by choosing option 3 again and entering it.")

        print("Waiting for the job to finish (queue time varies). Press Ctrl+C to stop waiting.")
        result = job.result()

    except KeyboardInterrupt:
        print("\nStopped waiting. The job keeps running on IBM's side.")
        try:
            print(f"Job ID to fetch later: {job_id}")
        except NameError:
            pass
        return
    except Exception as exc:
        print(f"\nThe hardware run failed: {str(exc).replace(token, '***')[:400]}")
        return

    hw_counts = [result[i].data.bob.get_counts() for i in range(len(circuits))]
    hw_err = [_error_probability(c) for c in hw_counts]
    ideal_err = _ideal_baseline(circuits)

    # Save the raw counts (never the API key)
    if _make_folder(HW_RESULTS_DIR):
        try:
            (HW_RESULTS_DIR / "hardware_counts.json").write_text(json.dumps({
                "backend": backend.name,
                "job_id": job_id,
                "shots": HW_SHOTS,
                "states": labels,
                "counts": hw_counts,
                "error_probability": hw_err,
            }, indent=2))
            print("Raw counts saved to results/hardware_counts.json")
        except OSError as exc:
            print(f"Could not save the raw counts ({exc}).")

    print("\n" + "=" * 52)
    print(f" ERROR PROBABILITY ON {backend.name}")
    print("=" * 52)
    header = f"{'State':<8}{'Hardware':>14}"
    if ideal_err is not None:
        header += f"{'Ideal':>14}"
    print(header)
    print("-" * 52)
    for i, label in enumerate(labels):
        row = f"|{label}>".ljust(8) + f"{hw_err[i]:>14.4f}"
        if ideal_err is not None:
            row += f"{ideal_err[i]:>14.4f}"
        print(row)
    print("-" * 52)
    avg = "average".ljust(8) + f"{np.mean(hw_err):>14.4f}"
    if ideal_err is not None:
        avg += f"{np.mean(ideal_err):>14.4f}"
    print(avg)
    print("=" * 52)

    plot_error_probability_graph(labels, hw_err, ideal_err, backend.name, job_id)


# ============================================================
# 10. MAIN MENU
# ============================================================

def main():
    print("\n==========================================")
    print("  QUANTUM TELEPORTATION VERIFICATION LAB")
    print("==========================================")
    print("1. Teleport one state + compare Bloch spheres")
    print("2. Run the six-state challenge + fidelity graph")
    print("3. Run on a REAL IBM quantum computer + error probability graph")
    print("4. Exit")

    first_run = True

    while True:
        choice = input("\nSelect option (1/2/3/4): ").strip()

        if choice == "1":
            alpha, beta = choose_state()

            run_quantum_teleportation(
                alpha,
                beta,
                show_circuit=first_run,
                show_bloch=True
            )

            first_run = False

        elif choice == "2":
            run_six_state_benchmark()

        elif choice == "3":
            run_hardware_error_graph()

        elif choice == "4":
            print("Thank you for using the simulator!")
            break

        else:
            print("Invalid choice. Enter 1, 2, 3 or 4.")


if __name__ == "__main__":
    main()
