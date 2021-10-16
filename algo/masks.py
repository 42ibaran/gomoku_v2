from enum import Enum

Patterns = Enum(
    'Patterns',
    """
    AX_DEVELOPING_TO_2
    AX_DEVELOPING_TO_3
    AX_DEVELOPING_TO_4
    UNBLOCKABLE_4
    FIVE_IN_A_ROW
    """
)

PatternsValue = {
    Patterns.AX_DEVELOPING_TO_2 : 1,
    Patterns.AX_DEVELOPING_TO_3 : 10,
    Patterns.AX_DEVELOPING_TO_4 : 100,
    Patterns.UNBLOCKABLE_4      : 1000,
    Patterns.FIVE_IN_A_ROW      : 10000,
}

MASKS = {
    6: {
        Patterns.UNBLOCKABLE_4: [
            0x1e  # .XXXX.
        ],
    },
    5: {
        Patterns.FIVE_IN_A_ROW: [
            0x1f  # XXXXX
        ],
        Patterns.AX_DEVELOPING_TO_4: [
            0x1e, # XXXX.
            0xf,  # .XXXX
        ],
        Patterns.AX_DEVELOPING_TO_3: [
            0x1c, # XXX..
            0xe,  # .XXX.
            0x7,  # ..XXX
            0x1a, # XX.X.
            0xd,  # .XX.X
            0x16, # X.XX.
            0xb,  # .X.XX
            0x19, # XX..X
            0x15, # X.X.X
            0x13, # X..XX
        ],
        Patterns.AX_DEVELOPING_TO_2: [
            0x18, # XX...
            0xc,  # .XX..
            0x6,  # ..XX.
            0x3,  # ...XX
            0x14, # X.X..
            0xa,  # .X.X.
            0x5,  # ..X.X
            0x12, # X..X.
            0x9,  # .X..X
            0x11, # X...X
        ]
    }
}
