# Generated by Django 5.1.7 on 2025-04-13 22:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Election",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                (
                    "election_type",
                    models.CharField(
                        choices=[
                            ("presidential", "Presidential"),
                            ("parliamentary", "Parliamentary"),
                            ("starosty", "Starosty"),
                            ("dean", "Dean"),
                        ],
                        max_length=20,
                    ),
                ),
                ("date", models.DateField()),
                ("description", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="Voter",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("pesel_num", models.CharField(max_length=11, unique=True)),
                ("eligible", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Candidate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "election",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="candidates",
                        to="wybory.election",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ElectionResult",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("votes_count", models.PositiveIntegerField(default=0)),
                (
                    "candidate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wybory.candidate",
                    ),
                ),
                (
                    "election",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wybory.election",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Vote",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "candidate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wybory.candidate",
                    ),
                ),
                (
                    "election",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wybory.election",
                    ),
                ),
                (
                    "voter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="wybory.voter"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="VotingCriteria",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("age_min", models.PositiveIntegerField()),
                ("age_max", models.PositiveIntegerField()),
                ("residency_required", models.BooleanField(default=True)),
                (
                    "election",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wybory.election",
                    ),
                ),
            ],
        ),
    ]
