from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native


class CriteriaTriggers(NativeClass):
    NAME = "net/minecraft/advancements/CriteriaTriggers"

    @native("func_192118_a",
            "(Lnet/minecraft/advancements/ICriterionTrigger;)Lnet/minecraft/advancements/ICriterionTrigger;", static=True)
    def func_192118_a(self, instance):
        return instance


class ICriterionTrigger(NativeClass):
    NAME = "net/minecraft/advancements/ICriterionTrigger"

