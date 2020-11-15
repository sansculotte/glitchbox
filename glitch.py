#!/usr/bin/env python3
# vim: sts=4: ts=4: sw=4:
import sys
import argparse
import cv2  # type: ignore
import numpy as np  # type: ignore
from scipy.ndimage import rotate, center_of_mass  # type: ignore
import random


class GlitchBase:
    """
    base class for shared glitch operations
    """

    bitmap = None

    def random_block(self):
        """
        Coordinates for a random block
        """
        if self.margin is None:
            margin = (self.width//10, self.height//10)
        else:
            margin = (self.margin, self.margin)

        x_start = random.randint(0, self.width-margin[0])
        width = random.randint(1, self.width - x_start - margin[0])
        x_edge = (x_start, width)

        y_start = random.randint(0, self.height-margin[1])
        height = random.randint(1, self.height - y_start - margin[1])
        y_edge = (y_start, height)

        return (x_edge, y_edge)

    def save(self, outfile):
        """ Save the scrambled files """
        cv2.imwrite(outfile, self.bitmap)


class Glitcher(GlitchBase):
    """
    Inject, distort, disturb, intersect, explode an image file with various
    methods of destruction
    """
    def __init__(self, args):
        """ Run the glitcher """
        if args.imagefile:
            self.bitmap = cv2.imread(args.imagefile)

        self.line: int = args.line
        self.block: int = args.block
        self.rotation: int = args.rotation
        self.perspective: int = args.perspective
        self.angle: float = args.angle
        self.margin: int = args.margin
        self.jitter: int = args.jitter
        self.mask = args.mask

    def glitch(self):
        """ Run the glitcher """
        if self.bitmap is None:
            raise Exception('No image loaded')

        self.height, self.width, self.colors = self.bitmap.shape

        self.line_glitch(amount=self.line)
        self.block_glitch(amount=self.block)
        self.block_rotate_glitch(amount=self.rotation)
        self.perspective_scramble(amount=self.perspective)

    def line_glitch(self, amount: int = 0):
        """
        Move random selection of lines in x-direction
        """
        if amount <= 0:
            return

        for i in range(amount):
            line = random.randint(0, self.height-1)
            shift = random.randint(0, amount) - amount // 2
            self.bitmap[line] = np.roll(self.bitmap[line], shift, 0)

    def block_glitch(self, amount: int = 0):
        """
        Copy blocks around
        """
        if not amount > 0:
            return

        for i in range(amount):
            edge_x, edge_y = self.random_block()
            x = max(0, edge_x[0] + random.randint(0, amount) - amount // 2)
            y = max(0, edge_y[0] + random.randint(0, amount) - amount // 2)
            while (
                x + edge_x[1] < self.width
                or random.randint(0, amount) > 0
            ):
                try:
                    if random.randint(0, 10) > 5:
                        # rotate 90°
                        self.bitmap[
                            y:y+edge_y[1],
                            x:x+edge_x[1]
                        ] = self.bitmap[
                            edge_y[0]:sum(edge_y),
                            edge_x[0]:sum(edge_x)
                        ]
                    else:
                        self.bitmap[
                            x:x+edge_x[1],
                            y:y+edge_y[1]
                        ] = self.bitmap[
                            edge_x[0]:sum(edge_x),
                            edge_y[0]:sum(edge_y)
                        ]
                except Exception:
                    pass

                if self.jitter:
                    jitter = self.jitter
                    x += edge_x[1] + random.randint(0, jitter) - jitter // 2
                    y += random.randint(0, jitter) - jitter // 2
                else:
                    x += edge_x[1]

    def block_rotate_glitch(self, amount: int = 0):
        """
        Cut blocks, rotate and reinsert
        """
        if amount <= 0:
            return

        for i in range(amount):
            edge_x, edge_y = self.random_block()
            x = random.randint(0, self.width - edge_x[1])
            y = random.randint(0, self.height - edge_y[1])
            try:
                block = self.bitmap[
                    edge_x[0]:sum(edge_x),
                    edge_y[0]:sum(edge_y)
                ]
                rotated = rotate(block, self.angle, mode='nearest')
                width, height, _ = rotated.shape
                self.bitmap[x:x + width, y:y + height] = rotated
            except Exception as e:
                print(e)
                pass

    def perspective_scramble(self, amount: int = 0):
        """
        Cut image into shards and throw them into space
        """
        if amount <= 0:
            return

        cow = center_of_mass(self.bitmap)
        mop = (self.width // 2, self.height // 2)
        if isinstance(cow, list):
            cow = cow[0]
            mop = cow[1]

        for i in range(amount):
            edge_x, edge_y = self.random_block()
            x = random.randint(0, self.width - edge_x[1])
            y = random.randint(0, self.height - edge_y[1])

            pts1 = np.float32([
                [edge_x[0], edge_y[0]],
                [sum(edge_x), edge_y[0]],
                [edge_x[0], sum(edge_y)],
                [sum(edge_x), sum(edge_y)]
            ])
            pts2 = np.float32([
                [cow[0], cow[1]],
                [mop[0], mop[1]],
                [x, y],
                [(x + sum(edge_x)) % self.width, (y + sum(edge_y)) % self.height]
            ])
            M = cv2.getPerspectiveTransform(pts1, pts2)
            try:
                warped = cv2.warpPerspective(
                    self.bitmap,
                    M,
                    (self.width - int(cow[0]), self.height - int(cow[1]))
                )
                width, height, colors = warped.shape
                t_x = int(cow[0])
                t_y = int(cow[1])
                for c in range(colors):
                    self.bitmap[t_x:(t_x + width), t_y:(t_y + height), c] = warped[:, :, c]

            except Exception as e:
                print(e)
                pass

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Image Scrambler')
    ap.add_argument('imagefile', metavar='imagefile', type=str,
        help='filename of image to be scrambled'
    )
#    parser.add_argument('action', metavar='action', type=str, default='block',
#        help='module for the glitching')
    ap.add_argument('-o', '--outfile', dest='outfile', action='store',
        default='output.png',
        help='image file to write output to'
    )
    ap.add_argument('-b', '--block', dest='block', type=int, action='store',
        default=9,
        help='amount of block destruction'
    )
    ap.add_argument('-l', '--line', dest='line', type=int, action='store',
        default=9,
        help='amount of line destruction'
    )
    ap.add_argument('-r', '--rotation', dest='rotation', type=int, action='store',
        default=0,
        help='amount of rotation'
    )
    ap.add_argument('-p', '--perspective', dest='perspective', type=int, action='store',
        default=0,
        help='amount of perspective sharding'
    )
    ap.add_argument('-a', '--angle', dest='angle', type=float, action='store',
        default=7.0,
        help='rotation angle in degree, defaults to 7°'
    )
    ap.add_argument('-m', '--margin', dest='margin', type=int, action='store',
        help='block size limit, default to 10%% of image'
    )
    ap.add_argument('-j', '--jitter', dest='jitter', type=int, action='store',
        help='translation abberations'
    )
    ap.add_argument('-M', '--mask', dest='mask', action='store',
        help='Mask an area within which to apply the glitch'
    )
    ap.add_argument('--mask-threshold', dest='mask_threshold', action='store',
        default=0.5
    )
    args = ap.parse_args()

    glitcher = Glitcher(args)
    try:
        glitcher.glitch()
    except Exception as e:
        print(e)
        sys.exit(-1)

    glitcher.save(args.outfile)
