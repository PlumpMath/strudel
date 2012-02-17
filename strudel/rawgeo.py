#!/usr/bin/ppython
# -*- coding: utf-8 -*-

"""
$File: //user/russell/urth/rawgeo.py $
$Author: russell $
$DateTime: 2011/12/03 12:24:59 $

Copyright (c) 2010-2012 Russell Borogove. All rights reserved.

This is not open source software.

You may inspect and experiment with this software as much as you like.

You may copy small portions ("snippets") of this software into your own 
provided that you fully understand them. You should assume that using any 
of my code without understanding it will reformat your hard disk and seduce
your loved ones.

If I can point out more faults in a copied snippet of my code than you 
can, you are in violation of this license.
"""  

from pandac.PandaModules import Vec3, Vec4, Point3
from pandac.PandaModules import GeomVertexFormat, GeomVertexData
from pandac.PandaModules import Geom, GeomTriangles, GeomVertexWriter
from pandac.PandaModules import GeomNode

# create a vert midway on an edge and pop it out to unit distance
def MidpointVert( verta, vertb ):
    """Given two points/vectors as 3-tuples, return a point midway between them."""
    (ax,ay,az) = verta
    (bx,by,bz) = vertb
    
    return ((ax+bx)*0.5, (ay+by)*0.5, (az+bz)*0.5 )

    
# def Cross( a, b ):
#     """Take normalized cross product of a pair of 3-tuple vectors."""
#     ax, ay, az = a
#     av = Vec3( ax, ay, az )    
#     
#     bx, by, bz = b
#     bv = Vec3( bx, by, bz )  
# 
#     p = av.cross(bv)
#     p.normalize()
#     return (p[0],p[1],p[2])    


class RawGeometry( object ):
    def __init__(self):
        self.verts = []
        self.faces = []
        self.normals = []
     
    def UniformSubdivide( self, midpointdisplace=None ):
        """given triangular faces, subdivide x4"""
        
        def NewVert( a, b, displacecallback=midpointdisplace ):
            if displacecallback:
                return displacecallback( MidpointVert(a,b) )
            else:
                return MidpointVert(a,b)

        new_faces = []
        # create verts at midpoint of each edge
        edge_midpoint_verts = {}
        for (a,b,c) in self.faces:
            # get these into a consistent order for edge naming purposes
            abkey = (a,b) if a < b else (b,a)
            bckey = (b,c) if b < c else (c,b)
            ackey = (a,c) if a < c else (c,a)
            av = self.verts[a]
            bv = self.verts[b]
            cv = self.verts[c]

            if abkey not in edge_midpoint_verts.keys():
                abv = NewVert( av, bv )
                edge_midpoint_verts[abkey] = len(self.verts)
                self.verts.append(abv)

            if bckey not in edge_midpoint_verts.keys():
                bcv = NewVert( bv, cv ) 
                edge_midpoint_verts[bckey] = len(self.verts)
                self.verts.append( bcv )

            if ackey not in edge_midpoint_verts.keys():
                acv = NewVert( av, cv ) 
                edge_midpoint_verts[ackey] = len(self.verts)
                self.verts.append( acv )

            ab = edge_midpoint_verts[abkey]
            bc = edge_midpoint_verts[bckey]
            ac = edge_midpoint_verts[ackey]

            # add the new faces to the new faces list
            new_faces.append( ( a, ab, ac) )
            new_faces.append( (ac, ab, bc) )
            new_faces.append( (ab,  b, bc) )
            new_faces.append( (ac, bc,  c) )

        self.faces = new_faces

