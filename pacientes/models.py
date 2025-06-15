from django.db import models

class Paciente(models.Model):
    SEXO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    )

    nombre = models.CharField(max_length=100)
    edad = models.PositiveIntegerField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    celular = models.CharField(max_length=20)
    correo = models.EmailField()
    procedencia = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre