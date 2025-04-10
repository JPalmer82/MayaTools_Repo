import importlib
import MayaUtilities
importlib.reload(MayaUtilities)

from MayaUtilities import * # the * imports everything in the file be careful using this
from PySide2.QtWidgets import QPushButton, QVBoxLayout
import maya.cmds as mc

class ProxyRigger:
    def __init__(self):
        self.skin = ""
        self.model = ""
        self.joints = []

    def CreateProxyRigFromSelectedMesh(self):
        mesh = mc.ls(sl = True)[0]
        if not IsMesh(mesh):
            raise TypeError(f"{mesh} is not a mesh! Please select a mesh")
        
        self.model = mesh
        modelShape = mc.listRelatives(self.model, s = True)[0]
        print(f"found mesh {mesh}, and shape {modelShape}")

        skin = GetAllConnectionsIn(modelShape, GetUpperStream, 10, IsSkin)
        if not skin:
            raise Exception(f"{mesh} has no skin! Tool only works with a rigged model")
        
        self.skin = skin[0]

        joints = GetAllConnectionsIn(modelShape, GetUpperStream, 10, IsJoint)
        if not joints:
            raise Exception(f"{mesh} has no joints bound! Tool only works with a rigged model.")
        
        self.joints = joints

        print(f"start build with mesh: {self.model}, skin: {self.skin}, and joints: {self.joints}")

        jointVertMap = self.GenerateJointVertDict()
        segments = []
        controls = []
        for joint, verts in jointVertMap.items():
            print(f"joint {joints} controls {verts} primarily")

    def GenerateJointVertDict(self):
        dict = {}
        for joint in self.joints:
            dict[joint] = []

        verts = mc.ls(f"{self.model}.vtx[*]", fl = True)
        for vert in verts:
            owningJoint = self.GetJointWithMaxInfluence(vert, self.skin)
            dict[owningJoint].append(vert)

        return dict

    def GetJointWithMaxInfluence(self, vert, skin):
        weights = mc.skinPercent(skin, vert, q = True, v = True)
        joints = mc.skinPercent(skin, vert, q = True, t = None)

        maxWeightIndex = 0
        maxWeight = weights[0]

        for i in range(1, len(weights)):
            if weights[i] > maxWeight:
                maxWeight = weights[i]
                maxWeightIndex = i

        return joints[maxWeightIndex]
        

class ProxyRiggerWidget(QMayaWindow):
    def __init__(self):
        super().__init__()
        self.proxyRigger = ProxyRigger()
        self.setWindowTitle("Proxy Rigger")
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        generateProxyRigButton = QPushButton("Generate Proxy Rig")
        self.masterLayout.addWidget(generateProxyRigButton)
        generateProxyRigButton.clicked.connect(self.GenerateProxyRigButtonClicked)

    def GenerateProxyRigButtonClicked(self):
        self.proxyRigger.CreateProxyRigFromSelectedMesh()

    def GetWindowHash(self):
        return "712890f8c1f9b099b91b6e9aa2fcc0830973ff04"

proxyRiggerWidget = ProxyRiggerWidget()
proxyRiggerWidget.show()