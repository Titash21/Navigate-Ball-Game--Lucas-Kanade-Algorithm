# 1 - Import library
import pygame
from pygame.locals import *
import random
import time
# 2 - Initialize the game
pygame.init()
width, height = 1200, 700
screen=pygame.display.set_mode((width, height))
keys = [False, False, False, False]
playerpos=[100,100]

badtimer=100
badtimer1=0
badguys=[[1200,100]]
healthvalue=200
# 3 - Load images
player = pygame.image.load("1.jpg")
background = pygame.image.load("4.jpg")
badguyimg = pygame.image.load("2.jpg")
healthbar = pygame.image.load("healthbar.png")
health = pygame.image.load("health.png")
gameover = pygame.image.load("gameover.png")
# 4 - keep looping through
time0=time.time()
running = 1
exitcode = 0
while running:
    badtimer-=1
    # 5 - clear the screen before drawing it again
    screen.fill(0)
    # 6 - draw the screen elements
    for x in range(int(width/background.get_width()+1)):
        for y in range(int(height/background.get_height()+1)):
            screen.blit(background,(x*500,y*300))
    screen.blit(player, playerpos)
    if badtimer==0:
        badguys.append([1200, random.randint(50,700)])
        badtimer=100-(badtimer1*2)
        if badtimer1>=35:
            badtimer1=35
        else:
            badtimer1+=5
    index=0
    for badguy in badguys:
        if badguy[0]<-64:
            badguys.pop(index)
        badguy[0]-=7
        badrect=pygame.Rect(badguyimg.get_rect())
        badrect.top=badguy[1]
        badrect.left=badguy[0]
        index+=1
    for badguy in badguys:
        playerrect=pygame.Rect(player.get_rect())
        playerrect.left=playerpos[0]
        playerrect.top=playerpos[1]
        if badrect.colliderect(playerrect):
            healthvalue -= 1
        screen.blit(badguyimg, badguy)

    font = pygame.font.Font(None, 24)
    timeX=time.time()-time0;
    survivedtext = font.render(str(timeX), True, (0,0,0))
    textRect = survivedtext.get_rect()
    textRect.topright=[1200,5]
    screen.blit(survivedtext, textRect)
    screen.blit(healthbar, (3,3))
    for health1 in range(healthvalue):
        screen.blit(health, (health1+5,5))
    # 7 - update the screen
    pygame.display.flip()
    # 8 - loop through the events
    for event in pygame.event.get():
        # check if the event is the X button
        if event.type==pygame.QUIT:
            # if it is quit the gamepy
            game.quit()
            exit(0)
        if event.type == pygame.MOUSEMOTION:
            playerpos[1] = event.pos[1]
            playerpos[0] = event.pos[0]
     #10 - Win/Lose check
    if healthvalue<=0:
        running=0
        exitcode=0
       # 11 - Win/lose display 
if exitcode==0:
    pygame.font.init()
    font = pygame.font.Font(None, 24)
    text = font.render("You survive: "+str(time.time()-time0), True, (0,255,0))
    textRect = text.get_rect()
    textRect.centerx = screen.get_rect().centerx
    textRect.centery = screen.get_rect().centery+24
    screen.blit(gameover, (0,0))
    screen.blit(text, textRect)
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    pygame.display.flip()

