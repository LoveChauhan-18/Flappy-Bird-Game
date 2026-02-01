import pygame
import sys
import random
import os

pygame.init()
pygame.mixer.init()

# ---------------- CONSTANTS ----------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Ultimate")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 60)

START, PLAYING, GAME_OVER = 0, 1, 2
state = START
difficulty = None

DARK_MODE = False
RAIN = False
FOG = False

# ---------------- HIGHSCORE ----------------
def load_highscore():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            return int(f.read())
    return 0

def save_highscore(val):
    with open("highscore.txt", "w") as f:
        f.write(str(val))

high_score = load_highscore()

# ---------------- THEME ----------------
def set_theme():
    if DARK_MODE:
        return {"sky": (15,15,30),"text":(230,230,230),
                "ground":(70,70,70),"pipe":(0,180,120)}
    else:
        return {"sky": (135,206,235),"text":(0,0,0),
                "ground":(222,216,149),"pipe":(0,180,0)}

# ---------------- SOUNDS ----------------
jump_sound = pygame.mixer.Sound("jump.wav.mp3")
hit_sound = pygame.mixer.Sound("hit.wav.mp3")
score_sound = pygame.mixer.Sound("score.wav.mp3")

# ---------------- BIRD ----------------
bird = pygame.transform.scale(pygame.image.load("bird.png"), (40,30))
bird_x, bird_y = 100, HEIGHT//2
bird_vel = 0
gravity = 0.3
jump_force = -7

# ---------------- PARALLAX ----------------
stars = [(random.randint(0,WIDTH), random.randint(0,HEIGHT//2)) for _ in range(60)]
star_x = mount_x = hill_x = cloud_x = 0

# ---------------- WEATHER ----------------
rain_drops = [[random.randint(0,WIDTH), random.randint(0,HEIGHT)] for _ in range(120)]
fog_x = 0

# ---------------- GROUND ----------------
ground_h = 60
ground_y = HEIGHT-ground_h
ground_x = 0

# ---------------- PIPES ----------------
pipe_w = 80
pipe_gap = 180
pipe_speed = 3
pipes = []

score = 0

# ---------------- FUNCTIONS ----------------
def set_difficulty(level):
    global gravity, jump_force, pipe_gap, pipe_speed
    if level == "EASY":
        gravity, jump_force, pipe_gap, pipe_speed = 0.3, -7, 220, 2
    elif level == "MEDIUM":
        gravity, jump_force, pipe_gap, pipe_speed = 0.35, -8, 180, 3
    else:
        gravity, jump_force, pipe_gap, pipe_speed = 0.45, -9, 150, 4

def new_pipe():
    return {"x": WIDTH, "top": random.randint(120,350), "passed": False}

def reset_game():
    global bird_y, bird_vel, pipes, score
    bird_y, bird_vel = HEIGHT//2, 0
    pipes = [new_pipe()]
    score = 0

# ---------------- MAIN LOOP ----------------
while True:
    theme = set_theme()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d: DARK_MODE = True
            if event.key == pygame.K_l: DARK_MODE = False
            if event.key == pygame.K_r: RAIN = not RAIN
            if event.key == pygame.K_f: FOG = not FOG

        if state == START and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: difficulty = "EASY"
            if event.key == pygame.K_2: difficulty = "MEDIUM"
            if event.key == pygame.K_3: difficulty = "HARD"
            if difficulty:
                set_difficulty(difficulty)
                reset_game()
                state = PLAYING

        if state == PLAYING and event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            bird_vel = jump_force
            jump_sound.play()

        if state == GAME_OVER and event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            state = START
            difficulty = None

    # ---------------- BACKGROUND ----------------
    screen.fill(theme["sky"])

    star_x -= 0.2
    for x,y in stars:
        pygame.draw.circle(screen,(255,255,255),((x+int(star_x))%WIDTH,y),2)

    mount_x -= 0.4
    for i in range(5):
        pygame.draw.polygon(screen,(120,120,150),
            [((mount_x+i*300)%WIDTH,ground_y),
             ((mount_x+i*300+150)%WIDTH,250),
             ((mount_x+i*300+300)%WIDTH,ground_y)])

    hill_x -= 0.8
    for i in range(6):
        pygame.draw.circle(screen,(80,170,90),
            ((hill_x+i*200)%WIDTH,ground_y),120)

    cloud_x -= 1.2
    for i in range(5):
        pygame.draw.circle(screen,(255,255,255),
            ((cloud_x+i*220)%WIDTH,120+i*5),30)

    # ---------------- WEATHER ----------------
    if RAIN:
        for d in rain_drops:
            d[0]-=2; d[1]+=8
            if d[1]>HEIGHT:
                d[0]=random.randint(0,WIDTH); d[1]=random.randint(-100,0)
            pygame.draw.line(screen,(180,180,255),(d[0],d[1]),(d[0]+3,d[1]+10))

    if FOG:
        fog = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        fog.fill((200,200,200,40))
        fog_x = (fog_x+0.3)%WIDTH
        screen.blit(fog,(-fog_x,0))
        screen.blit(fog,(WIDTH-fog_x,0))

    # ---------------- GROUND ----------------
    ground_x -= pipe_speed
    if ground_x <= -WIDTH: ground_x = 0
    pygame.draw.rect(screen,theme["ground"],(ground_x,ground_y,WIDTH,ground_h))
    pygame.draw.rect(screen,theme["ground"],(ground_x+WIDTH,ground_y,WIDTH,ground_h))

    # ---------------- STATES ----------------
    if state == START:
        screen.blit(big_font.render("FLAPPY BIRD",True,theme["text"]),(260,120))
        screen.blit(font.render("1 EASY  2 MEDIUM  3 HARD",True,theme["text"]),(240,300))
        screen.blit(font.render(f"High Score : {high_score}",True,theme["text"]),(300,350))
        screen.blit(font.render("R Rain  F Fog  D/L Theme",True,theme["text"]),(210,400))

    elif state == PLAYING:
        bird_vel += gravity
        bird_y += bird_vel
        bird_rect = pygame.Rect(bird_x,bird_y,40,30)

        if bird_y<=0 or bird_y+30>=ground_y:
            hit_sound.play(); state=GAME_OVER

        for p in pipes:
            p["x"]-=pipe_speed
            top = pygame.Rect(p["x"],0,pipe_w,p["top"])
            bot = pygame.Rect(p["x"],p["top"]+pipe_gap,pipe_w,HEIGHT)

            pygame.draw.rect(screen,theme["pipe"],top)
            pygame.draw.rect(screen,theme["pipe"],bot)

            if bird_rect.colliderect(top) or bird_rect.colliderect(bot):
                hit_sound.play(); state=GAME_OVER

            if not p["passed"] and p["x"]+pipe_w<bird_x:
                p["passed"]=True
                score+=1
                score_sound.play()
                if score>high_score:
                    high_score=score
                    save_highscore(high_score)

        if pipes[0]["x"]<-pipe_w:
            pipes.pop(0); pipes.append(new_pipe())

        screen.blit(pygame.transform.rotate(bird,-bird_vel*3),(bird_x,bird_y))
        screen.blit(font.render(f"Score : {score}",True,theme["text"]),(20,20))
        screen.blit(font.render(f"High : {high_score}",True,theme["text"]),(20,50))

    else:
        screen.blit(big_font.render("GAME OVER",True,(255,60,60)),(260,230))
        screen.blit(font.render(f"Score : {score}",True,theme["text"]),(330,300))
        screen.blit(font.render(f"High : {high_score}",True,theme["text"]),(330,340))
        screen.blit(font.render("Press any key",True,theme["text"]),(300,390))

    pygame.display.update()
    clock.tick(60)