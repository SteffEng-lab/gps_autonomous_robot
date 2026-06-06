from setuptools import find_packages, setup

package_name = 'robot_sensors'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='radxa',
    maintainer_email='181676543+SteffEng-lab@users.noreply.github.com',
    description='Publish sensor data',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'imu_publisher_node = robot_sensors.imu_publisher:main',
            'gps_publisher_node = robot_sensors.gps_publisher:main'
        ],
    },
)
