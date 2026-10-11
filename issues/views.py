"""JSON API views; entities live in models.py, persistence in storage.py."""
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import CriticalIssue, Issue, LowPriorityIssue, Reporter
from .storage import insert_record, read_records


def _parse_request_json(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError('Invalid JSON body') from exc
    if not isinstance(data, dict):
        raise ValueError('Expected a JSON object')
    return data


def _required_fields(data, fields):
    for field in fields:
        if field not in data:
            raise ValueError(f'Missing field: {field}')


def _get_by_id_or_all(request, filename, label):
    records = read_records(filename)
    if 'id' in request.GET:
        try:
            item_id = int(request.GET['id'])
        except ValueError:
            return JsonResponse({'error': 'ID must be an integer'}, status=400)
        for record in records:
            if record['id'] == item_id:
                return JsonResponse(record, status=200)
        return JsonResponse({'error': f'{label} not found'}, status=404)
    return records


@csrf_exempt  # For Postman/local exercise only; use proper auth + CSRF in production.
@require_http_methods(['GET', 'POST'])
def reporters_view(request):
    if request.method == 'GET':
        result = _get_by_id_or_all(request, 'reporters.json', 'Reporter')
        return result if isinstance(result, JsonResponse) else JsonResponse(result, safe=False)

    try:
        data = _parse_request_json(request)
        _required_fields(data, ('id', 'name', 'email', 'team'))
        reporter = Reporter(data['id'], data['name'], data['email'], data['team'])
        reporter.validate()
        result = reporter.to_dict()
        insert_record('reporters.json', result)
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    return JsonResponse(result, status=201)


@csrf_exempt  # For Postman/local exercise only; use proper auth + CSRF in production.
@require_http_methods(['GET', 'POST'])
def issues_view(request):
    if request.method == 'GET':
        result = _get_by_id_or_all(request, 'issues.json', 'Issue')
        if isinstance(result, JsonResponse):
            return result
        if 'status' in request.GET:
            status = request.GET['status']
            if status not in Issue.ALLOWED_STATUSES:
                return JsonResponse({'error': 'Invalid status'}, status=400)
            result = [record for record in result if record['status'] == status]
        return JsonResponse(result, safe=False, status=200)

    try:
        data = _parse_request_json(request)
        _required_fields(data, ('id', 'title', 'description', 'status', 'priority', 'reporter_id'))
        if data['priority'] == 'critical':
            issue_class = CriticalIssue
        elif data['priority'] == 'low':
            issue_class = LowPriorityIssue
        else:
            issue_class = Issue
        issue = issue_class(
            id=data['id'], title=data['title'], description=data['description'],
            status=data['status'], priority=data['priority'],
            reporter_id=data['reporter_id'],
            **({'created_at': data['created_at']} if 'created_at' in data else {}),
        )
        issue.validate()
        result = issue.to_dict()
        insert_record('issues.json', result, check_reporter=True)
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    result['message'] = issue.describe()
    return JsonResponse(result, status=201)
