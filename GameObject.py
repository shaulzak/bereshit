import copy

from bereshit import Material, MeshRander
from bereshit.bereshitCore import GameObject, Joint


class GameObject(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Keeps original Python component objects alive
        self._components = {}
        self._py_components = []


        self.add_component(Material.Material())
        self.add_component(MeshRander.MeshRander(shape="box"))

    def add_component(self, *components):
        for component in components:
            self._add_component(component)
        return self

    def _add_component(self, component):
        name= None
        if "attach" in type(component).__dict__:
            name = component.attach(self)
        super().add_component(component)

        # Save by component name, for cam.Camera
        if not name:
            self._components[component.__class__.__name__] = component
            if component.is_python_component():
                self._py_components.append(component)
        else:
            self._components[name] = component
            if component.is_python_component():
                self._py_components.append(component)

        return self

    def __getattr__(self, name):
        if "_components" in self.__dict__:
            if name in self._components:
                return self._components[name]

        raise AttributeError(name)

    def __deepcopy__(self, memo):

        # Return the existing copy when this object was already visited.
        if id(self) in memo:
            return memo[id(self)]

        # Joints are added last, once every copied body exists, and held to the copy of their other body.
        # A joint whose other body isn't part of the copy stays on that body.
        joints = []
        obj = self._copy_hierarchy(memo, joints)
        for owner, joint in joints:
            body = joint.body_b
            joint.body_b = memo.get(id(body), body)
            owner.add_component(joint)
        return obj

    def _copy_hierarchy(self, memo, joints):
        obj = GameObject(
            self.transform.position,
            self.transform.rotation,
            self.transform.size,
            [],
            self.name
        )

        # Register the copy BEFORE recursively copying components or children.
        memo[id(self)] = obj

        for component in self._components.values():
            component_copy = copy.copy(component)

            if isinstance(component_copy, Joint):
                joints.append((obj, component_copy))
            elif component_copy is not None:
                obj.add_component(component_copy)

        for child in self.children:
            if isinstance(child, GameObject):
                child_copy = child._copy_hierarchy(memo, joints)
            else:
                child_copy = copy.deepcopy(child, memo)
            obj.add_child(child_copy)

        return obj
