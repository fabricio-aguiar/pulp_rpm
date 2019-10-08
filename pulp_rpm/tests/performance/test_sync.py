# coding=utf-8
"""Tests that sync rpm plugin repositories."""
import unittest

from pulp_smash import api, config
from pulp_smash.pulp3.constants import REPO_PATH
from pulp_smash.pulp3.utils import (
    delete_orphans,
    gen_repo,
    get_added_content_summary,
    get_content,
    get_content_summary,
    sync,
)

from pulp_rpm.tests.functional.constants import (
    RPM_KICKSTART_CONTENT_NAME,
    RPM_KICKSTART_FIXTURE_SUMMARY,
    RPM_KICKSTART_FIXTURE_URL,
    RPM_REMOTE_PATH,
    CENTOS7_URL,
    CENTOS8_APPSTREAM_URL,
    CENTOS8_BASEOS_URL,
)
from pulp_rpm.tests.functional.utils import gen_rpm_remote
from pulp_rpm.tests.functional.utils import set_up_module as setUpModule  # noqa:F401


class KickstartSyncTestCase(unittest.TestCase):
    """Sync repositories with the rpm plugin."""

    @classmethod
    def setUpClass(cls):
        """Create class-wide variables."""
        cls.cfg = config.get_config()
        cls.client = api.Client(cls.cfg, api.json_handler)

        delete_orphans(cls.cfg)

    def rpm_sync(self, url=RPM_KICKSTART_FIXTURE_URL, policy='on_demand'):
        """Sync repositories with the rpm plugin.

        This test targets the following issue:
        `Pulp #5506 <https://pulp.plan.io/issues/5506>`_.

        In order to sync a repository a remote has to be associated within
        this repository. When a repository is created this version field is set
        as None. After a sync the repository version is updated.

        Do the following:

        1. Create a repository and a remote.
        2. Assert that repository version is None.
        3. Sync the remote.
        4. Assert that repository version is not None.
        5. Assert that distribution_tree units were added and are present in the repo.
        """
        delete_orphans(self.cfg)
        repo = self.client.post(REPO_PATH, gen_repo())
        self.addCleanup(self.client.delete, repo['_href'])

        # Create a remote with the standard test fixture url.
        body = gen_rpm_remote(url=url, policy=policy)
        remote = self.client.post(RPM_REMOTE_PATH, body)
        self.addCleanup(self.client.delete, remote['_href'])

        # Sync the repository.
        self.assertIsNone(repo['_latest_version_href'])
        sync(self.cfg, remote, repo)
        repo = self.client.get(repo['_href'])
        for kickstart_content in get_content(repo)[RPM_KICKSTART_CONTENT_NAME]:
            self.addCleanup(self.client.delete, kickstart_content['_href'])

        # Check that we have the correct content counts.
        self.assertIsNotNone(repo['_latest_version_href'])

        self.assertIn(
            list(RPM_KICKSTART_FIXTURE_SUMMARY.items())[0],
            get_content_summary(repo).items(),
        )
        self.assertIn(
            list(RPM_KICKSTART_FIXTURE_SUMMARY.items())[0],
            get_added_content_summary(repo).items(),
        )

    def test_centos7_on_demand(self):
        """Kickstart Sync CentOS 7."""
        self.rpm_sync(url=CENTOS7_URL)

    def test_centos8_baseos_on_demand(self):
        """Kickstart Sync CentOS 8 BaseOS."""
        self.rpm_sync(url=CENTOS8_BASEOS_URL)

    def test_centos8_appstream_on_demand(self):
        """Kickstart Sync CentOS 8 AppStream."""
        self.rpm_sync(url=CENTOS8_APPSTREAM_URL)
