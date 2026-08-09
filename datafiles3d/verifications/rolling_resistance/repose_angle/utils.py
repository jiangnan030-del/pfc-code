import itasca
from itasca import ballarray as ba
import numpy as np
from scipy.spatial.kdtree import KDTree
from scipy import optimize 
from scipy import stats 
import os

def cone_eq(data,a,b):
   return a*(1-np.sqrt(data[:,0]**2+data[:,1]**2)/
                      (a*np.tan((90.0-b)*np.pi/180.0)))

def locally_extreme_points(coords, data, neighbourhood, 
                           lookfor = 'max', p_norm = 2.):
    '''
    Find local maxima of points in a pointcloud.  
    Ties result in both points passing through the filter.

    Not to be used for high-dimensional data.  It will be slow.

    coords: A shape (n_points, n_dims) array of point locations
    data: A shape (n_points, ) vector of point values
    neighbourhood: The (scalar) size of the neighbourhood in which to search.
    lookfor: Either 'max', or 'min', depending on whether you 
             want local maxima or minima
    p_norm: The p-norm to use for measuring distance 
            (e.g. 1=Manhattan, 2=Euclidian)

    returns
        filtered_coords: The coordinates of locally extreme points
        filtered_data: The values of these points
    '''
    assert coords.shape[0] == data.shape[0], \
        'You must have one coordinate per data point'
    extreme_fcn = {'min': np.min, 'max': np.max}[lookfor]
    kdtree = KDTree(coords)
    neighbours = kdtree.query_ball_tree(kdtree, 
                                        r=neighbourhood, p = p_norm)
    i_am_extreme = [data[i]==extreme_fcn(data[n]) 
                        for i, n in enumerate(neighbours)]
    extrema, = np.nonzero(i_am_extreme) # This line just saves time on indexing
    return extrema,coords[extrema], data[extrema]

def fit_cone(fname):
    '''
    Fit a cone

    fname: A save file name

    returns
        t_fit: The repose angle
        ci:    The student-t 95% confidence interval
    '''
    itasca.command("""
                   model restore \'{}\'
                   """.format(fname)
                  )
    bname = os.path.splitext(fname)[0]
    sname = bname + '-ps.p3sav'
    
    positions = ba.pos()
    radii = ba.radius() 
    
    rmin= np.amin(ba.radius())
    rmax= np.amax(ba.radius())
    ravg= 0.5*(rmin+rmax) 
    x,y,z = positions.T
    zmax = z + radii
    coords = np.vstack((x, y)).T
    
    extrema, newcoords,val = locally_extreme_points(coords, z, 
                                                    2.0*ravg, 
                                                    lookfor = 'max', 
                                                    p_norm = 2.)
    
    damp = ba.damp()
    damp[extrema] = 1
    ba.set_damp(damp)
    
    xc = x[extrema]
    yc = y[extrema]
    zc = zmax[extrema]
    
    # Fit a cone on the local extrema. 
    # Use scipy.optimize.curve_fit to estimate the confidence interval
    cC = np.amax(zc)
    mask_up = (cC - 2.0*rmax) > zc 
    mask_lo =  zc > (2.0*rmax)
    xm = xc[mask_up & mask_lo]
    ym = yc[mask_up & mask_lo]
    zm = zc[mask_up & mask_lo]
    data = np.vstack((xm, ym)).T   

    p0 = [cC,40.0] # initial guess for optimization
    params, pcov = optimize.curve_fit(cone_eq, data, zm, p0)
    
    # student-t value for the dof and confidence level
    n = len(zm)         # number of data points
    p = len(params)     # number of parameters
    dof = max(0, n - p) # number of degrees of freedom
    alpha = 0.05        # 95% confidence interval = 100*(1-alpha)
    tval = stats.distributions.t.ppf(1.0-alpha/2., dof) 
    
    ci = []
    for i, p,var in zip(range(n), params, np.diag(pcov)):
        sigma = var**0.5
        ci.append(sigma*tval)
        print('p{0}: {1} [{2}  {3}]'.format(i, p,
                                      p - sigma*tval,
                                      p + sigma*tval))
    
    c_fit, t_fit = params 
    R_fit = c_fit*np.tan((90.0-t_fit)*np.pi/180.0)
    
    itasca.command(
                    """
                      ball group \'mask\' range position-z {zmin} {zmax} not
                      [repose_angle = {ra}]
                      geometry generate cone base (0,0,0) ...
                                             axis (0,0,1) ...
                                             height {c}   ...
                                             radius {r}   ...
                                             cap false
                      model save \'{s}\'
                    """.format(ra=t_fit,c=c_fit,r=R_fit,
                               zmin = 2.0*rmax,
                               zmax = (cC - 2.0*rmax),s=sname)
                  )
    return [t_fit,ci[1]]
    