import mido
from mido import Message, MidiFile, MidiTrack
import pygame
import numpy as np
import time
import threading

class WaveformVisualizer:
    def __init__(self, width=1000, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("MIDI Waveform Visualizer")
        
        self.active_notes = {}
        self.waveform_history = []
        self.max_history = 200
        self.running = True
        
        # Colors
        self.bg_color = (20, 20, 35)
        self.wave_color = (0, 255, 136)
        self.bar_color = (100, 100, 255)
        self.text_color = (200, 200, 200)
        
        # Font
        self.font = pygame.font.Font(None, 24)
        
    def generate_waveform(self, samples=500):
        """Generate waveform from active notes"""
        t = np.linspace(0, 0.05, samples)
        wave = np.zeros_like(t)
        
        for note, velocity in self.active_notes.items():
            freq = 440 * (2 ** ((note - 69) / 12))
            wave += (velocity / 127) * np.sin(2 * np.pi * freq * t)
        
        if len(self.active_notes) > 0:
            wave /= max(len(self.active_notes), 1)
            wave = np.clip(wave, -1, 1)
        
        return wave
    
    def draw_waveform(self, wave):
        """Draw the main waveform"""
        if len(wave) < 2:
            return
        
        # Waveform area
        waveform_height = self.height // 2 - 50
        center_y = waveform_height // 2 + 30
        
        points = []
        for i, amp in enumerate(wave):
            x = int((i / len(wave)) * (self.width - 40)) + 20
            y = int(center_y - amp * (waveform_height // 2 - 20))
            points.append((x, y))
        
        if len(points) > 1:
            pygame.draw.lines(self.screen, self.wave_color, False, points, 2)
        
        # Center line
        pygame.draw.line(self.screen, (50, 50, 70), 
                        (20, center_y), (self.width - 20, center_y), 1)
    
    def draw_spectrum(self):
        """Draw active notes as bars"""
        bar_area_top = self.height // 2 + 20
        bar_height_max = self.height // 2 - 60
        
        # Draw all possible notes (21-108)
        num_keys = 88
        bar_width = (self.width - 40) / num_keys
        
        for i in range(num_keys):
            note = i + 21
            x = 20 + i * bar_width
            
            # Check if note is active
            if note in self.active_notes:
                velocity = self.active_notes[note]
                height = (velocity / 127) * bar_height_max
                
                # Color based on note
                hue = (note * 4) % 360
                color = pygame.Color(0)
                color.hsva = (hue, 80, 100, 100)
                
                pygame.draw.rect(self.screen, color,
                               (x, bar_area_top + bar_height_max - height, 
                                bar_width - 1, height))
            else:
                # Dim background bar
                is_black = note % 12 in [1, 3, 6, 8, 10]
                bg_color = (30, 30, 45) if is_black else (40, 40, 55)
                pygame.draw.rect(self.screen, bg_color,
                               (x, bar_area_top + bar_height_max - 5, 
                                bar_width - 1, 5))
    
    def draw_note_info(self):
        """Display current notes being played"""
        y_offset = 5
        
        # Title
        title = self.font.render("Active Notes:", True, self.text_color)
        self.screen.blit(title, (10, y_offset))
        y_offset += 25
        
        # Note names
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        if self.active_notes:
            for note, velocity in sorted(self.active_notes.items()):
                octave = (note // 12) - 1
                note_name = note_names[note % 12]
                freq = 440 * (2 ** ((note - 69) / 12))
                
                text = f"{note_name}{octave} (MIDI {note}) - {freq:.1f}Hz - Vel:{velocity}"
                note_text = self.font.render(text, True, self.wave_color)
                self.screen.blit(note_text, (10, y_offset))
                y_offset += 22
        else:
            text = self.font.render("None", True, (100, 100, 100))
            self.screen.blit(text, (10, y_offset))
    
    def draw(self):
        """Main draw function"""
        self.screen.fill(self.bg_color)
        
        # Generate and draw waveform
        wave = self.generate_waveform()
        self.draw_waveform(wave)
        
        # Draw spectrum bars
        self.draw_spectrum()
        
        # Draw note info
        self.draw_note_info()
        
        # Divider line
        pygame.draw.line(self.screen, (70, 70, 90), 
                        (0, self.height // 2), 
                        (self.width, self.height // 2), 2)
        
        pygame.display.flip()
    
    def process_midi_messages(self, midi_file):
        """Process MIDI messages in real-time"""
        mid = MidiFile(midi_file)
        
        for msg in mid.play():
            if not self.running:
                break
            
            if msg.type == 'note_on' and msg.velocity > 0:
                self.active_notes[msg.note] = msg.velocity
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                self.active_notes.pop(msg.note, None)
    
    def visualize(self, midi_file):
        """Start visualization"""
        # Start MIDI playback
        pygame.mixer.init()
        pygame.mixer.music.load(midi_file)
        pygame.mixer.music.play()
        
        # Process MIDI messages in separate thread
        midi_thread = threading.Thread(target=self.process_midi_messages, args=(midi_file,))
        midi_thread.daemon = True
        midi_thread.start()
        
        # Main visualization loop
        clock = pygame.time.Clock()
        
        while self.running and (pygame.mixer.music.get_busy() or self.active_notes):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            self.draw()
            clock.tick(60)  # 60 FPS
        
        pygame.quit()


def numbers_to_midi_and_play(numbers, output_file='output.mid', visualize=True):
    # Create MIDI file
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Add tempo
    track.append(mido.MetaMessage('set_tempo', tempo=500000))
    
    for num in numbers:
        note = int(60 + (num % 24))
        track.append(Message('note_on', note=note, velocity=64, time=0))
        track.append(Message('note_off', note=note, velocity=64, time=480))
    
    mid.save(output_file)
    print(f"MIDI file saved: {output_file}")
    
    if visualize:
        # Play with visualization
        viz = WaveformVisualizer()
        viz.visualize(output_file)
    else:
        # Play without visualization
        pygame.mixer.init()
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    
    print("Playback finished")


class AdvancedWaveformVisualizer:
    def __init__(self, width=1200, height=700):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Advanced MIDI Visualizer")
        
        self.active_notes = {}
        self.waveform_history = []
        self.max_history = 100
        self.running = True
        
        # Visual settings
        self.show_waveform = True
        self.show_spectrum = True
        self.show_oscilloscope = True
        
        self.font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 32)
        
    def generate_waveform(self, samples=800):
        """Generate waveform from active notes"""
        t = np.linspace(0, 0.05, samples)
        wave = np.zeros_like(t)
        
        for note, velocity in self.active_notes.items():
            freq = 440 * (2 ** ((note - 69) / 12))
            wave += (velocity / 127) * np.sin(2 * np.pi * freq * t)
        
        if len(self.active_notes) > 0:
            wave /= max(len(self.active_notes), 1)
        
        return np.clip(wave, -1, 1)
    
    def draw_oscilloscope(self):
        """Draw scrolling oscilloscope"""
        osc_x = 20
        osc_y = 20
        osc_width = self.width - 40
        osc_height = 150
        
        # Background
        pygame.draw.rect(self.screen, (25, 25, 40), 
                        (osc_x, osc_y, osc_width, osc_height))
        
        # Title
        title = self.title_font.render("Waveform", True, (200, 200, 200))
        self.screen.blit(title, (osc_x + 10, osc_y - 30))
        
        # Generate current waveform
        wave = self.generate_waveform(samples=osc_width)
        
        # Add to history
        self.waveform_history.append(wave)
        if len(self.waveform_history) > self.max_history:
            self.waveform_history.pop(0)
        
        # Draw waveform
        center_y = osc_y + osc_height // 2
        points = []
        
        for i, amp in enumerate(wave):
            x = osc_x + i
            y = int(center_y - amp * (osc_height // 2 - 10))
            points.append((x, y))
        
        if len(points) > 1:
            # Glow effect
            for offset in range(3, 0, -1):
                alpha_color = (0, 255 - offset * 40, 136 - offset * 20)
                pygame.draw.lines(self.screen, alpha_color, False, points, offset)
        
        # Grid lines
        for i in range(5):
            y = osc_y + i * (osc_height // 4)
            pygame.draw.line(self.screen, (40, 40, 55), 
                           (osc_x, y), (osc_x + osc_width, y), 1)
    
    def draw_spectrum_bars(self):
        """Draw frequency spectrum"""
        spec_x = 20
        spec_y = 200
        spec_width = self.width - 40
        spec_height = 200
        
        # Background
        pygame.draw.rect(self.screen, (25, 25, 40), 
                        (spec_x, spec_y, spec_width, spec_height))
        
        # Title
        title = self.title_font.render("Spectrum Analyzer", True, (200, 200, 200))
        self.screen.blit(title, (spec_x + 10, spec_y - 30))
        
        # Draw bars for each note
        num_bars = 88
        bar_width = spec_width / num_bars
        
        for i in range(num_bars):
            note = i + 21
            x = spec_x + i * bar_width
            
            if note in self.active_notes:
                velocity = self.active_notes[note]
                height = (velocity / 127) * spec_height * 0.9
                
                # Color gradient based on frequency
                hue = (i / num_bars) * 300
                color = pygame.Color(0)
                color.hsva = (hue, 90, 100, 100)
                
                # Draw bar with glow
                for glow in range(2, -1, -1):
                    glow_color = tuple(max(0, c - glow * 30) for c in color[:3])
                    pygame.draw.rect(self.screen, glow_color,
                                   (x - glow, spec_y + spec_height - height - glow, 
                                    bar_width + glow * 2, height + glow * 2))
    
    def draw_piano_roll(self):
        """Draw mini piano roll"""
        piano_x = 20
        piano_y = 430
        piano_width = self.width - 40
        piano_height = 100
        
        # Title
        title = self.title_font.render("Piano Roll", True, (200, 200, 200))
        self.screen.blit(title, (piano_x + 10, piano_y - 30))
        
        num_keys = 88
        key_width = piano_width / num_keys
        
        for i in range(num_keys):
            note = i + 21
            x = piano_x + i * key_width
            
            # Determine if black or white key
            is_black = note % 12 in [1, 3, 6, 8, 10]
            
            if note in self.active_notes:
                # Active note - bright color
                hue = (note * 4) % 360
                color = pygame.Color(0)
                color.hsva = (hue, 80, 100, 100)
                height = piano_height
            else:
                # Inactive note
                color = (50, 50, 70) if is_black else (100, 100, 120)
                height = 40 if is_black else 60
            
            pygame.draw.rect(self.screen, color,
                           (x, piano_y + piano_height - height, 
                            max(1, key_width - 1), height))
    
    def draw_info_panel(self):
        """Draw information panel"""
        info_x = 20
        info_y = 560
        
        # Active notes
        y_offset = info_y
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        info_text = self.title_font.render("Active Notes:", True, (200, 200, 200))
        self.screen.blit(info_text, (info_x, y_offset))
        y_offset += 35
        
        if self.active_notes:
            for note, velocity in sorted(self.active_notes.items())[:5]:  # Show max 5
                octave = (note // 12) - 1
                note_name = note_names[note % 12]
                freq = 440 * (2 ** ((note - 69) / 12))
                
                text = f"♪ {note_name}{octave} - {freq:.1f} Hz - Velocity: {velocity}"
                rendered = self.font.render(text, True, (0, 255, 136))
                self.screen.blit(rendered, (info_x + 20, y_offset))
                y_offset += 25
        else:
            text = self.font.render("No notes playing", True, (100, 100, 120))
            self.screen.blit(text, (info_x + 20, y_offset))
        
        # Instructions
        inst_y = self.height - 25
        instructions = "Press ESC to exit"
        inst_text = self.font.render(instructions, True, (150, 150, 150))
        self.screen.blit(inst_text, (info_x, inst_y))
    
    def draw(self):
        """Main draw function"""
        self.screen.fill((15, 15, 25))
        
        self.draw_oscilloscope()
        self.draw_spectrum_bars()
        self.draw_piano_roll()
        self.draw_info_panel()
        
        pygame.display.flip()
    
    def process_midi_messages(self, midi_file):
        """Process MIDI messages"""
        mid = MidiFile(midi_file)
        
        for msg in mid.play():
            if not self.running:
                break
            
            if msg.type == 'note_on' and msg.velocity > 0:
                self.active_notes[msg.note] = msg.velocity
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                self.active_notes.pop(msg.note, None)
    
    def visualize(self, midi_file):
        """Start visualization"""
        pygame.mixer.init()
        pygame.mixer.music.load(midi_file)
        pygame.mixer.music.play()
        
        midi_thread = threading.Thread(target=self.process_midi_messages, args=(midi_file,))
        midi_thread.daemon = True
        midi_thread.start()
        
        clock = pygame.time.Clock()
        
        while self.running and (pygame.mixer.music.get_busy() or self.active_notes):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            self.draw()
            clock.tick(60)
        
        pygame.quit()


def numbers_to_midi_and_play(numbers, output_file='output.mid', visualize=True, advanced=False):
    """
    Convert numbers to MIDI and play with visualization
    
    Args:
        numbers: List of numbers to convert
        output_file: Output MIDI filename
        visualize: Whether to show visualization
        advanced: Use advanced visualizer (more features)
    """
    # Create MIDI file
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Add tempo
    track.append(mido.MetaMessage('set_tempo', tempo=500000))
    
    for num in numbers:
        note = int(60 + (num % 24))
        track.append(Message('note_on', note=note, velocity=64, time=0))
        track.append(Message('note_off', note=note, velocity=64, time=480))
    
    mid.save(output_file)
    print(f"MIDI file saved: {output_file}")
    
    if visualize:
        if advanced:
            viz = AdvancedWaveformVisualizer()
        else:
            viz = WaveformVisualizer()
        viz.visualize(output_file)
    else:
        pygame.mixer.init()
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    
    print("Playback finished")


# Test it
if __name__ == "__main__":
    # Simple sequence
    numbers = [1, 3, 5, 7, 9, 7, 5, 3, 1]
    numbers_to_midi_and_play(numbers, visualize=True, advanced=True)
    
    # More complex example
    # numbers = [i**2 % 20 for i in range(30)]
    # numbers_to_midi_and_play(numbers, visualize=True, advanced=True)