Glitchbox
=========

You need "opencv":http://opencv.org/ python bindings installed.



Usage
=====

to run an animation do something like this:

    for i in $(seq 1 100); do ./glitch.py ~/grfx/vector/praxis_graffitty.png -o anim/$(printf %03d $i).png -a 25 -m 350; done

or this:

    for i in $(seq 1 100); do ./glitch.py ~/grfx/vector/praxis_graffitty.png -o anim/$(printf %03d $i).png -a $((20+$i)) -m 350; done
