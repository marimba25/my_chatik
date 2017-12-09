from setuptools import setup, find_packages


setup(
    name='my_chatik',
    packages=find_packages(),
    package_data={'': ['*.py', '*.ui', '*.jpg', '*.png']},
    version='0.1.1'
)
