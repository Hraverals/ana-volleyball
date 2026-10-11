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

AIR = dict(grounded=False, back_foot=(-1, 2), front_foot=(1, 1))

POSES = {
    # standing: gentle bob, arm swing, feet shuffle
    (0, 0): Pose(),
    (0, 1): Pose(dy=1, torso_sy=0.97, arm=60, back_foot=(-1, 0),
                 front_foot=(1, 0), tail=(0, 1)),
    (0, 2): Pose(dy=2, torso_sx=1.03, torso_sy=0.94, arm=72, tail=(0, 1),
                 ear_tilt=-4),
    (0, 3): Pose(dy=1, torso_sy=0.97, arm=60, back_foot=(1, 0),
                 front_foot=(-1, 0), tail=(0, 1)),
    (0, 4): Pose(arm=42, ear_tilt=3),

    # jump: arm flaps, feet dangle, ear streams back
    (1, 0): Pose(dy=1, torso_sy=1.04, arm=-30, ear_tilt=-12, tail=(1, -2),
                 **AIR),
    (1, 1): Pose(dy=1, arm=5, ear_tilt=-8, tail=(0, -1), **AIR),
    (1, 2): Pose(dy=1, torso_sy=0.97, arm=35, ear_tilt=-4, **AIR),
    (1, 3): Pose(dy=1, arm=5, ear_tilt=-8, tail=(0, -1), **AIR),
    (1, 4): Pose(torso_sy=1.05, arm=-55, ear_tilt=-15, head_dy=-1,
                 tail=(1, -3), **AIR),

    # power hit: lean back with the arm cocked up front, then smash
    # forward and down; the jelly arm stretches
    (2, 0): Pose(dy=1, torso_tilt=-8, arm=-35, arm_len=9, mouth='open',
                 ear_tilt=-10, **AIR),
    (2, 1): Pose(dy=1, torso_tilt=-14, head_dx=-1, arm=-40, arm_len=10,
                 mouth='open', ear_tilt=-18, tail=(1, 1), **AIR),
    (2, 2): Pose(dy=1, torso_tilt=-2, arm=-15, arm_len=11, eyes='wince',
                 mouth='open', ear_tilt=-12, **AIR),
    (2, 3): Pose(dy=1, torso_tilt=12, head_dx=2, arm=20, arm_len=11,
                 eyes='wince', mouth='open', ear_tilt=-20, tail=(-1, -2),
                 **AIR),
    (2, 4): Pose(dy=1, torso_tilt=6, head_dx=1, arm=50, arm_len=8,
                 ear_tilt=-8, **AIR),

    # diving forward: body stretched flat, arms reaching ahead, tail and
    # feet trailing behind
    (3, 0): Pose(dy=6, torso_tilt=84, torso_sy=1.4, head_dx=7, head_dy=6,
                 arm=-10, arm_len=10, ear_tilt=-30, eyes='wince',
                 mouth='open', tail=(-15, 17), tail_scale=0.8,
                 grounded=False),
    (3, 1): Pose(dy=7, torso_tilt=88, torso_sy=1.45, head_dx=8, head_dy=6,
                 arm=-3, arm_len=11, ear_tilt=-35, eyes='wince',
                 mouth='open', tail=(-15, 15), tail_scale=0.8,
                 grounded=False),

    # lying on the floor after the dive
    (4, 0): Pose(dy=11, torso_tilt=90, torso_sx=0.8, torso_sy=1.45,
                 head_dx=8, head_dy=11, arm=6, arm_len=10, ear_tilt=-45,
                 eyes='closed', mouth='flat', tail=(-15, 19),
                 tail_scale=0.8, grounded=False),

    # win: hop and wave the arm out front, eyes closed in a smile
    (5, 0): Pose(arm=20, eyes='closed', mouth='open'),
    (5, 1): Pose(dy=-2, torso_sy=1.03, arm=-10, arm_len=9, eyes='closed',
                 mouth='open', ear_tilt=-6, **AIR),
    (5, 2): Pose(dy=-4, torso_sy=1.05, arm=-18, arm_len=10, eyes='closed',
                 mouth='open', ear_tilt=-10, tail=(0, -2), **AIR),
    (5, 3): Pose(dy=-2, torso_sy=1.02, arm=-10, arm_len=9, eyes='closed',
                 mouth='open', ear_tilt=-6, **AIR),
    (5, 4): Pose(arm=-15, arm_len=10, head_dy=-1, eyes='closed',
                 mouth='open', ear_tilt=4),

    # lose: startled, then slumps down dizzy
    (6, 0): Pose(arm=70, eyes='surprised', mouth='o', sweat=True),
    (6, 1): Pose(dy=1, arm=80, head_dy=1, eyes='surprised', mouth='o',
                 sweat=True, ear_tilt=-15),
    (6, 2): Pose(dy=2, torso_sy=0.9, head_dy=4, arm=90, eyes='dizzy',
                 mouth='frown', ear_tilt=-22, tail=(0, 2)),
    (6, 3): Pose(dy=3, torso_sy=0.86, head_dy=6, arm=95, eyes='dizzy',
                 mouth='frown', ear_tilt=-28, tail=(0, 3)),
    (6, 4): Pose(dy=3, torso_sy=0.84, head_dy=7, arm=95, eyes='dizzy',
                 mouth='frown', ear_tilt=-32, tail=(0, 3)),
}

assert sorted(POSES) == [(s, f) for s, n in enumerate(FRAME_COUNTS)
                         for f in range(n)]
