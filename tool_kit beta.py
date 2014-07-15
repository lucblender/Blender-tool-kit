bl_info = {
    "name": "Tool Kit",
    "description": "Useful Tools",
    "author": "lucblender",
    "version": (1, '10_beta'),
    "blender": (2, 69, 0),
    "location": "Left UI",
    "warning": "", # used for warning icon and text in addons 
    "wiki_url": ""
                "Scripts/My_Script",
    "category": "User"}

import bpy
from bpy.props import *
import time
import datetime

from bpy.types import Operator, AddonPreferences, Panel, Menu

tab=[]  #tableau auquel sera inclu les objets utilisant un materiel
#originNbrScene=len(bpy.data.scenes)

global FormatItem, maximise_minimase, maximise_minimase_Mat,stop,checked_render, animation_state, Exception_materials

animation_state = True

checked_render = False  # permet de savoir si le rendu ce fait en mode checked render or all render
stop = True #permet de savoir quand un rendu est fini
maximise_minimase = True
maximise_minimase_Mat = True

FormatItem=[('H264 1440*1080', 'H264 4/3 HD1080', 'H264 1440*1080'), 
                 ('PNG 800*600', 'PNG 4/3 LowRes 600', 'PNG 800*600'),
				 ('PNG 1920*1080', 'PNG Full HD', 'PNG 1920*1080'),
				 ('PNG 1280*720', 'PNG HD 720', 'PNG 1280*720')]

Exception_materials = [('Material','Material','Material')]                 
                 
def MaterialCheck ():
    scn = bpy.data.scenes[0]
    materialError=False 
    objs = []  
    try:            
        mat = bpy.context.object.active_material#essaye d'avoir le materiel actif   
    except:
        materialError=True  #si aucun materiel active
        mat_str="No active object"   #fait un report d'erreur        
    else:
        if mat == None:     #si le materiel active = None -> objet actif pas de materiel  
            materialError=True  #si aucun materiel activ
            mat_str="Object has no material"   
        else: #si aucune erreur de materiel est détecté
            for obj in bpy.data.objects:    #pour tous les objet
                for slot in obj.material_slots: #pour chaque slot de materiel par objet
                    if slot.material == mat:    #si le materiel est le même que le materiel de l'objet actif 
                        objs.append(obj.name)   #append le nom de l'objet 
            mat_str = 'Active material: '+str(bpy.context.object.active_material.name)+\
            ', '+"".join(str(x)+', ' for x in objs)        
    return mat_str

def check_obj_mat():
    all_mat=[]
    for obj in bpy.context.scene.objects:
        if obj.type=='MESH':
            for mat in obj.material_slots:
                all_mat.append(mat.material)
    return all_mat                
def replace_obj_mat(mat_to_assign=[]):
    i=0
    for obj in bpy.context.scene.objects:
        if obj.type=='MESH':
            for mat in obj.material_slots:
                mat.material=mat_to_assign[i]
                i=i+1 

class Tool_KitPreferences(AddonPreferences):
    bl_idname = __name__

    tool_disable_enable_animation = BoolProperty(
            name="Disable-Enable animation",
            description="Possibility to enable or disable the animation",
            default=True,
            )            
    tool_change_format_file = BoolProperty(
            name="Change format file",
            description="Change the format file of all scenes",
            default=True,
            )
    tool_render_path = BoolProperty(
            name="Render path",
            description="Change the render path of all scene",
            default=True,
            )
    tool_add_new_scene = BoolProperty(
            name="Add new scene",
            description="Add new scene with material correction",
            default=True,
            )
    tool_material_correction = BoolProperty(
            name="Material correction",
            description="Replace double material",
            default=True,
            )
    tool_font_cleaning = BoolProperty(
            name="Font Cleaning",
            description="Change all font for the selected one",
            default=True,
            )
    tool_active_object_material = BoolProperty(
            name="Active object material",
            description="Show the active object material and all his users",
            default=True,
            )    
    tool_render_specific_scene = BoolProperty(
            name="Render specific scene",
            description="Render all scene or selected scene",
            default=True,
            )  
    tool_other_shortcut = BoolProperty(
            name="Other shortcut",
            description="Other usefull shortcut",
            default=True,
            )                                                          
    def draw(self, context):
        layout = self.layout

        layout.label(
            text="Here you can enable or disable any of the 9 tools of the toolkit")

        split = layout.split(percentage=0.25)

        col = split.column()
        sub = col.column(align=True)
        sub.label(text="List of tools available", icon="PREFERENCES")
        
        sub.separator()
        sub.prop(self, "tool_disable_enable_animation",icon='PLAY')
        sub.prop(self, "tool_change_format_file",icon='FILE') 
        sub.prop(self, "tool_render_path",icon='FILE_FOLDER')
        sub.prop(self, "tool_add_new_scene",icon='SCENE_DATA')
        sub.prop(self, "tool_material_correction",icon='MATERIAL')
        sub.prop(self, "tool_font_cleaning",icon='FONT_DATA')
        sub.prop(self, "tool_active_object_material",icon='MATERIAL')
        sub.prop(self, "tool_render_specific_scene",icon='RENDER_ANIMATION')
        sub.prop(self, "tool_other_shortcut", icon='PREFERENCES') 
        
        sub.separator()
        
        col = split.column()
        sub = col.column(align=True)
        
        sub.separator()      
        sub.label(text='')       
        sub.label(text="Possibility to enable or disable the animation to play")
        sub.label(text="Change the format file of all scenes with some preset")
        sub.label(text="Change the render path of all scene and possibility to add or remove keyword from the path")
        sub.label(text="Add new scene (full copy) with material correction (no material duplication)")
        sub.label(text="Replace double material ex: Material , Material.001 -> become both Material")
        sub.label(text="Change all font for the selected one")
        sub.label(text="Show the active object material and all his users with some details")
        sub.label(text="Possibility to render all scenes or selected scenes")
        sub.label(text="Other useful shortcut already implemented in blender")
		
#
#    Menu in UI region
#
class UIPanel(bpy.types.Panel):
    bl_label = "ToolKit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tool Kit"
    
    
    def draw(self, context):
        
        current_scn=bpy.context.scene
        scn = bpy.data.scenes[0]   
        
        #for developpement 
        try: __name__
        except: __name__ = 'tool_kit beta'        
        
        preferences = context.user_preferences.addons[__name__].preferences     
        
        layout = self.layout
        
        layout.template_reports_banner()
        layout.template_running_jobs()   
        
        
        if preferences.tool_active_object_material==False and\
            preferences.tool_add_new_scene==False and\
            preferences.tool_change_format_file==False and\
            preferences.tool_disable_enable_animation==False and\
            preferences.tool_font_cleaning==False and\
            preferences.tool_material_correction==False and\
            preferences.tool_other_shortcut==False and\
            preferences.tool_render_path==False and\
            preferences.tool_render_specific_scene == False:
            layout.label(text='Warning no tools enable', icon ='ERROR')        
        
        if preferences.tool_disable_enable_animation == True: 
                   
            layout.label('Disable-Enable animation')
            
            box = layout.box()
            row = box.row(align=True)   
             
            global animation_state
            
            if animation_state == True:     
            
                row.operator("animation.disable")
            else:
                row.operator("animation.enable")
        
        if preferences.tool_change_format_file== True:
            
            layout.label(text="Change the format of all scene file")  
            
            box = layout.box()  
            box.prop(bpy.context.scene, 'FormatFile', text=bpy.context.scene.name)
            box.operator("file.format")
        
            box = box.box() 
            row=box.row()
            row = row.column(align=True)
            row.prop(current_scn.render,'resolution_x')
            row.prop(current_scn.render,'resolution_y')
            row.prop(current_scn.render.image_settings,'file_format')  
                 
            row = box.row(align=True)    #le row permet de 'coller' les 2 boutons         
            row.operator("add.format")      
            row.operator("remove.format")
            
        if preferences.tool_render_path == True:    
        
            layout.label('Render Path modifications')
            box = layout.box()
                    
            box.prop(bpy.context.scene,'NewRenderPath')
            box.operator('render.changepath')
            
            box.prop(bpy.context.scene,'AddRemoveRenderPath')          
            row = box.row(align = True)
            row.operator('to_render_path.add')
            row.operator('to_render_path.remove')
        
        
        if preferences.tool_add_new_scene == True:
            
            layout.label(text="Add new Scene")
            box = layout.box()
            box.operator("full_copy.mat_corr", icon = 'ZOOMIN')
        
        if preferences.tool_material_correction:
                
            layout.label(text="Replace 'double' material")
            box = layout.box()
            box.operator("clean.material",icon = 'MATERIAL')
            box.label('Exceptions materials, be carefull only selected Material are Exception')
            
            row=box.row()
            row = row.column(align=True)
            
            row.prop(bpy.context.scene,'ExceptionMaterials')
                 
            if len(bpy.context.scene.ExceptionMaterials)==0: #si le nbre d'exception est =0 
                row.label("No exception material", icon='INFO') #si pas d'exception -> info
                   
            row.prop(bpy.context.scene, 'MaterialException',icon='OUTLINER_DATA_FONT',text='')  # affichage dynamique des exception
            
            row.separator()
            
            row = box.row(align = True)  
            
            row.operator("add.exception")  
            row.operator("remove.exception")    
   
        
        if preferences.tool_font_cleaning == True:
            
            layout.label('Font cleaning')
            box = layout.box()   
            
            if len(bpy.data.fonts) == 0:
                box.enabled=False     
                box.label(text='Warning no Font yet', icon='ERROR')                     
            box.operator("font.clean", icon ='FILE_FONT')
            box.prop(bpy.context.scene,'AllFont', text = 'Keep this font')
                
        
        if preferences.tool_active_object_material == True:
            
            layout.label(text="Active material and its objects")
            
            box = layout.box()  #créer une boxe pour les materiaux
            
            materialobject = MaterialCheck()
            
            try:
                tab = materialobject.rsplit(',')    # essai de faire un rsplit -> si fonctionne veux dire que tab comporte le nom de plusieurs objets -> tab = tableau des objets ayant le material actif
            except:
                tab=[str(materialobject)]   # sinon met la chaîne de char materialobject dans tab -> index de tab = 1
            
            for i in range(0, len(tab)):
               
                if materialobject in ("Object has no material","No active object"): #si materialobject contient un text 'erreur'
                    try:
                        bpy.context.active_object.type     #test de voir si il y a un objet actif
                    except:
                        box.label(text='No active object', icon='ERROR')    #erreur aucun objet actif
                    else:    
                        row=box.row()    
                        if bpy.context.active_object.type != 'MESH':    #si l'objet actif n'est pas un mesh
                            row.label(text='Active object is {0} not mesh'.format(bpy.context.active_object.type.title()),icon='ERROR')  #erreur objet non mesh
                        else:    
                            row.label(str(tab[i]),icon='ERROR')  # sinon objet = mesh mais pas de materiel              
                elif i!=0 :
                    if maximise_minimase_Mat == False:   
                        if i != len(tab)-1:
                            #row=box.row()       
                            for scn in bpy.data.scenes:
                                for obj in scn.objects:
                                    if str(obj.name) == str(tab[i]).replace(' ',''):  
                                        row=box.row()    
                                        row.label(str(tab[i])+' ',icon='OBJECT_DATAMODE')
                                        row.label(icon = 'FORWARD')
                                        row.label(str(scn.name),icon='SCENE_DATA')
                                        break
                                        
                else:
                    row=box.row()
                    if maximise_minimase_Mat==True:
                        row.label(str(tab[i])[:13]+'...',icon='MATERIAL')
                    else:
                        row.label(str(tab[i]),icon='MATERIAL')   
           
            row = box.row()
            row.alignment = 'RIGHT'
            if maximise_minimase_Mat == True or bpy.context.active_object == None or bpy.context.active_object.active_material == None :
                try:
                    bpy.context.active_object.active_material.name
                    row.enabled = True
                except:
                    row.enabled = False  
                row.operator("max_min.matprop", icon='TRIA_DOWN', text='')              
            else:
                row.operator("max_min.matprop", icon='TRIA_UP', text='')           
                

        if preferences.tool_render_specific_scene == True:
                        
            layout.label(text="Render all or selected scene.")
            box = layout.box()
            
            row = box.row(align=True)    #le row permet de 'coller les 2 boutons  

            row.operator("allscene.render")
            row.operator("checkedscene.render")
            
            box = box.box()
            global maximise_minimase
            
            if maximise_minimase == False or len(bpy.data.scenes) == 1: 
                for NumberScene in bpy.data.scenes:     #va créer dynamiquement bpy.data.scenes[x].RenderTrue et créer une checkbox 
                    row=box.row()
                    row.prop(NumberScene, 'RenderTrue', text=NumberScene.name) 
            else:
                row=box.row()
                toPrint = (bpy.data.scenes[0].name[:-3]+'...')
                if bpy.data.scenes[0].RenderTrue  == True:
                    row.label(str(toPrint), icon='CHECKBOX_HLT') 
                else:
                    row.label(str(toPrint), icon='CHECKBOX_DEHLT') 

                    
                      
            row=box.row()
            row.alignment = 'RIGHT'
            if maximise_minimase == True or len(bpy.data.scenes) == 1:
                if len(bpy.data.scenes) == 1:
                    row.enabled = False
                else:
                    row.enabled = True    
                row.operator("max_min.sceneprop",icon='TRIA_DOWN',text='')
            else:
                row.operator("max_min.sceneprop",icon='TRIA_UP',text='')        
        
        if preferences.tool_other_shortcut == True:
            layout.label('Other shortcut')
            box = layout.box()
            
            box.operator("object.constraint_add",text='Add Constraint',icon='CONSTRAINT')  
            box.operator("object.modifier_add", text='Add Modifier',icon='MODIFIER')  
            try:
                bpy.context.active_object.show_wire                 #essai de voir si l'objet à les option show_wire et double_sided
                bpy.context.active_object.data.show_double_sided
            except:
                pass
            else:    
                box.prop(bpy.context.active_object,'show_wire',text='Show Wire')    #affiche le show_wire et double_sided
                box.prop(bpy.context.object.data,'show_double_sided',text='Double sided') 
                box.prop(bpy.context.object, 'show_all_edges',text='show all edges') 
            try:
                bpy.context.active_object.active_material   #test si il y a un objet actif
            except:
                box.label(text='No active object', icon='ERROR')    #affiche erreur
            else:      
                    
                if bpy.context.active_object.active_material == None:   #sinon regarde si l'objet à un materiel
                    if bpy.context.active_object.type == 'MESH':    #si objet n'a pas de materiel check si c'est un mesh
                        box.label(text='No active material on this mesh', icon='ERROR') # -> l'objet activ est un mesh sans texture
                        box = box.row(align=True)
                        box.operator('add.slot_material', text='Add New Mat',icon='ZOOMIN')
                    else:
                        box.label(text='Active object is {0} not mesh'.format(bpy.context.active_object.type.title()), icon='ERROR')  # -> l'objet actif n'est pas un mesh   
                else:                       
                    row = box.row(align=True)    #le row permet de 'coller les 2 boutons  

                    row.prop(bpy.context.active_object,'active_material',text='Active Material')
                    row.operator('add.slot_material', text='',icon='ZOOMIN')
                    box.prop(bpy.context.object.active_material,'diffuse_color', text='Color')            
        
        
class FileFormatButton(bpy.types.Operator):
    bl_idname = "file.format"
    bl_label = "Change all scene format file"
    bl_description='Change all scene format file with the active File Format of the liste below'
 
    def execute(self, context):
        active_scn = bpy.context.scene
        fileFormat=active_scn.FormatFile    #récupère la valeur de l'enum


        for i in range (0,len(bpy.data.scenes)):    #va passer dans toutes les scenes
            
            bpy.data.scenes[i].render.resolution_percentage = 100    #met le rendu à 100%
            FormatData = bpy.context.scene.FormatFile
            FileFormat = FormatData.rpartition(' ')[0]
            ResolutionX=FormatData.rpartition(FileFormat+' ')[2].rpartition('*')[0]
            ResolutionY=FormatData.rpartition(FileFormat+' ')[2].rpartition('*')[2]
                
            bpy.data.scenes[i].render.resolution_x = int(ResolutionX)
            bpy.data.scenes[i].render.resolution_y = int(ResolutionY)
            bpy.data.scenes[i].render.image_settings.file_format =FileFormat            
    
        return{'FINISHED'}   
    
class FileFormatAdd(bpy.types.Operator):
    bl_idname = "add.format"
    bl_label = "Add a format data"
    bl_description='Remove the current format data from the file format list'
 
    def execute(self, context):
        
        render = bpy.context.scene.render
        
        CurrentFormatFile = str(render.image_settings.file_format)+" "+str(render.resolution_x)+'*'+str(render.resolution_y)
        scn = bpy.data.scenes[0]
        global FormatItem
        FormatItem.append((CurrentFormatFile,CurrentFormatFile,CurrentFormatFile))  
        bpy.types.Scene.FormatFile = bpy.props.EnumProperty(items=FormatItem)
         
        return{'FINISHED'}   
        
class FileFormatRemove(bpy.types.Operator):
    bl_idname = "remove.format"
    bl_label = "Remove current format data"
    bl_description = 'Remove the current format data from the file format list'
 
    def execute(self, context): 
        
        active_scn = bpy.context.scene
        
        global FormatItem
        
        if len(FormatItem)<=1:
            self.report({'ERROR'},"Cannot remove last format item")      
        else:
            for format in FormatItem:
                if format[0] == active_scn.FormatFile:
                    
                    FormatItem.remove((format))
                    break

        bpy.types.Scene.FormatFile = bpy.props.EnumProperty(items=FormatItem)
        active_scn.FormatFile=FormatItem[0][0]

          
        
        return{'FINISHED'}            

 
class CleanMaterialButton(bpy.types.Operator):
    bl_idname = "clean.material"
    bl_label = "Clean material"
    bl_description = 'Clean double material ex: Mat.001, Mat.002'
 
    def execute(self, context):      
    
        exception = bpy.context.scene.ExceptionMaterials 
        
        for obj in bpy.data.objects:        #pour tous les objets
            for slt in obj.material_slots:  #pour touts les materiaux de la scene
                part = slt.name.rpartition('.') #'défragmente' le nom du materiel selectonner 
                
                if part[0] not in (exception) and part[2] not in (exception) and slt.name not in (exception):   #si les textures n'ont pas le nom de l'exception               
                                
                    for i in range (0,11):
                        index=str(10-i)
                        realindex='.'+'0'*(3-len(index))+str(index)
                        try:
                            slt.material=bpy.data.materials[part[0]]  #va changer la texture des objets si une texture avec un index plus petit est trouver
                        except:
                            try:
                                slt.material=bpy.data.materials[part[0]+realindex] 
                            except:
                                continue    

        return{'FINISHED'}
      
class AllSceneRenderButton(bpy.types.Operator): #fait un rendu de toutes les scenes
    bl_idname = "allscene.render"
    bl_label = "All scene render"
    bl_description = 'Do a render of all scene'
    
    def execute(self, context):   
        global stop,checked_render 
        checked_render = False
        stop = False   
        bpy.context.screen.scene = bpy.data.scenes[0]
        bpy.ops.view3d.render_and_execute()
              
        return{'FINISHED'}  
    
def start_new_render(returned_scene):
    global stop
    
    stop = True

class VIEW3D_OT_render_and_execute(bpy.types.Operator):
    """Render and Execute"""
    bl_idname = 'view3d.render_and_execute'
    bl_label = 'Render and Execute'
    bl_options = {'REGISTER'}

    prev_stat = None
    timer = None

    def modal(self, context, event):
        
        H = bpy.app.handlers.render_complete
        if start_new_render not in H: H.append(start_new_render) 
        
        global stop,checked_render
        if event.type == 'TIMER' and stop == True:
            stop = False

            print("Render finished.") # POST-RENDER CODE HERE
            if bpy.context.scene == bpy.data.scenes[len(bpy.data.scenes)-1]:
                pass
            else:
                for i in range (0, len(bpy.data.scenes)):
                        
                    if bpy.context.scene == bpy.data.scenes[i]:
                        bpy.context.screen.scene = bpy.data.scenes[i+1]
                        break
                
                bpy.ops.view3d.render_and_execute()
                                     
            #checked_render = False
            return {'FINISHED'} #permet de savoir si le rendu est fini

        return {'PASS_THROUGH'}

    def execute(self, context):
        
        wm = context.window_manager
        wm.modal_handler_add(self)
        self.timer = wm.event_timer_add(2.0, context.window)
        global checked_render
        if bpy.context.scene.camera == None or \
            (checked_render == True and bpy.context.scene.RenderTrue == False):
            global stop
            stop = True
        else:
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True)

        return {'RUNNING_MODAL'}       
    
class CheckedSceneRenderButton(bpy.types.Operator): #fait un rendu des scenes selectionner par la check box
    bl_idname = "checkedscene.render"
    bl_label = "Checked scene render"
    bl_description = 'Do a render of all checked scene'
 
    def execute(self, context):      

        global stop, checked_render
        checked_render = True
        stop = False   
        bpy.context.screen.scene = bpy.data.scenes[0]
        bpy.ops.view3d.render_and_execute()            
          
        return{'FINISHED'}        
			
    
class AddException(bpy.types.Operator):
    bl_idname = "add.exception"
    bl_label = "Add exception material"
    bl_description = 'add an exeption material for the clean material'
 
    def execute(self, context):   
        
        global Exception_materials
        
        Exception_materials.append((bpy.context.scene.MaterialException,bpy.context.scene.MaterialException,bpy.context.scene.MaterialException))
        bpy.types.Scene.ExceptionMaterials = bpy.props.EnumProperty(items=Exception_materials,options={'ENUM_FLAG'})
        
           


        return{'FINISHED'}  
    
class RemoveException(bpy.types.Operator):
    bl_idname = "remove.exception"
    bl_label = "Remove exception material"
    bl_description = 'remove an exeption material for the clean material'
 
    def execute(self, context):   
        
        global Exception_materials
        
        try:
            Exception_materials.remove((bpy.context.scene.MaterialException,bpy.context.scene.MaterialException,bpy.context.scene.MaterialException))
        except:
             self.report({'ERROR'},('No exception material named : '+ str(bpy.context.scene.MaterialException)))        
        bpy.types.Scene.ExceptionMaterials = bpy.props.EnumProperty(items=Exception_materials,options={'ENUM_FLAG'})
        
      

        return{'FINISHED'}     
     
class add_slot_material(bpy.types.Operator): 
    bl_idname = "add.slot_material"
    bl_label = "add slot and material"
    bl_description = 'create a new material and assign it to the active object'
 
    def execute(self, context): 
        
        mat_old =[] #materiaux avant l'appel de la fonction
        mat_new=[]  #materiaux après l'appel de la fonction
        
        for mat in bpy.data.materials:
            mat_old.append(mat.name)      #rempli mat_old
                
        bpy.ops.material.new()      #ajoute le nouveau materiel
        
        for mat in bpy.data.materials:
            mat_new.append(mat.name)  #rempli mat_new
        
            
        for old in mat_old: 
            for new in range (0,len(mat_new)):
                if old == mat_new[new]:
                     mat_new[new] ='concordance'    #check les deux tableaux trouve le nouveaux materiel
                                                    #remplace les materiaux deja existant par 'concordance' dans le tableau
        
        for new in mat_new:
            if new != 'concordance':
                bpy.context.active_object.active_material=bpy.data.materials[new] #va assigner le seul materiel pas à double au mesh actif         


        return{'FINISHED'}     
    
class maximise_minimise_Scene(bpy.types.Operator): 
    bl_idname = "max_min.sceneprop"
    bl_label = "Max or min the list of scene"
    bl_description = 'Maximise or minimise the list of scene'
 
    def execute(self, context): 
        global maximise_minimase
        maximise_minimase = not(maximise_minimase)
        return{'FINISHED'}  
               
class maximise_minimise_Mat(bpy.types.Operator): 
    bl_idname = "max_min.matprop"
    bl_label = "Max or min the list of scene"
    bl_description = 'Maximise or minimise the list of object'
 
    def execute(self, context): 
        global maximise_minimase_Mat
        maximise_minimase_Mat = not(maximise_minimase_Mat)
        return{'FINISHED'}                 
        
class full_copy_material_correction(bpy.types.Operator): 
    bl_idname = "full_copy.mat_corr"
    bl_label = "Full Copy Mat Correction"
    bl_description = 'Do a full copy of the scene but re-take existing material'
 
    def execute(self, context): 

        material_all=check_obj_mat()
        bpy.ops.scene.new(type='FULL_COPY')
        replace_obj_mat(material_all)

        return{'FINISHED'}   
    
class clean_font(bpy.types.Operator): 
    bl_idname = "font.clean"
    bl_label = "Clean all font"
    bl_description = 'Replace ALL font with the one selected'
 
    def execute(self, context): 
        for obj in bpy.data.objects:
            if obj.type=='FONT':
                obj.data.font=bpy.data.fonts[str(bpy.context.scene.AllFont)]
                obj.data.font_bold=bpy.data.fonts[str(bpy.context.scene.AllFont)]
                obj.data.font_bold_italic=bpy.data.fonts[str(bpy.context.scene.AllFont)]
                obj.data.font_italic=bpy.data.fonts[str(bpy.context.scene.AllFont)]



        return{'FINISHED'}   
    
class clean_font(bpy.types.Operator): 
    bl_idname = "render.changepath"
    bl_label = "Change render path"
    bl_description = 'Change the render file path'
 
    def execute(self, context): 
        
        for scn in bpy.data.scenes:    
            file_name=scn.render.filepath.rpartition('\\')[2]
            scn.render.filepath = bpy.context.scene.NewRenderPath+file_name


        return{'FINISHED'}    
class renderpathadd(bpy.types.Operator): 
    bl_idname = "to_render_path.add"
    bl_label = "Add to path"
    bl_description = 'Add text above to render path'
 
    def execute(self, context): 
        
        not_added = []
        
        for scn in bpy.data.scenes:    
            if scn.render.filepath.find(bpy.context.scene.AddRemoveRenderPath) == -1:
                scn.render.filepath = scn.render.filepath +bpy.context.scene.AddRemoveRenderPath
            else:
                not_added.append(scn.name)
        if not_added != []:
            self.report({'ERROR'},('Scenes : '+str(not_added)+' already have'+ bpy.context.scene.AddRemoveRenderPath+' in its path'))        


        return{'FINISHED'} 
       
class renderpathremove(bpy.types.Operator): 
    bl_idname = "to_render_path.remove"
    bl_label = "Remove to path"
    bl_description = 'Remove text above from render path'
 
    def execute(self, context): 
        
        for scn in bpy.data.scenes:    
            file_name=scn.render.filepath.rpartition('\\')[2]
            file_name=file_name.replace(bpy.context.scene.AddRemoveRenderPath,'')
            scn.render.filepath = scn.render.filepath.rpartition('\\')[0]+scn.render.filepath.rpartition('\\')[1]+file_name


        return{'FINISHED'}     
    
class disable_anim(bpy.types.Operator): 
    bl_idname = "animation.disable"
    bl_label = "Disable animation"
    bl_description = 'Disable animation. If animation start it will be automatically stopped'
 
    def execute(self, context): 
        
        def stop_anim(empty):
            bpy.ops.screen.animation_cancel()
        
        bpy.app.handlers.frame_change_pre.append(stop_anim)   
        global animation_state
        
        animation_state = False
        
        self.report({'WARNING'},"Animation is now disabled")    
        
        return{'FINISHED'}  
    
class disable_anim(bpy.types.Operator): 
    bl_idname = "animation.enable"
    bl_label = "Re-enable animation"
    bl_description = 'Re-enable animation.'
 
    def execute(self, context): 
        
        for frame_change_pre_item in bpy.app.handlers.frame_change_pre:
            if frame_change_pre_item.__name__=='stop_anim':
                bpy.app.handlers.frame_change_pre.remove(frame_change_pre_item)    
                self.report({'INFO'},"Animation is now re-enabled") 
        
        global animation_state
        
        animation_state = True
        
        
               
        return{'FINISHED'}                   
            
def register(): #fonction de registration
    
    bpy.utils.register_class(Tool_KitPreferences)
	
    def AllFont(self,context):
        all_font=[]
        for font in bpy.data.fonts:
            all_font.append((font.name,str(str(font.users)+' '+str(font.name)),font.name))
        return all_font
           
    bpy.utils.register_module(__name__) #registre les classes
    bpy.types.Scene.RenderTrue = bpy.props.BoolProperty(default=True)   #initialise scene.RenderTrue
    bpy.types.Scene.MaterialException = bpy.props.StringProperty(default='Material.001')    #initialise material.MaterialException
    bpy.types.Scene.NewRenderPath = bpy.props.StringProperty(default='C:',subtype='DIR_PATH')  
    bpy.types.Scene.AddRemoveRenderPath = bpy.props.StringProperty(default='High_resolution')  
    bpy.types.Scene.FormatFile = bpy.props.EnumProperty(items=FormatItem, default='H264 1440*1080')
    bpy.types.Scene.ExceptionMaterials = bpy.props.EnumProperty(items=Exception_materials,options={'ENUM_FLAG'})
    bpy.types.Scene.AllFont = bpy.props.EnumProperty(items=AllFont)
 
def unregister():   #fonction de dé-registration
    bpy.utils.unregister_module(__name__)   
    
 
if __name__ == "__main__": #
    register()
    