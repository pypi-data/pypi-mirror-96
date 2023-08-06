"""ChoiceSet classes for device onboarding.

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

from nautobot.utilities.choices import ChoiceSet


class OnboardingStatusChoices(ChoiceSet):
    """Valid values for OnboardingTask "status"."""

    STATUS_FAILED = "failed"
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_SUCCEEDED = "succeeded"
    STATUS_SKIPPED = "skipped"

    CHOICES = (
        (STATUS_FAILED, "failed"),
        (STATUS_PENDING, "pending"),
        (STATUS_RUNNING, "running"),
        (STATUS_SUCCEEDED, "succeeded"),
        (STATUS_SKIPPED, "skipped"),
    )


class OnboardingFailChoices(ChoiceSet):
    """Valid values for OnboardingTask "failed reason"."""

    FAIL_LOGIN = "fail-login"
    FAIL_CONFIG = "fail-config"
    FAIL_CONNECT = "fail-connect"
    FAIL_EXECUTE = "fail-execute"
    FAIL_GENERAL = "fail-general"
    FAIL_DNS = "fail-dns"

    CHOICES = (
        (FAIL_LOGIN, "fail-login"),
        (FAIL_CONFIG, "fail-config"),
        (FAIL_CONNECT, "fail-connect"),
        (FAIL_EXECUTE, "fail-execute"),
        (FAIL_GENERAL, "fail-general"),
        (FAIL_DNS, "fail-dns"),
    )
