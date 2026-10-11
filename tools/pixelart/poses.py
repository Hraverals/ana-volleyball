"""Poses for all 27 player frames, keyed by (state, frame).

How the game plays them (physics.js):
- state 0 (standing/walking): frames 0..4 back and forth
- state 1 (jump): frames 0, 1, 2 repeated (3 and 4 are drawn but unused)
- state 2 (power hit): 0 -> 4 once, then back to jump
- state 3 (diving): 2 frames; state 4 (lying after the dive): 1 frame
- state 5 (win) / 6 (lose): 0 -> 4, then hold frame 4
"""

from characters import Pose

FRAME_COUNTS = [5, 5, 5, 2, 1, 5, 5]

# feet hang a little lower in the air
AIR = dict(back_foot=(-1, 1), front_foot=(1, 1))

POSES = {
    # standing: gentle bob, arm swing, feet shuffle
    (0, 0): Pose(),
    (0, 1): Pose(squash=1, arm=52, back_foot=(-1, 0), front_foot=(1, 0)),
    (0, 2): Pose(squash=2, arm=60),
    (0, 3): Pose(squash=1, arm=52, back_foot=(1, 0), front_foot=(-1, 0)),
    (0, 4): Pose(arm=38),

    # jump: arm flaps, feet dangle
    (1, 0): Pose(squash=-1, arm=-20, **AIR),
    (1, 1): Pose(arm=10, **AIR),
    (1, 2): Pose(squash=1, arm=40, **AIR),
    (1, 3): Pose(arm=10, **AIR),
    (1, 4): Pose(squash=-2, arm=-40, **AIR),

    # power hit: lean back with the arm cocked, then smash forward and
    # down; the jelly arm stretches
    (2, 0): Pose(lean=-2, arm=-30, arm_len=12, mouth='open', **AIR),
    (2, 1): Pose(lean=-3, squash=-1, arm=-45, arm_len=13, mouth='open',
                 **AIR),
    (2, 2): Pose(arm=-5, arm_len=16, eyes='wince', mouth='open', **AIR),
    (2, 3): Pose(lean=3, arm=25, arm_len=16, eyes='wince', mouth='open',
                 **AIR),
    (2, 4): Pose(lean=1, arm=50, arm_len=12, **AIR),

    # diving forward and lying on the floor after it
    (3, 0): Pose(dive=1, arm=-2, arm_len=12, eyes='wince', mouth='open'),
    (3, 1): Pose(dive=1, dx=1, dy=-1, arm=-8, arm_len=14, eyes='wince',
                 mouth='open'),
    (4, 0): Pose(dive=2, arm=8, arm_len=11, eyes='closed', mouth='flat'),

    # win: hop and wave the arm out front, eyes closed in a smile
    (5, 0): Pose(arm=20, eyes='closed', mouth='open'),
    (5, 1): Pose(dy=-2, arm=-10, arm_len=12, eyes='closed', mouth='open',
                 **AIR),
    (5, 2): Pose(dy=-4, squash=-1, arm=-20, arm_len=13, eyes='closed',
                 mouth='open', **AIR),
    (5, 3): Pose(dy=-2, arm=-10, arm_len=12, eyes='closed', mouth='open',
                 **AIR),
    (5, 4): Pose(arm=-20, arm_len=13, eyes='closed', mouth='open'),

    # lose: startled, then slumps down dizzy
    (6, 0): Pose(arm=70, eyes='surprised', mouth='o', sweat=True),
    (6, 1): Pose(neck=1, arm=80, eyes='surprised', mouth='o', sweat=True),
    (6, 2): Pose(neck=3, squash=2, arm=85, eyes='dizzy', mouth='frown'),
    (6, 3): Pose(neck=4, squash=3, arm=90, eyes='dizzy', mouth='frown'),
    (6, 4): Pose(neck=5, squash=3, arm=90, eyes='dizzy', mouth='frown'),
}

assert sorted(POSES) == [(s, f) for s, n in enumerate(FRAME_COUNTS)
                         for f in range(n)]
