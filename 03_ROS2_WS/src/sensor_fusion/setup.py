from setuptools import find_packages, setup

package_name = 'sensor_fusion'

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
    description='Sensor Fusion Algorithm',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'linear_kf_node = sensor_fusion.sensor_fusion_node:main'
        ],
    },
)
