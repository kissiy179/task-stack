import os
import maya.cmds as cmds

def get_relatvie_path_in_maya_project(abs_path):
    pj_path = cmds.workspace(query=True, rootDirectory=True)

    try:
        rel_path = os.path.relpath(abs_path, start=pj_path)

    except:
        rel_path = abs_path

    if rel_path[:2] == '..':
        rel_path = abs_path

    return rel_path.replace(os.sep, os.altsep)

def get_absolute_path_in_maya_project(rel_path):
    if os.path.isabs(rel_path):
        return rel_path

    pj_path = cmds.workspace(query=True, rootDirectory=True)
    abs_path = os.path.join(pj_path, rel_path)
    return abs_path.replace(os.sep, os.altsep)
    
