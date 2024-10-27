# Generated by Django 5.1.2 on 2024-10-21 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_user_is_role_alter_user_login_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_role',
            field=models.IntegerField(blank=True, choices=[(3, 'Customer Support Staff'), (1, 'Admin'), (2, 'Moderator')], default=0, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='login_by',
            field=models.IntegerField(blank=True, choices=[(1, 'General'), (2, 'Guest'), (3, 'Google'), (4, 'Facebook')], default=1, null=True),
        ),
    ]