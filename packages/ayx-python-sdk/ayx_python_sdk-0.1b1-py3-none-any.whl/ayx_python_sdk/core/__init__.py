# Copyright (C) 2021 Alteryx, Inc. All rights reserved.
#
# Licensed under the ALTERYX SDK AND API LICENSE AGREEMENT;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.alteryx.com/alteryx-sdk-and-api-license-agreement
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Alteryx Python SDK: Core classes and interfaces."""

from .constants import NULL_VALUE_PLACEHOLDER
from .environment_base import EnvironmentBase, UpdateMode
from .field import Field, FieldType
from .input_anchor_base import InputAnchorBase
from .input_connection_base import InputConnectionBase
from .io_base import IoBase
from .metadata import Metadata
from .output_anchor_base import OutputAnchorBase
from .plugin import Plugin
from .provider_base import ProviderBase
from .record_packet import RecordPacket
from .record_packet_base import RecordPacketBase
from .register_plugin import register_plugin

__all__ = [
    "EnvironmentBase",
    "UpdateMode",
    "Field",
    "FieldType",
    "InputAnchorBase",
    "InputConnectionBase",
    "IoBase",
    "Metadata",
    "OutputAnchorBase",
    "Record",
    "RecordPacket",
    "RecordPacketBase",
    "Plugin",
    "ProviderBase",
    "register_plugin",
    "ProviderBase",
    "NULL_VALUE_PLACEHOLDER",
]
