#!/usr/bin/env python
from carbon.helpers import curry
from carbon.enumeration import Enumeration
from carbon.enumeration import EnumItem
from carbon.helpers import invertDict
from carbon.helpers import nestedproperty
from carbon.seqtostring import seqToString
from carbon.helpers import sortDict
from copy import copy
from copy import deepcopy
from iron.delegator import Delegator
from operator import add
from random import randint
from random import seed
from random import shuffle
from UserString import MutableString
import logging
import types
import sys

Delegator.STATE_HANDLER_FORMAT         = '{1}State_{0}Event'
Delegator.DEFAULT_STATE_HANDLER_FORMAT = '{1}State_defaultEvent'
Delegator.EVENT_HANDLER_FORMAT         = '{0}Event'
Delegator.DEFAULT_EVENT_HANDLER_FORMAT = 'defaultEvent'

class IllException(Exception): pass

class _AlignmentEnumeration(Enumeration):
    __opposites = []

    def __init__( self ):
        super( _AlignmentEnumeration, self ).__init__( enumList = 'COMMUNIST CONSERVATIVE CRIMINAL FANATIC GOVERNMENT LIBERAL PEACEFUL STRAIGHT VIOLENT WEIRD' )

        # Initialize the opposites table if it is not already initialized.
        if len(_AlignmentEnumeration.__opposites) == 0:
            _AlignmentEnumeration.__opposites.insert( self.COMMUNIST,    self.GOVERNMENT   )
            _AlignmentEnumeration.__opposites.insert( self.CONSERVATIVE, self.LIBERAL      )
            _AlignmentEnumeration.__opposites.insert( self.CRIMINAL,     None              )
            _AlignmentEnumeration.__opposites.insert( self.FANATIC,      self.FANATIC      )
            _AlignmentEnumeration.__opposites.insert( self.GOVERNMENT,   self.COMMUNIST    )
            _AlignmentEnumeration.__opposites.insert( self.LIBERAL,      self.CONSERVATIVE )
            _AlignmentEnumeration.__opposites.insert( self.PEACEFUL,     self.VIOLENT      )
            _AlignmentEnumeration.__opposites.insert( self.STRAIGHT,     self.WEIRD        )
            _AlignmentEnumeration.__opposites.insert( self.VIOLENT,      self.PEACEFUL     )
            _AlignmentEnumeration.__opposites.insert( self.WEIRD,        self.STRAIGHT     )

    def isOpposite( self, a, b ):
        # Convert the input parameters to ints.
        if type(a) == types.StringType:
            a = self.nameToValue[ a ]
        elif type(a) == EnumItem:
            a = a.value

        if type(b) == types.StringType:
            b = self.nameToValue[ b ]
        elif type(b) == EnumItem:
            b = b.value

        return self.__opposites[a] == b

    def compare( self, listA, listB ):
        # Convert the input parameters to a list of ints.
        if type(listA) == types.IntType:
            listA = [listA]
        elif type(listA) == types.StringType:
            listA = listA.split()
        elif type(listA) == EnumItem:
            listA = [listA.value]

        if type(listB) == types.IntType:
            listB = [listB]
        elif type(listB) == types.StringType:
            listB = listB.split()
        elif type(listB) == EnumItem:
            listB = [listB.value]

        n = 0
        for a in listA:
            for b in listB:
                if self.isOpposite( a, b ):
                    n -= 1
                elif a == b:
                    n += 1

        return n

Alignment = _AlignmentEnumeration()

class _DirectionEnumeration(Enumeration):
    """ Implements a direction enumeration for NORTH, EAST, SOUTH, and WEST. """

    def __init__( self ):
        # Note, the order of these directions is critical.
        # NORTH must be 0, EAST must be 1, SOUTH must be 2, and WEST must be 3.
        # If not, the conversions from direction to degrees will be broken.
        # Also, rotate() and calculateDegrees() will be broken.
        super( _DirectionEnumeration, self ).__init__( enumList = 'NORTH EAST SOUTH WEST', firstValue = 0 )

    def toDegrees( self, direction, reverse = False ):
        # Convert the input parameter to an int.
        if type(direction) == types.StringType:
            direction = self.valueToName( direction )
        elif type(direction) == EnumItem:
            direction = direction.value

        degrees = direction * 90
        if reverse:
            degrees -= 360

        return degrees

    def rotate( self, direction, degrees ):
        # Convert the input direction to an int.
        if type(direction) == types.StringType:
            direction = self.valueToName( direction )
        elif type(direction) == EnumItem:
            direction = direction.value

        # Verify the input degrees.
        degrees = self.normalize( degrees )
        if not degrees % 90 == 0:
            raise Exception( 'Attempting to rotate by an invalid degree, ' + str(degrees) + '.  Must be 0, 90, 180, 270, -90, -180, or -270.' )

        direction += (degrees / 90)
        direction %= len(self)
        return direction

    def calculateDegrees( self, directionA, directionB ):
        #print ( self.toDegrees( directionB ) - 180 )
        #print self.normalize( self.toDegrees( directionB ) - 180 )
        #print self.toDegrees( directionA )
        #print self.normalize( self.toDegrees( directionA ) )
        #print self.normalize( self.normalize( self.toDegrees( directionA ) ) - self.normalize( self.toDegrees( directionB ) - 180 ) )
        return self.normalize( self.toDegrees( directionA ) - self.toDegrees( directionB ) - 180 )

    @staticmethod
    def normalize( degrees ):
        if degrees < 0:
            degrees += 360

        degrees %= 360

        return degrees

Direction = _DirectionEnumeration()

class Layout(object):
    INPUT_E = '*'
    INPUT_W = '*'
    INPUT_N = '*'
    INPUT_S = '*'

    OUTPUT_E = '-'
    OUTPUT_W = '-'
    OUTPUT_N = '|'
    OUTPUT_S = '|'

    SPACER = ' '

    __toPoints = \
        {
            Direction.NORTH : (  0, -1 ),
            Direction.EAST  : (  1,  0 ),
            Direction.SOUTH : (  0,  1 ),
            Direction.WEST  : ( -1,  0 ),
        }

    __fromPoints = invertDict( __toPoints )

    @staticmethod
    def toPoint( direction ):
        # Convert the input parameter to an int.
        if type(direction) == types.StringType:
            direction = direction.nameToValue( direction )

        return Layout.__toPoints[direction]

    @staticmethod
    def fromPoint( point ):
        return Layout.__fromPoints[point]

    @staticmethod
    def fromPoints( pointA, pointB ):
        point = ( pointB[0] - pointA[0], pointB[1] - pointA[1] )
        return Layout.__fromPoints[point]

    def __init__( self, card = None, center = (0, 0), rect = (0, 0, 0, 0) ):
        super( Layout, self ).__init__()
        self.cards = {}
        self.center = center
        self.resetRect( rect )

        if card:
            self.render( card, center )

    def resetRect( self, rect ):
        self.minX = rect[0]
        self.minY = rect[1]
        self.maxX = rect[2]
        self.maxY = rect[3]

    def updateRect( self, point ):
        if self.minX > point[0]:
            self.minX = point[0]

        if self.minY > point[1]:
            self.minY = point[1]

        if self.maxX < point[0]:
            self.maxX = point[0]

        if self.maxY < point[1]:
            self.maxY = point[1]

    def render( self, card, point = (0,0), rect = (0, 0, 0, 0) ):
        self.cards.clear()
        self.resetRect( rect )
        self.render_r( card, point )

    def render_r( self, card, point ):
        if self.cards.has_key(point):
            raise IllException( 'Cannot attach card, ' + str(card.name) + ', at point, ' + str(point) + ', because card, ' + str(self.cards[point].name) + ', already exists there.' )

        self.cards[point] = card

        for (childDirection, child) in card.children.iteritems():
            if child:
                deltaPoint = self.toPoint( childDirection )
                childPoint = ( point[0] + deltaPoint[0], point[1] + deltaPoint[1] )
                #print 'childPoint:', childPoint, 'deltaPoint:', deltaPoint
                self.render_r( child, childPoint )

        # Update the range after the children have been moved.
        # This will minimize the number of changes to the range.
        self.updateRect( point )

    def __str__( self ):
        s = MutableString()

        s += 'center: '
        s += '('
        s += str(self.center[0])
        s += ', '
        s += str(self.center[1])
        s += ')'
        s += ', '
        s += 'rect: '
        s += '('
        s += str(self.minX)
        s += ', '
        s += str(self.minY)
        s += ')'
        s += ' - '
        s += '('
        s += str(self.maxX)
        s += ', '
        s += str(self.maxY)
        s += ')'
        s += '\n'

        i = 0
        cardList = []

        for y in range(self.minY, self.maxY + 1):
            for x in range(self.minX, self.maxX + 1):
                if self.cards.has_key( (x,y) ):
                    s += self.strCardTop( self.cards[(x,y)] )
                else:
                    s += self.SPACER + self.SPACER + self.SPACER
            s += '\n'

            for x in range(self.minX, self.maxX + 1):
                if self.cards.has_key( (x,y) ):
                    s += self.strCardMiddle( self.cards[(x,y)], str(i) )

                    cardList.append( self.cards[(x,y)] )
                    i += 1
                else:
                    s += self.SPACER + self.SPACER + self.SPACER
            s += '\n'

            for x in range(self.minX, self.maxX + 1):
                if self.cards.has_key( (x,y) ):
                    s += self.strCardBottom( self.cards[(x,y)] )
                else:
                    s += self.SPACER + self.SPACER + self.SPACER
            s += '\n'


        s += '\n'
        for i in range(0, len(cardList)):
            s += str(i) + ': ' + str(cardList[i]) + '\n'

        return str(s)

    def strCardTop( self, card ):
        s = MutableString()

        s += self.SPACER

        if card.children.has_key(Direction.NORTH):
            s += self.OUTPUT_N
        elif card.input == Direction.NORTH:
            s += self.INPUT_N
        else:
            s += self.SPACER

        s += self.SPACER

        return str(s)

    def strCardMiddle( self, card, abbreviation = None ):
        s = MutableString()

        if card.children.has_key(Direction.WEST):
            s += self.OUTPUT_W
        elif card.input == Direction.WEST:
            s += self.INPUT_W
        else:
            s += self.SPACER

        if abbreviation:
            s += str(abbreviation)
        else:
            s += str(card.name)

        if card.children.has_key(Direction.EAST):
            s += self.OUTPUT_E
        elif card.input == Direction.EAST:
            s += self.INPUT_E
        else:
            s += self.SPACER

        return str(s)

    def strCardBottom( self, card ):
        s = MutableString()

        s += self.SPACER

        if card.children.has_key(Direction.SOUTH):
            s += self.OUTPUT_S
        elif card.input == Direction.SOUTH:
            s += self.INPUT_S
        else:
            s += self.SPACER

        s += self.SPACER

        return str(s)

class Group(object):
    Location = Enumeration( 'DEAD_PILE DRAW_PILE ILLUMINATI_PILE CONTROLLED UNCONTROLLED' )

    def __init__( self, name, power, transferablePower, income, resistance = 0, input = None, childrenSpec = None, alignments = (), maxAttacks = 1 ):
        super( Group, self ).__init__()
        self.name              = name
        self.power             = power
        self.transferablePower = transferablePower
        self.income            = income
        self.treasury          = 0
        self.modifiers         = []
        self.actions           = []

        # Non-Illuminati cards only.
        self.resistance        = resistance
        self.input             = input
        self.alignments        = alignments

        self.group                 = None
        self.player                = None
        self.parent                = None
        self.children              = {}

        self.maxAttacks            = maxAttacks
        self.numAttacksUsed        = 0
        self.transferablePowerUsed = False

        if childrenSpec:
            # Group card has only some outputs.
            outputs = childrenSpec
        else:
            # Illuminati card has all outputs.
            outputs = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]

        for direction in outputs:
            self.children[direction] = None

    @staticmethod
    def moveCard( parent, child, direction ):
        oldDirection = parent.findChildDirection( child )

        # Detach the child from the old location.
        Group.detach( child )

        try:
            # Attach the child to the new location.
            Group.attach( parent, child, direction )
            # Map to a view to ensure that no cards overlap.
            Layout( parent )
        except IllException, e:
            # The attach or map to a view failed.

            # Dettach from the new location (in case this succeeded).
            Group.detach( child )
            # Reattach it to the old location.
            Group.attach( parent, child, oldDirection )
            # Re-raise the exception.
            raise

    @staticmethod
    def attach( parent, child, direction ):
        parent.attachChild( child, direction )
        child.attachParent( parent )

        child.rotate( Direction.calculateDegrees( direction, child.input ) )

    @staticmethod
    def detach( child ):
        if child.parent:
            child.parent.detachChild( child )
            child.detachParent()

    def isIlluminati( self ):
        return self.input == None

    def attachChild( self, child, direction ):
        if not self.children.has_key(direction):
            raise IllException( 'Unable to attach child, ' + str(child.name) + ', to card, ' + str(self.name) + ', at direction, ' + str(direction) + ' because there is no output.' )

        if self.children[direction]:
            raise IllException( 'Unable to attach child, ' + str(child.name) + ', to card, ' + str(self.name) + ', at direction, ' + str(direction) + ' because the output is filled.' )

        self.children[direction] = child

    def attachParent( self, parent ):
        self.parent = parent
        self.group = parent.group
        self.player = parent.player

    def findChildDirection( self, child ):
        for (direction, card) in self.children.iteritems():
            if card and child == card:
                return direction

        raise IllException( 'The card, ' + str(child.name) + ', is not a child of parent, ' + str(self.name) + '.' )

    def detachChild( self, child ):
        direction = self.findChildDirection( child )
        if direction != None:
            self.children[ direction ] = None

    def detachParent( self ):
        self.parent = None
        self.group = None
        self.player = None

    def collectIncome( self ):
        TransferMegabucksFromBank( destination = self.player.illuminati, megabucks = self.income, allOrNothing = False )

    def getDistanceFromIlluminati( self ):
        distance = 0
        current = self.parent
        while current:
            if current.isIlluminati():
                return distance
            else:
                distance += 1
                current = current.parent

    def getValue( self ):
        value = self.power + self.transferablePower + self.resistance + self.income
        value += ( len(self.actions) * 2 )
        return value

    def hasOutput( self, direction ):
        return len(self.children) > 0

    def hasOutputAt( self, direction ):
        return self.children.has_key( direction )

    def hasEmptyOutput( self ):
        for child in self.children.itervalues():
            if not child:
                return True

        return False

    def hasEmptyOutputAt( self, direction ):
        return self.children.has_key( direction ) and self.children[direction] == None

    def reset( self ):
        self.numAttacksUsed = 0
        self.transferablePowerUsed = False

    def transferPower( self ):
        if not self.transferablePowerUsed:
            self.transferablePowerUsed = True
            return self.transferablePower
        else:
            return 0

    def cancelTransferPower( self ):
        self.transferablePowerUsed = False

    def startAttack( self ):
        if self.numAttacksUsed >= self.maxAttacks:
            raise IllException( 'Group, ' + str(self.name) + ', cannot attack again this turn.' )

        self.numAttacksUsed += 1

    def cancelAttack( self ):
        if self.numAttacksUsed < 1:
            raise IllException( 'Group, ' + str(self.name) + ', failed to cancel the attack.' )

        self.numAttacksUsed -= 1

    def rotate( self, degrees ):
        """Rotate the card and all child-cards by degrees."""

        self.input = Direction.rotate( self.input, degrees )

        newChildren = {}
        for (childDirection, child) in self.children.iteritems():
            # Rotate the output.
            newChildren[ Direction.rotate( childDirection, degrees ) ] = child

            # If there is a child, then rotate it too.
            if child:
                child.rotate( degrees )

        # Save the new outputs.
        self.children = newChildren

    def getActions( self, player ):
        if self.player and self.player == player:
            for special in self.actions:
                yield (special.action.name, special.action.__call__)

    def __iter__( self ):
        for action in self.actions:
            yield action

    def __eq__( self, other ):
        return self.name == other.name

    def __str__( self ):
        s = MutableString()

        s += str(self.name)
        s += ': '

        s += 'p:('
        s += str(self.power)
        s += '/'
        s += str(self.transferablePower)
        s += ') '

        s += 'r:'
        s += str(self.resistance)
        s += ' '

        s += 'i:('
        s += str(self.income)
        s += ' '
        s += str(self.treasury)
        s += ')'

        for (name, value) in Direction:
            if value == self.input:
                s += ' '
                s += str(name[0])
                s += '['
                if self.parent:
                    s += str(self.parent.name)
                s += ']'
            elif self.children.has_key(value):
                s += ' '
                s += str(name[0])
                s += '('
                if self.children[value]:
                    s += str(self.children[value].name)
                s += ')'
        s += ', '

        s += ' '.join( [ str(alignment) for alignment in self.alignments ] )
        s += ' '

        s += 'group: '
        if self.group:
            s += str(self.group)
        s += ', '

        if self.player:
            s += 'player: '
            s += str(self.player.name)
            s += ', '

        if self.transferablePowerUsed:
            s += 'transferablePowerUsed: '
            s += str(self.transferablePowerUsed)
            s += ', '

        s += 'attacksUsed: '
        s += str(self.numAttacksUsed)
        s += ' of '
        s += str(self.maxAttacks)

        if len(self.actions):
            s += '\nSpecials:\n  '
            s += '\n  '.join( [ str(action.action.description) for action in self.actions ] )

        if len(self.modifiers):
            s += '\nModifiers:\n  '
            s += '\n  '.join( [ str(modifier.description) for modifier in self.modifiers ] )

        return str(s)

class Pile(object):
    def __init__( self, group, cards ):
        super( Pile, self ).__init__()
        self.cards = cards

        for card in self.cards:
            card.group = group

        shuffle( self.cards )

    def drawCard( self, group, player ):
        card = self.cards.pop()
        ##print 'Drawing ' + str(card.name) + '.'

        if type(card) == Group:
            card.group = group
            card.player = player
        elif type(card) == Special:
            card.group = None
            card.player = player
            player.specials.append(card)

        return card

    def drawCards( self, group, player = None, count = 1 ):
        if len(self.cards) < count:
            count = len(self.cards)

        cards = []
        for i in range(count):
            cards.append( self.drawCard( group, player ) )

        return cards

    def __len__( self ):
        return len(self.cards)

    @nestedproperty
    def len():
        doc = 'Get the number of cards in the pile.'
        def fget( self ):
            return len(self.cards)
        return property( fget, None, None, doc )

    def __iter__( self ):
        for card in self.cards.itervalues():
            yield card

    def __str__( self ):
        return '\n'.join( [ str(card) for card in self.cards ] )

class Deck(object):
    def __init__( self ):
        super( Deck, self ).__init__()
        self.cards = {}

    def __len__( self ):
        return len(self.cards)

    def __iter__( self ):
        for card in self.cards.itervalues():
            yield card

    def __getitem__( self, key ):
        return self.cards[key]

    def __setitem__( self, key, value ):
        self.cards[key] = value

    def __str__( self ):
        cards = sortDict( self.cards )
        return '\n'.join( [ str(card) for card in cards ] )
deck = Deck()

class BasicGoal(object):
    __numGroupsNeeded = \
    {
        2 : 13,
        3 : 13,
        4 : 12,
        5 : 10,
        6 : 9,
        7 : 8,
        8 : 8,
    }

    def isComplete( self, game, player ):
        # Add up the number of groups this player controls.
        numGroups = reduce( add, [ 1 for card in deck if card.player == self ], 0 )

        return numGroups >= self.__numGroupsNeeded[len(game.players)]

    def __str__( self ):
        return 'Player must control ' + str(self.__numGroupsNeeded) + ' groups.'

class Modifier(object):
    def __init__( self, modifier = 0, attackTypes = None, attackers = None, attackersAlignments = None, defenders = None, defendersAlignments = None ):
        super( Modifier, self ).__init__()
        """ A value of 'None' for attackTypes, attackers, defenders, or defendersAlignments means 'any'. """
        self.modifier = modifier
        self.attackTypes = attackTypes
        self.attackers = attackers
        self.attackersAlignments = attackersAlignments
        self.defenders = defenders
        self.defendersAlignments = defendersAlignments

    @nestedproperty
    def description():
        doc = ''
        def fget( self ):
            s = MutableString()

            if self.modifier > 0:
                s += '+'
            s += self.modifier

            s += ' '
            s += 'on'
            s += ' '

            s += 'any attempt to'
            s += ' '

            attackTypeNames = self.attackTypes
            if not attackTypeNames:
                attackTypeNames = ( Attack.Type.CONTROL, Attack.Type.NEUTRALIZE, Attack.Type.DESTROY )
            attackTypeNames = [ str(attackType).lower() for attackType in attackTypeNames ]

            s += seqToString( attackTypeNames, 'or' )
            s += ' '

            if self.defenders:
                s += seqToString( [ str(card.name) for card in self.defenders ], 'or' )
            elif self.defendersAlignments:
                s += 'any'
                s += ' '
                s += seqToString( [Alignment[alignment] for alignment in self.defendersAlignments], 'or' )
                s += ' '
                s += 'group'
            else:
                s += 'any'
                s += ' '
                s += 'group'

            s += '.'

            return str(s)
        return property( fget, None, None, doc )

    def isEnabled( self, attack ):
        if not attack:
            return False

        if self.attackTypes and attack.attackType not in self.attackTypes:
            return False

        if self.attackers and attack.attacker not in self.attackers:
            return False

        if self.defenders and attack.defender not in self.defenders:
            return False

        return True

    def calculate( self, attack ):
        if not self.isEnabled( attack ):
            return 0
        else:
            return self.modifier

    def __str__( self ):
        return str(self.description)

    def __repr__( self ):
        s = MutableString()

        s += 'modifier: '
        s += str(self.modifier)
        s += ', '

        if self.attackTypes:
            s += 'attackTypes: '
            s += ', '.join( [ str(attackType) for attackType in self.attackTypes ] )
            s += ' '

        if self.attackers:
            s += 'attackers: '
            s += ', '.join( [ str(attacker.name) for attacker in self.attackers ] )
            s += ', '

        if self.attackersAlignments:
            s += 'attackersAlignments: '
            s += ', '.join( [ str(attackersAlignment) for attackersAlignment in self.attackersAlignments ] )
            s += ', '

        if self.defenders:
            s += 'defenders: '
            s += ', '.join( [ str(defender.name) for defender in self.defenders ] )
            s += ', '

        if self.defendersAlignments:
            s += 'defendersAlignments: '
            s += ', '.join( [ str(defendersAlignment) for defendersAlignment in self.defendersAlignments ] )

        return str(s)

class FiniteBank(object):
    def __init__( self, treasury ):
        super( FiniteBank, self ).__init__()
        self.__treasury = treasury

    @nestedproperty
    def treasury():
        doc = 'Get the treasury for this bank.'
        def fget( self ):
            return self.__treasury
        def fset( self, value ):
            if value < 0:
                raise IllException( 'Cannot set the bank to a negative value.' )
            self.__treasury = value
        return property( fget, fset, None, doc )

    def __str__( self ):
        return 'treasury: ' + str(self.treasury)

class InfiniteBank(object):
    def __init__( self, treasury = 1000000 ):
        super( InfiniteBank, self ).__init__()
        self.__treasury = treasury

    @nestedproperty
    def treasury():
        doc = 'Get the treasury for this bank.'
        def fget( self ):
            return self.__treasury
        def fset( self, value ):
            pass
        return property( fget, fset, None, doc )

    def __str__( self ):
        return 'treasury: ' + str(self.__treasury)

"""
This function transfers megabucks from one object to another.  The objects can
be of any type as long as they have a self.treasury.  This includes Groups,
Players, and Banks.

The destination is optional.  If it is not specified, the megabucks are taken
from the source and removed.

The option, allOrNothing, specifies if the transfer should fail if the source
does not have enough megabucks.
"""
def TransferMegabucks( source, destination, megabucks, allOrNothing = True ):
    if not megabucks:
        return 0

    if not source:
        raise IllException( 'TransferMegabucks requires a source.' )

    if megabucks > source.treasury:
        if allOrNothing:
            raise IllException( 'TransferMegabucks cannot transfer ' + str(megabucks) + ' megabucks.' )
        else:
            # If the card does not have enough megabucks, then transfer as much as possible.
            megabucks = source.treasury

    source.treasury -= megabucks

    # If a destination was specified, add the megabucks.
    if destination:
        destination.treasury += megabucks

    return megabucks

#bank = FiniteBank( 1000 )
bank = InfiniteBank()
TransferMegabucksToBank = curry( TransferMegabucks, destination = bank )
TransferMegabucksFromBank = curry( TransferMegabucks, source = bank )

class Attack(object):
    Type = Enumeration( 'CONTROL NEUTRALIZE DESTROY' )
    STATE = Enumeration( 'idle started committed complete' )

    def __init__( self, listener = None ):
        super( Attack, self ).__init__()
        self.listener = listener
        self.attackType = None
        self.priviledged = False
        self.attacker = None
        self.defender = None
        self.megabucksFromAttacker = 0
        self.megabucksFromDefender = 0
        self.megabucksFromDefendersIlluminati = 0
        self.megabucksToAssist = {}
        self.megabucksToInterfere = {}
        self.aides = []
        self.modifiers = []
        self.die1 = 0
        self.die2 = 0
        self.success = None

        self.state = self.STATE.idle

    def identifyState( self, event ):
        return self.state

    @Delegator.eventHandler
    def start( self, attackType, attacker, defender ): pass
    @Delegator.eventHandler
    def cancel( self ): pass
    @Delegator.eventHandler
    def aid( self, card ): pass
    @Delegator.eventHandler
    def assist( self, card, megabucks ): pass
    @Delegator.eventHandler
    def interfere( self, card, megabucks ): pass
    @Delegator.eventHandler
    def roll( self ): pass

    def idleState_startEvent( self, attackType, attacker, defender ):
        attacker.startAttack()

        # For attacks to control, verify that the attacker can attach the new group.
        if attackType is Attack.Type.CONTROL:
            if not attacker.hasEmptyOutput():
                raise IllException( 'Attacker does not have an empty output.' )

            if defender.group != Group.Location.CONTROLLED and defender.group != Group.Location.UNCONTROLLED:
                raise IllException( 'Attack to neutralize must target a controlled or uncontrolled group.  Group, ' + str(defender.name) + ', is in group, ' + str(defender.group) + '.' )

        # For attacks to neutralize, verify that the defender is controlled.
        if attackType is Attack.Type.NEUTRALIZE:
            if defender.group != Group.Location.CONTROLLED:
                raise IllException( 'Attack to neutralize must target a controlled group.  Group, ' + str(defender.name) + ', is in group, ' + str(defender.group) + '.' )

        self.attackType = attackType
        self.attacker = attacker
        self.defender = defender

        self.state = self.STATE.started

    def startedState_cancelEvent( self ):
        if self.isCommitted():
            raise IllException( 'Cannot cancel the attack since it is committed.' )

        self.attacker.cancelAttack()

        for card in self.aides:
            card.cancelTransferPower()
        self.aides = []

        if self.listener:
            self.listener.attackCancelled()

    def startedState_aidEvent( self, card ):
        return self.committedState_aidEvent( card )

    def committedState_aidEvent( self, card ):
        if self.isCommitted():
            raise IllException( 'Cannot transfer power since the attack is committed.' )

        if card.transferablePowerUsed:
            raise IllException( 'The card, ' + str(card.name) + ', has already used its transferable power this turn.' )

        card.transferPower()
        self.aides.append( card )

    def startedState_assistEvent( self, card, megabucks ):
        return self.committedState_assistEvent( card, megabucks )

    def committedState_assistEvent( self, card, megabucks ):
        if card != self.attacker:
            if not card.isIlluminati():
                raise IllException( 'Only the attacker or illuminatis may assist with attacks.' )

        TransferMegabucksToBank( source = card, megabucks = megabucks )
        if card.player == self.attacker.player:
            self.megabucksFromAttacker += megabucks
        else:
            self.megabucksToAssist[card] = megabucks

        self.state = self.STATE.committed

    def startedState_interfereEvent( self, card, megabucks ):
        return self.committedState_interfereEvent( card, megabucks )

    def committedState_interfereEvent( self, card, megabucks ):
        if self.attackType == Attack.Type.CONTROL:
            if ( card != self.defender ) and ( not card.isIlluminati() or card.player != self.defender.player ):
                raise IllException( "Only the defender or the defender's illuminatis may assist with attacks to neutralize or destroy." )
        else:
            if ( card != self.defender ) and ( not card.isIlluminati() ):
                raise IllException( "Only the defender or illuminatis may assist with attacks to control." )

        TransferMegabucksToBank( source = card, megabucks = megabucks )
        if card.player == self.defender.player:
            if card.isIlluminati():
                self.megabucksFromDefendersIlluminati += megabucks
            else:
                self.megabucksFromDefender += megabucks
        else:
            self.megabucksToInterfere[card] = megabucks

        self.state = self.STATE.committed

    def startedState_rollEvent( self ):
        return self.committedState_rollEvent()

    def committedState_rollEvent( self ):
        self.die1 = randint( 1, 6 )
        self.die2 = randint( 1, 6 )
        roll = self.die1 + self.die2

        # 11 or 12 is an automatic failure.
        if roll > 10:
            self.success = False
        else:
            self.success = (roll <= self.targetRoll)
            if self.success:
                if self.attackType is Attack.Type.NEUTRALIZE:
                    defender.group = Group.Location.UNCONTROLLED
                elif self.attackType is Attack.Type.DESTROY:
                    defender.group = Group.Location.DEAD_PILE

        ##print 'Roll: ' + str(self.die1) + '+' + str(self.die2) + ' (' + str(self.success) + ').'

        self.state = self.STATE.complete

        if self.listener:
            if self.success:
                self.listener.attackSuccess()
            else:
                self.listener.attackFailed()

        return self.success

    @nestedproperty
    def totalMegabucksToAssist():
        doc = 'Get the total megabucks to assist this attack.'
        def fget( self ):
            return reduce( add, [ megabucks for megabucks in self.megabucksToAssist.itervalues() ], 0 )
        return property( fget, None, None, doc )

    @nestedproperty
    def totalMegabucksToInterfere():
        doc = 'Get the total megabucks to interfere with this attack.'
        def fget( self ):
            return reduce( add, [ megabucks for megabucks in self.megabucksToInterfere.itervalues() ], 0 )
        return property( fget, None, None, doc )

    def isCommitted( self ):
        return self.megabucksFromAttacker or self.megabucksFromDefender or self.megabucksFromDefendersIlluminati or len(self.megabucksToAssist) or len(self.megabucksToInterfere)

    @nestedproperty
    def targetRoll():
        doc = 'Get the target roll.'
        def fget( self ):
            if not self.attacker or not self.defender:
                return -1

            # Calculate the basic target roll.
            if self.attackType == Attack.Type.CONTROL or self.attackType == Attack.Type.NEUTRALIZE:
                __targetRoll = self.attacker.power - self.defender.resistance
            elif self.attackType == Attack.Type.DESTROY:
                __targetRoll = self.attacker.power - self.defender.power

            # Apply neutralize bonus.
            if self.attackType == Attack.Type.NEUTRALIZE:
                __targetRoll += 6

            # Compare the alignments.
            compare = Alignment.compare( self.attacker.alignments, self.defender.alignments )
            if self.attackType == Attack.Type.CONTROL or self.attackType == Attack.Type.NEUTRALIZE:
                __targetRoll += 4 * compare
            elif self.attackType == Attack.Type.DESTROY:
                __targetRoll -= 4 * compare

            # Measure the distance of defender from defenders's illuminati.
            distance = self.defender.getDistanceFromIlluminati()
            if distance == 0:
                __targetRoll -= 10
            elif distance == 1:
                __targetRoll -= 5
            elif distance == 2:
                __targetRoll -= 2

            # Adjust by megabucks spent.
            __targetRoll += self.megabucksFromAttacker
            __targetRoll -= ( 2 * self.megabucksFromDefender )
            __targetRoll -= self.megabucksFromDefendersIlluminati
            __targetRoll += self.totalMegabucksToAssist
            __targetRoll -= self.totalMegabucksToInterfere

            # Add transferable power from aides.
            for card in self.aides:
                __targetRoll += card.transferablePower

            # Adjust for modifiers.
            for modifier in self.attacker.modifiers:
                __targetRoll += modifier.calculate( self )

            for modifier in self.modifiers:
                __targetRoll += modifier.calculate( self )

            return __targetRoll

        return property( fget, None, None, doc )

    def getActions( self, player ):
        if player == self.attacker.player:
            # Current player
            actionNames = ( 'start', 'cancel', 'aid', 'assist', 'interfere', 'roll' )
        else:
            # Other players
            actionNames = ( 'assist', 'interfere' )

        for actionName in actionNames:
            handler = Delegator.getHandler( self, actionName )
            if handler:
                yield (actionName, handler)

    def __iter__( self ):
        pass

    def __str__( self ):
        s = MutableString()

        s += 'state: '
        s += self.state
        s += ', '

        if self.attacker:
            s += str(self.attacker.name)

        s += ' attacks to '
        s += str(self.attackType)
        s += ' '

        if self.defender:
            s += str(self.defender.name)
        s += ', '

        if self.priviledged:
            s += 'priviledged'
            s += ', '

        if self.isCommitted():
            s += 'committed: '
            s += str(self.isCommitted())
            s += ', '


        s += 'target roll: '
        s += str(self.targetRoll)
        s += ', '

        if self.die1 and self.die2:
            s += 'roll: '
            s += str(self.die1)
            s += '+'
            s += str(self.die1)
            s += '='
            s += str(self.die1 + self.die2)
            s += ' '
            if self.success:
                s += '[success]'
            else:
                s += '[failure]'
        s += '\n'

        if self.megabucksFromAttacker:
            s += '  Attacker: '
            s += str(self.megabucksFromAttacker)
            s += ' mb\n'

        if self.megabucksFromAttacker:
            s += '  Defender: '
            s += str(self.megabucksFromDefender)
            s += ' mb\n'

        if self.megabucksFromDefendersIlluminati:
            s += '  Defender illuminati: '
            s += str(self.megabucksFromDefendersIlluminati)
            s += ' mb\n'

        if self.totalMegabucksToAssist:
            s += '  Assist: '
            s += str(self.totalMegabucksToAssist)
            s += ' mb\n'

        if self.totalMegabucksToInterfere:
            s += '  Interfere: '
            s += str(self.totalMegabucksToInterfere)
            s += ' mb\n'
        s += '\n'

        if len(self.aides):
            s += 'Aides:\n  '
            s += '\n  '.join( [ str(aid.name) + ' +' + str(aid.transferablePower) for aid in self.aides ] )
            s += '\n'

        if len(self.attacker.modifiers) or len(self.modifiers):
            s += '\nModifiers:\n  '
            s += '\n  '.join( [ str(modifier.description) for modifier in self.attacker.modifiers ] )
            s += '\n  '.join( [ str(modifier.description) for modifier in self.modifiers ] )

        return str(s)

    def __repr__( self ):
        s = MutableString()

        s += 'state: '
        s += str(self.state)
        s += ', '

        s += 'attackType: '
        s += str(self.attackType)
        s += ', '

        s += 'priviledged: '
        s += str(self.priviledged)
        s += ', '

        s += 'attacker: '
        if self.attacker:
            s += str(self.attacker.name)
        s += ', '

        s += 'defender: '
        if self.defender:
            s += str(self.defender.name)
        s += ', '

        s += 'megabucksFromAttacker: '
        s += str(self.megabucksFromAttacker)
        s += ', '

        s += 'megabucksFromDefender: '
        s += str(self.megabucksFromDefender)
        s += ', '

        s += 'megabucksFromDefendersIlluminati: '
        s += str(self.megabucksFromDefendersIlluminati)
        s += ', '

        s += 'megabucksToAssist: '
        s += str(self.megabucksToAssist)
        s += ', '

        s += 'megabucksToInterfere: '
        s += str(self.megabucksToInterfere)
        s += ', '

        s += 'totalMegabucksToAssist: '
        s += str(self.totalMegabucksToAssist)
        s += ', '

        s += 'totalMegabucksToInterfere: '
        s += str(self.totalMegabucksToInterfere)
        s += ', '

        s += 'aides: '
        s += ', '.join( [ str(aid.name) for aid in self.aides ] )
        s += ', '

        s += 'modifiers: '
        s += ', '.join( [ str(modifier.name) for modifier in self.modifiers ] )
        s += ', '

        s += 'isCommitted: '
        s += str(self.isCommitted())
        s += ', '

        s += 'targetRoll: '
        s += str(self.targetRoll)
        s += ', '

        s += 'roll: '
        s += str(self.die1)
        s += '+'
        s += str(self.die1)
        s += '='
        s += str(self.die1 + self.die2)
        s += ', '
        s += 'success: '
        s += str(self.success)

        return str(s)

class Player(object):
    def __init__( self, name, illuminati, numDraws = 1, maxActions = 2, maxMegabucksTransfers = 2 ):
        super( Player, self ).__init__()
        self.name = name
        self.group = Layout()

        self.illuminati = illuminati
        self.illuminati.group = Group.Location.CONTROLLED
        self.illuminati.player = self

        self.numDraws = numDraws
        self.maxActions = maxActions
        self.maxMegabucksTransfers = maxMegabucksTransfers
        self.goals = []
        self.specials = []

        #FIXME:DEBUG
        self.illuminati.actions.append( Special( CollectTax(5) ) )
        self.specials.append( Special( PriviledgeAttack() ) )
        self.specials.append( Special( InterfereAttack() ) )

    @nestedproperty
    def power():
        doc = 'Get the total power for this player.'
        def fget( self ):
            return reduce( add, [ card.power for card in deck if card.player == self ], 0 )
        return property( fget, None, None, doc )

    @nestedproperty
    def transferablePower():
        doc = 'Get the total transferable power for this player.'
        def fget( self ):
            return reduce( add, [ card.transferablePower for card in deck if card.player == self ], 0 )
        return property( fget, None, None, doc )

    @nestedproperty
    def income():
        doc = 'Get the total income for this player.'
        def fget( self ):
            return reduce( add, [ card.income for card in deck if card.player == self ], 0 )
        return property( fget, None, None, doc )

    @nestedproperty
    def treasury():
        doc = 'Get the total treasury for this player.'
        def fget( self ):
            return reduce( add, [ card.treasury for card in deck if card.player == self ], 0 )
        def fset( self, value ):
            if value < 0:
                raise IllException( 'Cannot set a player\'s treasury to a negative value.' )

            # Get the player's cards.
            cards = [ card for card in deck if card.player == self ]

            megabucksToSpend = self.treasury - value
            while megabucksToSpend > 0:
                # Take the subset of cards that have a non-empty treasury.
                cards = [ card for card in cards if card.treasury ]
                # Sort by most megabucks.
                cards.sort(lambda a, b: b.treasury - a.treasury )
                if len(cards) == 0:
                    raise IllException( 'Ran out of cards with a treasury while attempting to spend megabucks.' )

                # Spend a megabuck from each card with a treasury.
                for card in cards:
                    if megabucksToSpend == 0:
                        break
                    TransferMegabucksToBank( source = card, megabucks = 1 )
                    megabucksToSpend -= 1

        return property( fget, fset, None, doc )

    def startTurn( self, pile ):
        pile.drawCards( group = Group.Location.UNCONTROLLED, player = None, count = self.numDraws )
        [ card.collectIncome() for card in deck if card.player == self ]

    def endTurn( self ):
        [ card.reset() for card in deck if card.player == self ]

        for special in self.specials:
            special.reset()

    def isComplete( self, game ):
        for goal in self.goals:
            if goal.isComplete( game, self ):
                return True

        return False

    def getActions( self, game ):
        for special in self.specials:
            if special.isEnabled( game ):
                yield (special.action.name, special.__call__)

    def __iter__( self ):
        for special in self.specials.itervalues():
            yield special

    def __str__( self ):
        s = MutableString()

        s += str(self.name)
        s += ': '

        s += 'power: '
        s += str(self.power)
        s += ', '
        s += 'transferablePower: '
        s += str(self.transferablePower)
        s += ', '
        s += 'income: '
        s += str(self.income)
        s += ', '
        s += 'treasury: '
        s += str(self.treasury)
        s += ', '

        s += 'numDraws: '
        s += str(self.numDraws)
        s += ', '
        s += 'maxActions: '
        s += str(self.maxActions)
        s += ', '
        s += 'maxMegabucksTransfers: '
        s += str(self.maxMegabucksTransfers)
        s += '\n'

        #s += '  '
        #s += '\n  '.join( [ str(card) for card in deck if card.player == self ] )

        self.group.render( self.illuminati )
        s += str(self.group)

        return str(s)

class Turn(object):
    STATE = Enumeration( 'idle attacking placing complete' )

    def __init__( self, listener, game, player ):
        super( Turn, self ).__init__()
        self.log = logging.getLogger( self.__class__.__name__ )

        self.listener = listener
        #self.game = game
        self.player = player

        # State
        self.state = self.STATE.idle
        self.numActions = 0
        self.numMegabucksTransfers = 0
        self.attack = None

        self.player.startTurn( game.drawPile )

    def identifyState( self, event ):
        #print self.state
        return self.state

    # Event methods.
    @Delegator.eventHandler
    def startAttack( self, attackType, attacker, defender ): pass
    @Delegator.eventHandler
    def attackSuccess( self ): pass
    @Delegator.eventHandler
    def attackFailed( self ): pass
    @Delegator.eventHandler
    def attackCancelled( self ): pass
    @Delegator.eventHandler
    def placeGroup( self, direction, megabucks ): pass
    @Delegator.eventHandler
    def moveGroup( self, source, destination, direction ): pass
    @Delegator.eventHandler
    def transferMegabucks( self, source, destination, megabucks = 0 ): pass
    @Delegator.eventHandler
    def end( self ): pass

    def idleState_startAttackEvent( self, attackType, attacker, defender ):
        if self.numActions >= self.player.maxActions:
            return

        self.numActions += 1
        self.attack = Attack( self )
        self.attack.start( attackType, attacker, defender )
        self.state = self.STATE.attacking

    def idleState_moveGroupEvent( self, source, destination, direction ):
        if self.numActions >= self.player.maxActions:
            return

        if source == destination:
            return

        if source.player != self.player:
            raise IllException( 'The card, ' + str(source.name) + ' is not owned by the current player and cannot be moved.' )

        if destination.player != self.player:
            raise IllException( 'The card, ' + str(destination.name) + ' is not owned by the current player and cannot be moved.' )

        self.numActions += 1
        Group.moveCard( destination, source, direction )

    def idleState_transferMegabucksEvent( self, source, destination, megabucks ):
        if self.numMegabucksTransfers >= self.player.maxMegabucksTransfers:
            return

        if source == destination:
            return

        if source.player != self.player:
            raise IllException( 'The card, ' + str(source.name) + ' is not owned by the current player and cannot be used in a transfer.' )

        if destination.player != self.player:
            raise IllException( 'The card, ' + str(destination.name) + ' is not owned by the current player and cannot be used in a transfer.' )

        self.numMegabucksTransfers += 1
        TransferMegabucks( source, destination, megabucks )

    def idleState_endEvent( self ):
        if self.numActions == 0 and self.numMegabucksTransfers == 0:
            TransferMegabucksFromBank( destination = self.player.illuminati, megabucks = 5, allOrNothing = False )

        self.player.endTurn()

        self.state = self.STATE.complete

        if self.listener:
            self.listener.turnEnded()

    def attackingState_attackSuccessEvent( self ):
        self.state = self.STATE.placing

    def attackingState_attackFailureEvent( self ):
        self.attack = None
        self.state = self.STATE.idle

    def attackingState_attackCancelledEvent( self ):
        self.attack = None
        self.numActions -= 1
        self.state = self.STATE.idle

    def placingState_placeGroupEvent( self, direction, megabucks = 0 ):
        if megabucks:
            TransferMegabucks( self.attack.attacker, self.attack.defender, megabucks )
        Group.attach( self.attack.attacker, self.attack.defender, direction )

        self.attack = None
        self.state = self.STATE.idle

    def getActions( self, player ):
        if player == self.player:
            # Current player
            actionNames = ( 'startAttack', 'placeGroup', 'moveGroup', 'transferMegabucks', 'end' )
        else:
            # Other players
            actionNames = ()

        for actionName in actionNames:
            handler = Delegator.getHandler( self, actionName )
            if handler:
                yield (actionName, handler)

        if self.attack:
            for action in self.attack.getActions( player ):
                yield action

    def __iter__( self ):
        pass

    def __str__( self ):
        s = MutableString()

        s += 'state: '
        s += str(self.state)
        s += ', '

        s += 'player: '
        s += str(self.player.name)
        s += ': '

        s += 'numActions: '
        s += str(self.numActions)
        s += ', '

        s += 'numMegabucksTransfers: '
        s += str(self.numMegabucksTransfers)
        s += ', '

        s += 'attack: '
        s += str(self.attack)

        return str(s)

class Game(object):
    STATE = Enumeration( 'initial setup active complete' )

    def __init__( self, name, description = '' ):
        super( Game, self ).__init__()

        self.name = name
        self.description = description
        self.drawPile = None
        self.specialsPile = None
        self.players = []

        # State
        self.state = self.STATE.initial
        self.nextPlayerIndex = 0
        self.turn = None
        self.winner = None

    def currentPlayer( self ):
        if not self.turn:
            return None

        return self.turn.player

    def startTurn( self ):
        # Create a new turn.
        self.turn = Turn( self, self, self.players[self.nextPlayerIndex] )

        # Increment the index.
        self.nextPlayerIndex = ( self.nextPlayerIndex + 1 ) % len(self.players)

    def identifyState( self, event ):
        #print self.state
        return self.state

    @Delegator.eventHandler
    def setup( self, playerNames ): pass
    @Delegator.eventHandler
    def start( self ): pass
    @Delegator.eventHandler
    def turnEnded( self ): pass

    def initialState_setupEvent( self, playerNames ):
        illuminatis = [ card for card in deck if card.isIlluminati() ]
        shuffle( illuminatis )

        basicGoal = BasicGoal()

        for playerName in playerNames:
            # Create the player.
            player = Player( playerName, illuminatis.pop() )
            player.goals.append( basicGoal )

            self.players.append( player )

        self.state = self.STATE.setup

    def setupState_startEvent( self ):
        shuffle( self.players )

        # Create the draw pile and draw the first cards to the uncontrolled pile.
        self.drawPile = Pile( Group.Location.DRAW_PILE, [ card for card in deck if not card.isIlluminati() ] )
        self.drawPile.drawCards( group = Group.Location.UNCONTROLLED, player = None, count = 4 )

        # Create the specials pile.
        self.specialsPile = Pile( Group.Location.DRAW_PILE, Assets.specials )

        self.startTurn()

        self.state = self.STATE.active

    def activeState_turnEndedEvent( self ):
        # Check if there is a winner.
        for player in self.players:
            if player.isComplete( self ):
                self.winner = player
                return False

        self.startTurn()

        return True

    def getActions( self, player ):
        actionNames = ( 'setup', 'start' )
        for actionName in actionNames:
            handler = Delegator.getHandler( self, actionName )
            if handler:
                yield (actionName, handler)

        if self.turn:
            for action in self.turn.getActions( player ):
                yield action

        for card in deck:
            for action in card.getActions( player ):
                yield action

        if player:
            for action in player.getActions( self ):
                yield action

    def __iter__( self ):
        pass

    def __str__( self ):
        s = MutableString()

        s += 'state: '
        s += str(self.state)
        s += ', '

        s += 'name: '
        s += str(self.name)
        s += ', '

        s += 'description: '
        s += str(self.description)
        s += ': '

        s += 'drawPile: '
        if self.drawPile:
            s += str(len(self.drawPile))

        return str(s)

class Special(object):
    def __init__( self, action ):
        super( Special, self ).__init__()
        self.action = action
        self.group = None
        self.player = None
        self.used = False

    def isEnabled( self, game ):
        return not self.used and self.action.isEnabled( game )

    def reset( self ):
        self.used = False

    def __call__( self, game ):
        self.used = True
        return self.action( game )

    def __str__( self ):
        s = MutableString()

        s += 'name: '
        s += str(self.action.name)
        s += ', '

        s += 'description: '
        s += str(self.action.description)

        return str(s)

class CollectTax(object):
    def __init__( self, megabucks ):
        super( CollectTax, self ).__init__()
        self.name = 'Collect Tax'
        self.description = 'Collect %d MB from each player.' % megabucks
        self.megabucks = megabucks

    def isEnabled( self, game ):
        return game.turn and game.turn.state != Turn.STATE.complete

    def __call__( self, game ):
        player = game.turn.player
        for opponent in game.players:
            if player != opponent:
                TransferMegabucks( opponent, player.illuminati, self.megabucks, allOrNothing = False )

class PriviledgeAttack(object):
    def __init__( self ):
        super( PriviledgeAttack, self ).__init__()
        self.name = 'Priviledge'
        self.description = 'Make the current attack priviledged.'

    def isEnabled( self, game ):
        return game.turn.attack and game.turn.attack.priviledged == False

    def __call__( self, game ):
        game.turn.attack.priviledged = True

class InterfereAttack(object):
    def __init__( self ):
        super( InterfereAttack, self ).__init__()
        self.name = 'Interfere'
        self.description = 'Make the current attack NOT priviledged.'

    def isEnabled( self, game ):
        return game.turn.attack and game.turn.attack.priviledged == True

    def __call__( self, game ):
        game.turn.attack.priviledged = False

class Assets(object):
    modifiers = []
    specials = []

    @staticmethod
    def Spec( **kwargs ):
        return kwargs

    @staticmethod
    def load():
        Assets.loadDeck( StandardDeck + ExpansionDeck )
        Assets.loadSpecials( Specials )
        Assets.loadModifiers( StandardModifiers )

    @staticmethod
    def loadDeck( cardSpecs ):
        deck.cards.clear()
        for card in cardSpecs:
            deck[deepcopy(card.name)] = deepcopy(card)
        return deck

    @staticmethod
    def loadSpecials( specialSpecs ):
        for special in specialSpecs:
            Assets.specials.append( deepcopy(special) )
        return Assets.specials

    @staticmethod
    def loadModifiers( modifierSpecs ):
        for modifierSpec in modifierSpecs:
            modifier = Assets.loadModifier( **modifierSpec )
            Assets.modifiers.append( deepcopy(modifier) )
        return Assets.modifiers

    @staticmethod
    def loadModifier( card, modifier = 0, attackTypes = None, attackers = None, attackersAlignments = None, defenders = None, defendersAlignments = None ):
        # Map the card names to card objects.
        _card = deck[card]

        _attackers = None
        if attackers:
            _attackers = []
            for attacker in attackers:
                _attackers.append( deck[attacker] )

        _defenders = None
        if defenders:
            _defenders = []
            for defender in defenders:
                _defenders.append( deck[defender] )

        # Create the new modifier and attach it to the card.
        modifier = Modifier( modifier, attackTypes, _attackers, attackersAlignments, _defenders, defendersAlignments )
        _card.modifiers.append( modifier )

        # Return the new modifier.
        return modifier

StandardDeck = \
[
    # Illuminiati
    Group( 'The Bavarian Illuminati', 10, 10, 9 ),
    Group( 'The Bermuda Triangle', 8, 8, 9 ),
    Group( 'The Discordian Society', 8, 8, 8 ),
    Group( 'The Gnomes of Zurich', 7, 7, 12 ),
    Group( 'The Network', 7, 7, 9 ),
    Group( 'The Servants of Cthulhu', 9, 9, 7 ),
    Group( 'The Society of Assassins', 8, 8, 8 ),
    Group( 'The UFOs', 6, 6, 8 ),

    # Groups
    Group( 'American Autoduel Association', 1, 0, 5, 1, Direction.WEST, (Direction.EAST,), (Alignment.VIOLENT, Alignment.WEIRD,) ),
    Group( 'Anti-Nuclear Activists', 2, 0, 5, 1, Direction.WEST, (Direction.WEST,), (Alignment.LIBERAL,) ),
    Group( 'Anti-Nuclear Activists', 2, 5, 0, 1, Direction.WEST, (), (Alignment.LIBERAL,) ),
    Group( 'Antiwar Activists', 0, 0, 3, 1 , Direction.WEST, (), (Alignment.LIBERAL, Alignment.PEACEFUL,) ),
    Group( 'Big Media', 4, 3, 6, 3 , Direction.EAST, (Direction.SOUTH, Direction.WEST,), (Alignment.LIBERAL, Alignment.STRAIGHT,) ),
    Group( 'C.I.A.', 6, 4, 5, 0 , Direction.EAST, (Direction.SOUTH, Direction.WEST,), (Alignment.GOVERNMENT, Alignment.VIOLENT,) ),
    Group( 'California', 5, 0, 4, 5 , Direction.WEST, (Direction.NORTH, Direction.SOUTH,), (Alignment.GOVERNMENT, Alignment.LIBERAL, Alignment.WEIRD,) ),
    Group( 'CFL-AIO', 6, 0, 5, 3 , Direction.EAST, (Direction.NORTH, Direction.SOUTH, Direction.WEST,), (Alignment.LIBERAL,) ),
    Group( 'Chinese Campaign Donors', 3, 0, 2, 3 , Direction.EAST, (Direction.SOUTH,), (Alignment.COMMUNIST,) ),
    Group( 'Clone Arrangers', 6, 2, 6, 1, Direction.WEST, (Direction.SOUTH, Direction.EAST,), (Alignment.VIOLENT, Alignment.COMMUNIST, Alignment.CRIMINAL,) ),
    Group( 'Convenience Stores', 1, 0, 4, 3 , Direction.WEST, (Direction.SOUTH,), (Alignment.STRAIGHT,) ),
    Group( 'Cycle Gangs', 0, 0, 4, 0 , Direction.WEST, (), (Alignment.VIOLENT,Alignment.WEIRD,) ),
    Group( 'Democrats', 5, 0, 4, 3 , Direction.EAST, (Direction.SOUTH, Direction.WEST,), (Alignment.LIBERAL,) ),
    Group( 'Empty Vee', 3, 0, 3, 4 , Direction.EAST, (Direction.SOUTH, Direction.WEST,) ),
    Group( 'Evil Geniuses For a Better Tomorrow', 0, 2, 6, 3, Direction.EAST, (Direction.WEST,), (Alignment.VIOLENT, Alignment.WEIRD,) ),
    Group( 'F.B.I.', 4, 2, 6, 0, Direction.EAST, (Direction.NORTH, Direction.SOUTH,), (Alignment.GOVERNMENT, Alignment.STRAIGHT,) ),
    Group( 'Federal Reserve', 5, 3, 7, 6 , Direction.WEST, (Direction.NORTH, Direction.EAST,), (Alignment.GOVERNMENT,) ),
    Group( 'Feminists', 2, 0, 2, 1, Direction.WEST, (Direction.SOUTH,), (Alignment.LIBERAL,) ),
    Group( 'Gun Lobby', 1, 0, 3, 1 , Direction.EAST, (), (Alignment.CONSERVATIVE, Alignment.VIOLENT,) ),
    Group( 'Gun Lobby', 1, 0, 3, 1, Direction.EAST, (Direction.WEST, Direction.SOUTH,), (Alignment.CONSERVATIVE, Alignment.VIOLENT,) ),
    Group( 'Hackers', 1, 1, 4, 2, Direction.EAST, (Direction.WEST,), (Alignment.WEIRD, Alignment.FANATIC,) ),
    Group( 'Health Food Stores', 1, 0, 3, 2, Direction.WEST, (Direction.WEST,), (Alignment.LIBERAL,) ),
    Group( 'Hollywood', 2, 0, 0, 5 , Direction.WEST, (Direction.SOUTH, Direction.EAST,), (Alignment.LIBERAL,) ),
    Group( 'I.R.S.', 5, 3, 5, 0 , Direction.EAST, (Direction.SOUTH,), (Alignment.CRIMINAL, Alignment.GOVERNMENT,) ),
    Group( 'Intellectuals', 0, 0, 3, 1 , Direction.WEST, (), (Alignment.FANATIC, Alignment.WEIRD,) ),
    Group( 'International Cocaine Smugglers', 3, 0, 5, 5, Direction.WEST, (Direction.EAST,), (Alignment.CRIMINAL,) ),
    Group( 'International Communist Conspiracy', 7, 0, 8, 6, Direction.EAST, (Direction.SOUTH, Direction.WEST,), (Alignment.COMMUNIST,) ),
    Group( 'Junk Mail', 1, 0, 3, 2, Direction.EAST, (Direction.WEST,), (Alignment.CRIMINAL,) ),
    Group( 'KGB', 2, 2, 6, 0, Direction.EAST, (Direction.WEST,), (Alignment.COMMUNIST, Alignment.VIOLENT,) ),
    Group( 'L-4 Society', 1, 0, 2, 0, Direction.EAST, (Direction.WEST,), (Alignment.WEIRD,) ),
    Group( 'Libertarians', 1, 0, 4, 1, Direction.WEST, (Direction.NORTH,), (Alignment.FANATIC,) ),
    Group( 'Madison Avenue', 3, 3, 3, 2, Direction.EAST, (Direction.WEST, Direction.SOUTH,), (Alignment.LIBERAL,) ),
    Group( 'Militia', 2, 0, 4, 2, Direction.EAST, (Direction.WEST,), (Alignment.VIOLENT, Alignment.CONSERVATIVE,) ),
    Group( 'Moral Minority', 2, 0, 1, 2 , Direction.EAST, (Direction.SOUTH,), (Alignment.CONSERVATIVE,Alignment.STRAIGHT,Alignment.FANATIC,) ),
    Group( 'Multinational Oil Companies', 6, 0, 4, 8, Direction.WEST, (Direction.NORTH, Direction.SOUTH, Direction.EAST,), () ),
    Group( 'Nuclear Power Companies', 4, 0, 4, 3, Direction.EAST, (Direction.WEST,), (Alignment.CONSERVATIVE,) ),
    Group( 'Orbital Mind Control Lasers', 4, 2, 5, 0 , Direction.WEST, (Direction.NORTH, Direction.EAST,), (Alignment.COMMUNIST,) ),
    Group( 'Pentagon', 6, 0, 6, 2 , Direction.EAST, (Direction.NORTH, Direction.SOUTH, Direction.WEST,), (Alignment.GOVERNMENT, Alignment.STRAIGHT, Alignment.VIOLENT,) ),
    Group( 'Phone Phreaks', 0, 1, 1, 1, Direction.WEST, (Direction.WEST,), (Alignment.CRIMINAL, Alignment.LIBERAL,) ),
    Group( 'Post Office', 4, 3, 3, -1, Direction.EAST, (Direction.SOUTH,), (Alignment.GOVERNMENT,) ),
    Group( 'Punk Rockers', 0, 0, 4, 1, Direction.WEST, (), (Alignment.WEIRD,) ),
    Group( 'Recyclers', 2, 0, 2, 3 , Direction.EAST, (Direction.WEST,), (Alignment.LIBERAL,) ),
    Group( 'Republicans', 4, 0, 4, 4, Direction.EAST, (Direction.WEST,), (Alignment.CONSERVATIVE,) ),
    Group( 'Robot Sea Monsters', 0, 0, 2, 6, Direction.EAST, (Direction.NORTH,), (Alignment.COMMUNIST, Alignment.VIOLENT) ),
    Group( 'S.M.O.F.', 1, 0, 1, 0, Direction.EAST, (), (Alignment.WEIRD,) ),
    Group( 'S.M.O.F.', 1, 0, 1, 0, Direction.EAST, (Direction.SOUTH,), (Alignment.WEIRD,) ),
    Group( 'Science Fiction Fans', 0, 0, 5, 1, Direction.WEST, (), (Alignment.WEIRD,) ),
    Group( 'Science Fiction Fans', 0, 0, 5, 1, Direction.WEST, (Direction.WEST,), (Alignment.WEIRD,) ),
    Group( 'Semiconscious Liberation Army', 0, 0, 8, 0, Direction.WEST, (Direction.WEST,), (Alignment.CRIMINAL, Alignment.VIOLENT, Alignment.LIBERAL, Alignment.WEIRD, Alignment.COMMUNIST,) ),
    Group( 'South American Nazis', 4, 0, 6, 2 , Direction.EAST, (Direction.NORTH, Direction.SOUTH,), (Alignment.CONSERVATIVE, Alignment.VIOLENT,) ),
    Group( 'Spammers', 0, 0, 3, 3, Direction.WEST, (Direction.WEST,), (Alignment.CRIMINAL,) ),
    Group( 'Survivalists', 0, 0, 6, 2 , Direction.EAST, (), (Alignment.CONSERVATIVE, Alignment.FANATIC, Alignment.VIOLENT,) ),
    Group( 'Survivalists', 0, 0, 6, 2, Direction.EAST, (Direction.WEST,), (Alignment.CONSERVATIVE, Alignment.VIOLENT, Alignment.FANATIC,) ),
    Group( 'Tabloids', 2, 0, 3, 3 , Direction.EAST, (), (Alignment.WEIRD,) ),
    Group( 'Tabloids', 2, 0, 3, 3, Direction.EAST, (Direction.WEST,), (Alignment.WEIRD,) ),
    Group( 'Texas', 6, 0, 0, 4 , Direction.WEST, (Direction.NORTH, Direction.EAST,), (Alignment.CONSERVATIVE, Alignment.GOVERNMENT, Alignment.VIOLENT,) ),
    Group( 'The Mafia', 7, 0, 7, 6 , Direction.EAST, (Direction.SOUTH,Direction.WEST), (Alignment.CRIMINAL, Alignment.VIOLENT,) ),
    Group( 'The Mafia', 7, 0, 7, 6, Direction.EAST, (Direction.WEST, Direction.SOUTH,), (Alignment.CRIMINAL, Alignment.VIOLENT,) ),
    Group( 'The Men in Black', 0, 2, 6, 1 , Direction.WEST, (), (Alignment.CRIMINAL, Alignment.WEIRD,) ),
    Group( 'The Phone Company', 5, 2, 6, 3, Direction.WEST, (Direction.EAST, Direction.SOUTH,), (Alignment.LIBERAL,) ),
    Group( 'Tobacco & Liqour Companies', 4, 0, 3, 3 , Direction.EAST, (Direction.WEST,), (Alignment.STRAIGHT,) ),
    Group( 'Trekkies', 0, 0, 4, 3 , Direction.EAST, (), (Alignment.WEIRD, Alignment.FANATIC,) ),
    Group( 'Triliberal Commission', 5, 0, 6, 3, Direction.EAST, (Direction.NORTH, Direction.SOUTH,), (Alignment.LIBERAL, Alignment.STRAIGHT,) ),
    Group( 'TV Preachers', 3, 0, 6, 4 , Direction.EAST, (Direction.SOUTH,Direction.WEST,), (Alignment.STRAIGHT,Alignment.FANATIC,) ),
    Group( 'TV Preachers', 3, 0, 6, 4, Direction.EAST, (Direction.WEST, Direction.SOUTH,), (Alignment.STRAIGHT, Alignment.FANATIC,) ),
    Group( 'Video Games', 2, 0, 3, 7 , Direction.EAST, (), () ),
    Group( 'Video Games', 2, 0, 3, 7, Direction.EAST, (Direction.SOUTH,), (Alignment.LIBERAL,) ),
]
ExpansionDeck = \
[
    # Illuminati
    Group( 'Church of the SubGenius', 6, 6, 9 ),
    Group( 'Shangri-La', 7, 7, 8 ),

    # Groups
]

Specials = \
[
    Special( CollectTax( 5 ) ),
    Special( PriviledgeAttack() ),
    Special( InterfereAttack() ),
]

StandardModifiers = \
[
    # Attack modifiers.
    Assets.Spec( card = 'Anti-Nuclear Activists', modifier = +2, attackTypes = (Attack.Type.DESTROY,), defenders = ('Nuclear Power Companies',) ),
    Assets.Spec( card = 'Cycle Gangs', modifier = +2, attackTypes = (Attack.Type.DESTROY,) ),
    Assets.Spec( card = 'Science Fiction Fans', modifier = +2, attackTypes = (Attack.Type.CONTROL,), defendersAlignments = (Alignment.WEIRD,) ),
    Assets.Spec( card = 'Clone Arrangers', modifier = +3, attackTypes = (Attack.Type.DESTROY,) ),
    Assets.Spec( card = 'Evil Geniuses For a Better Tomorrow', modifier = +4, defenders = ('Orbital Mind Control Lasers',) ),
    Assets.Spec( card = 'Feminists', modifier = +3, attackTypes = (Attack.Type.CONTROL,), defendersAlignments = (Alignment.LIBERAL,) ),
    Assets.Spec( card = 'Hackers', modifier = +3, attackTypes = (Attack.Type.NEUTRALIZE,) ),
    Assets.Spec( card = 'Health Food Stores', modifier = +2, attackTypes = (Attack.Type.CONTROL,), defenders = ('Anti-Nuclear Activists',) ),
    Assets.Spec( card = 'International Cocaine Smugglers', modifier = +4, attackTypes = (Attack.Type.CONTROL,), defenders = ('Punk Rockers','Cycle Gangs','Hollywood',) ),
    Assets.Spec( card = 'International Communist Conspiracy', modifier = +3, attackTypes = (Attack.Type.CONTROL,), defendersAlignments = (Alignment.COMMUNIST,) ),
    Assets.Spec( card = 'Junk Mail', modifier = +4, attackTypes = (Attack.Type.CONTROL,), defenders = ('Post Office',) ),
    Assets.Spec( card = 'KGB', modifier = +2, attackTypes = (Attack.Type.DESTROY,) ),
    Assets.Spec( card = 'Madison Avenue', modifier = +5, attackTypes = (Attack.Type.CONTROL,), defenders = ('Big Media','Empty Vee',) ),
    Assets.Spec( card = 'Militia', modifier = +6, attackTypes = (Attack.Type.DESTROY,), defendersAlignments = (Alignment.COMMUNIST,) ),
    Assets.Spec( card = 'Phone Phreaks', modifier = +3, defenders = ('The Phone Company',) ),
    Assets.Spec( card = 'Semiconscious Liberation Army', modifier = +1, attackTypes = (Attack.Type.DESTROY,) ),

    # Illuminati
    Assets.Spec( card = 'The Discordian Society', modifier = -100, defendersAlignments = (Alignment.GOVERNMENT,Alignment.STRAIGHT,) ),
    Assets.Spec( card = 'The Discordian Society', modifier = +4, attackTypes = (Attack.Type.CONTROL,), defendersAlignments = (Alignment.WEIRD,) ),
    Assets.Spec( card = 'The Servants of Cthulhu', modifier = +2, attackTypes = (Attack.Type.DESTROY,) ),
    Assets.Spec( card = 'The Society of Assassins', modifier = +4, attackTypes = (Attack.Type.NEUTRALIZE,) ),

    # When this card is attacking only.
    Assets.Spec( card = 'L-4 Society', modifier = +4, attackers = ('L-4 Society',), defenders = ('Orbital Mind Control Lasers',) ),
    Assets.Spec( card = 'S.M.O.F.', modifier = +2, attackTypes = (Attack.Type.CONTROL,), attackers = ('S.M.O.F.',), defenders = ('Trekkies',) ),
    Assets.Spec( card = 'S.M.O.F.', modifier = +5, attackTypes = (Attack.Type.CONTROL,), attackers = ('S.M.O.F.',), defenders = ('Science Fiction Fans',) ),
    Assets.Spec( card = 'The Mafia', modifier = +3, attackTypes = (Attack.Type.CONTROL,), attackers = ('The Mafia',), defendersAlignments = (Alignment.CRIMINAL,) ),
    Assets.Spec( card = 'TV Preachers', modifier = +3, attackTypes = (Attack.Type.CONTROL,), attackers = ('TV Preachers',), defenders = ('Moral Minority',) ),

    Assets.Spec( card = 'Tabloids', modifier = +3, attackTypes = (Attack.Type.CONTROL,), attackers = ('Tabloids','Video Games',), defenders = ('Convenience Stores',) ),
    Assets.Spec( card = 'Video Games', modifier = +3, attackTypes = (Attack.Type.CONTROL,), attackers = ('Tabloids','Video Games',), defenders = ('Convenience Stores',) ),

    # Defend modifiers.
    Assets.Spec( card = 'Gun Lobby', modifier = -7, attackersAlignments = (Alignment.LIBERAL, Alignment.COMMUNIST, Alignment.WEIRD,), defenders = ('Gun Lobby',) ),
    Assets.Spec( card = 'Survivalists', modifier = -2, ),
]

