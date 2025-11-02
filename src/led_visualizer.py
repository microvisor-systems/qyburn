from gpiozero import LED
from time import sleep
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
import numpy as np


# ==================== LED SETUP ====================
class LEDVisualizer:
    """Control LEDs in sync with quantum music"""

    def __init__(self):
        self.red_led = LED(6)
        self.green_led = LED(26)
        self.blue_led = LED(17)
        self.yellow_led = LED(21)
        self.white_led = LED(12)

        self.leds = [
            self.red_led,
            self.green_led,
            self.blue_led,
            self.yellow_led,
            self.white_led,
        ]
        self.led_names = ["Red", "Green", "Blue", "Yellow", "White"]

    def all_off(self):
        """Turn off all LEDs"""
        for led in self.leds:
            led.off()

    def all_on(self):
        """Turn on all LEDs"""
        for led in self.leds:
            led.on()

    def cleanup(self):
        """Clean up GPIO"""
        self.all_off()

    def play_note(self, value, max_value=31, duration=0.3, mode="range"):
        """
        Light up LEDs based on quantum number value

        Modes:
        - 'range': Different value ranges = different LEDs
        - 'binary': Binary representation lights up LEDs
        - 'intensity': More LEDs = higher values
        - 'sequential': Cycle through LEDs
        - 'random': Random LED for each note
        """

        if mode == "range":
            # Divide the value range into 5 sections for 5 LEDs
            section_size = max_value / 5
            led_index = min(int(value / section_size), 4)

            self.all_off()
            self.leds[led_index].on()
            print(f"Note {value:2d} → {self.led_names[led_index]:6s} LED", end="\r")
            sleep(duration)
            self.leds[led_index].off()

        elif mode == "binary":
            # Use binary representation (5 LEDs = 5 bits)
            self.all_off()
            binary = format(value, "05b")  # 5-bit binary

            for i, bit in enumerate(binary):
                if bit == "1" and i < 5:
                    self.leds[i].on()

            print(
                f"Note {value:2d} (binary: {binary}) → LEDs: {[self.led_names[i] for i, bit in enumerate(binary) if bit == '1' and i < 5]}",
                end="\r",
            )
            sleep(duration)
            self.all_off()

        elif mode == "intensity":
            # More LEDs light up for higher values
            self.all_off()
            num_leds = int((value / max_value) * 5) + 1
            num_leds = min(num_leds, 5)

            for i in range(num_leds):
                self.leds[i].on()

            print(f"Note {value:2d} → {num_leds} LEDs on", end="\r")
            sleep(duration)
            self.all_off()

        elif mode == "sequential":
            # Just cycle through LEDs regardless of value
            led_index = value % 5

            self.all_off()
            self.leds[led_index].on()
            print(f"Note {value:2d} → {self.led_names[led_index]:6s} LED", end="\r")
            sleep(duration)
            self.leds[led_index].off()

        elif mode == "random":
            # Pick random LED(s) based on value as seed
            np.random.seed(value)
            num_leds = np.random.randint(1, 6)
            led_indices = np.random.choice(5, size=num_leds, replace=False)

            self.all_off()
            for idx in led_indices:
                self.leds[idx].on()

            print(f"Note {value:2d} → Random pattern", end="\r")
            sleep(duration)
            self.all_off()

        elif mode == "all":
            # All LEDs blink together
            self.all_on()
            print(f"Note {value:2d} → All LEDs", end="\r")
            sleep(duration)
            self.all_off()
            sleep(duration * 0.5)


# ==================== QUANTUM MUSIC GENERATOR ====================
class QuantumMusicGenerator:
    """Generate musical note arrays from quantum circuits"""

    def __init__(self, shots=1024):
        self.simulator = AerSimulator()
        self.shots = shots

    def run_circuit(self, circuit):
        """Execute a quantum circuit and return measurement results"""
        compiled_circuit = transpile(circuit, self.simulator)
        job = self.simulator.run(compiled_circuit, shots=self.shots)
        result = job.result()
        counts = result.get_counts(circuit)
        return counts

    def counts_to_numbers(self, counts, num_notes=20):
        """Convert measurement counts to an array of numbers"""
        numbers = []

        for bitstring, count in counts.items():
            value = int(bitstring, 2)
            numbers.extend([value] * count)

        np.random.shuffle(numbers)
        return numbers[:num_notes]

    def superposition_random(self, num_qubits=5, num_notes=20):
        """Pure quantum randomness from superposition"""
        qc = QuantumCircuit(num_qubits, num_qubits)

        for i in range(num_qubits):
            qc.h(i)

        qc.measure(range(num_qubits), range(num_qubits))

        counts = self.run_circuit(qc)
        return self.counts_to_numbers(counts, num_notes)

    def entangled_melody(self, num_qubits=5, num_notes=20):
        """Create correlated notes using entanglement"""
        qc = QuantumCircuit(num_qubits, num_qubits)

        qc.h(0)
        for i in range(num_qubits - 1):
            qc.cx(i, i + 1)

        for i in range(num_qubits):
            qc.ry(np.pi / 4 * i, i)

        qc.measure(range(num_qubits), range(num_qubits))

        counts = self.run_circuit(qc)
        return self.counts_to_numbers(counts, num_notes)

    def bell_state_chords(self, num_notes=20):
        """Create harmonious chords using Bell states"""
        qc = QuantumCircuit(5, 5)

        qc.h(0)
        qc.cx(0, 1)

        qc.h(2)
        qc.cx(2, 3)

        qc.cx(1, 2)
        qc.h(1)
        qc.h(4)

        qc.measure(range(5), range(5))

        counts = self.run_circuit(qc)
        return self.counts_to_numbers(counts, num_notes)

    def quantum_walk_melody(self, steps=5, num_notes=20):
        """Quantum walk creates a melodic progression"""
        num_qubits = 5
        qc = QuantumCircuit(num_qubits, num_qubits)

        qc.h(0)

        for step in range(steps):
            qc.h(0)

            for i in range(num_qubits - 1):
                qc.cx(0, i + 1)

            qc.p(np.pi / (step + 1), 0)

        qc.measure(range(num_qubits), range(num_qubits))

        counts = self.run_circuit(qc)
        return self.counts_to_numbers(counts, num_notes)


# ==================== MAIN INTEGRATION ====================
def quantum_led_visualizer(
    pattern="entangled", num_notes=30, duration=0.3, mode="range"
):
    """
    Main function to run quantum music with LED visualization

    Parameters:
    - pattern: "random", "entangled", "bell", "walk"
    - num_notes: How many notes to generate
    - duration: How long each LED stays on (seconds)
    - mode: "range", "binary", "intensity", "sequential", "random", "all"
    """

    print("=" * 60)
    print("QUANTUM LED MUSIC VISUALIZER")
    print("=" * 60)
    print(f"\nPattern: {pattern}")
    print(f"Mode: {mode}")
    print(f"Notes: {num_notes}")
    print(f"Duration: {duration}s per note")
    print("\nGenerating quantum music...\n")

    # Initialize
    qm = QuantumMusicGenerator(shots=1024)
    leds = LEDVisualizer()

    try:
        # Generate quantum numbers
        if pattern == "random":
            numbers = qm.superposition_random(num_qubits=5, num_notes=num_notes)
        elif pattern == "entangled":
            numbers = qm.entangled_melody(num_qubits=5, num_notes=num_notes)
        elif pattern == "bell":
            numbers = qm.bell_state_chords(num_notes=num_notes)
        elif pattern == "walk":
            numbers = qm.quantum_walk_melody(steps=5, num_notes=num_notes)
        else:
            numbers = qm.entangled_melody(num_qubits=5, num_notes=num_notes)

        print(f"Quantum numbers: {numbers}\n")
        print("Playing... (Press Ctrl+C to stop)\n")

        # Play the melody with LEDs
        max_value = max(numbers)

        for i, value in enumerate(numbers):
            print(f"[{i+1}/{len(numbers)}] ", end="")
            leds.play_note(value, max_value=max_value, duration=duration, mode=mode)

        print("\n\nFinished!")

    except KeyboardInterrupt:
        print("\n\nStopped by user")

    finally:
        leds.cleanup()


# ==================== DEMO FUNCTIONS ====================


def demo_all_modes():
    """Demo all LED visualization modes"""
    patterns = ["entangled", "random", "bell", "walk"]
    modes = ["range", "binary", "intensity", "sequential"]

    for pattern in patterns:
        for mode in modes:
            print(f"\n{'='*60}")
            print(f"Pattern: {pattern.upper()} | Mode: {mode.upper()}")
            print("=" * 60)

            quantum_led_visualizer(
                pattern=pattern, num_notes=15, duration=0.25, mode=mode
            )

            sleep(2)  # Pause between demos


def simple_demo():
    """Simple demo - just run one pattern"""
    quantum_led_visualizer(
        pattern="entangled", num_notes=30, duration=0.3, mode="binary"
    )


# ==================== INTERACTIVE MODE ====================


def interactive_mode():
    """Interactive mode - choose your settings"""
    print("\n" + "=" * 60)
    print("QUANTUM LED MUSIC VISUALIZER - INTERACTIVE MODE")
    print("=" * 60)

    print("\nSelect Pattern:")
    print("  1. Random (Superposition)")
    print("  2. Entangled Melody")
    print("  3. Bell State Chords")
    print("  4. Quantum Walk")

    pattern_choice = input("\nEnter choice (1-4) [default: 2]: ") or "2"
    patterns = {"1": "random", "2": "entangled", "3": "bell", "4": "walk"}
    pattern = patterns.get(pattern_choice, "entangled")

    print("\nSelect LED Mode:")
    print("  1. Range (different LEDs for different value ranges)")
    print("  2. Binary (LEDs show binary representation)")
    print("  3. Intensity (more LEDs = higher value)")
    print("  4. Sequential (cycle through LEDs)")
    print("  5. Random (random LED patterns)")

    mode_choice = input("\nEnter choice (1-5) [default: 2]: ") or "2"
    modes = {
        "1": "range",
        "2": "binary",
        "3": "intensity",
        "4": "sequential",
        "5": "random",
    }
    mode = modes.get(mode_choice, "binary")

    num_notes = input("\nNumber of notes [default: 30]: ") or "30"
    num_notes = int(num_notes)

    duration = input("Duration per note in seconds [default: 0.3]: ") or "0.3"
    duration = float(duration)

    quantum_led_visualizer(
        pattern=pattern, num_notes=num_notes, duration=duration, mode=mode
    )


# ==================== RUN ====================

if __name__ == "__main__":
    # Choose one of these to run:

    # Option 1: Simple demo
    simple_demo()

    # Option 2: Interactive mode
    # interactive_mode()

    # Option 3: Demo all modes (takes a while)
    # demo_all_modes()

    # Option 4: Custom run
    # quantum_led_visualizer(
    #     pattern="bell",      # "random", "entangled", "bell", "walk"
    #     num_notes=40,
    #     duration=0.25,
    #     mode="binary"        # "range", "binary", "intensity", "sequential", "random"
    # )
