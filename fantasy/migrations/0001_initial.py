# Generated by Django 4.1 on 2022-08-30 10:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Jugador',
            fields=[
                ('id', models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('estado', models.CharField(blank=True, max_length=50)),
                ('posicion', models.CharField(max_length=50)),
                ('equipo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasy.equipo')),
            ],
        ),
        migrations.CreateModel(
            name='Valores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jornada', models.SmallIntegerField()),
                ('valor', models.FloatField()),
                ('jugador_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasy.jugador')),
            ],
        ),
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jornada', models.SmallIntegerField()),
                ('puntos', models.SmallIntegerField()),
                ('minutos', models.SmallIntegerField()),
                ('goles', models.SmallIntegerField()),
                ('asist', models.SmallIntegerField()),
                ('asistSinGol', models.SmallIntegerField()),
                ('paradas', models.SmallIntegerField()),
                ('amarillas', models.SmallIntegerField()),
                ('rojas', models.SmallIntegerField()),
                ('centros', models.SmallIntegerField()),
                ('despejes', models.SmallIntegerField()),
                ('penFallados', models.SmallIntegerField()),
                ('encajados', models.SmallIntegerField()),
                ('tiros', models.SmallIntegerField()),
                ('regates', models.SmallIntegerField()),
                ('recuperaciones', models.SmallIntegerField()),
                ('perdidas', models.SmallIntegerField()),
                ('ptsMarca', models.SmallIntegerField()),
                ('jugador_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantasy.jugador')),
            ],
        ),
        migrations.CreateModel(
            name='Plantilla',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jugadores', models.ManyToManyField(blank=True, to='fantasy.jugador')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Favoritos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jugadores', models.ManyToManyField(blank=True, to='fantasy.jugador')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]