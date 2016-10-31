"""Test H2 molecule atomization with MOPAC."""
from ase.build import molecule
from ase.calculators.mopac import MOPAC
from ase.optimize import BFGS
h2 = molecule('H2', calculator=MOPAC(label='h2'))
BFGS(h2, trajectory='h2.traj').run(fmax=0.01)
e2 = h2.get_potential_energy()
h1 = h2.copy()
del h1[1]
h1.set_initial_magnetic_moments([1])
h1.calc = MOPAC(label='h1')
e1 = h1.get_potential_energy()
d = h2.get_distance(0, 1)
ea = 2 * e1 - e2
print(d, ea)
assert abs(d - 0.759) < 0.001
assert abs(ea - 5.907) < 0.001

calc = MOPAC('h2')
atoms = calc.get_atoms()
print('PM7 homo lumo:', calc.get_homo_lumo_levels())
calc.set(method='AM1')
atoms.get_potential_energy()
print('AM1 homo lumo:', calc.get_homo_lumo_levels())
