"""Run the dependency-free OOP checks with: python scripts/verify_oop.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from issues.models import BaseEntity, CriticalIssue, Issue, LowPriorityIssue, Reporter


class ObjectModelChecks(unittest.TestCase):
    def test_abstract_base(self):
        with self.assertRaises(TypeError):
            BaseEntity()

    def test_reporter_serialization_and_validation(self):
        reporter = Reporter(1, 'Alex Kim', 'alex@example.com', 'backend')
        reporter.validate()
        self.assertEqual(reporter.to_dict(), {
            'id': 1, 'name': 'Alex Kim', 'email': 'alex@example.com', 'team': 'backend'
        })

    def test_reporter_invalid_email(self):
        with self.assertRaisesRegex(ValueError, 'Invalid email'):
            Reporter(1, 'Alex', 'wrong', 'backend').validate()

    def test_valid_critical_issue_response_fields(self):
        issue = CriticalIssue(1, 'Login button not working on mobile',
                              'Users on iOS 17 cannot tap the login button',
                              'open', 'critical', 1)
        issue.validate()
        response = {**issue.to_dict(), 'message': issue.describe()}
        self.assertEqual(response['message'],
                         '[URGENT] Login button not working on mobile — needs immediate attention')
        self.assertEqual(response['reporter_id'], 1)

    def test_blank_title_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Title cannot be empty'):
            Issue(2, '', 'desc', 'open', 'high', 1).validate()

    def test_status_and_priority_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Invalid status'):
            Issue(2, 'Title', 'desc', 'pending', 'high', 1).validate()
        with self.assertRaisesRegex(ValueError, 'Invalid priority'):
            Issue(2, 'Title', 'desc', 'open', 'invalid', 1).validate()

    def test_method_overrides(self):
        self.assertEqual(LowPriorityIssue(3, 'Cleanup', '', 'open', 'low', 1).describe(),
                         'Cleanup — low priority, handle when free')
        self.assertEqual(Issue(3, 'Cleanup', '', 'open', 'medium', 1).describe(),
                         'Cleanup [medium]')


if __name__ == '__main__':
    unittest.main(verbosity=2)
