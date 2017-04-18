Glitchbox
=========

Dependencies:
- [opencv](http://opencv.org/ python bindings installed)
- [numpy](http://www.numpy.org/)
- [scipy](http://www.scipy.org/)

this is best handled through pip, or your system's package manager


Usage
=====

glitch.py
---------

to run an animation do something like this:

    for i in $(seq 1 100); do ./glitch.py ~/grfx/vector/praxis_graffitty.png -o anim/$(printf %03d $i).png -a 25 -m 350; done

or this:

    for i in $(seq 1 100); do ./glitch.py ~/grfx/vector/praxis_graffitty.png -o anim/$(printf %03d $i).png -a $((20+$i)) -m 350; done



emerge.py
---------

will show an image or animation against a backdrop of noise, more amplitude shows more of the image,
less amplitude more of the noise. make some noise, by dumping data into a junkfile, like:

    cat someimage.tiff someaudiofile.wav somebinary > junkfile

example:

    ./emerge.py -s soundfile.wav image.png -o /tmp/ -t 0.05 --junkfile junkfile


distort.py
----------

shifts line horizontally by the amplitude of the input signal samples.

example:

    ./distort.py -s soundfile.wav image.png -o /tmp/ -a 15 


combine emerge and distort for better noise/signal ratio
