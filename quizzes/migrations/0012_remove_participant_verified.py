# Generated manually to remove the verified field which was deleted from the model

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0011_remove_quiz_quizzes_qui_status_376889_idx_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='verified',
        ),
    ]
