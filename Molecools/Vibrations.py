"""
Provides classes that manage molecular vibrations
"""

import numpy as np, scipy.linalg as slag
from McUtils.Coordinerds.CoordinateSystems import CoordinateSystem, CartesianCoordinates3D, CoordinateSet
from McUtils.Data import AtomData, UnitsData
from .Molecule import Molecule
from .Transformations import MolecularTransformation

__all__ = [
    "MolecularVibrations",
    "MolecularNormalModes",
]

class MolecularVibrations:

    def __init__(self,
                 molecule, basis,
                 freqs = None,
                 init = None
                 ):
        """Sets up a vibration for a Molecule object over the CoordinateSystem basis

        :param molecule:
        :type molecule: Molecule
        :param init:
        :type init: None | CoordinateSet
        :param basis:
        :type basis: MolecularNormalModes
        """
        self._mol = molecule
        self._coords = init
        self._basis = basis
        if freqs is None and hasattr(basis, "freqs"):
            freqs = basis.freqs
        self.freqs = freqs

    @property
    def basis(self):
        return self._basis
    @property
    def molecule(self):
        return self._mol
    @molecule.setter
    def molecule(self, mol):
        self._mol = mol
    @property
    def coords(self):
        if self._coords is None:
            if self._basis.in_internals:
                return self._mol.internal_coordinates
            else:
                return self._mol.coords
        else:
            return self._coords

    def __len__(self):
        return self._basis.matrix.shape[0]

    def displace(self, displacements = None, amt = .1, n = 1, which = 0):

        if displacements is None:
            displacements = self._basis.displacement(np.arange(1, n+1)*amt)
        displacements = np.asarray(displacements)
        if displacements.ndim == 1:
            disp_coords = CoordinateSet(np.zeros((n,) + self._basis.coordinate_shape), self._basis)
            disp_coords[:, which] = displacements
        else:
            disp_coords = CoordinateSet(displacements, self._basis)
        coords = np.broadcast_to(self._coords, (n, ) + self._coords.shape)
        disp_coords = disp_coords.convert(self._coords.system)
        displaced = coords + disp_coords
        return displaced

    def visualize(self, step_size = .1, steps = (5, 5), which = 0, anim_opts = None, mode = 'fast', **plot_args):
        from McUtils.Plots import Animator

        if isinstance(steps, (int, np.integer)):
            steps = [steps, steps]

        left  = np.flip(self.displace(amt=-step_size, n=steps[0], which=which), axis=0)
        right = self.displace(amt=step_size, n=steps[1], which=which)
        all_geoms = np.concatenate((left, np.broadcast_to(self._coords, (1, ) + self._coords.shape), right))

        figure, atoms, bonds = self._mol.plot(*all_geoms, objects = True, mode = mode, **plot_args)

        def animate(*args, frame = 0, _atoms = atoms, _bonds = bonds, _figure = figure):

            my_stuff = []
            nframes = len(_atoms)
            forward = ( frame // nframes ) % 2 == 0
            frame = frame % nframes
            if not forward:
                frame = -frame - 1

            if _atoms[frame] is not None:
                for a in _atoms[frame]:
                    coll = a.plot(figure)
                    my_stuff.append(coll)
            if _bonds[frame] is not None:
                for b in _bonds[frame]:
                    for bb in b:
                        p = bb.plot(figure)
                        try:
                            my_stuff.extend(p)
                        except ValueError:
                            my_stuff.append(p)

            return my_stuff

        if anim_opts is None:
            anim_opts = {}
        return Animator(figure, None, plot_method = animate, **anim_opts)

class MolecularNormalModes(CoordinateSystem):
    """
    A Coordinerds CoordinateSystem object that manages all of the data needed to
     work with normal mode coordinates + some convenience functions for generating and whatnot
    """
    name="MolecularNormalModes"
    def __init__(self,
                 molecule, coeffs,
                 name=None, freqs=None,
                 internal=False, origin=None, basis=None, inverse=None
                 ):
        if freqs is None:
            freqs = np.diag(coeffs.T@coeffs)
        if inverse is None:
            if freqs is not None:
                inverse = coeffs.T/freqs[:, np.newaxis]
            else:
                inverse = None
        self.molecule = molecule
        self.in_internals = internal
        # if origin is None:
        #     origin = molecule.coords
        if basis is None:
            basis = molecule.sys
        super().__init__(
            matrix=coeffs,
            inverse=inverse,
            name=self.name if name is None else name,
            basis=basis,
            dimension=(len(freqs),),
            origin=origin
        )
        self.freqs = freqs
    # also need a Cartesian equivalent of this
    def to_internals(self, intcrds=None, dYdR=None, dRdY=None):
        if self.in_internals:
            return self
        else:
            if intcrds is None:
                intcrds = self.molecule.internal_coordinates
                if intcrds is None:
                    raise ValueError("{}.{}: can't convert to internals when molecule {} has no internal coordinate specification".format(
                        type(self).__name__,
                        'to_internals',
                        self.molecule
                    ))
            if dRdY is None or dYdR is None:
                internals = intcrds.system
                ccoords = self.molecule.coords
                carts = ccoords.system
                ncrds = self.matrix.shape[0]
                dXdR = intcrds.jacobian(carts, 1).reshape(ncrds, ncrds)
                dRdX = ccoords.jacobian(internals, 1).reshape(ncrds, ncrds)
                masses = self.molecule.masses
                mass_conv = np.sqrt(np.broadcast_to(masses[:, np.newaxis], (3, len(masses))).flatten())
                dYdR = dXdR * mass_conv[np.newaxis]
                dRdY = dRdX / mass_conv[:, np.newaxis]

            # get the new normal modes
            dQdR = dYdR@self.matrix
            dRdQ = self.inverse@dRdY

            return type(self)(self.molecule, dQdR,
                              basis = intcrds.system, origin=intcrds, inverse=dRdQ,
                              internal=True, freqs=self.freqs
                              )
    @property
    def origin(self):
        if self._origin is None:
            if self.in_internals:
                return self.molecule.internal_coordinates
            else:
                return self.molecule.coords

    def embed(self, frame):
        """

        :param frame:
        :type frame: MolecularTransformation
        :return:
        :rtype:
        """

        raise NotImplementedError("Haven't finished doing this... :)")

        import copy

        if self.in_internals:
            raise ValueError("Internal coordinate normals modes can't be re-embedded")

        tmat = frame.matrix
        mat = self.matrix
        mat = tmat@mat

        orig = self.origin
        orig = tmat@orig

        return type(self)(
            self.molecule,
            mat,
            origin = orig
        )


    @classmethod
    def from_force_constants(cls,
                             molecule,
                             fcs,
                             atoms = None,
                             masses = None,
                             mass_units = "AtomicMassUnits",
                             inverse_mass_matrix = False,
                             remove_transrot = True,
                             normalize = True,
                             **opts
                             ):
        """
        Generates normal modes from the specified force constants

        :param molecule:
        :type molecule: Molecule
        :param fcs: force constants array
        :type fcs: np.ndarray
        :param atoms: atom list
        :type atoms: Iterable[str]
        :param masses: mass list
        :type masses: Iterable[float]
        :param mass_units: units for the masses...not clear if this is useful or a distraction
        :type mass_units: str
        :param inverse_mass_matrix: whether or not we have G or G^-1 (default: `False`)
        :type inverse_mass_matrix: bool
        :param remove_transrot: whether or not to remove the translations and rotations (default: `True`)
        :type remove_transrot: bool
        :param normalize: whether or not to normalize the modes (default: `True`)
        :type normalize: bool
        :param opts:
        :type opts:
        :return:
        :rtype: MolecularNormalModes
        """

        # this needs some major clean up to be less of a
        # garbage fire

        if atoms is None and masses is None:
            masses = molecule.masses
            mass_units = "AtomicMassUnits" # Danger, Will Robinson! This will likely need to be un-hard-coded in the future...

        if atoms is not None and masses is None:
            masses = np.array([AtomData[a, "Mass"] if isinstance(a, str) else a for a in atoms])

        if mass_units != "AtomicUnitOfMass" and mass_units != "ElectronMass":
            mass_conv = UnitsData.convert(mass_units, "AtomicUnitOfMass"),
        else:
            mass_conv = 1

        if masses is not None:
            masses = np.asarray(masses)
            masses = masses*mass_conv
            if masses.ndim == 1:
                masses = np.broadcast_to(masses, (len(masses), 3)).T.flatten()
                masses = np.diag(masses)
                inverse_mass_matrix = True
        else:
            masses = np.eye(len(fcs))

        freqs, modes = slag.eigh(fcs, masses, type=(1 if inverse_mass_matrix else 3))
        if normalize:
            normalization = np.broadcast_to(1/np.linalg.norm(modes, axis=0), modes.shape)
            modes = modes * normalization

        freqs = np.sign(freqs) * np.sqrt(np.abs(freqs))
        sorting = np.argsort(freqs)
        if remove_transrot:
            sorting = sorting[6:]

        freqs = freqs[sorting]
        modes = modes[:, sorting]

        return cls(molecule, modes, freqs = freqs, **opts)