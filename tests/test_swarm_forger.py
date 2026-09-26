import unittest

from swarm_forger import ProjectInfo, describe_project, get_project_info


class SwarmForgerTests(unittest.TestCase):
    def test_get_project_info_returns_python_metadata(self) -> None:
        self.assertEqual(
            get_project_info(),
            ProjectInfo(
                name="generic-scraper2",
                purpose="Swarm Forger project",
                language="Python",
            ),
        )

    def test_describe_project_mentions_python(self) -> None:
        description = describe_project()

        self.assertIn("Swarm Forger project", description)
        self.assertIn("Python", description)


if __name__ == "__main__":
    unittest.main()
