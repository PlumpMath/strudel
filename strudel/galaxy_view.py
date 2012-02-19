from math import log
from panda3d.core import NodePath, Vec4, Point3, GeomVertexData, GeomVertexFormat, GeomVertexWriter, GeomVertexArrayFormat, InternalName, Geom, TransparencyAttrib, GeomPoints, GeomNode, TextureStage, TexGenAttrib, PandaNode, ColorBlendAttrib
from strudel.view import View

class GalaxyView(View):
    def __init__(self, base, obj, **kwargs):
        super(GalaxyView, self).__init__(base, obj, **kwargs)

        array = GeomVertexArrayFormat()
        array.addColumn(InternalName.make('vertex'), 3, Geom.NTFloat32, Geom.CPoint)
        array.addColumn(InternalName.make('color'), 4, Geom.NTFloat32, Geom.CColor)
        array.addColumn(InternalName.make('size'), 1, Geom.NTFloat32, Geom.COther)
        gmformat = GeomVertexFormat()
        gmformat.addArray(array)
        gmformat = GeomVertexFormat.registerFormat(gmformat)

        vdata = GeomVertexData('points', gmformat, Geom.UHDynamic)

        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        size = GeomVertexWriter(vdata, 'size')

        self.node = NodePath('galaxy')
        self.node.reparentTo(self.base.render)
        self.node.setTransparency(TransparencyAttrib.MAlpha)

        lumsort = sorted([star.luminosity for star in self.obj.stars])
        #highest_luminosity = lumsort[-1]
        median_luminosity = lumsort[len(lumsort)/2]
        for star in self.obj.stars:
            vertex.addData3f(star.galpos.x, star.galpos.y, star.galpos.z)
            color.addData4f(star.red, star.green, star.blue, 1.0)
            #size.addData1f(min(100, max(5, 10-star.magnitude/2)))
            sizeval = 10+log(star.luminosity)
            size.addData1f(min(30, max(10, sizeval)))

        prim = GeomPoints(Geom.UHStatic)
        prim.addConsecutiveVertices(0, len(self.obj.stars))
        prim.closePrimitive()

        geom = Geom(vdata)
        geom.addPrimitive(prim)

        node = GeomNode('gnode')
        node.addGeom(geom)

        galaxy_node = self.node.attachNewNode(node)
        galaxy_node.setRenderModeThickness(1)
        ts = TextureStage.getDefault()#TextureStage('ts')
        #ts.setMode(TextureStage.MGlow)
        galaxy_node.setTexGen(ts, TexGenAttrib.MPointSprite)
        galaxy_node.setTexture(ts, self.base.loader.loadTexture('texture/flare.png'))
        #galaxy_node.setRenderModePerspective(True)

        galaxy_node.setBin("unsorted", 1)
        galaxy_node.setDepthWrite(0)
        galaxy_node.setTransparency(1)

        self.setup_glow_shader()

        """
        render.setShaderAuto()
        filters = CommonFilters(base.win, self.cam)
        filters.setBloom(blend=(1, 1, 1, 1), desat=0.2, intensity=1.0, size="large")
        """

    def setup_glow_shader(self):
        glow_shader=self.base.loader.loadShader("shader/glowShader.cg")
        glow_buffer=self.base.win.makeTextureBuffer("Glow scene", 512, 512)
        glow_buffer.setSort(-3)
        glow_buffer.setClearColor(Vec4(0,0,0,1))
        self.glowcam=self.base.makeCamera(glow_buffer, lens=self.base.cam.node().getLens())
        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setShader(glow_shader)
        self.glowcam.node().setInitialState(tempnode.getState())
        self.glowcam.reparentTo(self.base.camera)
        blurXBuffer=self.makeFilterBuffer(glow_buffer,    "Blur X", -2, "shader/XBlurShader.cg")
        blurYBuffer=self.makeFilterBuffer(blurXBuffer, "Blur Y", -1, "shader/YBlurShader.cg")
        self.finalcard = blurYBuffer.getTextureCard()
        self.finalcard.reparentTo(self.base.render2d)
        self.finalcard.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))

        self.base.accept("v", self.base.bufferViewer.toggleEnable)
        self.base.accept("V", self.base.bufferViewer.toggleEnable)
        self.base.bufferViewer.setPosition("llcorner")
        self.base.bufferViewer.setLayout("hline")
        self.base.bufferViewer.setCardSize(0.652,0)

        #render.setShaderAuto()
        #filters = CommonFilters(base.win, self.cam)
        #filters.setBlurSharpen(amount=0.8)

    def makeFilterBuffer(self, srcbuffer, name, sort, prog):
        blur_buffer = self.base.win.makeTextureBuffer(name, 512, 512)
        blur_buffer.setSort(sort)
        blur_buffer.setClearColor(Vec4(1,0,0,1))
        blur_camera = self.base.makeCamera2d(blur_buffer)
        blur_scene = NodePath("new Scene")
        blur_camera.node().setScene(blur_scene)
        shader = self.base.loader.loadShader(prog)
        card = srcbuffer.getTextureCard()
        card.reparentTo(blur_scene)
        card.setShader(shader)
        return blur_buffer

    def remove(self):
        super(GalaxyView, self).remove()
        self.glowcam.removeNode()
