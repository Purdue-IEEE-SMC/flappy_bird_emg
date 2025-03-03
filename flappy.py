import pygame, random, time
from pygame.locals import *
import serial
import serial.tools
import serial.tools.list_ports
import sys

#VARIABLES
SCREEN_WIDHT = 400
SCREEN_HEIGHT = 600
SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15
LOOP_SPEED = 10

GROUND_WIDHT = 2 * SCREEN_WIDHT
GROUND_HEIGHT= 100

PIPE_WIDHT = 80
PIPE_HEIGHT = 500

PIPE_GAP = 150

THRESHOLD = 50
flap = True
emg_debug = False

wing = 'assets/audio/wing.wav'
hit = 'assets/audio/hit.wav'

pygame.mixer.init()


ports = serial.tools.list_ports.comports()

port_selected = False
auto_select = True

while(not(port_selected)):
    print("===Available Serial Ports===")
    for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))
    print("Exit: exit")
    print("Keyboard-Only Mode: none")
    if(len(ports) == 1 & auto_select):
        #print(str(sorted(ports)[0].device))
        try:
            serial_port = serial.Serial(sorted(ports)[0].device)
            port_selected = True
            print("Port ", str(sorted(ports)[0].device),"autoselected")
        except:
            print("autoselection failed")
            port_selected = False
            auto_select = False
    else:
        choice = input("Enter Serial Port name to be used: ")
        if(choice == "exit"):
            sys.exit()
        if(choice == "none"):
            break
        try:
            serial_port = serial.Serial(choice)
            port_selected = True
        except:
            print("\nERROR: Invalid Serial Port Choice.\n")
            port_selected = False

if(port_selected):
    serial_port.timeout = 0.1


class Bird(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.images =  [pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
                        pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
                        pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()]

        self.speed = SPEED

        self.current_image = 0
        self.image = pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDHT / 6
        self.rect[1] = SCREEN_HEIGHT / 2

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY

        #UPDATE HEIGHT
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

    def begin(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]

    def reset(self):
        self.rect[0] = SCREEN_WIDHT / 6
        self.rect[1] = SCREEN_HEIGHT / 2




class Pipe(pygame.sprite.Sprite):

    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)

        self. image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDHT, PIPE_HEIGHT))


        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize


        self.mask = pygame.mask.from_surface(self.image)


    def update(self):
        self.rect[0] -= GAME_SPEED

        

class Ground(pygame.sprite.Sprite):
    
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDHT, GROUND_HEIGHT))

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT
    def update(self):
        self.rect[0] -= GAME_SPEED

def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDHT, SCREEN_HEIGHT))
BEGIN_IMAGE = pygame.image.load('assets/sprites/message.png').convert_alpha()

bird_group = pygame.sprite.Group()
bird = Bird()
bird_group.add(bird)

ground_group = pygame.sprite.Group()

for i in range (2):
    ground = Ground(GROUND_WIDHT * i)
    ground_group.add(ground)

pipe_group = pygame.sprite.Group()
for i in range (2):
    pipes = get_random_pipes(SCREEN_WIDHT * i + 800)
    pipe_group.add(pipes[0])
    pipe_group.add(pipes[1])



clock = pygame.time.Clock()

begin = True

while(True):
    while begin:

        clock.tick(LOOP_SPEED)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE or event.key == K_UP:
                    bird.bump()
                    pygame.mixer.music.load(wing)
                    pygame.mixer.music.play()
                    begin = False
        if(port_selected):
            serial_port.reset_input_buffer()
            line = serial_port.readline()
            line = str(line.strip().decode())            
            if(emg_debug):
                print(line)
            try:
                if(int(line) > THRESHOLD):
                    if(flap == False):
                        bird.bump()
                        pygame.mixer.music.load(wing)
                        pygame.mixer.music.play()
                        if(emg_debug):
                            print("flap!")
                        flap = True
                        begin = False
                else:
                    flap = False
            except:
                pass

        screen.blit(BACKGROUND, (0, 0))
        screen.blit(BEGIN_IMAGE, (120, 150))

        if is_off_screen(ground_group.sprites()[0]):
            ground_group.remove(ground_group.sprites()[0])

            new_ground = Ground(GROUND_WIDHT - 20)
            ground_group.add(new_ground)

        bird.begin()
        ground_group.update()

        bird_group.draw(screen)
        ground_group.draw(screen)

        pygame.display.update()


    while True:

        clock.tick(LOOP_SPEED)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE or event.key == K_UP:
                    bird.bump()
                    pygame.mixer.music.load(wing)
                    pygame.mixer.music.play()
        if(port_selected):
            serial_port.reset_input_buffer()
            line = serial_port.readline()
            line = str(line.strip().decode())
            if(emg_debug):
                print(line)
            try:
                if(int(line) > THRESHOLD):
                    if(flap == False):
                        bird.bump()
                        pygame.mixer.music.load(wing)
                        pygame.mixer.music.play()
                        if(emg_debug):
                            print("flap!")
                        flap = True
                else:
                    flap = False
            except:
                pass


        screen.blit(BACKGROUND, (0, 0))

        if is_off_screen(ground_group.sprites()[0]):
            ground_group.remove(ground_group.sprites()[0])

            new_ground = Ground(GROUND_WIDHT - 20)
            ground_group.add(new_ground)

        if is_off_screen(pipe_group.sprites()[0]):
            pipe_group.remove(pipe_group.sprites()[0])
            pipe_group.remove(pipe_group.sprites()[0])

            pipes = get_random_pipes(SCREEN_WIDHT * 2)

            pipe_group.add(pipes[0])
            pipe_group.add(pipes[1])

        bird_group.update()
        ground_group.update()
        pipe_group.update()

        bird_group.draw(screen)
        pipe_group.draw(screen)
        ground_group.draw(screen)

        pygame.display.update()

        if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
                pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)):
            pygame.mixer.music.load(hit)
            pygame.mixer.music.play()
            time.sleep(1)
            break
    begin = True
    bird.reset()

