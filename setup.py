from setuptools import setup, find_packages

setup(
    name='Pytest-xdist-kubernetes',
    version='0.0.0.0',
    description='Your package description',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Aiden Seo',
    author_email='minwoo3180@gmail.com',
    url='https://github.com/Aidenseo3180/ECE1894-Industry-Project-with-Microsoft',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
        "Development Status :: 1 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.9',
)