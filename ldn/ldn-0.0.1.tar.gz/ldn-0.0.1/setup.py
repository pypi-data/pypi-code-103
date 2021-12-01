
import setuptools

description = \
	"LDN."

long_description = description

extensions = [
	#setuptools.Extension(name="ldn", source=sources)
]

setuptools.setup(
	name = "ldn",
	version = "0.0.1",
	description = description,
	long_description = long_description,
	author = "Yannik Marchand",
	author_email = "ymarchand@me.com",
	url = "https://github.com/kinnay/Nintendo-LDN",
	license = "GPLv3",
	ext_modules = extensions
)
