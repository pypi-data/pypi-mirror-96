import numpy as np


def coordinates_to_distancematrix(Coord3D):
    """
    Transform coordinates to distance matrix. Will apply transformation on last dimension.
    Changing of shape (...,N,3) -> (...,N,N)
    
    Arg:
        Coord3D (numpy array):  Coordinates of shape (...,N,3) for cartesian coordinates (x,y,z) 
                                and N the number of atoms or points. Coordinates are last dimension.

    Returns:
        Distance matrix as numpy array with shape (...,N,N) where N is the number of atoms
    """
    shape_3d = len(Coord3D.shape)
    a = np.expand_dims(Coord3D, axis = shape_3d -2)
    b = np.expand_dims(Coord3D, axis = shape_3d -1)
    c = b-a
    d = np.sqrt(np.sum(np.square(c),axis = shape_3d))
    return d


def invert_distance(d,nan=0,posinf=0,neginf=0):
    """
    Invert distance array, e.g. distance matrix. Inversion is done for all entries.
    Keeping of shape (...,) -> (...,)
    
    Args:
        d (numpy array): array of distance values of shape (...,)
        nan (value): replacement for np.nan after division, default = 0
        posinf (value): replacement for np.inf after division, default = 0
        neginf (value): replacement for -np.inf after division, default = 0
        
    Returns:
        Inverted distance array as numpy array of identical shape (...,) and
        replaces np.nan and np.inf with e.g. 0
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        c = np.true_divide(1,d)
        #c[c == np.inf] = 0
        c = np.nan_to_num(c,nan=nan,posinf=posinf,neginf=neginf)
    return c


def distance_to_gaussdistance(Distance, GBins = 20, GRange = 4, GSigma = 0.4):
    """ 
    Convert distance array to smooth one-hot representation using Gaussian functions.
    Changes shape for gaussian distance (...,) -> (...,GBins)
    The Default values match units in Angstroem.
    
    Args:
        Distance (numpy array): Array of distances of shape (...,)
        GBins (int): number of Bins to sample distance from, default = 25
        GRange (value): maximum distance to be captured by bins, default = 5.0
        GSigma (value): sigma of the gaussian function, determining the width/sharpness, default = 0.5
    
    Returns:
        Numpy array of gaussian distance with expanded last axis (...,GBins)
    """
    gamma = 1/GSigma/GSigma*(-1)/2
    d_shape = Distance.shape
    EdgeDistGrid= np.expand_dims(Distance,axis=-1)
    EdgeGausBin = np.arange(0,GBins,1)/GBins*GRange
    EdgeGausBin = np.broadcast_to(EdgeGausBin, np.append(np.ones(len(d_shape),dtype=np.int32),EdgeGausBin.shape)) #shape (1,1,...,GBins)
    EdgeGausBin = np.square(EdgeDistGrid-EdgeGausBin)*gamma # (N,M,...,1) - (1,1,...,GBins)
    EdgeGausBin = np.exp(EdgeGausBin)
    return EdgeGausBin



def get_connectivity_from_inversedistancematrix(invdistmat,protons,radii_dict=None, k1=16.0, k2=4.0/3.0, cutoff=0.85,force_bonds=True): 
    """
    Get connectivity table from inverse distance matrix defined at last dimensions (...,N,N) and corresponding bond-radii. Keeps shape with (...,N,N).
    Covalent radii, from Pyykko and Atsumi, Chem. Eur. J. 15, 2009, 188-197. 
    Values for metals decreased by 10% according to Robert Paton's Sterimol implementation. 
    Partially based on code from Robert Paton's Sterimol script, which based this part on Grimme's D3 code
    
    Args:
        invdistmat (numpy array):   inverse distance matrix defined at last dimensions (...,N,N)
                                    distances must be in Angstroem not in Bohr  
        protons (numpy array):      An array of atomic numbers matching the invdistmat (...,N),
                                    for which the radii are to be computed.
        radii_dict (numpy array):   covalent radii for each element. If default=None, stored values are used. Otherwise array with covalent bonding radii.
                                    example: np.array([0, 0.34, 0.46, 1.2, ...]) from {'H': 0.34, 'He': 0.46, 'Li': 1.2, ...}
        k1 (value):                 default = 16
        k2 (value):                 default = 4.0/3.0
        cutoff (value):             cutoff value to set values to Zero (no bond) default = 0.85
        force_bonds (value):        whether to force at least one bond in the bond table per atom (default = True)
        
    Retruns:
        Connectivity table with 1 for chemical bond and zero otherwise of shape (...,N,N) -> (...,N,N)
    """
    #Dictionary of bond radii    
    proton_raddi_dict = np.array([0, 0.34, 0.46, 1.2, 0.94, 0.77, 0.75, 0.71, 0.63, 0.64, 0.67, 1.4, 1.25, 1.13, 1.04, 1.1, 1.02, 0.99, 0.96, 1.76, 1.54, 1.33, 1.22, 1.21, 1.1, 1.07, 1.04, 1.0, 0.99, 1.01, 1.09, 1.12, 1.09, 1.15, 1.1, 1.14, 1.17, 1.89, 1.67, 1.47, 1.39, 1.32, 1.24, 1.15, 1.13, 1.13, 1.19, 1.15, 1.23, 1.28, 1.26, 1.26, 1.23, 1.32, 1.31, 2.09, 1.76, 1.62, 1.47, 1.58, 1.57, 1.56, 1.55, 1.51, 1.52, 1.51, 1.5, 1.49, 1.49, 1.48, 1.53, 1.46, 1.37, 1.31, 1.23, 1.18, 1.16, 1.11, 1.12, 1.13, 1.32, 1.3, 1.3, 1.36, 1.31, 1.38, 1.42, 2.01, 1.81, 1.67, 1.58, 1.52, 1.53, 1.54, 1.55])
    if(radii_dict== None):
        radii_dict = proton_raddi_dict #index matches atom number
    #Get Radii 
    protons = np.array(protons,dtype=np.int)
    radii = radii_dict[protons]
    # Calculate
    shape_rad = radii.shape
    r1 = np.expand_dims(radii, axis = len(shape_rad)-1)
    r2 = np.expand_dims(radii, axis = len(shape_rad))
    rmat = r1+r2
    rmat = k2*rmat
    rr = rmat*invdistmat
    damp = (1.0+np.exp(-k1*(rr-1.0)))
    damp = 1.0/damp        
    if(force_bonds==True): # Have at least one bond
        maxvals = np.expand_dims(np.argmax(damp,axis=-1),axis=-1)
        np.put_along_axis(damp,maxvals,1,axis=-1)
        #To make it symmetric transpose last two axis
        damp = np.swapaxes(damp,-2,-1)
        np.put_along_axis(damp,maxvals,1,axis=-1)
        damp = np.swapaxes(damp,-2,-1)
    damp[damp<cutoff] = 0
    bond_tab = np.round(damp)          
    return bond_tab


def define_adjacency_from_distance(DistanceMatrix,max_distance=np.inf,max_neighbours=np.inf,exclusive=True,self_loops=False):
    """
    Construct adjacency matrix from a distance matrix by distance and number of neighbours. Works for batches.
    
    This does take into account special bonds (e.g. chemical) just a general distance measure.
    Tries to connect nearest neighbours.

    Args:
        DistanceMatrix (np.array): Distance Matrix of shape (...,N,N)
        max_distance (float, optional): Maximum distance to allow connections, can also be None. Defaults to np.inf.
        max_neighbours (int, optional): Maximum number of neighbours, can also be None. Defaults to np.inf.
        exclusive (bool, optional): Whether both max distance and Neighbours must be fullfileed. Defaults to True.
        self_loops (bool, optional): Allow self-loops on diagonal. Defaults to False.

    Returns:
        tuple: GraphAdjacency,GraphIndices
        
        - GraphAdjacency (np.array): Adjacency Matrix of shape (...,N,N) of dtype=np.bool.
        - GraphIndices (np.array): Flatten indizes from former array that have Adjacency == True.
    """
    DistanceMatrix = np.array(DistanceMatrix)
    NumAtoms = DistanceMatrix.shape[-1]
    if(exclusive==True):
        GraphAdjacency = np.ones_like(DistanceMatrix,dtype = np.bool)
    else:
        GraphAdjacency = np.zeros_like(DistanceMatrix,dtype = np.bool)
    inddiag = np.arange(NumAtoms) 
    #Make Indix Matrix
    indarr = np.indices(DistanceMatrix.shape)
    re_order =np.append (np.arange(1,len(DistanceMatrix.shape)+1),0)
    GraphIndices = indarr.transpose(re_order) 
    #print(GraphIndices.shape)
    #Add Max Radius
    if(max_distance is not None):
        temp = DistanceMatrix < max_distance
        #temp[...,inddiag,inddiag] = False
        if(exclusive==True):
            GraphAdjacency = np.logical_and(GraphAdjacency, temp)
        else:
            GraphAdjacency = np.logical_or(GraphAdjacency, temp)
    # Add #Nieghbours
    if(max_neighbours is not None):
        max_neighbours = min(max_neighbours,NumAtoms)
        SortingIndex = np.argsort(DistanceMatrix,axis=-1)
        #SortedDistance = np.take_along_axis(self.DistanceMatrix, SortingIndex, axis=-1)
        ind_sorted_red = SortingIndex[...,:max_neighbours+1]
        temp = np.zeros_like(DistanceMatrix,dtype = np.bool)
        np.put_along_axis(temp,ind_sorted_red, True,axis=-1)
        if(exclusive==True):
            GraphAdjacency = np.logical_and(GraphAdjacency, temp)
        else:
            GraphAdjacency = np.logical_or(GraphAdjacency, temp)
    # Allow self-loops
    if(self_loops == False):
        GraphAdjacency[...,inddiag,inddiag] = False

    GraphIndices = GraphIndices[GraphAdjacency]
    return GraphAdjacency,GraphIndices

