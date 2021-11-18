from enum import Enum

Patterns = Enum(
    'Patterns',
    """
    AX_DEVELOPING_TO_2
    BLOCK_AX_DEVELOPING_TO_2
    AX_DEVELOPING_TO_3
    BLOCK_AX_DEVELOPING_TO_3
    AX_DEVELOPING_TO_4
    BLOCK_AX_DEVELOPING_TO_4
    FREE_4
    BLOCK_FREE_4
    FIVE_IN_A_ROW
    BLOCK_FIVE_IN_A_ROW
    CAPTURE
    POTENTIAL_CAPTURE
    """
)

PatternsValue = {
    Patterns.AX_DEVELOPING_TO_2       : 1,
    Patterns.BLOCK_AX_DEVELOPING_TO_2 : 10,
    Patterns.POTENTIAL_CAPTURE        : 100,
    Patterns.AX_DEVELOPING_TO_3       : 1000,
    Patterns.BLOCK_AX_DEVELOPING_TO_3 : 10000,
    Patterns.AX_DEVELOPING_TO_4       : 100000,
    Patterns.BLOCK_AX_DEVELOPING_TO_4 : 1000000,
    Patterns.FREE_4                   : 10000000,
    Patterns.BLOCK_FREE_4             : 100000000,
    Patterns.CAPTURE                  : 1000000000,
    Patterns.FIVE_IN_A_ROW            : 10000000000,
    Patterns.BLOCK_FIVE_IN_A_ROW      : 100000000000,
}

# Patterns.BLOCK_FIVE_IN_A_ROW:[
#     0xa1,   # XOOOO
#     0xd7,   # OXOOO
#     0xe9,   # OOXOO
#     0xef,   # OOOXO
#     0xf1,   # OOOOX
# ],
# Patterns.BLOCK_AX_DEVELOPING_TO_4: [
#     0x9f,   # XOOO.
#     0xd5,   # OXOO.
#     0xe7,   # OOXO.
#     0xed,   # OOOX.
#     0x35,   # .XOOO
#     0x47,   # .OXOO
#     0x4d,   # .OOXO
#     0x4f,   # .OOOX
# ],

MASKS_WHITE = {
    6: {
        Patterns.FREE_4: [
            0x78,   # .XXXX.
        ],
    },
    5: {
        Patterns.FIVE_IN_A_ROW: [
            0x79,   # XXXXX
        ],
        Patterns.AX_DEVELOPING_TO_4: [
            0x28,   # .XXXX
            0x5e,   # X.XXX
            0x70,   # XX.XX
            0x76,   # XXX.X
            0x78,   # XXXX.
        ],
        Patterns.AX_DEVELOPING_TO_3: [
            0x75,   # XXX..
            0x27,   # .XXX.
            0xd,    # ..XXX
            0x6f,   # XX.X.
            0x25,   # .XX.X
            0x5d,   # X.XX.
            0x1f,   # .X.XX
            0x6d,   # XX..X
            0x5b,   # X.X.X
            0x55,   # X..XX
        ],
        Patterns.AX_DEVELOPING_TO_2: [
            0x6c,   # XX...
            0x24,   # .XX..
            0xc,    # ..XX.
            0x4,    # ...XX
            0x5a,   # X.X..
            0x1e,   # .X.X.
            0xa,    # ..X.X
            0x54,   # X..X.
            0x1c,   # .X..X
            0x52,   # X...X
        ]
    },
    4: {
        Patterns.POTENTIAL_CAPTURE: [
            0x19,   # .OOX # .XXO
            0x33    # XOO. # OXX.
        ]
    }
}

MASKS_BLACK = {
    6: {
        Patterns.FREE_4: [
            240
        ]
    },
    5: {
        Patterns.FIVE_IN_A_ROW: [
            242,
        ], 
        Patterns.AX_DEVELOPING_TO_4: [
            80,
            188,
            224,
            236,
            240
        ], 
        Patterns.AX_DEVELOPING_TO_3: [
            234,
            78,
            26,
            222,
            74,
            186,
            62,
            218,
            182,
            170,
        ],    
        Patterns.AX_DEVELOPING_TO_2: [
            216,
            72,
            24,
            8,
            180,
            60,
            20,
            168,
            56,
            164,
        ]
    },
    4: {
        Patterns.POTENTIAL_CAPTURE: [
            0xe,
            0x42,
        ]
    }
}

# BLOCKING_PATTERN_CODE_CONVERTION = {
#     Patterns.AX_DEVELOPING_TO_2 : Patterns.BLOCK_AX_DEVELOPING_TO_2,
#     Patterns.AX_DEVELOPING_TO_3 : Patterns.BLOCK_AX_DEVELOPING_TO_3,
#     Patterns.AX_DEVELOPING_TO_4 : Patterns.BLOCK_AX_DEVELOPING_TO_4,
#     Patterns.FREE_4             : Patterns.BLOCK_FREE_4,
#     Patterns.FIVE_IN_A_ROW      : Patterns.BLOCK_FIVE_IN_A_ROW,
# }