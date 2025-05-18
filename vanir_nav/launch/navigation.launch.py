import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration



def generate_launch_description():
    pkg_share = get_package_share_directory('vanir_nav')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    map_yaml_file = LaunchConfiguration('map',
                default=os.path.join(pkg_share, 'config', 'my_map.yaml'))
    nav2_config_file = LaunchConfiguration('params', 
                    default=os.path.join(pkg_share, 'config', 'nav2_params.yaml'))

    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')]),
        launch_arguments={
            'slam_params_file': os.path.join(pkg_share, 'config', 'mapper_params_online_async.yaml'),
            'use_sim_time': 'true'}.items(),
    )

    nav2_bringup_launch_file = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_nav2_bringup,"launch","bringup_launch.py")),
        launch_arguments={
            "map":map_yaml_file,
            "use_sim_time":use_sim_time,
            "params_file":nav2_config_file
        }.items()
    )

    localization = IncludeLaunchDescription(
    PythonLaunchDescriptionSource([
        os.path.join(
            get_package_share_directory('nav2_bringup'),
            'launch',
            'localization_launch.py'
        )
    ]),
    launch_arguments={
        'map': os.path.join(pkg_share, 'config', 'my_map.yaml'),
        'use_sim_time': 'true'
    }.items()
)
    
    return LaunchDescription([
            DeclareLaunchArgument("map",default_value=map_yaml_file,description="map.yaml file"),
            DeclareLaunchArgument("params_file",default_value=nav2_config_file,description="params for nav2"),
            DeclareLaunchArgument("use_sim_time",default_value=use_sim_time,description="sim_time true or false"),
            localization,
            nav2_bringup_launch_file
        ])