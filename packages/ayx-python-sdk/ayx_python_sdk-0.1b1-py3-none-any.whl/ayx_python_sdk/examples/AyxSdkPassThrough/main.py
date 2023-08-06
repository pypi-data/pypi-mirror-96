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
"""Example pass through tool."""
from ayx_python_sdk.core import (
    InputConnectionBase,
    Plugin,
    ProviderBase,
    register_plugin,
)


class AyxSdkPassThrough(Plugin):
    """A sample Plugin that passes data from an input connection to an output connection."""

    def __init__(self, provider: ProviderBase):
        """Construct the AyxRecordProcessor."""
        self.name = "Pass through"
        self.provider = provider
        self.output_anchor = self.provider.get_output_anchor("Output")

        self.provider.io.info(f"{self.name} tool started")

    def on_input_connection_opened(self, input_connection: InputConnectionBase) -> None:
        """Initialize the Input Connections of this plugin."""
        if input_connection.metadata is None:
            raise RuntimeError("Metadata must be set before setting containers.")

        input_connection.max_packet_size = 1000
        output_metadata = input_connection.metadata.clone()
        self.output_anchor.open(output_metadata)

    def on_record_packet(self, input_connection: InputConnectionBase) -> None:
        """Handle the record packet received through the input connection."""
        packet = input_connection.read()
        self.output_anchor.write(packet)

    def on_complete(self) -> None:
        """Handle for when the plugin is complete."""
        self.provider.io.info(f"{self.name} tool done")


AyxPlugin = register_plugin(AyxSdkPassThrough)
