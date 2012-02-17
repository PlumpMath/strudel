#!/usr/bin/ppython
# -*- coding: utf-8 -*-

"""
$File: //user/russell/urth/spheregeo.py $
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
from rawgeo import MidpointVert, RawGeometry

import math

    
def NormalizeVert( vert ):
    """Normalize a 3-tuple."""
    mx, my, mz = vert
    m = Vec3( mx, my, mz )
    m.normalize()
    return (m[0], m[1], m[2]) 
            
def Octahedron():
    """Generate an octahedron as a Geometry object."""
    oct = RawGeometry()
        
    
    E = 1e-6
    E = 0
    
    # we have to double the X = 0, Z = -1 point 
    # so that we can wrap the texture nicely - otherwise
    # there's shared vertices and a flyback.
    oct.verts.append( (E,E,1) )
    oct.verts.append( (E,1,E) )
    oct.verts.append( (1,E,E) )
    oct.verts.append( (E,E,-1) )
    oct.verts.append( (E,-1,E) )
    oct.verts.append( (-1,E,E) )
    oct.verts.append( (E,E,-1) )

    # so the 1-3-5 face becomes 1-6-5
    # and the 3-4-5 face becomes 6-4-5
    oct.faces.append( (0,2,1) )
    oct.faces.append( (0,1,5) )
    oct.faces.append( (0,4,2) )
    oct.faces.append( (0,5,4) )
    oct.faces.append( (1,2,3) )
    oct.faces.append( (1,6,5) )
    oct.faces.append( (2,4,3) )
    oct.faces.append( (6,4,5) )
    
    return oct
                 
# technically an ellipsoid
class SphereNode( GeomNode ):
    def __init__(self,subdivides=3,scale=1.0):
        super(SphereNode,self).__init__('sphere')
        uniform = True
        # see if scale is a tuple
        try:
            xs,ys,zs = scale
            uniform = False
        except TypeError:
            # no, it's a scalar
            xs,ys,zs = scale,scale,scale
               
        north = (0.0,1.0,0.0)
        g = Octahedron()
        
        for i in range(subdivides):
            g.UniformSubdivide( midpointdisplace = NormalizeVert )
            
        #print "%d faces per sphere"%len(g.faces)
        
        # okay, we're gonna use setShaderInput to set constants for 
        # surface coverages and planetary seed, so all we need per 
        # vertex is position and normal
        # and we kind of don't need normal for a unit sphere, but 
        # we want to use the same shader for other thangs
        format=GeomVertexFormat.getV3n3()
        vdata=GeomVertexData('sphere', format, Geom.UHDynamic)

        vertex=GeomVertexWriter(vdata, 'vertex')
        normal=GeomVertexWriter(vdata, 'normal')


        for (x,y,z) in g.verts:
            vertex.addData3f( x*xs, y*ys, z*zs )
            if uniform:            
                normal.addData3f( x, y, z )
            else:
                n = NormalizeVert( (x/(xs*xs),y/(ys*ys),z/(zs*zs)) )
                normal.addData3f( n[0], n[1], n[2] )  
            
        trilist=GeomTriangles(Geom.UHDynamic)
        
        for (a,b,c) in g.faces:
            trilist.addVertex(a)
            trilist.addVertex(b)
            trilist.addVertex(c)
        
        trilist.closePrimitive()
        self.geom = Geom(vdata)
        self.geom.addPrimitive( trilist )
        
        self.addGeom( self.geom )

class RingNode( GeomNode ):
    def __init__(self,inner,outer,sectors):
        super(RingNode,self).__init__('ring')
        self.inner = inner
        self.outer = outer
        self.sectors = sectors
        
        ringgeo = RawGeometry()
        
        # inner and outer radii are the true circular limits, so expand a little bit 
        # for the sectored mesh
        mesh_inner = self.inner * 0.9
        mesh_outer = self.outer * 1.1
        
        angular_width = 2.0 * math.pi / self.sectors
        for sector in range( self.sectors ):
            start = sector * angular_width
            end = (sector+1) * angular_width
            # add a quad
            x0 = math.sin(start) * mesh_inner
            x1 = math.sin(start) * mesh_outer
            x2 = math.sin(end  ) * mesh_inner
            x3 = math.sin(end  ) * mesh_outer
            
            z0 = math.cos(start) * mesh_inner
            z1 = math.cos(start) * mesh_outer
            z2 = math.cos(end  ) * mesh_inner
            z3 = math.cos(end  ) * mesh_outer
            
            index = len(ringgeo.verts)
            ringgeo.verts.append( (x0, 0, z0) )
            ringgeo.verts.append( (x1, 0, z1) )
            ringgeo.verts.append( (x2, 0, z2) )
            ringgeo.verts.append( (x3, 0, z3) )
            
            # double-side the faces so they render from either side
            # top pair...
            ringgeo.faces.append( (index+0,index+1,index+2) )
            ringgeo.faces.append( (index+1,index+3,index+2) )
            # bottom pair...
            ringgeo.faces.append( (index+0,index+2,index+1) )
            ringgeo.faces.append( (index+1,index+2,index+3) )
            
        format=GeomVertexFormat.getV3n3()
        vdata=GeomVertexData('ring', format, Geom.UHDynamic)

        vertex=GeomVertexWriter(vdata, 'vertex')
        normal=GeomVertexWriter(vdata, 'normal')


        for (x,y,z) in ringgeo.verts:
            vertex.addData3f( x, y, z )
            normal.addData3f( 0, 1, 0 )
            
        trilist=GeomTriangles(Geom.UHDynamic)
        
        for (a,b,c) in ringgeo.faces:
            trilist.addVertex(a)
            trilist.addVertex(b)
            trilist.addVertex(c)
        
        trilist.closePrimitive()
        ring = Geom(vdata)
        ring.addPrimitive( trilist )
        
        self.addGeom( ring )

            
            
        
        
        
    