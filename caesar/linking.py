import numpy as np

from yt.funcs import mylog

def link_galaxies_and_halos(obj):
    """Link galaxies and halos to one another.

    This function creates the links between galaxy-->halo and
    halo-->galaxy objects.  Is run during creation, and loading in of
    each CAESAR file.

    Parameters
    ----------
    obj : :class:`main.CAESAR`
        Object containing halos and galaxies lists.

    """
    if not obj._has_galaxies:
        return

    mylog.info('Linking galaxies and halos')
    
    # halos
    for halo in obj.halos:
        halo.galaxies = []
        for galaxy_index in halo.galaxy_index_list:
            halo.galaxies.append(obj.galaxies[galaxy_index])
    
    # galaxies
    for galaxy in obj.galaxies:
        if galaxy.parent_halo_index > -1:
            galaxy.halo = obj.halos[galaxy.parent_halo_index]
        else:
            galaxy.halo = None



def link_clouds_and_galaxies(obj):
    """Link clouds and galaxies to one another.
    
    This function creates the links between cloud-->galaxy and
    galaxy-->cloud objects.  Is run during creation, and loading in of
    each CAESAR file.
    
    Parameters
    ----------
    obj : :class:`main.CAESAR`
        Object containing halos and galaxies lists.
    
    """
    
    if not obj._has_clouds:
        return
  
    mylog.info('Linking clouds and galaxies')

    #galaxies
    for galaxy in obj.galaxies:
        galaxy.clouds = []
        for cloud_index in galaxy.cloud_index_list:
            galaxy.clouds.append(obj.clouds[cloud_index])
    
    for cloud in obj.clouds:
        if cloud.parent_galaxy_index > -1:
            cloud.galaxy = obj.galaxies[cloud.parent_galaxy_index]
        else:
            cloud.galaxy = None

  
def create_sublists(obj):
    """Create sublists of objects.

    Will create the sublists:
        - central_galaxies
        - satellite_galaxies
        - unassigned_galaxies (those without a halo)

    Parameters
    ----------
    obj : :class:`main.CAESAR`
        Object containing halos and galaxies lists already linked.

    """
    if not obj._has_galaxies:
        return

    mylog.info('Creating sublists')
    
    obj.central_galaxies   = []
    obj.satellite_galaxies = []
    
    # assign halo sub lists
    for halo in obj.halos:
        halo.central_galaxy = -1
        for galaxy in halo.galaxies:
            if galaxy.central:
                halo.central_galaxy = galaxy.GroupID
#             else:
#                 halo.satellite_galaxies.append(galaxy)

    # assign galaxy sub lists
    for galaxy in obj.galaxies:
        if galaxy.central and galaxy.halo is not None:
#             galaxy.satellites = galaxy.halo.satellite_galaxies
            obj.central_galaxies.append(galaxy)
        elif galaxy.halo is not None:
#             galaxy.satellites = []
            obj.satellite_galaxies.append(galaxy)
        else:
            if not hasattr(obj, 'unassigned_galaxies'):
                obj.unassigned_galaxies = []
            obj.unassigned_galaxies.append(galaxy)
            
