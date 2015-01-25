# vim: sts=4: ts=4: sw=4:
import sys
import argparse
import cv2

class Glitcher:
    """
    Inject, distort, disturb, intersect, explode an image file with various
    methods of destruction
    """
    def __init__(self, img=None, filename=None):
        """ Run the glitcher """
        self.bitmap = None 
        if img:
            self.bitmap = img
        if filename:
            self.bitmap = cv2.imread( filename )

    def glitch(self):
        """ Run the glitcher """
        if not self.bitmap:
            raise Exception('No image loaded')
        self.bitmap = self.bitmap

    def save(self, outfile):
        """ Save the scrambled files """
        cv2.imwrite( outfile, self.bitmap )


if __name__ == '__main__':
    parser = argparse.ArgumentParser( description='Image Scrambler' )
    parser.add_argument('imagefile', metavar='imagefile', type=str,
        help='filename of image to be scrambled')
    parser.add_argument('-o', '--outfile', dest='outfile', action='store', default='output.png',
        help='image file to write output to')
    args = parser.parse_args()

    glitcher = Glitcher( filename=args.imagefile )
    try:
        glitcher.glitch
    except Exception, e:
        print e
        sys.exit(-1)

    glitcher.save( args.outfile )
