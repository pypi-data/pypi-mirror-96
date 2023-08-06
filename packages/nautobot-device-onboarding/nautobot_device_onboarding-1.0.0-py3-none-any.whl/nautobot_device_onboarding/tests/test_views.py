"""Unit tests for nautobot_device_onboarding views.

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
from nautobot.dcim.models import Site
from nautobot.utilities.testing import ViewTestCases

from nautobot_device_onboarding.models import OnboardingTask


class OnboardingTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,  # pylint: disable=no-member
):
    """Test the OnboardingTask views."""

    def _get_base_url(self):
        return "plugins:{}:{}_{{}}".format(self.model._meta.app_label, self.model._meta.model_name)

    model = OnboardingTask

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        """Setup test data."""
        site = Site.objects.create(name="USWEST", slug="uswest")
        OnboardingTask.objects.create(ip_address="10.10.10.10", site=site)
        OnboardingTask.objects.create(ip_address="192.168.1.1", site=site)

        cls.form_data = {
            "site": site.pk,
            "ip_address": "192.0.2.99",
            "port": 22,
            "timeout": 30,
        }

        cls.csv_data = (
            "site,ip_address",
            "uswest,10.10.10.10",
            "uswest,10.10.10.20",
            "uswest,10.10.10.30",
        )
