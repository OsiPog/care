import pygame, math, time, numpy, random, sys

SCREEN_RES = (1280, 720)
WINDOW_RES = (1920, 1080)
FRAMERATE = 60

PATH_LEVEL = "assets/levels/"
PATH_SPRITE = "assets/sprites/"
#PATH_MUSIC = "assets/music/"
PATH_SOUNDS = "assets/sounds/"


#necessary functions
def init():
    global screen, window, overlay, clock, _mouseState, font_textBox_small, font_textBox_big
    pygame.init()
    pygame.mixer.pre_init(44100, 16, 2, 4096)
    pygame.mixer.init()
    pygame.font.init()

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(SCREEN_RES)
    pygame.display.set_caption("Care")
    
    _mouseState = list(pygame.mouse.get_pressed(5))

    overlay = pygame.Surface(SCREEN_RES, pygame.SRCALPHA)
    font_textBox_small = pygame.font.Font("assets/fonts/Pixellari.ttf",30)
    font_textBox_big = pygame.font.Font("assets/fonts/ModernDOS8x8.ttf",40)

    update()

#@profile
def update():
    global overlay, screen, mousePos, mouseButtons, _mouseState


    mousePos = list(pygame.mouse.get_pos())
    
    mouseButtons = [False, False, False, False, False]
    mouse = list(pygame.mouse.get_pressed(5))
    for i,button in enumerate(mouse):
        if button:
            if not _mouseState[i]:
                mouseButtons[i] = True
                _mouseState[i] = True
        else:
            _mouseState[i] = False


    for camera in Camera.instances:
        camera.update()

    for timer in Timer.instances:
        timer.update()

    try:
        if Player: drawUI()
    except NameError:
        pass

    for box in Textbox.instances:
        box.update()



    screen.blit(overlay, [0,0])
    #window.blit(pygame.transform.scale(screen, WINDOW_RES), [0,0])
    #update frame, clearing screen and setting tickrate

    pygame.display.update()
    clock.tick(FRAMERATE)

    screen.fill([0,0,0]) #resetting the screen surface
    overlay = pygame.Surface(SCREEN_RES, pygame.SRCALPHA)

    pygame.event.pump()


    for event in pygame.event.get():
    #exit game
        if event.type == pygame.QUIT:
            Textbox(["Are you sure you want to close the Game?", "Your progress will be lost!"], sys.exit, ignoreAnim=True)













#utility functions/classes

def mathWithStr(one, operator, two):
    if operator == "+":
        return one + two
    if operator == "-":
        return one - two
    if operator == "*":
        return one * two
    if operator == "/":
        return one / two

def listOp(first, operation, second, toRound=False, roundNDigit=None):
    result = []
    if type(second) is list:

        #throwing an exception if the given arrays are not the same size
        if len(first) != len(second):
            raise Exception("The two arrays are not the same size ({} != {})".format(len(first),len(second)))

        #does the given operation for every element with the same index
        for i in range( len(first) ):
            result.append(mathWithStr(first[i], operation, second[i]))

    else:
        #same as above but "second" is always there
        for i in range( len(first) ):
            result.append(mathWithStr(first[i], operation, second))

    if toRound:
        for i,element in enumerate(result):
            if roundNDigit == None:
                result[i] = round(element)
            else:
                result[i] = round(element, roundNDigit)

    return result


def posOnLine(one, two, perc):
    result = []
    if type(one) is list:
        for i in range(len(one)): #for both coordinates, x and y
            result.append(two[i] + (one[i] - two[i])*perc) #subtract the two numbers to get the line length, multiply that by a number between 0 and 1, add the second number again
    else: result = two + (one - two)*perc
    return result

def linearSearch(item, list, onlyFirst=True, convToStr=False): #returns index
    if convToStr:
        strList = list.copy()
        for i,element in enumerate(strList):
            strList[i] = str(element)

        list = strList
        item = str(item)

    result = []
    for i in range(len(list)):
        if list[i] == item:
            if onlyFirst: return i
            result.append(i)

def forwardVec(angle):
    rad = math.radians(angle)
    return [math.cos(rad), math.sin(rad)]

def angleFromForward(forward):
    return math.degrees(math.atan2(forward[0], forward[1]))

def toUnitVec(vec):
    magnitude = math.sqrt(vec[0]**2 + vec[1]**2)
    return listOp(vec, "/", magnitude)

def inBounds(bounds, number):
    if bounds[0] < bounds[1]:
        return not ((number < bounds[0]) or (bounds[1] < number))
    if bounds[0] > bounds[1]:
        return not ((number > bounds[0]) or (bounds[1] > number))
    if bounds[0] == bounds[1]:
        return number == bounds[0]
    return True

def pointInRect(start, end, point):
    return inBounds([start[0], end[0]], point[0]) and inBounds([start[1], end[1]], point[1])

def distance2D(start,destination): 

    a = start[0] - destination[0]
    b = destination[1] - start[1]

    return math.sqrt( a**2 + b**2 ) #pythagoras ma boi

def rectRect(start1, size1, start2, size2):

    # are the sides of one rectangle touching the other?

    return start1[0] + size1[0] >= start2[0] and start1[0] <= start2[0] + size2[0] and start1[1] + size1[1] >= start2[1] and start1[1] <= start2[1] + size2[1] 

def drawTile(tile, color=[255,0,0], width=None):
    screenPos = MainCam.toScreenPos(tile, False)
    if width == None:
        tile = pygame.Surface([MainCam.onScreen_tilesize, MainCam.onScreen_tilesize])
        tile.fill(color)
        tile.set_alpha(100)
        screen.blit(tile, screenPos)
    else:
        pygame.draw.rect(screen, color, [screenPos[0], screenPos[1], MainCam.onScreen_tilesize, MainCam.onScreen_tilesize], width)


def playSound(file):
    sound = pygame.mixer.Sound(PATH_SOUNDS + file)
    sound.play()








class Timer:
    instances = [] #list to keep track of all instances
    
    def __init__(self, function, speed=1, multiplier=100):

        self.speed = speed
        self.function = function
        self.multiplier = multiplier

        self._oldTimer = 0
        self._mod = 0

        Timer.instances.append(self)

    def update(self):
        if self.speed == 1:
            self.function()
            return

        currentMod = round(time.time()*self.multiplier) % self.speed #calculating the current mod of the time (times multiplier) and the timer speed
        if self._mod >= currentMod: #if this mod was 0 or surpassed it
            self.function()

        self._mod = currentMod #setting the mod




class Animation:

    def __init__(self, surface, frame_size, speed=1):

        #getting animation frames
        self.animations = []

        for y in range(round(surface.get_height()/frame_size[1])): #every line of sprites in an animation file is an animation
            animation = []

            for x in range(round(surface.get_width()/frame_size[0])): #every sprite in an animation is an animation frame

                #cropping the tile
                cropped = pygame.Surface(frame_size, pygame.SRCALPHA)
                cropped.blit(surface, [0, 0], [x*frame_size[0], y*frame_size[1], x*frame_size[0] + frame_size[0], y*frame_size[1] + frame_size[1]]) # start x, start y; end x, end y
                    
                if not numpy.any(pygame.surfarray.pixels_alpha(cropped) != 0): #checking the whole frame if every pixel is alpha 0 ,thanks numpy
                    break
                    
                else:

                    animation.append(cropped)

            self.animations.append(animation)


        self.timer = Timer(self.nextFrame, speed)

        self.selectedAnimation = 0
        self._currentFrame = 0 #current frame in the selected animation


        self.getCurrentFrame()






    def getCurrentFrame(self):
        if self._currentFrame >= len(self.animations[self.selectedAnimation]): #if the animation frame is non existent then just revert the variable back to 0
            self._currentFrame = 0
        return self.animations[self.selectedAnimation][self._currentFrame] #returning the current frame


    #function which gets called by the timer class
    def nextFrame(self):
        self._currentFrame += 1




















#everything level classes
class Level:
    
    instances = []

    COLL_WALK = (0,255,0)
    COLL_DRIVE = (0,0,255)
    COLL_ALL = (255,255,0)
    COLL_BARRIER = (255,0,0)

    def __init__(self, tileSize, size, chunkSize, tileData, boundaries=None):
        if not (size % chunkSize == 0): raise Exception("size is not divisable by chunksize")
        self.tileSize = tileSize
        self.size = size
        self.chunkSize = chunkSize
        self.chunkAmount = int(size / chunkSize)
        self.middle = int(self.size/2)
        self.boundaries = boundaries
        
        self.tileData = tileData #stores things like events, teleport tiles, different animation
        if self.tileData == {}:
            self.tileData = {"name": "undefined"}


        self.layers = []

        Level.instances.append(self)

        if self.boundaries == None:
            self.boundaries = [0,0,size,size]



    def addCollisionMap(self, coll_file):
        coll = pygame.image.load(PATH_LEVEL + coll_file).convert_alpha()
        if not (coll.get_width() == self.size*self.tileSize): raise Exception("collisionMap's size doesn't match levels size")
        self.collisionMap = coll


    def getCollision(self, entity, position, reverse=False): #reverse means return every tile which isn't from the color
        collisions = []
        
        for otherEntity in entity.level.layers[entity.level.entityLayerIndex]:

            if isinstance(otherEntity, Level.Particle): continue
            if otherEntity is entity: continue


            if distance2D(otherEntity.position, position) < 10:
                collWithEnt = entity.collidingWithEnt(position, otherEntity)
                for coll in collWithEnt:
                    if reverse: collisions.append(coll)
        
        #looping hitbox size times
        for y in range(entity.hitbox[1]):
            for x in range(entity.hitbox[0]):

                tile = [round(position[0] + entity.hitboxOffset[0] + x), round(position[1] + entity.hitboxOffset[1] + y)]
                try:
                    if (self.collisionMap.get_at(listOp(tile, "*", self.tileSize)) in entity.allowedColl):

                        if not reverse: collisions.append(tile)

                    elif reverse:
                        collisions.append(tile)
                except IndexError:
                    collisions.append(tile)


        for collision in collisions:
            #drawTile(collision, [255,0,0],2)
            pass

        return collisions



    def addLayer(self, tile_file):
        tileMap = pygame.image.load(PATH_LEVEL + tile_file).convert_alpha()

        if not (tileMap.get_width() == self.size*self.tileSize): raise Exception("tileMap's size doesn't match levels size")
        

        new = Level.Layer(self, tileMap)
        self.layers.append(new)


    def addEntityLayer(self):
        self.entityLayerIndex = len(self.layers)
        self.layers.append([])


    class Layer:
        def __init__(self, level, tileMap):
            self.level = level #class
            self.tileMap = tileMap #surface

            self.chunks = []
            for y in range(self.level.chunkAmount):
                self.chunks.append([])
                for x in range(self.level.chunkAmount):
                    self.chunks[y].append(Level.Layer.Chunk(self, [x,y]))


        class Chunk:
            def __init__(self, layer, position):
                self.layer = layer
                self.position = position

                self.surface = pygame.Surface([ self.layer.level.tileSize*self.layer.level.chunkSize, 
                                                self.layer.level.tileSize*self.layer.level.chunkSize], pygame.SRCALPHA)
                self.surface.blit(self.layer.tileMap, [0,0], [  self.position[0]*self.surface.get_width(),
                                                                self.position[1]*self.surface.get_height(), 
                                                                self.position[0]*self.surface.get_width() + self.surface.get_width(),
                                                                self.position[1]*self.surface.get_height() + self.surface.get_height()])
                return
                collisionMap = self.layer.level.collisionMap.copy()
                collisionMap.set_alpha(100)
                self.surface.blit(collisionMap, [0,0], [  self.position[0]*self.surface.get_width(),
                                                                self.position[1]*self.surface.get_height(), 
                                                                self.position[0]*self.surface.get_width() + self.surface.get_width(),
                                                                self.position[1]*self.surface.get_height() + self.surface.get_height()])




    class Particle:

        def __init__(self, level, surface, size, pos, direction=[0,0], flySpeed=0.2, fadeSpeed=5, animation=None) -> None:
            self.level = level
            self.size = size.copy()
            self.surface = surface.copy()
            self.position = pos.copy()
            self.direction = direction.copy()
            self.flySpeed = flySpeed
            self.fadeSpeed = fadeSpeed

            self.level.layers[self.level.entityLayerIndex].append(self)

            self.timer = Timer(self.update)

            self.animation = animation

            self.dontSort = True

        def update(self):
            if self.animation != None:
                self.surface = self.animation.getCurrentFrame()

            self.position = listOp(self.position, "+", listOp(self.direction, "*", self.flySpeed))


            self.surface.set_alpha(self.surface.get_alpha() - self.fadeSpeed)

            if self.surface.get_alpha() == 0:

                #linear searching through the entity list and timer list, converting memory adresses to str becuase I don't know why it doesn't work
                Timer.instances.pop(linearSearch(self.timer, Timer.instances, True, True))
                self.level.layers[self.level.entityLayerIndex].pop(linearSearch(self, self.level.layers[self.level.entityLayerIndex], True, True))
                
                del self


        def group(level, surface, size, pos, direction, flySpeed, fadeSpeed, sizeRange, posRange, dirAngleRange, fadeSpeedRange, amount):
                dirAngle = angleFromForward(direction)
                
                for _ in range(amount):

                    indvSize = [0,0] 
                    indvSize[0] = round(random.uniform(size[0] - sizeRange/2, size[0] + sizeRange/2),2)
                    indvSize[1] = round(random.uniform(size[1] - sizeRange/2, size[1] + sizeRange/2),2)

                    indvPos = [0,0]
                    indvPos[0] = round(random.uniform(pos[0] - posRange/2, pos[0] + posRange/2),2)
                    indvPos[1] = round(random.uniform(pos[1] - posRange/2, pos[1] + posRange/2),2)
                    
                    indvDirection = forwardVec(round(random.uniform(dirAngle - dirAngleRange/2, dirAngle + dirAngleRange/2)))

                    indvFade = round(random.uniform(fadeSpeed - fadeSpeedRange/2, fadeSpeed + fadeSpeedRange/2))
                    #print(indvDirection)

                    Level.Particle(level, surface, indvSize, indvPos, indvDirection, flySpeed, indvFade)




    class Entity:
        
        #animation indexes
        ROT_RIGHT = 0
        ROT_UP = 1
        ROT_LEFT = 2
        ROT_DOWN = 3

        ANIMTYPE_CHAR = "char"
        CHAR_IDLE=[0,1,2,3]
        CHAR_SLEEP=[4,5,6,7]
        CHAR_RUN=[8,9,10,11]
        CHAR_SIT=[13,13,12,12]
        CHAR_COFFEE = [14,14,14,14]
        CHAR_SLEEP = [15,15,15,15]

        ANIMTYPE_CAR = "car"
        CAR_FREEZE=[0,2,1,3]
        CAR_IDLE=[4,6,5,7]
        CAR_DRIVE=[8,10,9,11]

        ANIMTYPE_TRAFFIC = "traffic"
        TRAFFIC_IDLE = [0,0,0,0]

        ALL_DIRECTIONS = [
            [1,0],
            [0,1],
            [-1,0],
            [0,-1]
        ]


        def __init__(self, level, sprite_file, size, position, animType, hitboxChange=None, allowedColl=None):
            sprites = pygame.image.load(PATH_SPRITE + sprite_file).convert_alpha()
            
            self.hitboxChange = hitboxChange

            if self.hitboxChange == None:
                self.hitboxChange = dict()
                self.hitboxChange["default"] = [size, [0,0]]
            

            self.level = level #level where it's located
            self.position = position #position in level
            self.walkGoal = position #position goal where to walk
            self.size = size #size in tiles
            self.animType = animType #animation type: "char","car",etc
            self.walkSpeed = 0.1
            self.baseSprintSpeed = 0.15
            self.baseWalkSpeed = 0.05
            self.baseExhaustSpeed = 0.04
            self.walking = False
            self.animFreeze = False
            self.dontSort = False
            self.onClickIgnoreDst = False
            self.justGotExhausted=False
            self.interactionDst = 3
            self.moveLock = []
            self.allowedColl = allowedColl
            if self.allowedColl == None: self.allowedColl = [Level.COLL_WALK, Level.COLL_ALL, Level.COLL_DRIVE]
            self.rotation = 0 #mostly needed for animation, 0 - 0, 1 - 90, etc
            self.animation = Animation(sprites, listOp(size,"*",self.level.tileSize), 10)
            self.timer = Timer(self.update)

            #only for player
            self.energy = 100
            self.money = 0

            level.layers[level.entityLayerIndex].append(self)
            
            self.update()

        def kill(self):
            self.level.layers[self.level.entityLayerIndex].remove(self)
            Timer.instances.remove(self.timer)


        def attachCamera(self,camera):
            camera.attachedEntity = self


        def update(self):
            self.surface = self.animation.getCurrentFrame()



            if self.rotation in self.hitboxChange:
                self.hitbox = self.hitboxChange[self.rotation][0]
                self.hitboxOffset = self.hitboxChange[self.rotation][1]
            else:
                self.hitbox = self.hitboxChange["default"][0]
                self.hitboxOffset = self.hitboxChange["default"][1]

            #walk to position
            if self.walkGoal != self.position:
                self.walking = True
                
                #stats stuff
                if self is Player: 
                    stats["walkTime"] += 1/60
                    self.energy -= 1/60

                    if not self.justGotExhausted and self.energy <= 0:
                        Textbox(["You were walking so much that you are exhausted now.", "Sleep or eat something to get your energy back"])
                        self.position = self.walkGoal
                        self.justGotExhausted=True
                    if self.energy <= 0:
                        self.energy = 0
                        self.walkSpeed = self.baseExhaustSpeed
                        self.animation.timer.speed = 20
                    else:
                        self.walkSpeed = self.baseWalkSpeed
                        self.animation.timer.speed = 10
                
                difference = listOp(self.walkGoal, "-", self.position)
    
                direction = [0,0]
                for i in range(2):
                    if difference[i] != 0:
                        if difference[i] > 0:
                            direction[i] = self.walkSpeed
                        else:
                            direction[i] = self.walkSpeed * -1
                        #break
                        
                #difference = listOp(difference, "*", self.walkSpeed)
                self.position = listOp(self.position, "+", direction, True, 2)

                if (round(self.position[0],2) == self.walkGoal[0]) and (round(self.position[1],2) == self.walkGoal[1]):

                    self.position = self.walkGoal
                    self.walking = False

            else:
                self.walking = False
                animGroup = None
                #animation
                if self.animType == Level.Entity.ANIMTYPE_CHAR: 
                    animGroup = Level.Entity.CHAR_IDLE

                if self.animType == Level.Entity.ANIMTYPE_CAR: 
                    animGroup = Level.Entity.CAR_IDLE


                if animGroup != None: self.animation.selectedAnimation = animGroup[self.rotation]


            pos_key = str(list(map(round, self.position)))
            if pos_key in self.level.tileData:
                    
                if "onStand" in self.level.tileData[pos_key]:
                    onStand = self.level.tileData[pos_key]["onStand"]

                    if "animation" in onStand:
                        try:
                            self.animation.selectedAnimation = onStand["animation"][self.animType]
                        except KeyError:
                            pass

                    if "moveLock" in onStand:
                        self.walkGoal = list(map(round, self.position))
                        self.moveLock = onStand["moveLock"]

                    if "level" in onStand:
                        self.setLevel(onStand["level"])

                    if "goto" in onStand:
                        self.goto(onStand["goto"])

                    if "fade" in onStand:
                        MainCam.fade(onStand["fade"][0], onStand["fade"][1])
                        MainCam.paused = True
                        Controller.enabled = False


            else: #resetting to default values
                self.moveLock = []



            if self.animFreeze:
                if self.animType == Level.Entity.ANIMTYPE_CAR: self.animation.selectedAnimation = Level.Entity.CAR_FREEZE[self.rotation]




            #print(self.position, listOp(self.position, "+", listOp(self.size, "+", -1)))
            if pointInRect(self.position, listOp(self.position, "+", listOp(self.size, "+", -1)), MainCam.toTilePos(mousePos, True)) and MainCam.level == self.level:
                self.onHover(self)
                if not self.onClickIgnoreDst:
                    if distance2D(Player.position, self.position) < self.interactionDst:
                        self.onClick(self,mouseButtons)
                else:
                    self.onClick(self,mouseButtons)

            else:
                self.onNoHover(self)



            self.truePosition = listOp(self.position, "+", self.hitboxOffset)


            #for tile in self.level.getCollision(self, self.position): drawTile(tile, [255,255,0],2)




        def walk(self,direction):
            #if self.walkGoal != self.position: return

            
            if direction in self.moveLock: return

            self.rotation = Level.Entity.toRot(direction)
            testGoal = listOp(direction, "+", self.position, True)
            if not self.level.getCollision(self, testGoal, True):
                self.walkGoal = testGoal

                
                #animations
                if self.animType == Level.Entity.ANIMTYPE_CHAR:
                    animGroup = Level.Entity.CHAR_RUN

                if self.animType == Level.Entity.ANIMTYPE_CAR: 
                    animGroup = Level.Entity.CAR_DRIVE

                self.animation.selectedAnimation = animGroup[self.rotation]


        def goto(self,pos):
            self.position = listOp(pos, "-", self.hitboxOffset)
            self.walkGoal = listOp(pos, "-", self.hitboxOffset)


        def setLevel(self, strLevel):
            for level in Level.instances:
                if level.tileData["name"] == strLevel:
                    newLevel = level
                    break
            for channel in musicChannels:
                if channel == strLevel:
                    musicChannels[channel].set_volume(0.2)
                else:
                    musicChannels[channel].set_volume(0)


            self.level.layers[self.level.entityLayerIndex].remove(self)
            newLevel.layers[newLevel.entityLayerIndex].append(self)
            self.level = newLevel

        def collidingWithEnt(self, position, entity):
            collisions = []

            ownTiles = []
            for y in range(self.hitbox[1]):
                for x in range(self.hitbox[0]):
                    ownTiles.append([round(position[0] + self.hitboxOffset[0] + x), round(position[1] + self.hitboxOffset[1] + y)])
            
            entTiles = []
            for y in range(entity.hitbox[1]):
                for x in range(entity.hitbox[0]):
                    entTiles.append([round(entity.position[0] + entity.hitboxOffset[0] + x), round(entity.position[1] + entity.hitboxOffset[1] + y)])

            for tile in ownTiles:
                if tile in entTiles:
                    collisions.append(tile)
            
            return collisions



        def toRot(direction):
            if direction == [1, 0]: return Level.Entity.ROT_RIGHT
            if direction == [0, -1]: return Level.Entity.ROT_UP
            if direction == [0, 1]: return Level.Entity.ROT_DOWN
            if direction == [-1, 0]: return Level.Entity.ROT_LEFT
        
        def outline(entity, color=None,width=5):
            if color == None:
                color = [0,0,0]
                if not entity.onClickIgnoreDst:
                    if distance2D(entity.position, Player.position) < entity.interactionDst:
                        color = [0, 200, 0]

            pos = MainCam.toScreenPos(entity.position, False)
            size = listOp(entity.size, "*", MainCam.onScreen_tilesize) 
            pygame.draw.rect(screen, color, [pos[0], pos[1], size[0], size[1]], width)




        def onClick(self,dummy, mouse):
            pass


        def onHover(self, dummy):
            pass


        def onNoHover(self, dummy):
            pass

        class Car:
            def __init__(self, level, sprite_file, position, startSpeed=0.1, fullSpeed=0.4, zeroHundred=0.5, brakeWay=0.5):

                self.entity = Level.Entity(level, sprite_file, [3,2], position, "car", {0:[ [3,1], [0,1] ],
                                                                                        1:[ [1,1], [1,1] ],
                                                                                        2:[ [3,1], [0,1] ],
                                                                                        3:[ [1,1], [1,1] ]}, [Level.COLL_DRIVE, Level.COLL_ALL])
                self.timer = Timer(self.update,10)
                
                self.zeroHundred = zeroHundred
                self.brakeWay = brakeWay
                self.startSpeed = startSpeed
                self.fullSpeed = fullSpeed
                self.inUse = False

                self.time = 0

                self.entity.animation.timer.speed = 50
                self.entity.onClick = self.onClick
                self.entity.onHover = Level.Entity.outline
                self.entity.onClickIgnoreDst = True

            def update(self):
                if self.inUse:
                    self.entity.animFreeze = True
                    stats["carTime"] += 0.1

                    particlePos = [0,0]
                    
                    if self.entity.rotation == 0:
                        particlePos = listOp(self.entity.position, "+", [-0.3,1])
                        direction = [0,-1]
                    if self.entity.rotation == 1:
                        particlePos = listOp(self.entity.position, "+", [1.25,1.7])
                        direction = [1,0]

                    if self.entity.rotation == 2:
                        particlePos = listOp(self.entity.position, "+", [2.7,1])
                        direction = [0,1]

                    if self.entity.rotation == 3:
                        particlePos = listOp(self.entity.position, "+", [1.25,-0.4])
                        direction = [-1,0]

                    Level.Particle.group(level_city, smoke, [0.5,0.5], particlePos, direction, 0.05, 10, 0.5, 0, 40, 5, 5)

                    if self.entity.walking:

                        if self.time == self.zeroHundred:
                            self.entity.walkSpeed = self.fullSpeed
                        self.time += 0.1
                        self.entity.animation.timer.speed = 10

                        if listOp(self.entity.walkGoal, "-", self.entity.position, True) == [0,0]:
                            self.entity.position = list(map(round, self.entity.walkGoal))

                    else:
                        self.entity.walkSpeed = self.startSpeed
                        self.entity.animation.timer.speed = 50
                        self.time = 0
                    
                else:
                    self.entity.animFreeze = True

            def use(self):
                if self.inUse:
                    if self.entity.walkSpeed == self.fullSpeed: return

                    #looking for player tiles
                    topLeft = listOp(self.entity.position, "+", [-5,-5], True)
                    bottRight = listOp(self.entity.position, "+", [5,5], True)
                    freeTiles = []

                    for y in range(topLeft[1], bottRight[1]):
                        for x in range(topLeft[0], bottRight[0]):
                            for tile in self.entity.level.getCollision(Player, [x,y], False):
                                freeTiles.append(tile)
                            
                    
                    #get closest free tile for player to spawn on
                    closest = freeTiles[0]
                    for tile in freeTiles:
                        if distance2D(tile, self.entity.position) < distance2D(closest, self.entity.position):
                            closest = tile


                    
                    Player.goto(closest)

                    Player.attachCamera(MainCam)
                    MainCam.changeScale(0.4)

                    Controller.entity = Player
                    Controller.sprint = True

                    self.inUse = False
                else:
                    Controller.entity = self.entity
                    Controller.sprint = False

                    Player.goto([0,0])

                    MainCam.goto([0,0])

                    self.entity.attachCamera(MainCam)
                    MainCam.changeScale(-0.4)
                    
                    self.inUse = True

            def onClick(self, dummy, mouse):
                if mouse[2]:
                    self.use()

class Camera:
    instances = []

    def __init__(self, level, position):
        self.level = level
        self.position = position
        self.scale = 1
        self.attachedEntity = None
        self.entityOffset = [0,0]

        self.oldPos = [0,0]

        self.paused = False
        self.hidden = False

        self.output = pygame.Surface(SCREEN_RES)
        
        self._fadeSurf = pygame.Surface(SCREEN_RES)
        self._fadeSurf.fill([0,0,0])
        self._fadeSurf.set_alpha(0)
        self._fadeSpeed = 1
        self._fadeValues = []
        self._fadeTimer = Timer(self._fading)

        Camera.instances.append(self)

        self.update()

    def update(self, onlyVar=False):

        self.onScreen_tilesize = int(self.level.tileSize * self.scale)
        
        if self.attachedEntity != None:
            forceGoto = False
            if self.level != self.attachedEntity.level: forceGoto = True
            self.level = self.attachedEntity.level

            self.goto(listOp(self.attachedEntity.position, "+", listOp(self.attachedEntity.hitboxOffset, "+", self.entityOffset)), forceGoto)



        topLeft = self.toTilePos((0,0), True)
        bottRight = self.toTilePos(SCREEN_RES, True)
        extendTopLeft = listOp(topLeft, "+", -10) 
        extendBottRight = listOp(bottRight, "+", 10) 


        if onlyVar: return


        if not self.paused:

            self.output.fill([0,0,0])


            for layer in self.level.layers:
                


                if (layer == self.level.layers[self.level.entityLayerIndex]):

                    #sort entities after y value, so that no weird overlappings happen
                    unsortedEntities = []
                    dontSort = []

                    for entity in layer:
                        if pointInRect(extendTopLeft, extendBottRight, entity.position):
                            if entity.dontSort:
                                dontSort.append(entity)
                                continue

                            unsortedEntities.append(entity)

                    #actual sorting
                    sortedEntities = []
                    for entity in unsortedEntities:
                        if len(sortedEntities) == 0:
                            sortedEntities.append(entity)
                            continue
                        
                        for i in range(len(sortedEntities)):
                            if entity.position[1] < sortedEntities[i].position[1]:
                                sortedEntities.insert(i, entity)
                            else:
                                sortedEntities.insert(i-1, entity)


                    dontSort.extend(sortedEntities)
                    for entity in dontSort:
                        surf = entity.surface
                        surf = pygame.transform.scale(surf, listOp(entity.size, "*", self.onScreen_tilesize, True))
                        self.output.blit(surf, self.toScreenPos(entity.position,False))
                    continue



                for y in range(topLeft[1],bottRight[1] + self.level.chunkSize, self.level.chunkSize):
                    if y < 0: continue

                    for x in range(topLeft[0],bottRight[0] + self.level.chunkSize, self.level.chunkSize):
                        if x < 0: continue

                        pos = [math.floor(x / self.level.chunkSize), math.floor(y / self.level.chunkSize)]

                        try:
                            chunk = layer.chunks[pos[1]][pos[0]].surface
                        except IndexError:
                            continue
                        
                        scaled_chunk = pygame.transform.scale(chunk,[self.onScreen_tilesize * self.level.chunkSize, self.onScreen_tilesize * self.level.chunkSize])

                        self.output.blit(scaled_chunk,(self.toScreenPos(listOp(pos, "*", self.level.chunkSize), False)))
            
            #tileData
            for y in range(topLeft[1]-1,bottRight[1]+1):
                for x in range(topLeft[0]-1,bottRight[0]+1):
                    pos_key = str([x, y])
                    if pos_key in self.level.tileData:
                        tileData = self.level.tileData[pos_key]

                        if self.toTilePos(mousePos, True) == [x,y]:
                            if "onHover" in tileData:
                                onHover = tileData["onHover"]

                                if "outline" in onHover:
                                    outline = onHover["outline"]
                                    pos = self.toScreenPos([outline["rect"][0], outline["rect"][1]], False)
                                    size = listOp([outline["rect"][2], outline["rect"][3]], "*", self.onScreen_tilesize)
                                    pygame.draw.rect(self.output, outline["color"], [pos[0], pos[1], size[0], size[1]], outline["width"])

                                    if distance2D([x,y], Player.position) <= Player.interactionDst:
                                        pygame.draw.rect(self.output, outline["colorInDst"], [pos[0], pos[1], size[0], size[1]], outline["width"])
                            #print(distance2D([x,y], Player.truePosition))
                            if ("onClick2" in tileData) and (mouseButtons[2]) and (distance2D([x,y], Player.position) <= Player.interactionDst):
                                onClick = tileData["onClick2"]
                                if "level" in onClick:
                                    Player.setLevel(onClick["level"])
                                
                                if "goto" in onClick:
                                    Player.goto(onClick["goto"])

                                if "fade" in onClick:
                                    self.fade(onClick["fade"][0], onClick["fade"][1])
                                    self.paused = True

                                if "script" in onClick:
                                    onClick["script"]()
        

        if not self.hidden:
            if not self._fadeSurf.get_alpha() == 255: screen.blit(self.output, [0,0])

            if not self._fadeSurf.get_alpha() == 0:   screen.blit(self._fadeSurf, [0,0])



    def fade(self,speed=1,values=[255,0]):
        self._fadeSpeed = speed
        self._fadeValues = values.copy()



    def _fading(self):
        if len(self._fadeValues) > 0:
            currentAlph = self._fadeSurf.get_alpha() 


            #if a goal in the list is reached
            if currentAlph == self._fadeValues[0]:
                self._fadeValues.pop(0)

                self.paused = False
                Controller.enabled = True
                return

            self.paused = True
            Controller.enabled = False
            
            if currentAlph < self._fadeValues[0]:
                self._fadeSurf.set_alpha(currentAlph + self._fadeSpeed)

            if currentAlph > self._fadeValues[0]:
                self._fadeSurf.set_alpha(currentAlph - self._fadeSpeed)


    def toTilePos(self, screenPos, roundIt=False):
        tilePos = [0,0]
        tilePos[0] = (screenPos[0] - self.position[0])/self.onScreen_tilesize + self.level.middle
        tilePos[1] = (screenPos[1] - self.position[1])/self.onScreen_tilesize + self.level.middle

        if roundIt:
            tilePos[0] = round(tilePos[0])
            tilePos[1] = round(tilePos[1])

        return tilePos


    def toScreenPos(self, tilePos, trueConvert=True):
        screenPos = [0,0]
        screenPos[0] = (tilePos[0] - self.level.middle) * self.onScreen_tilesize + self.position[0]
        screenPos[1] = (tilePos[1] - self.level.middle) * self.onScreen_tilesize + self.position[1]

        if not trueConvert:
            screenPos[0] -= self.onScreen_tilesize/2
            screenPos[1] -= self.onScreen_tilesize/2

        return screenPos



    def goto(self, point, force=False): #point in tiles

        currentMiddle = listOp(SCREEN_RES, "/", 2)                    #converting both to screen positions
        screenPoint = self.toScreenPos(point, True)


        difference = listOp(currentMiddle, "-", screenPoint) #difference between the middle and the goal position

        prevPos = self.position.copy()
        self.position = listOp(difference, "+", self.position) #adding this difference to the camera position


    def changeScale(self, direction, zoomTo=None):
        if zoomTo == None:
            zoomTo = self.toTilePos(listOp(SCREEN_RES, "/", 2))

        self.scale += direction

        if self.scale < 0.05:
            self.scale = 0.05

        self.update(onlyVar=True)
        self.goto(zoomTo) #previous tile in the middle






class EntityController:
    default_controls = {
        
        "move":{
            "up": pygame.K_w,
            "down": pygame.K_s,
            "left": pygame.K_a,
            "right": pygame.K_d,
            "sprint": pygame.K_LSHIFT,
        },
        "fly":{
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
        }
    }

    def __init__(self, entity, controls=None, sprint=False, fly=False, enabled=True):
        if controls == None:
            self.contr = EntityController.default_controls
        else:
            self.contr = controls
    
        self.entity = entity
        self.fly = False
        self.sprint = sprint
        self.enabled = enabled

        self.timer = Timer(self.update)

    def update(self):

        keyboard = pygame.key.get_pressed()

        if self.enabled:
            if keyboard[self.contr["move"]["left"] ]: self.entity.walk([-1,0])
            if keyboard[self.contr["move"]["right"] ]: self.entity.walk([1,0])
            if keyboard[self.contr["move"]["up"] ]: self.entity.walk([0,-1])
            if keyboard[self.contr["move"]["down"] ]: self.entity.walk([0,1])

        if self.fly:
            if keyboard[self.contr["fly"]["up"] ]: self.entity.goto(listOp(self.entity.truePosition, "+", [0,-1]))
            if keyboard[self.contr["fly"]["down"] ]: self.entity.goto(listOp(self.entity.truePosition, "+", [0,1]))
            if keyboard[self.contr["fly"]["left"] ]: self.entity.goto(listOp(self.entity.truePosition, "+", [-1,0]))
            if keyboard[self.contr["fly"]["right"] ]: self.entity.goto(listOp(self.entity.truePosition, "+", [1,0]))



class Textbox:

    instances = []

    def __init__(self, text=[""], cond=None, pos=None, color=[50,50,50], centered=False, font=None, surf=None, offset=[0,0], instaRemove=False, ignoreAnim=False):

        Textbox.instances.append(self)
        self.toRemove = False
        self.ignoreAnim = ignoreAnim
        self.fadeSpeed = 20
        self.cond = cond
        self.instaRemove = instaRemove
        self.createTime = time.time()

        if pos == None:
            self.position = listOp(SCREEN_RES, "/", 2)
            
            self.rendered = text_box_big.copy()
            self.rendered.set_alpha(0)
            font = font_textBox_small

            if self.cond != None:
                yesNo = text_box_small.copy()

                yes = font.render("Yes", False, [50,50,50])
                no = font.render("No", False, [50,50,50])

                yesNo.blit(yes, [74 - yes.get_width()/2 ,28 +23 - yes.get_height()/2])
                yesNo.blit(no, [74 - no.get_width()/2 ,28+46 +23 - no.get_height()/2])

                self.rendered.blit(yesNo, [926, 411])





            for i,tLine in enumerate(text):
                line = font.render(tLine, False, [50,50,50])
                newOffset = [0, i*(font.get_height() + 10)]
                self.rendered.blit(line, listOp([240, 600], "+", newOffset, True))

            if not instaRemove:
                try: Controller.enabled = False
                except: pass
            return

        if font == None:
            font = font_textBox_small
        if surf == None:
            surf = text_box_small.copy()

        self.text = text
        self.position = pos
        self.rendered = surf.copy()
        self.rendered.set_alpha(0)

        lines = []
        for i,line in enumerate(text):
            lines.append(font.render(line, False, color))

        if centered:
            for i,line in enumerate(lines):
                newOffset = [offset[0], i*font.get_height() + offset[1]]
                middle = listOp(self.rendered.get_size(), "/", 2)
                middleLine = listOp(line.get_size(), "/", 2)
                self.rendered.blit(line, listOp(listOp(middle, "-", middleLine), "+", newOffset, True))





    def update(self):
        if animPlaying and not self.ignoreAnim:
            self.kill()

        currentAlph = self.rendered.get_alpha()
        if (currentAlph != 255) and not self.toRemove:
            self.rendered.set_alpha(currentAlph + self.fadeSpeed)
        elif self.instaRemove:
            if time.time() - self.createTime >= 1:
                self.toRemove = True


        screen.blit(self.rendered, listOp(self.position, "-", listOp(self.rendered.get_size(), "/", 2), True))
        
        
        if self.cond != None:
            if pointInRect([926,411+28], [96+926,46+411+28], mousePos): #yes
                pygame.draw.rect(screen, [0,0,0], [926+28,411+28,96,46], 5)
                if mouseButtons[0]:
                    self.cond()
                    self.toRemove = True
                    try: Controller.enabled = True
                    except: pass


            if pointInRect([926,411+28+46], [96+926,46+411+28+46], mousePos): #no
                pygame.draw.rect(screen, [0,0,0], [926+28, 411+28+46, 96, 46], 5)
                if mouseButtons[0]:
                    self.toRemove = True
                    try: Controller.enabled = True
                    except: pass

        else:
            if mouseButtons[0]:
                try: Controller.enabled = True
                except: pass
                self.toRemove = True

        if self.toRemove: self.kill()


    def kill(self, force=False):
        currentAlph = self.rendered.get_alpha()
        self.rendered.set_alpha(currentAlph - self.fadeSpeed)
        if currentAlph == 0 or force: 
            Textbox.instances.remove(self)




class Arrow:
    def __init__(self, posOrEnt, level=None, icon=None, hideInRange=False):
        self.posOrEnt = posOrEnt
        self.icon = icon
        self.level = level
        self.iconDst = 64
        self.hideInRange = hideInRange

        self.timer = Timer(self.update)

    def update(self):
        if isinstance(self.posOrEnt, Level.Entity):
            position = self.posOrEnt.truePosition
            level = self.posOrEnt.level
        else:
            position = self.posOrEnt
            level = self.level
        
        if level == MainCam.level and not MainCam.paused and not MainCam.hidden and not animPlaying:
            topLeft = MainCam.toTilePos([0,0])
            bottRight = MainCam.toTilePos(SCREEN_RES)
            middle = MainCam.toTilePos(listOp(SCREEN_RES, "/", 2))

            if not pointInRect(topLeft, bottRight, position):
                difference = listOp(position, "-", middle)
                
                unitvec = toUnitVec(difference)
                
                normalized = listOp(listOp(unitvec, "+", 1), "/", 2)
                
                angle = angleFromForward(unitvec)

                
                screenPos = listOp(listOp(SCREEN_RES, "-", 50), "*", normalized)
                screenPos = listOp(screenPos, "+", 25)


                #if angle >= 180: angle = abs(180 - angle) +180
                inRange = False

            else:
                angle = 0
                screenPos = MainCam.toScreenPos(listOp(position, "+", [0,-1]))
                inRange = True



            rotated = pygame.transform.rotate(arrow, angle-90)

            if self.icon != None:
                rotated.blit(self.icon, listOp(listOp(rotated.get_size(), "/", 2, True), "-", listOp(self.icon.get_size(), "/", 2, True)))

            if (inRange and not self.hideInRange) or not inRange:
                screen.blit(rotated, listOp(screenPos, "-", listOp(rotated.get_size(), "/", 2, True)))



















stats = dict()
stats["carTime"] = 0
stats["walkTime"] = 0
stats["wrongBin"] = 0
stats["rightBin"] = 0
stats["garbagePickedUp"] = 0
stats["garbageIgnored"] = 0



day = 0
binPrize = 20
fruitsPrize = 5
worked = False
inventory = [0,0,0,0]
animPlaying = False
salary = 15













def drawUI():
    if not animPlaying and not MainCam.paused and not MainCam.hidden:
        screen.blit(ui, [0,0])

        pygame.draw.rect(screen, [255,200,0], [1135, 31, round(103*(Player.energy/100)), 31])
        screen.blit(bolts, [1135, 31])

        for i,amount in enumerate(inventory):
            text = font_textBox_small.render(str(round(amount)), False, [50,50,50])
            screen.blit(text, [1230 - text.get_width()/2,130 + i*64])


        money = font_textBox_small.render("$" + str(Player.money), False, [50,150,50])
        screen.blit(money, [1012 - money.get_width()/2, 49 - money.get_height()/2])



def work():
    global worked
    if not worked:

            worked = True

            fadeSpeed = 5
            scale = 3
            values = [255]
            duration = 1

            
            MainCam.fade(fadeSpeed, values.copy())
            




            fontRendered = font_textBox_big.render("$" + str(Player.money), False, [0,200,0])
            fontRendered = pygame.transform.scale(fontRendered, [fontRendered.get_width()*scale, fontRendered.get_height()*scale])
            pos = listOp(listOp(SCREEN_RES, "/", 2), "-",listOp(fontRendered.get_size(), "/", 2))
            fontRendered.set_alpha(0)
            currentAlph = fontRendered.get_alpha()


            while True:
                update()
                if len(MainCam._fadeValues) == 0: break

            MainCam.hidden = True
            values = [255, 0]
            prevMon = Player.money
            while True:
                update()
                screen.fill([0,0,0])
                screen.blit(fontRendered, pos)
                
                if len(values) > 0:
                    currentAlph = fontRendered.get_alpha()
                    if currentAlph == None: currentAlph = 255

                    if currentAlph < values[0]:
                        fontRendered.set_alpha(currentAlph + 5)
                    if currentAlph > values[0]:
                        fontRendered.set_alpha(currentAlph - 5)

                    
                    if currentAlph == values[0]:
                        if round(duration,2) == 0:
                            while True:
                                update()
                                if Player.money == prevMon + salary: break
                                Player.money += 1
                                screen.fill([0,0,0])
                                screen.blit(fontRendered, pos)
                                fontRendered = font_textBox_big.render("$" + str(Player.money), False, [0,200,0])
                                fontRendered = pygame.transform.scale(fontRendered, [fontRendered.get_width()*scale, fontRendered.get_height()*scale])
                                pos = listOp(listOp(SCREEN_RES, "/", 2), "-",listOp(fontRendered.get_size(), "/", 2))



                            values.pop(0)
                            duration = 1
                            continue
                        duration -= 1/60

                else:
                    break
            
            MainCam.hidden = False
            values = [0]
            MainCam.fade(fadeSpeed, values.copy())
            while True:
                update()
                if len(MainCam._fadeValues) == 0: break

    else:
        Textbox(["You did your work for today already.", "Come back tomorrow!"])
















TILEDAT_TEMPL = dict()
TILEDAT_TEMPL["sit_left"] = {

    "onStand": {
            "animation": {
                Level.Entity.ANIMTYPE_CHAR: 12 #sit left facing
            },
            "moveLock": [ [1,0], [0,1], [0,-1] ]
    }
}
TILEDAT_TEMPL["sleep"] = {

    "onClick": {

    }
}
TILEDAT_TEMPL["TP_pHouse_city_0"] = {

    "onStand": {
        "fade": [10, [255,0]],
        "goto": [11, 60],
        "level": "city"
    }
}
TILEDAT_TEMPL["TP_pHouse_city_1"] = {

    "onStand": {
        "fade": [10, [255,0]],
        "goto": [12, 60],
        "level": "city"
    }
}
TILEDAT_TEMPL["TP_city_pHouse_0"] = {

    "onClick2": {
        "fade": [10, [255,0]],
        "goto": [51, 76],
        "level": "pHouse",
    },
    "onHover": {
        "outline": {
            "color": [0,0,0],
            "colorInDst": [0,200,0],
            "rect": [11, 58, 2, 2],
            "width": 5
        }
    }
}


TILEDAT_TEMPL["TP_market_city"] = {

    "onStand": {
        "fade": [10, [255,0]],
        "goto": [49, 78],
        "level": "city"
    }
}
TILEDAT_TEMPL["TP_city_market"] = {

    "onClick2": {
        "fade": [10, [255,0]],
        "goto": [46, 58],
        "level": "market",
    },
    "onHover": {
        "outline": {
            "color": [0,0,0],
            "colorInDst": [0,200,0],
            "rect": [48, 76, 3, 2],
            "width": 5
        }
    }
}


TILEDAT_TEMPL["work"] = {

    "onClick2": {
        "script": work,
    },
    "onHover": {
        "outline": {
            "color": [0,0,0],
            "colorInDst": [0,200,0],
            "rect": [16, 84, 2, 2],
            "width": 5
        }
    }
}




LEVEL_CITY_DATA = {"name":"city"}
LEVEL_CITY_DATA["[11, 35]"] = TILEDAT_TEMPL["sit_left"]
LEVEL_CITY_DATA["[11, 36]"] = TILEDAT_TEMPL["sit_left"]
LEVEL_CITY_DATA["[11, 38]"] = TILEDAT_TEMPL["sit_left"]
LEVEL_CITY_DATA["[11, 39]"] = TILEDAT_TEMPL["sit_left"]

LEVEL_CITY_DATA["[12, 59]"] = TILEDAT_TEMPL["TP_city_pHouse_0"]
LEVEL_CITY_DATA["[12, 58]"] = TILEDAT_TEMPL["TP_city_pHouse_0"]
LEVEL_CITY_DATA["[11, 58]"] = TILEDAT_TEMPL["TP_city_pHouse_0"]
LEVEL_CITY_DATA["[11, 59]"] = TILEDAT_TEMPL["TP_city_pHouse_0"]

LEVEL_CITY_DATA["[48, 76]"] = TILEDAT_TEMPL["TP_city_market"]
LEVEL_CITY_DATA["[49, 76]"] = TILEDAT_TEMPL["TP_city_market"]
LEVEL_CITY_DATA["[50, 76]"] = TILEDAT_TEMPL["TP_city_market"]
LEVEL_CITY_DATA["[48, 77]"] = TILEDAT_TEMPL["TP_city_market"]
LEVEL_CITY_DATA["[49, 77]"] = TILEDAT_TEMPL["TP_city_market"]
LEVEL_CITY_DATA["[50, 77]"] = TILEDAT_TEMPL["TP_city_market"]

LEVEL_CITY_DATA["[16, 84]"] = TILEDAT_TEMPL["work"]
LEVEL_CITY_DATA["[16, 85]"] = TILEDAT_TEMPL["work"]
LEVEL_CITY_DATA["[17, 84]"] = TILEDAT_TEMPL["work"]
LEVEL_CITY_DATA["[17, 85]"] = TILEDAT_TEMPL["work"]



LEVEL_PHOUSE_DATA = {"name":"pHouse"}
LEVEL_PHOUSE_DATA["[56, 72]"] = TILEDAT_TEMPL["sleep"]
LEVEL_PHOUSE_DATA["[51, 76]"] = TILEDAT_TEMPL["TP_pHouse_city_0"]
LEVEL_PHOUSE_DATA["[52, 76]"] = TILEDAT_TEMPL["TP_pHouse_city_1"]

LEVEL_MARKET_DATA = {"name":"market"}
LEVEL_MARKET_DATA["[45, 58]"] = TILEDAT_TEMPL["TP_market_city"]
LEVEL_MARKET_DATA["[46, 58]"] = TILEDAT_TEMPL["TP_market_city"]
LEVEL_MARKET_DATA["[47, 58]"] = TILEDAT_TEMPL["TP_market_city"]



def makeMainCam(level):
    global MainCam
    try:
        if MainCam: return
    except:
        MainCam = Camera(level, [0,0])

def load_level_city():
    global level_city
    try:
        if level_city: return
    except:
        level_city = Level(16, 100, 5, LEVEL_CITY_DATA, [0,9,78,87])
        level_city.addCollisionMap("city_coll.png")
        level_city.addLayer("city_below.png")
        level_city.addEntityLayer()
        level_city.addLayer("city_above.png")


def load_level_pHouse():
    global level_pHouse
    try:
        if level_pHouse: return
    except:
        level_pHouse = Level(16, 100, 5, LEVEL_PHOUSE_DATA)
        level_pHouse.addCollisionMap("pHouse_coll.png")
        level_pHouse.addLayer("pHouse_below.png")
        level_pHouse.addEntityLayer()
        level_pHouse.addLayer("pHouse_above.png")

def load_level_market():
    global level_market
    try:
        if level_market: return
    except:
        level_market = Level(16, 100, 5, LEVEL_MARKET_DATA)
        level_market.addCollisionMap("market_coll.png")
        level_market.addLayer("market_below.png")
        level_market.addEntityLayer()
        level_market.addLayer("market_above.png")


def load():
    global MainCam, Player, Car, Controller, level_city, pBlack_bin, pBed, fruits_basket, arrows, bins, musicChannels

    musicChannels = dict()
    musicChannels["pHouse"] = pygame.mixer.Channel(0)
    musicChannels["pHouse"].play(pygame.mixer.Sound(PATH_SOUNDS + "pHouse.ogg"),-1)
    musicChannels["pHouse"].set_volume(0)
    musicChannels["city"] = pygame.mixer.Channel(1)
    musicChannels["city"].play(pygame.mixer.Sound(PATH_SOUNDS + "city.ogg"),-1)
    musicChannels["city"].set_volume(0)
    musicChannels["market"] = pygame.mixer.Channel(2)
    musicChannels["market"].play(pygame.mixer.Sound(PATH_SOUNDS + "market.ogg"),-1)
    musicChannels["market"].set_volume(0)

    load_level_city()
    load_level_pHouse()
    load_level_market()


    makeMainCam(level_city)
    MainCam.scale = 3.5
    MainCam.scale = 3.5

    Player = Level.Entity(level_pHouse, "character.png", [1,2], [55,72], "char", {"default":[ [1,1], [0,1] ]}, [Level.COLL_WALK, Level.COLL_ALL ])
    Player.setLevel("pHouse")
    Player.rotation = 3
    Player.baseWalkSpeed = 0.1


    Car = Level.Entity.Car(level_city, "car.png", [4, 61])
    
    Player.attachCamera(MainCam)
    Controller = EntityController(Player, None, True, True)

    MainCam.entityOffset = [0,-2]


    #entities


    def binClick(bin,mouse):
        if mouse[2]:
            if bin.animation.selectedAnimation < 5:
                if Player.energy > 0:
                    if bin.animation.selectedAnimation == 0: kind = "plastic"
                    if bin.animation.selectedAnimation == 1: kind = "glass"
                    if bin.animation.selectedAnimation == 2: kind = "paper"
                    if bin.animation.selectedAnimation == 3: kind = "bio"
                    if bin.animation.selectedAnimation == 4: kind = "rest"

                    tb = Textbox(["Click the garbage which you want to dump into this {} bin.".format(kind), "(Select with right click)"])    
                    selected = []
                    _rects = []
                    while True:
                        update()
                        topLeft =[1140, 105]
                        size = [112, 64]
                        for i in range(4):
                            newTL = [topLeft[0], topLeft[1] + (size[1] + 1)*i]
                            rect = [newTL[0], newTL[1], size[0], size[1]]

                            if pointInRect(newTL, listOp(newTL, "+", size), mousePos):
                                if not (rect in _rects): pygame.draw.rect(overlay, [0,0,0], rect, 5)
                                
                                if mouseButtons[2]:
                                    if not (i in selected): 
                                        selected.append(i)
                                        _rects.append(rect)
                    
                        for rect in _rects:
                            pygame.draw.rect(overlay, [0,200,0], rect, 5)

                        if tb.toRemove:
                            for i in range(4):
                                newTL = [topLeft[0], topLeft[1] + (size[1] + 1)*i]
                                rect = [newTL[0], newTL[1], size[0], size[1]]

                                if pointInRect(newTL, listOp(newTL, "+", size), mousePos):
                                    selected.append(i)
                                    _rects.append(rect)
                            break
                                    

                    notZero = True
                    if len(selected) == 0: notZero = False
                    
                    while notZero:
                        update()
                        for i in selected:
                            if inventory[i] == 0: continue
                            inventory[i] -= 1
                                
                            if bin.animation.selectedAnimation == i:
                                stats["rightBin"] += 1
                            else:
                                stats["wrongBin"] += 1

                            break

                        testIfZero = []
                        for i in selected:
                            testIfZero.append(inventory[i])
                        if max(testIfZero) == 0: break

                    MainCam.update()
                else:
                    Textbox(["You are too exhausted to do anything.", "Maybe eat something or sleep a bit."])

            else:
                if Player.money >= binPrize:
                    if bin.animation.selectedAnimation == 5: 
                        binColor = "plastic"
                    if bin.animation.selectedAnimation == 6: 
                        binColor = "glass"
                    if bin.animation.selectedAnimation == 7: 
                        binColor = "paper"
                    if bin.animation.selectedAnimation == 8: 
                        binColor = "bio"
                    if bin.animation.selectedAnimation == 9: 
                        binColor = "rest"

                    def buyBin():
                        bin.animation.selectedAnimation -= 5
                        bin.goto([4 - bin.animation.selectedAnimation, 58])
                        bin.setLevel("city")

                        print(bin.level.tileData["name"])

                        Player.money -= binPrize 

                    Textbox(["Do you want to buy this {} bin for ${}?".format(binColor, binPrize)], buyBin)
                else:
                    Textbox(["You don't have enough money to buy this. (${})".format(binPrize)])


    bins = []


    black_bin = Level.Entity(level_city, "bin.png", [1,2], [7,58], "bin")
    black_bin.animation.selectedAnimation = 4
    black_bin.onClick = binClick
    black_bin.onHover = Level.Entity.outline
    bins.append(black_bin)
    for i in range(0,4):
        sale_bin = Level.Entity(level_market, "bin.png", [1,2], [50 + i,61], "bin")
        sale_bin.animation.selectedAnimation = i + 5
        sale_bin.onClick = binClick
        sale_bin.onHover = Level.Entity.outline
        bins.append(sale_bin)

    def clickFruits(entity, mouse):
        if mouse[2]:
            if Player.money >= fruitsPrize:

                def buyFruits():
                    fruits_basket.goto([0,0])
                    fruits_basket.animation.selectedAnimation = random.randint(0,2)
                    Player.energy = 100
                    Player.money -= fruitsPrize
                    


                Textbox(["Do you want to buy this basket of fruits for ${}?".format(fruitsPrize), "(Will fill your energy)"], buyFruits)
            else:
                Textbox(["You don't have enough money to buy this. (${})".format(fruitsPrize)])


    fruits_basket = Level.Entity(level_market, "fruits.png", [1,2], [59, 60], None)
    fruits_basket.onHover = Level.Entity.outline
    fruits_basket.onClick = clickFruits
    fruits_basket.animation.selectedAnimation = random.randint(0,2)


    pBed = Level.Entity(level_pHouse, "bed.png", [3,3], [56,72], "bed", {"default": [[3,2], [0,1]]})
    pBed.animation.timer.speed = 30
    pBed.onHover = Level.Entity.outline
    pBed.onClick = newDay

    #placing all of the traffic
    traffic = pygame.image.load(PATH_SPRITE + "traffic.png").convert_alpha()
    for i in range(10):
        Level.Particle(level_city, traffic, [6,6], [71,30 + i*6], [0,0], 0,0, Animation(traffic, [6*16,6*16], 4))
   
   
    #arrows
    arrows = []
    arrows.append(Arrow([49, 75], level_city, pygame.image.load("assets/market_icon.png").convert_alpha()))
    arrows.append(Arrow(Car.entity, level_city, pygame.image.load("assets/car_icon.png").convert_alpha(), True))
    arrows.append(Arrow([16.5, 83], level_city, pygame.image.load("assets/work_icon.png").convert_alpha()))
    arrows.append(Arrow([11.5, 57], level_city, pygame.image.load("assets/home_icon.png").convert_alpha()))




    update()







def playDevLogo(duration):
    initialDuration = duration
    play = True
    logo = pygame.image.load("assets/devLogo.png").convert_alpha()
    pos = listOp(listOp(SCREEN_RES, "/", 2), "-", listOp(logo.get_size(), "/", 2), True)
    logo.set_alpha(0)
    values = [0,255,0]
    currentAlph = logo.get_alpha()
    while play:
        update()
        screen.fill([0,0,0])
        screen.blit(logo, pos)
        if len(values) > 0:
            if currentAlph < values[0]:
                logo.set_alpha(currentAlph + 5)
            if currentAlph > values[0]:
                logo.set_alpha(currentAlph - 5)

            currentAlph = logo.get_alpha()
            if currentAlph == values[0]:
                if round(duration,2) == 0:
                    values.pop(0)
                    duration = initialDuration
                duration -= 1/60

        else:
            play = False
 







def menu():
    global MainCam, start, Player, Controller
    start = False
    
    level = Level(16, 100, 5, {}, [0,30,78,88])
    level.addLayer("city_below.png")
    level.addLayer("city_above.png")
    level.addEntityLayer()

    
    makeMainCam(level)
    MainCam.scale = 7.5

    black_pane = pygame.image.load(PATH_SPRITE + "black_pane.png").convert()
    black_pane.set_alpha(50)
    Level.Particle(level, black_pane, [15,10], [0,52], [0,0], 0,0)


    def leftClickStart(bin,mouse):
        global start
        if mouse[0]:
            start = True


    startBin = Level.Entity(level, "bin.png", [1,2], [4,58], "bin", {"default":[ [1,2], [0,1] ]})
    helpBin = Level.Entity(level, "bin.png", [1,2], [7,58], "bin", {"default":[ [1,2], [0,1] ]})
    
    sign = pygame.image.load("assets/text_sign.png").convert_alpha()
    sign1 = Textbox(["Start","Game"], None, [435,430], [71,52,40],True, font_textBox_big, text_box_small.copy(), [3,-10]) #[165, 63,63]
    sign2 = Textbox(["How to", "Play"], None, [795,430], [71,52,40],True, font_textBox_big, text_box_small.copy(), [0,-10])

    logo = pygame.image.load("assets/big_logo.png").convert_alpha()

    startBin.animation.selectedAnimation = 2
    startBin.onClickIgnoreDst = True
    startBin.onHover = Level.Entity.outline
    startBin.onClick = leftClickStart


    def howToPlay(dummy,mouse):
        global mouseButtons, helpbox, blitLogo
        if mouse[0]:
            blitLogo = False
            mouseButtons = [False, False, False, False, False]
            helpbox =Textbox(
                ["How to play",
                "In this game you have a normal life where you can decide if",
                "you want to care for your future or not. For example picking",
                "up garbage and putting it in the right bin (which you have to",
                "buy at first). You will have to go to work too to get money too.",
                "You will play 7 days and after the 7th day, the game will show", 
                "you how the future would look like with the lifestyle which you",
                "had. Remember that this is a pre-alpha rushed for the",
                "OLC CODE JAM 2021 so don't expect too much!"]
            
            ,surf=pygame.image.load("assets/text_box_super_big.png"), centered=True, offset=[0,60], pos=listOp(SCREEN_RES, "/", 2, True))


    helpBin.onClickIgnoreDst = True
    helpBin.onHover = Level.Entity.outline
    helpBin.animation.selectedAnimation = 2
    helpBin.onClick = howToPlay
    blitLogo = True
    
    while not start:
        sign1.toRemove = False
        sign2.toRemove = False
        update()
        if mouseButtons[2]: print(mousePos)
        if blitLogo: overlay.blit(logo, [0,0])
        MainCam.goto([5.7,57])


        screen.fill([0,0,0]) #resetting the screen surface

    try: Textbox.instances.remove(sign1)
    except: pass
    try: Textbox.instances.remove(sign2)
    except: pass
    try: Textbox.instances.remove(helpbox)
    except: pass
    MainCam.paused = True
    







def newDay(bed, mouse):
    global day, worked, animPlaying

    if mouse[2]:
        if worked or (day == 0):

            def dumpAll():
                Controller.enabled = False

                while True:
                    update()
                    for i,amount in enumerate(inventory):
                        if amount == 0: continue
                        inventory[i] = amount - 1
                        
                        stats["wrongBin"] += 1

                        break

                    if inventory == [0,0,0,0]: break
                MainCam.update()
                Controller.enabled = True
                newDay(bed, mouse=[False, False, True])

            if max(inventory) != 0: 
                Textbox(["You cannot sleep with garbage in your pockets", "Do you want to put it in your rest garbage bin?"], dumpAll)
                return

            fruits_basket.goto([59,60])
            worked = False

            animPlaying = True
            for box in Textbox.instances:
                box.kill(True)     

            pBed.animation.selectedAnimation = 1
            pBed.animation._currentFrame = 0

            Player.goto([0,0])
            MainCam.attachedEntity = None
            update()
            
            if day == 7:
                future()
                return

            fadeSpeed = 2
            scale = 2
            values = [255]
            duration = 1

            
            MainCam.fade(fadeSpeed, values.copy())
            



            day += 1

            fontRendered = font_textBox_big.render("Day " + str(day), False, [255,255,255])
            fontRendered = pygame.transform.scale(fontRendered, [fontRendered.get_width()*scale, fontRendered.get_height()*scale])
            pos = listOp(listOp(SCREEN_RES, "/", 2), "-",listOp(fontRendered.get_size(), "/", 2))
            fontRendered.set_alpha(0)
            currentAlph = fontRendered.get_alpha()


            while True:
                update()
                if len(MainCam._fadeValues) == 0: break

            MainCam.hidden = True
            values = [255, 0]
            while True:
                update()
                screen.fill([0,0,0])
                screen.blit(fontRendered, pos)
                
                if len(values) > 0:
                    currentAlph = fontRendered.get_alpha()
                    if currentAlph == None: currentAlph = 255

                    if currentAlph < values[0]:
                        fontRendered.set_alpha(currentAlph + 5)
                    if currentAlph > values[0]:
                        fontRendered.set_alpha(currentAlph - 5)

                    
                    if currentAlph == values[0]:
                        if round(duration,2) == 0:
                            values.pop(0)
                            duration = 1
                            continue
                        duration -= 1/60

                else:
                    break
            




            #level changing loading stuff
            for y in range(level_city.boundaries[1],level_city.boundaries[3]):
                for x in range(level_city.boundaries[0],level_city.boundaries[2]):
                    #if y == 0: print(listOp([x,y], "*", 16), [x,y])
                    if level_city.collisionMap.get_at(listOp([x,y], "*", 16)) in Player.allowedColl:
                        rng = random.randint(1,100)
                        if rng == 1:
                            garbage = Level.Entity(level_city, "garbage.png", [1,1], [x,y], None, {"default": [[0,0], [0,0]]})
                            #garbageSurf = pygame.image.load(PATH_SPRITE + "garbage.png")
                            #garbage = Level.Particle(level_city, garbageSurf, [1,1], [x,y], [0,0], 0, 0, Animation(garbageSurf, [16,16]))
                            garbage.dontSort = True
                            garbage.animation.selectedAnimation = random.randint(0,3)
                            
                            def collectGarbage(entity, mouse):
                                if mouse[2]:
                                    if Player.energy > 0:
                                        if entity.animation.selectedAnimation == 0: kind = "plastic"
                                        if entity.animation.selectedAnimation == 1: kind = "glass"
                                        if entity.animation.selectedAnimation == 2: kind = "paper"
                                        if entity.animation.selectedAnimation == 3: kind = "bio"
                                        Textbox(["+", kind, "garbage"], instaRemove=True, pos=[1200, 480], offset=[0,-30], centered=True)
                                        entity.kill()
                                        inventory[entity.animation.selectedAnimation] += 1
                                        
                                        stats["garbagePickedUp"] += 1
                                        stats["garbageIgnored"] -= 1
                                    else:
                                        Textbox(["You are too exhausted to do anything.", "Maybe eat something or sleep a bit."])

                            stats["garbageIgnored"] += 1
                            garbage.onHover = Level.Entity.outline
                            garbage.onClick = collectGarbage


            MainCam.hidden = False
            values = [0]
            MainCam.fade(fadeSpeed, values)

            Player.energy = 100

            while True:
                update()
                if len(MainCam._fadeValues) == 0: break

            pBed.animation.selectedAnimation = 0
            Player.goto([55,73])
            MainCam.attachedEntity = Player
            MainCam.update()
            animPlaying = False
        else:
            if not animPlaying: Textbox(["You cannot sleep yet, you need to go to work!"])



def future():
    global animPlaying
    arrows.clear()
    Car.entity.kill()
    animPlaying = True

    for entity in level_city.layers[level_city.entityLayerIndex].copy():
        if isinstance(entity, Level.Particle): level_city.layers[level_city.entityLayerIndex].remove(entity)

    MainCam.fade(2, [255])
    
    while True:
        update()
        if len(MainCam._fadeValues) == 0: break

    MainCam.attachedEntity = None
    MainCam.level = level_city


    if stats["garbagePickedUp"] == 0: possibility = 1
    else:
        possibility = stats["garbagePickedUp"]*2

    for y in range(level_city.boundaries[1],level_city.boundaries[3]):
        for x in range(level_city.boundaries[0],level_city.boundaries[2]):
            #if y == 0: print(listOp([x,y], "*", 16), [x,y])
            if level_city.collisionMap.get_at(listOp([x,y], "*", 16)) in [Level.COLL_ALL, Level.COLL_DRIVE, Level.COLL_WALK]:
                rng = random.randint(1,possibility)
                if rng == 1:
                    garbage = Level.Entity(level_city, "garbage.png", [1,1], [x,y], None, {"default": [[0,0], [0,0]]})
                    #garbageSurf = pygame.image.load(PATH_SPRITE + "garbage.png")
                    #garbage = Level.Particle(level_city, garbageSurf, [1,1], [x,y], [0,0], 0, 0, Animation(garbageSurf, [16,16]))
                    garbage.dontSort = True
                    garbage.animation.selectedAnimation = random.randint(0,3)




    if stats["rightBin"] - stats["wrongBin"] < 0:
        for bin in bins:
            pass

    pollution = pygame.image.load("assets/pollution.png").convert_alpha()

    pollution.set_alpha(int((stats["carTime"])))

    tb = Textbox(["7 Days passed, you will now be shown how","your lifestyle will impact on the future."], ignoreAnim=True)
    while True:
        update()
        if tb.toRemove: 
            break

    
    MainCam.fade(2, [0])
    MainCam.goto([11, 38])
    positions = [[70, 38], [11, 51], [70, 51], [11, 64], [70, 64], [11, 77], [70, 77]]

    while True:
        update()
        if len(MainCam._fadeValues) == 0: break
        overlay.blit(pollution, [0,0])
    


    text = [
        ["You were driving with your car for {}".format(round(stats["carTime"])), "seconds, which is causing pollution."],
        ["You picked up garbage {} times...".format(stats["garbagePickedUp"])],
        ["...and you left {} garbage untouched.".format(stats["garbageIgnored"])],
        ["You put garbage in the right bin {} times".format(stats["rightBin"]), "But in the wrong bin {} times".format(stats["wrongBin"])],
    ]
    index = 0
    textbox = Textbox(text[index], ignoreAnim=True)
    while True:
        update()

        if textbox.toRemove:
            index += 1
            if index >= len(text):
                index = len(text)
            else:
                textbox = Textbox(text[index], ignoreAnim=True)

        overlay.blit(pollution, [0,0])

        middle = MainCam.toTilePos(listOp(SCREEN_RES, "/", 2))
        newPos = True

        if len(positions) != 0:
            for i in range(2):
                

                if positions[0][i] > round(middle[i]):
                    newPos = False
                    middle[i] += 0.05
                    break
                elif positions[0][i] < round(middle[i]):
                    newPos = False
                    middle[i] -= 0.05
                    break

            MainCam.goto(middle)

            if newPos:
                positions.pop(0)







def main():
    global smoke, text_box_small, text_box_big,ui,bolts, arrow, start, day, worked
    start = True

    init()
    text_box_small = pygame.image.load("assets/text_box_small.png").convert_alpha()
    text_box_big = pygame.image.load("assets/text_box_big.png").convert_alpha()
    smoke = pygame.image.load(PATH_SPRITE + "smoke.png").convert_alpha()
    ui = pygame.image.load("assets/ui.png").convert_alpha()
    bolts = pygame.image.load("assets/energy_bolts.png").convert_alpha()
    arrow = pygame.image.load("assets/arrow.png").convert_alpha()
    
    playDevLogo(1)

    menu()

    #initialize
    load()
    #Player.setLevel("city")
    #Player.goto([68, 33])

    #Timer(test, 10)
    #Player.money = 100
    #Player.energy = 0
    #stats["garbagePickedUp"] = 7*100
    #stats["carTime"] = 7*100
    #worked = True
    #day = 7
    #inventory = [10,10,10,10]
    newDay(pBed, [True, True, True, True, True])
    #def test():
    #    print("yay")
    #Textbox(["This is a textbox text test text box text", "2nd line is also from big importance for that game"], test)
    


    while start:
        #print(Car.entity.rotation)
        #print(clock.get_fps())

        #print(stats)
        update()
        #print(MainCam.position)
        #if mouseButtons[2]: print(MainCam.toTilePos(mousePos, True), mousePos)

        
        #print(MainCam.toTilePos(mousePos, True), Player.position)
        #colls = level_city.getCollision(ent, ent.position, Level.COLL_WALK)
        #for coll in colls:
        #    sp = cam.toScreenPos(coll, False)
        #    pygame.draw.rect(overlay, [0,0,255], [sp[0], sp[1], cam.onScreen_tilesize, cam.onScreen_tilesize])


        #if keyboard[pygame.K_SPACE]: MainCam.fade(10)


        #print(cam.position, keyboard)


#        for i,chunk in enumerate(level.layers[0].chunks):
#            screen.blit(chunk.surface, [i*level.chunkSize*level.tileSize + 10*i, 0])






if __name__ == '__main__':
    main()