import pygame as pg
from sys import exit
import pickle
import os
from time import sleep


WIDTH = 1200
HEIGHT = 800
RECT_A = 50
BLOCK_A = 70
TOOL_A = 60
SPEED = 10
FPS = 60


class OpenMap:
    def __init__(self):
        if not os.path.isdir("levels"):
            os.mkdir("levels")
        files = os.listdir("levels")

        self.back = pg.Surface((500, 500))
        self.back.fill("white")
        screen.blit(self.back, ((WIDTH - 500) / 2, 180))
        self.texts = []

        y = 250
        interval = 35
        for file in files:
            font = pg.font.Font("fonts/RobotoCondensed-Light.ttf", 24)
            file_text = font.render(f"       {file}       ", True, "white", (80, 80, 80))
            text_rect = file_text.get_rect(center=(WIDTH / 2, y))
            screen.blit(file_text, text_rect)
            self.texts.append([text_rect, file])
            y += interval

    @staticmethod
    def open_file(file_name):
        try:
            with open(f"levels\\{file_name}", "rb") as file:
                data = pickle.load(file)
                return data
        except FileNotFoundError:
            print("Ошибка при чтении файла")

    def run(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()

                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse = pg.mouse.get_pos()
                    for rect in self.texts:
                        if rect[0].collidepoint(mouse):
                            return self.open_file(rect[1])

            pg.display.update()
            clock.tick(FPS)


class ToolsBar:
    def __init__(self):
        surf = pg.Surface((RECT_A, RECT_A))
        surf.fill((50, 50, 50))
        self.number_tool = 0
        self.tools = [
            [pg.image.load("images/grass.png").convert(), "grass"],
            [pg.image.load("images/stone.png").convert(), "stone"],
            [pg.image.load("images/water.png").convert(), "water"],
            [pg.image.load("images/sand.png").convert(), "sand"],
            [surf, None],
        ]
        self.count = len(self.tools)
        self.save_rect = self.open_rect = None

    def draw_texts(self):
        font = pg.font.Font("fonts/RobotoCondensed-Light.ttf", 24)
        save_text = font.render(" save ", True, "white", (80, 80, 80))
        self.save_rect = save_text.get_rect(topleft=(0, 0))
        open_text = font.render(" open ", True, "white", (80, 80, 80))
        self.open_rect = open_text.get_rect(topleft=self.save_rect.topright)
        screen.blit(save_text, self.save_rect)
        screen.blit(open_text, self.open_rect)

    def draw(self):
        blocks_length = BLOCK_A * self.count
        start_x = int(WIDTH / 2 - blocks_length / 2)
        end_x = int(WIDTH / 2 + blocks_length / 2) - 5

        i = 0
        for x in range(start_x, end_x, BLOCK_A):
            if i == self.number_tool:
                color = (150, 150, 150)
            else:
                color = (20, 20, 20)

            pg.draw.rect(screen, color, (x, 0, BLOCK_A, BLOCK_A))

            img = pg.transform.scale(self.tools[i][0], (TOOL_A, TOOL_A))
            screen.blit(img, (x + 5, 5))
            i += 1


class Creator:
    def __init__(self):
        self.background = pg.Surface((WIDTH * 3, HEIGHT * 3))
        self.background.fill((100, 100, 100))
        self.background_x = -WIDTH
        self.background_y = -HEIGHT
        self.rectangles = []
        self.map = []
        self.rectangles_init()
        self.tools_bar = ToolsBar()

    def save_map(self):
        if not os.path.isdir("levels"):
            os.mkdir("levels")

        for i in range(1, 100):
            if f"{i}.bin" not in os.listdir("levels"):
                try:
                    with open(f"levels\\{i}.bin", "wb") as file:
                        pickle.dump(self.map, file)
                        print("Сохранено", f"{i}.bin")
                        return
                except FileNotFoundError:
                    print("Ошибка при сохранении")

    def open_map(self):
        if len(os.listdir("levels")) != 0:
            open_map = OpenMap()
            self.map = open_map.run()
            self.draw_new_map()

    def draw_new_map(self):
        i = 0
        for fields in self.map:
            j = 0
            for field in fields:
                for tool in self.tools_bar.tools:
                    if tool[1] == field:
                        rect = pg.Rect(j * (RECT_A + 2), i * (RECT_A + 2), RECT_A, RECT_A)
                        self.rectangles.append(rect)
                        img = pg.transform.scale(tool[0], (RECT_A, RECT_A))
                        self.background.blit(img, rect)
                j += 1
            i += 1

    def rectangles_init(self):
        for y in range(0, HEIGHT * 3 - 10, RECT_A + 2):
            self.map.append([None for i in range(0, WIDTH * 3 - 10, RECT_A + 2)])

            for x in range(0, WIDTH * 3 - 10, RECT_A + 2):
                rect = pg.Rect(x, y, RECT_A, RECT_A)
                self.rectangles.append(rect)
                surf = pg.Surface((RECT_A, RECT_A))
                surf.fill((50, 50, 50))
                self.background.blit(surf, rect)

    def paint_rect(self, empty=False):
        mouse = pg.mouse.get_pos()
        mouse_x = mouse[0] - int(self.background_x)
        mouse_y = mouse[1] - int(self.background_y)
        for rect in self.rectangles:
            if rect.collidepoint((mouse_x, mouse_y)):
                if not empty:
                    img = self.tools_bar.tools[self.tools_bar.number_tool][0]
                    img = pg.transform.scale(img, (RECT_A, RECT_A))
                    name_img = self.tools_bar.tools[self.tools_bar.number_tool][1]
                else:
                    img = self.tools_bar.tools[-1][0]
                    name_img = None

                self.map[mouse_y // (RECT_A + 2)][mouse_x // (RECT_A + 2)] = name_img
                self.background.blit(img, (rect.left, rect.top))

    def main(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    self.tools_bar.number_tool = (self.tools_bar.number_tool - 1) % self.tools_bar.count
                elif event.key == pg.K_e:
                    self.tools_bar.number_tool = (self.tools_bar.number_tool + 1) % self.tools_bar.count

            if event.type == pg.MOUSEWHEEL:
                self.tools_bar.number_tool = (self.tools_bar.number_tool + event.y) % self.tools_bar.count

            if event.type == pg.MOUSEBUTTONDOWN:
                mouse = pg.mouse.get_pos()

                if self.tools_bar.save_rect.collidepoint(mouse):
                    self.save_map()
                    sleep(0.2)
                    return
                elif self.tools_bar.open_rect.collidepoint(mouse):
                    self.open_map()
                    sleep(0.2)
                    return

        keys = pg.key.get_pressed()

        # region
        if keys[pg.K_1]:
            self.tools_bar.number_tool = 0 % self.tools_bar.count
        elif keys[pg.K_2]:
            self.tools_bar.number_tool = 1 % self.tools_bar.count
        elif keys[pg.K_3]:
            self.tools_bar.number_tool = 2 % self.tools_bar.count
        elif keys[pg.K_4]:
            self.tools_bar.number_tool = 3 % self.tools_bar.count
        elif keys[pg.K_5]:
            self.tools_bar.number_tool = 4 % self.tools_bar.count
        elif keys[pg.K_6]:
            self.tools_bar.number_tool = 5 % self.tools_bar.count
        elif keys[pg.K_7]:
            self.tools_bar.number_tool = 6 % self.tools_bar.count
        elif keys[pg.K_8]:
            self.tools_bar.number_tool = 7 % self.tools_bar.count
        elif keys[pg.K_9]:
            self.tools_bar.number_tool = 8 % self.tools_bar.count
        elif keys[pg.K_0]:
            self.tools_bar.number_tool = 9 % self.tools_bar.count

        x = y = 0
        if keys[pg.K_w]:
            y = 1
        if keys[pg.K_s]:
            y = -1
        if keys[pg.K_d]:
            x = -1
        if keys[pg.K_a]:
            x = 1
        if x != 0 or y != 0:
            self.background_x += x / (x**2 + y**2)**0.5 * SPEED
            self.background_y += y / (x**2 + y**2)**0.5 * SPEED
        # endregion

        if pg.mouse.get_pressed()[0]:
            self.paint_rect()
        elif pg.mouse.get_pressed()[2]:
            self.paint_rect(empty=True)

        screen.blit(self.background, (self.background_x, self.background_y))
        self.tools_bar.draw()
        self.tools_bar.draw_texts()


def run():
    while True:
        window.main()

        pg.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("LEVEL CREATOR")
    icon = pg.image.load("images/tool.png")
    pg.display.set_icon(icon)
    clock = pg.time.Clock()
    window = Creator()
    run()
