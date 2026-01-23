import pandas as pd
import random

# --- 1. DEFINICIONES DE CATEGORÍAS (Tu lógica de negocio) ---
CAT_COMIDA  = {0: "Nada", 1: "Almuerzo", 2: "Rapida", 3: "Saludable", 4: "Cafes"}
CAT_ESTUDIO = {0: "Nada", 1: "Biblioteca", 2: "Grupal", 3: "AireLibre", 4: "Lab", 5: "Aulas"}
CAT_HOBBY   = {0: "Nada", 1: "Futbol", 2: "Basquet", 3: "Ecuavoley", 4: "Gaming", 5: "Gym", 6: "Relax"}

# Afinidades para dar puntos extra (Ej: Si te gusta Futbol, te puede gustar Basquet)
AFINIDAD_HOBBY = {
    1: [2, 3], # Futbol -> Basquet, Ecuavoley
    2: [1, 3], # Basquet -> Futbol, Ecuavoley
    3: [1, 2], # Ecuavoley -> Futbol, Basquet
    6: [3, 4]  # Relax -> Ecuavoley, Gaming
}

# --- 2. LISTA MAESTRA DE SERVICIOS (Basada EXACTAMENTE en tu SQL) ---
# Formato: (Nombre, [Lista Comida], [Lista Estudio], [Lista Hobby], Popularidad)
SERVICIOS_REALES = [
    # -- ADMINISTRACIÓN --
    ("DGIP",                            [], [], [], 2),
    ("Biblioteca Central",              [], [1, 2], [], 10),
    ("Área Administrativa",             [], [], [], 1),
    ("Rectorado",                       [], [], [], 1),
    ("Departamento de Ciencias Sociales",[], [5], [], 4),
    ("Departamento de Matemática",      [], [5, 2], [], 6),
    ("Club de Andinismo",               [], [], [6, 5], 7),
    ("Estación Astronómica",            [], [4], [6], 8),

    # -- CIVIL --
    ("Laboratorios de Civil",           [], [4], [], 6),
    ("Biblioteca de Civil",             [], [1, 2], [], 8),
    ("Asociación de Estudiantes Civil", [], [2], [6, 4], 7),
    ("Aulas Civil",                     [], [5], [], 6),
    ("Centro de Educación Continua (CEC)", [], [5, 2], [], 7),

    # -- SERVICIOS GENERALES --
    ("Cafetería Servicios Generales",   [1, 2], [], [], 8),
    ("Sala de Uso Múltiple",            [], [2], [6], 6),
    ("Cafetería Alta",                  [2, 4], [], [], 7),

    # -- CIENCIAS --
    ("Biblioteca de Ciencias",          [], [1, 2], [], 8),
    ("Laboratorio Materia Condensada",  [], [4], [], 5),
    ("Laboratorios de Cómputo",         [], [4], [4], 9),
    ("MODEMAT",                         [], [5, 4], [], 7),

    # -- SISTEMAS (FIS) --
    ("FEPON",                           [2], [2], [6], 9),
    ("Comedor Politécnico",             [1, 3], [], [], 10),
    ("Biblioteca FIS",                  [], [1, 2], [], 9),
    ("Laboratorios FIS",                [], [4], [], 8),
    ("Aulas FIS",                       [], [5], [], 7),
    ("Asociación de Estudiantes (AEIS)",[], [2], [4, 6], 8),
    ("Laboratorio AEIS",                [], [4, 2], [4], 7),
    ("FABLAB",                          [], [2, 4], [6], 8),

    # -- DEPORTES --
    ("Estadio Politécnico",             [], [], [1, 5], 9),
    ("Cancha Bombonera",                [], [], [1, 3], 8),
    ("Espacios Verdes ESFOT",           [], [3], [6], 8),
    ("Cancha Mecánica",                 [], [], [1, 2], 7),
    ("Canchas Deportivas",              [], [], [2, 3], 8),
    ("Gimnasio EPN",                    [], [], [5], 9),
    ("Teatro Politécnico",              [], [], [6], 6)
]

def calcular_score_inteligente(u_c, u_e, u_h, caps, popularidad):
    cap_c, cap_e, cap_h = caps
    score = 0
    
    # 1. Match Directo (Puntos fuertes)
    if u_c > 0 and u_c in cap_c: score += 30
    if u_e > 0 and u_e in cap_e: score += 30
    if u_h > 0 and u_h in cap_h: score += 30
    
    # 2. Match por Afinidad (Puntos extra)
    # Si el usuario quiere un hobby y el lugar tiene hobbies relacionados
    if u_h in AFINIDAD_HOBBY:
        interseccion = set(cap_h).intersection(AFINIDAD_HOBBY[u_h])
        if interseccion:
            score += 15
            
    # 3. Factor Popularidad (Base)
    score += popularidad
    
    # 4. Penalización si no hay NADA que hacer
    if score == popularidad: # Solo sumó popularidad, nada más
         score = max(0, score - 5) # Reducimos un poco para que no aparezcan arriba por error

    # 5. Ruido Aleatorio (Para que no sea robótico siempre igual)
    score += random.randint(-3, 3)
    
    return max(0, min(100, score))

data_train = []
print(f"Generando dataset con {len(SERVICIOS_REALES)} lugares reales...")

# Generamos 40,000 registros sintéticos para que la IA aprenda bien los patrones
for _ in range(40000):
    # Simular un Usuario con gustos aleatorios
    uc = random.choice(list(CAT_COMIDA.keys()))
    ue = random.choice(list(CAT_ESTUDIO.keys()))
    uh = random.choice(list(CAT_HOBBY.keys()))
    
    # Elegir un lugar aleatorio del campus
    serv = random.choice(SERVICIOS_REALES)
    nombre, c_c, c_e, c_h, pop = serv
    
    # Calcular Features (Inputs para la IA)
    mc = 1 if uc in c_c else 0
    me = 1 if ue in c_e else 0
    mh = 1 if uh in c_h else 0
    
    maf_h = 0
    if uh in AFINIDAD_HOBBY and set(c_h).intersection(AFINIDAD_HOBBY[uh]):
        maf_h = 1
        
    # Calcular el Score Real (Target) usando nuestra lógica
    target = calcular_score_inteligente(uc, ue, uh, (c_c, c_e, c_h), pop)
    
    # Guardar fila
    data_train.append([uc, ue, uh, mc, me, mh, maf_h, pop, target])

# Guardar CSV
df = pd.DataFrame(data_train, columns=['uc','ue','uh','mc','me','mh','maf_h','pop','score'])
df.to_csv('dataset_servicios_inteligente.csv', index=False)
print("Dataset generado exitosamente: dataset_servicios_inteligente.csv")