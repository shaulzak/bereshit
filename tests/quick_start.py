import sys
from pathlib import Path

# make the `bereshit` package importable when running this file directly
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bereshit import GameObject, Vector3, Core, Camera, BoxCollider, Rigidbody
from bereshit.addons.essentials import FPS_cam, CamController

cam = GameObject(position=Vector3(0, 0, -8)).add_component(Camera(), CamController(), FPS_cam())

floor = GameObject(size=Vector3(10,1,10), position=Vector3(0,-1,0)).add_component(BoxCollider(), Rigidbody(isKinematic=True))

obj2 = GameObject(position=Vector3(0,2,0)).add_component(BoxCollider(), Rigidbody())

Core.run([cam, floor, obj2])
