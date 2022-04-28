import bpy
import bmesh


def init():
    # toggle to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # delete everything
    bpy.ops.object.select_all(action='SELECT') # selektiert alle Objekte
    bpy.ops.object.delete(use_global=False, confirm=False) # löscht selektierte objekte
    bpy.ops.outliner.orphans_purge() # löscht überbleibende Meshdaten etc.


def main():
    create_toadstool()
    

def create_toadstool():
    # create (empty) mesh
    toadstool_mesh = bpy.data.meshes.new('Toadstool')
    # create object
    toadstool_object = bpy.data.objects.new("Toadstool", toadstool_mesh)
    # add object to a collection
    bpy.context.collection.objects.link(toadstool_object)

    # create a new bmesh
    bm = bmesh.new()
    # create a bmesh cube
    bmesh.ops.create_cube(bm, size=1.0)
    # assign bmesh to the blender mesh
    bm.to_mesh(toadstool_mesh)

    # set the object to active in the 3d viewer
    bpy.context.view_layer.objects.active = bpy.data.objects['Toadstool']
    # get active object
    obj = bpy.context.active_object


    # add a subdivision surface modifier to the cube
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels = 4
    bpy.context.object.modifiers["Subdivision"].render_levels = 4

    """ STEP 1 : INSET CAP """
    # needed to get "bm.faces[i]"
    bm.faces.ensure_lookup_table()
    # get the face
    face = [bm.faces[4]]
    # inset the bottom face
    bmesh.ops.inset_region(bm, faces=face, thickness=0.25, depth=0)

    """ STEP 2 : EXTRUDE CAP """
    # extrude (creates new geometry)
    bmesh.ops.extrude_face_region(bm, geom=face)
    # needed to get the updated "bm.verts[i]"
    bm.verts.ensure_lookup_table()
    # loop through all vertices that need to be translated
    for i in range(12, 16):
        # translate vertex
        bm.verts[i].co += bm.verts[i].normal * -0.8
    # remove the leftover face (= face)
    bmesh.ops.delete(bm, geom=face, context ='FACES_ONLY')
    
    """ STEP 3 : INSET STEM """
    bm.faces.ensure_lookup_table()
    face = [bm.faces[9]]
    bmesh.ops.inset_region(bm, faces=face, thickness=0.25, depth=0)
    
    """ STEP 4 : EXTRUDE STEM """
    bmesh.ops.extrude_face_region(bm, geom=face)
    bm.verts.ensure_lookup_table()
    for i in range(20, 24):
        bm.verts[i].co += bm.verts[i].normal * 2
    bmesh.ops.delete(bm, geom=face, context ='FACES_ONLY')
    

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    

init()
main()