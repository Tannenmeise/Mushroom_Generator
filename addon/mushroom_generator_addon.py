import bpy
import bmesh
import random

# TODO: INSERT TYPES EVERYWHERE WHERE POSSIBLE!!!???


bl_info = {
    "name": "Mushroom Generator",
    "description": "Generate a delightful amount of likable mushrooms",
    "author": "Tamara Hezel",
    "version": (1, 0, 0),
    "blender": (3, 10, 0),
    "location": "View3D > Add > Mesh",
    "doc_url": "https://github.com/Tannenmeise/Mushroom_Generator",
    "tracker_url": "https://github.com/Tannenmeise/Mushroom_Generator/issues",
    "category": "Add Mesh"
}


class MUSHROOMGENERATOR_OT_add_mushroom(bpy.types.Operator):
    bl_idname = "mushroomgenerator.add_mushroom"
    bl_label = "Mushroom"
    bl_description = "Add a randomly generated mushroom"
    bl_options = {"REGISTER", "UNDO"}
    
    SPECIES: bpy.props.EnumProperty(
        name="Species",
        description="Select a mushroom species",
        items= [('SP1', "Boletus", ""),
                ('SP2', "Crested Inkling", ""),
                ('SP3', "Drab Bonnet", ""),
                ('SP4', "Toadstool", "")
        ]
    )
    SEED: bpy.props.IntProperty(name="Seed")
    
    
    def generate_mushroom(self) -> bpy.types.Object:
        # create (empty) mesh
        mushroom_mesh = bpy.data.meshes.new('Mushroom')
        # create object
        mushroom_object = bpy.data.objects.new("Mushroom", mushroom_mesh)
        # add object to a collection
        bpy.context.collection.objects.link(mushroom_object)

        # create a new bmesh
        bm = bmesh.new()
        # create a bmesh cube
        bmesh.ops.create_cube(bm, size=1.0)
        # assign bmesh to the blender mesh
        bm.to_mesh(mushroom_mesh)

        # set the object to active in the 3d viewer
        bpy.context.view_layer.objects.active = bpy.data.objects['Mushroom']
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
        random_stem_thickness = random.uniform(0.1, 0.3)
        #random_stem_thickness = 0.2
        bm.faces.ensure_lookup_table()
        face = [bm.faces[9]]
        bmesh.ops.inset_region(bm, faces=face, thickness=random_stem_thickness, depth=0)
        
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
        scale_factor = 1.5
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
        # voronoi node
        node_dots.inputs[2].default_value = 60 # scale
        random_randomness_value = random.uniform(0.5, 1)
        node_dots.inputs[5].default_value = random_randomness_value # randomness
        # less than node
        random_threshold_value = random.uniform(0.2, 0.45)
        node_math.inputs[1].default_value = random_threshold_value # threshold
        # color ramp node
        random_color_value_r = random.uniform(1, 1)
        random_color_value_g = random.uniform(0, 0.05)
        random_color_value_b = random.uniform(0, 0.)
        node_colors.color_ramp.elements[0].color = (random_color_value_r,random_color_value_g,random_color_value_b,1)
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
            
        """ STEP 8 : CHANGE CAP HEIGHT """
        random_translate_factor = random.uniform(0.1, 1)
        #random_translate_factor = 1
        bm.verts.ensure_lookup_table()
        for i in range(0, 7, 2):
            bm.verts[i].co.z *= random_translate_factor
        for i in range(8, 12):
            bm.verts[i].co.z *= random_translate_factor
        
        """STEP 9 : CHANGE CAP WIDTH """
        random_scale_factor = random.uniform(0.9, 2.5)
        #random_scale_factor = 1
        bm.verts.ensure_lookup_table()
        for i in range(0, 7, 2):
            bm.verts[i].co.x *= random_scale_factor
            bm.verts[i].co.y *= random_scale_factor
        for i in range(8, 12):
            bm.verts[i].co.x *= random_scale_factor
            bm.verts[i].co.y *= random_scale_factor
            
        """ STEP 9 : OVERALL SCALING """
        # scale all vectors to make an overall smaller or bigger mushroom
        # realistic size (1 = 1m): mushroom 10cm to 20cm
        random_scale_factor = random.uniform(0.045, 0.09)
        #random_scale_factor = 0.09
        bm.verts.ensure_lookup_table()
        for vert in bm.verts:
            vert.co.x *= random_scale_factor
            vert.co.y *= random_scale_factor
            vert.co.z *= random_scale_factor
        
        """ DONE """

        obj.data.update()
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
        
        return mushroom_object
    
    
    def generate_boletus(self) -> bpy.types.Object:
        boletus: bpy.types.Object = self.generate_mushroom()
        
        return boletus
    
    
    def generate_crested_inkling(self) -> bpy.types.Object:
        crested_inkling: bpy.types.Object = self.generate_mushroom()
        
        return crested_inkling
        
        
    def generate_drab_bonnet(self) -> bpy.types.Object:
        drab_bonnet: bpy.types.Object = self.generate_mushroom()
        
        return drab_bonnet
    
    
    def generate_toadstool(self) -> bpy.types.Object:
        toadstool: bpy.types.Object = self.generate_mushroom()
        
        return toadstool
        
    
    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        random.seed(self.SEED)
        mushroom_collection: bpy.types.Collection
        
        if "Mushroom" in bpy.data.collections:
            mushroom_collection = bpy.data.collections["Mushroom"]
        else:
            mushroom_collection = bpy.data.collections.new("Mushroom")
         
        try:
            bpy.context.scene.collection.children.link(mushroom_collection)
        except:
            ... # collction already linked
            
            
        if self.SPECIES == 'SP1':
            boletus_mushroom: bpy.types.Object = self.generate_boletus()
            mushroom_collection.objects.link(boletus_mushroom)
            bpy.context.object.name = "Boletus"
            
        elif self.SPECIES == 'SP2':
            crested_inkling_mushroom: bpy.types.Object = self.generate_crested_inkling()
            mushroom_collection.objects.link(crested_inkling_mushroom)
            bpy.context.object.name = "Crested Inkling"
        
        elif self.SPECIES == 'SP3':
            drab_bonnet_mushroom: bpy.types.Object = self.generate_drab_bonnet()
            mushroom_collection.objects.link(drab_bonnet_mushroom)
            bpy.context.object.name = "Drab Bonnet"
            
        elif self.SPECIES == 'SP4':
            toadstool_mushroom: bpy.types.Object = self.generate_toadstool()
            mushroom_collection.objects.link(toadstool_mushroom)
            bpy.context.object.name = "Toadstool"
        

        return {"FINISHED"}


def menu_func(self, context):
    self.layout.operator(MUSHROOMGENERATOR_OT_add_mushroom.bl_idname, icon='LIGHT_HEMI')

def register():
    bpy.utils.register_class(MUSHROOMGENERATOR_OT_add_mushroom)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

def unregister():
    bpy.utils.unregister_class(MUSHROOMGENERATOR_OT_add_mushroom)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

    
