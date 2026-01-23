import pandas as pd
import random

# --- 1. CONFIGURACIÓN DE CATEGORÍAS ---
CAT_COMIDA  = {0: "Nada", 1: "Almuerzo", 2: "Rapida", 3: "Saludable", 4: "Cafes"}
CAT_ESTUDIO = {0: "Nada", 1: "Biblioteca", 2: "Grupal", 3: "AireLibre", 4: "Lab", 5: "Aulas"}
CAT_HOBBY   = {0: "Nada", 1: "Futbol", 2: "Basquet", 3: "Ecuavoley", 4: "Gaming", 5: "Gym", 6: "Relax"}

AFINIDAD_HOBBY = {1: [2, 3], 2: [1, 3], 3: [1, 2], 6: [3, 4]}

# --- 2. LISTA MAESTRA DE SERVICIOS (Toda la EPN según tu SQL) ---
# Formato: (Nombre, [Lista Comida], [Lista Estudio], [Lista Hobby], Popularidad)
SERVICIOS_REALES = [
    ("DGIP", [], [], [], 2),
    ("Biblioteca Central", [], [1, 2], [], 10),
    ("Área Administrativa", [], [], [], 1),
    ("Rectorado", [], [], [], 1),
    ("Departamento de Ciencias Sociales", [], [5], [], 4),
    ("Departamento de Matemática", [], [5, 2], [], 6),
    ("Club de Andinismo", [], [], [6, 5], 7),
    ("Estación Astronómica", [], [4], [6], 8),
    ("Laboratorios de Civil", [], [4], [], 6),
    ("Biblioteca de Civil", [], [1, 2], [], 8),
    ("Asociación de Estudiantes Civil", [], [2], [6, 4], 7),
    ("Aulas Civil", [], [5], [], 6),
    ("Centro de Educación Continua (CEC)", [], [5, 2], [], 7),
    ("Cafetería Servicios Generales", [1, 2], [], [], 8),
    ("Sala de Uso Múltiple", [], [2], [6], 6),
    ("Cafetería Alta", [2, 4], [], [], 7),
    ("Biblioteca de Ciencias", [], [1, 2], [], 8),
    ("Laboratorio Materia Condensada", [], [4], [], 5),
    ("Laboratorios de Cómputo", [], [4], [4], 9),
    ("MODEMAT", [], [5, 4], [], 7),
    ("FEPON", [2], [2], [6], 9),
    ("Comedor Politécnico", [1, 3], [], [], 10),
    ("Biblioteca FIS", [], [1, 2], [], 9),
    ("Laboratorios FIS", [], [4], [], 8),
    ("Aulas FIS", [], [5], [], 7),
    ("Asociación de Estudiantes (AEIS)", [], [2], [4, 6], 8),
    ("Laboratorio AEIS", [], [4, 2], [4], 7),
    ("FABLAB", [], [2, 4], [6], 8),
    ("Estadio Politécnico", [], [], [1, 5], 9),
    ("Cancha Bombonera", [], [], [1, 3], 8),
    ("Espacios Verdes ESFOT", [], [3], [6], 8),
    ("Cancha Mecánica", [], [], [1, 2], 7),
    ("Canchas Deportivas", [], [], [2, 3], 8),
    ("Gimnasio EPN", [], [], [5], 9),
    ("Teatro Politécnico", [], [], [6], 6)
]

def calcular_score_target(u_c, u_e, u_h, caps, pop):
    cap_c, cap_e, cap_h = caps
    score = pop
    if u_c > 0 and u_c in cap_c: score += 35
    if u_e > 0 and u_e in cap_e: score += 35
    if u_h > 0 and u_h in cap_h: score += 35
    if u_h in AFINIDAD_HOBBY and set(cap_h).intersection(AFINIDAD_HOBBY[u_h]): score += 15
    return max(0, min(100, score + random.randint(-2, 2)))

data_train = []
# NOMBRES DE COLUMNAS QUE USAREMOS SIEMPRE
COLUMNAS = ['u_comida', 'u_estudio', 'u_hobby', 'match_comida', 'match_estudio', 'match_hobby', 'match_afinidad', 'popularidad', 'score']

print("Generando dataset sintético...")
for _ in range(10000):
    uc, ue, uh = [random.choice(list(c.keys())) for c in [CAT_COMIDA, CAT_ESTUDIO, CAT_HOBBY]]
    serv = random.choice(SERVICIOS_REALES)
    _, c_c, c_e, c_h, pop = serv
    
    features = [
        uc, ue, uh,
        1 if uc in c_c else 0,
        1 if ue in c_e else 0,
        1 if uh in c_h else 0,
        1 if uh in AFINIDAD_HOBBY and set(c_h).intersection(AFINIDAD_HOBBY[uh]) else 0,
        pop
    ]
    target = calcular_score_target(uc, ue, uh, (c_c, c_e, c_h), pop)
    data_train.append(features + [target])

df = pd.DataFrame(data_train, columns=COLUMNAS)
df.to_csv('dataset_servicios_inteligente.csv', index=False)
print("Hecho: dataset_servicios_inteligente.csv")