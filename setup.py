from setuptools import setup, find_packages

setup(
	name='tgsafebox',
	version='1.0.0',
	py_modules=['tg', '__init__', 'crypto', 'fsm', 'main'],
	packages=find_packages(),
	include_package_data=True,
	install_requires=[
		'tgcrypto',
		'pyrogram',
		'cryptography'
	],
	entry_points={
		'console_scripts': [
			'tgsafebox=main:main',
		],
	},
	author='Syn3xuS',
	description='A utility for securely storing files in Telegram',
	url='https://github.com/Syn3xuS/TgSafeBox',
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
	],
	python_requires='>=3.6',
)
