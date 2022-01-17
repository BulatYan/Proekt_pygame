import pygame
from datetime import datetime, timedelta


SIZE = width, height = 1000, 500
score = 0
start_time = 0
game_time = 180
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
balls = pygame.sprite.Group()
start_border = pygame.sprite.Group()
finish_border = pygame.sprite.Group()
state = False

class StartBut:
    def __init__(self):
        self.width = 120
        self.height = 28
        self.x = 11
        self.y = 1

    def render(self, screen):
        font = pygame.font.Font(None, 25)
        text = font.render("Начать", 1, (255, 255, 255))
        pygame.draw.rect(screen, 'green', (self.x, self.y, self.width, self.height), 0)
        screen.blit(text, (self.x + (self.width - text.get_width()) // 2,
                           self.y + (self.height - text.get_height()) //2))

    def check_click(self, pos):
        global start_time, state
        if self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height:
            for i in balls:
                i.kill()
            start_time = datetime.now()
            state = True


class TimeShow:
    def __init__(self):
        self.width = 135
        self.height = 28
        self.x = 148
        self.y = 1

    def render(self, screen, delta):
        font = pygame.font.Font(None, 25)
        name = f"Осталось: {game_time - int(delta)}"
        text = font.render(name, 1, (255, 255, 255))
        pygame.draw.rect(screen, 'green', (self.x, self.y, self.width, self.height), 0)
        screen.blit(text, (self.x + 10, self.y + (self.height - text.get_height()) // 2))


class ScoreShow:
    def __init__(self):
        self.width = 135
        self.height = 28
        self.x = 294
        self.y = 1

    def render(self, screen, delta):
        font = pygame.font.Font(None, 25)
        name = f"Всего: {score}"
        text = font.render(name, 1, (255, 255, 255))
        pygame.draw.rect(screen, 'green', (self.x, self.y, self.width, self.height), 0)
        screen.blit(text, (self.x + 10, self.y + (self.height - text.get_height()) // 2))


class Ball(pygame.sprite.Sprite):
    def __init__(self, radius, x, y, vx, vy):
        super().__init__(balls)
        self.radius = radius
        self.active = False
        self.image = pygame.Surface((2 * radius, 2 * radius),
                                    pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("red"),
                           (radius, radius), radius)
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
        self.vx = vx
        self.vy = vy

    def update(self):
        global score, state
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx
        if pygame.sprite.spritecollideany(self, start_border):
            self.active = True
        if pygame.sprite.spritecollideany(self, finish_border) and self.active and state:
            score += 1
            self.kill()
        if len(pygame.sprite.spritecollide(self, balls, False)) >= 2:
            pygame.sprite.spritecollide(self, balls, True)


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, xw, yh, color='black', group=all_sprites):
        super().__init__(group)
        self.add(group)
        self.image = pygame.Surface([xw, yh])
        self.image.fill(color)
        self.rect = pygame.Rect(x1, y1, xw, yh)


def draw_line(x, y, x1, y1, screen):
    pygame.draw.line(screen, 'black', (x, y), (x1, y1))


def main():
    pygame.init()
    pygame.display.set_caption('Balls')
    screen = pygame.display.set_mode(SIZE)
    start_but = StartBut()
    running = True
    clock = pygame.time.Clock()
    fps = 100
    begin_pos = (0, 0)
    Border(1, 31, width - 2, 5, 'black', horizontal_borders)
    Border(1, height - 6, width - 2, 5, 'black', horizontal_borders)
    Border(1, 37, 5, height - 44, 'red', vertical_borders)
    Border(width - 6, 37, 5, height - 44, 'green', vertical_borders)
    Border(width - 6, 7, 5, height - 14, 'green', start_border)
    Border(1, 7, 5, height - 14, 'red', finish_border)
    Border(width // 3, 37, 5, height // 2, 'orange', vertical_borders)
    Border(width // 2, height // 2 - 8, 5, height // 2, 'orange', vertical_borders)

    vx = 0
    vy = 0
    # today = datetime.now().time()
    delta_time = 0
    end_pos = (0, 0)
    new_pos = (0, 0)
    draw = False
    time_show = TimeShow()
    score_show = ScoreShow()
    while running:
        screen.fill((255, 255, 255))
        score_show.render(screen, score)
        time_show.render(screen, delta_time)
        cur_time = datetime.now()
        if start_time != 0:
            delta_time = (cur_time - start_time).total_seconds()
            if delta_time > game_time:
                running = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                start_but.check_click(event.pos)
                if event.button == 1:
                    begin_pos = event.pos
                    end_pos = begin_pos
                    draw = True
            elif event.type == pygame.MOUSEMOTION and draw:
                end_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                draw = False
                if event.button == 1:
                    vx = (begin_pos[0] - end_pos[0]) // 20
                    vy = (begin_pos[1] - end_pos[1]) // 20
                    ball = Ball(10, *end_pos, vx, vy)
                    balls.add(ball)
        if draw:
            draw_line(*begin_pos, *end_pos, screen)
        balls.update()

        balls.draw(screen)
        start_but.render(screen)
        horizontal_borders.draw(screen)
        vertical_borders.draw(screen)
        pygame.display.flip()
        clock.tick(fps)
    # pygame.display.quit()

if __name__ == '__main__':
    main()
