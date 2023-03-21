# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "RefSimilarImage",
    "description": "This is an add-on that uses BlendRef card nodes and loads images from outside",
    "author": "Yuuzen401",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location":  "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "https://github.com/Yuuzen401/RefSimilarImage",
    "category" : "Generic"
}

import bpy
import glob
import os
import sys
import time
from bpy.props import IntProperty, FloatProperty, FloatVectorProperty, BoolProperty, PointerProperty, CollectionProperty, StringProperty, EnumProperty
from .env import get_cv2_path
from .helper import show_message_error

cv2_path = get_cv2_path()
if cv2_path is not None :
    sys.path.append(get_cv2_path())
    import cv2

# Updater ops import, all setup in this file.
from . import addon_updater_ops

class RefSimilarImagePropertyGroup(bpy.types.PropertyGroup):

    image_method_enums = [
        ("FROM_VIEW_3D", "From View3D", ""),
        ("SELECT_IMAGE", "Select Image", ""),
    ]

    directory : StringProperty(name="directory", default=os.path.expanduser("~"), subtype="DIR_PATH")
    get_file_n : IntProperty(name="get file", default = 10, min = 1 , max = 100)
    image: PointerProperty(type=bpy.types.Image)
    image_method : EnumProperty(items = image_method_enums, name = "Select Image", default = "FROM_VIEW_3D")

class file() :

    def getNodeTree(self) :
        for area in bpy.context.screen.areas:
            if area.type == "NODE_EDITOR":
                tree_type = area.spaces.active.tree_type
                if tree_type == "BlendRefTreeType":
                    for space in area.spaces :
                        return space.node_tree
        return None

    def execute(self, context):

        ntree = self.getNodeTree(self)
        prop = context.scene.ref_similar_image_prop

        if ntree is None :
            show_message_error("BrendRefのノードツリーが作成されていません。")
            return {"CANCELLED"}

        if prop.image_method == "SELECT_IMAGE" :
            if prop.image is None :
                show_message_error("画像ファイルが選択されていません。")
                return {"CANCELLED"}

        files = self.getFiles(self, context)
        if len(files) == 0 :
            show_message_error("指定したディレクトリに画像ファイルが存在しません。")
            return {"CANCELLED"}

        # bpy.ops.object.select_all(action="DESELECT")
        # for obj in bpy.data.objects:
        #     if obj.type == "CAMERA":
        #         if "Camera" in obj.name:
        #             obj.select_set(True)
        #             bpy.data.objects.remove(obj)

        # cam = bpy.data.cameras.new(name="Camera")
        # if cam is None:
        #     return {"CANCELLED"}
        # my_camera = bpy.data.objects.new("Camera", cam)
        # if my_camera is None:
        #     return {"CANCELLED"}
       
        # bpy.context.scene.collection.objects.link(my_camera)
        # context.scene.camera = my_camera
        # bpy.ops.view3d.camera_to_view()
       
        # 撮影設定
        # bpy.context.scene.render.resolution_x = 1920
        # bpy.context.scene.render.resolution_y = 1080

        # ノードが追加されるエディタのnoodle_typeを取得

        nodes = ntree.nodes
        for node in nodes :
            nodes.remove(node)

        for i, file in enumerate(files) :
            image = bpy.data.images.load(file[1], check_existing = True)
            if image:
                node = ntree.nodes.new(type = "CardNode")
                node.image = image

        # From Code BlendRef LICENSE GNU
        # ****************************************************
        if len(nodes) > 0:
            node = nodes[0]
            prev_node = node
            max_height = node.width * node.image.size[1] / node.image.size[0]
            height = 0
            for i, cnode in enumerate(nodes[1:]):
                cnode.location.x = prev_node.location.x + prev_node.width + 10
                cnode.location.y = node.location.y - height - 20
                max_height = max(cnode.width * cnode.image.size[1] / cnode.image.size[0], max_height)
                prev_node = cnode
                
                if i % 10 == 0:
                    height += max_height
                    max_height = 0
                    prev_node = node
        # ****************************************************

        return {"FINISHED"}

    def getFiles(self, context):
        prop = context.scene.ref_similar_image_prop
        # アドオンの実行ディレクトリ内に一時ファイルを出力する
        tmp_dir = tmp_file = os.path.dirname(os.path.realpath(__file__)) + "/tmp".replace(os.sep, "/") + "/"
        timestamp = str(int(time.time()))
        tmp_file = tmp_dir + "tmp_" + timestamp + ".jpg"

        for tmp in  glob.glob(tmp_dir + "/tmp_*.jpg") :
            os.remove(tmp)

        if prop.image_method == "SELECT_IMAGE" :
            # 選択した画像を使用する
            prop.image.save_render(filepath = tmp_file)
        else :
            # View3Dの画像を使用する

            bpy.context.scene.render.filepath = tmp_file
            bpy.context.scene.render.image_settings.file_format = "JPEG"
            # bpy.context.scene.camera = my_camera
            # bpy.ops.render.render(write_still=True, use_viewport=True)
            bpy.ops.render.opengl(write_still = True, view_context = True)

        cam_img = cv2.imread(tmp_file)
        cam_gray = cv2.cvtColor(cam_img, cv2.COLOR_BGR2GRAY)
        orb = cv2.ORB_create()
        _, cam_descriptors = orb.detectAndCompute(cam_gray, None)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True)

        path = prop.directory
        files = []
        diff_files = [(9999, tmp_file)]
        for t in ("jpg", "jpeg", "png", "gif", "bmp", "tif", "tiff") :
            for fail in glob.glob(path + "/*." + t) :
                try :
                    files.append((fail.replace(os.sep, "/")))
                except:
                    pass
        
        if len(files) == 0 :
            return []

        for i, fail in enumerate(files) :
            try :
                diff_img = cv2.imread(fail)
                diff_gray = cv2.cvtColor(diff_img, cv2.COLOR_BGR2GRAY)
                # ORB (Oriented FAST and Rotated BRIEF)を使って特徴量を抽出する
                orb = cv2.ORB_create()
                _, diff_descriptors = orb.detectAndCompute(diff_gray, None)

                # 特徴量を使って類似度を計算する
                matches = bf.match(diff_descriptors, cam_descriptors)

                # 類似度を表示する
                value = len(matches)
                diff_files.append((value, fail))
            except:
                  pass

        # 高い順で並び変える
        sort_files = sorted(diff_files, reverse = True)
        n = prop.get_file_n
        return sort_files[:n]

class RefSimilarImageOperator(bpy.types.Operator, file):
    bl_idname = "ref_similar_image.operator"
    bl_label = "Get Reference"

    def invoke(self, context, event) :
        file.execute(file, context)
        return {"FINISHED"}

class VIEW3D_PT_RefSimilarImagePanel(bpy.types.Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = 'UI'
    bl_category = "Similar Image Search"
    bl_label = "Similar Image Search"
    
    @classmethod
    def poll(self, context):
        if context.area.type == "NODE_EDITOR":
            tree_type = context.area.spaces.active.tree_type
            if tree_type == "BlendRefTreeType" :
                return True
        return False

    def draw(self, context):
       prop = context.scene.ref_similar_image_prop
       layout = self.layout
       row = layout.row()
       row.prop(prop, "directory", text = "Select Directory")
       row = layout.row()
       row.prop(prop, "get_file_n", text = "Get File")
       row = layout.row()
       row.prop(prop, "image_method")
       row = layout.row()
       if prop.image_method == "SELECT_IMAGE" :
           row = layout.row()
           row.template_ID(prop, 'image', open = "image.open", live_icon = True)

       row = layout.row()
       row.operator(RefSimilarImageOperator.bl_idname)
       if cv2_path is None :
           row.enabled = False

class RefSimilarImageUpdaterPanel(bpy.types.Panel):
    bl_label = "Updater RefSimilarImage Panel"
    bl_idname = "OBJECT_PT_RefSimilarImageUpdaterPanel_hello"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS" if bpy.app.version < (2, 80) else "UI"
    bl_context = "objectmode"
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout

        # Call to check for update in background.
        # Note: built-in checks ensure it runs at most once, and will run in
        # the background thread, not blocking or hanging blender.
        # Internally also checks to see if auto-check enabled and if the time
        # interval has passed.
        addon_updater_ops.check_for_update_background()

        layout.label(text="RefSimilarImage Updater Addon")
        layout.label(text="")

        col = layout.column()
        col.scale_y = 0.7
        col.label(text="If an update is ready,")
        col.label(text="popup triggered by opening")
        col.label(text="this panel, plus a box ui")

        # Could also use your own custom drawing based on shared variables.
        if addon_updater_ops.updater.update_ready:
            layout.label(text="Custom update message", icon="INFO")
        layout.label(text="")

        # Call built-in function with draw code/checks.
        addon_updater_ops.update_notice_box_ui(self, context)

@addon_updater_ops.make_annotations
class RefSimilarImagePreferences(bpy.types.AddonPreferences):
    """RefSimilarImage bare-bones preferences"""
    bl_idname = __package__

    # Addon updater preferences.

    auto_check_update = bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False)

    updater_interval_months = bpy.props.IntProperty(
        name="Months",
        description="Number of months between checking for updates",
        default=0,
        min=0)

    updater_interval_days = bpy.props.IntProperty(
        name="Days",
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31)

    updater_interval_hours = bpy.props.IntProperty(
        name="Hours",
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23)

    updater_interval_minutes = bpy.props.IntProperty(
        name="Minutes",
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59)

    def draw(self, context):
        layout = self.layout

        # Works best if a column, or even just self.layout.
        mainrow = layout.row()
        col = mainrow.column()

        # Updater draw function, could also pass in col as third arg.
        addon_updater_ops.update_settings_ui(self, context)

        # Alternate draw function, which is more condensed and can be
        # placed within an existing draw function. Only contains:
        #   1) check for update/update now buttons
        #   2) toggle for auto-check (interval will be equal to what is set above)
        # addon_updater_ops.update_settings_ui_condensed(self, context, col)

        # Adding another column to help show the above condensed ui as one column
        # col = mainrow.column()
        # col.scale_y = 2
        # ops = col.operator("wm.url_open","Open webpage ")
        # ops.url=addon_updater_ops.updater.website

classes = (
    RefSimilarImagePropertyGroup,
    VIEW3D_PT_RefSimilarImagePanel,
    RefSimilarImagePreferences,
    RefSimilarImageUpdaterPanel,
    RefSimilarImageOperator,
    )

def register():
    addon_updater_ops.register(bl_info)
    for cls in classes:
        addon_updater_ops.make_annotations(cls)  # Avoid blender 2.8 warnings.
        bpy.utils.register_class(cls)
    bpy.types.Scene.ref_similar_image_prop = bpy.props.PointerProperty(type = RefSimilarImagePropertyGroup)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.ref_similar_image_prop

    addon_updater_ops.unregister()

if __name__ == "__main__":
    register()