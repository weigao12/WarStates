"""
Show the proper way to organize a game using the a game class.

Sample Python/Pygame Programs
Simpson College Computer Science
http://programarcadegames.com/
http://simpson.edu/computer-science/

Explanation video: http://youtu.be/O4Y5KrNgP_c
"""

import pygame
import random
import numpy as np
import shelve
import json


# --- Global constants ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE= (0, 0, 255)
YELLOW= (255,255,0)

SCREEN_EDGE = 5
SCREEN_WIDTH = 250
SCREEN_HEIGHT = 300
BLOCK_WIDTH = 10
STATE_NUM = 1
StateName = {"RED":RED,"BLUE":BLUE,"GREEN":GREEN}
#RGB = StateName[jname]
# --- Classes ---


class Block(pygame.sprite.Sprite):
    """ This class represents a simple block the player collects. """
    def __init__(self):
        """ Constructor, create the image of the block. """
        self.radius=20
        super().__init__()
        self.image = pygame.Surface([BLOCK_WIDTH,BLOCK_WIDTH])
        #self.image.fill(colour)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

    def reset_pos(self):
        """ Called when the block is 'collected' or falls off
            the screen. """
        self.rect.y = random.randrange(-300, -20)
        self.rect.x = random.randrange(SCREEN_WIDTH)

    def update(self):
        """ Automatically called when we need to move the block. """
        #self.rect.y += 1

        #self.image = pygame.Surface([20, 20])
        self.image = pygame.Surface([ self.radius, self.radius])
        self.rect = self.image.get_rect()
        self.radius = self.radius + 1
        if self.rect.y > SCREEN_HEIGHT + self.rect.height:
            self.reset_pos()


class Player(pygame.sprite.Sprite):
    """ This class represents the player. """
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([BLOCK_WIDTH,BLOCK_WIDTH])
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()

    def update(self):
        """ Update the player location. """
        pos = pygame.mouse.get_pos()
        self.rect.x = pos[0]
        self.rect.y = pos[1]


class NatureBlock(pygame.sprite.Sprite):
    """ This class represents a simple block the player collects. """
    def __init__(self,colour,x,y):
        """ Constructor, create the image of the block. """
        super().__init__()
        self.colour = colour
        self.image = pygame.Surface([BLOCK_WIDTH,BLOCK_WIDTH])
        self.image.fill(self.colour)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.radius=BLOCK_WIDTH

class MountainRiver(object):
    def __init__(self,colour):
        self.name = ''
        self.city_count = 0
        self.colour = colour

        # Create mountain and river
        self.block_list = pygame.sprite.Group()
        riverWidth=BLOCK_WIDTH

        for x in np.arange(0,SCREEN_WIDTH,riverWidth):
            #print("%d mount river add block ",x)
            block=NatureBlock(colour,x,SCREEN_HEIGHT/2)
            self.block_list.add(block)
        #Add ferry
        for x in np.arange(SCREEN_WIDTH/2-2*riverWidth,SCREEN_WIDTH/2,riverWidth):
            block=NatureBlock(colour,x,SCREEN_HEIGHT/2)
            blocks_hit_list = pygame.sprite.spritecollide(block,self.block_list, True)


    def display(self,screen):
        self.block_list.draw(screen)

    def stopTraffic(self,state):
        for block in self.block_list:
            #blocks_hit_list = pygame.sprite.spritecollide(block,state.borderBlocks, True)
            blocks_hit_list = pygame.sprite.spritecollide(block,state.all_sprites_list, False)
            for block in blocks_hit_list:
                state.delBlock(block)


class CityBlock(pygame.sprite.Sprite):
    """ This class represents a simple block the player collects. """
    def __init__(self,colour):
        """ Constructor, create the image of the block. """
        super().__init__()
        self.colour = colour
        self.image = pygame.Surface([BLOCK_WIDTH,BLOCK_WIDTH])
        self.image.fill(self.colour)
        self.rect = self.image.get_rect()
        self.radius=BLOCK_WIDTH

    def reset_pos(self):
        """ Called when the block is 'collected' or falls off
            the screen. """
        self.rect.y = random.randrange(SCREEN_WIDTH)
        self.rect.x = random.randrange(SCREEN_WIDTH)

    def update(self):
        """ Automatically called when we need to move the block. """
        self.image = pygame.Surface([ self.radius, self.radius])
        self.rect = self.image.get_rect()

class State(object):
    """ This class represents a state"""

    def __init__(self,name,colour):
        """ Constructor """

        self.name = name
        self.city_count = 0
        self.colour = colour
        self.aggression = 5 #SunZi yue, Wu Ze Gong Zhi 
        print("State ", self.name)
        # Create sprite lists
        self.new_sprites_list= pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()
        self.block_list = pygame.sprite.Group()
        self.borderBlocks = pygame.sprite.Group()
        self.warborderCnt = {"RED":0,"BLUE":0,"GREEN":0}
        self.army= {"RED":0,"BLUE":0,"GREEN":0}
        self.power= 0

        # Create the init city of state
        for i in range(1):
            block = CityBlock(self.colour)

            block.rect.x = random.randrange(SCREEN_WIDTH)
            #block.rect.x = block.rect.x - block.rect.x%BLOCK_WIDTH #align
            block.rect.y = random.randrange(SCREEN_HEIGHT)
            #block.rect.y = block.rect.y - block.rect.y%BLOCK_WIDTH
            print("Init point: x is",block.rect.x,",y is",block.rect.y )

            self.new_sprites_list.add(block)
            self.all_sprites_list.add(block)
            self.borderBlocks.add(block)

    def allColor(self):
        for block in self.all_sprites_list:
            block.image.fill(self.colour)

    def borderColor(self,colour):
        for block in self.borderBlocks:
            block.image.fill(colour)

    def expand_direction(self,block,x,y):
            new_block = CityBlock(self.colour)
            new_block.rect.x = block.rect.x  + x*block.radius
            new_block.rect.y = block.rect.y  + y*block.radius

            #out of screen, older block is border
            if((new_block.rect.y > SCREEN_HEIGHT-SCREEN_EDGE) or (new_block.rect.x>SCREEN_WIDTH-SCREEN_EDGE)
               or (new_block.rect.y <0 ) or (new_block.rect.x < 0)):
                 blocks_hit_list = pygame.sprite.spritecollide(block,self.block_list, True)
                 self.block_list.add(block)
                 return

            #this is not in all_sprites_list, it is a really new block
            blocks_hit_list = pygame.sprite.spritecollide(new_block,self.all_sprites_list, False)
            if(len(blocks_hit_list) == 0):
                blocks_hit_list = pygame.sprite.spritecollide(new_block,self.block_list, True)
                self.block_list.add(new_block)

    def expand(self):
        # State expand.
        add_block_num=0
        self.block_list = pygame.sprite.Group()
        #self.block_list.empty()

        for block in self.borderBlocks:
            self.expand_direction(block,0,1)
            self.expand_direction(block,1,1)
            self.expand_direction(block,1,0)
            self.expand_direction(block,1,-1)
            self.expand_direction(block,0,-1)
            self.expand_direction(block,-1,-1)
            self.expand_direction(block,-1,0)
            self.expand_direction(block,-1,1)

        add_block_num=len(self.block_list)
        #print('------------add block',add_block_num)

        self.all_sprites_list.add(self.block_list)
        self.borderBlocks= self.block_list

    def shrinkDirection(self,block,x,y):
            new_block = CityBlock(self.colour)
            new_block.rect.x = block.rect.x  + x*block.radius
            new_block.rect.y = block.rect.y  + y*block.radius

            #this is in all_sprites_list, the new block will add to border
            blocks_hit_list = pygame.sprite.spritecollide(new_block,self.all_sprites_list, False)
            if(len(blocks_hit_list) > 0):
                blocks_hit_list = pygame.sprite.spritecollide(new_block,self.borderBlocks, False)
                if(len(blocks_hit_list) == 0):
                    self.borderBlocks.add(new_block)

    def shrinkBlock(self,block):
            self.shrinkDirection(block,0,1)
            self.shrinkDirection(block,1,1)
            self.shrinkDirection(block,1,0)
            self.shrinkDirection(block,1,-1)
            self.shrinkDirection(block,0,-1)
            self.shrinkDirection(block,-1,-1)
            self.shrinkDirection(block,-1,0)
            self.shrinkDirection(block,-1,1)

    def delBlock(self,block):
        blocks_hit_list = pygame.sprite.spritecollide(block,self.all_sprites_list, True)
        blocks_hit_list = pygame.sprite.spritecollide(block,self.borderBlocks, True)
        self.shrinkBlock(block)

    """
    If this direction's new block is in some state, return True 
    else return False
    """
    def conflict_detect_direction(self,state,block,x,y):
        new_block = CityBlock(self.colour)
        new_block.rect.x = block.rect.x  + x*block.radius
        new_block.rect.y = block.rect.y  + y*block.radius

        #out of screen, older block is border
        #if((new_block.rect.y > SCREEN_HEIGHT-SCREEN_EDGE) or (new_block.rect.x>SCREEN_WIDTH-SCREEN_EDGE)
        #      or (new_block.rect.y <0 ) or (new_block.rect.x < 0)):
        #    return False 

        #this is not in all_sprites_list, it is a really new block
        blocks_hit_list = pygame.sprite.spritecollide(new_block,state.all_sprites_list, False)
        if(len(blocks_hit_list) != 0):
            return True

        return False 

    def isBorder(self,block):
        if((False == self.conflict_detect_direction(self,block,0,1)) or 
           (False == self.conflict_detect_direction(self,block,1,1)) or
           (False == self.conflict_detect_direction(self,block,1,0)) or
           (False == self.conflict_detect_direction(self,block,1,-1)) or
           (False == self.conflict_detect_direction(self,block,0,-1)) or
           (False == self.conflict_detect_direction(self,block,-1,-1)) or
           (False == self.conflict_detect_direction(self,block,-1,0)) or
           (False == self.conflict_detect_direction(self,block,-1,1))
                ):
           return True 

        #print("state add border",self.name)
        return False 


    def addBlock(self,x,y):
        new_block = CityBlock(self.colour)
        #print("New block Colour is ",self.colour)
        new_block.rect.x = x
        new_block.rect.y = y
        self.all_sprites_list.add(new_block)

    def selBorder(self):
        for block in self.all_sprites_list:
            #print("!!! whether border ",state.name)
            if( True == self.isBorder(block)):
                 #print("state add border for %(n)s %(s)s" % {'n': block.rect.x, 's': block.rect.y})
                 self.borderBlocks.add(block)


    def peace(self,enemy):
        block_list = self.borderBlocks.copy()
        for block in block_list:
            blocks_hit_list = pygame.sprite.spritecollide(block,enemy.all_sprites_list, False)

            if(len(blocks_hit_list) == 0):
                continue

            self.delBlock(block)

    def expandToEnemyDirection(self,block,enemy,x,y):
        new_block = CityBlock(self.colour)
        new_block.rect.x = block.rect.x  + x*block.radius
        new_block.rect.y = block.rect.y  + y*block.radius

        #out of screen, older block is border
        if((new_block.rect.y > SCREEN_HEIGHT-SCREEN_EDGE) or (new_block.rect.x>SCREEN_WIDTH-SCREEN_EDGE)
          or (new_block.rect.y <0 ) or (new_block.rect.x < 0)):
                 return 100


        #expand into own terr, return 2
        blocks_hit_list = pygame.sprite.spritecollide(new_block,self.all_sprites_list, False)
        if(len(blocks_hit_list) > 0):
            return 0

        #this new block is in enemy terratary, it is a really conflict block
        blocks_hit_list = pygame.sprite.spritecollide(new_block,enemy.all_sprites_list, False)
        if(len(blocks_hit_list) > 0):
            blocks_hit_list = pygame.sprite.spritecollide(new_block,self.all_sprites_list, True)
            self.all_sprites_list.add(new_block)
            blocks_hit_list = pygame.sprite.spritecollide(new_block,self.borderBlocks, True)
            self.borderBlocks.add(new_block)
            return 1
        #not in my state, neither enemy state, return 100 as out of screen, older block is border
        return 100

    def expandConflictToState(self,enemy):
        # State expand to enemy state.
        add_block_num=0
        self.block_list = self.borderBlocks

        for block in self.block_list :
            isConflict=0
            isConflict += self.expandToEnemyDirection(block,enemy,0,1)
            isConflict += self.expandToEnemyDirection(block,enemy,1,1)
            isConflict += self.expandToEnemyDirection(block,enemy,1,0)
            isConflict += self.expandToEnemyDirection(block,enemy,1,-1)
            isConflict += self.expandToEnemyDirection(block,enemy,0,-1)
            isConflict += self.expandToEnemyDirection(block,enemy,-1,-1)
            isConflict += self.expandToEnemyDirection(block,enemy,-1,0)
            isConflict += self.expandToEnemyDirection(block,enemy,-1,1)

            #if no block add, it is in own terr
            if(isConflict == 0):
                self.borderBlocks.remove(block)
            #if block expand to enemy terrertry, it will not be a border block
            #if(isConflict > 0):
                #out of screen is special, will be larger than 100
                #if(isConflict <100):
                    #self.borderBlocks.remove(block)
                    #print('------------add block',add_block_num)


    def updStatewarborderCnt(self,enemy):
        self.warborderCnt[enemy.name] = 0
        for block in self.borderBlocks:
            if((True == self.conflict_detect_direction(enemy,block,0,1)) or 
               (True == self.conflict_detect_direction(enemy,block,0,-1)) or
               (True == self.conflict_detect_direction(enemy,block,1,1)) or
               (True == self.conflict_detect_direction(enemy,block,1,0)) or
               (True == self.conflict_detect_direction(enemy,block,1,-1)) or
               (True == self.conflict_detect_direction(enemy,block,-1,1)) or
               (True == self.conflict_detect_direction(enemy,block,-1,-1)) or
               (True == self.conflict_detect_direction(enemy,block,-1,0)) 
               ):
                  self.warborderCnt[enemy.name] = self.warborderCnt[enemy.name] +1
                  continue
        #print("State %(s)s border count to state %(n)s is %(c)s"%{"s":self.name,"n":enemy.name,"c":self.warborderCnt[enemy.name]})

    def conflictWithType(self,enemy,type):
        if(type == "army"):
            self.armyConflictToState(enemy)
        if(type == "line"):
            self.lineConflictToState(enemy)

    def armyConflictToState(self,enemy):
        if ((self.army[enemy.name] == 0) or (enemy.army[self.name] == 0)):
            return

        armyComp = self.army[enemy.name]/enemy.army[self.name]
        if(armyComp >= self.aggression):
            print("Army: state %(n)s %(s)s VS state %(m)s %(b)s"% {'n': self.name, 's':self.army[enemy.name], 'm': enemy.name,'b':enemy.army[self.name]})
            print("Blocks: state %(n)s %(s)s VS state %(m)s %(b)s"% {'n': self.name, 's':self.warborderCnt[enemy.name], 'm': enemy.name,'b':enemy.warborderCnt[self.name]})
            print("Army comp bigger than 5, attack",armyComp)
            if (self.warborderCnt[enemy.name] > 1):
            #    army war mode  ---- lost army  /total army = lost block / total blocks
                self.expandConflictToState(enemy)
                for warField in self.borderBlocks:
                    blocks_hit_list = pygame.sprite.spritecollide(warField,enemy.borderBlocks, False)
                    if(len(blocks_hit_list) == 0):
                        continue
    
                    #defense strength * 2(SunZi yue, bei ze zhan zhi), every defense block arrange equal army
                    blockSoldiers = self.army[enemy.name] / self.warborderCnt[enemy.name]
                    enemyBlockSoldiers = enemy.army[self.name] / enemy.warborderCnt[self.name]
                    print("state %(n)s %(s)s VS state %(m)s %(b)s"% {'n': self.name, 's':blockSoldiers, 'm': enemy.name,'b':enemyBlockSoldiers })
                    if(blockSoldiers/enemyBlockSoldiers >=2):
                        blocks_hit_list = pygame.sprite.spritecollide(warField,enemy.all_sprites_list, True)
                        for delB in blocks_hit_list:
                            enemy.delBlock(delB)
                        print("state %(n)s VS state %(m)s Win 1 battal"% {'n': self.name,'m': enemy.name})
                        self.army[enemy.name] = self.army[enemy.name] - enemyBlockSoldiers*2
                        enemy.army[self.name] = enemy.army[self.name] - enemyBlockSoldiers
                    else:
                        blocks_hit_list = pygame.sprite.spritecollide(warField,self.all_sprites_list, True)
                        for delB in blocks_hit_list:
                            self.delBlock(delB)

            else:  
            #It's a tunnel, like Tibet to India or China inner city
            #    soldier fight mode
                self.lineConflictToState(enemy)
                
   



    def lineConflictToState(self,enemy):
        self.expandConflictToState(enemy)
        for warField in self.borderBlocks:
            blocks_hit_list = pygame.sprite.spritecollide(warField,enemy.borderBlocks, False)
            if(len(blocks_hit_list) == 0):
                continue

            #print("state %(n)s to state %(m)s bias is %(b)s"% {'n': self.name, 'm': enemy.name,'b':bias})
            risk = random.uniform(0, 1)
            if(risk>0.5):
                blocks_hit_list = pygame.sprite.spritecollide(warField,enemy.all_sprites_list, True)
                for delB in blocks_hit_list:
                    enemy.delBlock(delB)
            else:
                blocks_hit_list = pygame.sprite.spritecollide(warField,self.all_sprites_list, True)
                for delB in blocks_hit_list:
                    self.delBlock(delB)

    #conflict proto type
    def conflict(self,enemy):
        #i=random.randrange(len(self.borderBlocks))
        #warField = self.borderBlocks.sprites()[i]
        #for warField in self.borderBlocks:
        #    self.expand_direction(warField,0,1)
        #    print('war start at',warField)
        self.expandConflictToState(enemy)
        for warField in self.borderBlocks:
            blocks_hit_list = pygame.sprite.spritecollide(warField,enemy.borderBlocks, False)
            if(len(blocks_hit_list) == 0):
                continue

            #calculate state entity power and effect on random
            #bias = self.calculatePower() / enemy.calculatePower() 
            #print("state %(n)s to state %(m)s bias is %(b)s"% {'n': self.name, 'm': enemy.name,'b':bias})
            risk = random.uniform(0, 1)
            #risk = risk * bias
            if(risk>0.5):
                blocks_hit_list = pygame.sprite.spritecollide(warField,enemy.all_sprites_list, True)
                for delB in blocks_hit_list:
                    enemy.delBlock(delB)
            else:
                blocks_hit_list = pygame.sprite.spritecollide(warField,self.all_sprites_list, True)
                for delB in blocks_hit_list:
                    self.delBlock(delB)

    def calculatePower(self):  
        power = len(self.all_sprites_list.sprites())
        return power  

    def arrangeArmy(self):  
        self.power = self.calculatePower()
        temp_power = self.power 
        totalwarborderCnt = 0
        for key,val in self.warborderCnt.items():
            totalwarborderCnt = totalwarborderCnt + val
            #print("State %(s)s border to state %(n)s is %(c)s"%{"s":self.name,"n":key,"c":val})

        if(totalwarborderCnt != 0):
            self.army[self.name] =  temp_power 
            for key,val in self.warborderCnt.items():
                self.army[key] = round (val/totalwarborderCnt * self.power/2)
                self.army[self.name] =  temp_power - self.army[key] 
                temp_power = self.army[self.name]   
                #print("State %(s)s army to state %(n)s is %(c)s"%{"s":self.name,"n":key,"c":self.army[key]})
        else:
            #no enemy now
            self.army[self.name] =  temp_power





class Game(object):
    """ This class represents an instance of the game. If we need to
        reset the game we'd just need to create a new instance of this
        class. """

    def __init__(self):
        """ Constructor. Create all our attributes and initialize
        the game. """

        self.isPeace= 1
        self.autoFight = 0
        self.game_over = False
        player = Player()

        # Create the block sprites
        #for i in range(1):
        self.yellowriver = MountainRiver(YELLOW)
        stateRed = State("RED",RED)
        stateBlue = State("BLUE",BLUE)
        stateGreen = State("GREEN",GREEN)
        self.states=(stateRed,stateBlue,stateGreen)
        #Add state to 'war states array'

        # Create the player
        self.players = pygame.sprite.Group()
        self.players.add(player)

    def process_events(self):
        """ Process all of the events. Return a "True" if we need
            to close the window. """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.isPeace =0
                if self.game_over:
                    self.__init__()
                for state in self.states:
                    self.stateExpandConflict(state)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    self.load_states()
                if event.key == pygame.K_s:
                    self.save_states()
                if event.key == pygame.K_p:
                    self.print_states()
                if event.key == pygame.K_f:
                    self.autoFight = True

        return False

    def stateExpandConflict(self,state):
        for s in self.states:
            if(state != s):
                #state.conflict(s)
                #state.conflictWithType(s,"line")
                state.conflictWithType(s,"army")
        self.stateExpandPeace(state)

    def stateExpandPeace(self,state):
        state.expand()
        self.yellowriver.stopTraffic(state)

        for s in self.states:
            if(state != s):
                state.peace(s)

    def updStateswarborderCnt(state,its_enemy):
        state.warborderCnt[its_enemy.name]  = 0;

    def run_logic(self):
        """
        This method is run each time through the frame. It
        updates positions and checks for collisions.
        """
        if(self.isPeace == 1):
            for state in self.states:
                self.stateExpandPeace(state)

        if(self.autoFight == 1):
            for state in self.states:
                self.stateExpandConflict(state)

        for state in self.states:
            for s in self.states:
                if(state != s):
                    state.updStatewarborderCnt(s)
            state.arrangeArmy()

        #if not self.game_over:
            # Move all the sprites

            # See if the player block has collided with anything.
            #blocks_hit_list = pygame.sprite.spritecollide(self.player, self.block_list, True)


    def display_frame(self, screen):
        """ Display everything to the screen for the game. """
        screen.fill(WHITE)

        if self.game_over:
            # font = pygame.font.Font("Serif", 25)
            font = pygame.font.SysFont("serif", 25)
            text = font.render("Game Over, click to restart", True, BLACK)
            center_x = (SCREEN_WIDTH // 2) - (text.get_width() // 2)
            center_y = (SCREEN_HEIGHT // 2) - (text.get_height() // 2)
            screen.blit(text, [center_x, center_y])

        if not self.game_over:
            for state in self.states:
                state.allColor()
                state.all_sprites_list.draw(screen)
                state.borderColor(BLACK)
                state.borderBlocks.draw(screen)

            self.yellowriver.block_list.draw(screen)
        self.display_player(screen)
        pygame.display.flip()

    def display_player(self,screen):
        self.players.update()
        self.players.draw(screen)


    def load_states(self):
      jsondata = {}
      jgameshot = {}
      jstates = []
      jstate = {}
      jblocks = []

      with open('save_game.json') as fp:
         jsondata = json.load(fp)
         #print(jsondata['gameshots'][0]['states'][0]['blocks'])
         fp.close()

      for state in self.states:
          state.all_sprites_list.empty()
          #state.all_sprites_list  = pygame.sprite.Group()
          state.block_list.empty()
          state.borderBlocks.empty()

      for jstate in jsondata['gameshots'][0]['states']:
        jname = jstate['name']
        #print("JState jname is ",jname)
        for state in self.states:
            #print("Load State color ",state.colour)
            if(jname == state.name):
               #print("State name is ",state.name)
               print("Load State color ",state.name)
               for rect in jstate['blocks']:
                  state.addBlock(rect[0],rect[1])

               state.selBorder()


    """
    {
        "gameshots":
        [
            {
                "states":
                [
                        {
                            "name":"RED",
                            "blocks":
                            [
                                topleft1,
                                topleft2,
                            ]
                        }
                        {
                            "name":"Blue",
                            "blocks":
                            [
                                topleft1,
                                topleft2,
                            ]
                        }
                ]
            }
            {
                "states":
                ...
            }
        ]
    }
    """
    def save_states(self):
      print('Saving')
      jsondata = {}
      jgameshots = []
      jgameshot = {}
      jstates = []
      jstate = {}
      jblocks = []

      for state in self.states:
          print("Save state ",state.name)
          jstate = {}
          jstate['name'] = state.name
          jblocks = []
          for block in state.all_sprites_list :
              jblocks.append(block.rect.topleft)
          jstate['blocks'] = jblocks
          jstates.append(jstate)


      jgameshot['states'] = jstates
      jgameshots.append(jgameshot)
      jsondata['gameshots'] = jgameshots
      with open('save_game.json', 'w') as fp:
          json.dump(jsondata, fp)
          fp.close()


    def print_states(self):
      for state in self.states:
          print("Print state ",state.name)
          print("power is %(c)s"%{"c":state.power})
          for enemy in self.states:
              print("border count to state %(n)s is %(c)s"%{"n":enemy.name,"c":state.warborderCnt[enemy.name]})
              print("army to state %(n)s is %(c)s"%{"n":enemy.name,"c":state.army[enemy.name]})


def main():
    """ Main program function. """
    # Initialize Pygame and set up the window
    statesDisplayFreq = 0 # mod 5
    pygame.init()

    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("My Game")
    pygame.mouse.set_visible(False)

    # Create our objects and set the data
    done = False
    clock = pygame.time.Clock()

    game = Game()

    # Main game loop
    while not done:
      #if(statesDisplayFreq%5 ==0 ):
        # Process events (keystrokes, mouse clicks, etc)
        done = game.process_events()
        # Update object positions, check for collisions
        game.run_logic()
        # Draw the current frame
        game.display_frame(screen)
        #game.show_1_frame(frameID)
      #statesDisplayFreq +=1
      # Pause for the next frame
        clock.tick(2)


    # Close window and exit
    pygame.quit()

# Call the main function, start up the game
if __name__ == "__main__":
    main()