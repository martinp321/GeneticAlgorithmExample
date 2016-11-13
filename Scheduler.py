#mutation - randomly change a bit of the program
#crossover - take the best programs and reuse bits amongst eachother

#at each stage, calculate success via a fitness func
# each stage, is a generation

# termination condition ends the entire program
# - perfect solution has been found
# - good enough solution found
# - solution hasnt improved for several generation
# - number of generations reached a specific limit

from random import random, randint, choice
from copy import deepcopy
from math import log


class Node(object):
    """
    The class for function nodes (nodes with children). This is initialized with an
    Fwrapper . When evaluate is called, it evaluates the child nodes and then applies
    the function to their results.
    """
    def __init__(self, fw, children):
        self.func = fw.func
        self.name = fw.name
        self.children = children

    def evaluate(self, inp):
        return self.func([n.evaluate(inp) for n in self.children])

    def display(self,indent=0):
        print (' ' * indent) + self.name
        for c in self.children:
            c.display(indent + 1)

class ParamNode(object):
    def __init__(self, idx):
        self.idx = idx

    def evaluate(self, inp):
        """ returns the parameter specified by idx. """
        return inp[self.idx]

    def display(self, indent=0):
        print '{}p{}'.format(' ' * indent, self.idx)
    
class ConstNode(object):
    def __init__(self, v):
        self.v = v

    def evaluate(self, inp):
        """ returns the value with which it was initialized. """
        return self.v

    def display(self, indent=0):
        print '{}c{}'.format(' ' * indent, self.v)

class Fwrapper(object):
    """
    A wrapper for the functions that will be used on function nodes. Its member
    variables are the name of the function, the function itself, and the number of
    parameters it takes.
    """
    def __init__(self, func, childCount, name):
        self.func = func
        self.childcount = childCount
        self.name = name


addw = Fwrapper(lambda x:x[0] + x[1], 2, 'ADD')
subw = Fwrapper(lambda x:x[0] - x[1], 2, 'SUB')
mulw = Fwrapper(lambda x:x[0] * x[1], 2, 'MUL')
gtw = Fwrapper(lambda  x:x[0] > x[1], 2, 'GT')
ifw = Fwrapper(lambda  x:x[1] if x[0] else x[2], 3, 'IF')
flist = [addw, mulw, ifw, gtw, subw]


#def func(x,y):
#    if x>3:
#        return y + 5
#    else:
#        return y - 2

def exampleTree():
    return Node(ifw, 
                [Node(gtw, [ParamNode(0), ConstNode(3)]), 
                 Node(addw, [ParamNode(1), ConstNode(5)]), 
                 Node(subw, [ParamNode(1), ConstNode(2)])])

def makerandomtree(paramCount,maxdepth=4,funcProb=0.5,paramProb=0.6):
    if random() < funcProb and maxdepth > 0:
        f = choice(flist)
        children = [makerandomtree(paramCount, maxdepth - 1, funcProb, paramProb) for i in range(f.childcount)]
        return Node(f, children)
    elif random() < paramProb:
        return ParamNode(randint(0,paramCount - 1))
    else:
        return ConstNode(randint(0,10))

def hiddenfunction(x,y):
    return x ** 2 + 2 * y + 3 * x + 5

def buildhiddenset():
    rows = []
    for i in range(200):
        x = randint(0, 40)
        y = randint(0, 40)
        rows.append([x, y, hiddenfunction(x,y)])
    return rows

def scorefunction(tree,s):
    return sum(abs(tree.evaluate([data[0],data[1]])-data[2]) for data in s)

def mutate(tree, paramCount ,probChange=0.1):
    if random()<probChange:
        return makerandomtree(paramCount)
    else:
        result = deepcopy(tree)
        if isinstance(tree, Node):
            result.children=[mutate(c, paramCount, probChange) for c in tree.children]
        return result

def crossover(tree1, tree2, probSwap=0.5, top=1):
    if random()<probSwap and not top:
        return deepcopy(tree2)
    else:
        result=deepcopy(tree1)
        if isinstance(tree1, Node) and isinstance(tree2, Node):
            result.children=[crossover(c,choice(tree2.children),probSwap,0) for c in tree1.children]
        return result

def evolve(paramCount, popSize, rankFunc, maxgen=500, mutationrate=0.1, breedingrate=0.4, pexp=0.7, pnew=0.05):
    # Returns a random number, tending towards lower numbers. The lower pexp
    # is, more lower numbers you will get
    def selectindex():
        return int(log(random())/log(pexp))

    # Create a random initial population
    population=[makerandomtree(paramCount) for i in range(popSize)]

    for i in range(maxgen):
        scores = rankFunc(population)
        print scores[0][0]
        if scores[0][0]==0: break
        # The two best always make it

        newpop=[scores[0][1],scores[1][1]]

        # Build the next generation
        while len(newpop) < popSize:
            if random()>pnew:
                newpop.append(mutate(crossover(scores[selectindex()][1], scores[selectindex()][1], probSwap=breedingrate), paramCount, probChange=mutationrate))
            else:
                # Add a random node to mix things up
                newpop.append(makerandomtree(paramCount))
        population=newpop
    scores[0][1].display()
    return scores[0][1]

def getrankfunction(dataset):
    def rankfunction(population):
        scores=[(scorefunction(t, dataset), t) for t in population]
        scores.sort()
        return scores
    return rankfunction

def main():
    getrankfunction(buildhiddenset())
    evolve(2,500,rf,mutationrate=0.2,breedingrate=0.1,pexp=0.7,pnew=0.1)