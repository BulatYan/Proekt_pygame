import pygame
from datetime import datetime
import sys
import os
import sqlite3


SIZE = width, height = 1000, 500
score = 0
start_time = 0
game_time = 180
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
balls = pygame.sprite.Group()
boms = pygame.sprite.Group()
start_border = pygame.sprite.Group()
finish_border = pygame.sprite.Group()
level_group = pygame.sprite.Group()
help_show = True
stat_show = False
state = False
level = 1
max_level = 1
stat_text = []
count = 0


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def help_screen(screen):
    #Создание инструкции
    intro_text = ["ИНСТРУКЦИЯ", "",
                  "Правила игры:",
                  "Сделайте левый клик и не отпуская клавишу потяните мышь и отпустите.",
                  "Это сгенерирует шар, который полетит вдоль нарисованной линии.",
                  "Шарик должен отскочить от зеленой правой боковой стенки и долететь до красной левой.",
                  "За каждый шар, который долетит до левой красной боковой стенки",
                  "пользователь получит 1 балл.",
                  "Пользователю необходимо, как можно больше шаров довести до цели за указанное время.",
                  "Для перехода на второй уровень нужно три раза набрать 20 и более очков.",
                  "Шары самоликвидируются при взаимном столкновении."]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height - 31))
    screen.blit(fon, (0, 31))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)


def stat_screen(screen):
    # создание статистики
    global stat_text, level, max_level
    score_1 = 0
    date_1 = ''
    score_2 = 0
    date_2 = ''
    con = sqlite3.connect('data/db.db')
    cur = con.cursor()
    result_l1 = cur.execute("""SELECT MAX(Score), Date FROM
            (SELECT Date, Score, Level FROM Log
             WHERE Level = 1)""")
    for row in result_l1:
        score_1 = row[0]
        date_1 = row[1][:19].replace('-', '.')
    result_l2 = cur.execute("""SELECT MAX(Score), Date FROM
                (SELECT Date, Score, Level FROM Log
                 WHERE Level = 2)""")
    for row in result_l2:
        score_2 = row[0]
        date_2 = row[1][:19].replace('-', '.')
    # Проверка уровня игрока
    if level == 1:
        result = cur.execute("""SELECT Score FROM Log
            WHERE Level = 1 and Score >= 20""").fetchall()
        if len(list(result)) >= 3:
            max_level = 2
            que = f"UPDATE Level SET Current = {max_level}"
            cur.execute(que)
    con.commit()
    con.close()
    stat_text = ["СТАТИСТИКА", "",
                 f"Вы набрали {score} очков", "",
                 "Ваш максимальный результат на первом уровне ",
                 f"составляет {score_1} очков на {date_1}", "",
                 "Ваш максимальный результат на втором уровне ",
                 f"составляет {score_2} очков на {date_2}", "",
                 f"Ваш текущий уровень: {level}"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height - 31))
    screen.blit(fon, (0, 31))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in stat_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)


class StartBut:
    def __init__(self):
        #Инициализация стартовой кнопки
        self.width = 120
        self.height = 28
        self.x = 11
        self.y = 1

    def render(self, screen):
        #Создание текста
        font = pygame.font.Font(None, 25)
        text = font.render("Начать", True, (255, 255, 255))
        pygame.draw.rect(screen, 'green', (self.x, self.y, self.width, self.height), 0)
        screen.blit(text, (self.x + (self.width - text.get_width()) // 2,
                           self.y + (self.height - text.get_height()) // 2))

    def check_click(self, pos):
        # Обрабатованние клика
        global start_time, state, score, help_show, stat_show

        if self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height:
            for ball in balls:
                ball.kill()
            start_time = datetime.now()
            state = True
            help_show = False
            stat_show = False
            score = 0


class HelpBut:
    def __init__(self):
        #Инициализация кнопки
        self.width = 100
        self.height = 28
        self.x = 691
        self.y = 1

    def render(self, screen):
        #Создание текста
        font = pygame.font.Font(None, 25)
        text = font.render("Справка", True, (255, 255, 255))
        pygame.draw.rect(screen, 'green', (self.x, self.y, self.width, self.height), 0)
        screen.blit(text, (self.x + (self.width - text.get_width()) // 2,
                           self.y + (self.height - text.get_height()) // 2))

    def check_click(self, pos):
        #Обрабатование клика
        global help_show, state, stat_show

        if self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height:
            if help_show:
                help_show = False
                state = True
            else:
                help_show = True
                state = False
                stat_show = False


class StatisBut:
    def __init__(self):
        #Инициализация кнопки
        self.width = 115
        self.height = 28
        self.x = 819
        self.y = 1

    def render(self, screen):
        #Размещение текста
        font = pygame.font.Font(None, 25)
        text = font.render("Статистика", True, (255, 255, 255))
        pygame.draw.rect(screen, 'green', (self.x, self.y, self.width, self.height), 0)
        screen.blit(text, (self.x + (self.width - text.get_width()) // 2,
                           self.y + (self.height - text.get_height()) // 2))

    def check_click(self, pos):
        #Обрабатывается клик
        global stat_show, help_show, state

        if self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height:
            if stat_show:
                stat_show = False
                state = True
            else:
                stat_show = True
                help_show = False
                state = False


class TimeShow:
    def __init__(self):
        #Инициализация текста
        self.width = 135
        self.height = 28
        self.x = 148
        self.y = 1

    def render(self, screen, delta):
        #Размещение кнопки
        font = pygame.font.Font(None, 25)
        name = f"Осталось: {game_time - int(delta)}"
        text = font.render(name, True, 'blue')
        pygame.draw.rect(screen, 'white', (self.x, self.y, self.width, self.height), 0)
        screen.blit(text, (self.x + 10, self.y + (self.height - text.get_height()) // 2))


class ScoreShow:
    def __init__(self):
        #Инициализация score
        self.width = 135
        self.height = 28
        self.x = 294
        self.y = 1

    def render(self, screen):
        # Создание текста
        font = pygame.font.Font(None, 25)
        name = f"Всего очков: {score}"
        text = font.render(name, True, 'red')
        pygame.draw.rect(screen, 'white', (self.x, self.y, self.width, self.height), 0)
        screen.blit(text, (self.x + 10, self.y + (self.height - text.get_height()) // 2))


class LevelText:
    def __init__(self):
        #Инициализация текста
        self.width = 95
        self.height = 28
        self.x = 457
        self.y = 1

    def render(self, screen):
        #Создание текста
        font = pygame.font.Font(None, 25)
        text = font.render("Уровни:", True, (0, 0, 0))
        pygame.draw.rect(screen, 'white', (self.x, self.y, self.width, self.height), 1)
        screen.blit(text, (self.x + 10, self.y + (self.height - text.get_height()) // 2))


class LevelBut:
    def __init__(self, name, x, y, color='green'):
        # Инициализация кнопок
        self.name = name
        self.width = 30
        self.height = 28
        self.color = color
        self.x = x
        self.y = y

    def render(self, screen):
        # Рисавание кнопок
        font = pygame.font.Font(None, 25)
        text = font.render(self.name, True, (255, 255, 255))
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 0)
        screen.blit(text, (self.x + 10, self.y + (self.height - text.get_height()) // 2))

    def check_click(self, pos):

        global level, state, help_show, stat_show, max_level
        # Смена уровня в зависимости от доступных уровней для игрока
        # Менять уровень запрещаем во время игры
        if self.x <= pos[0] <= self.x + self.width and 1 <= pos[1] <= 1 + self.height and start_time == 0:
            dez_level = int(self.name)
            if max_level >= dez_level:
                level = dez_level
                help_show = False
                stat_show = False
                state = True
                # Устанавливаем преграды в зависимости от уровня игрока
                if level == 1:
                    for el in level_group:
                        el.kill()
                    border1 = Border(width // 3, 37, 10, height // 2, 'orange', vertical_borders)
                    border2 = Border(width // 2, height // 2 - 8, 10, height // 2, 'orange', vertical_borders)
                    level_group.add(border1)
                    level_group.add(border2)
                if level == 2:
                    for el in level_group:
                        el.kill()
                    border1 = Border(width // 3 - 50, 37, 10, height // 2, 'orange', vertical_borders)
                    border2 = Border(width // 2 - 100, height // 2 - 8, 10, height // 2, 'orange', vertical_borders)
                    border3 = Border(width // 3 + 200, 37, 10, height // 2, 'orange', vertical_borders)
                    level_group.add(border1)
                    level_group.add(border2)
                    level_group.add(border3)


class Bom(pygame.sprite.Sprite):
    # Спрайт имитирующий достижение цели

    image = load_image("boom.png")

    def __init__(self, x, y):
        super().__init__(boms)
        self.count = 15
        self.image = Bom.image
        self.rect = pygame.Rect(x, y, 20, 20)

    def update(self):
        self.count -= 1
        if self.count <= 0:
            self.kill()


class Ball(pygame.sprite.Sprite):
    # Отрисовка шарика
    def __init__(self, radius, x, y, vx, vy):
        super().__init__(balls)
        self.radius = radius
        self.active = False
        self.image = pygame.Surface((2 * radius, 2 * radius),
                                    pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("red"),
                           (radius, radius), radius)
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
        if vx >= 50:
            vy = vy * 50 // vx
            vx = 50
        self.vx = vx
        self.vy = vy

    def update(self):
        # Обратываем двежение шарика
        global score, state

        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx
        if pygame.sprite.spritecollideany(self, start_border):
            self.active = True
        if pygame.sprite.spritecollideany(self, finish_border) and self.active and state:
            if start_time != 0:
                score += 1
            Bom(self.rect.x, self.rect.y)
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
    # Указатель напрвления движения шара
    pygame.draw.line(screen, 'black', (x, y), (x1, y1))


def main():

    global state, help_show, stat_show, count, level, max_level, start_time

    pygame.init()
    pygame.display.set_caption('Рикошет')
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()
    fps = 100
    # Читаем уровень игрока 
    con = sqlite3.connect('data/db.db')
    cur = con.cursor()
    result = cur.execute("""SELECT Current FROM Level""")
    for i in list(result):
        level = i[0]
        max_level = level
    con.close()

    statistic_but = StatisBut()
    start_but = StartBut()
    help_but = HelpBut()
    time_show = TimeShow()
    score_show = ScoreShow()
    level_text = LevelText()
    begin_pos = (0, 0)
    end_pos = (0, 0)
    delta_time = 0
    show_line = False
    running = True

    #  Устанавливаем ограничения, преграды
    Border(1, 31, width - 2, 5, 'black', horizontal_borders)
    Border(1, height - 6, width - 2, 5, 'black', horizontal_borders)
    Border(1, 37, 5, height - 44, 'red', vertical_borders)
    Border(width - 6, 37, 5, height - 44, 'green', vertical_borders)
    Border(width - 6, 7, 5, height - 14, 'green', start_border)
    Border(1, 7, 5, height - 14, 'red', finish_border)
    border1 = Border(width // 3, 37, 10, height // 2, 'orange', vertical_borders)
    border2 = Border(width // 2, height // 2 - 8, 10, height // 2, 'orange', vertical_borders)
    level_group.add(border1)
    level_group.add(border2)
    if max_level == 1:
        level_but1 = LevelBut('1', 555, 1)
        level_but2 = LevelBut('2', 608, 1, color='grey')
    else:
        level_but1 = LevelBut('1', 555, 1)
        level_but2 = LevelBut('2', 608, 1)

    while running:
        screen.fill((255, 255, 255))
        score_show.render(screen)
        help_but.render(screen)
        level_but1.render(screen)
        if max_level == 2:
            level_but2 = LevelBut('2', 608, 1)
        level_but2.render(screen)
        time_show.render(screen, delta_time)
        level_text.render(screen)
        statistic_but.render(screen)
        cur_time = datetime.now()
        if start_time != 0 and state:
            delta_time = (cur_time - start_time).total_seconds()
            if delta_time > game_time:
                con = sqlite3.connect('data/db.db')
                cur = con.cursor()
                cur.execute("INSERT INTO Log(Date, Level, Score)\
                VALUES(?, ?, ?)", [start_time, level, score])
                con.commit()
                con.close()
                state = False
                start_time = 0
                for ball in balls:
                    ball.kill()
                stat_show = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                start_but.check_click(event.pos)
                level_but1.check_click(event.pos)
                level_but2.check_click(event.pos)
                help_but.check_click(event.pos)
                statistic_but.check_click(event.pos)
                if event.button == 1:
                    begin_pos = event.pos
                    end_pos = begin_pos
                    show_line = True
            elif event.type == pygame.MOUSEMOTION and show_line:
                end_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                show_line = False
                if event.button == 1:
                    vx = (begin_pos[0] - end_pos[0]) // 20
                    vy = (begin_pos[1] - end_pos[1]) // 20
                    if height - 16 > end_pos[1] > 41 or height - 16 > vy > 41:
                        ball = Ball(10, *end_pos, vx, vy)
                        balls.add(ball)
        if show_line:
            draw_line(*begin_pos, *end_pos, screen)
        balls.update()
        start_but.render(screen)
        if help_show:
            help_screen(screen)
        elif stat_show:
            stat_screen(screen)
        elif state:
            balls.draw(screen)
            boms.draw(screen)
            boms.update()
            horizontal_borders.draw(screen)
            vertical_borders.draw(screen)
            level_group.draw(screen)
        pygame.display.flip()
        clock.tick(fps)


if __name__ == '__main__':
    main()
