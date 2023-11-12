import bpy
import os

dir_path = os.path.dirname(__file__)


class QNAL_OT_PlaneQuadMaskAdd(bpy.types.Operator):
    bl_idname = "qnal.plane_quad_mask_add"
    bl_label = "Add quad mask"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ao = context.active_object is not None
        am = context.active_object.active_material is not None
        is_mesh = context.active_object.type == "MESH"
        it = None
        if am:
            it = "Image Texture" in context.active_object.active_material.node_tree.nodes
        return ao and am and is_mesh and it

    def execute(self, context):
        # dir_path = "/home/user/git/qnal_blender_addon/"  # TODO
        for file in os.listdir(dir_path):
            if file.endswith(".blend"):
                filepath = os.path.join(dir_path, file)
                break
        else:
            raise FileNotFoundError("No .blend File in directory " + dir_path)

        # create quad mask child object
        image_object = context.active_object
        verts = [
            (-1, -1, 0),
            (1, -1, 0),
            (-1, 1, 0),
            (1, 1, 0),
        ]
        edges = [(0, 1), (1, 3), (3, 2), (2, 0)]

        mesh = bpy.data.meshes.new("quad_mask.000")
        mesh.from_pydata(verts, edges, [])
        mesh.update()

        from bpy_extras import object_utils
        highlight_object = object_utils.object_data_add(context, mesh)
        highlight_object.parent = image_object
        highlight_object.matrix_parent_inverse = image_object.matrix_world.inverted()
        highlight_object.matrix_parent_inverse.identity()

        highlight_object.location = (0, 0, 0.001)
        highlight_object.lock_location[2] = True
        highlight_object.scale *= 0.5

        # geo nodes

        gmn = image_object.modifiers.new("Geometry Nodes", "NODES")
        gmn.node_group = append_node_group(filepath, "QuadMaskCo.000")
        gmn["Input_2"] = highlight_object
        gmn["Output_7_attribute_name"] = highlight_object.name_full + ".v1"
        gmn["Output_8_attribute_name"] = highlight_object.name_full + ".v2"
        gmn["Output_9_attribute_name"] = highlight_object.name_full + ".v3"
        gmn["Output_10_attribute_name"] = highlight_object.name_full + ".v4"

        # shader nodes

        shader_node_tree = image_object.active_material.node_tree
        ih_node_group = shader_node_tree.nodes.new("ShaderNodeGroup")
        ih_node_group.node_tree = append_node_group(
            filepath, "inverse_highlight.000")
        ih_node_group.label = highlight_object.name_full
        ih_node_group.node_tree.nodes["Attribute.v1"].attribute_name = highlight_object.name_full + ".v1"
        ih_node_group.node_tree.nodes["Attribute.v2"].attribute_name = highlight_object.name_full + ".v2"
        ih_node_group.node_tree.nodes["Attribute.v3"].attribute_name = highlight_object.name_full + ".v3"
        ih_node_group.node_tree.nodes["Attribute.v4"].attribute_name = highlight_object.name_full + ".v4"

        image_texture_node = shader_node_tree.nodes["Image Texture"]
        for i in shader_node_tree.links:
            if i.from_node.name == "Image Texture" and i.from_socket.name == "Color":
                shader_node_tree.links.new(
                    ih_node_group.outputs[0], i.to_socket)
        shader_node_tree.links.new(
            image_texture_node.outputs[0], ih_node_group.inputs[0])

        # default colors
        ih_node_group.inputs[1].default_value = 8
        ih_node_group.inputs[2].default_value = (0, 0, 0, 1) # black
        ih_node_group.inputs[3].default_value = (1, 1, 0, 1) # yellow

        return {'FINISHED'}


def append_node_group(filepath, node_group_name):
    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        assert (node_group_name in data_from.node_groups)
        data_to.node_groups = [node_group_name]
    return data_to.node_groups[0]


def menu_func(self, context):
    self.layout.operator(QNAL_OT_PlaneQuadMaskAdd.bl_idname, icon='MOD_OPACITY')

addon_keymaps = []

def register():
    bpy.utils.register_class(QNAL_OT_PlaneQuadMaskAdd)
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func)


def unregister():
    bpy.utils.unregister_class(QNAL_OT_PlaneQuadMaskAdd)
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.qnal.plane_quad_mask_add()

    # unregister()
