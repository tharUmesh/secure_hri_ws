from setuptools import find_packages, setup
import glob

package_name = 'hri_secure_nodes'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Install launch files so ros2 launch can find them by package name
        ('share/' + package_name + '/launch',
            glob.glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='HRI Team',
    maintainer_email='student@eng.ruh.ac.lk',
    description='Secure HRI mock nodes for InfoSec course project',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'emotion_node  = hri_secure_nodes.emotion_node:main',
            'gesture_node  = hri_secure_nodes.gesture_node:main',
            'motion_node   = hri_secure_nodes.motion_node:main',
            'context_node  = hri_secure_nodes.context_node:main',
            'fusion_engine = hri_secure_nodes.fusion_engine_node:main',
            'rogue_node    = hri_secure_nodes.rogue_node:main',
        ],
    },
)