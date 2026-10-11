"""Run with: python manage.py test"""
import json
import tempfile
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from .models import BaseEntity, CriticalIssue, Issue, LowPriorityIssue, Reporter


class EntityTests(SimpleTestCase):
    def test_to_dict_and_abstract_base(self):
        self.assertEqual(Reporter(1, 'A', 'a@b.com', 'backend').to_dict()['id'], 1)
        with self.assertRaises(TypeError):
            BaseEntity()

    def test_reporter_validation(self):
        with self.assertRaisesRegex(ValueError, 'Name cannot be empty'):
            Reporter(1, '', 'valid@example.com', 'backend').validate()
        with self.assertRaisesRegex(ValueError, 'Invalid email'):
            Reporter(1, 'Alex', 'not-an-email', 'devops').validate()

    def test_issue_validation(self):
        with self.assertRaisesRegex(ValueError, 'Title cannot be empty'):
            Issue(1, ' ', 'desc', 'open', 'critical', 1).validate()
        with self.assertRaisesRegex(ValueError, 'Invalid status'):
            Issue(1, 'Bug', 'desc', 'pending', 'high', 1).validate()
        with self.assertRaisesRegex(ValueError, 'Invalid priority'):
            Issue(1, 'Bug', 'desc', 'open', 'urgent', 1).validate()

    def test_overridden_describe(self):
        issue_args = (1, 'Login broken', 'desc', 'open', 'critical', 1)
        self.assertEqual(Issue(*issue_args).describe(), 'Login broken [critical]')
        self.assertEqual(
            CriticalIssue(*issue_args).describe(),
            '[URGENT] Login broken — needs immediate attention',
        )
        low_args = (1, 'Cleanup', 'desc', 'open', 'low', 1)
        self.assertEqual(
            LowPriorityIssue(*low_args).describe(),
            'Cleanup — low priority, handle when free',
        )


class ApiTests(SimpleTestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.override = override_settings(BASE_DIR=Path(self.temp_dir.name))
        self.override.enable()
        self.addCleanup(self.override.disable)
        (Path(self.temp_dir.name) / 'reporters.json').write_text('[]\n', encoding='utf-8')
        (Path(self.temp_dir.name) / 'issues.json').write_text('[]\n', encoding='utf-8')
        self.reporter = {'id': 1, 'name': 'Alex Kim', 'email': 'alex@example.com', 'team': 'backend'}
        self.issue = {
            'id': 1,
            'title': 'Login button not working on mobile',
            'description': 'Users on iOS 17 cannot tap the login button',
            'status': 'open',
            'priority': 'critical',
            'reporter_id': 1,
        }

    def post_json(self, url, payload):
        return self.client.post(url, data=json.dumps(payload), content_type='application/json')

    def create_reporter(self):
        result = self.post_json('/api/reporters/', self.reporter)
        self.assertEqual(result.status_code, 201)
        return result

    def test_reporter_create_list_and_lookup(self):
        self.create_reporter()
        self.assertEqual(self.client.get('/api/reporters/').json(), [self.reporter])
        self.assertEqual(self.client.get('/api/reporters/?id=1').json(), self.reporter)
        self.assertEqual(self.client.get('/api/reporters/?id=2').status_code, 404)

    def test_reporter_invalid_email(self):
        bad = {**self.reporter, 'email': 'alex.example.com'}
        result = self.post_json('/api/reporters/', bad)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.json(), {'error': 'Invalid email'})

    def test_issue_create_exact_expected_response(self):
        self.create_reporter()
        result = self.post_json('/api/issues/', self.issue)
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.json(), {
            **self.issue,
            'message': '[URGENT] Login button not working on mobile — needs immediate attention',
        })
        stored = json.loads((Path(self.temp_dir.name) / 'issues.json').read_text(encoding='utf-8'))
        self.assertEqual(stored, [self.issue])

    def test_issue_list_lookup_and_status_filter(self):
        self.create_reporter()
        self.post_json('/api/issues/', self.issue)
        self.assertEqual(self.client.get('/api/issues/').json(), [self.issue])
        self.assertEqual(self.client.get('/api/issues/?id=1').json(), self.issue)
        self.assertEqual(self.client.get('/api/issues/?status=open').json(), [self.issue])
        self.assertEqual(self.client.get('/api/issues/?status=closed').json(), [])
        self.assertEqual(self.client.get('/api/issues/?id=2').json(), {'error': 'Issue not found'})

    def test_issue_invalid_title(self):
        self.create_reporter()
        result = self.post_json('/api/issues/', {**self.issue, 'title': ''})
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.json(), {'error': 'Title cannot be empty'})

    def test_issue_requires_existing_reporter(self):
        result = self.post_json('/api/issues/', self.issue)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.json(), {'error': 'Reporter not found'})

    def test_duplicate_id(self):
        self.create_reporter()
        result = self.post_json('/api/reporters/', self.reporter)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.json(), {'error': 'ID already exists'})

    def test_low_and_medium_priority_messages(self):
        self.create_reporter()
        low = {**self.issue, 'priority': 'low'}
        result = self.post_json('/api/issues/', low)
        self.assertEqual(result.status_code, 201)
        self.assertIn('low priority, handle when free', result.json()['message'])
        medium = {**self.issue, 'id': 2, 'priority': 'medium'}
        result = self.post_json('/api/issues/', medium)
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.json()['message'], 'Login button not working on mobile [medium]')

    def test_invalid_query_id_and_status(self):
        self.assertEqual(self.client.get('/api/issues/?id=abc').status_code, 400)
        self.assertEqual(self.client.get('/api/issues/?status=unknown').status_code, 400)

    def test_invalid_json_and_missing_field(self):
        result = self.client.post('/api/issues/', data='oops', content_type='application/json')
        self.assertEqual(result.status_code, 400)
        result = self.post_json('/api/reporters/', {'id': 1})
        self.assertEqual(result.json(), {'error': 'Missing field: name'})

    def test_http_method_not_allowed(self):
        self.assertEqual(self.client.put('/api/issues/').status_code, 405)

    def test_optional_created_at_and_unicode(self):
        self.create_reporter()
        result = self.post_json('/api/issues/', {
            **self.issue, 'title': 'Ñ-special issue',
            'created_at': '2026-10-11 10:00:00',
        })
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.json()['created_at'], '2026-10-11 10:00:00')
