from setuptools import setup, find_packages

setup(
	name='tgsafebox',
	version='1.0.2',
	py_modules=['main', 'tools.fsm', 'tools.crypto', 'tools.console', 'tools.tg'],
	packages=find_packages(),
	include_package_data=True,
	install_requires=[
		'tgcrypto',
		'pyrogram',
		'pycryptodome'
	],
	entry_points={
		'console_scripts': [
			'tgsafebox=main:main',
		],
	},
	author='Syn3xuS',
	description='A utility for securely storing files in Telegram',
	url='https://github.com/Syn3xuS/TgSafeBox',
	python_requires='>=3.11.9',
)
