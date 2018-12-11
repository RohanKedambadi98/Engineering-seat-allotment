import winsound
import time
import pygame

freq=5000
duration=100
winsound.Beep(freq,duration)


for i in range(1,10):
    time.sleep(0.5)
    winsound.MessageBeep(5)
    time.sleep(0.3)
    winsound.Beep(freq, duration)
    time.sleep(1)



pygame.init()

pygame.mixer.music.load("test.wav")

pygame.mixer.music.play()

time.sleep(10)



