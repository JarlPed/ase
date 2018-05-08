# -*- coding: utf-8 -*-
"""colors.py - select how to color the atoms in the GUI."""
from __future__ import unicode_literals
from ase.gui.i18n import _

import numpy as np

import ase.gui.ui as ui
from ase.gui.utils import get_magmoms


class ColorWindow:
    """A window for selecting how to color the atoms."""
    def __init__(self, gui):
        self.win = ui.Window(_('Colors'))
        self.gui = gui
        self.win.add(ui.Label(_('Choose how the atoms are colored:')))
        values = ['jmol', 'tag', 'force', 'velocity',
                  'initial charge', 'magmom', 'neighbors']
        labels = [_('By atomic number, default "jmol" colors'),
                  _('By tag'),
                  _('By force'),
                  _('By velocity'),
                  _('By initial charge'),
                  _('By magnetic moment'),
                  _('By number of neighbors'),]

        self.radio = ui.RadioButtons(labels, values, self.toggle,
                                     vertical=True, )
        self.radio.value = gui.colormode
        self.win.add(self.radio)
        self.activate()
        self.label = ui.Label()
        self.win.add(self.label)

    def change_mnmx(self):
        print('change min/max value')
        mn, mx = self.mnmx[1].value, self.mnmx[3].value
        colorscale, _, _ = self.gui.colormode_data
        self.gui.colormode_data = colorscale, mn, mx
        self.gui.draw()

    def activate(self):
        images = self.gui.images
        atoms = self.gui.atoms
        radio = self.radio
        radio['tag'].active = atoms.has('tags')

        # XXX not sure how to deal with some images having forces,
        # and other images not.  Same goes for below quantities
        F = images.get_forces(atoms)
        radio['force'].active = F is not None
        radio['velocity'].active = atoms.has('momenta')
        radio['initial charge'].active = atoms.has('initial_charges')
        radio['magmom'].active = get_magmoms(atoms).any()
        radio['neighbors'].active = True

    def toggle(self, value):
        self.gui.colormode = value
        if value == 'jmol' or value == 'neighbors':
            text = ''
        else:
            scalars = np.array([self.gui.get_color_scalars(i)
                                for i in range(len(self.gui.images))])
            mn = scalars.min()
            mx = scalars.max()
            try:
                import matplotlib as plt
                # matplotlib diverse colormaps
                cmaps = ['magma', 'viridis', 'plasma', 'inferno', 
                         'rainbow', 'jet',
                         'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
                         'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm',
                         'bwr', 'seismic']
                print('set self.colormap')
                self.colormap = ui.ComboBox(cmaps, cmaps, self.update_colormap)
                self.gui.colormode_data = None, mn, mx
                self.update_colormap(cmaps[0])
                self.win.add(self.colormap)
            except:
                colorscale = ['#{0:02X}AA00'.format(red)
                              for red in range(0, 240, 10)]
                self.gui.colormode_data = colorscale, mn, mx

            unit = {'tag': '',
                    'force': 'eV/Ang',
                    'velocity': '??',
                    'charge': '|e|',
                    'initial charge': '|e|',
                    u'magmom': 'μB'}[value]
            text = '[{0},{1}]: [{2:.6f},{3:.6f}] {4}'.format(
                _('Green'), _('Yellow'), mn, mx, unit)

            rng = mx - mn  # XXX what are optimal allowed range and steps ?
            self.mnmx = [_('min:'),
                         ui.SpinBox(mn, mn - 10 * rng, mx + rng, rng / 10.,
                                    self.change_mnmx),
                         _('max:'),
                         ui.SpinBox(mx, mn - 10 * rng, mx + rng, rng / 10.,
                                    self.change_mnmx),
                         _(unit)
            ]
            self.win.add(self.mnmx)

        self.label.text = text
        self.radio.value = value
        self.gui.draw()
        return text  # for testing

    def notify_atoms_changed(self):
        "Called by gui object when the atoms have changed."
        self.activate()
        mode = self.gui.colormode
        if not self.radio[mode].active:
            mode = 'jmol'
        self.toggle(mode)

    def update_colormap(self, cmap):
        "Called by gui when colormap has changed"
        N = 10  # XXX change default n
        print('gewaehlt:', cmap)
        colorscale, mn, mx = self.gui.colormode_data
        import pylab as plt
        import matplotlib
        cmap = plt.cm.get_cmap(cmap)
        print('0 colorscale', colorscale)
        colorscale = [matplotlib.colors.rgb2hex(c[:3]) for c in
                      cmap(np.linspace(0, 1, N))]
        print('1 colorscale', colorscale)
        self.gui.colormode_data = colorscale, mn, mx
        self.gui.draw()
