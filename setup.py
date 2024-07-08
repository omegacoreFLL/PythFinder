from setuptools import setup, find_packages

setup(
    name = 'pythfinder',
    version = '0.0.4.3',
    license = 'MIT',
    author = 'Contraș Adrian',
    author_email = 'omegacoresincai@gmail.com',
    description = 'Motion Planning library designed for FLL teams',
    packages = find_packages(),
    keywords = [
        'motion-planning',
        'mobile-robots',
        'robotics',
        'first-lego-league',
        'first-robotics',
        'fll'
    ],
    install_requires = ['pygame>=2.0.0', 'matplotlib>=3.3.0'],
    include_package_data=True,
)
