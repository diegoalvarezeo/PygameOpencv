import pygame
import random
import cv2
import numpy as np
import threading 
import time




pygame.font.init()

# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 30 height per block
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height



""" redBajo1 = np.array([0,100,20],np.uint8)
redAlto1 = np.array([5,255,255],np.uint8)

redBajo2 = np.array([175,100,20],np.uint8)
redAlto2 = np.array([179,255,255],np.uint8) """
azulBajo = np.array([100,100,20],np.uint8)
azulAlto = np.array([125,255,255],np.uint8)
amarilloBajo = np.array([15,100,20],np.uint8)
amarilloAlto = np.array([45,255,255],np.uint8)
redBajo1 = np.array([0,100,20],np.uint8)
redAlto1 = np.array([5,255,255],np.uint8)
redBajo2 = np.array([175,100,20],np.uint8)
redAlto2 = np.array([179,255,255],np.uint8)
font = cv2.FONT_HERSHEY_SIMPLEX




# SHAPE FORMATS

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
# index 0 - 6 represent shape


class Piece(object):  # *
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


def create_grid(locked_pos={}):  # *
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j,i)]
                grid[i][j] = c
    return grid


def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False


def get_shape():
    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width /2 - (label.get_width()/2), top_left_y + play_height/2 - label.get_height()/2))


def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (128,128,128), (sx, sy + i*block_size), (sx+play_width, sy+ i*block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j*block_size, sy),(sx + j*block_size, sy + play_height))


def clear_rows(grid, locked):

    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0,0,0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j,i)]
                except:
                    continue

    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc
    


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 30))


def update_score(nscore):
    score = max_score()

    with open('scores.txt', 'w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))


def max_score():
    with open('scores.txt', 'r') as f:
        lines = f.readlines()
        score = lines[0].strip()

    return score


def draw_window(surface, grid, score=0, last_score = 0):
    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    # current score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(score), 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100

    surface.blit(label, (sx + 20, sy + 160))
    # last score
    label = font.render('High Score: ' + last_score, 1, (255,255,255))

    sx = top_left_x - 250
    sy = top_left_y + 200

    surface.blit(label, (sx + 20, sy + 160))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

    draw_grid(surface, grid)
    #pygame.display.update()



"""-------------------------OPENCV---------------------"""
"""La idea principal es que los controles sean, pixeles de la linea izquierda->mover bloque a izquierda| pixeles superiores a linea derecha->mover bloque a derecha|hacia arriba girar bloque"""
cap = cv2.VideoCapture(0)
def pointCoordenates(frame):
    global cordeX, cordeY   #Coordenadas del objeto a detectar por su color(Rojo)
    #Definimos los rangos del color a detectar
    azulBajo = np.array([100, 100, 20])
    azulAlto = np.array([125, 255, 255])
    #Convertimos la imagen de BGR a HSV 
    frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Aplicamos la mascara
    mask = cv2.inRange(frameHSV, azulBajo, azulAlto)
    # Obtenemos los contornos de las partes blancas y los dibujamos
    contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Como se dibujan multiples contornos.
    for contor in contornos: #Recorremos todos los contornos azules encontrados
        area = cv2.contourArea(contor) #Obtenemos el area de los contornos
        if area > 700: #Solo los mayores a 700
            # Buscamos las coordenadas del centro
            centros = cv2.moments(contor)
            if (centros["m00"] == 0): centros["m00"] = 1
            x = int(centros["m10"] / centros["m00"])
            y = int(centros["m01"] / centros["m00"])
            cordeX = x # coordenada x del contorno
            cordeY = y # coordenada y del contorno
            # Dibujamos un circulo con las coordenadas del contorno
            #cv2.circle(frame, (x, y), 7, (0, 255, 0), -1) # 7 es el radio del circulo
            # Mostramos en pantalla las coordenadas
            cv2.putText(frame, '{},{}'.format(x, y), (x + 10, y), font, 0.75, (0, 255, 0), 1, cv2.LINE_AA)
            # Luego de eliminar los contorno menores a cierta area, vamos a suavizar los contornos
            contorSuavi = cv2.convexHull(contor) #suavizamos los contornos
            cv2.drawContours(frame, [contorSuavi], 0, (255, 0, 0), 3) #dibujamos los contornos


def openCamera():
    global x_change,cordeX,cordeY   #Coordenadas del objeto a detectar por su color
    global current_piece
    global grid
    

    while (cap.isOpened()): #Mientras la camara se encuentre abierta se realizará la lectura de los frames
        
        ret, frame = cap.read() # capturamos un frame
        frame = cv2.flip(frame, 1) #Usamos flip 1 para girar el frame horizontalmente
        if ret == True: # Si se logró leer con exito un frame realizamos el preprocesado.
            #Creamos el volante
            cv2.rectangle(frame,(150,80),(470,300),(0,255,0),1)
            #cv2.circle(frame,(318,382),170,(0,255,0),2)

            fil = frame.shape[0]  #capturamos las dimensiones de l frame
            col = frame.shape[1]  #capturamos las dimensiones de l frame
            # las coordenas en x de las lineas usadas para los umbrales
            x_medio_derecha = int((col + 60) / 2)
            x_medio_izquierda = int((col - 60) / 2)
            cordeX = int(col / 2) #inicializamos las cordenas del material de color rojo
            cordeY = int(fil / 2) #inicializamos las cordenas del material de color rojo
            # creamos dos lineas, las cuales nos servirán para definir los segmentos donde se encuentre objeto azul
            # Linea derecha
            cv2.line(frame, (x_medio_derecha, 0), (x_medio_derecha, fil), (0, 255, 0), 2)
            cv2.line(frame, (x_medio_izquierda, 80), (x_medio_derecha, 80), (0, 255, 0), 3)
            # Linea izquierda
            cv2.line(frame, (x_medio_izquierda, 0), (x_medio_izquierda, fil), (0, 255, 0), 2)
            pointCoordenates(frame) #Hacemos uso de la función documentada anteriormente
            # Deacuerdo a la coordenada en X donde se encuentre el objeto a detectar, realizamos el moviemto 
            # izquierda
            if (cordeX > 0 and cordeX < x_medio_izquierda):
                x_change = -0.7 #indica que el objeto se encuentra en el segmento izquierdo y por lo tanto el usuario desea mover el bloque en esta dirección
                if(current_piece.x>1):
                    current_piece.x -= 1
                    time.sleep(0.5)
            if(cordeX >= x_medio_izquierda and cordeX <= x_medio_derecha):
                x_change = 0 #indica que el objeto azul se encuentra en el segmento centro y por lo tanto el usuario desea no mover el bloque en ninguna dirección 
            #derecha
            if(cordeX > x_medio_derecha and cordeX < col): #indica que el objeto se encuentra en el segmento derecho y por lo tanto el usuario desea mover el bloque en esta dirección
                x_change = 0.7 
                """ if(current_piece.x<5):
                    current_piece.x -= 1
                    time.sleep(0.5)  not defined!!"""
            if(cordeX > x_medio_derecha and cordeX < col): #indica que el objeto se encuentra en el segmento derecho y por lo tanto el usuario desea mover bloque en esta dirección
                x_change = 0.7 
                #current_piece.x -= 1     not defined ??????????????---- 
            #Girar bloque    
            cv2.imshow('Tetris', frame) #Mostramos la imagen
            if cv2.waitKey(1) & 0xFF == ord('s'): # Cuando se presione la tecla 'S', se cierra la pestaña
                break
                
    cap.release() #Finalizamos la lectura de la camara
    cv2.destroyAllWindows() #Destruir pestañas
"""-----------------Final OPENCV------------------""" 
def main(win):  # *
    last_score = max_score()
    global locked_positions
    locked_positions = {}
    
    #grid = create_grid(locked_positions)

    change_piece = False
    run = True
    global current_piece
    current_piece = get_shape()
    
    
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    score = 0
    global x_change
    red_detected = False
    

    while run:          
        
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()


        if level_time/1000 > 5:
            level_time = 0
            if level_time > 0.12:
                level_time -= 0.005

        if fall_time/1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
            

            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.rotation -= 1
                
                        


        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        draw_window(win, grid, score, last_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(win, "YOU LOST!", 80, (255,255,255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_score(score)
   
              


def main_menu(win):  # *
    run = True
    while run:
        win.fill((0,0,0))
        draw_text_middle(win, 'Press Any Key To Play', 60, (255,255,255))

        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
            if event.type == pygame.KEYDOWN:
                   
                main(win)
                
                
    
        

    pygame.display.quit()


win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')

threadCamera = threading.Thread(target=openCamera)
threadCamera.start()

main_menu(win)

       
cap.release()
cv2.destroyAllWindows()