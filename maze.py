import random
from io import StringIO
from collections import namedtuple

GridLocation = namedtuple('GridLocation','x y')

class GoalLocation:
    """A goal location in the grid. 

    (A root of a tree in the context of union-find whose value is a GridLocation.)"""
    def __init__(self, location):
        self.location = location
    def __str__(self):
        return "<Goal location: " + str(self.location) + ">"
    def goal(self, grid):
        return self.location

class CanAccess:
    """A location that connects to some goal in the grid. 

    (An intermediate node in the context of union find.)"""
    def __init__(self, to):
        self.accessTo = to
    def __str__(self):
        return "<Can get to location " + str(self.accessTo) + ">"
    def goal(self, grid):
        """(Normalise in the context of union-find, which destructively links us directly to
        our root node.)
        """
        goal = grid[self.accessTo]
        self.accessTo = goal
        return goal

class GoalGrid:
    """A grid, each of whose elements is initially a goal location."""
    def __row(self, j, width):
        return [GoalLocation(GridLocation(i,j)) for i in range(0,width)]
    def __init__(self, width, height):
        it = [ self.__row(j, width) for j in range(0,height) ]
        self.rows = list(it)
    def setGoal(self, p1, p2):
        """Set p1's goal to p2's. 

        (Union in the context of union-find.)"""
        q1 = self[p1]
        self.rows[q1.y][q1.x] = CanAccess(p2)
    def __getitem__(self, p):
        """Get p's goal."""
        return self.rows[p.y][p.x].goal(self)

class Grid:
    """A two dimensional grid indexed by GridLocations."""
    def __init__(self, init, width, height):
        self.grid = [ [ init.copy() for i in range(0,width) ]
                      for j in range(0, height) ]
    def __getitem__(self, p):
        return self.grid[p.y][p.x]
    def __setitem__(self, p, x):
        self.grid[p.y][p.x] = x

def compactToBlock(p):
    return GridLocation(p.x*2 + 1, p.y*2 + 1)

def blockToCompact(p):
    return GridLocation(p.x // 2, p.y // 2) if p.x % 2 == 1 and p.y % 2 == 1 else None

class Maze:
    """A randomly generated standard maze of the given width and height.

    >>> myMaze = Maze(5,6)

    gives you a new random maze of width 5 and height 10. To quickly view this maze,
    you can use:
    
    >>> print(myMaze.draw())
    ***********
    * *   *   *
    * * *** ***
    *         *
    * *** * ***
    * * * *   *
    *** ***** *
    *   * *   *
    * * * *** *
    * * *     *
    * * * *** *
    * *   *   *
    ***********

    The top-left of the maze is at GridLocation(0,0). As we move East (right), we
    increase our x-coordinate. As we move South (down), we increase our y-coordinate.

    This maze has been drawn using a "block representation", where walls are
    "fat". So while we asked for a maze of width 5 and height 6, we actually drew it
    so that it is myMaze.blocksWidth == 11 characters across and myMaze.blocksHeight
    == 13 characters down. That way, we could represent the maze walls by the
    character '*'.

    We can query whether or not there is a wall block at any location in this
    representation using hasBlockAt:

    >>> myMaze.hasBlockAt(GridLocation(5,9))
    False

    Let's mark this empty location on the map with an 'X':

    ***********
    * *   *   *
    * * *** ***
    *         *
    * *** * ***
    * * * *   *
    *** ***** *
    *   * *   *
    * * * *** *
    * * *X    *
    * * * *** *
    * *   *   *
    ***********

    We can verify that the block's around us are as depicted:

    >>> myMaze.hasBlockAt(GridLocation(4,8)) # Northwest
    True
    >>> myMaze.hasBlockAt(GridLocation(5,8)) # North
    False
    >>> myMaze.hasBlockAt(GridLocation(6,8)) # Northeast
    True
    >>> myMaze.hasBlockAt(GridLocation(4,9)) # West
    True    
    >>> myMaze.hasBlockAt(GridLocation(6,9)) # East
    False
    >>> myMaze.hasBlockAt(GridLocation(4,9)) # Southwest
    True
    >>> myMaze.hasBlockAt(GridLocation(5,10)) # South
    False
    >>> myMaze.hasBlockAt(GridLocation(6,10)) # Southeast
    True

    Now there is also a "compact representation" where walls are "thin". Here, our
    location X on our map can be found using the function blockToCompact:

    >>> blockToCompact(GridLocation(5,9))
    GridLocation(x=2, y=4)

    We can identify the walls at this location using waysFrom:

    >>> myMaze.waysFrom(GridLocation(2,4))

    ['E', 'S', 'N']

    Here, we are told we can move:

    1) East to GridLocation(3,4)
    2) South to GridLocation(2,5)
    3) North to GridLocation(2,3)

    but we cannot move West. This is because:

    1) there is no East/West wall between locations GridLocation(2,4) and
    GridLocation(3,4)
    2) there is no North/South wall between locations GridLocation(2,4) and
    GridLocation(2,5)
    3) there is no North/South wall between locations GridLocation(2,4) and
    GridLocation(2,3)
    4) there is an East/West wall between locations GridLocation(2,4) and
    GridLocation(2,4).

    So here, walls are "thin" and are inserted directly between locations, rather
    than being placed as blocks at locations,

    To convert a coordinate GridLocation(x,y) in the compact representation to the
    block representation, use

    >>> compactToBlock(GridLocation(2,4))
    GridLocation(x=5, y=9)

    To convert back, use:

    >>> blockToCompact(GridLocation(5,9))
    GridLocation(x=2, y=4)

    >>> compactToBlock(GridLocation(2,4))
    GridLocation(x=5, y=9)

    Note that not all locations in the block representation are valid locations in
    the compact representation. If you try to convert these, you'll get None.

    >>> compactToBlock(GridLocation(5,8))

    For creating a maze in Minecraft, use the block representation.
    """
    def __init__(self, width, height):
    """Both width and height are assumed to be positive integers. Assume bad
    things if you provide any other values."""
        self.width        = width
        self.height       = height
        self.blocksWidth  = self.width * 2 + 1
        self.blocksHeight = self.height * 2 + 1
        goalGrid          = GoalGrid(width,height)
        self.wayGrid      = Grid([],width,height)
        walls             = [ (i,j,w)
                              for w in "ES"
                              for i in range(0,width)
                              for j in range(0,height) ]
        random.shuffle(walls)
        for (x,y,w) in walls:
            if (w == 'E' and x < width-1
                and not goalGrid[GridLocation(x,y)] == goalGrid[GridLocation(x+1,y)]):
                goalGrid.setGoal(GridLocation(x,y),GridLocation(x+1,y))
                self.wayGrid[GridLocation(x,y)].append(w)
            if (w == 'S' and y < height-1
                and not goalGrid[GridLocation(x,y)] == goalGrid[GridLocation(x,y+1)]):
                    goalGrid.setGoal(GridLocation(x,y),GridLocation(x,y+1))
                    self.wayGrid[GridLocation(x,y)].append(w)
    def waysFrom(self,p):
        """The directions we can move in the maze from the GridLocation p in the compact
        representation.

        Returns a list of compass directions, given by the characters 'N', 'E', 'S' and 'W'.
        """
        if p.x >= 0 and p.x < self.width and p.y >= 0 and p.y < self.height:
            ways = self.wayGrid[p][:]
            if p.x > 0 and 'E' in self.wayGrid[GridLocation(p.x - 1, p.y)]:
                ways += ['W']
            if p.y > 0 and 'S' in self.wayGrid[GridLocation(p.x, p.y - 1)]:
                ways += ['N']
            return ways
        else:
            return []
    def hasBlockAt(self,p):
        """Whether there is a block at GridLocation p in the block representation."""
        return (p.x < 0 or p.y < 0 or p.x >= self.blocksWidth or p.y >= self.blocksHeight
                or (p.x % 2 == 0 and p.y % 2 == 0)
                or (p.x % 2 == 0 and p.y % 2 == 1
                    and not 'E' in self.wayGrid[GridLocation((p.x-1)//2,p.y//2)])
                or (p.x % 2 == 1 and p.y % 2 == 0
                    and not 'S' in self.wayGrid[GridLocation(p.x//2,(p.y-1)//2)]))
    def __drawRow(self,y,strio,block,space):
        for x in range(0,self.blocksWidth):
            strio.write(block if self.hasBlockAt(GridLocation(x,y)) else space)
    def drawBlocks(self, block='*', space=' '):
        """Pretty-print the maze in block representation using optional block and space
        characters."""
        strio = StringIO()
        self.__drawRow(0,strio,block,space)
        for y in range(1,self.blocksHeight):
            strio.write("\n")
            self.__drawRow(y,strio,block,space)
        thestr = strio.getvalue()
        strio.close()
        return thestr
