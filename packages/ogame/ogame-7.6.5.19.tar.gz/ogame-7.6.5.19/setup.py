from distutils.core import setup

setup(
    name='ogame',
    packages=['ogame'],
    version='7.6.5.19',
    license='MIT',
    description='lib for the popular browsergame ogame',
    author='PapeprPieceCode',
    author_email='marcos.gam@hotmail.com',
    url='https://github.com/PiecePaperCode/pyogame2',
    download_url='https://github.com/alaingilbert/pyogame',
    keywords=['OGame', 'lib', 'for bots', 'bot'],
    install_requires=['requests', 'bs4', 'html5lib'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
)
