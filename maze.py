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
    """A randomly generated standard maze."""
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
