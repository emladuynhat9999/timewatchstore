# Generated by Django 3.2.5 on 2022-01-06 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timewatchstore', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategory',
            name='gender',
            field=models.CharField(max_length=150, null=True),
        ),
    ]
