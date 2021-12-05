
import os
import minimo
import traceback


# mmo = minimo.Application(interface="api")
# return True or False for `init` result
# result = mmo.call("init", name="helloKitty")


# # inst_path = os.path.dirname(__file__)
# inst_path = "/home/philip1134/projects/test/mmo-test/hello_kitty"
# mmo = minimo.Application(
#     interface="api",
#     root_path=inst_path)


# mmo.call("ls")
# # print mmo.call("version")
# # print mmo.call("init", name="hello_kitty")
# print mmo.call("new", cases=["hello", "shithappens/init", "shithappens/delete"])
# # end

inst_path = os.path.join(os.path.dirname(__file__), "dejavu")
mmo = minimo.Application(
    interface="api",
    root_path=inst_path
)
mmo.call(
    "run",
    cases=["bots/hell", "cat/hell"]
)

# end
