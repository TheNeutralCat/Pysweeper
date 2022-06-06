import json, threading, sys, time, random, math, threading
from data import indicatorColors, fx_explosion
from getkey import getkey, keys


class Settings:
  def __init__(self):
    self.settings = {"name": "Player", "debugMode": False, "screenWidth": 60, "screenHeight":40, "highlight": [255,0,255], "highlightFaded": [100,100,100], "borderColor":[125,125,125], "edgeChar": "|", "lineChar": "=", "flagChar": "⚑", "tileChar": "#", "mineChar": "*"}
    self.loadFromFile()

  def loadFromFile(self, name="options.json"):
    try:
      with open(name, "r") as options_file:
        options_data = json.load(options_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError): return

    self.settings.update(options_data)
  
  def saveToFile(self, name="options.json"):
    with open(name, "w") as options_file:
      json.dump(self.settings, options_file)




class Game:
  def __init__(self, gameSettings):
    self.settings = gameSettings.settings

  def newGame(self, difficulty=1, width=16, height=8):
    Clear.screen()
    Cursor.hide()

    startTime = time.time()
    gameIsActive = True
    playerX = width//2; playerY = height//2
  
    ########### GRID GENERATOR ###########
    def genGrid():
      grid = {"mineCount":math.ceil(((width*height)//10)*(1.5**(difficulty))), "width":width, "height":height, "flagCount": 0, "minesCovered": 0, "firstClick": True, "tiles": {}}
      for x in range(1,grid["width"]+1):
        for y in range(1,grid["height"]+1):
          grid["tiles"][(x,y)] = {"state": 0, "num": 0, "mine": False, "flag": False}
          # assembles the grid
      return grid
    ########### GRID GENERATOR ###########
    grid = genGrid()

    
    ########### MINE GENERATOR ###########
    def genMines(mineCount):
      minesPlaced = 0
      while minesPlaced < mineCount:
        randomCell = ((random.randint(1,grid["width"]),random.randint(1,grid["height"])))
        
        if grid["tiles"][randomCell]["mine"] == False:
          grid["tiles"][randomCell]["mine"] = True
          minesPlaced += 1
      
      if self.settings["debugMode"] == True:
        trueMineCount = 0
        for cell in grid["tiles"]:
          if grid["tiles"][cell]["mine"] == True:
            trueMineCount += 1
    
        print(f"\033[93mDEBUG: mine generator results\033[39m\nmineCount: {grid['mineCount']}\ntrueMineCount: {trueMineCount}")
        getkey()
    ########### MINE GENERATOR ###########
    genMines(grid["mineCount"])


    
    ######### INDICATOR GENERATOR #########
    def genIndicators():
      for cell in grid["tiles"]:
        minesInRange = 0
        for xoffset in range(-1,2):
          for yoffset in range(-1,2):
            try:
              if grid["tiles"][(cell[0]+xoffset,cell[1]+yoffset)]["mine"] == True:
                minesInRange += 1
            except KeyError:
              pass
          grid["tiles"][cell]["num"] = minesInRange
          # generates the indicators for how many mines there are near a tile
    ######### INDICATOR GENERATOR #########
    genIndicators()

    
    ############ CELL RENDERER ############
    def drawCell(cell,p=""):
      Cursor.moveTo(cell[1]+3,cell[0]+2)
      # p -> "prefix" (used for drawing the cursor highlight)
      if grid["tiles"][cell]["flag"] == 1: print(f"{p}\033[1m{self.settings['flagChar']}\033[0m",end="") # renders flagged tiles
      elif grid["tiles"][cell]["state"] == 0: print(f"{p}\033[2m{self.settings['tileChar']}\033[0m",end="") # renders covered tiles
      elif grid["tiles"][cell]["state"] == 1: # renders uncovered tiles
        if grid["tiles"][cell]["mine"] == True: print(f"{p}\033[2m{self.settings['mineChar']}\033[0m",end="") # renders mines
        elif grid["tiles"][cell]["num"] > 0: print(f"{p}{indicatorColors[grid['tiles'][cell]['num']]}{grid['tiles'][cell]['num']}\033[0m",end="") # renders mine indicators
        else:
          print(f"{p} \033[0m",end="") # renders blank space
      sys.stdout.flush()
    ############ CELL RENDERER ############

    
    borderColor = f"\033[38;2;{self.settings['borderColor'][0]};{self.settings['borderColor'][1]};{self.settings['borderColor'][2]}m"
    ########### USER INTERFACE ###########
    if grid["width"] > 26:
      def drawUI_flags():
        Cursor.moveTo(2,(grid["width"]//2)+5)
        print(f"\033[93mFLAGS:\033[0m {grid['flagCount']}/{grid['mineCount']}".ljust((grid["width"]//2)-3),end="")
      
      def drawUI_time():
        print(f"\033[2;4H\033[93mTIME:\033[0m \033[38;2;175;50;50m0000\033[0m",end="")

      def drawUI_dynamicTime():
        while gameIsActive == True:
          print(f"\033[2;4H\033[93mTIME:\033[0m \033[38;2;255;50;50m{str(round(time.time()-startTime))[0:4].rjust(4,'0')}\033[0m",end="")
          sys.stdout.flush()
          if time.time()-startTime > 9999:
            endGame(2)
            break
          time.sleep(1)
    
    else:
      def drawUI_flags():
        Cursor.moveTo(2,(grid["width"]//2)+5)
        print(f"{grid['flagCount']}/{grid['mineCount']}".center((grid["width"]//2)-3),end="")
      
      def drawUI_time():
        print("\033[2;4H\033[38;2;175;50;50m"+"0000".center((grid["width"]//2)-3)+"\033[0m",end="")

      def drawUI_dynamicTime():
        while gameIsActive == True:
          print("\033[2;4H\033[38;2;255;50;50m"+str(round(time.time()-startTime))[0:4].rjust(4,'0').center((grid['width']//2)-3)+"\033[0m",end="")
          sys.stdout.flush()
          if time.time()-startTime > 9999:
            endGame(2)
            break
          time.sleep(1)

    
    def drawUI():
      if (grid["width"] % 2) == 0:
        border = self.settings["edgeChar"]+self.settings["edgeChar"]+(self.settings["edgeChar"]+self.settings["edgeChar"]).center(grid["width"],self.settings["lineChar"])+self.settings["edgeChar"]+self.settings["edgeChar"]
      else:
        border = self.settings["edgeChar"]+self.settings["edgeChar"]+self.settings["edgeChar"].center(grid["width"],self.settings["lineChar"])+self.settings["edgeChar"]+self.settings["edgeChar"]

      Cursor.moveTo(2)
      print(borderColor+border.replace(self.settings["lineChar"]," ")+"\033[0m",end="")
      # prints the center seperator in the header UI
      
      for y in [1,3,(grid["height"]+4)]:
        Cursor.moveTo(y)
        print(borderColor+border+"\033[0m",end="")
        # prints borders at any y coord in the list
      
      for side in [1,2,grid["width"]+3,grid["width"]+4]:
        for yValue in range(0,grid["height"]+2):
          Cursor.moveTo(yValue+2,side)
          print(borderColor+self.settings["edgeChar"]+"\033[0m",end="")
          # draws a border straight down on each side of the grid
          # (height depends on the max range of "yValue")

        drawUI_flags()
        drawUI_time()
    ########### USER INTERFACE ###########
    drawUI()

    
    def drawGrid():
      drawUI()
      for cell in grid["tiles"]:
        drawCell(cell)
      sys.stdout.flush()
    drawGrid()

    
    def drawCursor():
      drawCell((playerX,playerY),p="\033[48;2;255;255;255m"+"\033[38;2;0;0;0m")

      
    ############ AREA CLEARER ############
    def openAdjacent(x,y,dead=False):
      activeTiles = []
      for xoffset in range(-1,2):
        for yoffset in range(-1,2): #checks the current tile and the adjacent 8
          try:
            if grid["tiles"][(x+xoffset,y+yoffset)]["state"] == 0 and grid["tiles"][(x+xoffset,y+yoffset)]["mine"] == False:
              if grid["tiles"][(x+xoffset,y+yoffset)]["num"] == 0:
                activeTiles.append((x+xoffset,y+yoffset))
              else:
                grid["tiles"][(x+xoffset,y+yoffset)]["state"] = 1
                # opens and "kills" the tile
          except KeyError:
            pass # ignores if tile is outside of bounds
            
      for tile in activeTiles:
        grid["tiles"][tile]["state"] = 1
        openAdjacent(tile[0],tile[1])
        activeTiles.remove(tile)
    ############ AREA CLEARER ############

        
    ############ ON FIRST CLICK ############
    def onFirstClick():
      if grid["tiles"][(playerX,playerY)]["mine"] == True:
        while grid["tiles"][(playerX,playerY)]["mine"] == True:
          grid["tiles"][(playerX,playerY)]["mine"] = False
          genMines(1)
        genIndicators()
        # if the tile you open is a mine, move it and regen the board
      
      for xoffset in range(-1,2):
        for yoffset in range(-1,2):
          try:
            if grid["tiles"][(playerX+xoffset,playerY+yoffset)]["mine"] == False:
              openAdjacent(playerX+xoffset, playerY+yoffset)
              # searches the adjacent 8 tiles and tries to check for empty tiles around each of them
              # if it finds any, it will open all of them
          except KeyError:
            pass # ignores if tile is out of bounds
      
      drawGrid()
    ############ ON FIRST CLICK ############

      
    ############ ANIM RENDERER ############
    def playAnimation(x,y,spritesheet):
      for frame in spritesheet:
        Cursor.moveTo(y,x-1)
        print(frame,end="")
        sys.stdout.flush()
        time.sleep(0.1)
    ############ ANIM RENDERER ############

        
    ############ GAMESTATES ############
    def endGame(state=0):
      noKeyPressed = True
      def pressAnyKey():
        time.sleep(2)
        if noKeyPressed == True:
          print("\033[4;1H\033[2mpress any key to continue\033[0m")

      if state == 0: # player loses
        Clear.screen()
        print(f"\033[31mYou died!\033[39m\nYour time: {round(time.time()-startTime,2)} seconds\033[39m")
        threading.Thread(target=pressAnyKey,daemon=True).start()
        getkey()
        noKeyPressed = False
      
      if state == 1: # player wins
        Clear.screen()
        print(f"\033[92mYou win!\033[39m\nYour time: {round(time.time()-startTime,2)} seconds\033[39m")
        threading.Thread(target=pressAnyKey,daemon=True).start()
        getkey()
        noKeyPressed = False

      if state == 2: #player runs out of time
        Clear.screen()
        print(f"\033[93mTime's up!\033[39m\n\033[2m(you lost)\033[0m")
        threading.Thread(target=pressAnyKey,daemon=True).start()
        getkey()
        noKeyPressed = False
    ############ GAMESTATES ############

    
    
    threading.Thread(target=drawUI_dynamicTime,daemon=True).start()
    
    while True:
      drawCursor()
      Cursor.moveTo(grid["height"]+5)
      if self.settings["debugMode"] == True:
        print(f"\033[0J\ncoords: ({playerX},{playerY})\nmines: {grid['mineCount']}/{grid['width']*grid['height']} tiles\nflagCount: {grid['flagCount']}/{grid['mineCount']}\nminesCovered: {grid['minesCovered']}/{grid['mineCount']}\nactive threads: {threading.active_count()}",end="")
      else:
        print("\033[0J") # to prevent screen corrpution (clears to end of screen)
      
      playerInput = getkey()

      
      if playerInput in [keys.RIGHT,keys.LEFT,keys.UP,keys.DOWN]:
        drawCell((playerX,playerY))
        sys.stdout.flush()
        # undraws the cursor from current pos when it moves somewhere else
      
      if playerInput == keys.RIGHT: playerX += 1
      elif playerInput == keys.LEFT: playerX -= 1
      elif playerInput == keys.UP: playerY -= 1
      elif playerInput == keys.DOWN: playerY += 1
      # basic movement controls

      
      elif playerInput == keys.TAB:
        Clear.screen()
        drawUI()
        drawGrid()
        # hard refreshes the screen

      
      elif playerInput == keys.ESC:
        Clear.screen()
        gameIsActive = False
        return
        # exits the current game

      
      elif playerInput == keys.SPACE or playerInput == keys.ENTER:
        if grid["tiles"][(playerX,playerY)]["flag"] == True: pass
          # if tile is flagged or uncovered, do nothing
        else:
          if grid["firstClick"] == True:
            onFirstClick()
            grid["firstClick"] = False
          
          if grid["tiles"][(playerX,playerY)]["mine"] == True:
            gameIsActive = False
            playAnimation(playerX+2,playerY+3,fx_explosion)
            endGame(0)
            return
            # if there is a mine, you die
          
          elif grid["tiles"][(playerX,playerY)]["num"] == 0 and grid["tiles"][(playerX,playerY)]["state"] == 0:
            openAdjacent(playerX,playerY)
            drawGrid()
            # if tile is blank (AND covered), open others nearby

          grid["tiles"][(playerX,playerY)]["state"] = 1
          # (finally) uncovers the tile


      
      elif playerInput == keys.X:
        if grid["tiles"][(playerX,playerY)]["state"] == 0:
          # checks if tile is covered
          if grid["tiles"][(playerX,playerY)]["flag"] == True:
            grid["tiles"][(playerX,playerY)]["flag"] = False
            # if the tile is already flagged, un-flag it
            grid["flagCount"] -= 1
            if grid["tiles"][(playerX,playerY)]["mine"] == True:
              grid['minesCovered'] -= 1
              # if removing the flag unflags a mine, update this counter
  
          elif grid["flagCount"] < grid["mineCount"]:
            grid["tiles"][(playerX,playerY)]["flag"] = True
            # places a flag on the tile
            grid["flagCount"] += 1
            if grid["tiles"][(playerX,playerY)]["mine"] == True:
              grid["minesCovered"] += 1
              # if the flagged tile is a mine, update this counter
        
        drawUI_flags()
        # updates flag count on UI


      ############ BOARD SAVING ############
      elif playerInput == keys.S:
        self.saveGame(grid)
      ############ BOARD SAVING ############

          
      ############ BOARD LOADING ############
      elif playerInput == keys.L:
        grid = self.loadGame()
        Clear.screen()
        drawGrid()
      ############ BOARD LOADING ############
        
      
      if playerX < 1: playerX = grid["width"]
      elif playerX > grid["width"]: playerX = 1
      if playerY < 1: playerY = grid["height"]
      elif playerY > grid["height"]: playerY = 1
      # controls screen wrapping


      if grid["minesCovered"] == grid["mineCount"]:
        gameIsActive = False
        endGame(1)
        return
        # win condition


  

  def saveGame(self,grid):
    save_data = {"mineCount": grid["mineCount"], "width": grid["width"], "height": grid["height"], "flagCount": grid["flagCount"], "minesCovered": grid["minesCovered"], "firstClick": grid["firstClick"], "tiles": {}}
    for tile in grid["tiles"]:
      save_data["tiles"][str(tile)] = grid["tiles"][tile]
      # tuples cannot be saved in json, convert to str
    
    with open("savestate.json", "w") as save_file:
      json.dump(save_data, save_file)

  
  
  def loadGame(self):
    with open("savestate.json", "r") as save_file:
      save_data = json.load(save_file)

    grid = {"mineCount": save_data["mineCount"], "width": save_data["width"], "height": save_data["height"], "flagCount": save_data["flagCount"], "minesCovered": save_data["minesCovered"], "firstClick": save_data["firstClick"],}
    for tile in save_data["tiles"]:
      coords = []
      for coord in tile[1:-1].split(", "):
        coords.append(int(coord))
      grid["tiles"][tuple(coords)] = save_data["tiles"][tile]
    
    return grid




















class Dialog:
  def __init__(self, gameSettings):
    self.settings = gameSettings.settings

  
  def new(self, data, submenu=False):
    Clear.screen()

    highlight = f"\033[48;2;{self.settings['highlight'][0]};{self.settings['highlight'][1]};{self.settings['highlight'][2]}m"
    highlightFaded = f"\033[48;2;{self.settings['highlightFaded'][0]};{self.settings['highlightFaded'][1]};{self.settings['highlightFaded'][2]}m"
    borderColor = f"\033[38;2;{self.settings['borderColor'][0]};{self.settings['borderColor'][1]};{self.settings['borderColor'][2]}m"
    currentItem = 0

    ####################### BORDER #######################
    if (self.settings["screenWidth"] % 2) == 0:
      border = borderColor+self.settings["edgeChar"]+"||".center(self.settings["screenWidth"]-2,self.settings["lineChar"])+self.settings["edgeChar"]+"\033[39m"
    else:
      border = borderColor+self.settings["edgeChar"]+"|".center(self.settings["screenWidth"]-2,self.settings["lineChar"])+self.settings["edgeChar"]+"\033[39m"
    # creates border and stores it in memory
    ####################### BORDER #######################

      
    ####################### HEADER #######################
    def drawHeader():
      try: print(borderColor+self.settings["edgeChar"]+(" "+data["header"]+" ").center(self.settings["screenWidth"]-2,self.settings["lineChar"])+self.settings["edgeChar"]+"\033[39m\n",end="")
      except KeyError: print(border)
    # if there is a "header" tag, this centers its contents in the top border
    ####################### HEADER #######################

        
    ####################### FOOTER #######################
    def drawFooter():
      try: print(borderColor+self.settings["edgeChar"]+(" "+data["footer"]+" ").center(self.settings["screenWidth"]-2,self.settings["lineChar"])+self.settings["edgeChar"]+"\033[39m\n",end="")
      except KeyError: print(border)
    # if there is a "footer" tag, this centers its contents in the bottom border
    ####################### FOOTER #######################

        
    ####################### MESSAGE #######################
    def drawMessage():
      try:
        data["message"]
        # checks if message tag exists
        
        def formatMessage(message):
          if len(message) > self.settings["screenWidth"]-4:
            word_list = message.split()
            # breaks down the message string into a list
            # (ex. ["This","is","a","message"])
    
            string = ""
            while len(word_list) > 0:
              # runs as until the full message has been fully printed
              string += word_list.pop(0)+" "
              
              while len(string) < self.settings["screenWidth"]-4:
                try:
                  if len(string)+len(word_list[0])+1 > self.settings["screenWidth"]-4:
                    break
                    # quits the function if continuing would overflow
                  else:
                    string += word_list.pop(0)+" "
                except IndexError: break
                # assembles each line until it's too long to fit
    
              print(borderColor+self.settings["edgeChar"]+"\033[39m",string[:-1].center(self.settings["screenWidth"]-4),borderColor+self.settings["edgeChar"]+"\033[39m\n",end="")
              string = ""
          
          else:
            print(borderColor+self.settings["edgeChar"]+"\033[39m",message.center(self.settings["screenWidth"]-4),borderColor+self.settings["edgeChar"]+"\033[39m\n",end="")
    
        ##################################
        if type(data["message"]) == list:
          for message in data["message"]:
            formatMessage(message)
        
        elif type(data["message"]) == str:
          formatMessage(data["message"])
        ##################################
      
      except KeyError: pass
      # if there is a "message" tag, this will print its contents
      # controls word wrap across multiple lines
    ####################### MESSAGE #######################

    
    try:
      padding = ""
      for x in range(data["padding"]):
        padding += " "
    except KeyError: padding = " "
    # controls the padding of horizontal menu options
    
    optionList = []
    for x in data["options"]:
      optionList.append(x["name"])
    # creates a list of all the menu options specified
    # ex. ["SAVE","LOAD","CLEAR","CANCEL"]


    try:
      if data["vertical"] == True:
        ########### VERTICAL ###########
        def drawOptions(currentItem,h=True):
          for option in data["options"]:
            print(self.settings["edgeChar"],option["name"].center(self.settings["screenWidth"]-4),self.settings["edgeChar"])
    
          if h==True: prefix = highlight
          elif h==False: prefix = highlightFaded
          
          print(f"\033[{len(data['options'])-currentItem}A",end="")
          # travels up to the selected uption
          
          print(borderColor+self.settings["edgeChar"]+"\033[39m",(prefix+data["options"][currentItem]["name"]+"\033[0m").center(self.settings["screenWidth"]+len(prefix)," "),borderColor+self.settings["edgeChar"]+"\033[39m\n",end="")
          # highlights the "selected" option
    
          for x in range(len(data["options"])-currentItem-1):
            print()
          # goes back to the bottom of the page to print the footer
        ########### VERTICAL ###########
        
      else:
        raise KeyError
    except KeyError:
      ########### HORIZONTAL ###########
      def drawOptions(index,h=True):
        optionDisplay = []
        for x in optionList:
          optionDisplay.append(x)
        # For some reason you CANNOT just set "optionDisplay" equal to "optionList"
        # Doing it like this is dumb but required to avoid quantum entanglement
        
        if h == True:
          optionDisplay.insert(index, highlight)
        else:
          optionDisplay.insert(index, "\033[48;2;100;100;100m")
        optionDisplay.insert(index+2, "\033[0m")
  
        export = ""
        for x in optionDisplay:
          export += x + padding
          # I LOVE PADDING I LOVE PADDING I LOVE PADDING
        
        print(borderColor+self.settings["edgeChar"]+"\033[39m"+(export.center(self.settings["screenWidth"]+len(highlight)+2, " "))+borderColor+self.settings["edgeChar"]+"\033[39m\n",end="")
        # draws the menu (with padding)
      ########### HORIZONTAL ###########

    
    exitDialog = False
    Cursor.hide()
    while True:
      drawHeader()
      drawMessage()
      drawOptions(currentItem)
      drawFooter()

      sys.stdout.flush()
      playerInput = getkey()

      if playerInput == keys.RIGHT or playerInput == keys.DOWN: currentItem += 1
      elif playerInput == keys.LEFT or playerInput == keys.UP: currentItem -= 1
      elif playerInput == keys.ESC:
        ########### WEAK ###########
        try:
          if data["weak"] == True: exitDialog = True
          # if the menu has the "weak" tag, pressing esc will close the dialog
        except KeyError: pass
        ########### WEAK ###########

      
      elif playerInput == keys.ENTER or playerInput == keys.SPACE:
        ########### FUNC ###########  
        try:
          if type(data["options"][currentItem]["func"]) == list:
            for func in data["options"][currentItem]["func"]:
              func()
          else:
            data["options"][currentItem]["func"]()
        except KeyError: pass
          # the "func" tag
          # runs any function attached to the tag
        ########### FUNC ###########


        ########### SUBMENU ###########
        try:
          data["options"][currentItem]["submenu"]
          # checks whether the key exists
          
          self.new(data["options"][currentItem]["submenu"],submenu=True)
          # creates a new dialog loop with the data contained in the tag
        except KeyError: pass
        ########### SUBMENU ###########

          
        ########### EXIT ###########
        try:
          if data["options"][currentItem]["exit"] == True: exitDialog = True
        except KeyError: pass
        # the "exit" tag
        # breaks the dialog loop if tag is set to "True"
        ########### EXIT ###########

      
      if currentItem > len(data["options"])-1: currentItem = 0
      if currentItem < 0: currentItem = len(data["options"])-1
      
      Clear.screen()
      ########### ON DIALOG EXIT ###########
      if exitDialog == True:
        if submenu != True:
          Cursor.show()
        break
      ########### ON DIALOG EXIT ###########

      


  
  def err(self, error_msg):
    self.new({"header":"ERROR","message":f"{error_msg}.","weak":True,"options":[{"name":"OK","exit":True}]})











class InputThread(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
   
  def run(self): 
    pass







class Cursor:
  def show(f=True):
    sys.stdout.write("\033[?25h")
    if f == True: sys.stdout.flush()
  def hide(f=True):
    sys.stdout.write("\033[?25l")
    if f == True: sys.stdout.flush()
  
  def moveTo(line=1,column=1,f=False):
    sys.stdout.write(f"\033[{line};{column}H")
    if f == True: sys.stdout.flush()

class Clear:
  def screen(f=False):
    sys.stdout.write("\033[2J")
    sys.stdout.write(f"\033[0;0H")
    if f == True: sys.stdout.flush()

  def line(f=False):
    sys.stdout.write("\033[2K")
    if f == True: sys.stdout.flush()