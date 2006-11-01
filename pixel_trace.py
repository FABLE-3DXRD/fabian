# pixel_trace is based on td_dda.py - Three-Dimensional Digital Differential Analyser
# Algorithm for traverse voxels with a ray defined by two coordinate sets
# and calculated the path lenght of the ray in every traversed voxel. 
# Finally the intensity along the ray is integrated.
#
# (int_along_ray, voxels) = td_tdd(start_point,end_point)
#
# start_point = [x1 y1]
# end_point = [x2 y2]
#
# Example:
# pixel_trace([0.5, 0.5],[2.5, 5.5])
#
# This function is largely following the algorithm:
# "A Fast Traversal Algorithm" by John Amanatides,
# Proc. Eurographics '87, Amsterdam, The Netherlands, August 1987, pp 1-10.
#
# Henning Osholm Sorensen, Risoe National Lab., Nov 1, 2006.

from  Numeric import *
import copy

def pixel_trace(corners):

    # Initialize variables
    p_start = array([corners[0], corners[1]],Float)
    p_end = array([corners[2], corners[3]],Float)
    zero = 1e-09
    final_out = False
    t_total = 0
    nr_voxels = 0
    nextpix = zeros(2,Int)
    delta = ones(2,Int)
    t = zeros(2,Float)
    t_one = zeros(2,Float)
    #voxel=zeros((product(gridsize),3))
    voxel = []

    # the ray is defined r0 + t *r
    r0 = p_start
    r = p_end-r0
    t_max = sqrt(sum(r*r)) # Maximum ray path lenght in normalized coordinate system
    r = r/t_max

    startpix = floor(r0)+1  #The pixel where the ray originates
    # Set step size and direction in x,y,z
    # find first intersection with voxel border
    for i in range(2):
        if r[i] == 0:
            t_one[i] = float('Inf') # Determine paths for stepping 1 in x,y,z respectively.
            t[i] =  float('Inf')    # Maybe add a check for r(i) = 0 not to divide by zero
        else:
            t_one[i] = abs(1/r[i])  # Determine paths for stepping 1 in x,y,z respectively.
            if r[i] > 0:
                t[i] = (floor(r0[i])+1-r0[i])/r[i]
            else:
                delta[i] = -1
                t[i] = (floor(r0[i])-r0[i])/r[i]

    # Find which voxel border is intersected next
    while t_total < t_max-zero: # to make sure that an extra step is not taken if t_total essitianlly equals t_max
        t_old =t
        if t[0] < t[1]:
            #print "%i : x<y, " %nr_voxels
            pix = copy.copy(nextpix)
            nextpix[0] = nextpix[0] + delta[0]
            t_voxel = t[0] - t_total
            t_total = t[0]
            t[0] = t[0] + t_one[0]
        else:
            #print "%i : y<x" %nr_voxels
            pix = copy.copy(nextpix)
            nextpix[1] = nextpix[1] + delta[1]
            t_voxel = t[1] - t_total
            t_total = t[1]
            t[1] = t[1] + t_one[1]
        # Do not output if t_voxel is zero
        if t_voxel > zero:
            pix = pix + startpix
            nr_voxels = nr_voxels + 1
            voxel.append([pix[0],pix[1],t_voxel])


    # Correct t_voxel of the last voxel if overshot
    if final_out == False: voxel[nr_voxels-1][2] = voxel[nr_voxels-1][2]-(t_total-t_max)
    
    voxel = array(voxel)
        
    # Integrate intensity along ray
    return voxel

if __name__=='__main__':
    start = [3.6 , 2]
    end = [11, 12]
    pixlist = pixel_trace(start,end)

    #print int
    print pixlist
