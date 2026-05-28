import pygame
import numpy as np
import sys

# CHAKRA HOLOGRAM · TETHER · CREATE
# Standalone, no browser, no WebGL2 issues

WIDTH, HEIGHT = 1200, 800
FPS = 60

# Colors from your template
VOID = (1, 1, 8)
COBALT = (42, 92, 187)
GOLD = (212, 168, 76)
SARAH = (192, 136, 255)
ROTH = (90, 170, 139)
CHAKRAS = [
    (221, 51, 51), (238, 119, 34), (221, 187, 34),
    (51, 187, 85), (51, 136, 221), (102, 68, 204), (170, 68, 221)
]

class HologramApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("CHAKRA HOLOGRAM · TETHER · CREATE")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('consolas', 14)

        self.objects = [] # (x, y, amp)
        self.wavelength = 20.0
        self.hammy_phase = 0.0
        self.hammy_on = False
        self.active_chakra = 3 # Heart
        self.beams_enabled = [True] * 7

        # Precompute for speed
        self.y_grid, self.x_grid = np.mgrid[0:HEIGHT, 0:WIDTH]
        self.x_grid = (self.x_grid - WIDTH/2) / 100.0
        self.y_grid = (self.y_grid - HEIGHT/2) / 100.0

    def compute_hologram(self):
        """GPU-style computation on CPU with numpy"""
        k = 2 * np.pi / self.wavelength

        # Reference beams (7 chakras)
        R_real = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
        R_imag = np.zeros((HEIGHT, WIDTH), dtype=np.float32)

        for i, enabled in enumerate(self.beams_enabled):
            if not enabled: continue
            angle = i * np.pi / 3.5
            phase_offset = i * 0.5 + self.hammy_phase
            phase = k * (self.x_grid * np.cos(angle) + self.y_grid * np.sin(angle)) + phase_offset
            R_real += np.cos(phase) * 0.3
            R_imag += np.sin(phase) * 0.3

        # Object waves
        O_real = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
        O_imag = np.zeros((HEIGHT, WIDTH), dtype=np.float32)

        for ox, oy, amp in self.objects:
            ox_norm = (ox - WIDTH/2) / 100.0
            oy_norm = (oy - HEIGHT/2) / 100.0
            dx = self.x_grid - ox_norm
            dy = self.y_grid - oy_norm
            r = np.sqrt(dx*dx + dy*dy) + 0.01
            phase = k * r
            O_real += np.cos(phase) * amp / r
            O_imag += np.sin(phase) * amp / r

        # Interference: |R + O|²
        total_real = R_real + O_real
        total_imag = R_imag + O_imag
        intensity = total_real**2 + total_imag**2

        # Map to color
        hue = (np.arctan2(total_imag, total_real) / (2*np.pi) + 0.5)
        hue_idx = (hue * 7).astype(int) % 7

        # Create RGB image
        img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        for i, color in enumerate(CHAKRAS):
            mask = (hue_idx == i)
            val = np.clip(intensity[mask] * 80, 0, 255)
            img[mask, 0] = (color[0] * val / 255).astype(np.uint8)
            img[mask, 1] = (color[1] * val / 255).astype(np.uint8)
            img[mask, 2] = (color[2] * val / 255).astype(np.uint8)

        return pygame.surfarray.make_surface(np.transpose(img, (1, 0, 2)))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        self.objects.append((event.pos[0], event.pos[1], 1.0))
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.objects.clear()
                    elif event.key == pygame.K_h:
                        self.hammy_on = not self.hammy_on
                    elif event.key == pygame.K_SPACE:
                        self.beams_enabled = [not b for b in self.beams_enabled]

            if self.hammy_on:
                self.hammy_phase += 0.01 # 1.01x spiral

            # Render
            self.screen.fill(VOID)
            holo = self.compute_hologram()
            self.screen.blit(holo, (0, 0))

            # HUD
            hud = self.font.render(
                f"CHAKRA HOLOGRAM · Objects: {len(self.objects)} · Hammy: {'ON' if self.hammy_on else 'OFF'} · [Click] add · [C] clear · [H] hammy · [SPACE] toggle beams",
                True, (200, 220, 255)
            )
            self.screen.blit(hud, (10, 10))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = HologramApp()
    app.run()