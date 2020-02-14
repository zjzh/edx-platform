from django.db import migrations
from opaque_keys.edx.django.models import CourseKeyField

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    TeammateLoveMessage = apps.get_model("teams", "TeammateLoveMessage")
    db_alias = schema_editor.connection.alias
    TeammateLoveMessage.objects.using(db_alias).bulk_create([
        TeammateLoveMessage(text="You're a great teammate!"),
        TeammateLoveMessage(text="Great job on the assignment!"),
        TeammateLoveMessage(text="I appreciate your hard work!"),
        TeammateLoveMessage(text=":)"),
    ])

def reverse_func(apps, schema_editor):
    # forwards_func() creates two Country instances,
    # so reverse_func() should delete them.
    empty_course_key = CourseKeyField.Empty
    TeammateLoveMessage = apps.get_model("teams", "TeammateLoveMessage")
    db_alias = schema_editor.connection.alias
    TeammateLoveMessage.objects.using(db_alias).filter(
        text="You're a great teammate!",
        course_id=empty_course_key
    ).delete()
    TeammateLoveMessage.objects.using(db_alias).filter(
        text="Great job on the assignment!",
        course_id=empty_course_key
    ).delete()
    TeammateLoveMessage.objects.using(db_alias).filter(
        text="I appreciate your hard work!",
        course_id=empty_course_key
    ).delete()
    TeammateLoveMessage.objects.using(db_alias).filter(
        text=":)",
        course_id=empty_course_key
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0004_teammate_love'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
