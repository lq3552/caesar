import h5py
import numpy as np

from .group import Halo, Galaxy
from .saver import blacklist

from yt.extern import six
from yt.units.yt_array import YTQuantity, YTArray, UnitRegistry

######################################################################

def restore_single_list(obj, group, key):
    infile = h5py.File(obj.data_file,'r')
    data   = np.array(infile['%s_data/lists/%s' % (group.obj_type, key)])
    infile.close()
    start  = getattr(group, '%s_start' % key)
    end    = getattr(group, '%s_end'   % key)
    setattr(group, key, data[start:end])    

######################################################################

def get_unit_quant(v, data):
    unit  = None
    quant = True
    if 'unit' in v.attrs:
        unit = v.attrs['unit'].decode('utf8')
        if len(np.shape(data)) > 1:
            quant = False
    return unit, quant
                
######################################################################

def restore_global_attributes(obj, hd):
    for k,v in six.iteritems(hd.attrs):
        if k in blacklist: continue
        setattr(obj, k, v)

    if 'global_attribute_units' in hd:
        uhd = hd['global_attribute_units']
        for k,v in six.iteritems(uhd.attrs):
            setattr(obj, k, YTQuantity(getattr(obj, k), v, registry=obj.unit_registry))

######################################################################            
            
def restore_object_list(obj_list, key, hd):
    if ('lists/%s' % key) not in hd: return
    if key in blacklist: return    
    data = np.array(hd['lists/%s' % key])
    for i in obj_list:
        start = getattr(i, '%s_start' % key)
        end   = getattr(i, '%s_end'   % key)
        setattr(i, key, data[start:end])
        #delattr(i, '%s_start' % key)
        #delattr(i, '%s_end'   % key)

######################################################################                    
        
def restore_object_dicts(obj_list, hd, unit_reg):
    if 'dicts' not in hd: return
    hdd = hd['dicts']
    for k,v in six.iteritems(hdd):
        data = np.array(v)

        unit, use_quant = get_unit_quant(v, data)               
        
        dict_name, dict_key = k.split('.')
        if dict_key in blacklist: continue
        for i in range(0,len(obj_list)):
            if not hasattr(obj_list[i], dict_name):
                setattr(obj_list[i], dict_name, {})
            cur_dict = getattr(obj_list[i], dict_name)

            if unit is not None:
                if use_quant:
                    cur_dict[dict_key] = YTQuantity(data[i], unit, registry=unit_reg)
                else:
                    cur_dict[dict_key] = YTArray(data[i], unit, registry=unit_reg)
            else:
                cur_dict[dict_key] = data[i]
            setattr(obj_list[i], dict_name, cur_dict)
            
######################################################################

def restore_object_attributes(obj_list, hd, unit_reg):
    for k,v in six.iteritems(hd):
        if k in blacklist: continue
        if k == 'lists' or k == 'dicts': continue
        data = np.array(v)

        unit, use_quant = get_unit_quant(v, data)
            
        for i in range(0,len(obj_list)):
            if unit is not None:
                if use_quant:
                    setattr(obj_list[i], k, YTQuantity(data[i], unit, registry=unit_reg))
                else:
                    setattr(obj_list[i], k, YTArray(data[i], unit, registry=unit_reg))
            else:
                setattr(obj_list[i], k, data[i])

######################################################################        

def load(filename, ds = None, obj = None):
    try:
        infile = h5py.File(filename, 'r')
    except IOError:
        raise

    if obj is None:
        import os
        from .main import CAESAR
        obj = CAESAR()
        obj.data_file = os.path.abspath(filename)

    unit_registry_json = infile.attrs['unit_registry_json']
    obj.unit_registry  = UnitRegistry.from_json(unit_registry_json.decode('utf8'))
    
    restore_global_attributes(obj, infile)
    obj.simulation._unpack(obj, infile)
    
    # restore halo data
    if 'halo_data' in infile:
        hd = infile['halo_data']
        obj.halos = []
        for i in range(0,obj.nhalos):
            obj.halos.append(Halo(obj))
        restore_object_attributes(obj.halos, hd, obj.unit_registry)
        restore_object_dicts(obj.halos, hd, obj.unit_registry)
        restore_object_list(obj.halos, 'galaxy_index_list', hd)

        # optional
        for vals in ['dmlist', 'glist', 'slist']:
            restore_object_list(obj.halos, vals, hd)
   
    # restore galaxy data
    if 'galaxy_data' in infile:
        hd = infile['galaxy_data']
        obj.galaxies = []
        for i in range(0,obj.ngalaxies):
            obj.galaxies.append(Galaxy(obj))
        restore_object_attributes(obj.galaxies, hd, obj.unit_registry)
        restore_object_dicts(obj.galaxies, hd, obj.unit_registry)

        # optional
        for vals in ['glist', 'slist']:
            restore_object_list(obj.galaxies, vals, hd)

    infile.close()
            
    obj._link_objects()

    if ds is not None:
        obj.yt_dataset = ds

    return obj