#!/usr/bin/env python3
# vim: sts=4: ts=4: sw=4:
import sys
import argparse
import cv2
import numpy as np
import random
from glitch import GlitchBase


class Merger(GlitchBase):
    """
    Combine two images in various ways
    """
    def __init__(self, args):
        self.method = args.method
        self.iterations = args.iterations
        self.jitter = args.jitter

    def merge(self, img1, img2):
        """ Run the merger """
        self.bitmap_1 = cv2.imread(img1)
        self.bitmap_2 = cv2.imread(img2)
        assert self.bitmap_1.any()
        assert self.bitmap_2.any()

        self.height, self.width, self.colors = self.bitmap_1.shape
        self.bitmap = np.zeros(shape=(self.width, self.height, 3), dtype=np.uint8)
        if self.method == 'block':
            self.block_merge(self.iterations, amount=100)
        elif self.method == 'convolution':

    def convolution_merge(self):
        l1 = np.reshape(self.bitmap_1, -1)
        l2 = np.reshape(self.bitmap_2, -1)
        l2 = np.resize(l2, 4321)
        new = np.convolve(l1, l2)
        ex = len(l2) // 2
        self.bitmap = np.reshape(new[ex:-ex], self.bitmap_1.shape)

    def block_merge(self, iterations, amount, relation=50):
        for i in range(iterations):
            edge_x, edge_y = self.random_block()
            x, width = edge_x
            y, height = edge_y

            # select source
            if random.randint(0, 100) > relation:
                source = self.bitmap_1
            else:
                source = self.bitmap_2

            source_width, source_height, _ = source.shape
            source_x, source_y = self.random_block(width=source_width, height=source_height)

            width = min(width, source_x[1])
            height = min(height, source_y[1])

            try:
                self.bitmap[
                    x:x+width,
                    y:y+height
                ] = source[
                    source_x[0]:source_x[0] + width,
                    source_y[0]:source_y[0] + height
                ]
            except Exception:
                pass

            if self.jitter:
                x += edge_x[1] + random.randint(0, 2) - 1
                y += random.randint(0, 2) - 1
            else:
                x += edge_x[1]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Image Scrambler')
    parser.add_argument('imagefile1', metavar='imagefile1', type=str,
        help='filename of first image to be merged')
    parser.add_argument('imagefile2', metavar='imagefile2', type=str,
        help='filename of second image to be merged')
    parser.add_argument('-o', '--outfile', dest='outfile', action='store', default='output.png',
        help='image file to write output to')
    parser.add_argument('-m', '--method', dest='method', action='store', default='block',
        help='merge method')
    parser.add_argument('-i', '--iterations', dest='iterations', type=int, action='store', default=100,
        help='merge method')
    parser.add_argument('-j', '--jitter', dest='jitter', type=int, action='store',
        help='translation abberations'
    )
    args = parser.parse_args()

    merger = Merger(args)
    try:
        merger.merge(args.imagefile1, args.imagefile2)

    except Exception as e:
        print(e)
        sys.exit(-1)

    merger.save(args.outfile)
