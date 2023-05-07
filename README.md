# Bezierve v2

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Tkinter application for Bézier curves read off.

It allows the user to create linear, quadratic and cubic Bézier curves, find their extrema and their bounding box and import images.
Its main promise is to provide users with the equations needed to create a Bézier curve. This is done by importing an image with the desired Bézier curve, creating one in the application and "shaping" it to look like the curve in the image, after which they can simple copy the equations as a tuple.

It also allows the user to save his progress as a save file and return to it anytime. This is done with the help of a .txt file.

Bezierve v2 is a follow up to my previous application Bezierve, where only one Bézier curve could be created. Because of how I constructed it, it would be challenging to add a support for multiple curves, so I decided to rework it from the ground up.
Together with the previous application, I worked on this project for roughly 2.5 months.

After I finished the previous application Bezierve, I published a [video](https://www.youtube.com/watch?v=HN47iyTLCG8& "My first desktop application in Tkinter") on my channel, where I go into a little bit more detail.

#

Start application with `python main.py`.
