import pytest
from users.models import User
from projects.models import Project, Task, Comment

@pytest.mark.django_db
def test_comment_belongs_to_task_and_author_and_orders_by_created():
    u = User.objects.create_user(email='a@b.dev', name='A', password='password123')
    p = Project.objects.create(name='P', owner=u)
    t = Task.objects.create(project=p, title='T', created_by=u)
    c1 = Comment.objects.create(task=t, author=u, body='first')
    c2 = Comment.objects.create(task=t, author=u, body='second')
    assert list(t.comments.values_list('body', flat=True)) == ['first', 'second']
    assert c1.created_at <= c2.created_at

@pytest.mark.django_db
def test_deleting_author_keeps_comment_with_null_author():
    u = User.objects.create_user(email='a@b.dev', name='A', password='password123')
    p = Project.objects.create(name='P', owner=u)
    t = Task.objects.create(project=p, title='T', created_by=u)
    keeper = User.objects.create_user(email='k@b.dev', name='K', password='password123')
    c = Comment.objects.create(task=t, author=keeper, body='kept')
    keeper.delete()
    c.refresh_from_db()
    assert c.author_id is None
    assert c.body == 'kept'
