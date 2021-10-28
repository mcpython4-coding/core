import typing
from abc import ABC

from pyglet.window import mouse

from .AbstractFluidContainer import AbstractFluidContainer
from mcpython.common.container.ResourceStack import ItemStack, FluidStack
from mcpython import shared
from mcpython.common.fluid import LavaFluid, WaterFluid


@shared.registry
class BucketItem(AbstractFluidContainer):
    NAME = "minecraft:bucket"

    STACK_SIZE = 16

    @classmethod
    def could_accept(
        cls,
        itemstack: ItemStack,
        fluidstack: FluidStack,
    ) -> bool:
        if fluidstack.amount < 1000: return False
        return fluidstack.fluid.NAME+"_bucket" in shared.registry.get_by_name("minecraft:item")

    @classmethod
    def accept(
        cls,
        itemstack: ItemStack,
        fluidstack: FluidStack,
        insert_parts=True,
    ) -> bool:
        if fluidstack.amount < 1000: return False

        if not insert_parts and fluidstack.amount != 1000: return False

        itemstack.copy_from(ItemStack(fluidstack.fluid.NAME+"_bucket", 1000))
        fluidstack.amount -= 1000
        return True

    def on_player_interact(self, player, block, button: int, modifiers: int, itemstack, previous) -> bool:
        if button != mouse.RIGHT: return False

        from mcpython.common.block.FluidBlock import IFluidBlock

        if isinstance(block, IFluidBlock):
            shared.world.get_active_dimension().remove_block(block)

            bucket = ItemStack(block.NAME+"_bucket")

            if itemstack.amount > 1:
                itemstack.add_amount(-1)
                player.pick_up_item(bucket)
            else:
                itemstack.copy_from(bucket)

            return True

        return False


class FilledBucketItem(AbstractFluidContainer, ABC):
    ASSIGNED_FLUID = None

    STACK_SIZE = 1

    @classmethod
    def get_underlying_fluid_stacks(
            cls, itemstack: ItemStack
    ) -> typing.Iterable[FluidStack]:
        return FluidStack(cls.ASSIGNED_FLUID, amount=1000),

    @classmethod
    def can_provide(
        cls,
        itemstack: ItemStack,
        fluidstack: FluidStack,
    ) -> bool:
        return fluidstack.fluid == cls.ASSIGNED_FLUID and fluidstack.amount >= 1000

    @classmethod
    def provide(
        cls,
        itemstack: ItemStack,
        fluidstack: FluidStack,
        extract_parts=True,
    ) -> bool:
        if fluidstack.amount < 1000: return False
        if not extract_parts and fluidstack.amount != 1000: return False

        itemstack.copy_from(ItemStack("minecraft:bucket"))
        fluidstack.amount -= 1000
        return True

    def on_player_interact(self, player, block, button: int, modifiers: int, itemstack, previous) -> bool:
        if button != mouse.RIGHT:
            return False

        if previous is not None:
            player.dimension.add_block(previous, self.ASSIGNED_FLUID.NAME)
            itemstack.copy_from(ItemStack("minecraft:bucket"))
            return True

        return False


@shared.registry
class WaterBucket(FilledBucketItem):
    NAME = "minecraft:water_bucket"
    ASSIGNED_FLUID = WaterFluid.WaterFluid


@shared.registry
class LavaBucket(FilledBucketItem):
    NAME = "minecraft:lava_bucket"
    ASSIGNED_FLUID = LavaFluid.LavaFluid

