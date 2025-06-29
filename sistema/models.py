# apps/sistema/models.py

from django.db import models

def logo_upload_path(instance, filename):
    return f'logos/{instance.pk}_logo_{filename}'

class ConfiguracionLaboratorio(models.Model):
    # Información General
    nombre_laboratorio = models.CharField(max_length=255)
    direccion = models.TextField(blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    correo = models.EmailField(blank=True)
    logo = models.ImageField(upload_to=logo_upload_path, null=True, blank=True)

    # Configuración Email
    enviar_resultados = models.BooleanField(default=False)
    enviar_notificaciones = models.BooleanField(default=False)
    servidor_smtp = models.CharField(max_length=255, blank=True)
    puerto_smtp = models.CharField(max_length=10, blank=True)
    usuario_smtp = models.CharField(max_length=255, blank=True)
    password_smtp = models.CharField(max_length=255, blank=True)

    # Configuración Reportes
    formato_pdf = models.CharField(max_length=20, default="A4")
    mostrar_logo = models.BooleanField(default=True)
    mostrar_firma = models.BooleanField(default=True)
    color_encabezado = models.CharField(max_length=20, default="#1976d2")
    pie_pagina = models.CharField(max_length=255, blank=True)

    # Configuración Backup
    backup_automatico = models.BooleanField(default=False)
    frecuencia_backup = models.CharField(max_length=20, default="diario")
    hora_backup = models.TimeField(default="03:00")
    ruta_backup = models.CharField(max_length=255, default="/backups")

    def __str__(self):
        return f"Configuración {self.nombre_laboratorio or 'Laboratorio'}"
    