from setuptools import find_packages, setup

package_name = 'gr_sequence'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='polkky',
    maintainer_email='polkky@todo.todo',
    description='Mediapipe based ROS2 gesture sequence recognition',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'sequence_node = gr_sequence.gesture_sequence:main'
        ],
    },
)
