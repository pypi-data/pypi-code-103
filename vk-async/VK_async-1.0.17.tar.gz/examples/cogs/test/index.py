from async_vk_lib.cog import Cog

cog = Cog()

class Example_data_class():
    def __init__(self):
        self.text = 'asdasdasd'

cla = Example_data_class()

@cog.command(name = 'asd')
async def test(ctx):
    print(cla.text)


def setup(bot):
    bot.add_cog(cog)
