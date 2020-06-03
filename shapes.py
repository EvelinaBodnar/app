
# / -------------------------------------------------------------------------- \

import random
from copy import copy

import pygame as pg

from config import config
from color import colors, ColorEffect

# / -------------------------------------------------------------------------- \

# Форми та обертання
T = [['000',
      '.0.'],

     ['.0',
      '00',
      '.0'],

     ['.0.',
      '000',],

     ['0.',
      '00',
      '0.']]



S1 = [['.00',
       '00.',],

      ['0.',
       '00',
       '.0']]


S2 = [['00.',
       '.00'],

      ['.0',
       '00',
       '0.']]



L1 = [['0.',
       '0.',
       '00'],
      
     ['000',
      '0..',],
      
     ['00',
      '.0',
      '.0'],
      
     ['..0',
      '000',]]
      

L2 = [['.0',
       '.0',
       '00'],

     ['0..',
      '000'],
      
     ['00',
      '0.',
      '0.'],

     ['000',
      '..0']]


I = [['.0.',
      '.0.',
      '.0.',
      '.0.'],

     ['....',
      '0000',
      '....']]




dict_shapes = {'T' :   T,
               'S1' :  S1,
               'S2' :  S2, 
               'L1' :  L1,
               'L2' :  L2,
               'I' :   I}


shape_colors = {'T' :   colors['pink'],
                'S1' :  colors['purple'],
                'S2' :  colors['purple'],
                'L1' :  colors['cherry'],
                'L2' :  colors['cherry'],
                'I' :   colors['blue'],
}
                
# Вага для випадкового вибору
weights = {'T' :   0.95,
           'S1' :  0.95,
           'S2' :  0.95,
           'L1' :  0.95,
           'L2' :  0.95,
           'I' :   0.95}

class Shapes:
    
    # / ----------------------------------------------------------------------- \

    def __init__(self):

        #блоки, які випали
        self.dropped = []
        self.dropped_index = []
        self.dropped_colors = []

        # Стерті блоки
        self.eresed = []
        self.eresed_colors = []

        self.dict_shapes = dict_shapes
        self.weights = weights
        
    # / ----------------------------------------------------------------------- \

    def restart(self):

        self.dropped = []
        self.dropped_index = []
        self.dropped_colors = []
        
        self.eresed = []
        self.eresed_colors = []



        self.dict_shapes = dict_shapes
        self.weights = weights
        
    # / ----------------------------------------------------------------------- \
                
    def next_shape(self, shape=None):
        
        self.pressed_x_speed = config.block_size
        self.pressed_y_speed = 0
        
        if shape is None:
            self.shape_key = random.choices(list(self.dict_shapes.keys()), 
                                            weights=list(self.weights.values()))[0]
            self.n_positions = len(self.dict_shapes[self.shape_key])
            self.position = random.randint(0, self.n_positions-1)

        else:
            # Копіювання ключа форми та положення з екземпляра вхідної форми
            self.shape_key = copy(shape.shape_key)
            self.n_positions = copy(shape.n_positions)
            self.position = copy(shape.position)

        # Початкове (x, y) положення
        self.x =  config.game_boundaries[0] +  (config.ncols // 2  - 1) * config.block_size
        self.y = -(len(self.dict_shapes[self.shape_key][self.position]) * config.block_size)

        # Колір
        self.shape_color = ColorEffect(shape_colors[self.shape_key], interval=45, length=10)

        self.get_shape()        
        self.move = True
        
    # / ----------------------------------------------------------------------- \
                
    def get_shape(self):
  
        # self.shape - це список pg.Rect
        self.shape = []
        
        for i, row in enumerate(self.dict_shapes[self.shape_key][self.position]):
            for j, column in enumerate(row):
                if column == '0':
                    x = self.x + config.block_size * j
                    y = self.y + config.block_size * i
                    rect = pg.Rect(x, y, config.block_size, config.block_size)
                    self.shape.append(rect)

        self.shape_corners = self.get_shape_corners()
        self.center = self.get_shape_center()
        
    # / ----------------------------------------------------------------------- \

    def get_shape_corners(self):
        xs = [rect[0] for rect in self.shape]
        ys = [rect[1] for rect in self.shape]
        xmin = min(xs)
        ymin = min(ys)
        xmax = max(xs) + config.block_size
        ymax = max(ys) + config.block_size
        self.shape_corners = [xmin, ymin, xmax, ymax]
        return self.shape_corners        
        
    # / ----------------------------------------------------------------------- \

    def get_shape_center(self):
        cx = self.shape_corners[0] + (self.shape_corners[2] - self.shape_corners[0]) / 2
        cy = self.shape_corners[1] + (self.shape_corners[3] - self.shape_corners[1]) / 2
        self.center = [cx, cy]
        return self.center
        
    # / ----------------------------------------------------------------------- \

    def get_index(self, x, y):
        # Отримання індекса рядків і стовпців, коли форма не може рухатися вниз "
        row = int((y - config.game_boundaries[1]) / config.block_size)
        col = int((x - config.game_boundaries[0]) / config.block_size)
        return row, col    
        
    # / ----------------------------------------------------------------------- \

    def difference(self, bound, current_shape_bound, direction='bottom'):
        
        diff = 0
        if direction == 'left':
            if current_shape_bound < bound:
                diff = bound - current_shape_bound

        elif direction == 'right':
            if current_shape_bound > bound:
                diff = bound - current_shape_bound

        elif direction == 'bottom':
            if current_shape_bound > bound:
                diff = bound - current_shape_bound

        return diff        
        
    # / ----------------------------------------------------------------------- \

    def move_down(self, pressed_y=None):
        
        self.move = True
        
        if pressed_y is not None:
            if pressed_y:
                self.pressed_y_speed = 10
            else:
                self.pressed_y_speed = 0
         
        y_move = config.speed + self.pressed_y_speed        
        self.move_shape(0, y_move)

        # Перевірка на заповненість
        if self.dropped:
            for rect1 in self.dropped:
                for rect2 in self.shape:
                    if rect1.colliderect(rect2):
                        diff = self.difference(rect1.top, rect2.bottom, 'bottom')
                        self.move_shape(0, diff)
                        self.move = False
                        return self.move

        # Перевірка, чи форма є поза нижньою межею
        diff = self.difference(config.game_boundaries[3], self.shape_corners[3], 'bottom')
        if diff != 0:
            self.move_shape(0, diff)
            self.move = False
            return self.move

        return self.move
        
    # / ----------------------------------------------------------------------- \
        
    def move_left(self):
        
        self.move_shape(-self.pressed_x_speed, 0)
        
        # Перевірка, чи форма є поза лівою межею
        diff = self.difference(config.game_boundaries[0], self.shape_corners[0], 'left')        
        if diff != 0:
            self.move_shape(diff, 0)

        # Перевірка на заповненість
        if self.dropped:
            for rect1 in self.dropped:
                for rect2 in self.shape:
                    if rect1.colliderect(rect2):
                        diff = self.difference(rect1.right, rect2.left,  'left')
                        self.move_shape(diff, 0)
                        return None
                        
    # / ----------------------------------------------------------------------- \

    def move_right(self):
        
        # Перевірка, чи форма є поза правою межею
        self.move_shape(self.pressed_x_speed, 0)        
        diff = self.difference(config.game_boundaries[2], self.shape_corners[2], 'right')
        if diff != 0:
            self.move_shape(diff, 0)
            
        # Перевірка на заповненість
        if self.dropped:
            for rect1 in self.dropped:
                for rect2 in self.shape:
                    if rect1.colliderect(rect2):
                        diff = self.difference(rect1.left, rect2.right, 'right')
                        self.move_shape(diff, 0)                        
                        return None
                        
    # / ----------------------------------------------------------------------- \

    def move_shape(self, x, y):
        self.x += x
        self.y += y
        self.shape = [rect.move(x, y) for rect in self.shape]
        self.shape_corners = self.get_shape_corners()
        self.center = self.get_shape_center()
        
    # / ----------------------------------------------------------------------- \

    def rotate(self):
        
        # Змінення позиції
        self.position += 1
        if self.position >= self.n_positions:
            self.position = 0
        
        # Оновлення фігури до нової позиції
        self.get_shape()

        # Перевірка, чи обернена форма є поза= межею
        diff_left = self.difference(config.game_boundaries[0],  self.shape_corners[0], 'left')
        if diff_left != 0:
            self.move_shape(diff_left, 0)
        
        diff_right = self.difference(config.game_boundaries[2], self.shape_corners[2], 'right')
        if diff_right != 0:
            self.move_shape(diff_right, 0)

        # Перевірка чи обернена фігура ні з чим не перетинається
        if self.dropped:
            if any(rect1.colliderect(rect2) for rect1 in self.shape for rect2 in self.dropped):
                self.position -= 1
                if self.position < 0:
                    self.position = self.n_positions - 1

                self.get_shape()

                if diff_left != 0:
                    self.move_shape(-diff_left, 0)

                if diff_right != 0:
                    self.move_shape(-diff_right, 0)
                    
    # / ----------------------------------------------------------------------- \
              
    def update_filled_spaces(self):
        # Додавання поточної форми до викинутих фігур
        for rect in self.shape:
            row, col = self.get_index(rect.left, rect.top)
            self.dropped.append(rect)
            self.dropped_index.append([row, col])
            self.dropped_colors.append(self.shape_color)

    # / ----------------------------------------------------------------------- \

    def erese_blocks(self):

        n_eresed = 0

        # Видалення блоків, коли рядок заповнений
        if self.dropped:
            
            # Отримання ід заповнених рядків
            indexes_removed = []
            removed_rows = []
            for row in range(config.nrows)[::-1]:
                cols_filled = [i for i, idx in enumerate(self.dropped_index) if idx[0] == row]
                if len(cols_filled) == config.ncols:                    
                    removed_rows.append(row)
                    indexes_removed.extend(cols_filled)
            
            if removed_rows:
                
                # Отримання блоків, які найбільше видаляються
                self.eresed = [self.dropped[i] for i in indexes_removed]
                self.eresed_colors = [self.dropped_colors[i] for i in indexes_removed]
                
                # Видалення блоків
                indexes = [i for i in range(len(self.dropped_index)) if i not in indexes_removed]
                self.dropped = [self.dropped[i] for i in indexes]
                self.dropped_index = [self.dropped_index[i] for i in indexes]
                self.dropped_colors = [self.dropped_colors[i] for i in indexes]

                # Перегляд, які блоки потрібно рухати вниз
                to_update = []
                for i, row in enumerate(removed_rows):
                    for j, rect in enumerate(self.dropped):
                        if self.dropped_index[j][0] < row:
                            to_update.append(j)

                # Рух блоків вниз
                for index in to_update:
                    self.dropped[index] = self.dropped[index].move(0, config.block_size)
                    self.dropped_index[index][0] += 1

                n_eresed = len(self.eresed)
                            




        return n_eresed
        
    # / ----------------------------------------------------------------------- \

    def draw_eresed(self, screen):
        for i, rect, in enumerate(self.eresed):
            color = self.eresed_colors[i].change_color()
            color = self.eresed_colors[i].modify_color(color, l=-20)
            pg.draw.rect(screen, color, rect)
            pg.draw.rect(screen, colors['white'], rect, 1)
            
        self.eresed = []
        self.eresed_colors = []
            
        pg.display.update()
        pg.time.wait(350)

    # / ----------------------------------------------------------------------- \        

    def draw_shape(self, screen):
        color = self.shape_color.change_color()
        for rect in self.shape:
            if rect.bottom > config.game_boundaries[1]:
                pg.draw.rect(screen, color, rect)
                pg.draw.rect(screen, colors['white'], rect, 1)

    # / ----------------------------------------------------------------------- \

    def draw_filled(self, screen):
        if self.dropped:
            for i, rect in enumerate(self.dropped):
                color = self.dropped_colors[i].change_color()
                pg.draw.rect(screen, color, rect)
                pg.draw.rect(screen, colors['white'], rect, 1)

    # / ----------------------------------------------------------------------- \
    
    def draw_next_shape(self, x, y, screen):
        
        dx = x - self.center[0]
        dy = y - self.center[1]
        self.move_shape(dx, dy)

        color = self.shape_color.change_color()
        for rect in self.shape:
            pg.draw.rect(screen, color, rect)
            pg.draw.rect(screen, colors['white'], rect, 1)               
    
    # / ----------------------------------------------------------------------- \         
   
 # / -------------------------------------------------------------------------- \
 # / --------------------------------------------------- \
 # / -------------------------------- \
 # / ------------- \
 # /Кінець
