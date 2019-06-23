# -*- coding: utf-8 -*-
import pygame, sys, time, os
import numpy as np

# 定义每行，每列各有多少cell
WIDTH = 200
HEIGHT = 120

# 初始化记录按钮状态的变量
pygame.button_down = False

# 矩阵定义
pygame.world=np.zeros((HEIGHT,WIDTH))

# 创建“cell”类
class Cell(pygame.sprite.Sprite):

    #每个“cell”的大小
    size = 6

    def __init__(self, position):

        pygame.sprite.Sprite.__init__(self)
        #定义大小时减去0.1，造成差值，可以显示如表格一样的网格线
        self.image = pygame.Surface([self.size, self.size])

        # 填充为白色
        self.image.fill((255,255,255))

        # 创建一个以左上角为原点的矩阵
        self.rect = self.image.get_rect()
        self.rect.topleft = position        #左上角的位置

# 绘图函数
def draw():
    screen.fill((0,0,0))        #填充为黑色
    for sp_col in range(pygame.world.shape[1]):         #每列
        for sp_row in range(pygame.world.shape[0]):     #每行
            if pygame.world[sp_row][sp_col]:
                new_cell = Cell((sp_col * Cell.size,sp_row * Cell.size))    #由第几行第几列推算出每个cell左上角的位置
                screen.blit(new_cell.image,new_cell.rect)

# Update the map according to cell update rules
def next_generation():
    #借用roll函数，通过滚动矩阵，使目标cell周围的八个位置，分别滚动到自己位置一次
    #将每个滚动到目标cell位置上的新cell的值累加，即该cell的四周所存在的cell数
    '''
        i = -1 时表示中心点位下面一行的三个相邻点位；
        i = 0  时表示中心点位左右两边的两个相邻点位；
        i = 1  时表示中心点位上面一行的三个相邻点位；
    '''
    nbrs_count = sum(np.roll(np.roll(pygame.world, i, 0), j, 1) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i != 0 or j != 0))
    
    #满足上文中2，4条件时，记录为“1”
    pygame.world = (nbrs_count == 3) | ((pygame.world == 1) & (nbrs_count == 2)).astype('int')

#初始化地图
def init():
    pygame.world.fill(0)
    draw()
    return 'Stop'

#停止时的相关操作
def stop():
    for event in pygame.event.get():
        #关闭窗体，退出程序
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        #回车键，开始演化
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return 'Move'

        #“R”键，重置地图
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            return 'Reset'

        #记录鼠标操作，赋给另一个变量，便于之后做if判断
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.button_down = True
            pygame.button_type = event.button

        if event.type == pygame.MOUSEBUTTONUP:
            pygame.button_down = False

        #有鼠标操作时，获取光标的坐标
        if pygame.button_down:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            sp_col = int(mouse_x / Cell.size);
            sp_row = int(mouse_y / Cell.size);

            if pygame.button_type == 1:         #鼠标左键
                pygame.world[sp_row][sp_col] = 1
            elif pygame.button_type == 3:       #鼠标右键
                pygame.world[sp_row][sp_col] = 0
            draw()

    return 'Stop'

#计时器
pygame.clock_start = 0

#程序运行时（演化过程中）的操作
def move():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        #空格键，停止演化
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            return 'Stop'
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            return 'Reset'
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.button_down = True
            pygame.button_type = event.button

        if event.type == pygame.MOUSEBUTTONUP:
            pygame.button_down = False

        #此处不可以在'Move'状态下执行下述操作，会报错，只能先返回'Stop'状态
        if pygame.button_down:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            sp_col = mouse_x / Cell.size;
            sp_row = mouse_y / Cell.size;

            if pygame.button_type == 1:
                pygame.world[sp_row][sp_col] = 1
            elif pygame.button_type == 3:
                pygame.world[sp_row][sp_col] = 0
            draw()

    #每一代演化的频率控制，此处为0.02
    if time.clock() - pygame.clock_start > 0.02:
        next_generation()
        draw()
        pygame.clock_start = time.clock()

    return 'Move'

if __name__ == '__main__':
    # init, stop, move 三种状态的字典
    state_actions = {
            'Reset': init,
            'Stop': stop,
            'Move': move
        }

    state = 'Reset'
    pygame.init()

    pygame.display.set_caption('Conway\'s Game of Life')
    #定义窗体初始位置
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50, 70)
    screen = pygame.display.set_mode((WIDTH * Cell.size, HEIGHT * Cell.size))

    while True:
        #主循环
        state = state_actions[state]()
        pygame.display.update()