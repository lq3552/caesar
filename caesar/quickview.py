import os.path

import h5py
import numpy as np
from yt.units.yt_array import YTQuantity, YTArray, UnitRegistry
from yt.funcs import mylog
from caesar.utils import info_printer
from caesar.simulation_attributes import SimulationAttributes
import IPython


class CAESAR:
    def __init__(self, filename):
        self.data_file = os.path.abspath(filename)
        with h5py.File(filename, 'r') as hd:
            mylog.info('Reading {}'.format(filename))

            self.unit_registry = UnitRegistry.from_json(
                hd.attrs['unit_registry_json'].decode('utf8'))

            # Load the information about the simulation itself
            self.simulation = SimulationAttributes()
            self.simulation._unpack(self, hd)

            # Load the particle index lists; this is the most expensive stage by a lot
            self.halo_dmlist = hd['halo_data/lists/dmlist'][:]
            self.halo_slist = hd['halo_data/lists/slist'][:]
            self.halo_glist = hd['halo_data/lists/glist'][:]

            if 'bhlist' in hd['halo_data/lists']:
                self.halo_bhlist = hd['halo_data/lists/bhlist'][:]

            self.galaxy_slist = hd['galaxy_data/lists/slist'][:]
            self.galaxy_glist = hd['galaxy_data/lists/glist'][:]

            if 'bhlist' in hd['galaxy_data/lists']:
                self.galaxy_bhlist = hd['galaxy_data/lists/bhlist'][:]

            self.galaxy_index_list = hd['halo_data/lists/galaxy_index_list'][:]

            mylog.info('Restoring halo attributes')
            self.halo_data = {}
            for k, v in hd['halo_data'].items():
                if type(v) == h5py.Dataset:
                    if 'unit' in v.attrs:
                        self.halo_data[k] = YTArray(
                            v[:], v.attrs['unit'], registry=self.unit_registry)
                    else:
                        self.halo_data[k] = v[:]

            self.halo_dicts = {}
            for k, v in hd['halo_data/dicts'].items():
                if 'unit' in v.attrs:
                    dictname, arrname = k.split('.')
                    if dictname not in self.halo_dicts:
                        self.halo_dicts[dictname] = {}
                    self.halo_dicts[dictname][arrname] = YTArray(
                        v[:], v.attrs['unit'], registry=self.unit_registry)
                else:
                    self.halo_dicts[dictname][arrname] = v[:]

            self.halos = [Halo(self, i) for i in range(hd.attrs['nhalos'])]

            mylog.info('Restoring galaxy attributes')
            self.galaxy_data = {}
            for k, v in hd['galaxy_data'].items():
                if type(v) == h5py.Dataset:
                    if 'unit' in v.attrs:
                        self.galaxy_data[k] = YTArray(
                            v[:], v.attrs['unit'], registry=self.unit_registry)
                    else:
                        self.galaxy_data[k] = v[:]

            self.galaxy_dicts = {}
            for k, v in hd['galaxy_data/dicts'].items():
                if 'unit' in v.attrs:
                    dictname, arrname = k.split('.')
                    if dictname not in self.galaxy_dicts:
                        self.galaxy_dicts[dictname] = {}
                    self.galaxy_dicts[dictname][arrname] = YTArray(
                        v[:], v.attrs['unit'], registry=self.unit_registry)
                else:
                    self.galaxy_dicts[dictname][arrname] = v[:]

            self.galaxies = [
                Galaxy(self, i) for i in range(hd.attrs['ngalaxies'])
            ]

            self._has_galaxies = True

    def galinfo(self, top=10):
        info_printer(self, 'galaxy', top)

    def haloinfo(self, top=10):
        info_printer(self, 'halo', top)


class Halo:
    def __init__(self, obj, index):
        self.obj = obj
        self._index = index
        self._galaxies = None
        self._satellite_galaxies = None
        self._central_galaxy = None

    def __dir__(self):
        return list(self.obj.halo_data) + list(
            self.obj.halo_dicts) + ['glist', 'slist', 'dmlist', 'bhlist']

    @property
    def glist(self):
        return self.obj.halo_glist[self.glist_start:self.glist_end]

    @property
    def slist(self):
        return self.obj.halo_slist[self.slist_start:self.slist_end]

    @property
    def dmlist(self):
        return self.obj.halo_dmlist[self.dmlist_start:self.dmlist_end]

    @property
    def bhlist(self):
        return self.obj.halo_bhlist[self.bhlist_start:self.bhlist_end]

    @property
    def galaxy_index_list(self):
        return self.obj.galaxy_index_list[self.galaxy_index_list_start:self.
                                          galaxy_index_list_end]

    def _init_galaxies(self):
        self._galaxies = []
        self._satellite_galaxies = []
        for galaxy_index in self.galaxy_index_list:
            galaxy = self.obj.galaxies[galaxy_index]
            self._galaxies.append(galaxy)
            if galaxy.central:
                self._central_galaxy = galaxy
            else:
                self._satellite_galaxies.append(galaxy)

    @property
    def galaxies(self):
        if self._galaxies is None:
            self._init_galaxies()
        return self._galaxies

    @property
    def central_galaxy(self):
        if self._central_galaxy is None:
            self._init_galaxies()
        return self._central_galaxy

    @property
    def satellite_galaxies(self):
        if self._satellite_galaxies is None:
            self._init_galaxies()
        return self._satellite_galaxies

    def __getattr__(self, attr):
        if attr in self.obj.halo_data:
            return self.obj.halo_data[attr][self._index]
        if attr in self.obj.halo_dicts:
            out = {}
            for d in self.obj.halo_dicts[attr]:
                out[d] = self.obj.halo_dicts[attr][d][self._index]
            return out
        raise AttributeError("'{}' object as no attribute '{}'".format(
            self.__class__.__name__, attr))


class Galaxy:
    def __init__(self, obj, index):
        self.obj = obj
        self._index = index
        self.halo = obj.halos[self.parent_halo_index]

    def __dir__(self):
        return list(self.obj.galaxy_data) + list(
            self.obj.galaxy_dicts) + ['glist', 'slist', 'dmlist', 'bhlist']

    @property
    def glist(self):
        return self.obj.galaxy_glist[self.glist_start:self.glist_end]

    @property
    def slist(self):
        return self.obj.galaxy_slist[self.slist_start:self.slist_end]

    @property
    def dmlist(self):
        return self.obj.galaxy_dmlist[self.dmlist_start:self.dmlist_end]

    @property
    def bhlist(self):
        return self.obj.galaxy_bhlist[self.bhlist_start:self.bhlist_end]

    def __getattr__(self, attr):
        if attr in self.obj.galaxy_data:
            return self.obj.galaxy_data[attr][self._index]
        if attr in self.obj.galaxy_dicts:
            out = {}
            for d in self.obj.galaxy_dicts[attr]:
                out[d] = self.obj.galaxy_dicts[attr][d][self._index]
            return out
        raise AttributeError("'{}' object as no attribute '{}'".format(
            self.__class__.__name__, attr))


def quickview(filename):
    obj = CAESAR(filename)
    IPython.embed(header="CAESAR file loaded into the 'obj' variable")

