import bpy
import bmesh

# TODO: INSERT TYPES EVERYWHERE WHERE POSSIBLE!!!


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
    translate_factor = 1
    # first extrusion
    bmesh.ops.extrude_face_region(bm, geom=face)
    bm.verts.ensure_lookup_table()
    for i in range(20, 24):
        bm.verts[i].co += bm.verts[i].normal * translate_factor
    bmesh.ops.delete(bm, geom=face, context ='FACES_ONLY')
    # second extrusion
    bm.faces.ensure_lookup_table()
    face = [bm.faces[17]]
    bmesh.ops.extrude_face_region(bm, geom=face)
    bm.verts.ensure_lookup_table()
    for i in range(24, 28):
        bm.verts[i].co += bm.verts[i].normal * translate_factor
    bmesh.ops.delete(bm, geom=face, context ='FACES_ONLY')

    """ STEP 5 : THICKEN STEM BASE """
    scale_factor = 2
    bm.verts.ensure_lookup_table()
    for i in range(24, 28):
        bm.verts[i].co.x *= scale_factor
        bm.verts[i].co.y *= scale_factor
        
    """ STEP 6 : CREATE STEM MATERIAL """
    stem_material = bpy.data.materials.new(name="toadstool_stem")
    stem_material.diffuse_color = (1, 0.847914, 0.631299, 1)
    obj.data.materials.append(stem_material)
    # assign material to stem faces
    bm.faces.ensure_lookup_table()
    bm.faces[10].material_index = 0
    for i in range(18, 26):
        bm.faces[i].material_index = 0
        
    """ STEP 7 : CREATE CAP MATERIAL """
    cap_material = bpy.data.materials.new(name="toadstool_cap")
    # enable nodes
    cap_material.use_nodes = True
    nodes_cap = cap_material.node_tree.nodes
    # create all nodes
    node_coords = nodes_cap.new("ShaderNodeTexCoord")
    node_mapping = nodes_cap.new("ShaderNodeMapping")
    node_dots = nodes_cap.new("ShaderNodeTexVoronoi")
    node_math = nodes_cap.new("ShaderNodeMath")
    node_math.operation = 'LESS_THAN'
    node_colors = nodes_cap.new("ShaderNodeValToRGB")
    # set nodes' values
    node_colors.color_ramp.elements[0].color = (1,0,0,1)
    # connect nodes
    cap_material.node_tree.links.new(node_coords.outputs[3], node_mapping.inputs[0])
    cap_material.node_tree.links.new(node_mapping.outputs[0], node_dots.inputs[0])
    cap_material.node_tree.links.new(node_dots.outputs[0], node_math.inputs[0])
    cap_material.node_tree.links.new(node_math.outputs[0], node_colors.inputs[0])
    cap_material.node_tree.links.new(node_colors.outputs[0], nodes_cap["Principled BSDF"].inputs[0])
    
    
    cap_material.diffuse_color = (1, 0, 0, 1)
    obj.data.materials.append(cap_material)
    # assign material to cap faces
    bm.faces.ensure_lookup_table()
    for i in range(0, 10):
        bm.faces[i].material_index = 1
    for i in range(11, 18):
        bm.faces[i].material_index = 1
    
    """ STEP X : PLACE TOADSTOOL SOMEWHERE IN SCENE """
    
    """ DONE """

    obj.data.update()
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


init()
main()