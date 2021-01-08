## <a id="Psience.BasisReps.Operators.Operator">Operator</a>
Provides a (usually) _lazy_ representation of an operator, which allows things like
QQQ and pQp to be calculated block-by-block.
Crucially, the underlying basis for the operator is assumed to be orthonormal.

### Properties and Methods
<a id="Psience.BasisReps.Operators.Operator.__init__" class="docs-object-method">&nbsp;</a>
```python
__init__(self, funcs, quanta, prod_dim=None, symmetries=None, selection_rules=None, zero_threshold=1e-14): 
```

- `funcs`: `callable | Iterable[callable]`
    >The functions use to calculate representation
- `quanta`: `int | Iterable[int]`
    >The number of quanta to do the deepest-level calculations up to (also tells us dimension)
- `prod_dim`: `int | None`
    >The number of functions in `funcs`, if `funcs` is a direct term generator
- `symmetries`: `Iterable[int] | None`
    >Labels for the funcs where if two funcs share a label they are symmetry equivalent

<a id="Psience.BasisReps.Operators.Operator.ndim" class="docs-object-method">&nbsp;</a>
```python
@property
ndim(self): 
```

<a id="Psience.BasisReps.Operators.Operator.shape" class="docs-object-method">&nbsp;</a>
```python
@property
shape(self): 
```

<a id="Psience.BasisReps.Operators.Operator.get_inner_indices" class="docs-object-method">&nbsp;</a>
```python
get_inner_indices(self): 
```
Gets the n-dimensional array of ijkl (e.g.) indices that functions will map over
        Basically returns the indices of the inner-most tensor
- `:returns`: `_`
    >No description...

<a id="Psience.BasisReps.Operators.Operator.__getitem__" class="docs-object-method">&nbsp;</a>
```python
__getitem__(self, item): 
```

<a id="Psience.BasisReps.Operators.Operator.__getstate__" class="docs-object-method">&nbsp;</a>
```python
__getstate__(self): 
```

<a id="Psience.BasisReps.Operators.Operator.filter_symmetric_indices" class="docs-object-method">&nbsp;</a>
```python
filter_symmetric_indices(self, inds): 
```
Determines which inds are symmetry unique.
        For something like `qqq` all permutations are equivalent, but for `pqp` we have `pi qj pj` distinct from `pj qj pi`.
        This means for `qqq` we have `(1, 0, 0) == (0, 1, 0)` but for `pqp` we only have stuff like `(2, 0, 1) == (1, 0, 2)` .
- `inds`: `np.ndarray`
    >indices to filter symmetric bits out of
- `:returns`: `_`
    >symmetric indices & inverse map

<a id="Psience.BasisReps.Operators.Operator.get_elements" class="docs-object-method">&nbsp;</a>
```python
get_elements(self, idx, parallelizer=None): 
```
Calculates a subset of elements
- `idx`: `Iterable[(Iterable[int], Iterable[int])]`
    >bra and ket states as tuples of elements
- `:returns`: `_`
    >No description...

<a id="Psience.BasisReps.Operators.Operator.__repr__" class="docs-object-method">&nbsp;</a>
```python
__repr__(self): 
```

### Examples

