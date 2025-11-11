import pygame
import numpy
import sys


"""
GAME RULES
Black moves first
If you CANNOT make a move to outflank and flip a disc, your turn is skipped
If you CAN make a move, you have to 
Any numbers of discs in any direction can be flipped by a single outflank
Your own color cannot be skipped over to outflank an opposing disk
Discs can only be flanked as a direct result of a move and must fall in the direct line of the disc placed down
All discs must be flipped in an outflank
If a player runs out of disks, he uses his opponents
When neither player can play, the game is over
The player with the majority of his color discs wins
"""


def initializeGame():
    positionArr = numpy.full((8,8), ' ', dtype=str)
    positionArr[3][3] = 'W' 
    positionArr[3][4] = 'B'
    positionArr[4][3] = 'B' 
    positionArr[4][4] = 'W' 
    positionArr[2][3] = "G"
    positionArr[3][2] = "G"
    positionArr[4][5] = "G"
    positionArr[5][4] = "G"

    gameBoardPositionsArr = [[[0 for k in range(2)] for j in range(8)] for i in range(8)]
    rowPosition = 50
    colPosition = 50
    for i in range(8):
        for j in range(8):
            gameBoardPositionsArr[i][j][0] = colPosition
            gameBoardPositionsArr[i][j][1] = rowPosition
            colPosition+=100
        colPosition=50
        rowPosition+=100

    return(positionArr, gameBoardPositionsArr)

def gameStart():
    return True

def AIMove(pruning):
    global positions, gameRunning
    
    if not gameRunning:
        return
    
    # find best move
    best_move = None
    best_score = -float('inf') if positions.player == 'B' else float('inf')
    
    positions.checkMoves()
    
    # try and score each move
    for i in range(8):
        for j in range(8):
            if positions.positionArr[i][j] == "G":
                newPos = GameBoard(positions.positionArr.copy(), positions.gameBoardPositionsArr, positions.player)
                newPos.placePiece(i, j, positions.player)
                newPos.player = 'B' if positions.player == 'W' else 'W'
                
                # Score this move
                if (pruning==True):
                    score = minimaxPruning(newPos, depth=3, maximizingPlayer=False)
                elif (pruning==False):
                    score = minimax(newPos, depth=3, maximizingPlayer=False)
                
                if positions.player == 'B' and score > best_score:
                    best_score = score
                    best_move = (i, j)
                elif positions.player == 'W' and score < best_score:
                    best_score = score
                    best_move = (i, j)
    
    # Make the best move
    if best_move:
        positions.placePiece(best_move[0], best_move[1], positions.player)

    if positions.player == 'B':
        positions.player = 'W'
        return  
    if positions.player == 'W':
         positions.player = 'B'
         return 


def minimax(positions, depth, maximizingPlayer):
    # root node or lost
    if depth == 0 or isGameOver(positions):
        return evaluatePosition(positions)

    if maximizingPlayer:
        maxEval = -100
        for child in getChildPositions(positions):
            eval = minimax(child, depth - 1, False)
            maxEval = max(maxEval, eval)
        return maxEval
    else:
        minEval = 100
        for child in getChildPositions(positions):
            # recurse back to maximizing player
            eval = minimax(child, depth - 1, True)
            minEval = min(minEval, eval)
        return minEval
            

def minimaxPruning(positions, depth, maximizingPlayer, alpha=-100, beta=100):
    if depth == 0 or isGameOver(positions):
        return evaluatePosition(positions)

    if maximizingPlayer:
        value = -100
        for child in getChildPositions(positions):
            value = max(value, minimaxPruning(child, depth - 1, False, alpha, beta))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = 100
        for child in getChildPositions(positions):
            value = min(value, minimaxPruning(child, depth - 1, True, alpha, beta))
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

def isGameOver(positions):
    # Save current player
    original_player = positions.player
    
    # Check if current player has moves
    positions.player = original_player
    positions.checkMoves()
    hasMovesCurrentPlayer = any(positions.positionArr[i][j] == "G" for i in range(8) for j in range(8))
    
    # Check if opponent has moves
    opponent = 'B' if original_player == 'W' else 'W'
    positions.player = opponent
    positions.checkMoves()
    hasMovesOpponent = any(positions.positionArr[i][j] == "G" for i in range(8) for j in range(8))
    
    # Restore original player
    positions.player = original_player
    
    return not hasMovesCurrentPlayer and not hasMovesOpponent

def evaluatePosition(positions):
    blackCount = numpy.count_nonzero(positions.positionArr == 'B')
    whiteCount = numpy.count_nonzero(positions.positionArr == 'W')
    
    # positive favors black, negative favors white
    return blackCount - whiteCount

def getChildPositions(positions):
    children = []
    positions.checkMoves()
    
    # Find all valid moves (marked with "G")
    for i in range(8):
        for j in range(8):
            if positions.positionArr[i][j] == "G":
                # Create a copy of the position
                newPos = GameBoard(positions.positionArr.copy(), positions.gameBoardPositionsArr, positions.player)
                # Make the move
                newPos.placePiece(i, j, positions.player)
                # Switch player
                newPos.player = 'B' if positions.player == 'W' else 'W'
                children.append(newPos)
    
    return children

def generateMoveSequences(rootPos, depth):
    sequences = []
    rootPos.checkMoves()
    for r in range(8):
        for c in range(8):
            if rootPos.positionArr[r][c] == "G":
                newPos = GameBoard(rootPos.positionArr.copy(), rootPos.gameBoardPositionsArr, rootPos.player)
                color = rootPos.player
                newPos.placePiece(r, c, color)
                newPos.player = 'B' if color == 'W' else 'W'
                recurseSequences(newPos, depth - 1, [(color, r, c)], sequences)
    return sequences

def recurseSequences(pos, depth, moves, sequences):
    if depth == 0 or isGameOver(pos):
        sequences.append((moves, evaluatePosition(pos)))
        return
    pos.checkMoves()
    children_found = False
    for r in range(8):
        for c in range(8):
            if pos.positionArr[r][c] == "G":
                children_found = True
                newPos = GameBoard(pos.positionArr.copy(), pos.gameBoardPositionsArr, pos.player)
                color = pos.player
                newPos.placePiece(r, c, color)
                newPos.player = 'B' if color == 'W' else 'W'
                recurseSequences(newPos, depth - 1, moves + [(color, r, c)], sequences)
    if not children_found:
        sequences.append((moves, evaluatePosition(pos)))

def showSequencesWindow():
    global surface
    if not gameRunning:
        return
    depth = 4  # same as AIMove/minimax depth
    sequences = generateMoveSequences(positions, depth)
    sequences.sort(key=lambda x: x[1], reverse=True)
    seq_surface = pygame.display.set_mode((900, 700))
    pygame.display.set_caption("Move Sequences")
    font_seq = pygame.font.SysFont('Consolas', 18)
    line_h = 22
    offset = 0
    rendered = []
    for mv, score in sequences:
        mv_txt = " -> ".join(f"{c}({r},{col})" for (c, r, col) in mv)
        rendered.append(font_seq.render(f"{score:+3d} | {mv_txt}", True, (255,255,255)))
    running_seq = True
    clock_local = pygame.time.Clock()
    while running_seq:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running_seq = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running_seq = False
                elif e.key == pygame.K_UP:
                    offset = max(0, offset - 1)
                elif e.key == pygame.K_DOWN:
                    offset = min(max(0, len(rendered) - 1), offset + 1)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 4:
                    offset = max(0, offset - 1)
                elif e.button == 5:
                    offset = min(max(0, len(rendered) - 1), offset + 1)
        seq_surface.fill((30,30,30))
        viewable = (700 - 50) // line_h
        start = offset
        end = min(len(rendered), start + viewable)
        y = 40
        for i in range(start, end):
            seq_surface.blit(rendered[i], (10, y))
            y += line_h
        pygame.display.flip()
        clock_local.tick(60)
    # Restore original window
    surface = pygame.display.set_mode((1280, 800))
    pygame.display.set_caption("Othello")

class GameBoard:
    def __init__(self, positionArr, gameBoardPositionsArr, player, piecesLeft=64):
        self.positionArr = positionArr
        self.gameBoardPositionsArr = gameBoardPositionsArr
        self.player = player
        self.piecesLeft = piecesLeft

    def checkMoves(self):
        # Clear previous valid moves
        for i in range(8):
            for j in range(8):
                if self.positionArr[i][j] == "G":
                    self.positionArr[i][j] = ' '
        
        opponent = 'B' if self.player == 'W' else 'W'            
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        # Check each empty cell
        for row in range(8):
            for col in range(8):
                if self.positionArr[row][col] != ' ':
                    continue
                
                # Check all 8 directions
                for dr, dc in directions:
                    # Find if opponent piece is next to cur piece
                    nr, nc = row + dr, col + dc
                    if nr < 0 or nr >= 8 or nc < 0 or nc >= 8:
                        continue
                    if self.positionArr[nr][nc] != opponent:
                        continue
                    
                    # Find edge or same color piece
                    nr, nc = nr + dr, nc + dc
                    while 0 <= nr < 8 and 0 <= nc < 8:
                        if self.positionArr[nr][nc] == ' ':
                            break
                        if self.positionArr[nr][nc] == self.player:
                            # Valid move found
                            self.positionArr[row][col] = "G"
                            break
                        nr, nc = nr + dr, nc + dc
        
        return self.positionArr

    def drawPieces(self):
        for i in range(8):
            for j in range(8):
                if self.positionArr[i][j] == "W":
                    pygame.draw.circle(board, (255,255,255), self.gameBoardPositionsArr[i][j], 40, width=75)
                if self.positionArr[i][j] == "B":
                    pygame.draw.circle(board, (0,0,0), self.gameBoardPositionsArr[i][j], 40, width=75)
                if self.positionArr[i][j] == "G":
                    pygame.draw.circle(board, (0,255,0), self.gameBoardPositionsArr[i][j], 40, width=75)

    def checkClick(self, mousePos):
        #bounds check
        mx = mousePos[0] - 240
        my = mousePos[1] - 0
        if mx < 0 or my < 0 or mx > 800 or my > 800:
            return
        
        # check if potential move clicked
        for i in range(8):
            for j in range(8):
                if self.positionArr[i][j] != "G":
                    continue
                cx = int(self.gameBoardPositionsArr[i][j][0])
                cy = int(self.gameBoardPositionsArr[i][j][1])
                dx = mx - cx
                dy = my - cy
                if dx*dx + dy*dy <= 40*40:
                    # move clicked
                    clicked = pygame.mouse.get_pressed(3)
                    if clicked[0] == True:
                        if self.player == 'B':
                            self.placePiece(i, j, "B")
                            self.player = 'W'
                            return
                        if self.player == 'W':
                            self.placePiece(i, j, "W")
                            self.player = 'B'
                            return           

    def placePiece(self, row, column, color):
        self.positionArr[row][column] = color
        self.piecesLeft -= 1
        self.checkOutFlanked(row, column, color)

    def checkOutFlanked(self, row, column, color):
        opponent = 'B' if color == 'W' else 'W'
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        # check row, columns, and diagonals for opponent pieces
        for dr, dc in directions:
            piecesToFlip = []
            nr, nc = row + dr, column + dc
            
            # get opponent pieces to flip
            while 0 <= nr < 8 and 0 <= nc < 8 and self.positionArr[nr][nc] == opponent:
                piecesToFlip.append((nr, nc))
                nr += dr
                nc += dc
            
            # if own piece at end, flip opponent pieces
            if 0 <= nr < 8 and 0 <= nc < 8 and self.positionArr[nr][nc] == color:
                for flip_row, flip_col in piecesToFlip:
                    self.positionArr[flip_row][flip_col] = color
    
    
class Button():
    def __init__(self, x, y, width, height, buttonText, onclickFunction, onePress=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.buttonText = buttonText
        self.onclickFunction = onclickFunction
        self.onePress = onePress
        self.alreadyPressed = False
        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.buttonSurf = font.render(buttonText, True, (20, 20, 20))
        buttons.append(self)

        self.fillColors = {
            'normal': '#ffffff',
            'hover': '#666666',
            'pressed': '#333333',
        }

    def process(self):
        mousePos = pygame.mouse.get_pos()
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if self.onePress:
                    result = self.onclickFunction()
                    return result
                elif not self.alreadyPressed:
                    result = self.onclickFunction()
                    self.alreadyPressed = True
                    return result
            else:
                self.alreadyPressed = False
        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
            self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
        ])
        surface.blit(self.buttonSurface, self.buttonRect)


arrs = initializeGame()
positions = GameBoard(arrs[0], arrs[1],'B')
# print(positions.positionArr)
# print(positions.gameBoardPositionsArr)

# --- RENDER GAME --- #
pygame.init()
# Main Game Screen
surface = pygame.display.set_mode((1280, 800))

#Game board surface
board = pygame.Surface((800,800), pygame.SRCALPHA)

gameBoardColor = pygame.Color(80,64,51)
gameSidesColor = pygame.Color(51,25,0)
font = pygame.font.SysFont('Arial', 40)
buttons = []
Button(1060, 20, 200, 100, 'New Game', gameStart)
# FIX: pass callables so AIMove runs on click, not at import time
Button(1060, 130, 200, 100, 'AI Play', lambda: AIMove(pruning=False), onePress=True)
Button(1060, 240, 200, 100, 'AI Pruning', lambda: AIMove(pruning=True), onePress=True)
Button(1060, 350, 200, 100, 'Sequences', showSequencesWindow, onePress=True)

curTurnSurface = pygame.Surface((220,100))
curTurnContainer = pygame.Rect(10, 10, 220, 100)


clock = pygame.time.Clock()
running = True
gameRunning = False
dt = 0

linesY = [(0,100),(0,200),(0,300),(0,400),(0,500),(0,600),(0,700),(0,800)]
linesX = [(100,0),(200,0),(300,0),(400,0),(500,0),(600,0),(700,0),(800,0)]

gameResultText = None  # winner text

def endGame():
    global gameResultText
    if gameResultText:
        return
    blackCount = numpy.count_nonzero(positions.positionArr == 'B')
    whiteCount = numpy.count_nonzero(positions.positionArr == 'W')
    if blackCount > whiteCount:
        gameResultText = f"Black Wins"
    elif whiteCount > blackCount:
        gameResultText = f"White Wins"
    else:
        gameResultText = f"Tie"

# Game Initialization 
while running:
    surface.fill(gameSidesColor)
    board.fill(gameBoardColor)
    #Draw gameboard lines
    for line in linesY:
        pygame.draw.lines(board, "black", False, [line, (800, line[1])], width=4)

    for line in linesX:
        pygame.draw.lines(board, "black", False, [line, (line[0], 800)], width=4)   

    if (gameRunning):
        positions.checkMoves()
        positions.drawPieces()
    
    for button in buttons:
        result = button.process()
        if result == True:
            if button.buttonText == 'New Game':
                arrs = initializeGame()
                positions = GameBoard(arrs[0], arrs[1],'B')
                gameRunning = result
            elif button.buttonText == 'AI play':
                AIMove(pruning=False)
            elif button.buttonText == 'AI with Pruning':
                AIMove(pruning=True)

    if positions.player == "B":
        curTurnSurface.fill(gameSidesColor)
        curTurnText = font.render("Turn: Black", True, (255,255,255))
        curTurnSurface.blit(curTurnText, [ curTurnSurface.get_rect().width/2 - curTurnText.get_rect().width/2, curTurnSurface.get_rect().height/2 - curTurnText.get_rect().height/2 ])
        surface.blit(curTurnSurface, curTurnContainer)
    elif positions.player == "W":
        curTurnSurface.fill(gameSidesColor)
        curTurnText = font.render("Turn: White", True, (255,255,255))
        curTurnSurface.blit(curTurnText, [ curTurnSurface.get_rect().width/2 - curTurnText.get_rect().width/2, curTurnSurface.get_rect().height/2 - curTurnText.get_rect().height/2 ])
        surface.blit(curTurnSurface, curTurnContainer)

    # trigger endGame when board full or pieces exhausted
    if positions.piecesLeft <= 0 or not any(positions.positionArr[r][c] == ' ' for r in range(8) for c in range(8)):
        endGame()

    # draw winner box if gameResultText set
    if gameResultText:
        resultSurf = pygame.Surface((220,140))
        resultSurf.fill(gameSidesColor)
        pygame.draw.rect(resultSurf, (255,255,255), resultSurf.get_rect(), 2)
        title = font.render("Game Over", True, (255,215,0))
        winner = font.render(gameResultText, True, (255,255,255))
        resultSurf.blit(title, (resultSurf.get_width()/2 - title.get_width()/2, 10))
        resultSurf.blit(winner, (resultSurf.get_width()/2 - winner.get_width()/2, 70))
        surface.blit(resultSurf, (10, 120))

    surface.blit(board, (240,0))
        
    # flip() the display to put your work on screen
    pygame.display.flip()
    clock.tick(60)

    mousePos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        positions.checkClick(mousePos)



pygame.quit()

