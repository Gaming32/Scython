from setuptools import setup

with open('README.md', 'r') as fp:
    long_description = fp.read()


setup(
    name = 'Scython',
    version = '0.1.0',
    description = 'A C-like alternative syntax parser/front-end for Python',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    author = 'Josiah (Gaming32) Glosson',
    author_email = 'gaming32i64@gmail.com',
    url = 'https://github.com/Gaming32/Scython',
    packages = ['scy'],
    license = 'License :: OSI Approved :: MIT License',
    entry_points = {
        'console_scripts': [
            'scy=scy.__main__:main',
        ],
    },
)
