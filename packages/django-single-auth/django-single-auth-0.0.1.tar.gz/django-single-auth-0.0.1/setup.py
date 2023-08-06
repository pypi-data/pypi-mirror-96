import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-single-auth",
    version="0.0.1",
    author="Ajit Mourya",
    author_email="ajit@glib.ai",
    description="single auth for all applications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GlibAI/django_authentication",
    packages=setuptools.find_packages(exclude=['django_authentication', 'manage.py']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
