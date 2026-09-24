from types import CellType
from typing import Self, Tuple
import pygame
from sys import exit
import random
import numpy
import pygame, time

pygame.init()
screenheight = 600
screenwidth = 800
running = True
screen = pygame.display.set_mode((screenwidth, screenheight)) #makes the screen into the set size
pygame.display.set_caption('Maze game :)' )
clock = pygame.time.Clock()
font = pygame.font.SysFont("arialblack", 25)
menuTrue = 0
blackscreen = True
usertext = '' #records the username
UserNameInput = False #Checks to see if the program should record the users key inputs
#sets colours that will be used so i dont have to input the rgb values each time
Light_Blue = (0, 127, 255)
Dark_Blue = (10, 77, 145)
black = (0,0,0)
white = (255, 255, 255)
red = (207, 29, 29)
green = (11, 153, 23)
maze = None
isPlayer = 0
GameClock = None
PlayerScore = 0

class Timer():
    def __init__(self):
        '''The start time is reset every time the player starts a new game
        The elapsed time is the total time the game has been open subtracted by start time
        The elapsed time is split into minutes and seconds and displayed on screen'''
        self.StartTime = None
        self.ElapsedTime = 0
        self.__TimerFont = pygame.font.SysFont("arialblack", 50)
    def StartTimer(self):
        self.StartTime = time.time()
    def UpdateTimer(self):
        if self.StartTime != None:
            self.ElapsedTime = time.time() - self.StartTime
    def DisplayTimer(self):
        seconds = int(self.ElapsedTime % 60)
        minutes = int(self.ElapsedTime / 60)
        TotalTime = str(minutes) + ":" + str(seconds)
        Timer = self.__TimerFont.render(TotalTime, True, Dark_Blue)
        return Timer
    def StopTimer(self):
        self.StartTime = None

class Cell():
    def __init__(self,XCoordinate, YCoordinate, Thickness):
        self.Visited = False #Checks if the cell has been visited by the pathfinding algorithm
        '''Sets the coordinates of the cells and thickness of the cell walls'''
        self.XCoordinate = XCoordinate
        self.YCoordinate = YCoordinate
        self.__Thickness = Thickness
        '''Decides if the walls on the north,east,south and west are on'''
        self.Wall = {'North':True,'East':True,'South':True,'West':True}
        self.Visited = False
        self.Finish = False
   
    def DrawCells(self,Screen,CellSize):
        '''From this point the code was borrowed from https://thepythoncode.com/article/build-a-maze-game-in-python#creating-grid-cell to help me figure out how to make the player work'''
        xSize = self.XCoordinate * CellSize + 5
        ySize = self.YCoordinate * CellSize + 5
        '''Draws each line of the cell if it is supposed to be there
        The lines are drawn at the distance of the size of the cell from the coordinates to make sure that they are draw in the correct position'''
        if self.Wall['North'] == True:
            pygame.draw.line(Screen,Dark_Blue,(xSize,ySize),(xSize + CellSize ,ySize),self.__Thickness)
        if self.Wall['East'] == True:
            pygame.draw.line(Screen,Dark_Blue,(xSize + CellSize,ySize),(xSize + CellSize, ySize+CellSize),self.__Thickness)
        if self.Wall['South'] == True:
            pygame.draw.line(Screen,Dark_Blue,(xSize + CellSize, ySize + CellSize), (xSize,ySize + CellSize),self.__Thickness)
        if self.Wall['West'] == True:
            pygame.draw.line(Screen,Dark_Blue,(xSize,ySize + CellSize),(xSize,ySize),self.__Thickness)


        '''This is the end point of the code borrowed from https://thepythoncode.com/article/build-a-maze-game-in-python#creating-grid-cell'''




    def CheckCell(self,XCoordinate,YCoordinate,ListOfCells,Columns,rows): #Checks if the cell exists and wether to draw it or not
        '''https://stackoverflow.com/questions/39217512/
        This link was used for the equation that helped me convert x and y coordinates to a position in a 1D array (variable: Array1D)'''
        Array1D = XCoordinate + (YCoordinate * Columns)
        '''This is the end of the code used from the above link'''
       
        if XCoordinate < 0 or XCoordinate >= Columns or YCoordinate < 0 or YCoordinate >= rows:
            return False
        else:
            return ListOfCells[Array1D]
    '''Converts the coordinates of the neighbouring cell to a position in the 1D array of Cells
    Checks if the XCoordinate or YCoordinate are outside the grid
    If it is outside the grid, the method returns false
    If it is in the grid, the method returns the location of the cell in the 1D array'''
       
    def CheckNeighbours(self,Columns,rows,ListOfCells): #Check if the neighbours exist and if they have been visited
        neighbours = []
        '''Check if the cells for top, left, right, bottom exist (CheckCell())'''
        TopNeighbour = self.CheckCell(self.XCoordinate,self.YCoordinate -1,ListOfCells,Columns,rows)
        RightNeighbour = self.CheckCell(self.XCoordinate +1 ,self.YCoordinate,ListOfCells,Columns,rows)
        BottomNeighbour = self.CheckCell(self.XCoordinate,self.YCoordinate +1,ListOfCells,Columns,rows)
        LeftNeighbour = self.CheckCell(self.XCoordinate -1 ,self.YCoordinate,ListOfCells,Columns,rows)
       
        '''Loops through all the neighbours and adds them to a list if they exist'''
        for neighbour in [TopNeighbour, RightNeighbour, BottomNeighbour, LeftNeighbour]:
            if neighbour:
                neighbours.append(neighbour)
        '''returns the full list of valid neighbours'''
        return neighbours

class Maze():
    def __init__ (self, Columns, rows):
        self.Columns = Columns #The number of columns in the grid (Y)
        self.rows = rows #The number of rows in the grid (X)
        self.Thickness = 2 #The thickness of the lines that separate the cells and make up the walls
        self.ListOfCells = []
        self.CellSize = 35
        '''The list of cells needs to create a cell for the number of rows and the number of columns'''
        for row in range(self.rows):
            for Column in range (self.Columns):
                self.ListOfCells.append(Cell(Column,row,self.Thickness))
    def removewalls(self,CurrentCell,NextCell):
        XDif = CurrentCell.XCoordinate - NextCell.XCoordinate
        '''Finds the difference in X coordinates between the Current Cell and the neighbouring Cell'''
        YDif = CurrentCell.YCoordinate - NextCell.YCoordinate
        '''Finds the difference in Y coordinates between the Current Cell and the neighbouring Cell'''
        '''If the difference between the coordinates is positive then the currentcell wall that needs to be removed is the west or north walls (and is the opposite for the next Cell) and if it is negative the wall will be east or south'''
        if XDif == 1:
            CurrentCell.Wall['West'] = False
            NextCell.Wall['East'] = False
        elif XDif == -1:
            CurrentCell.Wall['East'] = False
            NextCell.Wall['West'] = False


        if YDif == 1:
            CurrentCell.Wall['North'] = False
            NextCell.Wall['South'] = False
        elif YDif == -1:
            CurrentCell.Wall['South'] = False
            NextCell.Wall['North'] = False
    def GenerateMaze(self):
         startCell = numpy.random.choice(self.ListOfCells)
         startCell.Visited = True
           
         '''Adds the neighbours of the starting cell to the frontier cells(all unvisited cells adjacent to visited cells that are in the maze) list'''
         frontierCells = []
         for neighbour in startCell.CheckNeighbours(self.Columns, self.rows, self.ListOfCells):
            if not neighbour.Visited:
                frontierCells.append(neighbour)

         '''while there are items in the frontierCells, pick a random one'''
         while frontierCells:
            randCell = frontierCells.pop(random.randint(0,len(frontierCells)-1))
            '''skips the current cell if it has already been visited'''
            if randCell.Visited:
                continue

            '''Gets all visited neighbours of the current frontier cell'''
            EveryNeighbour = randCell.CheckNeighbours(self.Columns,self.rows, self.ListOfCells)
            VisitedNeighbours = []
            for n in EveryNeighbour:
                if n.Visited == True:
                    VisitedNeighbours.append(n)
           
            if VisitedNeighbours:
                #Selects a random visited neighbour to remove the walls between
                SelectedNeighbour = numpy.random.choice(VisitedNeighbours)
                self.removewalls(randCell, SelectedNeighbour)
                randCell.Visited = True

                #Adds any unvisited neighbours of this new cell to the frontier cells list
                for neighbour in randCell.CheckNeighbours(self.Columns,self.rows, self.ListOfCells):
                    if not neighbour.Visited:
                        frontierCells.append(neighbour)
        #Draws all the cells once the maze is generated
         global screen
         for CurrentDrawCell in self.ListOfCells:
            CurrentDrawCell.DrawCells(screen,self.CellSize)

class SearchAlgorithm():
    def __init__(self,SearchX,SearchY,CellSize,Thickness):
        self.SearchX = int(SearchX)
        self.SearchY = int(SearchY)
        self.CellSize = CellSize
        self.Thickness = Thickness
        self.RealSearchX = ((self.SearchX * self.CellSize) + self.Thickness + 2) +5
        self.RealSearchY = ((self.SearchY * self.CellSize) + self.Thickness +2) +5
        self.Rect = pygame.Rect(self.RealSearchX,self.RealSearchY,31,31)
        self.SearchColour = (red)
        self.SearchWin = False
        self.Stack = []
        self.Visited = set() #Does not need to be in order to search through it
        self.Finished = False
        self.Started = False
        self.CurrentCell = None
    def StartSearch(self,ListOfCells):
        start = self.GetCurrentCell(self.SearchX, self.SearchY, ListOfCells) #Sets the starting cell to the current cell the search algorithm is in (which is 0,0 because thats where it is set to start)
        if start != None: #If start hasn't already been set it will add the start cell to the stack of cells and say that the search has been started.
            self.Stack.append(start)
            self.Started = True
    
    def GetAdjacentcells(self, CurrentCell, ListOfCells):
        '''Gets all the adjacent cells of the current cell by checking if the cell exists in each cardinal direction with the getcurrentcell method'''
        adjacent = []
        x = CurrentCell.XCoordinate
        y = CurrentCell.YCoordinate

        if not CurrentCell.Wall['North']:
            cell = self.GetCurrentCell(x, y - 1, ListOfCells)
            if cell != None:
                adjacent.append(cell)
        
        if not CurrentCell.Wall['East']:
            cell = self.GetCurrentCell(x + 1, y, ListOfCells)
            if cell != None:
                adjacent.append(cell)
        
        if not CurrentCell.Wall['South']:
            cell = self.GetCurrentCell(x, y + 1, ListOfCells)
            if cell != None:
                adjacent.append(cell)

        if not CurrentCell.Wall['West']:
            cell = self.GetCurrentCell(x - 1, y, ListOfCells)
            if cell != None:
                adjacent.append(cell)

        return adjacent #Returns the list of adjacent cells

    def DFSMove(self,ListOfCells):
        if self.Finished:
            return
            #return is used to exit the function
        if not self.Started:
            #If the search hasn't been started already it will begin searching the maze
            self.StartSearch(ListOfCells)
        if len(self.Stack) == 0:
            #If there is nothing left to search (when there are no more cells to return to)
            self.Finished = True
            return
        #Get the next cell from the stack
        CurrentCell = self.Stack[len(self.Stack)-1]
        self.Stack.pop()

        #Ignore visited cells
        CellPos = (CurrentCell.XCoordinate, CurrentCell.YCoordinate)
        if CellPos in self.Visited:
            return
        elif CellPos not in self.Visited:
            self.Visited.add(CellPos)

        self.SearchX = CurrentCell.XCoordinate
        self.SearchY = CurrentCell.YCoordinate
        self.RealSearchX = ((self.SearchX * self.CellSize) + self.Thickness + 2) +5
        self.RealSearchY = ((self.SearchY * self.CellSize) + self.Thickness +2) +5
        self.Rect = pygame.Rect(self.RealSearchX, self.RealSearchY, 31,31)
        if CurrentCell.XCoordinate == 14 and CurrentCell.YCoordinate == 14:
            self.SearchWin = True
            self.Finished = True
            return
        else:
            AdjacentCells = self.GetAdjacentcells(CurrentCell,ListOfCells)
            for neighbour in AdjacentCells:
                self.Stack.append(neighbour)

    def GetCurrentCell(self,SearchX,SearchY,ListOfCells): #polymorphism from the player class
        for cell in ListOfCells:
            if cell.XCoordinate == SearchX and cell.YCoordinate == SearchY:
                return cell

    def DrawSearch(self):
            pygame.draw.rect(screen,self.SearchColour, self.Rect)

class Player():
    '''From this point the code was borrowed from https://thepythoncode.com/article/build-a-maze-game-in-python#creating-grid-cell to help me figure out how to make the player work'''
    def __init__(self,PlayerX,PlayerY,CellSize,Thickness):
        self.CellSize = CellSize
        self.Thickness = Thickness
        self.PlayerX = int(PlayerX)
        self.PlayerY = int(PlayerY)
        self.RealPlayerX = ((self.PlayerX * self.CellSize) + self.Thickness + 2) +5
        self.RealPlayerY = ((self.PlayerY * self.CellSize) + self.Thickness +2) +5
        self.Rect = pygame.Rect(self.RealPlayerX,self.RealPlayerY,31,31)
        self.PlayerColour = (green)
        self.LeftPressed = False
        self.RightPressed = False
        self.UpPressed = False
        self.DownPressed = False
        self.Win = False
    def GetCurrentCell(self,PlayerX,PlayerY,ListOfCells):
        for cell in ListOfCells:
            if cell.XCoordinate == PlayerX and cell.YCoordinate == PlayerY:
                return cell

    '''This is the end point of the code borrowed from https://thepythoncode.com/article/build-a-maze-game-in-python#creating-grid-cell'''
    def CheckMove(self,ListOfCells):
        '''This gets the current cell the player is in and checks if the player can move in each direction
       
        if it can the players coordinates are increased by 1 in that direction
       
        The realPlayer coordinates are used to find the coordinates the player has to be drawn onto the screen at
       
        If the player gets to the end square (14,14) then they win the game
       
        Every time this is called the player will be drawn in the new coordinates'''
        CurrentCell = self.GetCurrentCell(self.PlayerX, self.PlayerY, ListOfCells)
        if CurrentCell:
            if self.LeftPressed and not CurrentCell.Wall['West']:
                self.PlayerX -= 1
            if self.UpPressed and not CurrentCell.Wall['North']:
                self.PlayerY -= 1
            if self.RightPressed and not CurrentCell.Wall['East']:
                self.PlayerX += 1
            if self.DownPressed and not CurrentCell.Wall['South']:
                self.PlayerY += 1
            self.RealPlayerX = ((self.PlayerX * self.CellSize) + self.Thickness + 2) + 5
            self.RealPlayerY = ((self.PlayerY * self.CellSize) + self.Thickness +2) + 5
            self.Rect = pygame.Rect(self.RealPlayerX,self.RealPlayerY,31,31)
        else:
            print("Debug: Current Cell is empty")
        if self.PlayerX == 14 and self.PlayerY == 14:
            self.Win = True
        else:
            self.Win = False
    def DrawPlayer(self):
        if self.Win != True:
            pygame.draw.rect(screen,self.PlayerColour, self.Rect)

def checkMenu():
    global search
    global DFSRunning
    global LastDFSStep
    global maze
    global menuTrue
    global GameClock
    global PlayerScore
    DFSDelay = 50
    if menuTrue < 1: #If i want to load the main menu this value will be 0
        Menu() #Loads all the buttons for the main menu at the start
    elif menuTrue == 1: #If i have already used the menu, the value is 1 or greater
        SetUsername() #Loads the screen that has the username input
    elif menuTrue == 2:
        #Draws the cell in the winning coordinates white so you can see it
        finishcell = CreateRectangle(498, 498, 31, 31, white, " ", white , 0, 590, 590)
        #Displays the rules and how to play on the screen
        rules = CreateRectangle(600,600,31,31,black, "WASD or arrow keys to move, white square = WIN", white,0,10,550)
        global isPlayer
        #Checks if the player exists
        isPlayer = 1
        if maze == None:
            '''If the maze doesn't exist it generates the maze and starts the timer as well as drawing the player'''
            newscreen()
            maze = Maze(15,15)
            maze.GenerateMaze()
            player.CheckMove(maze.ListOfCells)
            GameClock = Timer()
            GameClock.StartTimer()
        elif maze != None:
            '''If the maze already exists and has been generated:
            The rules are written
            a button is made for the scoreboard
            the game clock is updated
            The cells of the maze are drawn
            The player is drawn
           
            Checks if the player has won
                If they have then it takes them to the winning screen
                and the scoreboard is updated'''
            newscreen()
            finishcell = CreateRectangle(501, 501, 25, 25, white, " ", white , 0, 590, 590)
            rules = CreateRectangle(600,600,31,31,black, "WASD or arrow keys to move, white square = WIN", white,0,10,550)
            ScoreboardButtonGame = Button("Scoreboard", 560,225,True,590,150)
            if ScoreboardButtonGame.checkClick():
                menuTrue = 4
            if GameClock != None:
                GameClock.UpdateTimer()
                screen.blit(GameClock.DisplayTimer(),(610,270))
           
            for cells in maze.ListOfCells: #type:ignore
                cells.DrawCells(screen,maze.CellSize)
                if search != None:
                    if DFSRunning:
                        search.DrawSearch()

            if isPlayer == 1:
                player.DrawPlayer()
            if player.Win == True and not DFSRunning:
                isPlayer = 0
                search = SearchAlgorithm(0,0,maze.CellSize, maze.Thickness)
                search.StartSearch(maze.ListOfCells)
                DFSRunning = True

                if GameClock != None:
                    PlayerScore = int(GameClock.ElapsedTime)
                    GameClock.StopTimer()

                UpdateScoreboard()
            if DFSRunning and search != None:
                CurrentTime = pygame.time.get_ticks()
                #LastDFSStep = 10000000000000
                if CurrentTime - LastDFSStep >= DFSDelay:
                    search.DFSMove(maze.ListOfCells)
                    LastDFSStep = CurrentTime
            if search != None:
                if search.SearchWin == True:
                    menuTrue = 3
                    search.SearchWin = False
                    if maze.ListOfCells != None:
                        for cell in maze.ListOfCells: #type:ignore
                            del cell
                    del maze
                    del finishcell
                    del rules
                    

    elif menuTrue == 3:
        '''This is the menu the player is taken to when they have won the game
       
        When the player clicks the button to return to the menu, all important information about the game is reset so they can play again'''
        newscreen()
        winButton = Button("You win! Click to continue", 225,115,True,230,225)
        if winButton.checkClick():
            newscreen()
            pygame.time.wait(500)
            menuTrue = 0
            player.PlayerX = 0
            player.PlayerY = 0
            winButton.enabled = False
            maze = None
            player.Win = False
            if search!= None:
                search.SearchWin = False
            search = None
            DFSRunning = False
   
    elif menuTrue == 4:
        '''The scoreboard menu:
        Displays the saved scores'''
        newscreen()
        Displayscoreboard()
        ScoreboardInstructions = CreateRectangle(1,1,1,1,black,"Username:Score",Dark_Blue,2,30,30)
        ScoreboardYay = CreateRectangle(1,1,1,1,black,"Scoreboard",Dark_Blue,2,30,10)
        backButton = Button("Back", 450,50,True,465,70)
        if backButton.checkClick():
            newscreen()
            menuTrue = 0
            maze = None
            player.PlayerX = 0
            player.PlayerY = 0
            player.Win = False
            if search!= None:
                search.SearchWin = False
            search = None
            DFSRunning = False 

def Menu():
    startButton = Button("Start",  225, 115, True,280,150) #creates the start and quit buttons on the main menu screen
    quitbutton = Button("Quit", 225, 170, True,280,150) #Creates the quit button on the main menu screen

    ScoreboardButton = Button("Scoreboard", 225,225,True,255,150)

    if startButton.checkClick(): #Checks if the start button has been clicked
        global menuTrue #Makes the variable main menu callable anywhere in the program so it can be accessed in the checkMenu subroutine
        menuTrue = 1 #If the start button is clicked it will show that the main menu has been used and move to the Username menu
    elif quitbutton.checkClick(): #Checks if the quit button has been clicked
        pygame.quit() #Closes the pygame window
        pygame.time.delay(200) #Waits so the window has time to close and the window doesn't stay open
        exit() #Stops the code from running
    elif ScoreboardButton.checkClick():
        menuTrue = 4
       
def SetUsername():
    for screenrefresh in range(1): #Makes sure this only happens once
        screen.fill(black) #Fills the screen black to remove the buttons
    global UserNameInput #Makes sure the UserNameInput variable can be accessed from the event handling loop in the main game loop
    UserNameInput = True #Allows the variable Usertext (which records the players username) to be editied if this value is true
    username_rect = pygame.rect.Rect(200,108,185,32) #Sets the values for the box around where the player inputs their username to show where it will be
    pygame.draw.rect(screen,white,username_rect,2) #Draws the box around the player username input
    inputfont = pygame.font.SysFont('arialblack', 25)  #Sets what font the text should be
    text_surface = inputfont.render(usertext, True, (white)) #Makes the text input white
    screen.blit(text_surface, (205,115)) #Draws the text input on the screen
    EnterUsername = CreateRectangle(195,40,200,32,black,"Enter Your Username:",white, 5, 205, 47)#Creates a box with the text prompting the user to input their username
    UsernameValidation = CreateRectangle(195,75,200,32,black,"Username must be between 1 and 12 characters",white, 5, 105, 75) #Creates text to show that the username must be between 1 and 12 characters
    ContinueButton = Button("Continue", 245,170,True,255,95)
    if ContinueButton.checkClick() == True and len(usertext) > 0 and len(usertext) <= 12:
        checkUsername = CheckUser(usertext)
        if checkUsername:
            UserNameInput = False
            global menuTrue
            menuTrue = 2
            for i in range(1):
                newscreen()

def CheckUser(usertext):
    InvalidChar = (":")
    for i in usertext:
        if i in InvalidChar:
            return False
    return True

class CreateRectangle():
    def __init__(self,RectXpos,RectYpos,RectWidth,RectHeight,RectColour,Text,TextColour,fillet,TextXpos,TextYpos):
        '''Sets all of the parameters in the class and calls the function to draw the rectangle and the text. This section also uses polymorphism from the button class
        This class creates rectangles with text that cannot be clicked and are just for display'''
        self.RectXpos = RectXpos
        self.RectYpos = RectYpos
        self.RectWidth = RectWidth
        self.RectHeight = RectHeight
        self.RectColour = RectColour
        self.Text = Text
        self.TextColour = TextColour
        self.fillet = fillet
        self.TextXpos = TextXpos
        self.TextYpos = TextYpos
        self.draw()
       
    def draw(self):
        RectText = font.render(self.Text,True,self.TextColour)
        DrawRect = pygame.rect.Rect(self.RectXpos,self.RectYpos,self.RectWidth,self.RectHeight)
        pygame.draw.rect(screen,self.RectColour,DrawRect,0,self.fillet)
        screen.blit(RectText,(self.TextXpos,self.TextYpos))

class Button(): #This class was used from a youtube video by LeMaster Tech referenced in my NEA to explain how to create buttons in pygame.  https://www.youtube.com/watch?v=16DM5Eem0cI
    def __init__(self,text, xPosition, yPosition,enabled,TextXpos,Width):
        '''This sets all the parameters that were input in the class'''
        self.text = text #This is the text that will be put on the button
        self.xPosition = xPosition #The x position of the button on the screen
        self.yPosition = yPosition #The y position of the button on the screen
        self.enabled = enabled  #Checks if the button is enabled, so it can be pressed
        self.Width = Width
        self.TextXpos = TextXpos
        self.draw() #draws the button and text onto the screen


    def draw(self):
        '''Draws the buttons and text on the screen '''
        ButtonText = font.render(self.text, True, 'white') #Sets the font, colour of text
        RectButton = pygame.rect.Rect((self.xPosition,self.yPosition),(self.Width,35)) #Selects the position and size of the button
        if self.enabled: #Checks if the button is enabled
            if self.checkClick(): #Checks if the player has clicked
                pygame.draw.rect(screen, Light_Blue, RectButton,0,5) #Draws the rect with the selected settings to show its been clicked
            else:
                pygame.draw.rect(screen, Dark_Blue, RectButton,0,5) #If the button isn't clicked, nothing changes and it goes back to its original state
        else:
            pygame.draw.rect(screen, black, RectButton,0,5) #Makes the button black which means the player cannot see it
            ButtonText = font.render(self.text, True, 'Black') #Makes the text black to make it invisible
        screen.blit(ButtonText, (self.TextXpos, self.yPosition + 10)) #Draws the text on the screen and shifts it to the position chosen
   
    def checkClick(self):
        '''Checks the cursor position and if the left mouse button has been pressed and compares it to the coordinates of the buttons and checks if they have been clicked'''
        mousePos = pygame.mouse.get_pos() #Gets the position of the mouse cursor
        leftClick = pygame.mouse.get_pressed()[0] #Checks if the mouse cursor has been clicked, the 0 checks if the left mouse button has been pressed
        RectButton = pygame.rect.Rect((self.xPosition,self.yPosition),(150,35)) #Selects the position and size of the button
        if leftClick and RectButton.collidepoint(mousePos) and self.enabled: #If the mouse is clicked and the cursor is over the button
            return True
        else:
            return False

def newscreen():
    '''Fills the screen black to remove any other objects on screen'''
    for newscreen in range(1):
        screen.fill(black)

def UpdateScoreboard():
    '''Scoreboard is set to an empty dictionary'''
    Scoreboard = {}
    try:
        '''The scoreboard file is opened and the contents are read and appended to the scoreboard dictionary
       
        The score is sorted into descending order with a priority queue using SortScoreboard()'''
        ScoreboardFile = open("Scoreboard.txt","r")
        for line in ScoreboardFile:
            username, score = line.strip().split(":")
            Scoreboard[username] = int(score)
        if usertext not in Scoreboard:
            Scoreboard[usertext] = PlayerScore
            #If the username doesn't already exist add the username and score
        elif PlayerScore < Scoreboard[usertext]:
            Scoreboard[usertext] = PlayerScore
            #If the username does exist
        Scoreboard = SortScoreboard(Scoreboard)
        ScoreboardFile.close()
        '''Writes the new usernames to the scoreboard file and closes it'''
        ScoreboardFile = open("Scoreboard.txt","w")
        for username, score in Scoreboard:
            ScoreboardFile.write(f"{username}:{score}\n")
        ScoreboardFile.close()


    except FileNotFoundError:
        #Creates a new file called Scoreboard.txt if it doesn't already exist
        ScoreboardFile = open("Scoreboard.txt", "x")
        ScoreboardFile.close()
        #Opens the new file and writes the new score(s) to it
        ScoreboardFile = open("Scoreboard.txt", "w")
        ScoreboardFile.write(f"{usertext}:{PlayerScore}\n")

def SortScoreboard(Scoreboard):
    '''Sorts the scoreboard using a priority queue'''
    ScorePriorityQueue = []
    #Creates an empty queue
    if len(Scoreboard) > 1:
        #checks if there are more than 1 items in the scoreboard
        for username, score in Scoreboard.items():
            #iterates through the scoreboard with the username and score combined into a tuple
            Inserted = False
            for j in range(len(ScorePriorityQueue)):
                #iterates through the location of each item in the queue
                if score > ScorePriorityQueue[j][1]:
                    #if the score is greater than the value of the current item in the queue
                    ScorePriorityQueue.insert(j,(username, score))
                    #insert it at this index position and move all other items up one index
                    Inserted = True
                    #shows it has been inserted
                    break
            if not Inserted:
                #if the index hasn't been inserted into the queue after the iteration it puts it at the end of the queue
                ScorePriorityQueue.append((username, score))
            while len(ScorePriorityQueue) > 10:
                #while the length of the queue is greater than 10, pop the first item until you have 10 or less items
                ScorePriorityQueue.pop(0)
        else:
            #if the queue is the correct size return the scoreboard
            return ScorePriorityQueue
    else:
        #returns if there is only one or less items because it doesn't need to be sorted
        return list(Scoreboard.items())

def Displayscoreboard():
    Scorefont = pygame.font.SysFont("arialblack", 50)
    #Puts all of the items in the scoreboard into an array
    DisplayedScoreboard = []
    try:
        DisplayingScore = open("Scoreboard.txt","r")
        for line in DisplayingScore:
            DisplayedScoreboard.append(line)
        #reverses the scoreboard so the fastest times go first and i am still using a priority queue
        DisplayedScoreboard.reverse()
        #The y coordinate of the text being displayed is set to 50
        Y = 50
        for index in DisplayedScoreboard:
            index = index.strip()
            ScoreboardText = Scorefont.render(index,True,Dark_Blue)
            screen.blit(ScoreboardText,(30,Y))
            #The score is put on screen and the y coordinate is increased by 40 so the next score is displayed beneath it
            Y += 40
    except FileNotFoundError:
        #Creates a new file called Scoreboard.txt if it doesn't already exist
        ScoreboardFile = open("Scoreboard.txt", "x")
        ScoreboardFile.close()

player = Player(0,0,35,2)
search = None
DFSRunning = False
LastDFSStep = 0
canMove = True
while running:
    '''Runs for the whole program and handles all the events like key presses and the quit button on the window'''
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        '''When the user has to input a username this checks for any key inputs'''
        if event.type == pygame.KEYDOWN and UserNameInput == True:
            if event.key == pygame.K_BACKSPACE:
                usertext = usertext[:-1]
            else:
                if event.key == pygame.K_RETURN:
                    pass
                else:
                    usertext += event.unicode
        '''Controls the movement of the player'''
        if event.type == pygame.KEYDOWN and not UserNameInput and isPlayer == 1 and not player.Win:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                player.UpPressed = True
                if canMove:
                    if maze != None:
                        player.CheckMove(maze.ListOfCells)
                        player.UpPressed = False
                        canMove = False
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                player.LeftPressed = True
                if canMove:
                    if maze != None:
                        player.CheckMove(maze.ListOfCells)
                        player.LeftPressed = False
                        canMove = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                player.RightPressed = True
                if canMove:
                    if maze != None:
                        player.CheckMove(maze.ListOfCells)
                        player.RightPressed = False
                        canMove = False
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                player.DownPressed = True
                if canMove:
                    if maze != None:
                        player.CheckMove(maze.ListOfCells)
                        player.DownPressed = False
                        canMove = False


        if event.type == pygame.KEYUP and not UserNameInput and isPlayer == 1:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                player.UpPressed = False
                canMove = True
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                player.LeftPressed = False
                canMove = True
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                player.RightPressed = False
                canMove = True
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                player.DownPressed = False
                canMove = True
    checkMenu()
    clock.tick(60) #sets fps ceiling to 60
    pygame.display.flip()
