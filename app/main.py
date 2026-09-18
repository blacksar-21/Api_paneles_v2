from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db, engine

# ============================================================
# MODELOS SQLALCHEMY
# ============================================================

from app.models.models import (
    Base,
    Ubicacion as UbicacionModel,
    Fabricante as FabricanteModel,
    InstalacionSolar as InstalacionSolarModel,
    ModeloPanel as ModeloPanelModel,
    ModeloInversor as ModeloInversorModel,
    Panel as PanelModel,
    Inversor as InversorModel,
    MedicionEnergetica as MedicionEnergeticaModel,
    CondicionAmbiental as CondicionAmbientalModel,
    ConfiguracionInstalacion as ConfiguracionInstalacionModel
)

# ============================================================
# SCHEMAS PYDANTIC
# ============================================================

from app.schemas.schemas import (
    # Ubicaciones
    UbicacionCreate,
    Ubicacion,

    # Fabricantes
    FabricanteCreate,
    Fabricante,

    # Instalaciones
    InstalacionSolarCreate,
    InstalacionSolar,

    # Modelos de panel
    ModeloPanelCreate,
    ModeloPanel,

    # Modelos de inversor
    ModeloInversorCreate,
    ModeloInversor,

    # Paneles
    PanelCreate,
    Panel,

    # Inversores
    InversorCreate,
    Inversor,

    # Mediciones energéticas
    MedicionEnergeticaCreate,
    MedicionEnergetica,

    # Condiciones ambientales
    CondicionAmbientalCreate,
    CondicionAmbiental,

    # Configuración
    ConfiguracionInstalacionCreate,
    ConfiguracionInstalacion,

    # Asistente IA
    AsistenteChat,
    AsistenteRespuesta
)

# ============================================================
# ASISTENTE IA
# ============================================================

from app.ai.solar_assistant import asistente_solar


# ============================================================
# CREAR TABLAS
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# APLICACIÓN FASTAPI
# ============================================================

app = FastAPI(
    title="API Optimización Energética de Paneles Solares"
)


# ============================================================
# FUNCIÓN AUXILIAR
# ============================================================

def add_nombres_instalacion(
    objeto,
    db: Session
):
    """
    Agrega el nombre de la instalación a los objetos
    que poseen id_instalacion.
    """

    if hasattr(objeto, "id_instalacion"):

        instalacion = db.query(
            InstalacionSolarModel
        ).filter(
            InstalacionSolarModel.id_instalacion
            == objeto.id_instalacion
        ).first()

        if instalacion:

            # Diferentes schemas pueden utilizar
            # diferentes nombres para este campo.

            if hasattr(objeto, "instalacion_nombre"):
                objeto.instalacion_nombre = (
                    instalacion.nombre
                )

    return objeto


# ============================================================
# RUTA PRINCIPAL
# ============================================================

@app.get("/")
def root():

    return {
        "message": (
            "API de Optimización Energética "
            "de Paneles Solares funcionando correctamente"
        )
    }


# ============================================================
# UBICACIONES
# ============================================================

@app.get(
    "/ubicaciones",
    response_model=List[Ubicacion]
)
def listar_ubicaciones(
    db: Session = Depends(get_db)
):

    return db.query(
        UbicacionModel
    ).all()


@app.get(
    "/ubicaciones/{ubicacion_id}",
    response_model=Ubicacion
)
def obtener_ubicacion(
    ubicacion_id: int,
    db: Session = Depends(get_db)
):

    ubicacion = db.query(
        UbicacionModel
    ).filter(
        UbicacionModel.id_ubicacion == ubicacion_id
    ).first()

    if not ubicacion:

        raise HTTPException(
            status_code=404,
            detail="Ubicación no encontrada"
        )

    return ubicacion


@app.post(
    "/ubicaciones",
    response_model=Ubicacion,
    status_code=status.HTTP_201_CREATED
)
def crear_ubicacion(
    ubicacion: UbicacionCreate,
    db: Session = Depends(get_db)
):

    nueva_ubicacion = UbicacionModel(
        **ubicacion.model_dump()
    )

    db.add(nueva_ubicacion)
    db.commit()
    db.refresh(nueva_ubicacion)

    return nueva_ubicacion


# ============================================================
# FABRICANTES
# ============================================================

@app.get(
    "/fabricantes",
    response_model=List[Fabricante]
)
def listar_fabricantes(
    db: Session = Depends(get_db)
):

    return db.query(
        FabricanteModel
    ).all()


@app.get(
    "/fabricantes/{fabricante_id}",
    response_model=Fabricante
)
def obtener_fabricante(
    fabricante_id: int,
    db: Session = Depends(get_db)
):

    fabricante = db.query(
        FabricanteModel
    ).filter(
        FabricanteModel.id_fabricante == fabricante_id
    ).first()

    if not fabricante:

        raise HTTPException(
            status_code=404,
            detail="Fabricante no encontrado"
        )

    return fabricante


@app.post(
    "/fabricantes",
    response_model=Fabricante,
    status_code=status.HTTP_201_CREATED
)
def crear_fabricante(
    fabricante: FabricanteCreate,
    db: Session = Depends(get_db)
):

    nuevo_fabricante = FabricanteModel(
        **fabricante.model_dump()
    )

    db.add(nuevo_fabricante)
    db.commit()
    db.refresh(nuevo_fabricante)

    return nuevo_fabricante


# ============================================================
# INSTALACIONES SOLARES
# ============================================================

@app.get(
    "/instalaciones",
    response_model=List[InstalacionSolar]
)
def listar_instalaciones(
    db: Session = Depends(get_db)
):

    return db.query(
        InstalacionSolarModel
    ).all()


@app.get(
    "/instalaciones/{instalacion_id}",
    response_model=InstalacionSolar
)
def obtener_instalacion(
    instalacion_id: int,
    db: Session = Depends(get_db)
):

    instalacion = db.query(
        InstalacionSolarModel
    ).filter(
        InstalacionSolarModel.id_instalacion
        == instalacion_id
    ).first()

    if not instalacion:

        raise HTTPException(
            status_code=404,
            detail="Instalación no encontrada"
        )

    return instalacion


@app.post(
    "/instalaciones",
    response_model=InstalacionSolar,
    status_code=status.HTTP_201_CREATED
)
def crear_instalacion(
    instalacion: InstalacionSolarCreate,
    db: Session = Depends(get_db)
):

    nueva_instalacion = InstalacionSolarModel(
        **instalacion.model_dump()
    )

    db.add(nueva_instalacion)
    db.commit()
    db.refresh(nueva_instalacion)

    return nueva_instalacion


# ============================================================
# MODELOS DE PANELES
# ============================================================

@app.get(
    "/modelos-paneles",
    response_model=List[ModeloPanel]
)
def listar_modelos_paneles(
    db: Session = Depends(get_db)
):

    return db.query(
        ModeloPanelModel
    ).all()


@app.get(
    "/modelos-paneles/{modelo_id}",
    response_model=ModeloPanel
)
def obtener_modelo_panel(
    modelo_id: int,
    db: Session = Depends(get_db)
):

    modelo = db.query(
        ModeloPanelModel
    ).filter(
        ModeloPanelModel.id_modelo_panel == modelo_id
    ).first()

    if not modelo:

        raise HTTPException(
            status_code=404,
            detail="Modelo de panel no encontrado"
        )

    return modelo


@app.post(
    "/modelos-paneles",
    response_model=ModeloPanel,
    status_code=status.HTTP_201_CREATED
)
def crear_modelo_panel(
    modelo: ModeloPanelCreate,
    db: Session = Depends(get_db)
):

    nuevo_modelo = ModeloPanelModel(
        **modelo.model_dump()
    )

    db.add(nuevo_modelo)
    db.commit()
    db.refresh(nuevo_modelo)

    return nuevo_modelo


# ============================================================
# MODELOS DE INVERSORES
# ============================================================

@app.get(
    "/modelos-inversores",
    response_model=List[ModeloInversor]
)
def listar_modelos_inversores(
    db: Session = Depends(get_db)
):

    return db.query(
        ModeloInversorModel
    ).all()


@app.get(
    "/modelos-inversores/{modelo_id}",
    response_model=ModeloInversor
)
def obtener_modelo_inversor(
    modelo_id: int,
    db: Session = Depends(get_db)
):

    modelo = db.query(
        ModeloInversorModel
    ).filter(
        ModeloInversorModel.id_modelo_inversor
        == modelo_id
    ).first()

    if not modelo:

        raise HTTPException(
            status_code=404,
            detail="Modelo de inversor no encontrado"
        )

    return modelo


@app.post(
    "/modelos-inversores",
    response_model=ModeloInversor,
    status_code=status.HTTP_201_CREATED
)
def crear_modelo_inversor(
    modelo: ModeloInversorCreate,
    db: Session = Depends(get_db)
):

    nuevo_modelo = ModeloInversorModel(
        **modelo.model_dump()
    )

    db.add(nuevo_modelo)
    db.commit()
    db.refresh(nuevo_modelo)

    return nuevo_modelo


# ============================================================
# PANELES
# ============================================================

@app.get(
    "/paneles",
    response_model=List[Panel]
)
def listar_paneles(
    db: Session = Depends(get_db)
):

    return db.query(
        PanelModel
    ).all()


@app.get(
    "/paneles/{panel_id}",
    response_model=Panel
)
def obtener_panel(
    panel_id: int,
    db: Session = Depends(get_db)
):

    panel = db.query(
        PanelModel
    ).filter(
        PanelModel.id_panel == panel_id
    ).first()

    if not panel:

        raise HTTPException(
            status_code=404,
            detail="Panel no encontrado"
        )

    return panel


@app.post(
    "/paneles",
    response_model=Panel,
    status_code=status.HTTP_201_CREATED
)
def crear_panel(
    panel: PanelCreate,
    db: Session = Depends(get_db)
):

    nuevo_panel = PanelModel(
        **panel.model_dump()
    )

    db.add(nuevo_panel)
    db.commit()
    db.refresh(nuevo_panel)

    return nuevo_panel


# ============================================================
# INVERSORES
# ============================================================

@app.get(
    "/inversores",
    response_model=List[Inversor]
)
def listar_inversores(
    db: Session = Depends(get_db)
):

    return db.query(
        InversorModel
    ).all()


@app.get(
    "/inversores/{inversor_id}",
    response_model=Inversor
)
def obtener_inversor(
    inversor_id: int,
    db: Session = Depends(get_db)
):

    inversor = db.query(
        InversorModel
    ).filter(
        InversorModel.id_inversor == inversor_id
    ).first()

    if not inversor:

        raise HTTPException(
            status_code=404,
            detail="Inversor no encontrado"
        )

    return inversor


@app.post(
    "/inversores",
    response_model=Inversor,
    status_code=status.HTTP_201_CREATED
)
def crear_inversor(
    inversor: InversorCreate,
    db: Session = Depends(get_db)
):

    nuevo_inversor = InversorModel(
        **inversor.model_dump()
    )

    db.add(nuevo_inversor)
    db.commit()
    db.refresh(nuevo_inversor)

    return nuevo_inversor


# ============================================================
# MEDICIONES ENERGÉTICAS
# ============================================================

@app.get(
    "/mediciones-energeticas",
    response_model=List[MedicionEnergetica]
)
def listar_mediciones(
    db: Session = Depends(get_db)
):

    mediciones = db.query(
        MedicionEnergeticaModel
    ).all()

    return [
        add_nombres_instalacion(
            medicion,
            db
        )
        for medicion in mediciones
    ]


@app.get(
    "/mediciones-energeticas/{medicion_id}",
    response_model=MedicionEnergetica
)
def obtener_medicion(
    medicion_id: int,
    db: Session = Depends(get_db)
):

    medicion = db.query(
        MedicionEnergeticaModel
    ).filter(
        MedicionEnergeticaModel.id_medicion
        == medicion_id
    ).first()

    if not medicion:

        raise HTTPException(
            status_code=404,
            detail="Medición energética no encontrada"
        )

    return add_nombres_instalacion(
        medicion,
        db
    )


@app.post(
    "/mediciones-energeticas",
    response_model=MedicionEnergetica,
    status_code=status.HTTP_201_CREATED
)
def crear_medicion(
    medicion: MedicionEnergeticaCreate,
    db: Session = Depends(get_db)
):

    nueva_medicion = MedicionEnergeticaModel(
        **medicion.model_dump()
    )

    db.add(nueva_medicion)
    db.commit()
    db.refresh(nueva_medicion)

    return add_nombres_instalacion(
        nueva_medicion,
        db
    )


# ============================================================
# CONDICIONES AMBIENTALES
# ============================================================

@app.get(
    "/condiciones-ambientales",
    response_model=List[CondicionAmbiental]
)
def listar_condiciones(
    db: Session = Depends(get_db)
):

    condiciones = db.query(
        CondicionAmbientalModel
    ).all()

    return [
        add_nombres_instalacion(
            condicion,
            db
        )
        for condicion in condiciones
    ]


@app.get(
    "/condiciones-ambientales/{condicion_id}",
    response_model=CondicionAmbiental
)
def obtener_condicion(
    condicion_id: int,
    db: Session = Depends(get_db)
):

    condicion = db.query(
        CondicionAmbientalModel
    ).filter(
        CondicionAmbientalModel.id_condicion
        == condicion_id
    ).first()

    if not condicion:

        raise HTTPException(
            status_code=404,
            detail="Condición ambiental no encontrada"
        )

    return add_nombres_instalacion(
        condicion,
        db
    )


@app.post(
    "/condiciones-ambientales",
    response_model=CondicionAmbiental,
    status_code=status.HTTP_201_CREATED
)
def crear_condicion(
    condicion: CondicionAmbientalCreate,
    db: Session = Depends(get_db)
):

    nueva_condicion = CondicionAmbientalModel(
        **condicion.model_dump()
    )

    db.add(nueva_condicion)
    db.commit()
    db.refresh(nueva_condicion)

    return add_nombres_instalacion(
        nueva_condicion,
        db
    )


# ============================================================
# CONFIGURACIONES DE INSTALACIÓN
# ============================================================

@app.get(
    "/configuraciones-instalacion",
    response_model=List[ConfiguracionInstalacion]
)
def listar_configuraciones(
    db: Session = Depends(get_db)
):

    configuraciones = db.query(
        ConfiguracionInstalacionModel
    ).all()

    return [
        add_nombres_instalacion(
            configuracion,
            db
        )
        for configuracion in configuraciones
    ]


@app.get(
    "/configuraciones-instalacion/{configuracion_id}",
    response_model=ConfiguracionInstalacion
)
def obtener_configuracion(
    configuracion_id: int,
    db: Session = Depends(get_db)
):

    configuracion = db.query(
        ConfiguracionInstalacionModel
    ).filter(
        ConfiguracionInstalacionModel.id_configuracion
        == configuracion_id
    ).first()

    if not configuracion:

        raise HTTPException(
            status_code=404,
            detail="Configuración no encontrada"
        )

    return add_nombres_instalacion(
        configuracion,
        db
    )


@app.post(
    "/configuraciones-instalacion",
    response_model=ConfiguracionInstalacion,
    status_code=status.HTTP_201_CREATED
)
def crear_configuracion(
    configuracion: ConfiguracionInstalacionCreate,
    db: Session = Depends(get_db)
):

    nueva_configuracion = ConfiguracionInstalacionModel(
        **configuracion.model_dump()
    )

    db.add(nueva_configuracion)
    db.commit()
    db.refresh(nueva_configuracion)

    return add_nombres_instalacion(
        nueva_configuracion,
        db
    )


# ============================================================
# ASISTENTE DE INTELIGENCIA ARTIFICIAL
# ============================================================

@app.post(
    "/asistente/chat",
    response_model=AsistenteRespuesta
)
async def asistente_chat(
    chat: AsistenteChat
):

 try:

     respuesta = await asistente_solar.preguntar(
        mensaje=chat.mensaje,
        conversation_id=chat.conversation_id
    )

     return {
        "respuesta": respuesta,
        "conversation_id": chat.conversation_id
    }

 except Exception as error:
    print("❌ ERROR DEL ASISTENTE:", repr(error))

    raise HTTPException(
        status_code=500,
        detail=f"Error del asistente: {str(error)}"
    )

# ============================================================
# LIMPIAR CONVERSACIÓN DEL ASISTENTE
# ============================================================

@app.delete(
    "/asistente/chat/{conversation_id}"
)
def limpiar_chat(
    conversation_id: str
):

    asistente_solar.limpiar_conversacion(
        conversation_id
    )

    return {
        "message": "Conversación eliminada correctamente",
        "conversation_id": conversation_id
    }


# ============================================================
# EJECUCIÓN DIRECTA
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )