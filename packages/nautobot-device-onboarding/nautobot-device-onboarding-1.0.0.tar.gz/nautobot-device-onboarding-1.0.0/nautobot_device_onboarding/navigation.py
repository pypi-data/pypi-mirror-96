"""Plugin additions to the Nautobot navigation menu.

(c) 2020-2021 Network To Code
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from nautobot.extras.plugins import PluginMenuButton, PluginMenuItem
from nautobot.utilities.choices import ButtonColorChoices


menu_items = (
    PluginMenuItem(
        link="plugins:nautobot_device_onboarding:onboardingtask_list",
        link_text="Onboarding Tasks",
        permissions=["nautobot_device_onboarding.view_onboardingtask"],
        buttons=(
            PluginMenuButton(
                link="plugins:nautobot_device_onboarding:onboardingtask_add",
                title="Onboard",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["nautobot_device_onboarding.add_onboardingtask"],
            ),
            PluginMenuButton(
                link="plugins:nautobot_device_onboarding:onboardingtask_import",
                title="Bulk Onboard",
                icon_class="mdi mdi-database-import-outline",
                color=ButtonColorChoices.BLUE,
                permissions=["nautobot_device_onboarding.add_onboardingtask"],
            ),
        ),
    ),
)
