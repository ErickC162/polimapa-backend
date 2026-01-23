from sqlalchemy import text
from database import engine, SessionLocal, Base
import models

def reset_database():
    # 1. ELIMINAR TABLAS VIEJAS
    print("Eliminando tablas existentes...")
    # Orden específico para evitar conflictos de Foreign Keys
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception as e:
        print(f"⚠️  Advertencia al borrar: {e}")

    # 2. CREAR TABLAS NUEVAS
    print("Creando esquema nuevo (Usuarios, Edificios, Servicios)...")
    Base.metadata.create_all(bind=engine)

    # 3. INSERTAR DATOS
    db = SessionLocal()
    try:
        print("Insertando Edificios...")
        query_edificios = text("""
        INSERT INTO edificios (id,nombre, lat, lng, descripcion) VALUES
        (1,'Teatro Politécnico', -0.211513, -78.490174, 'Auditorio principal y eventos culturales.'),
        (2,'Museo', -0.211905, -78.490228, 'Museo de historia natural y fauna.'),
        (3,'Administración Central', -0.211543, -78.490604, 'Rectorado y oficinas administrativas.'),
        (4,'Casa Patrimonial', -0.212280, -78.491226, 'Edificio histórico patrimonial.'),
        (5,'Centro de Investigación de la Vivienda', -0.212149, -78.491636, 'Investigación en urbanismo y vivienda.'),
        (6,'Facultad de Ingeniería Civil', -0.211862, -78.491250, 'Estructuras, hidráulica y ambiental.'),
        (7,'Departamento de Ciencias Nucleares', -0.211401, -78.491786, 'Laboratorios de física nuclear.'),
        (9,'Laboratorio de Aguas y Microbiología', -0.211229, -78.491548, 'Análisis de calidad de agua.'),
        (10,'Ingeniería Hidráulica', -0.211398, -78.491245, 'Laboratorios de fluidos.'),
        (11,'Centro de Investigación y Control Ambiental', -0.211143, -78.491068, 'Estudios de impacto ambiental.'),
        (12,'Facultad de Ciencias', -0.210942, -78.489957, 'Matemática, Física y Química.'),
        (13,'Facultad de Ingeniería en Geología y Petróleos', -0.210620, -78.489541, 'Recursos terrestres e hidrocarburos.'),
        (14,'Departamento de Formación Básica', -0.210038, -78.490094, 'Aulas de nivelación y ciencias básicas.'),
        (15,'Facultad de Ingeniería Mecánica', -0.209754, -78.489858, 'Diseño mecánico y energía.'),
        (16,'Facultad de Ingeniería Eléctrica y Electrónica', -0.209257, -78.489496, 'Sistemas de potencia y control.'),
        (17,'Edificio Química-Eléctrica (Bloque 17)', -0.209566, -78.489308, 'Laboratorios compartidos.'),
        (18,'Edificio Química-Eléctrica (Bloque 18)', -0.209839, -78.489201, 'Aulas técnicas y laboratorios.'),
        (19,'Departamento Ciencias de Alimentos y Biotecnología', -0.210033, -78.489472, 'Procesamiento y bioprocesos.'),
        (20,'Facultad de Ingeniería en Sistemas', -0.210253, -78.489102, 'Ingeniería de Software y Computación.'),
        (21,'ESFOT', -0.210151, -78.488557, 'Escuela de Formación de Tecnólogos.'),
        (22,'Departamento de Metalurgia Extractiva', -0.209231, -78.487621, 'Procesamiento de minerales.'),
        (23,'Plaza EARME', -0.209625, -78.487060, 'Área de integración estudiantil.'),
        (24,'Procesos de Producción Mecánica', -0.209810, -78.487970, 'Talleres de manufactura.'),
        (25,'Laboratorio de Vehículos y Movilidad Sostenible', -0.209088, -78.486355, 'Ingeniería automotriz.'),
        (26,'EARME / CEC / Admin.', -0.209174, -78.486714, 'Aulas nuevas y educación continua.'),
        (27,'Centro de Investigación en Recursos Hídricos', -0.209907, -78.487481, 'Gestión del agua.'),
        (28,'Sede Ladrón de Guevara', -0.211698, -78.492881, 'Instalaciones externas.'),
        (29,'Servicios Generales', -0.211089, -78.491966, 'Mantenimiento e infraestructura.'),
        (30,'Estadio EPN', -0.211323, -78.489112, 'Estadio de fútbol y atletismo.'),
        (31,'Canchas Deportivas', -0.211146, -78.489676, 'Canchas de uso múltiple.'),
        (32,'Cancha de Mecánica', -0.209925, -78.489643, 'Área deportiva norte.'),
        (34,'Centro de Acopio y Residuos Sólidos', -0.211387, -78.488410, 'Gestión de residuos.'),
        (35,'Coro', -0.209767, -78.487468, 'Actividades culturales.'),
        (39,'Junior College / Eval. Interna', -0.208850, -78.486186, 'Oficinas administrativas.'),
        (40,'Gimnasio', -0.211937, -78.489874, 'Entrenamiento físico.');
        """)
        db.execute(query_edificios)

        print("🛠️  Insertando Servicios...")
        query_servicios = text("""
        INSERT INTO servicios (nombre, piso, edificio_id, popularidad, caps_comida_str, caps_estudio_str, caps_hobby_str) VALUES 
        ('DGIP', 'Subsuelo', 3, 2, '', '', ''),
        ('Biblioteca Central', 'PB', 3, 10, '', '1,2', ''),
        ('Área Administrativa', 'PB', 3, 1, '', '', ''),
        ('Rectorado', 'Piso 1', 3, 1, '', '', ''),
        ('Departamento de Ciencias Sociales', 'Piso 4', 3, 4, '', '5', ''),
        ('Departamento de Matemática', 'Piso 5 al 8', 3, 6, '', '5,2', ''),
        ('Club de Andinismo', 'Piso 8', 3, 7, '', '', '6,5'),
        ('Estación Astronómica', 'Piso 9', 3, 8, '', '4', '6'),
        ('Laboratorios de Civil', 'PB', 6, 6, '', '4', ''),
        ('Biblioteca de Civil', 'Piso 3', 6, 8, '', '1,2', ''),
        ('Asociación de Estudiantes Civil', 'Piso 3', 6, 7, '', '2', '6,4'),
        ('Aulas Civil', 'Piso 3 y 4', 6, 6, '', '5', ''),
        ('Centro de Educación Continua (CEC)', 'Piso 5', 6, 7, '', '5,2', ''),
        ('Cafetería Servicios Generales', 'Piso 1', 29, 8, '1,2', '', ''),
        ('Sala de Uso Múltiple', 'Piso 1', 29, 6, '', '2', '6'),
        ('Cafetería Alta', 'Piso 2', 29, 7, '2,4', '', ''),
        ('Biblioteca de Ciencias', 'Subsuelo', 12, 8, '', '1,2', ''),
        ('Laboratorio Materia Condensada', 'PB', 12, 5, '', '4', ''),
        ('Laboratorios de Cómputo', 'Piso 2', 12, 9, '', '4', '4'),
        ('MODEMAT', 'Piso 4 y 5', 12, 7, '', '5,4', ''),
        ('FEPON', 'Piso 1', 20, 9, '2', '2', '6'),
        ('Comedor Politécnico', 'Planta Baja', 20, 10, '1,3', '', ''),
        ('Biblioteca FIS', 'Piso 1', 20, 9, '', '1,2', ''),
        ('Laboratorios FIS', 'Piso 3', 20, 8, '', '4', ''),
        ('Aulas FIS', 'Piso 4', 20, 7, '', '5', ''),
        ('Asociación de Estudiantes (AEIS)', 'Subsuelo', 20, 8, '', '2', '4,6'),
        ('Laboratorio AEIS', 'Piso 5', 20, 7, '', '4,2', '4'),
        ('FABLAB', 'Subsuelo', 20, 8, '', '2,4', '6'),
        ('Estadio Politécnico', '-', 30, 9, '', '', '1,5'),
        ('Cancha Bombonera', '-', 21, 8, '', '', '1,3'),
        ('Espacios Verdes ESFOT', '-', 21, 8, '', '3', '6'),
        ('Cancha Mecánica', '-', 32, 7, '', '', '1,2'),
        ('Canchas Deportivas', '-', 31, 8, '', '', '2,3'),
        ('Gimnasio EPN', '-', 40, 9, '', '', '5'),
        ('Teatro Politécnico', '-', 1, 6, '', '', '6');
        """)
        db.execute(query_servicios)

        # 4. RESETEAR CONTADORES DE ID (Importante en PostgreSQL)
        print("Reseteando secuencias de IDs...")
        try:
            db.execute(text("SELECT setval(pg_get_serial_sequence('edificios', 'id'), (SELECT MAX(id) FROM edificios));"))
            db.execute(text("SELECT setval(pg_get_serial_sequence('servicios', 'id'), (SELECT MAX(id) FROM servicios));"))
        except Exception as e:
            print(f"Nota: Si usas SQLite puedes ignorar este error: {e}")

        db.commit()
        print("¡BASE DE DATOS REINICIADA Y POBLADA EXITOSAMENTE!")

    except Exception as e:
        db.rollback()
        print(f"Error crítico: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_database()