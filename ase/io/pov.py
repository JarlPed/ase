import numpy as npy

from ase.io.eps import EPS
from ase.data import chemical_symbols

def pa(array):
    """Povray array syntax"""
    return '<% 6.2f, % 6.2f, % 6.2f>' % tuple(array)

def pc(array):
    """Povray color syntax"""
    if type(array) == str:
        return 'color ' + array
    if type(array) == float:
        return 'rgb <%.2f>*3' % array
    if len(array) == 3:
        return 'rgb <%.2f, %.2f, %.2f>' % tuple(array)
    if len(array) == 4: # filter
        return 'rgbf <%.2f, %.2f, %.2f, %.2f>' % tuple(array)
    if len(array) == 5: # filter and transmit
        return 'rgbft <%.2f, %.2f, %.2f, %.2f, %.2f>' % tuple(array)

class POVRAY(EPS):
    scale = 1.
    def cell_to_lines(self, A):
        return npy.empty((0, 3)), None, None

    def write(self, filename):
        # Scene setup. Should perhaps be moved to input keywords
        # x, y is the image plane, z is *out* of the screen
        display = True # Display while rendering
        ratio = float(self.w) / self.h
        canvas_width = 640
        camera_dist = 10. # z
        camera_type = 'orthographic'# perspective,orthographic,ultra_wide_angle
        point_lights = []           # [[loc1, color1], [loc2, color2], ...]
        area_light = [(1., 2., 50.),# location
                      'White',      # color
                      .7, .7, 4, 4] # width, height, Nlamps_x, Nlamps_y
        background = 'White'        # color

        # Produce the .ini file
        if filename.endswith('.pov'):
            ini = open(filename[:-4] + '.ini', 'w').write
        else:
            ini = open(filename + '.ini', 'w').write
        ini('Input_File_Name=%s\n' % filename)
        ini('Output_to_File=true\n')
        ini('Output_File_Type=N\n')
        ini('Output_Alpha=true\n')
        ini('; if you adjust Height, and width, you must preserve the ratio\n')
        ini('; Width / Height = %s\n' % repr(ratio))
        ini('Width=%i\n' % canvas_width)
        ini('Height=%i\n' % int(round(canvas_width / ratio)))
        ini('Antialias=true\n')
        ini('Antialias_Threshold=0.1\n')
        ini('Display=%s\n' % ['false', 'true'][display])
        ini('Pause_When_Done=true\n')
        ini('Verbose=false\n')
        del ini

        # Produce the .pov file
        w = open(filename, 'w').write
        w('#include "colors.inc"\n')
        w('#include "finish.inc"\n')
        w('\n')
        w('global_settings {assumed_gamma 1 max_trace_level 6}\n')
        w('background {%s}\n' % pc(background))
        w('camera {%s\n' % camera_type)
        w('  right %.2f*x up %.2f*y direction z\n' % (self.w, self.h))
        w('  location <0,0,%.2f> look_at <0,0,0>}\n' % camera_dist)
        for loc, rgb in point_lights:
            w('light_source {%s %s}\n' % (pa(loc), pc(rgb)))

        if area_light is not None:
            w('light_source {%s %s\n' % (pa(area_light[0]), pc(area_light[1])))
            w('  area_light <%.2f, 0, 0>, <0, %.2f, 0>, %i, %i\n' % tuple(
                area_light[2:6]))
            w('  adaptive 1 jitter}\n')

        w('\n')
        w('#declare simple = finish {phong 0.7}\n')
        w('#declare jmol = finish {'
          'ambient .2 '
          'diffuse .6 '
          'specular 1 '
          'roughness .001 '
          'metallic}\n')
        w('#declare ase2 = finish {'
          'ambient 0.05 '
          'brilliance 3 '
          'diffuse 0.6 '
          'metallic '
          'specular 0.70 '
          'roughness 0.04 '
          'reflection 0.15}\n')
        w('#declare ase3 = finish {'
          'ambient .2 '
          'brilliance 3 '
          'diffuse .6 '
          'metallic '
          'specular .7 '
          'roughness .001 '
          'reflection .02}\n')
        w('\n')
        w('#macro atom(LOC, R, COL, FIN)\n')
        w('  sphere{LOC, R texture{pigment{COL} finish{FIN}}}\n')
        w('#end\n')
        w('\n')
        
        z0 = self.X[:, 2].max()
        self.X -= (self.w / 2, self.h / 2, z0)

        # Draw unit cell
        if self.C is not None:
            self.C -= (self.w / 2, self.h / 2, z0)
            self.C.shape = (2, 2, 2, 3)
            for c in range(3):
                for j in ([0, 0], [1, 0], [1, 1], [0, 1]):
                    w('cylinder {')
                    for i in range(2):
                        j.insert(c, i)
                        x, y, z = self.C[tuple(j)]
                        del j[c]
                        w(pa([-x, y, z]) + ', ')
                    w('%0.3f pigment {Black}}\n' % 0.05)

        # Draw atoms
        a = 0
        for (x, y, z), dia, color in zip(self.X, self.d, self.colors):
            w('atom(%s, %.2f, %s, %s) // #%i \n' % (
                pa((-x, y, z)), dia / 2., pc(color), 'ase3', a))
            a += 1

def write_pov(filename, atoms, **parameters):
    if isinstance(atoms, list):
        assert len(atoms) == 1
        atoms = atoms[0]
    POVRAY(atoms, **parameters).write(filename)
