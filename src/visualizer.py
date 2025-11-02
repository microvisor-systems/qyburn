import pygame
import numpy as np
from collections import deque
import colorsys
import mido
from mido import Message, MidiFile, MidiTrack
from quantum_music_generator import QuantumMusicGenerator
import threading
import time


class NumberToAudioVisualizer:
    def __init__(self, width=1400, height=800):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Numbers to Audio Visualizer")

        # Audio settings
        self.SAMPLE_RATE = 44100
        self.audio_data = np.zeros(2048)
        self.frequency_data = np.zeros(1024)

        # Frequency bands
        self.bass = 0
        self.mid = 0
        self.treble = 0

        # History for smoothing
        self.bass_history = deque(maxlen=10)
        self.spectrum_history = deque(maxlen=5)

        # Visualization mode
        self.modes = ["spectrum", "circular", "waveform", "particles", "bars_3d", "all"]
        self.current_mode = 5  # Start with 'all' mode

        # Particle system
        self.particles = []
        self.max_particles = 200

        # Colors
        self.hue_offset = 0

        # Running flag
        self.running = True

        # Audio generation
        self.current_audio_chunk = np.zeros(2048)
        self.audio_position = 0
        self.full_audio = None

        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 20)

    def numbers_to_tones(self, numbers, duration=0.3, method="melodic"):
        """
        Convert numbers to audio tones

        Methods:
            'melodic': Musical notes
            'frequency': Direct frequency mapping
            'chord': Multiple harmonics
            'wave': Different waveform types
        """
        audio_chunks = []

        for num in numbers:
            if method == "melodic":
                # Map to musical scale
                note = int(60 + (num % 24))  # MIDI note
                freq = 440 * (2 ** ((note - 69) / 12))
                chunk = self.generate_tone(freq, duration, wave_type="sine")

            elif method == "frequency":
                # Direct frequency mapping
                freq = 200 + (num % 100) * 20  # 200-2200 Hz
                chunk = self.generate_tone(freq, duration, wave_type="sine")

            elif method == "chord":
                # Generate chord (root + third + fifth)
                note = int(60 + (num % 24))
                root_freq = 440 * (2 ** ((note - 69) / 12))
                third_freq = 440 * (2 ** ((note + 4 - 69) / 12))
                fifth_freq = 440 * (2 ** ((note + 7 - 69) / 12))

                chunk = (
                    self.generate_tone(root_freq, duration)
                    + self.generate_tone(third_freq, duration) * 0.5
                    + self.generate_tone(fifth_freq, duration) * 0.3
                )
                chunk /= 1.8

            elif method == "wave":
                # Different waveform types based on number
                note = int(60 + (num % 24))
                freq = 440 * (2 ** ((note - 69) / 12))
                wave_types = ["sine", "square", "sawtooth", "triangle"]
                wave_type = wave_types[num % len(wave_types)]
                chunk = self.generate_tone(freq, duration, wave_type=wave_type)

            audio_chunks.append(chunk)

        # Concatenate all chunks
        full_audio = np.concatenate(audio_chunks)

        # Normalize
        if np.max(np.abs(full_audio)) > 0:
            full_audio = full_audio / np.max(np.abs(full_audio)) * 0.8

        return full_audio

    def generate_tone(self, frequency, duration, wave_type="sine"):
        """Generate a tone with ADSR envelope"""
        samples = int(self.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, False)

        # Generate waveform
        if wave_type == "sine":
            wave = np.sin(2 * np.pi * frequency * t)
        elif wave_type == "square":
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == "sawtooth":
            wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        elif wave_type == "triangle":
            wave = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
        else:
            wave = np.sin(2 * np.pi * frequency * t)

        # Apply ADSR envelope
        envelope = self.create_envelope(samples)
        wave = wave * envelope

        return wave

    def create_envelope(
        self, samples, attack=0.05, decay=0.1, sustain=0.7, release=0.2
    ):
        """Create ADSR envelope"""
        envelope = np.zeros(samples)

        attack_samples = int(samples * attack)
        decay_samples = int(samples * decay)
        release_samples = int(samples * release)
        sustain_samples = samples - attack_samples - decay_samples - release_samples

        # Attack
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        # Decay
        start = attack_samples
        end = start + decay_samples
        envelope[start:end] = np.linspace(1, sustain, decay_samples)

        # Sustain
        start = end
        end = start + sustain_samples
        envelope[start:end] = sustain

        # Release
        start = end
        envelope[start:] = np.linspace(sustain, 0, release_samples)

        return envelope

    def play_audio(self, audio_data):
        """Play audio using pygame mixer"""
        # Convert to 16-bit integers
        audio_int16 = np.int16(audio_data * 32767)

        # Make stereo
        stereo_audio = np.column_stack((audio_int16, audio_int16))

        # Create pygame Sound object
        sound = pygame.sndarray.make_sound(stereo_audio)

        # Store full audio for visualization
        self.full_audio = audio_data
        self.audio_position = 0

        # Play
        sound.play()

        return sound

    def update_visualization_data(self):
        """Update audio data for visualization"""
        if self.full_audio is None:
            return

        chunk_size = 2048

        # Get current chunk of audio
        if self.audio_position + chunk_size < len(self.full_audio):
            self.current_audio_chunk = self.full_audio[
                self.audio_position : self.audio_position + chunk_size
            ]
            self.audio_position += chunk_size // 4  # Overlap for smoother visualization
        else:
            # Loop or fade out
            remaining = len(self.full_audio) - self.audio_position
            if remaining > 0:
                self.current_audio_chunk = np.pad(
                    self.full_audio[self.audio_position :],
                    (0, chunk_size - remaining),
                    "constant",
                )
            self.audio_position = 0  # Loop

        # Normalize
        if np.max(np.abs(self.current_audio_chunk)) > 0:
            self.audio_data = self.current_audio_chunk / np.max(
                np.abs(self.current_audio_chunk)
            )
        else:
            self.audio_data = self.current_audio_chunk

        # Perform FFT
        windowed = self.audio_data * np.hanning(len(self.audio_data))
        fft = np.fft.rfft(windowed)
        fft_magnitude = np.abs(fft)

        if np.max(fft_magnitude) > 0:
            self.frequency_data = fft_magnitude / np.max(fft_magnitude)
        else:
            self.frequency_data = fft_magnitude

        # Calculate frequency bands
        chunk = len(self.frequency_data)
        self.bass = np.mean(self.frequency_data[: chunk // 8])
        self.mid = np.mean(self.frequency_data[chunk // 8 : chunk // 4])
        self.treble = np.mean(self.frequency_data[chunk // 4 : chunk // 2])

        # Smooth bass
        self.bass_history.append(self.bass)
        self.bass = np.mean(self.bass_history)

        # Smooth spectrum
        self.spectrum_history.append(self.frequency_data.copy())
        if len(self.spectrum_history) > 0:
            self.frequency_data = np.mean(self.spectrum_history, axis=0)

    def draw_spectrum_bars(self):
        """Classic spectrum analyzer bars"""
        num_bars = 100
        bar_width = (self.width - 100) / num_bars
        max_height = self.height - 200

        samples_per_bar = len(self.frequency_data) // num_bars

        for i in range(num_bars):
            start_idx = i * samples_per_bar
            end_idx = start_idx + samples_per_bar
            if end_idx > len(self.frequency_data):
                break

            bar_value = np.mean(self.frequency_data[start_idx:end_idx])
            bar_height = bar_value * max_height

            x = 50 + i * bar_width
            y = self.height - 100 - bar_height

            hue = (i / num_bars + self.hue_offset) % 1.0
            rgb = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
            color = tuple(int(c * 255) for c in rgb)

            pygame.draw.rect(self.screen, color, (x, y, bar_width - 2, bar_height))

            if bar_height > 5:
                glow_color = tuple(min(255, int(c * 1.5)) for c in color)
                pygame.draw.rect(self.screen, glow_color, (x, y, bar_width - 2, 5))

    def draw_circular_visualizer(self):
        """Circular/radial spectrum analyzer"""
        center_x = self.width // 2
        center_y = self.height // 2
        base_radius = 100
        max_extension = 250

        num_bars = 120
        samples_per_bar = len(self.frequency_data) // num_bars

        for i in range(num_bars):
            start_idx = i * samples_per_bar
            end_idx = start_idx + samples_per_bar
            if end_idx > len(self.frequency_data):
                break

            bar_value = np.mean(self.frequency_data[start_idx:end_idx])
            extension = bar_value * max_extension

            angle = (i / num_bars) * 2 * np.pi

            inner_x = center_x + base_radius * np.cos(angle)
            inner_y = center_y + base_radius * np.sin(angle)
            outer_x = center_x + (base_radius + extension) * np.cos(angle)
            outer_y = center_y + (base_radius + extension) * np.sin(angle)

            hue = (i / num_bars + self.hue_offset) % 1.0
            rgb = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
            color = tuple(int(c * 255) for c in rgb)

            pygame.draw.line(
                self.screen, color, (inner_x, inner_y), (outer_x, outer_y), 3
            )

        # Draw center circle with bass reactivity
        bass_size = int(base_radius * (1 + self.bass * 0.5))
        for r in range(bass_size, 0, -5):
            alpha = r / bass_size
            hue = (self.hue_offset + 0.5) % 1.0
            rgb = colorsys.hsv_to_rgb(hue, 0.8, alpha)
            color = tuple(int(c * 255) for c in rgb)
            pygame.draw.circle(self.screen, color, (center_x, center_y), r, 2)

    def draw_waveform(self):
        """Oscilloscope-style waveform"""
        center_y = self.height // 2
        max_amplitude = self.height // 3

        num_points = min(len(self.audio_data), self.width - 100)
        step = len(self.audio_data) // num_points if num_points > 0 else 1

        points = []
        for i in range(num_points):
            x = 50 + i
            y = center_y + int(self.audio_data[i * step] * max_amplitude)
            points.append((x, y))

        if len(points) > 1:
            for offset in range(5, 0, -1):
                alpha = 255 - offset * 40
                hue = self.hue_offset
                rgb = colorsys.hsv_to_rgb(hue, 0.7, 1.0)
                color = tuple(int(c * alpha / 255) for c in [int(x * 255) for x in rgb])
                pygame.draw.lines(self.screen, color, False, points, offset)

        pygame.draw.line(
            self.screen, (50, 50, 80), (50, center_y), (self.width - 50, center_y), 1
        )

    def draw_particles(self):
        """Particle system that reacts to audio"""
        if self.bass > 0.3 and len(self.particles) < self.max_particles:
            for _ in range(int(self.bass * 10)):
                particle = {
                    "x": self.width // 2,
                    "y": self.height // 2,
                    "vx": np.random.randn() * 5 * self.bass,
                    "vy": np.random.randn() * 5 * self.bass,
                    "life": 1.0,
                    "hue": self.hue_offset,
                }
                self.particles.append(particle)

        particles_to_remove = []
        for particle in self.particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += 0.1
            particle["vx"] *= 0.99
            particle["vy"] *= 0.99
            particle["life"] -= 0.02

            if particle["life"] <= 0:
                particles_to_remove.append(particle)
            else:
                size = int(particle["life"] * 8 * (1 + self.bass))
                alpha = particle["life"]

                rgb = colorsys.hsv_to_rgb(particle["hue"], 0.8, 1.0)
                color = tuple(int(c * 255 * alpha) for c in rgb)

                pygame.draw.circle(
                    self.screen, color, (int(particle["x"]), int(particle["y"])), size
                )

        for particle in particles_to_remove:
            self.particles.remove(particle)

        # Background spectrum
        num_bars = 60
        bar_width = self.width / num_bars
        samples_per_bar = len(self.frequency_data) // num_bars

        for i in range(num_bars):
            start_idx = i * samples_per_bar
            end_idx = start_idx + samples_per_bar
            if end_idx > len(self.frequency_data):
                break

            bar_value = np.mean(self.frequency_data[start_idx:end_idx])
            bar_height = bar_value * (self.height - 100)

            x = i * bar_width
            y = self.height - bar_height

            hue = (i / num_bars + self.hue_offset) % 1.0
            rgb = colorsys.hsv_to_rgb(hue, 0.5, 0.5)
            color = tuple(int(c * 255) for c in rgb)

            pygame.draw.rect(self.screen, color, (x, y, bar_width - 2, bar_height))

    def draw_3d_bars(self):
        """Pseudo-3D perspective bars"""
        num_bars = 80
        bar_width = 15
        spacing = (self.width - 100) / num_bars
        max_height = self.height - 200

        samples_per_bar = len(self.frequency_data) // num_bars

        for i in range(num_bars):
            start_idx = i * samples_per_bar
            end_idx = start_idx + samples_per_bar
            if end_idx > len(self.frequency_data):
                break

            bar_value = np.mean(self.frequency_data[start_idx:end_idx])
            bar_height = bar_value * max_height

            depth = i / num_bars
            scale = 0.5 + depth * 0.5

            x = 50 + i * spacing
            y = self.height - 100 - bar_height * scale
            width = bar_width * scale
            height = bar_height * scale

            hue = (i / num_bars + self.hue_offset) % 1.0
            brightness = 0.5 + depth * 0.5
            rgb = colorsys.hsv_to_rgb(hue, 0.8, brightness)
            color = tuple(int(c * 255) for c in rgb)

            # Top face
            top_points = [
                (x, y),
                (x + width, y - width * 0.3),
                (x + width, y - width * 0.3 + height),
                (x, y + height),
            ]
            pygame.draw.polygon(self.screen, color, top_points)

            # Side face
            side_color = tuple(int(c * 0.7) for c in color)
            side_points = [
                (x + width, y - width * 0.3),
                (x + width + width * 0.5, y),
                (x + width + width * 0.5, y + height),
                (x + width, y - width * 0.3 + height),
            ]
            pygame.draw.polygon(self.screen, side_color, side_points)

    def draw_all_mode(self):
        """Combined view"""
        # Circular
        self.draw_small_circular(self.width // 2, 200, 80, 100)

        # Spectrum
        self.draw_small_spectrum(50, 350, self.width - 100, 150)

        # Waveform
        self.draw_small_waveform(50, 550, self.width - 100, 100)

        # Particles
        if self.bass > 0.4:
            for _ in range(int(self.bass * 3)):
                if len(self.particles) < 100:
                    particle = {
                        "x": np.random.randint(0, self.width),
                        "y": np.random.randint(0, self.height),
                        "vx": np.random.randn() * 2,
                        "vy": np.random.randn() * 2,
                        "life": 1.0,
                        "hue": self.hue_offset,
                    }
                    self.particles.append(particle)

        particles_to_remove = []
        for particle in self.particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["life"] -= 0.03

            if particle["life"] <= 0:
                particles_to_remove.append(particle)
            else:
                size = int(particle["life"] * 4)
                rgb = colorsys.hsv_to_rgb(particle["hue"], 0.6, 0.8)
                color = tuple(int(c * 255 * particle["life"]) for c in rgb)
                pygame.draw.circle(
                    self.screen, color, (int(particle["x"]), int(particle["y"])), size
                )

        for particle in particles_to_remove:
            self.particles.remove(particle)

    def draw_small_circular(self, center_x, center_y, base_radius, max_extension):
        """Small circular visualizer"""
        num_bars = 60
        samples_per_bar = len(self.frequency_data) // num_bars

        for i in range(num_bars):
            start_idx = i * samples_per_bar
            end_idx = start_idx + samples_per_bar
            if end_idx > len(self.frequency_data):
                break

            bar_value = np.mean(self.frequency_data[start_idx:end_idx])
            extension = bar_value * max_extension

            angle = (i / num_bars) * 2 * np.pi
            inner_x = center_x + base_radius * np.cos(angle)
            inner_y = center_y + base_radius * np.sin(angle)
            outer_x = center_x + (base_radius + extension) * np.cos(angle)
            outer_y = center_y + (base_radius + extension) * np.sin(angle)

            hue = (i / num_bars + self.hue_offset) % 1.0
            rgb = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
            color = tuple(int(c * 255) for c in rgb)

            pygame.draw.line(
                self.screen, color, (inner_x, inner_y), (outer_x, outer_y), 2
            )

    def draw_small_spectrum(self, x, y, width, height):
        """Small spectrum bars"""
        num_bars = 60
        bar_width = width / num_bars
        samples_per_bar = len(self.frequency_data) // num_bars

        for i in range(num_bars):
            start_idx = i * samples_per_bar
            end_idx = start_idx + samples_per_bar
            if end_idx > len(self.frequency_data):
                break

            bar_value = np.mean(self.frequency_data[start_idx:end_idx])
            bar_height = bar_value * height

            bar_x = x + i * bar_width
            bar_y = y + height - bar_height

            hue = (i / num_bars + self.hue_offset) % 1.0
            rgb = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
            color = tuple(int(c * 255) for c in rgb)

            pygame.draw.rect(
                self.screen, color, (bar_x, bar_y, bar_width - 2, bar_height)
            )

    def draw_small_waveform(self, x, y, width, height):
        """Small waveform"""
        center_y = y + height // 2

        num_points = min(len(self.audio_data), width)
        step = len(self.audio_data) // num_points if num_points > 0 else 1

        points = []
        for i in range(num_points):
            px = x + i
            py = center_y + int(self.audio_data[i * step] * height // 2)
            points.append((px, py))

        if len(points) > 1:
            hue = self.hue_offset
            rgb = colorsys.hsv_to_rgb(hue, 0.7, 1.0)
            color = tuple(int(c * 255) for c in rgb)
            pygame.draw.lines(self.screen, color, False, points, 2)

    def draw_info(self):
        """Draw info overlay"""
        mode_name = self.modes[self.current_mode].upper()
        title = self.title_font.render(mode_name, True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, 40))

        s = pygame.Surface((title_rect.width + 40, title_rect.height + 20))
        s.set_alpha(128)
        s.fill((0, 0, 0))
        self.screen.blit(s, (title_rect.x - 20, title_rect.y - 10))
        self.screen.blit(title, title_rect)

        instructions = [
            "SPACE: Change Mode",
            "ESC: Exit",
            f"Bass: {self.bass:.2f}",
            f"Mid: {self.mid:.2f}",
            f"Treble: {self.treble:.2f}",
        ]

        y_offset = self.height - 150
        for instruction in instructions:
            text = self.font.render(instruction, True, (200, 200, 200))
            text_rect = text.get_rect(left=20, top=y_offset)

            s = pygame.Surface((text_rect.width + 20, text_rect.height + 10))
            s.set_alpha(128)
            s.fill((0, 0, 0))
            self.screen.blit(s, (text_rect.x - 10, text_rect.y - 5))
            self.screen.blit(text, text_rect)
            y_offset += 25

    def draw(self):
        """Main draw function"""
        self.screen.fill((10, 10, 20))

        mode = self.modes[self.current_mode]

        if mode == "spectrum":
            self.draw_spectrum_bars()
        elif mode == "circular":
            self.draw_circular_visualizer()
        elif mode == "waveform":
            self.draw_waveform()
        elif mode == "particles":
            self.draw_particles()
        elif mode == "bars_3d":
            self.draw_3d_bars()
        elif mode == "all":
            self.draw_all_mode()

        self.draw_info()
        pygame.display.flip()

    def visualize_numbers(self, numbers, method="melodic", duration=0.3):
        """
        Convert numbers to audio and visualize

        Args:
            numbers: List of numbers to convert
            method: 'melodic', 'frequency', 'chord', or 'wave'
            duration: Duration of each note in seconds
        """
        print(f"Converting {len(numbers)} numbers to audio using '{method}' method...")

        # Generate audio from numbers
        audio_data = self.numbers_to_tones(numbers, duration, method)

        print(f"Generated {len(audio_data) / self.SAMPLE_RATE:.2f} seconds of audio")
        print("Starting playback and visualization...")

        # Play audio
        sound = self.play_audio(audio_data)

        # Visualization loop
        clock = pygame.time.Clock()

        while self.running and pygame.mixer.get_busy():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        self.current_mode = (self.current_mode + 1) % len(self.modes)
                        self.particles.clear()

            # Update visualization data
            self.update_visualization_data()

            # Update color cycling
            self.hue_offset = (self.hue_offset + 0.002) % 1.0

            # Draw
            self.draw()

            clock.tick(60)

        pygame.quit()
        print("Visualization complete!")


def demo_patterns():
    """Demo different number patterns and visualization methods"""

    print("=" * 60)
    print("NUMBER TO AUDIO VISUALIZER DEMO")
    print("=" * 60)

    patterns = {
        "1. Ascending Scale": list(range(20)),
        "2. Fibonacci": [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144],
        "3. Squares": [i**2 % 30 for i in range(20)],
        "4. Random Walk": [0] + list(np.cumsum(np.random.randint(-3, 4, 19))),
        "5. Sine Wave": [int(15 * np.sin(i * 0.5) + 15) for i in range(30)],
        "6. Prime Numbers": [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47],
    }

    print("\nAvailable Patterns:")
    for name in patterns.keys():
        print(f"  {name}")

    print("\nAvailable Methods:")
    print("  - melodic: Musical notes (default)")
    print("  - frequency: Direct frequency mapping")
    print("  - chord: Multiple harmonics")
    print("  - wave: Different waveform types")

    # Example: Let's use sine wave pattern with melodic method
    pattern_name = "5. Sine Wave"
    numbers = patterns[pattern_name]

    print(f"\n▶ Playing: {pattern_name}")
    print(f"  Numbers: {numbers}")

    viz = NumberToAudioVisualizer()
    viz.visualize_numbers(numbers, method="melodic", duration=0.3)


def custom_numbers_visualizer(numbers, method="melodic", duration=0.3):
    """
    Visualize your own array of numbers

    Args:
        numbers: List of numbers to convert to audio
        method: 'melodic', 'frequency', 'chord', or 'wave'
        duration: Duration of each note in seconds
    """
    viz = NumberToAudioVisualizer()
    viz.visualize_numbers(numbers, method=method, duration=duration)


# Example usage
if __name__ == "__main__":
    # Demo mode - shows various patterns
    # demo_patterns()

    # Custom numbers - YOUR ARRAY HERE!
    # my_numbers = [1, 3, 5, 7, 9, 11, 13, 11, 9, 7, 5, 3, 1]

    # Try different methods:
    # 'melodic' - Musical notes (nice melodies)
    # 'frequency' - Direct frequency mapping (more electronic)
    # 'chord' - Harmonies (richer sound)
    # 'wave' - Different waveforms (varied timbres)

    # custom_numbers_visualizer(my_numbers, method="melodic", duration=0.4)

    # Or try other patterns:
    # custom_numbers_visualizer([i**2 % 20 for i in range(25)], method='chord', duration=0.3)
    # custom_numbers_visualizer(list(range(1, 25)), method='wave', duration=0.2)

    # Create quantum music generator
    qm = QuantumMusicGenerator(shots=1024)
    
    # Generate quantum notes
    quantum_notes = qm.entangled_melody(num_qubits=4, num_notes=25)
    
    # Visualize
    custom_numbers_visualizer(quantum_notes, method="melodic", duration=0.3)
    
    # Or try different patterns:
    # quantum_notes = qm.qft_harmony(num_qubits=5, num_notes=30)
    # custom_numbers_visualizer(quantum_notes, method="chord", duration=0.25)
