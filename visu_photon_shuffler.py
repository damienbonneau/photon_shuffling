from switching_network import *
import pygame as pg



import os, sys
from pygame.locals import *

#if not pygame.font: print 'Warning, fonts disabled'
#if not pygame.mixer: print 'Warning, sound disabled'


CYCLING_COLUMN = 0
CYCLING_LINE = 1



class SwitchVisu():
    """The Main PyMan Class - This class handles the main 
    initialization and creating of the Game."""
    
    def __init__(self, width=640,height=480):
        pg.init()
        self.width = width
        self.height = height
        self.screen = pg.display.set_mode((self.width
                                               , self.height))
                                               
        self.switch = SwitchNetwork()
        self.sample = self.switch.get_sample() 
        self.status = CYCLING_COLUMN
        
        self.cursor_pos = [0,0]
        
        
        N,M = self.switch.matrix.shape
        
        self.w_pix = int(self.width/N )
        self.h_pix  = int(self.height/M )
        size = (self.w_pix,self.h_pix)
        self.photon_sprite = pg.Surface(size)
        self.cycle_area_sprite = pg.Surface(size)
        
        self.photon_sprite.fill((0,125,0))
        self.cycle_area_sprite.fill((20,20,20))
            
        self._cache_text = {}
        
    def toggle(self):
        if self.status == CYCLING_COLUMN:
            self.status = CYCLING_LINE
        else:
            self.status = CYCLING_COLUMN
     
    def handle(self,key):
        if key == K_SPACE:
            self.sample = self.switch.get_sample() 
        elif key == K_TAB: # toggle between row and column
            self.toggle()
        elif key == K_ESCAPE:
             sys.exit()
        
        if key in [K_UP,K_DOWN,K_LEFT,K_RIGHT]:
            if self.status == CYCLING_COLUMN:
                self.handle_cycle_line(key)
            if self.status == CYCLING_LINE:
                self.handle_cycle_column(key)
     
     
    def handle_cycle_line(self,key):
        N,M = self.switch.matrix.shape
        if key == K_RIGHT:
            self.sample = self.switch.cycle_line(self.sample,self.cursor_pos[1],RIGHT)
        if key == K_LEFT:
            self.sample = self.switch.cycle_line(self.sample,self.cursor_pos[1],LEFT)
        
        
        if key == K_DOWN:
            self.cursor_pos[1] += 1
            if self.cursor_pos[1] >M-1:
                self.cursor_pos[1] = 0
        elif key == K_UP:
            self.cursor_pos[1] -= 1
            if self.cursor_pos[1] <0:
                self.cursor_pos[1] = M-1
                
        
        
    def handle_cycle_column(self,key):
        N,M = self.switch.matrix.shape
        if key == K_UP:
            self.sample = self.switch.cycle_column(self.sample,self.cursor_pos[0],UP)
        elif key == K_DOWN :
            self.sample = self.switch.cycle_column(self.sample,self.cursor_pos[0],DOWN)
        if key == K_RIGHT:
            self.cursor_pos[0] += 1
            if self.cursor_pos[0] >N-1:
                self.cursor_pos[0] = 0
        elif key == K_LEFT:
            self.cursor_pos[0] -= 1
            if self.cursor_pos[0] <0:
                self.cursor_pos[0] = N-1
        
     
    def draw(self):
        N,M = self.switch.matrix.shape
        w,h = self.w_pix,self.h_pix
        
        # 
        for i in range(N):
            #i = N-1-i0
            for j in range(M):
                #j = M-1-j0
                pos = (w*i,h*j)
                # Draw switch
                if self.switch.matrix[i,j] == 1:
                    self.screen.blit(self.cycle_area_sprite,pos)
                
                # Draw photon
                if self.sample[i,j] == 1:
                    self.screen.blit(self.photon_sprite,pos)
        
        
        # Draw accessible places
        for i,j,di,dj in self.switch.get_accessible_coords(tuple(self.cursor_pos)):
            x,y = w*i,h*j
            pg.draw.rect(self.screen, (150,150,150),(x+1,y-1,w-2,h-2),  3)  

            if pg.font:
                font = pg.font.Font(None, 12)
                if not self._cache_text.has_key((di,dj)):
                    self._cache_text[(di,dj)] = font.render("%d,%d" % (di,dj), 1, (255, 0, 0))
                
                text = self._cache_text[(di,dj)] 
                textpos = text.get_rect(centerx=x+w/2,centery = y+h/2)
                self.screen.blit(text, textpos)
            
        
        # Draw groups
        group_colours = [(120,50,50),(255,50,50)]
        k = 0
        for group in self.switch.target_groups:
            for i,j in group:
                x,y = w*i,h*j
                pg.draw.rect(self.screen, group_colours[k % len(group_colours)],(x,y,w,h),  3)        
        
            k += 1
        
              
        
        # Draw cursor
        x,y = w*self.cursor_pos[0],h*self.cursor_pos[1]
        pg.draw.rect(self.screen, (0,125,255),(x+1,y-1,w-2,h-2), 3)        
        
        
        
    def MainLoop(self):
        # tell pygame to keep sending up keystrokes when they are held down
        pg.key.set_repeat(500, 30)
        
        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0,0,0))
        
        clock = pg.time.Clock() 
        
        
        while 1:
            for event in pg.event.get():
                if event.type == pg.QUIT: 
                    sys.exit()
           
                elif event.type == KEYDOWN:
                    #if event.key in [K_RIGHT,K_LEFT,K_UP,K_DOWN] :
                    self.handle(event.key)
                        
            self.screen.blit(self.background, (0, 0))     
            
            clock.tick(60)
            self.draw()
            
            pg.display.flip()
if __name__ == "__main__":
    sv = SwitchVisu()       
    sv.MainLoop()