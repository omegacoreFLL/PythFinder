from setuptools import setup, find_packages

setup(
    name='pythfinder',
    version='0.0.3',
    license='MIT',
    author='Contraș Adrian',
    author_email='omegacoresincai@gmail.com',
    description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
    packages=find_packages(),
    keywords=[
        'motion-planning',
        'mobile-robots',
        'robotics',
        'first-lego-league',
        'first-robotics',
        'fll'
    ],
    install_requires=['']
    
)
