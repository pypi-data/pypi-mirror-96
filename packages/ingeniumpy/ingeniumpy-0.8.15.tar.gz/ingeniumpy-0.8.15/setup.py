import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

# Version notes:
# 0.5.0-0.6.0 -> GijonIN OLD
# 0.6.1 -> GijonIN
# 0.7.0 -> CalidadAire
# 0.7.{1,2} -> CalidadAire cambios
# 0.8.0 -> 6LowPan
# 0.8.6 -> Valores 87, 88, 89 de Sock
# 0.8.9 -> Updated proxy dependencies
# 0.8.10 -> Updated naming when id is repeated
# 0.8.14 -> No poll when no devices
# 0.8.15 -> Catch timeout exception

setuptools.setup(
    name="ingeniumpy",
    version="0.8.15",
    author="Daniel Garcia",
    author_email="dgarcia@ingeniumsl.com",
    description="Ingenium API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/ingeniumpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiohttp>=3.6,<4.0",
    ],
    package_data={"ingeniumpy": ["bin/proxy*"]},
)
