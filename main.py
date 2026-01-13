# ... (Imports y setup igual que antes)

@app.get("/setup_datos_iniciales")
def setup_db(db: Session = Depends(get_db)):
    if db.query(models.EdificioDB).first():
        return {"msg": "La base de datos ya tiene datos."}
    
    # 1. Crear Edificios (AHORA SON NEUTROS)
    biblio = models.EdificioDB(nombre="Biblioteca Central", lat=-0.2110, lng=-78.4910, descripcion="Zona de silencio.")
    comedor = models.EdificioDB(nombre="Comedor Politécnico", lat=-0.2100, lng=-78.4900, descripcion="Almuerzos.")
    aso = models.EdificioDB(nombre="Aso Sistemas", lat=-0.2120, lng=-78.4920, descripcion="Gaming y PC.")
    
    db.add_all([biblio, comedor, aso])
    db.commit() 
    
    # 2. Agregar Servicios CON SUS ETIQUETAS
    servicios = [
        # La biblio tiene servicios de estudio
        models.ServicioDB(nombre="Cubículos", edificio_id=biblio.id, es_lugar_estudio=True),
        models.ServicioDB(nombre="Wifi", edificio_id=biblio.id, es_lugar_estudio=True),
        
        # El comedor tiene servicio de comida
        models.ServicioDB(nombre="Almuerzos", edificio_id=comedor.id, es_lugar_comida=True),
        
        # La aso tiene comida (bar) Y hobby (arcade) Y estudio (PC) -> ¡MIXTO!
        models.ServicioDB(nombre="Bar de Snacks", edificio_id=aso.id, es_lugar_comida=True),
        models.ServicioDB(nombre="Arcade", edificio_id=aso.id, es_lugar_hobby=True),
        models.ServicioDB(nombre="Impresiones", edificio_id=aso.id, es_lugar_estudio=True)
    ]
    
    db.add_all(servicios)
    
    # 3. Eventos
    ev = models.EventoDB(nombre="Torneo FC26", edificio_id=aso.id, tipo_evento="hobby")
    db.add(ev)
    
    db.commit()
    return {"msg": "Datos cargados: Etiquetas movidas a Servicios correctamente."}