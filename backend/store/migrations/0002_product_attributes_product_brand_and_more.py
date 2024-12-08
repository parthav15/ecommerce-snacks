# Generated by Django 5.1.3 on 2024-12-08 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='attributes',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='discount_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='product',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_keywords',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='rating',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='video_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_role',
            field=models.IntegerField(blank=True, choices=[(3, 'Customer Support Staff'), (2, 'Moderator'), (1, 'Admin')], default=0, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='login_by',
            field=models.IntegerField(blank=True, choices=[(4, 'Facebook'), (3, 'Google'), (2, 'Guest'), (1, 'General')], default=1, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, default='', null=True, upload_to='profile_pictures/'),
        ),
    ]
