import pytest
from rest_framework.test import APIClient
from users.models import User
from projects.models import Project, Membership, Task


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def owner(db):
    return User.objects.create_user(
        email='owner@taskboard.dev', name='Olive Owner', password='password123'
    )


@pytest.fixture
def project(owner):
    project = Project.objects.create(name='Comment Project', owner=owner)
    Membership.objects.create(user=owner, project=project, role='admin')
    return project


@pytest.fixture
def task(project, owner):
    return Task.objects.create(project=project, title='A task', created_by=owner)


def make_user(email, name='Test User'):
    return User.objects.create_user(email=email, name=name, password='password123')


def authed_client(user):
    """Return an APIClient with a Bearer token for the given user."""
    client = APIClient()
    response = client.post(
        '/api/auth/login',
        {'email': user.email, 'password': 'password123'},
        format='json',
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['token']}")
    return client


def member_client(project, email, role):
    """Create a user with `role` membership on `project` and return an authed client."""
    user = make_user(email, name=f'{role.title()} User')
    Membership.objects.create(user=user, project=project, role=role)
    return user, authed_client(user)


def comments_url(task_id):
    return f'/api/tasks/{task_id}/comments'


@pytest.mark.django_db
class TestComments:
    def test_comments_returned_oldest_first(self, project, task):
        _, client = member_client(project, 'member@taskboard.dev', 'member')
        for body in ['first', 'second', 'third']:
            resp = client.post(comments_url(task.id), {'body': body}, format='json')
            assert resp.status_code == 201

        resp = client.get(comments_url(task.id))
        assert resp.status_code == 200
        bodies = [c['body'] for c in resp.data['comments']]
        assert bodies == ['first', 'second', 'third']

    def test_comment_shows_author_body_and_timestamp(self, project, task):
        user, client = member_client(project, 'member@taskboard.dev', 'member')
        resp = client.post(comments_url(task.id), {'body': 'hello world'}, format='json')
        assert resp.status_code == 201

        resp = client.get(comments_url(task.id))
        assert resp.status_code == 200
        comment = resp.data['comments'][0]
        assert comment['body'] == 'hello world'
        assert comment['author']['name'] == user.name
        assert comment['author']['email'] == user.email
        assert comment['createdAt']

    def test_new_task_has_empty_thread(self, project, task):
        _, client = member_client(project, 'member@taskboard.dev', 'member')
        resp = client.get(comments_url(task.id))
        assert resp.status_code == 200
        assert resp.data['comments'] == []

    @pytest.mark.parametrize('role,expected', [
        ('admin', 201),
        ('member', 201),
        ('viewer', 403),
        ('non_member', 403),
    ])
    def test_role_can_or_cannot_post(self, project, task, role, expected):
        if role == 'non_member':
            user = make_user('nobody@taskboard.dev')
            client = authed_client(user)
        else:
            _, client = member_client(project, f'{role}@taskboard.dev', role)

        resp = client.post(comments_url(task.id), {'body': 'attempt'}, format='json')
        assert resp.status_code == expected

        if expected == 403:
            reader = authed_client(project.owner)
            listing = reader.get(comments_url(task.id))
            assert listing.data['comments'] == []

    def test_viewer_can_read_comments(self, project, task):
        _, poster = member_client(project, 'member@taskboard.dev', 'member')
        poster.post(comments_url(task.id), {'body': 'visible to viewers'}, format='json')

        _, viewer = member_client(project, 'viewer@taskboard.dev', 'viewer')
        resp = viewer.get(comments_url(task.id))
        assert resp.status_code == 200
        bodies = [c['body'] for c in resp.data['comments']]
        assert 'visible to viewers' in bodies

    def test_non_member_cannot_read_comments(self, project, task):
        stranger = make_user('stranger@taskboard.dev')
        client = authed_client(stranger)
        resp = client.get(comments_url(task.id))
        assert resp.status_code == 403

    def test_unauthenticated_request_is_rejected(self, client, task):
        get_resp = client.get(comments_url(task.id))
        assert get_resp.status_code == 401
        post_resp = client.post(comments_url(task.id), {'body': 'hi'}, format='json')
        assert post_resp.status_code == 401

    def test_comment_cannot_be_edited(self, project, task):
        _, client = member_client(project, 'member@taskboard.dev', 'member')
        client.post(comments_url(task.id), {'body': 'original'}, format='json')

        patch_resp = client.patch(comments_url(task.id), {'body': 'edited'}, format='json')
        assert patch_resp.status_code == 405
        put_resp = client.put(comments_url(task.id), {'body': 'edited'}, format='json')
        assert put_resp.status_code == 405

        resp = client.get(comments_url(task.id))
        bodies = [c['body'] for c in resp.data['comments']]
        assert bodies == ['original']

    def test_comment_cannot_be_deleted(self, project, task):
        _, client = member_client(project, 'member@taskboard.dev', 'member')
        client.post(comments_url(task.id), {'body': 'permanent'}, format='json')

        delete_resp = client.delete(comments_url(task.id))
        assert delete_resp.status_code == 405

        resp = client.get(comments_url(task.id))
        bodies = [c['body'] for c in resp.data['comments']]
        assert bodies == ['permanent']

    def test_empty_comment_is_rejected(self, project, task):
        _, client = member_client(project, 'member@taskboard.dev', 'member')
        resp = client.post(comments_url(task.id), {'body': '   '}, format='json')
        assert resp.status_code == 400

        listing = client.get(comments_url(task.id))
        assert listing.data['comments'] == []

    def test_author_is_the_authenticated_user(self, project, task):
        user, client = member_client(project, 'member@taskboard.dev', 'member')
        other = make_user('other@taskboard.dev', name='Other Person')

        resp = client.post(
            comments_url(task.id),
            {'body': 'mine', 'authorId': str(other.id)},
            format='json',
        )
        assert resp.status_code == 201
        assert resp.data['comment']['author']['id'] == str(user.id)
        assert resp.data['comment']['author']['id'] != str(other.id)

    def test_comments_are_isolated_per_task(self, project, owner):
        task_a = Task.objects.create(project=project, title='Task A', created_by=owner)
        task_b = Task.objects.create(project=project, title='Task B', created_by=owner)
        _, client = member_client(project, 'member@taskboard.dev', 'member')

        client.post(comments_url(task_a.id), {'body': 'on A'}, format='json')

        resp = client.get(comments_url(task_b.id))
        assert resp.status_code == 200
        assert resp.data['comments'] == []

    def test_comment_on_missing_task_returns_404(self, project):
        _, client = member_client(project, 'member@taskboard.dev', 'member')
        missing_id = '00000000-0000-0000-0000-000000000000'
        resp = client.post(comments_url(missing_id), {'body': 'hi'}, format='json')
        assert resp.status_code == 404
