import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='makefilemenu',
    version='0.2.1',
    python_requires='~=3.5',
    author='Isaac To',
    author_email='isaac.to@gmail.com',
    description='Console menu for Makefiles',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/isaacto/makefilemenu',
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "makefilemenu=makefilemenu.__main__:main",
        ]
    },
    package_data={'makefilemenu': ['py.typed']},
    install_requires=[
        'attrs',
        'calf',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
