# Copyright 2019 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module for the `PushRosNamespace` action."""

from typing import List

from launch import Action
from launch import Substitution
from launch.frontend import Entity
from launch.frontend import Parser
from launch.launch_context import LaunchContext
from launch.some_substitutions_type import SomeSubstitutionsType
from launch.substitutions import SubstitutionFailure
from launch.utilities import normalize_to_list_of_substitutions
from launch.utilities import perform_substitutions

from rclpy.validate_namespace import validate_namespace


class PushRosNamespace(Action):
    """
    Action that pushes the ros namespace.

    It's automatically popped when used inside a scoped `GroupAction`.
    There's not other way of popping it.
    """

    def __init__(
        self,
        namespace: SomeSubstitutionsType,
        **kwargs
    ) -> None:
        """Constructor."""
        super().__init__(**kwargs)
        self.__namespace = normalize_to_list_of_substitutions(namespace)

    @classmethod
    def parse(cls, entity: Entity, parser: Parser):
        """Return `SetLaunchConfiguration` action and kwargs for constructing it."""
        _, kwargs = super().parse(entity, parser)
        kwargs['namespace'] = parser.parse_substitution(entity.get_attr('namespace'))
        return cls, kwargs

    @property
    def namespace(self) -> List[Substitution]:
        """Getter for self.__name."""
        return self.__namespace

    def execute(self, context: LaunchContext):
        """Execute the action."""
        pushed_namespace = perform_substitutions(context, self.namespace)
        previous_namespace = context.launch_configurations.get('ros_namespace', '')
        namespace = pushed_namespace
        if not pushed_namespace.startswith('/'):
            namespace = previous_namespace + '/' + pushed_namespace
        namespace = namespace.rstrip('/')
        if namespace != '':
            try:
                validate_namespace(namespace)
            except Exception:
                raise SubstitutionFailure(
                    'The resulting namespace is invalid:'
                    " [previous_namespace='{}', pushed_namespace='{}']".format(
                        previous_namespace, pushed_namespace
                    )
                )
        context.launch_configurations['ros_namespace'] = namespace
