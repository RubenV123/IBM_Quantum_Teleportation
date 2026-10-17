# Quantum Teleportation on Real IBM Hardware: Measuring the Noise

**IBM Qiskit Fall Fest 2026 · RV University · Qiskit Quantum Computing Hackathon**

## Team

| Members |
| --- |
| Ruben Varghese |
| Sankalp PL |
| Gowthami Kasala |

---

## What is this project?

Quantum teleportation transfers an unknown quantum state from one qubit (Alice's) to another (Bob's) without physically moving the qubit itself or violating the no-cloning theorem.

Instead of copying data or transmitting information faster than light, the protocol relies on:
1. An **entangled Bell pair** shared between Alice and Bob.
2. Classical or quantum **corrections** applied to Bob's qubit based on operations on Alice's side.

Think of it like Alice and Bob sharing a pair of entangled "magic coins." Alice combines her secret message state with her coin and operates on her system. Bob can then apply standard bit or phase corrections to his coin, turning it into Alice's original state. The original state on Alice's qubit is destroyed in the process.

We built this project to test a simple question: **When we teleport the six standard cardinal states on actual IBM quantum hardware, how often does the protocol fail due to device noise?**

---

## How the Circuit Works

We use a 3-qubit circuit setup:

| Qubit | Role |
| --- | --- |
| `q0` | Alice's input state (the secret message) |
| `q1` | Alice's half of the entangled pair |
| `q2` | Bob's half of the entangled pair |

### Protocol Steps

1. **State Preparation:** Encode the message state onto `q0`.
2. **Entanglement:** Create a Bell pair between `q1` and `q2` using `H(1)` followed by `CX(1, 2)`.
3. **Bell Translation:** Apply `CX(0, 1)` and `H(0)` on Alice's side.
4. **Bob's Correction:** Apply conditional fixes (`CX(1, 2)` for $X$ correction, `CZ(0, 2)` for $Z$ correction).
5. **Verification:** Undo the message prep on Bob's qubit (`q2`) and measure it.

### Simulator vs. Hardware Implementations

* **Simulator Version (Options 1 & 2):** Alice measures `q0` and `q1` classically, and Bob's $X$ and $Z$ gates are applied only if the measured bits are 1. We compare states using fidelity metrics and Bloch sphere visualizers.
* **Hardware Version (Option 3):** Uses the equivalent **deferred-measurement** form where corrections are applied directly as controlled quantum gates (`CX`, `CZ`). The underlying physics is identical, but avoiding mid-circuit classical feed-forward keeps execution reliable on hardware backends.

### How We Measure Errors

After teleportation, we apply the *inverse* of the initial state preparation to Bob's qubit. If teleportation was 100% accurate, Bob's qubit collapses back to $|0\rangle$. Therefore, measuring $1$ indicates an error.

$$
\text{Error Rate} = \frac{\text{Counts of } |1\rangle}{\text{Total Shots}}
$$

---

## States Tested

We benchmarked all six cardinal poles of the Bloch sphere:

| Label | State Vector |
| --- | --- |
| |0⟩ | (1, 0) |
| |1⟩ | (0, 1) |
| |+⟩ | (1/√2, 1/√2) |
| |−⟩ | (1/√2, −1/√2) |
| |+i⟩ | (1/√2, i/√2) |
| |−i⟩ | (1/√2, −i/√2) |

---

## Setup & Dependencies

Requires Python 3 and, for hardware runs, a free IBM Quantum Platform account.

```bash
pip install -r requirements.txt
```

> **Known Issue on Windows:** Options 1 and 2 require `qiskit-aer`. On Windows running Python 3.14, Aer may terminate silently. If this occurs, set up a Python 3.12 virtual environment:
> ```bash
> py -3.12 -m venv venv
> venv\Scripts\activate
> pip install -r requirements.txt
> ```
> *Option 3 (real hardware) does not require Aer and runs on Python 3.14 without issues.*

---

## How to Run

Launch the interactive terminal menu:

```bash
python teleportation_lab.py
```

| Option | What it does |
| --- | --- |
| **1** | Teleport a selected state and compare Alice's and Bob's Bloch spheres *(Simulator)* |
| **2** | Run the six-state benchmark and plot fidelity graphs *(Simulator)* |
| **3** | Run the benchmark on a **real IBM quantum computer** and plot error rates |
| **4** | Exit |

**Option 3** prompts for your IBM Quantum API key (entered via hidden input). **The key is used strictly in-memory and is never saved or tracked in the repository.**

### Reproducing Our Saved Hardware Job

To load and plot our exact hackathon dataset without consuming queue minutes, choose Option 3 and enter Job ID:
`db9lv2ni0auc7390svv0` *(Requires an IBM account with access to the same instance).*

### Re-generating Circuit Diagrams

To draw `images/circuit.png`:

```bash
pip install pylatexenc
python make_circuit_diagram.py
```

---

## Hardware Results

These results come directly from an actual quantum processor:

* **Backend:** `ibm_kingston`
* **Date:** October 17, 2026
* **Shots per state:** 1024
* **Job ID:** `db9lv2ni0auc7390svv0`
* **Plan:** IBM Quantum Open Plan

| State | Real Hardware Error Rate |
| --- | --- |
| |0⟩ | 0.0566 |
| |1⟩ | 0.0654 |
| |+⟩ | 0.0596 |
| |−⟩ | 0.0381 |
| |+i⟩ | 0.0479 |
| |−i⟩ | 0.0498 |
| **Average** | **0.0529** |

### Key Takeaways

1. **Overall Performance:** On average, Bob's qubit returned to the expected state in **94.7%** of runs, yielding an average error rate of **5.3%**.
2. **Statistical Error Margin:** Error rates ranged between 3.8% and 6.5%. With 1024 shots per state, each bar carries a statistical uncertainty of roughly $\pm 0.6\%$ to $\pm 0.8\%$. Because these error bars overlap, we cannot conclude from a single run that any specific state teleports better than another.

---

## Limitations & What We Learned

* **Single Hardware Snapshot:** Device noise fluctuates over time due to thermal relaxation ($T_1/T_2$) and calibration drift. Repeating this run later on `ibm_kingston` would yield slightly different figures.
* **Lumped Noise:** The 5.3% error rate combines two-qubit gate decoherence, single-qubit gate errors, relaxation, and readout (measurement) errors. Isolating specific error sources requires Randomized Benchmarking or Process Tomography.
* **Indirect Verification:** Inverse state preparation measures state matching effectively, but it is not a full reconstruction of Bob's quantum state (which requires Quantum State Tomography).
* **Next Steps:** Benchmark across different timeframes and backends, integrate error mitigation like Zero-Noise Extrapolation (ZNE), and test dynamic circuits with mid-circuit readout on hardware.

---

## Credits & References

* C. H. Bennett et al., *Teleporting an unknown quantum state via dual classical and Einstein-Podolsky-Rosen channels*, Phys. Rev. Lett. 70, 1895 (1993).
* [Qiskit Documentation & IBM Quantum Learning](https://quantum.cloud.ibm.com/docs/)
* Google.com
* Wikipedia.com
* AI's Used: Gemini, Claude