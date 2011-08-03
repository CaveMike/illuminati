#!/usr/bin/env python
from illuminati.model import *
import logging
import unittest

class TestAlignment(unittest.TestCase):
    def verifyOpposite( self, enumeration, a, b, result ):
        #print str(enumeration[a]), str(enumeration[b]), str(result), enumeration.isOpposite( a, b )
        assert( enumeration.isOpposite( a, b ) == result )

    def verifyCompare( self, enumeration, a, b, result ):
        #print enumeration[a], enumeration[b], result, enumeration.compare( a, b )
        assert( enumeration.compare( a, b ) == result )

    def runTest( self ):
        # Verify singles.
        self.verifyOpposite( Alignment, Alignment.COMMUNIST,    Alignment.GOVERNMENT,   True )
        self.verifyOpposite( Alignment, Alignment.CONSERVATIVE, Alignment.LIBERAL,      True )
        self.verifyOpposite( Alignment, Alignment.CRIMINAL,     None,                   True )
        self.verifyOpposite( Alignment, Alignment.FANATIC,      Alignment.FANATIC,      True )
        self.verifyOpposite( Alignment, Alignment.GOVERNMENT,   Alignment.COMMUNIST,    True )
        self.verifyOpposite( Alignment, Alignment.LIBERAL,      Alignment.CONSERVATIVE, True )
        self.verifyOpposite( Alignment, Alignment.PEACEFUL,     Alignment.VIOLENT,      True )
        self.verifyOpposite( Alignment, Alignment.STRAIGHT,     Alignment.WEIRD,        True )
        self.verifyOpposite( Alignment, Alignment.VIOLENT,      Alignment.PEACEFUL,     True )
        self.verifyOpposite( Alignment, Alignment.WEIRD,        Alignment.STRAIGHT,     True )

        self.verifyOpposite( Alignment, Alignment.COMMUNIST,    Alignment.LIBERAL,      False )
        self.verifyOpposite( Alignment, Alignment.CONSERVATIVE, Alignment.FANATIC,      False )
        self.verifyOpposite( Alignment, Alignment.CRIMINAL,     Alignment.FANATIC,      False )
        self.verifyOpposite( Alignment, Alignment.FANATIC,      Alignment.COMMUNIST,    False )
        self.verifyOpposite( Alignment, Alignment.GOVERNMENT,   Alignment.CONSERVATIVE, False )
        self.verifyOpposite( Alignment, Alignment.LIBERAL,      Alignment.VIOLENT,      False )
        self.verifyOpposite( Alignment, Alignment.PEACEFUL,     Alignment.WEIRD,        False )
        self.verifyOpposite( Alignment, Alignment.STRAIGHT,     Alignment.PEACEFUL,     False )
        self.verifyOpposite( Alignment, Alignment.VIOLENT,      Alignment.STRAIGHT,     False )
        self.verifyOpposite( Alignment, Alignment.WEIRD,        Alignment.GOVERNMENT,   False )

        # Compare singles.
        self.verifyCompare( Alignment, Alignment.COMMUNIST,    Alignment.GOVERNMENT,   -1 )
        self.verifyCompare( Alignment, Alignment.CONSERVATIVE, Alignment.LIBERAL,      -1 )
        self.verifyCompare( Alignment, Alignment.FANATIC,      Alignment.FANATIC,      -1 )
        self.verifyCompare( Alignment, Alignment.GOVERNMENT,   Alignment.COMMUNIST,    -1 )
        self.verifyCompare( Alignment, Alignment.LIBERAL,      Alignment.CONSERVATIVE, -1 )
        self.verifyCompare( Alignment, Alignment.PEACEFUL,     Alignment.VIOLENT,      -1 )
        self.verifyCompare( Alignment, Alignment.STRAIGHT,     Alignment.WEIRD,        -1 )
        self.verifyCompare( Alignment, Alignment.VIOLENT,      Alignment.PEACEFUL,     -1 )
        self.verifyCompare( Alignment, Alignment.WEIRD,        Alignment.STRAIGHT,     -1 )

        # Compare Tuple
        self.verifyCompare( Alignment, ( Alignment.VIOLENT, Alignment.CONSERVATIVE ), ( Alignment.LIBERAL, Alignment.PEACEFUL ), -2 )

        # Compare List
        self.verifyCompare( Alignment, [ Alignment.VIOLENT, Alignment.CONSERVATIVE ], [ Alignment.LIBERAL, Alignment.PEACEFUL ], -2 )

        # Compare Mixed
        self.verifyCompare( Alignment, [ Alignment.VIOLENT, Alignment.CONSERVATIVE ], Alignment.LIBERAL, -1 )

class TestDirection(unittest.TestCase):
    def verifyRotate( self, enumeration, direction, degrees, result ):
        #print enumeration[direction], degrees, enumeration[result], enumeration[enumeration.rotate( direction, degrees )]
        assert( enumeration.rotate( direction, degrees ) == result )

    def calculateDegrees( self, enumeration, directionA, directionB, degrees ):
        #print enumeration[directionA], enumeration[directionB], degrees, enumeration.calculateDegrees( directionA, directionB )
        assert enumeration.calculateDegrees( directionA, directionB ) == degrees

    def runTest( self ):
        self.verifyRotate( Direction, Direction.NORTH, 0,    Direction.NORTH )
        self.verifyRotate( Direction, Direction.NORTH, 90,   Direction.EAST  )
        self.verifyRotate( Direction, Direction.NORTH, 180,  Direction.SOUTH )
        self.verifyRotate( Direction, Direction.NORTH, 270,  Direction.WEST  )
        self.verifyRotate( Direction, Direction.NORTH, -90,  Direction.WEST  )
        self.verifyRotate( Direction, Direction.NORTH, -180, Direction.SOUTH )
        self.verifyRotate( Direction, Direction.NORTH, -270, Direction.EAST  )
        self.assertRaises( Exception, Direction.rotate, Direction.NORTH, -91 )

        self.calculateDegrees( Direction, Direction.NORTH, Direction.NORTH, 180 )
        self.calculateDegrees( Direction, Direction.NORTH, Direction.EAST,   90 )
        self.calculateDegrees( Direction, Direction.NORTH, Direction.SOUTH,   0 )
        self.calculateDegrees( Direction, Direction.NORTH, Direction.WEST,  270 )

        self.calculateDegrees( Direction, Direction.EAST,  Direction.NORTH, 270 )
        self.calculateDegrees( Direction, Direction.EAST,  Direction.EAST,  180 )
        self.calculateDegrees( Direction, Direction.EAST,  Direction.SOUTH, 90 )
        self.calculateDegrees( Direction, Direction.EAST,  Direction.WEST,  0 )

        self.calculateDegrees( Direction, Direction.SOUTH, Direction.NORTH, 0 )
        self.calculateDegrees( Direction, Direction.SOUTH, Direction.EAST,  270 )
        self.calculateDegrees( Direction, Direction.SOUTH, Direction.SOUTH, 180 )
        self.calculateDegrees( Direction, Direction.SOUTH, Direction.WEST,  90 )

        self.calculateDegrees( Direction, Direction.WEST,  Direction.NORTH, 90 )
        self.calculateDegrees( Direction, Direction.WEST,  Direction.EAST,  0 )
        self.calculateDegrees( Direction, Direction.WEST,  Direction.SOUTH, 270 )
        self.calculateDegrees( Direction, Direction.WEST,  Direction.WEST,  180 )

class TestLayout(unittest.TestCase):
    def runTest( self ):
        g = Layout()

        cardA = Group( 'A', 0, 0, 0, 0, Direction.NORTH, (Direction.EAST,Direction.SOUTH,Direction.WEST) )
        cardB = Group( 'B', 0, 0, 0, 0, Direction.EAST,  (Direction.NORTH,Direction.SOUTH,Direction.WEST,) )
        cardC = Group( 'C', 0, 0, 0, 0, Direction.SOUTH, (Direction.EAST,Direction.NORTH,Direction.WEST,) )
        cardD = Group( 'D', 0, 0, 0, 0, Direction.WEST,  (Direction.EAST,Direction.SOUTH,Direction.NORTH,) )
        cardE = Group( 'E', 0, 0, 0, 0, Direction.NORTH, (Direction.EAST,Direction.SOUTH,Direction.WEST) )
        cardF = Group( 'F', 0, 0, 0, 0, Direction.EAST,  (Direction.NORTH,Direction.SOUTH,Direction.WEST,) )
        cardG = Group( 'G', 0, 0, 0, 0, Direction.SOUTH, (Direction.EAST,Direction.NORTH,Direction.WEST,) )
        cardH = Group( 'H', 0, 0, 0, 0, Direction.WEST,  (Direction.EAST,Direction.SOUTH,Direction.NORTH,) )
        cardI = Group( 'I', 0, 0, 0 )

        Group.attach( cardI, cardA, Direction.NORTH )
        Group.attach( cardA, cardB, Direction.EAST )
        Group.attach( cardA, cardC, Direction.NORTH )
        Group.attach( cardB, cardD, Direction.EAST )
        g.render( cardI )
        #print 'A NORTH of I:', str(g)

        Group.detach( cardA )
        g.render( cardI )
        #print 'Just I:', str(g)
        Group.attach( cardI, cardA, Direction.SOUTH )
        g.render( cardI )
        #print 'A SOUTH of I:', str(g)

        Group.detach( cardA )
        g.render( cardI )
        #print 'Just I:', str(g)
        Group.attach( cardI, cardA, Direction.EAST )
        g.render( cardI )
        #print 'A EAST of I:', str(g)

        Group.detach( cardA )
        g.render( cardI )
        #print 'Just I:', str(g)
        Group.attach( cardI, cardA, Direction.WEST )
        g.render( cardI )
        #print 'A WEST of I:', str(g)

        Group.detach( cardA )
        g.render( cardI )
        #print 'Just I:', str(g)
        Group.attach( cardI, cardA, Direction.NORTH )
        g.render( cardI )
        #print 'A NORTH of I:', str(g)

        Group.attach( cardI, cardE, Direction.SOUTH )
        Group.attach( cardE, cardF, Direction.EAST )
        Group.attach( cardE, cardG, Direction.SOUTH )
        Group.attach( cardF, cardH, Direction.EAST )
        g.render( cardI )
        #print 'A NORTH of I and E SOUTH of I:', str(g)

        try:
            Group.moveCard( cardI, cardE, Direction.NORTH )
        except IllException, e:
            #print str(e)
            pass
        g.render( cardI )
        #print 'A NORTH of I and E SOUTH of I:', str(g)

        try:
            Group.moveCard( cardI, cardE, Direction.EAST )
        except IllException, e:
            #print str(e)
            pass
        g.render( cardI )
        #print 'A NORTH of I and E SOUTH of I:', str(g)

        assert( Layout.toPoint( Direction.NORTH ) == ( 0, -1) )
        assert( Layout.toPoint( Direction.EAST  ) == ( 1,  0) )
        assert( Layout.toPoint( Direction.SOUTH ) == ( 0,  1) )
        assert( Layout.toPoint( Direction.WEST  ) == (-1,  0) )

        assert( Layout.fromPoint( ( 0, -1) ) == Direction.NORTH )
        assert( Layout.fromPoint( ( 1,  0) ) == Direction.EAST  )
        assert( Layout.fromPoint( ( 0,  1) ) == Direction.SOUTH )
        assert( Layout.fromPoint( (-1,  0) ) == Direction.WEST  )

        assert( Layout.fromPoints( (0, 0), ( 0, -1) ) == Direction.NORTH )
        assert( Layout.fromPoints( (0, 0), ( 1,  0) ) == Direction.EAST  )
        assert( Layout.fromPoints( (0, 0), ( 0,  1) ) == Direction.SOUTH )
        assert( Layout.fromPoints( (0, 0), (-1,  0) ) == Direction.WEST  )
        assert( Layout.fromPoints( (5, 5), ( 4,  5) ) == Direction.WEST  )

class TestGroup(unittest.TestCase):
    def runTest( self ):
        Assets.load()
        #FIXME: IMPLEMENT
        pass

class TestPile(unittest.TestCase):
    def runTest( self ):
        # Test null card list.
        self.assertRaises( TypeError, Pile, None, None )

        # Test empty card list.
        pile = Pile( Group.Location.DRAW_PILE, [] )
        self.assertRaises( IndexError, pile.drawCard, None, None )

class TestDeck(unittest.TestCase):
    def runTest( self ):
        Assets.load()
        #FIXME: IMPLEMENT
        pass

class TestBasicGoal(unittest.TestCase):
    def runTest( self ):
        assert( str(BasicGoal()) )

class TestModifier(unittest.TestCase):
    def runTest( self ):
        seed( 0 )

        attacker = Group( 'Anti-Nuclear Activists', 2, 0, 5, 1, Direction.WEST, (Direction.WEST,), (Alignment.LIBERAL,) )
        #print attacker

        defender = Group( 'Nuclear Power Companies', 4, 0, 4, 3, Direction.EAST, (Direction.WEST,), (Alignment.CONSERVATIVE,) )
        #print defender

        modifier = Modifier( modifier = +2, attackTypes = (Attack.Type.DESTROY,) )
        #print modifier

        attack = Attack()
        attack.start( Attack.Type.DESTROY, attacker, defender )

        assert( modifier.isEnabled( attack ) == True )
        attack.modifiers.append( modifier )

        assert( attack.targetRoll == 4 )

class TestFiniteBank(unittest.TestCase):
    def runTest( self ):
        b = FiniteBank( 10 )
        #print str(b)

        assert( TransferMegabucks( b, None, 0 ) == 0 )
        #print str(b)

        assert( TransferMegabucks( b, None, 4 ) == 4 )
        #print str(b)

        assert( TransferMegabucks( b, None, 4 ) == 4 )
        #print str(b)

        try:
            TransferMegabucks( b, None, 4 )
            self.fail()
        except IllException:
            pass
        #print str(b)

        assert( TransferMegabucks( b, None, 4, allOrNothing = False ) == 2 )
        #print str(b)

class TestInfiniteBank(unittest.TestCase):
    def runTest( self ):
        b = InfiniteBank()
        #print str(b)

        assert( TransferMegabucks( b, None, 0 ) == 0 )
        #print str(b)

        assert( TransferMegabucks( b, None, 4 ) == 4 )
        #print str(b)

        assert( TransferMegabucks( b, None, 4 ) == 4 )
        #print str(b)

        assert( TransferMegabucks( b, None, 4 ) == 4 )
        #print str(b)

        assert( TransferMegabucks( b, None, 4 ) == 4 )
        #print str(b)

        assert( TransferMegabucks( b, None, 4, allOrNothing = False ) == 4 )
        #print str(b)

class TestAttack(unittest.TestCase):
    def runTest( self ):
        seed( 0 )

        attacker = Group( 'Anti-Nuclear Activists', 2, 0, 5, 1, Direction.WEST, (Direction.WEST,), (Alignment.LIBERAL,) )
        #print attacker

        defender = Group( 'Nuclear Power Companies', 4, 0, 4, 3, Direction.EAST, (Direction.WEST,), (Alignment.CONSERVATIVE,) )
        #print defender

        attack = Attack()
        attack.start( Attack.Type.DESTROY, attacker, defender )

        assert( attack.targetRoll == 2 )
        assert( str(attack) )

class TestPlayer(unittest.TestCase):
    def runTest( self ):
        Assets.load()

        illuminati = deck['The UFOs']
        fbi = deck['F.B.I.']
        mafia = deck['The Mafia']
        pentagon = deck['Pentagon']
        post = deck['Post Office']
        rsm = deck['Robot Sea Monsters']
        fed = deck['Federal Reserve']
        cad = deck['Chinese Campaign Donors']
        irs = deck['I.R.S.']

        player = Player( 'The Beast', illuminati, numDraws = 1, maxActions = 2, maxMegabucksTransfers = 2 )

        Group.attach( illuminati, fbi,      Direction.NORTH )
        Group.attach( illuminati, mafia,    Direction.EAST  )
        Group.attach( mafia,      post,     Direction.NORTH )
        Group.attach( mafia,      pentagon, Direction.EAST  )
        Group.attach( pentagon,   rsm,      Direction.EAST  )
        Group.attach( pentagon,   cad,      Direction.NORTH )
        Group.attach( pentagon,   fed,      Direction.SOUTH )
        Group.attach( fed,        irs,      Direction.SOUTH )

        assert( str(player) )

class TestTurn(unittest.TestCase):
    def runTest( self ):
        seed( 0 )

        game = Game( 'test-turn-game', 'test-turn-game-description' )

        MiniDeck = \
        [
            Group( 'The Bavarian Illuminati', 10, 10, 9 ),
            Group( 'The Bermuda Triangle', 8, 8, 9 ),
            Group( 'The Discordian Society', 8, 8, 8 ),
            Group( 'The Gnomes of Zurich', 7, 7, 12 ),

            Group( 'American Autoduel Association', 1, 0, 5, 1, Direction.WEST, (Direction.EAST,), (Alignment.VIOLENT, Alignment.WEIRD,) ),
            Group( 'Anti-Nuclear Activists', 2, 5, 0, 1, Direction.WEST, (), (Alignment.LIBERAL,) ),
            Group( 'Antiwar Activists', 0, 0, 3, 1 , Direction.WEST, (), (Alignment.LIBERAL, Alignment.PEACEFUL,) ),
        ]
        Assets.loadDeck( MiniDeck )

        game.setup( [ 'Josh', 'Riley', 'Matt', 'Chloe' ] )

        game.drawPile = Pile( Group.Location.DRAW_PILE, [ card for card in deck if not card.isIlluminati() ] )
        game.playerIndex = 0

        player = game.players[0]
        #print player
        turn = Turn( listener = None, game = game, player = player )
        turn.end()
        #print turn
        #print player

        player = game.players[1]
        #print player
        turn = Turn( listener = None, game = game, player = player )
        turn.transferMegabucks( player.illuminati, player.illuminati, 5 )
        turn.transferMegabucks( player.illuminati, player.illuminati, 5 )
        turn.transferMegabucks( player.illuminati, player.illuminati, 5 )
        turn.end()
        #print turn
        #print player

        player = game.players[2]
        turn = Turn( listener = None, game = game, player = player )
        turn.startAttack( Attack.Type.CONTROL, deck['The Discordian Society'], deck['Anti-Nuclear Activists'] )
        turn.attackCancelled()
        turn.end()

        assert( str(turn) )

class TestGame(unittest.TestCase):
    def runTest( self ):
        seed( 0 )

        Assets.load()

        game = Game( 'TestGame', 'The Mice and Beasts Battle All' )
        game.setup( [ 'Josh', 'Riley', 'Matt', 'Chloe' ] )
        game.start()

        game.turn.end()

        game.turn.transferMegabucks( game.turn.player.illuminati, game.turn.player.illuminati, 5 )
        game.turn.end()

        deck['Anti-Nuclear Activists'].group = Group.Location.UNCONTROLLED

        game.turn.startAttack( Attack.Type.CONTROL, game.turn.player.illuminati, deck['Anti-Nuclear Activists'] )
        game.turn.attack.aid( game.turn.player.illuminati )
        game.turn.attack.roll()
        game.turn.placeGroup( Direction.NORTH, 1 )
        game.turn.end()

        game.turn.startAttack( Attack.Type.CONTROL, game.turn.player.illuminati, deck['Anti-Nuclear Activists'] )
        game.turn.attack.cancel()
        game.turn.end()

        return

class TestSpecials(unittest.TestCase):
    def runTest( self ):
        s = CollectTax( 5 )
        assert( str(s) )

        s = PriviledgeAttack()
        assert( str(s) )

        s = InterfereAttack()
        assert( str(s) )



if __name__ == "__main__":
    #logging.basicConfig( level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
    logging.basicConfig( filename='/tmp/illuminati.log', filemode='w', level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
    unittest.main()

