# vim: sts=4: ts=4: sw=4:
import cv2
import argparse

class Glitcher:
    """
    Inject, distort, disturb, intersect, explode an image file with various
    methods of destruction
    """
    def __init__(self, img=img, filname=filename):
        """ Run the glitcher """
        self.bitmap = None 
        if img:
            self.bitmap = img
        if filename:
            self.bitmap = cv.imread( filename )

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
    parser.add_argument('imagefile', type=string, action='store_const',
                   help='filename of image to be scrambled')
    parser.add_argument('--outfile', '-o', dest='outfile', action='store_const',
                   help='sum the integers (default: find the max)')

    glitcher = Glitcher( imagefile )
    try:
        glitcher.glitch
    except Exception, e:
        print e
        return(-1)

    glitcher.save( outfile )
