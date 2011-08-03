#!/usr/bin/env python
from illuminati.model import *
import inspect
import iron.delegator
import logging
import random
import sys

class CliGame(object):
    def __init__( self ):
        super( CliGame, self ).__init__()

        random.seed( 0 )

        self.game = Game( 'TestGame', 'The Mice and Beasts Battle' )
        self.game.setup( [ 'Josh', 'Riley', 'Matt', 'Chloe' ] )
        self.game.start()

        while not self.game.winner:
            self.chooseAction( self.getActions() )

        print game.winner.name

    def getActions( self ):
        # Model
        actions = [ action for action in self.game.getActions( self.game.currentPlayer() ) ]

        # UI actions
        actions.append( ('show game', self.printGame) )
        actions.append( ('show draw pile', self.printDrawPile) )
        if self.game.turn:
            actions.append( ('show turn', self.printTurn) )
            actions.append( ('show current player', self.printCurrentPlayer) )
            actions.append( ('show player', self.printPlayer) )
            if self.game.turn.attack:
                actions.append( ('show attack', self.printAttack) )
        actions.append( (self.seed.__name__, self.seed) )
        actions.append( (self.quit.__name__, self.quit) )

        return actions

    def choosePlayer( self ):
        while True:
            i = 0
            for player in self.game.players:
                print str(i) + ': ' + str(player.name)
                i += 1

            try:
                command = int(raw_input( '> ' ))
                playerId = int(command)
                if playerId >= 0 and playerId < i:
                    return self.game.players[playerId]
            except ValueError, e:
                pass
            except SyntaxError, e:
                pass
            print 'Invalid input.  Enter a number between 0 and ' + str(i-1) + '.'

    def chooseCard( self, cards ):
        while True:
            i = 0
            for card in cards:
                print str(i) + ': ' + str(card)
                i += 1

            try:
                command = int(raw_input( '> ' ))
                cardId = int(command)
                if cardId >= 0 and cardId < i:
                    return cards[cardId]
            except ValueError, e:
                pass
            except SyntaxError, e:
                pass
            print 'Invalid input.  Enter a number between 0 and ' + str(i-1) + '.'

    def chooseArgValue( self, argSpec ):
        #print str(argSpec)

        argValue = None

        if argSpec == 'attackType':
            argValue = raw_input( str(argSpec) + '(' + str(Attack.Type) + ')' + '> ' )
            argValue = Attack.Type.fromStr( argValue )
        elif argSpec in [ 'card', 'attacker', 'source', 'destination' ]:
            cards = [ card for card in deck.cards.itervalues() if card.player == self.game.turn.player ]
            argValue = self.chooseCard( cards )
        elif argSpec in [ 'defender' ]:
            cards = [ card for card in deck.cards.itervalues() if card.player != self.game.turn.player and card.group != Group.Location.DRAW_PILE and not card.isIlluminati() ]
            argValue = self.chooseCard( cards )
        elif argSpec == 'direction':
            argValue = raw_input( str(argSpec) + '(' + str(Direction) + ')' + '> ' )
            argValue = Direction.fromStr( argValue )
        elif argSpec == 'megabucks':
            argValue = int(raw_input( str(argSpec) + '> ' ))
        elif argSpec == 'player':
            argValue = self.choosePlayer()
        elif argSpec == 'newSeed':
            argValue = int(raw_input( str(argSpec) + '> ' ))
        elif argSpec == 'game':
            argValue = self.game
        else:
            raise Exception( 'Unexpected arg argSpec, ' + str(argSpec) + '.' )

        #print str(argValue)
        return argValue

    def chooseAction( self, actions ):
        while True:
            i = 0
            for action in actions:
                print str(i) + ': ' + action[0]
                i += 1

            try:
                commandId = int(raw_input( '> ' ))
                command = int(commandId)
                if command >= 0 and command < i:
                    handler = actions[command][1]

                    args = []
                    argSpecs = inspect.getargspec(handler).args
                    #print argSpecs

                    for argSpec in argSpecs[1:]: # Skip 'self'
                        argValue = self.chooseArgValue( argSpec )
                        if argValue:
                            args.append( argValue )

                    #print handler, args
                    return handler( *args )
            except ValueError, e:
                pass
            except SyntaxError, e:
                pass
            print 'Invalid input.  Enter a number between 0 and ' + str(i-1) + '.'

    def printGame( self ):
        print self.game

    def printDrawPile( self ):
        print self.game.drawPile

    def printTurn( self ):
        print self.game.turn

    def printCurrentPlayer( self ):
        print self.game.turn.player

    def printPlayer( self, player ):
        print player

    def printAttack( self ):
        print self.game.turn.attack

    def seed( self, newSeed ):
        random.seed( newSeed )

    def quit( self ):
        raise IllException( 'Quit game' )
        #sys.exit( 0 )

if __name__ == "__main__":
    logging.basicConfig( filename='/tmp/illuminati.log', filemode='w', level=logging.DEBUG, format='%(asctime)s.%(msecs)d %(levelname)s %(threadName)s(%(thread)d) %(name)s %(module)s.%(funcName)s#%(lineno)d %(message)s', datefmt='%d.%m.%Y %H:%M:%S' )
    try:
        Assets.load()
        CliGame()
    except IllException, e:
        print e

