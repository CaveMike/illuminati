#!/usr/bin/env python
from illuminati import *
from sys import stderr
from UserString import MutableString

# A helper tool to input group cards interactively.
# This is not needed to run the game.
def inputGroup():
    try:
        while 1:
            # Get inputs.
            stderr.write( 'name: ' )
            name = raw_input( '' )
            stderr.write( 'power: ' )
            powerString = raw_input( '' )
            powerList = powerString.split( '/' )

            stderr.write( 'resistance: ' )
            resistance = raw_input( '' )

            stderr.write( 'income: ' )
            income = raw_input( '' )

            stderr.write( 'input: ' )
            input = raw_input( '' )

            stderr.write( 'outputs: ' )
            outputs = raw_input( '' )
            outputList = outputs.split( ' ' )

            stderr.write( 'alignments: ' )
            alignments = raw_input( '' )
            alignmentList = alignments.split( ' ' )

            # Validate inputs.
            power = int(powerList[0])
            if len(powerList) > 1:
                tpower = int(powerList[1])
            else:
                tpower = 0

            resistance = int(resistance)
            income = int(income)
            input = Direction.fromName(input)
            outputs = [ 'Direction.' + Direction.fromName( output ) + ',' for output in outputList if Direction.fromName( output ) ]
            alignmentList = [ 'Alignment.' + Alignment.fromName( alignment ) + ','  for alignment in alignmentList if Alignment.fromName( alignment ) ]

            # Output group.
            s = MutableString()

            s += 'Loader.loadCard( deck, Group( '

            s += "'"
            s += name
            s += "'"
            s += ', '

            s += power
            s += ', '

            s += tpower
            s += ', '

            s += resistance
            s += ', '

            s += income
            s += ', '

            s += 'Direction.'
            s += input
            s += ', '

            s += '('
            s += ' '.join( outputs )
            s += ')'
            s += ', '

            s += '('
            s += ' '.join( alignmentList )
            s += ')'

            s += ' )'

            s += ' )'

            print str(s)

    except EOFError:
        pass

if __name__ == "__main__":
    inputGroup()

