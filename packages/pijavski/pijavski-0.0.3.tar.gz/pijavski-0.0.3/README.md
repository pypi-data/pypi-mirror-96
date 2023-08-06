# Pijavski

This is an example of how to use CFFI to call a Pijavski function written in C++ that optimises a test function and returns the minimum.

To install simply type:

```
$ pip install pijavski
```

To test, open a python console and import the package. The only available function at the moment is `get_minimum`, with arguments *lip*, *xl*, *xu*, *precision* and *maxiter*. The function prints `res`, `x0`, `f`, `prec`, `maxit`

```
>>> import pijavski
>>> pijavski.get_minimum()
0 -5323.428786928975 1.2546522006214123e-09 3.5218863499790176 65533
>>> pijavski.get_minimum(lip=3, xl=-100000, xu=100000, precision=1e-9, maxiter=1000000)
0 -87124.2182511797 2.102279885993885e-10 8.210802078457299 65533
```

The current version has a default test function `f=-cos(*x)+0.00001*(*x-100*3.1415)*(*x-100*3.1415)`. To change it, one needs to modify the source code and rebuild the package.
