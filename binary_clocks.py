import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation


class Clock():

    colors = {"background": "black", "text": "white",
              "clock": "white", "hand": "tab:blue"}

    def __init__(self, freq, axis, base=2, scale=1):
        self.freq, self. axis, self.base, self.scale = freq, axis, base, scale
        self.__initialize()

    def __initialize(self):
        self.time = 0.
        self.axis.axis("off")
        self.axis.set_aspect(1)
        self.axis.set_xlim([0, 1]), self.axis.set_ylim([0, 1])
        self.axis.add_patch(plt.Circle((.5, .5), 0.49, fill=False,
                                       transform=self.axis.transAxes, lw=2,
                                       color=self.colors["clock"]))
        for i in range(self.base):
            self.axis.text(0.5+0.4*np.cos(np.pi/2 - i/self.base*(2*np.pi)),
                           0.5+0.4*np.sin(np.pi/2 - i/self.base*(2*np.pi)),
                           f"{i}", va="center", ha="center",
                           color=self.colors["text"],
                           fontsize=self.scale *
                           (1 if self.base <= 12 else 12/self.base),
                           transform=self.axis.transAxes)

        self.arrow = self.axis.arrow(.5, .5, 0, .4, width=0.05, head_width=.1,
                                     length_includes_head=True, lw=1,
                                     color=self.colors["hand"],
                                     transform=self.axis.transAxes)
        self.update()

    def getUpdatables(self):
        return [self.arrow]

    def increment(self, dt, update=False):
        self.time += dt
        if update:
            self.update()

    def update(self):
        coords = self.axis.transData.transform([.5, .5])
        self.arrow.set_transform(
            self.axis.transData + mpl.transforms.Affine2D().rotate_around(*coords, -2*np.pi*self.freq*self.time))


class TModNum():

    def __init__(self, freq, axis, base=2, scale=1):
        self.freq, self. axis, self.base, self.scale = freq, axis, base, scale
        self.__initialize()

    def __initialize(self):
        self.time = 0.
        self.axis.axis("off")
        self.axis.set_aspect(1)
        self.axis.set_xlim([0, 1]), self.axis.set_ylim([0, 1])

        self.text = self.axis.text(.5, .5, "", va="center", ha="center",
                                   color=Clock.colors["text"],
                                   transform=self.axis.transAxes,
                                   fontsize=self.scale)
        self.update()

    def getUpdatables(self):
        return [self.text]

    def increment(self, dt, update=False):
        self.time += dt
        if update:
            self.update()

    def update(self):
        if self.base == 2:
            self.text.set_text(f"{(int(2*self.time*self.freq))&1}")
        else:
            self.text.set_text(
                f"{int(self.time*self.freq*self.base)%self.base:02.0f}")


# Plot VARS ##
FPS = 60


# CLOCKBASES and DISPLAYBASES are lowest clock and display first (aka right to left)

# CLOCKBASES = [12, 12, 12]
# DISPLAYBASES = [60, 60, 24]

CLOCKBASES = [2]*8 # [2]*8 = 8 bit clock
DISPLAYBASES = CLOCKBASES

DIGITS = len(CLOCKBASES)

f0 = 1/2
dt = 1/FPS

T = (np.cumprod(DISPLAYBASES)/DISPLAYBASES[0])[-1]/f0

Nframes = int(T * FPS)

fig_width = 15  # inches
figsize = (fig_width, fig_width*2./DIGITS)

fig = plt.figure(constrained_layout=True, figsize=figsize, dpi=96)
fig.patch.set_facecolor(Clock.colors["background"])
grid = gridspec.GridSpec(nrows=2, ncols=DIGITS, figure=fig)

clocks, bits, updatables = [], [], []
for i, (clockbase, displaybase) in enumerate(zip(CLOCKBASES, DISPLAYBASES)):
    f = f0/(np.cumprod(DISPLAYBASES)/DISPLAYBASES[0])[i]

    bits.append(TModNum(freq=f, axis=fig.add_subplot(grid[0, DIGITS-i-1]),
                        base=displaybase,
                        scale=40*fig.get_size_inches()[0]/DIGITS))
    clocks.append(Clock(freq=f, axis=fig.add_subplot(grid[1, DIGITS-i-1]),
                        base=clockbase,
                        scale=22))
    updatables.extend(bits[-1].getUpdatables())
    updatables.extend(clocks[-1].getUpdatables())


def plot_update(frame):
    if frame != 0:
        for bit, clock in zip(bits, clocks):
            bit.increment(dt, update=True)
            clock.increment(dt, update=True)
    return (*updatables,)


ani = FuncAnimation(fig, func=plot_update, interval=1000 /
                    FPS, frames=range(Nframes), blit=True, repeat=False)
