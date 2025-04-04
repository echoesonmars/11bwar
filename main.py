import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("11b WAR")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

PLAYER_IMAGE = pygame.image.load("player_tank.png")
BOT_IMAGE_1 = pygame.image.load("bot_tank_1.png")
BOT_IMAGE_2 = pygame.image.load("bot_tank_2.png")
BOT_IMAGE_3 = pygame.image.load("bot_tank_3.png")

PLAYER_IMAGE = pygame.transform.scale(PLAYER_IMAGE, (50, 50))
BOT_IMAGE_1 = pygame.transform.scale(BOT_IMAGE_1, (50, 50))
BOT_IMAGE_2 = pygame.transform.scale(BOT_IMAGE_2, (50, 50))
BOT_IMAGE_3 = pygame.transform.scale(BOT_IMAGE_3, (50, 50))

font = pygame.font.Font(None, 36)

class Player:
    def __init__(self):
        self.image = PLAYER_IMAGE
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.speed = 5
        self.bullets = []
        self.alive = True

    def move(self, keys, joystick):
        if keys[pygame.K_w] or (joystick and joystick.get_axis(1) < -0.5):
            self.rect.y -= self.speed
        if keys[pygame.K_s] or (joystick and joystick.get_axis(1) > 0.5):
            self.rect.y += self.speed
        if keys[pygame.K_a] or (joystick and joystick.get_axis(0) < -0.5):
            self.rect.x -= self.speed
        if keys[pygame.K_d] or (joystick and joystick.get_axis(0) > 0.5):
            self.rect.x += self.speed

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top, -10)
        self.bullets.append(bullet)

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        for bullet in self.bullets:
            bullet.draw(surface)

class Enemy:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = random.randint(2, 4)
        self.bullets = []
        self.alive = True

    def move_towards_player(self, player):
        if self.rect.x < player.rect.x:
            self.rect.x += self.speed // 2
        elif self.rect.x > player.rect.x:
            self.rect.x -= self.speed // 2

        if self.rect.y < player.rect.y:
            self.rect.y += self.speed // 2
        elif self.rect.y > player.rect.y:
            self.rect.y -= self.speed // 2

    def shoot(self):
        if random.randint(1, 100) > 95:
            bullet = Bullet(self.rect.centerx, self.rect.bottom, 5)
            self.bullets.append(bullet)

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        for bullet in self.bullets:
            bullet.draw(surface)

class Bullet:
    def __init__(self, x, y, speed):
        self.rect = pygame.Rect(x, y, 5, 10)
        self.speed = speed

    def move(self):
        self.rect.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)

class Button:
    def __init__(self, text, x, y, width, height, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
        
def respawn_enemies(count):
    enemy_images = [BOT_IMAGE_1, BOT_IMAGE_2, BOT_IMAGE_3]
    return [Enemy(random.randint(0, WIDTH), random.randint(-HEIGHT, 0), random.choice(enemy_images)) for _ in range(count)]

def main():
    clock = pygame.time.Clock()
    running = True
    menu_active = True
    game_active = False

    player = Player()
    enemies = respawn_enemies(3)

    play_button = Button("Play", WIDTH // 2 - 75, HEIGHT // 2 - 50, 150, 50, GREEN, BLACK)
    retry_button = Button("Retry", WIDTH // 2 - 75, HEIGHT // 2 + 90, 150, 50, GREEN, RED)

    pygame.joystick.init()
    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    score = 0

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if menu_active and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if play_button.is_clicked(mouse_pos):
                    menu_active = False
                    game_active = True

            if game_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or (joystick and joystick.get_button(0)):
                    player.shoot()

        if menu_active:
            play_button.draw(screen)
            if not player.alive:
                retry_button.draw(screen)

        elif game_active:
            keys = pygame.key.get_pressed()
            player.move(keys, joystick)
            player.draw(screen)

            for enemy in enemies:
                if enemy.alive:
                    enemy.move_towards_player(player)
                    enemy.shoot()
                    enemy.draw(screen)

                    for bullet in enemy.bullets[:]:
                        bullet.move()
                        if bullet.rect.colliderect(player.rect):
                            player.alive = False
                            game_active = False
                            menu_active = True
                        elif bullet.rect.top > HEIGHT:
                            enemy.bullets.remove(bullet)

            for bullet in player.bullets[:]:
                bullet.move()
                for enemy in enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        enemy.alive = False
                        player.bullets.remove(bullet)
                        score += 1

            enemies = [enemy for enemy in enemies if enemy.alive]

            if not enemies:
                enemies = respawn_enemies(3)

            score_text = font.render(f"Score: {score}", True, BLACK)
            screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
