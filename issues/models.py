"""Pure-Python OOP entities (not Django ORM models), as requested."""
from abc import ABC, abstractmethod


class BaseEntity(ABC):
    @abstractmethod
    def validate(self):
        """Raise ValueError when entity data is invalid."""

    def to_dict(self):
        """Serialize the entity's instance attributes to a plain dictionary."""
        return {key: value for key, value in self.__dict__.items()}


class Reporter(BaseEntity):
    def __init__(self, id, name, email, team):
        self.id = id
        self.name = name
        self.email = email
        self.team = team

    def validate(self):
        if type(self.id) is not int or self.id <= 0:
            raise ValueError('ID must be a positive integer')
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError('Name cannot be empty')
        if not isinstance(self.email, str) or '@' not in self.email:
            raise ValueError('Invalid email')
        if not isinstance(self.team, str) or not self.team.strip():
            raise ValueError('Team cannot be empty')


class Issue(BaseEntity):
    ALLOWED_STATUSES = ('open', 'in_progress', 'resolved', 'closed')
    ALLOWED_PRIORITIES = ('low', 'medium', 'high', 'critical')

    def __init__(self, id, title, description, status, priority, reporter_id, created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.reporter_id = reporter_id
        # Optional field: omit when not supplied so POST matches the brief's example.
        if created_at is not None:
            self.created_at = created_at

    def validate(self):
        if type(self.id) is not int or self.id <= 0:
            raise ValueError('ID must be a positive integer')
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError('Title cannot be empty')
        if not isinstance(self.description, str):
            raise ValueError('Description must be a string')
        if self.status not in self.ALLOWED_STATUSES:
            raise ValueError('Invalid status')
        if self.priority not in self.ALLOWED_PRIORITIES:
            raise ValueError('Invalid priority')
        if type(self.reporter_id) is not int or self.reporter_id <= 0:
            raise ValueError('Reporter ID must be a positive integer')
        if hasattr(self, 'created_at') and not isinstance(self.created_at, str):
            raise ValueError('created_at must be a string')

    def describe(self):
        return f'{self.title} [{self.priority}]'


class CriticalIssue(Issue):
    def describe(self):
        return f'[URGENT] {self.title} — needs immediate attention'


class LowPriorityIssue(Issue):
    def describe(self):
        return f'{self.title} — low priority, handle when free'
