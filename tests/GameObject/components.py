"""
Components on a GameObject, and how often Core.run calls their Update. Headless, prints PASS/FAIL per check
and exits with 1 when one fails.

    cd .. && PYTHONPATH=. python bereshit/tests/GameObject/components.py
"""
import sys
from pathlib import Path

# make the `bereshit` package importable when running this file directly
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from bereshit import GameObject, Core, BoxCollider, Rigidbody, Component

failures = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(name)


# 1. an attach inherited from a Python base class is called; the C++ Component's attach is not
class Base(Component):
    def attach(self, parent):
        self.attached_to = parent


class Inherited(Base):
    pass


class Plain(Component):
    pass


obj = GameObject().add_component(Inherited(), Plain())
check("inherited attach is called", getattr(obj.Inherited, "attached_to", None) is obj)
check("a component without attach is added", obj.Plain is not None)

from bereshit.addons.essentials.Servo import ServoControllerKeyboard

body = GameObject().add_component(BoxCollider(), Rigidbody())
controller = ServoControllerKeyboard(GameObject())
body.add_component(controller)
check("ServoControllerKeyboard gets its Rigidbody (attach of ServoController)", getattr(controller, "rb", None) is not None)

# 2. the essentials addon: everything in __all__ exists, and its components can be added
import bereshit.addons.essentials as essentials

missing = [name for name in essentials.__all__ if not hasattr(essentials, name)]
check("essentials.__all__ names exist", not missing, f"missing {missing}" if missing else "")
try:
    GameObject().add_component(essentials.PlayerController(), essentials.debug(None))
    check("PlayerController and debug can be added", True)
except TypeError as error:
    check("PlayerController and debug can be added", False, str(error))


# 3. Core.run calls Update ~30 times a simulated second by default, and every scriptRefreshRate seconds when given
# (tested on Core.script_steps: Core.run with MaxTime ends the whole process through World.Exit)
for tick, rate, expected in ((1 / 60, None, 30), (1 / 120, None, 30), (1 / 1200, None, 30), (1 / 200, 1 / 50, 50),
                             (1 / 60, 1 / 1000, 60)):
    per_second = round(1 / tick) / Core.script_steps(rate, tick)
    check(f"Update rate at tick 1/{round(1 / tick)}, scriptRefreshRate {rate}", abs(per_second - expected) < 1,
          f"{per_second:.1f} per second, expected {expected}")

print(f"\n{len(failures)} failed" if failures else "\nall passed")
sys.exit(1 if failures else 0)
