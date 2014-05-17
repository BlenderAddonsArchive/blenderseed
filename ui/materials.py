
#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2013 Franz Beaune, Joel Daniels, Esteban Tovagliari.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import bpy

#---------------------------------------------
class AppleseedMaterialPreview(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    
    bl_context = "material"
    bl_label = "Preview"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine in cls.COMPAT_ENGINES and context.object is not None and context.object.active_material is not None

    def draw(self, context):
        layout = self.layout
        obj = context.object
        material = obj.active_material
        asr_mat = material.appleseed

        layout.template_preview(context.material, show_buttons = True)
        layout.prop(asr_mat, "preview_quality")

        
class MATERIAL_UL_BSDF_slots(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        BSDF = item
        bsdf_type = BSDF.bsdf_type
        bsdf_type_name = bsdf_type[0].upper() + bsdf_type[1:-5] + " " + bsdf_type[-4:].upper()
        if 'DEFAULT' in self.layout_type:            
            layout.label(text = BSDF.name + "  |  " + bsdf_type_name, translate=False, icon_value=icon)

class AppleseedMaterialShading(bpy.types.Panel):
    bl_label = 'appleseed Surface Shading'
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    
    @classmethod
    def poll( cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER' and context.object is not None and context.object.type == 'MESH' and context.object.active_material is not None
    
    def draw(self, context):
        layout = self.layout
        object = context.object
        material = object.active_material
        asr_mat = material.appleseed
        
        layout.label("BSDF Layers:", icon = 'MATERIAL')

       
        row = layout.row()
        row.template_list("MATERIAL_UL_BSDF_slots", "appleseed_material_layers", asr_mat, "layers", asr_mat, "layer_index", maxrows = 16, type = "DEFAULT")
        
        row = layout.row(align=True)
        row.operator("appleseed.add_matlayer", icon = "ZOOMIN")
        row.operator("appleseed.remove_matlayer", icon = "ZOOMOUT")
                
        if asr_mat.layers:
            current_layer = asr_mat.layers[asr_mat.layer_index]   
            layout.prop(current_layer, "name")
            layout.prop(current_layer, "bsdf_type")
            layout.separator()

            layout.label("BSDF Layer Settings:")
            
            #Lambertian BRDF layout
            if current_layer.bsdf_type == "lambertian_brdf":
                box = layout.box()

                # Weight
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "lambertian_weight", text = "Layer Weight")
                if current_layer.lambertian_use_tex:
                    col.prop_search( current_layer, "lambertian_mix_tex", material, "texture_slots")

                col = split.column()
                col.prop( current_layer, "lambertian_use_tex", toggle = True)
                if current_layer.lambertian_mix_tex != '' and current_layer.lambertian_use_tex:
                    mix_tex = bpy.data.textures[current_layer.lambertian_mix_tex]
                    box.prop( mix_tex.image.colorspace_settings, "name", text = "Color Space")

                # Reflectance
                box.label("Lambertian Reflectance:")
                
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "lambertian_reflectance", text = "")
                if current_layer.lambertian_use_diff_tex:    
                    col.prop_search(current_layer, "lambertian_diffuse_tex", material, "texture_slots")
                
                col = split.column()
                col.prop(current_layer, "lambertian_use_diff_tex", text = "Use Texture", toggle = True)
                if current_layer.lambertian_diffuse_tex != '' and current_layer.lambertian_use_diff_tex:
                    diffuse_tex = bpy.data.textures[current_layer.lambertian_diffuse_tex]
                    box.prop(diffuse_tex.image.colorspace_settings, "name", text = "Color Space")
                box.prop(current_layer, "lambertian_multiplier")
            
            #-------------------------------------------------
            #Oren-Nayar BRDF layout
            if current_layer.bsdf_type == "orennayar_brdf":
                box = layout.box()

                # Weight
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "orennayar_weight", text = "Layer Weight")
                if current_layer.orennayar_use_tex:
                    col.prop_search( current_layer, "orennayar_mix_tex", material, "texture_slots")

                col = split.column()
                col.prop( current_layer, "orennayar_use_tex", toggle = True)
                if current_layer.orennayar_mix_tex != '' and current_layer.orennayar_use_tex:
                    mix_tex = bpy.data.textures[current_layer.orennayar_mix_tex]
                    box.prop( mix_tex.image.colorspace_settings, "name", text = "Color Space")

                # Reflectance
                box.label("Oren-Nayar Reflectance:")
                
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "orennayar_reflectance", text = "")

                if current_layer.orennayar_use_diff_tex:    
                    col.prop_search(current_layer, "orennayar_diffuse_tex", material, "texture_slots")
                
                col = split.column()
                col.prop(current_layer, "orennayar_use_diff_tex", text = "Use Texture", toggle = True)
                if current_layer.orennayar_diffuse_tex != '' and current_layer.orennayar_use_diff_tex:
                    diffuse_tex = bpy.data.textures[current_layer.orennayar_diffuse_tex]
                    box.prop(diffuse_tex.image.colorspace_settings, "name", text = "Color Space")
                box.prop(current_layer, "orennayar_multiplier")

                box.separator()

                # Roughness
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "orennayar_roughness")
                if current_layer.orennayar_use_rough_tex:    
                    col.prop_search(current_layer, "orennayar_rough_tex", material, "texture_slots")
                
                col = split.column()
                col.prop(current_layer, "orennayar_use_rough_tex", text = "Use Texture", toggle = True)
                if current_layer.orennayar_rough_tex != '' and current_layer.orennayar_use_rough_tex:
                    rough_tex = bpy.data.textures[current_layer.orennayar_diffuse_tex]
                    box.prop(rough_tex.image.colorspace_settings, "name", text = "Color Space")
                
            #-------------------------------------------------
            #Ashikhmin-Shirley BRDF layout    
            elif current_layer.bsdf_type == "ashikhmin_brdf":
                box = layout.box()

                # Weight
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "ashikhmin_weight", text = "Layer Weight")
                if current_layer.ashikhmin_use_tex:
                    col.prop_search( current_layer, "ashikhmin_mix_tex", material, "texture_slots")

                col = split.column()
                col.prop( current_layer, "ashikhmin_use_tex", toggle = True)
                if current_layer.ashikhmin_mix_tex != '' and current_layer.ashikhmin_use_tex:
                    mix_tex = bpy.data.textures[current_layer.ashikhmin_mix_tex]
                    box.prop( mix_tex.image.colorspace_settings, "name", text = "Color Space")
                
                # Reflectance
                box.label("Diffuse Reflectance:")
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "ashikhmin_reflectance", text = "")
                if current_layer.ashikhmin_use_diff_tex:
                    col.prop_search(current_layer, "ashikhmin_diffuse_tex", material, "texture_slots", text = "")
                
                col = split.column()
                col.prop(current_layer, "ashikhmin_use_diff_tex", text = "Use Texture", toggle = True)    
                if current_layer.ashikhmin_diffuse_tex != '' and current_layer.ashikhmin_use_diff_tex:
                    diffuse_tex = bpy.data.textures[current_layer.ashikhmin_diffuse_tex]
                    box.prop(diffuse_tex.image.colorspace_settings, "name", text = "Color Space")
                row = box.row()
                row.prop(current_layer, "ashikhmin_multiplier")
                
                box.label("Glossy Reflectance:")
                split = box.split(percentage = 0.65)
                col = split.column()    
                col.prop(current_layer, "ashikhmin_glossy", text = "")
                if current_layer.ashikhmin_use_gloss_tex:
                    col.prop_search(current_layer, "ashikhmin_gloss_tex", material, "texture_slots", text = "")
                
                col = split.column()
                col.prop(current_layer, "ashikhmin_use_gloss_tex", text = "Use Texture", toggle = True)
                if current_layer.ashikhmin_gloss_tex != '' and current_layer.ashikhmin_use_gloss_tex:
                    gloss_tex = bpy.data.textures[current_layer.ashikhmin_gloss_tex]
                    box.prop(gloss_tex.image.colorspace_settings, "name", text = "Color Space")
                row = box.row()
                row.prop(current_layer, "ashikhmin_glossy_multiplier")
                
                col = box.column()
                col.prop(current_layer, "ashikhmin_fresnel")
                row = box.row(align=True)
                row.prop(current_layer, "ashikhmin_shininess_u")
                row.prop(current_layer, "ashikhmin_shininess_v")
            
            #-------------------------------------------------
            #Diffuse BTDF layout
            elif current_layer.bsdf_type == "diffuse_btdf":
                box = layout.box()
                # Weight
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "transmittance_weight", text = "Layer Weight")
                if current_layer.transmittance_use_tex:
                    col.prop_search( current_layer, "transmittance_mix_tex", material, "texture_slots")

                col = split.column()
                col.prop( current_layer, "transmittance_use_tex", toggle = True)
                if current_layer.transmittance_mix_tex != '' and current_layer.transmittance_use_tex:
                    mix_tex = bpy.data.textures[current_layer.transmittance_mix_tex]
                    box.prop( mix_tex.image.colorspace_settings, "name", text = "Color Space")
                
                # Reflectance
                box.label("Transmittance Color:")
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "transmittance_color", text = "")
                if current_layer.transmittance_use_diff_tex:    
                    col.prop_search(current_layer, "transmittance_diff_tex", material, "texture_slots", text = "")
                col = split.column()
                col.prop(current_layer, "transmittance_use_diff_tex", text = "Use Texture", toggle = True)            
                if current_layer.transmittance_diff_tex!= '' and current_layer.transmittance_use_diff_tex:
                    diffuse_tex = bpy.data.textures[current_layer.transmittance_diff_tex]
                    box.prop(diffuse_tex.image.colorspace_settings, "name", text = "Color Space")

                # Transmittance
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "transmittance_multiplier", text = "Transmittance")
                if current_layer.transmittance_use_mult_tex:    
                    col.prop_search(current_layer, "transmittance_mult_tex", material, "texture_slots", text = "")
                col = split.column()
                col.prop(current_layer, "transmittance_use_mult_tex", text = "Use Texture", toggle = True)            
                if current_layer.transmittance_mult_tex!= '' and current_layer.transmittance_use_mult_tex:
                    mult_tex = bpy.data.textures[current_layer.transmittance_mult_tex]
                    box.prop(mult_tex.image.colorspace_settings, "name", text = "Color Space")
                    
            #-------------------------------------------------    
            #Kelemen BRDF layout    
            elif current_layer.bsdf_type == "kelemen_brdf":
                box = layout.box()

                # Weight
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "kelemen_weight", text = "Layer Weight")
                if current_layer.kelemen_use_tex:
                    col.prop_search( current_layer, "kelemen_mix_tex", material, "texture_slots")

                col = split.column()
                col.prop( current_layer, "kelemen_use_tex", toggle = True)
                if current_layer.kelemen_mix_tex != '' and current_layer.kelemen_use_tex:
                    mix_tex = bpy.data.textures[current_layer.kelemen_mix_tex]
                    box.prop( mix_tex.image.colorspace_settings, "name", text = "Color Space")
                
                # Reflectance
                box.label("Matte Reflectance:")
                
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "kelemen_matte_reflectance", text = "")
                if current_layer.kelemen_use_diff_tex:
                    col.prop_search(current_layer, "kelemen_diff_tex", material, "texture_slots", text = "")
                
                col = split.column()
                col.prop(current_layer, "kelemen_use_diff_tex", text = "Use Texture", toggle = True)            
                if current_layer.kelemen_diff_tex != '' and current_layer.kelemen_use_diff_tex:
                    diffuse_tex = bpy.data.textures[current_layer.kelemen_diff_tex]
                    box.prop(diffuse_tex.image.colorspace_settings, "name", text = "Color Space")
                row = box.row()
                row.prop(current_layer, "kelemen_matte_multiplier")
                
                box.label("Specular Reflectance:")
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "kelemen_specular_reflectance", text = "")    
                if current_layer.kelemen_use_spec_tex:
                    col.prop_search(current_layer, "kelemen_spec_tex", material, "texture_slots", text = "")
                col = split.column()
                col.prop(current_layer, "kelemen_use_spec_tex", text = "Use Texture", toggle = True)
                if current_layer.kelemen_spec_tex != '' and current_layer.kelemen_use_spec_tex:
                    spec_tex = bpy.data.textures[current_layer.kelemen_spec_tex]
                    box.prop(spec_tex.image.colorspace_settings, "name", text = "Color Space")
                box.prop(current_layer, "kelemen_specular_multiplier")
                box.prop(current_layer, "kelemen_roughness")
                
            #-------------------------------------------------
            #Microfacet BRDF layout
            elif current_layer.bsdf_type == "microfacet_brdf":
                box = layout.box()
                # Weight
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "microfacet_weight", text = "Layer Weight")
                if current_layer.microfacet_use_tex:
                    col.prop_search( current_layer, "microfacet_mix_tex", material, "texture_slots")

                col = split.column()
                col.prop( current_layer, "microfacet_use_tex", toggle = True)
                if current_layer.microfacet_mix_tex != '' and current_layer.microfacet_use_tex:
                    mix_tex = bpy.data.textures[current_layer.microfacet_mix_tex]
                    box.prop( mix_tex.image.colorspace_settings, "name", text = "Color Space")
                
                # Reflectance
                box.prop(current_layer, "microfacet_model", text= "Model")
                box.label("Microfacet Reflectance:")
                
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "microfacet_reflectance", text = "")
                if current_layer.microfacet_use_diff_tex:
                    col.prop_search(current_layer, "microfacet_diff_tex", material, "texture_slots", text = "")
                
                col = split.column()
                col.prop(current_layer, "microfacet_use_diff_tex", text = "Use Texture", toggle = True)
                if current_layer.microfacet_diff_tex != '' and current_layer.microfacet_use_diff_tex:
                    diff_tex = bpy.data.textures[current_layer.microfacet_diff_tex]
                    box.prop(diff_tex.image.colorspace_settings, "name", text = "Color Space:")
                box.prop(current_layer, "microfacet_multiplier")
                
                box.separator()
                split = box.split(percentage = 0.65)
                col = split.column()
                if current_layer.microfacet_model != 'blinn':
                    col.prop(current_layer, "microfacet_mdf")
                else:
                    col.prop(current_layer, "microfacet_mdf_blinn")
                    
                if current_layer.microfacet_use_spec_tex:
                    col.prop_search(current_layer, "microfacet_spec_tex", material, "texture_slots", text = "")
                col = split.column()
                col.prop(current_layer, "microfacet_use_spec_tex", text = "Use Texture", toggle = True)
                if current_layer.microfacet_spec_tex != '' and current_layer.microfacet_use_spec_tex:
                    spec_tex = bpy.data.textures[current_layer.microfacet_spec_tex]
                    box.prop(spec_tex.image.colorspace_settings, "name", text = "Color Space:")
                    
                box.prop(current_layer, "microfacet_fresnel")
            
            #-------------------------------------------------
            #Specular BRDF layout
            elif current_layer.bsdf_type == "specular_brdf":
                box = layout.box()

                # Weight
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "specular_weight", text = "Layer Weight")
                if current_layer.specular_use_tex:
                    col.prop_search( current_layer, "specular_mix_tex", material, "texture_slots")

                col = split.column()
                col.prop( current_layer, "specular_use_tex", toggle = True)
                if current_layer.specular_mix_tex != '' and current_layer.specular_use_tex:
                    mix_tex = bpy.data.textures[current_layer.specular_mix_tex]
                    box.prop( mix_tex.image.colorspace_settings, "name", text = "Color Space")
                
                # Reflectance
                box.label("Specular Reflectance:")
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "specular_reflectance", text = "")
                if current_layer.specular_use_gloss_tex:
                    col.prop_search(current_layer, "specular_gloss_tex", material, "texture_slots", text = "")
                col = split.column()
                col.prop(current_layer, "specular_use_gloss_tex", text = "Use Texture", toggle = True)
                if current_layer.specular_gloss_tex != '' and current_layer.specular_use_gloss_tex:
                    spec_tex = bpy.data.textures[current_layer.specular_gloss_tex]
                    box.prop(spec_tex.image.colorspace_settings, "name", text = "Color Space:")
                box.prop(current_layer, "specular_multiplier")
            
            #----------------------------------------------
            #Specular BTDF layout    
            elif current_layer.bsdf_type == "specular_btdf":
                box = layout.box()

                # Weight
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "spec_btdf_weight", text = "Layer Weight")
                if current_layer.spec_btdf_use_tex:
                    col.prop_search( current_layer, "spec_btdf_mix_tex", material, "texture_slots")

                col = split.column()
                col.prop( current_layer, "spec_btdf_use_tex", toggle = True)
                if current_layer.spec_btdf_mix_tex != '' and current_layer.spec_btdf_use_tex:
                    mix_tex = bpy.data.textures[current_layer.spec_btdf_mix_tex]
                    box.prop( mix_tex.image.colorspace_settings, "name", text = "Color Space")
                
                # Reflectance
                box.label("Specular Reflectance:")
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "spec_btdf_reflectance", text = "")
                if current_layer.spec_btdf_use_spec_tex:
                    col.prop_search(current_layer, "spec_btdf_spec_tex", material, "texture_slots", text = "")
                col = split.column()
                col.prop(current_layer, "spec_btdf_use_spec_tex", text = "Use Texture", toggle = True)
                if current_layer.spec_btdf_spec_tex != '' and current_layer.spec_btdf_use_spec_tex:
                    spec_tex = bpy.data.textures[current_layer.spec_btdf_spec_tex]
                    box.prop(spec_tex.image.colorspace_settings, "name", text = "Color Space:")
                box.prop(current_layer, "spec_btdf_ref_mult")
               
                box.separator()
                
                box.label("Transmittance Reflectance:")
                split = box.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "spec_btdf_transmittance", text = "")
                if current_layer.spec_btdf_use_trans_tex:
                    col.prop_search(current_layer, "spec_btdf_trans_tex", material, "texture_slots", text = "")
                col = split.column()
                col.prop(current_layer, "spec_btdf_use_trans_tex", text = "Use Texture", toggle = True)
                if current_layer.spec_btdf_trans_tex != '':
                    trans_tex = bpy.data.textures[current_layer.spec_btdf_trans_tex]
                    box.prop(trans_tex.image.colorspace_settings, "name", text = "Color Space:")
                box.prop(current_layer, "spec_btdf_trans_mult")
                
                row = box.row(align= True)
                row.prop(current_layer, "spec_btdf_from_ior")
                row.prop(current_layer, "spec_btdf_to_ior")
        
        #Per material alpha/bump
        layout.separator()
        layout.separator()
        layout.label("Per-material Alpha / Bump Mapping", icon = "TEXTURE_SHADED")
        box = layout.box()
        split = box.split(percentage = 0.65)
        col = split.column()
        col.prop(asr_mat, "material_use_bump_tex", text = "Use Bump Texture", toggle= True)
        col = split.column()
        if asr_mat.material_use_bump_tex:
            col.prop(asr_mat, "material_use_normalmap", text = "Normal Map", toggle = True)            
            box.prop_search(asr_mat, "material_bump_tex", material, "texture_slots", text = "")
            
            if asr_mat.material_bump_tex != '':
                bump_tex = bpy.data.textures[asr_mat.material_bump_tex]
                box.prop(bump_tex.image.colorspace_settings, "name",  text = "Color Space")
            box.prop(asr_mat, "material_bump_amplitude")
            
        box.separator()    
        split = box.split(percentage = 0.65)
        col = split.column()
        col.prop(asr_mat, "material_use_alpha", text = "Use Alpha Texture", toggle = True)
        col = split.column()
        if asr_mat.material_use_alpha:    
            col.prop_search(asr_mat, "material_alpha_map", material, "texture_slots", text = "")        
            if asr_mat.material_alpha_map != '':
                alpha_tex = bpy.data.textures[asr_mat.material_alpha_map]
                box.prop(alpha_tex.image.colorspace_settings, "name", text = "Color Space")
        else:
            col.prop(asr_mat, "material_alpha")
        
class AppleseedMatEmissionPanel(bpy.types.Panel):
    bl_label = "appleseed Light Emission"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll( cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER' and context.object is not None and context.object.type == 'MESH' and context.object.active_material is not None
    
    def draw_header(self, context):
        header = self.layout
        asr_mat = context.object.active_material.appleseed
        header.prop(asr_mat, "use_light_emission")
    
    def draw(self, context):
        layout = self.layout
        material = context.object.active_material
        asr_mat = material.appleseed
              
        #Light emission properties                 
        row = layout.row()
        row.active = asr_mat.use_light_emission
        row.prop(asr_mat, "light_emission", text = "Emission Strength")
        row = layout.row()
        row.prop(asr_mat, "light_color", text = "Light Color")

#class AppleseedMatSSSPanel(bpy.types.Panel):
#    bl_label = "appleseed FastSSS"
#    bl_space_type = "PROPERTIES"
#    bl_region_type = "WINDOW"
#    bl_context = "material"
#    bl_options = {'DEFAULT_CLOSED'}
#    
#    @classmethod
#    def poll( cls, context):
#        renderer = context.scene.render
#        return renderer.engine == 'APPLESEED_RENDER' and context.object is not None and context.object.type == 'MESH' and context.object.active_material is not None
#    
#    def draw_header(self, context):
#        header = self.layout
#        asr_mat = context.object.active_material.appleseed
#        header.prop(asr_mat, "sss_use_shader")
#    
#    def draw(self, context):
#        layout = self.layout
#        material = context.object.active_material
#        asr_mat = material.appleseed
#        layout.active = asr_mat.sss_use_shader
#        
#        row = layout.row(align=True)
#        row.prop(asr_mat, "sss_power", text = "SSS Power")
#        row.prop(asr_mat, "sss_scale")
#        
#        layout.label("Albedo Color:")
#        row = layout.row()
#        row.prop(material.subsurface_scattering, "color", text = "")
#        row.prop(asr_mat, "sss_albedo_use_tex", text = "Use Texture", toggle = True)
#        if asr_mat.sss_albedo_use_tex:
#            layout.prop_search(asr_mat, "sss_albedo_tex", material, "texture_slots", text = "")
#            if asr_mat.sss_albedo_tex != '':
#                albedo_tex = bpy.data.textures[asr_mat.sss_albedo_tex]
#                layout.prop(albedo_tex.image.colorspace_settings, "name", text = "Color Space")
#        
#        layout.separator()
#        
#        row = layout.row(align=True)
#        row.prop(asr_mat, "sss_ambient")  
#        row.prop(asr_mat, "sss_view_dep")  
#        
#        row = layout.row(align=True)
#        row.prop(asr_mat, "sss_diffuse")    
#        row.prop(asr_mat, "sss_distortion")
#        
#        row = layout.row(align=True)
#        row.prop(asr_mat, "sss_light_samples")
#        row.prop(asr_mat, "sss_occlusion_samples")

def register():
    bpy.types.MATERIAL_PT_context_material.COMPAT_ENGINES.add( 'APPLESEED_RENDER')
    bpy.types.MATERIAL_PT_custom_props.COMPAT_ENGINES.add( 'APPLESEED_RENDER')
    bpy.utils.register_class( AppleseedMaterialPreview)
    bpy.utils.register_class( MATERIAL_UL_BSDF_slots)
    bpy.utils.register_class( AppleseedMaterialShading)
    bpy.utils.register_class( AppleseedMatEmissionPanel)
    #bpy.utils.register_class( AppleseedMatSSSPanel)
    

def unregister():
    bpy.utils.unregister_class( AppleseedMaterialPreview)
    bpy.utils.unregister_class( MATERIAL_UL_BSDF_slots)
    bpy.utils.unregister_class( AppleseedMaterialShading)
    #bpy.utils.unregister_class( AppleseedMatEmissionPanel)
    bpy.utils.unregister_class( AppleseedMatSSSPanel)
