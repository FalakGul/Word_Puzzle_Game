import pygame
import math
import sys
import os
from datetime import datetime
from collections import deque

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Word Puzzle Game")

# Load and scale resources
BACKGROUND_IMAGE = pygame.image.load("pg15.gif")
BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (WIDTH, HEIGHT))
GAME_BACKGROUND_IMAGE = pygame.image.load("pic (1).jpg")
GAME_BACKGROUND_IMAGE = pygame.transform.scale(GAME_BACKGROUND_IMAGE, (WIDTH, HEIGHT))

pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (25, 25, 112)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GRAY = (211, 211, 211)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
SELECTED_LETTER_BG = (240, 248, 255)

# Fonts
font = pygame.font.Font(None, 36)
button_font = pygame.font.Font(None, 30)
header_font = pygame.font.Font(None, 48)
score_font = pygame.font.Font(None, 30)
input_font = pygame.font.Font(None, 40)

# Sound effects
click_sound = pygame.mixer.Sound("click.mp3")
correct_sound = pygame.mixer.Sound("correct.mp3")
wrong_sound = pygame.mixer.Sound("wrong.mp3")

# Game data
letters = ["S", "T", "H", "I", "N", "K"]
word_list = ["his", "hit", "ink", "kit", "sit", "sink", "skin", "thin", "this", "think", "stink"]
guessed_words = set()
selected_letters = []
score = 0
timer = 60
game_over = False
user_name = ""  # To store the usernames
mouse_dragging = False  #for mouse dragging


selected_letters = []
# Stack for Undo functionality
selection_stack = []

# deque for hints globally
hint_deque = deque([word for word in word_list if word not in guessed_words])

# File to store winners
WINNERS_FILE = "winners.txt"

# Circle layout for letters
center_x, center_y = WIDTH // 2, HEIGHT // 2
radius = 100
letter_positions = [
    (center_x + radius * math.cos(2 * math.pi * i / len(letters)),
     center_y + radius * math.sin(2 * math.pi * i / len(letters)))
    for i in range(len(letters))
]

# Track coupon availability
coupons = {
    "75%": 1,
    "50%": 1,
    "25%": 2,
}

# Function to draw buttons
def draw_button(x, y, width, height, text, color, hover_color):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    is_hovered = x <= mouse_x <= x + width and y <= mouse_y <= y + height
    pygame.draw.rect(screen, hover_color if is_hovered else color, (x, y, width, height), border_radius=20)
    text_surface = button_font.render(text, True, WHITE)
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (height - text_surface.get_height()) // 2))
    return is_hovered

# Check if the name already exists in the winners file
def is_name_used(name):
    if not os.path.exists(WINNERS_FILE):
        return False
    with open(WINNERS_FILE, "r") as file:
        for line in file:
            if name.strip() == line.strip().split(" - ")[0]:
                return True
    return False

# Handle name entry window
def name_entry_window():
    global user_name

    input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 25, 300, 50)
    name = ""
    clock = pygame.time.Clock()
    active = True
    error_message = ""

    while active:
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.K_RETURN:
                    if name.strip() == "":
                        error_message = "Name cannot be empty!"
                    elif is_name_used(name):
                        error_message = "Name already used. Try another!"
                    else:
                        user_name = name
                        active = False
                else:
                    name += event.unicode

        pygame.draw.rect(screen, WHITE, input_box, border_radius=10)
        name_text = input_font.render(name, True, BLACK)
        screen.blit(name_text, (input_box.x + 10, input_box.y + 10))

        header_text = header_font.render("Enter Your Name", True, DARK_BLUE)
        screen.blit(header_text, (WIDTH // 2 - header_text.get_width() // 2, HEIGHT // 2 - 100))
        if error_message:
            error_text = font.render(error_message, True, RED)
            screen.blit(error_text, (WIDTH // 2 - error_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(30)

# Draw game elements
def draw_game_elements():
    screen.blit(GAME_BACKGROUND_IMAGE, (0, 0))

    header_text = header_font.render(f"Player: {user_name}", True, DARK_BLUE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    timer_text = font.render(f"Time: {timer}s", True, RED)

    screen.blit(header_text, (10, 10))
    screen.blit(score_text, (WIDTH - 150, 10))
    screen.blit(timer_text, (WIDTH - 150, 50))

    for i, (x, y) in enumerate(letter_positions):
        pygame.draw.circle(screen, LIGHT_BLUE, (int(x) + 5, int(y) + 5), 35)
        pygame.draw.circle(screen, DARK_BLUE, (int(x), int(y)), 30)
        letter_text = font.render(letters[i], True, WHITE)
        screen.blit(letter_text, (x - letter_text.get_width() // 2, y - letter_text.get_height() // 2))

    box_x, box_y = center_x - 160, center_y + 170
    box_width, box_height = 320, 50
    pygame.draw.rect(screen, LIGHT_GRAY, (box_x + 5, box_y + 5, box_width, box_height), border_radius=20)
    pygame.draw.rect(screen, SELECTED_LETTER_BG, (box_x, box_y, box_width, box_height), border_radius=20)
    selected_text = font.render("".join(selected_letters), True, BLACK)
    screen.blit(selected_text, (box_x + (box_width - selected_text.get_width()) // 2, box_y + (box_height - selected_text.get_height()) // 2))

    guessed_x, guessed_y = 50, 100
    for word in word_list:
        if word in guessed_words:
            word_text = font.render(word.upper(), True, GREEN)
        else:
            word_text = font.render("_ " * len(word), True, BLACK)
        screen.blit(word_text, (guessed_x, guessed_y))
        guessed_y += 40

    submit_hovered = draw_button(WIDTH - 200, HEIGHT - 100, 80, 40, "Submit", DARK_BLUE, LIGHT_BLUE)
    clear_hovered = draw_button(WIDTH - 100, HEIGHT - 100, 80, 40, "Clear", DARK_BLUE, LIGHT_BLUE)
    undo_hovered = draw_button(WIDTH - 150, HEIGHT - 50, 80, 40, "Undo", DARK_BLUE, LIGHT_BLUE)
    hint_hovered = draw_button(WIDTH - 260, HEIGHT - 50, 100, 40, "Hint", DARK_BLUE, LIGHT_BLUE)

    return submit_hovered, clear_hovered ,undo_hovered, hint_hovered

# Handle submit logic
def handle_submit():
    global score, selected_letters, guessed_words
    selected_word = "".join(selected_letters).lower()
    if selected_word in word_list and selected_word not in guessed_words:
        guessed_words.add(selected_word)
        score += 10
        correct_sound.play()
    else:
        wrong_sound.play()
    selected_letters.clear()

# Handle undo logic
def handle_undo():
    global selected_letters, selection_stack
    if selection_stack:
        selected_letters = selection_stack.pop()

# Handle clear button
def handle_clear():
    global selected_letters
    selected_letters.clear()


# Update and display the hint
def provide_hint():
    if hint_deque:
        hint = hint_deque.popleft()
        return hint
    else:
        return None

'''def add_letter(letter):
    global selected_letters, selection_stack
    # Push current state to stack before changing
    selection_stack.append(selected_letters[:])  # Append a copy
    selected_letters.append(letter)'''

# Display the discount coupon screen
def show_coupon_screen():
    global coupons

    guessed_count = len(guessed_words)
    coupon_code = ""
    if guessed_count == len(word_list) and coupons["75%"] > 0:
        coupon_code = "75% Discount Code"
        coupons["75%"] -= 1
    elif guessed_count >= 8 and coupons["50%"] > 0:
        coupon_code = "50% Discount Code"
        coupons["50%"] -= 1
    elif guessed_count >= 6 and coupons["25%"] > 0:
        coupon_code = "25% Discount Code"
        coupons["25%"] -= 1

    # Save the winner's details
    if coupon_code:
        with open(WINNERS_FILE, "a") as file:
            file.write(f"{user_name} - {coupon_code} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Display the coupon screen
    clock = pygame.time.Clock()
    running = True
    header = "Congratulations!" if coupon_code else "Better Luck Next Time!"
    message = f"Your {coupon_code}" if coupon_code else "No coupon available."

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    running = False

        header_text = header_font.render(header, True, GREEN if coupon_code else RED)
        message_text = font.render(message, True, WHITE)
        footer_text = font.render("Press Enter to Exit", True, RED)

        screen.blit(header_text, (WIDTH // 2 - header_text.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(footer_text, (WIDTH // 2 - footer_text.get_width() // 2, HEIGHT // 2 + 100))

        pygame.display.flip()
        clock.tick(30)

# Main game loop
def game_loop():
    global timer, game_over, selected_letters, mouse_dragging

    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill(BLACK)
        submit_hovered, clear_hovered, undo_hovered, hint_hovered = draw_game_elements()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click
                    mouse_dragging = False
                    if submit_hovered:
                        handle_submit()
                    elif clear_hovered:
                        handle_clear()
                    elif undo_hovered:
                        handle_undo()
                    elif hint_hovered:
                        hint = provide_hint()
                        if hint:
                            hint_text = font.render(f"Hint: {hint}", True, GREEN)
                            screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT - 165))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        if mouse_dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for i, (x, y) in enumerate(letter_positions):
                if math.hypot(mouse_x - x, mouse_y - y) < 30 and letters[i] not in selected_letters:
                    selected_letters.append(letters[i])
                    break

        timer -= 1 / 60
        if len(guessed_words) == len(word_list):  # Stop if all words are guessed
            game_over = True
            running = False

        elif timer <= 0:
            game_over = True
            running = False

        pygame.display.flip()
        clock.tick(60)

    if game_over:
        show_coupon_screen()

# Run the game
if __name__ == "__main__":
    name_entry_window()
    game_loop()
