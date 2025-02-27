#!/usr/bin/env python

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

a0 = 1
f0 = 1
data = [(i, j) for i in range(10) for j in range(10)]
x, y = zip(*data)
z = [k * a0 / f0 for k in range(len(x))]

fig, ax = plt.subplots()
fig.subplots_adjust(left=0.25, bottom=0.25)
scatter = ax.scatter(x, y, c=z)

axcolor = 'lightgoldenrodyellow'
axfreq = fig.add_axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
axamp = fig.add_axes([0.25, 0.15, 0.65, 0.03], facecolor=axcolor)

sfreq = Slider(axfreq, 'Freq', -10, 10.0, valinit=f0)
samp = Slider(axamp, 'Amp', -10, 10.0, valinit=a0)

def update(val):
    amp = samp.val
    freq = sfreq.val
    scatter.set_array([k * amp / freq for k in range(len(x))])
    fig.canvas.draw_idle()

sfreq.on_changed(update)
samp.on_changed(update)

resetax = fig.add_axes([0.8, 0.025, 0.1, 0.04], facecolor=axcolor)
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')

def the_reset(event):
    sfreq.reset()
    samp.reset()

button.on_clicked(the_reset)

rax = fig.add_axes([0.025, 0.5, 0.15, 0.15], facecolor=axcolor)
radio = RadioButtons(rax, ('red', 'blue', 'green'), active=0)

def colorfunc(label):
    scatter.set_color(label)
    fig.canvas.draw_idle()

radio.on_clicked(colorfunc)

plt.show()
