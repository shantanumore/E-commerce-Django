# Generated by Django 3.0.7 on 2020-07-07 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('E_com', '0002_auto_20200703_0016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='desc',
            field=models.CharField(max_length=1000),
        ),
    ]