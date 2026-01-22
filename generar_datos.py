import pandas as pd
import random


SERVICIOS_REALES = [
    # --- ADMINISTRACIÓN CENTRAL (Edif 3) ---
    ("DGIP", 0, 0, 0),
    ("Biblioteca Central", 0, 1, 0),
    ("Área Administrativa", 0, 0, 0),
    ("Rectorado", 0, 0, 0),
    ("Sala de Consejo Politécnico", 0, 0, 0),
    ("Vicerrectorados", 0, 0, 0),
    ("Dirección Financiera", 0, 0, 0),
    ("Dirección de Talento Humano", 0, 0, 0),
    ("Departamento de Ciencias Sociales", 0, 1, 0),
    ("Departamento de Matemática", 0, 1, 0),
    ("Club de Andinismo", 0, 0, 1),
    ("Estación Astronómica", 0, 1, 1),

    # --- INGENIERÍA CIVIL (Edif 6) ---
    ("Laboratorios de Civil", 0, 1, 0),
    ("Sección Construcciones Civiles", 0, 0, 0),
    ("Departamento de Física", 0, 1, 0),
    ("Secretaría y Coordinación Civil", 0, 0, 0),
    ("Biblioteca de Civil", 0, 1, 0),
    ("Asociación de Estudiantes Civil", 0, 0, 1),
    ("Aulas Civil", 0, 1, 0),
    ("Sala de Conferencias Civil", 0, 0, 0),
    ("Centro de Educación Continua (CEC)", 0, 1, 0),
    ("Instituto Geofísico", 0, 1, 0),

    # --- SERVICIOS GENERALES (Edif 29) ---
    ("Bodegas", 0, 0, 0),
    ("Taller de Carpintería", 0, 0, 0),
    ("Taller de Mecánica", 0, 0, 0),
    ("Taller Eléctrico", 0, 0, 0),
    ("Cafetería Servicios Generales", 1, 0, 0),
    ("Sala de Uso Múltiple", 0, 0, 1),
    ("Sala de Reuniones SG", 0, 0, 0),
    ("Cafetería Alta", 1, 0, 0),

    # --- CIENCIAS (Edif 12) ---
    ("Biblioteca de Ciencias", 0, 1, 0),
    ("Laboratorio Materia Condensada", 0, 1, 0),
    ("Administración Facultad Ciencias", 0, 0, 0),
    ("Laboratorios de Cómputo Ciencias", 0, 1, 0),
    ("Área de TICs", 0, 0, 0),
    ("Oficinas Profesores Economía", 0, 0, 0),
    ("MODEMAT", 0, 1, 0),
    ("Asociación Estudiantes Ciencias", 0, 0, 1),

    # --- SISTEMAS (FIS - Edif 20) ---
    ("FEPON", 1, 1, 1), # Comodín
    ("Bienestar Politécnico (FIS)", 0, 0, 0),
    ("Comedor Politécnico", 1, 0, 0),
    ("Biblioteca FIS", 0, 1, 0),
    ("Decanato y Subdecanato FIS", 0, 0, 0),
    ("Jefatura DICC", 0, 0, 0),
    ("Secretarías FIS", 0, 0, 0),
    ("Oficinas Profesores FIS", 0, 0, 0),
    ("Laboratorios FIS", 0, 1, 0),
    ("Aulas FIS", 0, 1, 0),
    ("Sala de Grados FIS", 0, 0, 0),
    ("Asociación Estudiantes Sistemas (AEIS)", 0, 0, 1),
    ("Laboratorio AEIS", 0, 1, 1),

    # --- OTROS EDIFICIOS Y ZONAS ---
    ("Acelerador de Electrones", 0, 1, 0),
    ("Aulas CEC (Ladrón de Guevara)", 0, 1, 0),
    ("Estadio Politécnico", 0, 0, 1),
    ("Cancha Bombonera", 0, 0, 1),
    ("Aulas ESFOT", 0, 1, 0),
    ("Espacios Verdes ESFOT", 0, 0, 1),
    ("Cancha Mecánica", 0, 0, 1),
    ("Canchas de Voley", 0, 0, 1),
    ("Canchas de Basket", 0, 0, 1),
    ("Gimnasio EPN", 0, 0, 1),
    ("Teatro Politécnico", 0, 0, 0),
    ("Museo EPN", 0, 0, 0),
    
    # --- ASOCIACIONES GENERALES ---
    ("Asociación Mecánica", 0, 0, 1),
    ("Asociación Eléctrica", 0, 0, 1),
    ("Asociación Geología", 0, 0, 1),
    ("Asociación ESFOT", 0, 0, 1),
    ("Asociación Administrativas", 0, 0, 1),
    
    # --- EDIFICIO 26 (ADMINISTRATIVAS) ---
    ("Dirección Bienestar Politécnico", 0, 0, 0),
    ("Auditorios CEC", 0, 1, 0)
]

def calcular_match(usuario, servicio):
    u_comida, u_estudio, u_hobby = usuario
    _, s_comida, s_estudio, s_hobby = servicio
    
    score = 0
    
    # Sumar puntos si hay coincidencia
    if u_comida > 0 and s_comida == 1: score += u_comida * 18
    if u_estudio > 0 and s_estudio == 1: score += u_estudio * 18
    if u_hobby > 0 and s_hobby == 1: score += u_hobby * 18

    # PENALIZACIÓN FUERTE para lugares que no ofrecen nada de interés (0,0,0)
    # Esto asegura que Secretarías y Rectorado queden al fondo de la lista
    if s_comida == 0 and s_estudio == 0 and s_hobby == 0:
        score -= 50  # Penalización severa
        
    # Ruido aleatorio para realismo
    score += random.randint(-5, 5)
    
    # Limitar entre 0 y 100
    return max(0, min(100, score))

data = []
print(f"Generando datos con {len(SERVICIOS_REALES)} servicios (incluyendo administrativos)...")

for _ in range(25000):
    # Simulamos gustos de usuario (0 a 5)
    u_c = random.randint(0, 5)
    u_e = random.randint(0, 5)
    u_h = random.randint(0, 5)
    
    # Elegimos un servicio al azar
    servicio = random.choice(SERVICIOS_REALES)
    
    # Calculamos match
    score = calcular_match((u_c, u_e, u_h), servicio)
    
    # Guardamos vectores: [Gustos] + [Flags Servicio] -> [Score]
    data.append([
        u_c, u_e, u_h, 
        servicio[1], servicio[2], servicio[3], 
        score
    ])

df = pd.DataFrame(data, columns=['u_comida','u_estudio','u_hobby','s_comida','s_estudio','s_hobby','match_score'])
df.to_csv('dataset_servicios_epn_completo.csv', index=False)
print("Dataset generado: dataset_servicios_epn_completo.csv")