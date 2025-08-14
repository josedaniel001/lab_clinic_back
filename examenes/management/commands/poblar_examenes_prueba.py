from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from examenes.models import Examen
from banco_sangre.models import Donante
from medicos.models import Medico
from ordenes.models import Orden, DetalleOrden
from resultados.models import Resultado, ResultadoDetalle
from localizacion.models import Pais, Departamento, Municipio
from datetime import date, timedelta, time
import random
import json
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Puebla las tablas con datos de prueba para exámenes, donantes, órdenes y resultados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--examenes',
            type=int,
            default=30,
            help='Número de exámenes a crear (default: 30)'
        )
        parser.add_argument(
            '--donantes',
            type=int,
            default=50,
            help='Número de donantes a crear (default: 50)'
        )
        parser.add_argument(
            '--ordenes',
            type=int,
            default=100,
            help='Número de órdenes a crear (default: 100)'
        )
        parser.add_argument(
            '--resultados',
            type=int,
            default=80,
            help='Número de resultados a crear (default: 80)'
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Iniciando población de datos de prueba para exámenes...')
        
        # Crear usuario administrador si no existe
        self.crear_usuario_admin()
        
        # Poblar datos de localización si no existen
        self.poblar_localizacion()
        
        # Crear médicos si no existen
        self.crear_medicos_si_no_existen()
        
        # Crear exámenes
        self.crear_examenes(options['examenes'])
        
        # Crear donantes
        self.crear_donantes(options['donantes'])
        
        # Crear órdenes
        self.crear_ordenes(options['ordenes'])
        
        # Crear resultados
        self.crear_resultados(options['resultados'])
        
        self.stdout.write(self.style.SUCCESS('✅ Datos de prueba de exámenes creados exitosamente!'))

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

    def crear_medicos_si_no_existen(self):
        """Crear médicos si no existen"""
        if Medico.objects.count() == 0:
            self.stdout.write('⚠️ No hay médicos. Creando médicos de prueba...')
            from banco_sangre.management.commands.poblar_datos_prueba import Command as PoblarCommand
            poblar_cmd = PoblarCommand()
            poblar_cmd.crear_medicos(10)

    def crear_examenes(self, cantidad):
        """Crear exámenes de prueba"""
        categorias_examenes = {
            'Hematología': [
                {
                    'nombre': 'Hemograma Completo',
                    'codigo': 'HEM001',
                    'precio': 150.00,
                    'tiempo_procesamiento': '2-4 horas',
                    'metodologia': 'Análisis automatizado con contador hematológico',
                    'preparacion_paciente': 'Ayuno de 8-12 horas',
                    'valores_referencia': [
                        {"parametro": "Hematíes", "rango": "4.5-5.5", "unidad": "M/μL"},
                        {"parametro": "Hemoglobina", "rango": "13-17", "unidad": "g/dL"},
                        {"parametro": "Leucocitos", "rango": "4.5-11.0", "unidad": "K/μL"},
                        {"parametro": "Plaquetas", "rango": "150-450", "unidad": "K/μL"},
                        {"parametro": "Hematocrito", "rango": "40-50", "unidad": "%"}
                    ]
                },
                {
                    'nombre': 'Recuento de Plaquetas',
                    'codigo': 'HEM002',
                    'precio': 80.00,
                    'tiempo_procesamiento': '1-2 horas',
                    'metodologia': 'Contador automatizado de plaquetas',
                    'preparacion_paciente': 'No requiere ayuno',
                    'valores_referencia': [
                        {"parametro": "Plaquetas", "rango": "150-450", "unidad": "K/μL"}
                    ]
                },
                {
                    'nombre': 'Velocidad de Sedimentación',
                    'codigo': 'HEM003',
                    'precio': 60.00,
                    'tiempo_procesamiento': '1 hora',
                    'metodologia': 'Método de Westergren',
                    'preparacion_paciente': 'No requiere ayuno',
                    'valores_referencia': [
                        {"parametro": "VSG Hombres", "rango": "0-15", "unidad": "mm/h"},
                        {"parametro": "VSG Mujeres", "rango": "0-20", "unidad": "mm/h"}
                    ]
                }
            ],
            'Bioquímica': [
                {
                    'nombre': 'Glucosa en Sangre',
                    'codigo': 'BIO001',
                    'precio': 45.00,
                    'tiempo_procesamiento': '30 minutos',
                    'metodologia': 'Método enzimático (GOD-PAP)',
                    'preparacion_paciente': 'Ayuno de 8-12 horas',
                    'valores_referencia': [
                        {"parametro": "Glucosa", "rango": "70-100", "unidad": "mg/dL"}
                    ]
                },
                {
                    'nombre': 'Perfil Lipídico',
                    'codigo': 'BIO002',
                    'precio': 120.00,
                    'tiempo_procesamiento': '2-3 horas',
                    'metodologia': 'Métodos enzimáticos automatizados',
                    'preparacion_paciente': 'Ayuno de 12-14 horas',
                    'valores_referencia': [
                        {"parametro": "Colesterol Total", "rango": "<200", "unidad": "mg/dL"},
                        {"parametro": "HDL", "rango": ">40", "unidad": "mg/dL"},
                        {"parametro": "LDL", "rango": "<100", "unidad": "mg/dL"},
                        {"parametro": "Triglicéridos", "rango": "<150", "unidad": "mg/dL"}
                    ]
                },
                {
                    'nombre': 'Creatinina',
                    'codigo': 'BIO003',
                    'precio': 50.00,
                    'tiempo_procesamiento': '1 hora',
                    'metodologia': 'Método de Jaffé',
                    'preparacion_paciente': 'No requiere ayuno',
                    'valores_referencia': [
                        {"parametro": "Creatinina Hombres", "rango": "0.7-1.3", "unidad": "mg/dL"},
                        {"parametro": "Creatinina Mujeres", "rango": "0.6-1.1", "unidad": "mg/dL"}
                    ]
                }
            ],
            'Inmunología': [
                {
                    'nombre': 'VIH 1/2',
                    'codigo': 'INM001',
                    'precio': 200.00,
                    'tiempo_procesamiento': '4-6 horas',
                    'metodologia': 'Enzimoinmunoanálisis (ELISA)',
                    'preparacion_paciente': 'No requiere ayuno',
                    'valores_referencia': [
                        {"parametro": "VIH", "rango": "No reactivo", "unidad": ""}
                    ]
                },
                {
                    'nombre': 'Hepatitis B',
                    'codigo': 'INM002',
                    'precio': 180.00,
                    'tiempo_procesamiento': '4-6 horas',
                    'metodologia': 'Enzimoinmunoanálisis (ELISA)',
                    'preparacion_paciente': 'No requiere ayuno',
                    'valores_referencia': [
                        {"parametro": "HBsAg", "rango": "Negativo", "unidad": ""},
                        {"parametro": "Anti-HBs", "rango": ">10", "unidad": "mUI/mL"}
                    ]
                }
            ],
            'Microbiología': [
                {
                    'nombre': 'Cultivo de Orina',
                    'codigo': 'MIC001',
                    'precio': 90.00,
                    'tiempo_procesamiento': '48-72 horas',
                    'metodologia': 'Cultivo en medios selectivos',
                    'preparacion_paciente': 'Muestra de orina de primera micción',
                    'valores_referencia': [
                        {"parametro": "Cultivo", "rango": "Sin crecimiento", "unidad": ""}
                    ]
                },
                {
                    'nombre': 'Antibiograma',
                    'codigo': 'MIC002',
                    'precio': 150.00,
                    'tiempo_procesamiento': '24-48 horas',
                    'metodologia': 'Método de difusión en disco (Kirby-Bauer)',
                    'preparacion_paciente': 'Depende del tipo de muestra',
                    'valores_referencia': [
                        {"parametro": "Sensibilidad", "rango": "Según microorganismo", "unidad": ""}
                    ]
                }
            ],
            'Endocrinología': [
                {
                    'nombre': 'TSH',
                    'codigo': 'END001',
                    'precio': 120.00,
                    'tiempo_procesamiento': '2-3 horas',
                    'metodologia': 'Inmunoensayo quimioluminiscente',
                    'preparacion_paciente': 'No requiere ayuno',
                    'valores_referencia': [
                        {"parametro": "TSH", "rango": "0.4-4.0", "unidad": "mUI/L"}
                    ]
                },
                {
                    'nombre': 'T4 Libre',
                    'codigo': 'END002',
                    'precio': 100.00,
                    'tiempo_procesamiento': '2-3 horas',
                    'metodologia': 'Inmunoensayo quimioluminiscente',
                    'preparacion_paciente': 'No requiere ayuno',
                    'valores_referencia': [
                        {"parametro": "T4 Libre", "rango": "0.8-1.8", "unidad": "ng/dL"}
                    ]
                }
            ]
        }
        
        examenes_creados = 0
        for categoria, examenes_cat in categorias_examenes.items():
            for examen_data in examenes_cat:
                if examenes_creados >= cantidad:
                    break
                
                examen, created = Examen.objects.get_or_create(
                    codigo=examen_data['codigo'],
                    defaults={
                        'nombre': examen_data['nombre'],
                        'categoria': categoria,
                        'precio': Decimal(str(examen_data['precio'])),
                        'tiempo_procesamiento': examen_data['tiempo_procesamiento'],
                        'metodologia': examen_data['metodologia'],
                        'preparacion_paciente': examen_data['preparacion_paciente'],
                        'valores_referencia': json.dumps(examen_data['valores_referencia'], ensure_ascii=False),
                        'estado': 'Activo'
                    }
                )
                
                if created:
                    self.stdout.write(f'🔬 Examen creado: {examen.nombre} - {examen.codigo}')
                    examenes_creados += 1
        
        self.stdout.write(f'✅ {examenes_creados} exámenes creados')

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

    def crear_ordenes(self, cantidad):
        """Crear órdenes de prueba"""
        donantes = list(Donante.objects.filter(activo=True))
        medicos = list(Medico.objects.filter(activo=True))
        examenes = list(Examen.objects.filter(estado='Activo'))
        
        if not donantes:
            self.stdout.write('⚠️ No hay donantes activos para crear órdenes')
            return
        
        if not medicos:
            self.stdout.write('⚠️ No hay médicos activos para crear órdenes')
            return
        
        if not examenes:
            self.stdout.write('⚠️ No hay exámenes activos para crear órdenes')
            return
        
        estados_orden = ['PENDIENTE', 'VALIDADO', 'EN PROCESO', 'ENTREGADO', 'CANCELADO']
        prioridades = ['ALTA', 'MEDIA', 'NORMAL']
        
        for i in range(cantidad):
            donante = random.choice(donantes)
            medico = random.choice(medicos)
            
            # Fecha aleatoria en los últimos 30 días
            fecha_orden = date.today() - timedelta(days=random.randint(0, 30))
            hora_orden = time(random.randint(8, 17), random.randint(0, 59))
            
            # Generar código único
            codigo = f"ORD-{fecha_orden.strftime('%Y%m%d')}-{i+1:04d}"
            
            orden = Orden.objects.create(
                codigo=codigo,
                donante=donante,
                medico=medico,
                fecha=fecha_orden,
                hora=hora_orden,
                estado=random.choice(estados_orden),
                prioridad=random.choice(prioridades)
            )
            
            # Agregar 1-3 exámenes por orden
            num_examenes = random.randint(1, min(3, len(examenes)))
            examenes_orden = random.sample(examenes, num_examenes)
            
            for examen in examenes_orden:
                DetalleOrden.objects.create(
                    orden=orden,
                    examen=examen,
                    observaciones=f"Observación para {examen.nombre}",
                    estado=random.choice(['PENDIENTE', 'EN PROCESO', 'VALIDADO', 'ENTREGADO'])
                )
            
            if i < 5:  # Mostrar solo las primeras 5
                self.stdout.write(f'📋 Orden creada: {orden.codigo} - {orden.donante.primer_nombre} {orden.donante.primer_apellido}')
        
        self.stdout.write(f'✅ {cantidad} órdenes creadas')

    def crear_resultados(self, cantidad):
        """Crear resultados de prueba"""
        detalles_orden = list(DetalleOrden.objects.filter(estado__in=['EN PROCESO', 'VALIDADO']))
        
        if not detalles_orden:
            self.stdout.write('⚠️ No hay detalles de orden para crear resultados')
            return
        
        # Datos de ejemplo para diferentes tipos de exámenes
        parametros_por_examen = {
            'Hemograma Completo': [
                {'parametro': 'Hematíes', 'valor': '4.8', 'unidad': 'M/μL', 'rango_normal': '4.5-5.5', 'estado': 'normal'},
                {'parametro': 'Hemoglobina', 'valor': '14.2', 'unidad': 'g/dL', 'rango_normal': '13-17', 'estado': 'normal'},
                {'parametro': 'Leucocitos', 'valor': '7.5', 'unidad': 'K/μL', 'rango_normal': '4.5-11.0', 'estado': 'normal'},
                {'parametro': 'Plaquetas', 'valor': '250', 'unidad': 'K/μL', 'rango_normal': '150-450', 'estado': 'normal'}
            ],
            'Glucosa en Sangre': [
                {'parametro': 'Glucosa', 'valor': '95', 'unidad': 'mg/dL', 'rango_normal': '70-100', 'estado': 'normal'}
            ],
            'Perfil Lipídico': [
                {'parametro': 'Colesterol Total', 'valor': '180', 'unidad': 'mg/dL', 'rango_normal': '<200', 'estado': 'normal'},
                {'parametro': 'HDL', 'valor': '45', 'unidad': 'mg/dL', 'rango_normal': '>40', 'estado': 'normal'},
                {'parametro': 'LDL', 'valor': '110', 'unidad': 'mg/dL', 'rango_normal': '<100', 'estado': 'alto'},
                {'parametro': 'Triglicéridos', 'valor': '150', 'unidad': 'mg/dL', 'rango_normal': '<150', 'estado': 'normal'}
            ],
            'Creatinina': [
                {'parametro': 'Creatinina', 'valor': '1.1', 'unidad': 'mg/dL', 'rango_normal': '0.7-1.3', 'estado': 'normal'}
            ],
            'TSH': [
                {'parametro': 'TSH', 'valor': '2.5', 'unidad': 'mUI/L', 'rango_normal': '0.4-4.0', 'estado': 'normal'}
            ]
        }
        
        for i in range(cantidad):
            detalle = random.choice(detalles_orden)
            
            # Verificar si ya existe un resultado para este detalle
            if hasattr(detalle, 'resultado'):
                continue
            
            # Fecha de resultado
            fecha_resultado = date.today() - timedelta(days=random.randint(0, 7))
            
            resultado = Resultado.objects.create(
                resultado=detalle,
                observaciones=f"Resultado de {detalle.examen.nombre}",
                validado_por=random.choice(['Dr. García', 'Dr. López', 'Dr. Martínez', 'Dra. Rodríguez']),
                fecha_resultado=fecha_resultado,
                fecha_validacion=fecha_resultado if random.choice([True, False]) else None,
                estado=random.choice(['COMPLETADO', 'VALIDADO', 'EN PROCESO']),
                prioridad=random.choice(['normal', 'alta', 'media'])
            )
            
            # Crear detalles del resultado según el tipo de examen
            nombre_examen = detalle.examen.nombre
            parametros = parametros_por_examen.get(nombre_examen, [
                {'parametro': 'Parámetro General', 'valor': 'Normal', 'unidad': 'U', 'rango_normal': 'Normal', 'estado': 'normal'}
            ])
            
            for param in parametros:
                # Variar ligeramente los valores para hacerlos más realistas
                if param['parametro'] in ['Hematíes', 'Leucocitos', 'Plaquetas']:
                    valor = str(random.randint(int(float(param['valor']) * 0.9), int(float(param['valor']) * 1.1)))
                elif param['parametro'] in ['Hemoglobina', 'Glucosa', 'Creatinina']:
                    valor = str(round(random.uniform(float(param['valor']) * 0.9, float(param['valor']) * 1.1), 1))
                else:
                    valor = param['valor']
                
                ResultadoDetalle.objects.create(
                    resultado=resultado,
                    parametro=param['parametro'],
                    valor=valor,
                    unidad=param['unidad'],
                    rango_normal=param['rango_normal'],
                    estado=param['estado']
                )
            
            if i < 5:  # Mostrar solo los primeros 5
                self.stdout.write(f'📊 Resultado creado: {resultado.resultado.examen.nombre} - {resultado.estado}')
        
        self.stdout.write(f'✅ {cantidad} resultados creados') 