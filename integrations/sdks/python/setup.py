"""
Setup script para o CWB Hub Python SDK
Melhoria #3 Fase 3 - SDK Python
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cwb-hub-sdk",
    version="1.0.0",
    author="CWB Hub Team + Qodo",
    author_email="contato@cwbhub.com",
    description="SDK Python para integração com o CWB Hub Hybrid AI System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cwb-hub/python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/cwb-hub/python-sdk/issues",
        "Documentation": "https://cwb-hub-sdk.readthedocs.io/",
        "Source Code": "https://github.com/cwb-hub/python-sdk",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-autodoc-typehints>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cwb-hub=cwb_hub_sdk:main",
        ],
    },
    keywords=[
        "cwb-hub",
        "ai",
        "hybrid-ai", 
        "collaboration",
        "sdk",
        "python",
        "async",
        "api-client"
    ],
    include_package_data=True,
    zip_safe=False,
)