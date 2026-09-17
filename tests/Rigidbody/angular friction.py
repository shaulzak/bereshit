from bereshit import Core, Camera, GameObject, Component
from bereshit.addons.essentials import FPS_cam, CamController
from bereshit.bereshitCore import Vector3, BoxCollider, Rigidbody

class debug(Component):
    def __init__(self):
        super(debug, self).__init__()
        self.dt = 0
    # def PhysicsUpdate(self, dt):
    #     self.dt += dt
    #     if abs(self.parent.Rigidbody.angular_velocity.y) < 0.001:
    #         print(self.dt)
u = 0.5

cam = GameObject(position=Vector3(0,0,-3)).add_component(Camera(shading="material preview"), CamController(), FPS_cam())

obj2 = GameObject(position=Vector3(0,0,0)).add_component(BoxCollider(), Rigidbody(angular_velocity=Vector3(0,0,0), velocity=Vector3(1,0,0), friction_coefficient=u), debug())

floor = GameObject(size=Vector3(100,1,100), position=Vector3(0,-1,0)).add_component(BoxCollider(), Rigidbody(isKinematic=True, friction_coefficient=u))

Core.run_max_speed([cam,floor, obj2], tick=1/12000, Render=True)

