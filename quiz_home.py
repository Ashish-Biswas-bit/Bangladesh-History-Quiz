import pygame
import sys
import os
import subprocess

pygame.init()
pygame.mixer.init()

# Window setup
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quiz Game Home")

# Fonts
font = pygame.font.SysFont("arial", 48, bold=True)
small_font = pygame.font.SysFont("arial", 28)

# Colors
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
BLUE = (70, 130, 180)
LIGHT_BLUE = (135, 206, 250)
DARK_BLUE = (25, 50, 90)
GRAY = (180, 180, 180)
GREEN = (50, 180, 70)

GAME_NAME = "Bangladesh History Quiz"
TOTAL_QUESTIONS = 10

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

click_sound = pygame.mixer.Sound(resource_path("click.mp3"))
click_sound.play()

def draw_gradient_background(surface, color_top, color_bottom):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = GRAY
        self.color_active = BLUE
        self.color = self.color_inactive
        self.text = text
        self.txt_surface = small_font.render(text, True, BLACK)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.color = self.color_inactive
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < 15:
                self.text += event.unicode
            self.txt_surface = small_font.render(self.text, True, BLACK)

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+10, self.rect.y+10))
        pygame.draw.rect(screen, self.color, self.rect, 3, border_radius=8)

def main():
    clock = pygame.time.Clock()
    input_box = InputBox(180, 180, 240, 50)
    start_button = pygame.Rect(WIDTH//2 - 75, 270, 150, 60)

    running = True
    while running:
        draw_gradient_background(screen, LIGHT_BLUE, DARK_BLUE)

        title_surf = font.render(GAME_NAME, True, WHITE)
        title_rect = title_surf.get_rect(center=(WIDTH//2, 70))
        screen.blit(title_surf, title_rect)

        q_surf = small_font.render(f"Total Questions: {TOTAL_QUESTIONS}", True, WHITE)
        q_rect = q_surf.get_rect(center=(WIDTH//2, 140))
        screen.blit(q_surf, q_rect)

        label_surf = small_font.render("Enter your name:", True, WHITE)
        label_rect = label_surf.get_rect(midleft=(50, 205))
        screen.blit(label_surf, label_rect)
        input_box.rect.topleft = (label_rect.right + 10, 185)
        input_box.draw(screen)

        mouse_pos = pygame.mouse.get_pos()
        if start_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, GREEN, start_button, border_radius=12)
        else:
            pygame.draw.rect(screen, BLUE, start_button, border_radius=12)

        start_surf = small_font.render("Start Quiz", True, WHITE)
        start_rect = start_surf.get_rect(center=start_button.center)
        screen.blit(start_surf, start_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            input_box.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and start_button.collidepoint(event.pos):
                click_sound.play()
                pygame.time.delay(200)
                player_name = input_box.text.strip() or "Guest"
                pygame.quit()
                subprocess.Popen(["python", "quiz_game.py", player_name, str(TOTAL_QUESTIONS)])
                sys.exit()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
