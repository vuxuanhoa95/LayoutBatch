# Copyright (C) 2019, 2020 David Cattermole.
#
# This file is part of dcCameraInferno.
#
# dcCameraInferno is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# dcCameraInferno is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with dcCameraInferno.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Tools to use Camera Inferno.
"""

import pymel.core as pm


def load_plugins():
    pm.loadPlugin("dcCameraInfernoExtend", quiet=True)


def create_node(cam_tfm):
    # Create Node
    tfm = pm.createNode("transform", name="cameraInferno1", parent=cam_tfm)
    node = pm.createNode("dcCameraInfernoExtend", parent=tfm)

    # Make non-selectable.
    pm.setAttr(tfm + ".template", 1)

    # Create a default attributes
    pm.setAttr(node + ".maskAspectRatio", 1.7777)
    pm.setAttr(node + ".maskEnable", 0)
    pm.setAttr(node + ".textSize", 3.5)

    pm.setAttr(node + ".field[0].fieldType", 7)
    pm.setAttr(node + ".field[0].fieldLineWidth", 0.25)
    pm.setAttr(node + ".field[0].fieldLineStyle", 1)
    pm.setAttr(node + ".field[0].fieldLineAlpha", 0.25)

    pm.setAttr(node + ".field[0].fieldTextAlign", 4)
    pm.setAttr(node + ".field[0].fieldTextBold", 1)
    pm.setAttr(node + ".field[0].fieldTextSize", 2)
    pm.setAttr(node + ".field[0].fieldTextValue", r"Reuse Previz Mocap", type="string")

    pm.setAttr(node + ".field[1].fieldType", 1)
    pm.setAttr(node + ".field[1].fieldTextAlign", 1)
    pm.setAttr(node + ".field[1].fieldPositionAX", -0.6)
    pm.setAttr(node + ".field[1].fieldPositionAY", -0.96)
    pm.setAttr(node + ".field[1].fieldTextValue", r"spd {camera_speed_m_per_sec:.02f} m/s", type="string")

    return tfm, node

def get_cam_from_shot(shot):
    cam = pm.PyNode(pm.shot(shot, q=True, cc=True))
    if isinstance(cam, pm.nt.Camera):
        shape = cam
        transform = pm.listRelatives(shape, p=True, type='transform')[0]

    elif isinstance(cam, pm.nt.Transform):
        shape = cam.getShape()
        transform = cam

    else:
        return None, None

    return transform, shape

def main():
    load_plugins()

    # Create node from selection.
    sel_shot = pm.ls(selection=True, long=True, type="shot") or []
    sel = pm.ls(selection=True, long=True, type="transform") or []

    cam_tfms = []

    if len(sel_shot) == 0:
        print('No shot selected, adding tattoo node for selected camera')
        if len(sel) == 0:
            print('No camera selected, creating new camera with tattoo node')
            cam_tfm = pm.createNode(
                "transform", name="camera1")
            cam_shp = pm.createNode(
                "camera", name="cameraShape1", parent=cam_tfm)
            cam_tfms.append(cam_tfm)

        else:
            cam_tfms = [s for s in sel if isinstance(s.getShape(), pm.nt.Camera)]

    else:
        for s in sel_shot:
            cam_tfm, _ = get_cam_from_shot(s)
            cam_tfms.append(cam_tfm)

    for c in cam_tfms:
        tattoo_node = None
        for t in pm.listRelatives(c, ad=True, type='transform'):
            s = t.getShape()
            
            if not s:
                continue
            
            if s.type() == 'dcCameraInfernoExtend':
                print('Already added tattoo node', t)
                tattoo_node = t
                break
        
        if not tattoo_node:
            print('Adding tattoo node for', c)
            _, hud_node = create_node(c)
            pm.select(hud_node, replace=True)