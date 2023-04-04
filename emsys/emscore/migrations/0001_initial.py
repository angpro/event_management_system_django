# Generated by Django 4.1.7 on 2023-02-18 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EventDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_data', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=300)),
                ('address', models.CharField(max_length=300)),
                ('time', models.DateField()),
                ('description', models.TextField()),
            ],
        ),
    ]