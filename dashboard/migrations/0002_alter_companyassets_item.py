# Generated by Django 4.2.9 on 2025-02-10 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyassets',
            name='item',
            field=models.CharField(choices=[('server', 'Server'), ('database', 'Database'), ('website', 'Website'), ('other', 'Other')], max_length=255, verbose_name='Item'),
        ),
    ]
