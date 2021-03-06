"""
Provides a very general specification for a RepresentationBasis object that can be
used to define matrix representations
"""
import abc, numpy as np

from .Terms import TermComputer
from .Operators import Operator

__all__ = [
    "RepresentationBasis",
    "SimpleProductBasis"
]

class RepresentationBasis(metaclass=abc.ABCMeta):
    """
    Metaclass for representations.
    Requires concrete implementations of the position and momentum operators.
    """
    name = "Basis"
    def __init__(self, function_generator, n_quanta):
        """

        :param function_generator:
        :type function_generator:
        :param n_quanta: numbers of quanta
        :type n_quanta: int
        """
        self.quanta = n_quanta
        self.generator = function_generator
    def __getitem__(self, item):
        if self.generator is None:
            raise ValueError("basis function generator is None (i.e. explicit functions can't be returned)")
        return self.generator(item)
    def __repr__(self):
        return "{}('{}', generator={})".format(
            'RepresentationBasis',
            self.name,
            self.generator
        )
    @abc.abstractmethod
    def p(self, n):
        """
        Generates the momentum matrix up to n-quanta

        There's one big subtlety to what we're doing here, which is that
          for efficiency reasons we return an entirely real matrix
        The reason for that is we assumed people would mostly use it in the context
          of stuff like pp, pQp, or pQQp, in which case the imaginary part pulls out
          and becomes a negative sign
        We actually use this assumption across _all_ of our representations
        :param n:
        :type n:
        :return:
        :rtype:
        """
        raise NotImplemented
    @abc.abstractmethod
    def x(self, n):
        """
        Generates the coordinate matrix up to n-quanta

        :param n:
        :type n:
        :return:
        :rtype:
        """
        raise NotImplemented

    @property
    def operator_mapping(self):
        return {'x':self.x, 'p':self.p}
    def operator(self, *terms):
        funcs = [self.operator_mapping[f] if isinstance(f, str) else f for f in terms]
        q = (self.quanta,)
        op = Operator(funcs, q)
        return op
    def representation(self, *terms):
        """
        Provides a representation of a product operator specified by 'terms'
        :param terms:
        :type terms:
        :return:
        :rtype:
        """

        q=self.quanta
        return TermComputer(self.operator(*terms), q)

class SimpleProductBasis(RepresentationBasis):
    """
    Defines a direct product basis from a simpler basis.
    Mixed product bases aren't currently supported
    """
    def __init__(self, basis_type, n_quanta):
        """

        :param basis_type: the type of basis to do a product over
        :type basis_type: type
        :param n_quanta: the number of quanta for the representations
        :type n_quanta: Iterable[int]
        """
        self.basis_type = basis_type
        self.bases = tuple(basis_type(n) for n in n_quanta)
        super().__init__(self.get_function, None)
    @property
    def quanta(self):
        return tuple(b.quanta for b in self.bases)
    @quanta.setter
    def quanta(self, n):
        if n is not None:
            raise ValueError("{}: '{}' can't be set directly".format(
                type(self).__name__,
                'quanta'
            ))

    def get_function(self, idx):
        fs = tuple(b[n] for b, n in zip(self.bases, idx))
        return lambda *r, _fs=fs, **kw: np.prod(f(*r, **kw) for f in _fs)

    def operator(self, *terms):
        funcs = [self.bases[0].operator_mapping[f] if isinstance(f, str) else f for f in terms]
        q = self.quanta
        op = Operator(funcs, q)
        return op
    def representation(self, *terms):
        """
        Provides a representation of a product operator specified by 'terms'
        :param terms:
        :type terms:
        :return:
        :rtype:
        """
        q = self.quanta
        return TermComputer(self.operator(*terms), q)
    def x(self, n):
        """
        Returns the representation of x in the multi-dimensional basis with every term evaluated up to n quanta
        Whether this is what we want or not is still TBD
        :param n:
        :type n:
        :return:
        :rtype:
        """
        return self.representation(self.bases[0].x)[:n, :n]
    def p(self, n):
        """
        Returns the representation of p in the multi-dimensional basis with every term evaluated up to n quanta
        Whether this is what we want or not is still TBD
        :param n:
        :type n:
        :return:
        :rtype:
        """
        return self.representation(self.bases[0].p)[:n, :n]
