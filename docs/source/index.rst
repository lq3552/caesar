.. CAESAR documentation master file, created by
   sphinx-quickstart on Mon May 16 19:26:15 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: https://www.dropbox.com/s/0ze29i1qgq3duzx/CAESAR_bust.png?raw=1
   :align: center
   
Welcome to CAESAR's documentation!
==================================

``CAESAR`` is a python-based ``yt`` extension package for analyzing
the outputs from cosmological simulations.  ``CAESAR`` takes as
input a single snapshot from a simulation, and outputs a portable
and compact ``HDF5`` catalog containing a host of galaxy and halo properties
that can be read in and explored without the original simulation
binary.  ``CAESAR`` thus provides a simple and intuitive interface
for exploring object data within your outputs.

``CAESAR`` generates a catalog as follows:

1. Identify halos (or import a halo membership list)

2. Compute halo physical properties

3. Within each halo, identify galaxies using 6-D friends-of-friends

4. Compute galaxy physical properties

5. Optionally, compute galaxy photometry including line-of-sight extinction

6. Create particle lists for each galaxy and halo

7. Link galaxies and halos, identify centrals+satellites, quantify environment

8. Output all information into a stand-alone ``hdf5`` file

``CAESAR`` is OpenMP-parallelized using ``cython`` and ``joblib``,
and has reasonably good scaling with the (user-specifiable) number
of cores.  It does, however, have somewhat stringent memory
requirements -- e.g. a run with two billion particles requires a
machine with 512 GB to generate the catalog, and this scales with
the number of particles.  The resulting ``CAESAR`` catalog typically has
a filesize of 1% of the original snapshot, as a ballpark figure.

Once the ``CAESAR`` catalog has been generated, it can be loaded
and the data easily accessed using simple python commands.  ``CAESAR``
also provides additional functionality such as identifying most
massive progenitors/descendants across snapshots, generating `FSPS
<http://dfm.io/python-fsps/current/>`_ spectra for objects, and
checking for contamination in zoom simulations.  Finally, since the
``CAESAR`` catalog contains particle lists for each galaxy and halo,
it enables you to quickly grab the relevant particle data in the original
snapshot in order to compute any other quantity you want.

``CAESAR`` builds upon the `yt <http://yt-project.org>`_ project,
which provides support for a number of `simulation codes
<http://yt-project.org/doc/reference/code_support.html>`_ and
`symbolic units <http://yt-project.org/doc/analyzing/units/index.html>`_.
All meaningful quantities stored within a ``CAESAR`` catalog have
units attached, reducing ambiguity when working with your data.
This tight connection enables you to use both ``yt`` and ``CAESAR``
functionality straightforwardly within a single analysis.

``CAESAR`` currently supports the following codes/formats:

1. `GADGET <http://wwwmpa.mpa-garching.mpg.de/~volker/gadget/>`_
2. `GIZMO <http://www.tapir.caltech.edu/~phopkins/Site/GIZMO.html>`_
3. `TIPSY <http://www-hpcc.astro.washington.edu/tools/tipsy/tipsy.html>`_
4. `ENZO <http://enzo-project.org/>`_
5. `ART <http://adsabs.harvard.edu/abs/1999PhDT........25K>`_
6. `RAMSES <http://www.ics.uzh.ch/~teyssier/ramses/RAMSES.html>`_

In principle, any ``yt``-supported simulation snapshot could be 
supported by ``CAESAR``, but it may not work out-of-the-box.
We accept pull requests for further functionality, and bug fixes
of course.

To get started, follow the Getting Started link below!

----

Contents
========

.. toctree::
   :maxdepth: 2

   getting_started
   running
   loading
   usage
   photometry
   units

----

.. toctree::
   :maxdepth: 2

   code_reference/reference
   
----

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

