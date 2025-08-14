from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from banco_sangre.models import Donante, Lote, UnidadMuestra
from medicos.models import Medico
from localizacion.models import Pais, Departamento, Municipio
from datetime import date, timedelta
import random
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Puebla las tablas con datos de prueba para donantes y médicos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--donantes',
            type=int,
            default=50,
            help='Número de donantes a crear (default: 50)'
        )
        parser.add_argument(
            '--medicos',
            type=int,
            default=20,
            help='Número de médicos a crear (default: 20)'
        )
        parser.add_argument(
            '--unidades',
            type=int,
            default=100,
            help='Número de unidades de muestra a crear (default: 100)'
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Iniciando población de datos de prueba...')
        
        # Crear usuario administrador si no existe
        self.crear_usuario_admin()
        
        # Poblar datos de localización si no existen
        self.poblar_localizacion()
        
        # Crear médicos
        self.crear_medicos(options['medicos'])
        
        # Crear donantes
        self.crear_donantes(options['donantes'])
        
        # Crear unidades de muestra
        self.crear_unidades_muestra(options['unidades'])
        
        self.stdout.write(self.style.SUCCESS('✅ Datos de prueba creados exitosamente!'))

    def crear_usuario_admin(self):
        """Crear usuario administrador si no existe"""
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@labclinic.com',
                password='admin123'
            )
            self.stdout.write('👤 Usuario administrador creado: admin/admin123')

    def poblar_localizacion(self):
        """Poblar datos de localización básicos"""
        # Crear país Guatemala si no existe
        guatemala, _ = Pais.objects.get_or_create(nombre='Guatemala')
        
        # Crear departamentos principales
        departamentos = {
            'Guatemala': ['Ciudad de Guatemala', 'Mixco', 'Villa Nueva', 'San Miguel Petapa'],
            'Quetzaltenango': ['Quetzaltenango', 'Olintepeque', 'La Esperanza'],
            'Petén': ['Flores', 'San Benito', 'Santa Elena'],
            'Alta Verapaz': ['Cobán', 'San Pedro Carchá', 'Tactic'],
            'Baja Verapaz': ['Salama', 'Cubulco', 'Rabinal'],
        }
        
        for depto_nombre, municipios in departamentos.items():
            depto, _ = Departamento.objects.get_or_create(
                nombre=depto_nombre, 
                pais=guatemala
            )
            for municipio_nombre in municipios:
                Municipio.objects.get_or_create(
                    nombre=municipio_nombre, 
                    departamento=depto
                )

    def crear_medicos(self, cantidad):
        """Crear médicos de prueba"""
        especialidades = [choice[0] for choice in Medico.ESPECIALIDAD_CHOISE]
        generos = [choice[0] for choice in Medico.GENERO_CHOICES]
        tipos_documento = [choice[0] for choice in Medico.TIPO_DOCUMENTO_CHOICES]
        
        # Obtener algunos municipios
        municipios = list(Municipio.objects.all()[:10])
        
        nombres_masculinos = [
            'Carlos', 'Luis', 'Miguel', 'Jorge', 'Roberto', 'Fernando', 'Eduardo',
            'Ricardo', 'Alberto', 'Manuel', 'Francisco', 'Antonio', 'Javier', 'Diego'
        ]
        
        nombres_femeninos = [
            'María', 'Ana', 'Carmen', 'Isabel', 'Patricia', 'Rosa', 'Elena',
            'Sofia', 'Valentina', 'Camila', 'Gabriela', 'Daniela', 'Andrea', 'Laura'
        ]
        
        apellidos = [
            'García', 'Rodríguez', 'López', 'Martínez', 'González', 'Pérez',
            'Sánchez', 'Ramírez', 'Torres', 'Flores', 'Rivera', 'Morales',
            'Cruz', 'Ortiz', 'Reyes', 'Moreno', 'Jiménez', 'Díaz'
        ]
        
        for i in range(cantidad):
            genero = random.choice(generos)
            nombres = random.choice(nombres_masculinos if genero == 'M' else nombres_femeninos)
            apellido1 = random.choice(apellidos)
            apellido2 = random.choice(apellidos)
            
            medico = Medico.objects.create(
                numero_documento=f"{random.randint(10000000, 99999999)}",
                tipo_documento=random.choice(tipos_documento),
                nombres=nombres,
                apellidos=f"{apellido1} {apellido2}",
                telefono_consultorio=f"2{random.randint(1000000, 9999999)}",
                celular=f"5{random.randint(10000000, 99999999)}",
                codigo_laboratorio=f"LAB{random.randint(1000, 9999)}",
                email=f"{nombres.lower()}.{apellido1.lower()}@medico.com",
                direccion_consultorio=f"Consultorio {random.randint(1, 100)}, Zona {random.randint(1, 25)}",
                genero=genero,
                especialidad_medica=random.choice(especialidades),
                municipio=random.choice(municipios) if municipios else None,
                activo=random.choice([True, True, True, False])  # 75% activos
            )
            
            if i < 5:  # Mostrar solo los primeros 5
                self.stdout.write(f'👨‍⚕️ Médico creado: {medico.nombres} {medico.apellidos} - {medico.get_especialidad_medica_display()}')
        
        self.stdout.write(f'✅ {cantidad} médicos creados')

    def crear_donantes(self, cantidad):
        """Crear donantes de prueba"""
        municipios = list(Municipio.objects.all()[:10])
        
        nombres_masculinos = [
            'Juan', 'Pedro', 'José', 'Manuel', 'Carlos', 'Luis', 'Miguel',
            'David', 'Daniel', 'Andrés', 'Roberto', 'Fernando', 'Eduardo',
            'Ricardo', 'Alberto', 'Francisco', 'Antonio', 'Javier', 'Diego'
        ]
        
        nombres_femeninos = [
            'María', 'Ana', 'Carmen', 'Isabel', 'Patricia', 'Rosa', 'Elena',
            'Sofia', 'Valentina', 'Camila', 'Gabriela', 'Daniela', 'Andrea',
            'Laura', 'Claudia', 'Verónica', 'Mónica', 'Beatriz', 'Lucía'
        ]
        
        apellidos = [
            'García', 'Rodríguez', 'López', 'Martínez', 'González', 'Pérez',
            'Sánchez', 'Ramírez', 'Torres', 'Flores', 'Rivera', 'Morales',
            'Cruz', 'Ortiz', 'Reyes', 'Moreno', 'Jiménez', 'Díaz', 'Herrera'
        ]
        
        sexos = ['Masculino', 'Femenino']
        ocupaciones = [
            'Estudiante', 'Empleado', 'Técnico', 'Profesional', 'Comerciante',
            'Agricultor', 'Ama de casa', 'Jubilado', 'Desempleado', 'Otro'
        ]
        
        tipos_sangre = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        for i in range(cantidad):
            # Generar fecha de nacimiento entre 18 y 65 años
            edad = random.randint(18, 65)
            fecha_nacimiento = date.today() - timedelta(days=edad*365 + random.randint(0, 365))
            
            sexo = random.choice(sexos)
            primer_nombre = random.choice(nombres_masculinos if sexo == 'Masculino' else nombres_femeninos)
            segundo_nombre = random.choice([random.choice(nombres_masculinos if sexo == 'Masculino' else nombres_femeninos), ''])
            primer_apellido = random.choice(apellidos)
            segundo_apellido = random.choice([random.choice(apellidos), ''])
            
            # Generar CUI único
            cui = f"{random.randint(1000, 9999)}-{random.randint(10000, 99999)}-{random.randint(1000, 9999)}"
            
            donante = Donante.objects.create(
                cui=cui,
                primer_nombre=primer_nombre,
                segundo_nombre=segundo_nombre,
                primer_apellido=primer_apellido,
                segundo_apellido=segundo_apellido,
                direccion=f"Dirección {random.randint(1, 100)}, Zona {random.randint(1, 25)}",
                celular=f"5{random.randint(10000000, 99999999)}",
                sexo=sexo,
                fecha_nacimiento=fecha_nacimiento,
                edad=edad,
                ocupacion=random.choice(ocupaciones),
                municipio=random.choice(municipios) if municipios else None,
                apto_donacion=random.choice([True, True, True, False]),  # 75% aptos
                tiene_entrevista_apro=random.choice([True, False])
            )
            
            if i < 5:  # Mostrar solo los primeros 5
                self.stdout.write(f'🩸 Donante creado: {donante.primer_nombre} {donante.primer_apellido} - CUI: {donante.cui}')
        
        self.stdout.write(f'✅ {cantidad} donantes creados')

    def crear_unidades_muestra(self, cantidad):
        """Crear unidades de muestra de prueba"""
        donantes = list(Donante.objects.all())
        tipos_unidad = [choice[0] for choice in UnidadMuestra.TIPO_UNIDAD_CHOICES]
        tipos_sangre = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        if not donantes:
            self.stdout.write('⚠️ No hay donantes para crear unidades de muestra')
            return
        
        for i in range(cantidad):
            donante = random.choice(donantes)
            tipo_unidad = random.choice(tipos_unidad)
            tipo_sangre = random.choice(tipos_sangre)
            
            # Fecha de extracción en los últimos 30 días
            fecha_extraccion = date.today() - timedelta(days=random.randint(0, 30))
            
            # Fecha de caducidad (entre 30 y 365 días desde extracción)
            dias_vigencia = random.randint(30, 365)
            fecha_caducidad = fecha_extraccion + timedelta(days=dias_vigencia)
            
            # Volumen según tipo de unidad
            volumen_por_tipo = {
                'PLASMA': random.randint(200, 400),
                'PAQUETE_GLOBULAR': random.randint(250, 350),
                'PLAQUETAS': random.randint(50, 100),
                'CRIO_PRECIPITADO': random.randint(10, 20),
            }
            
            volumen = volumen_por_tipo.get(tipo_unidad, 250)
            
            unidad = UnidadMuestra.objects.create(
                donante=donante,
                tipo_unidad=tipo_unidad,
                tipo_sangre=tipo_sangre,
                volumen_ml=volumen,
                fecha_extraccion=fecha_extraccion,
                fecha_caducidad=fecha_caducidad,
                estado=random.choice(['DISPONIBLE', 'DISPONIBLE', 'RESERVADO', 'VENCIDO']),
                observaciones=f"Unidad de prueba {i+1}"
            )
            
            if i < 5:  # Mostrar solo las primeras 5
                self.stdout.write(f'🧪 Unidad creada: {unidad.correlativo} - {unidad.get_tipo_unidad_display()}')
        
        self.stdout.write(f'✅ {cantidad} unidades de muestra creadas') 