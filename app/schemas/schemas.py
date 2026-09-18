from pydantic import BaseModel, Field, PositiveFloat, model_validator
from datetime import date, datetime
from typing import Optional


# ============ UBICACIONES ============
class UbicacionBase(BaseModel):
    nombre_ubicacion: str
    direccion: str
    latitud: float = Field(ge=-90, le=90)
    longitud: float = Field(ge=-180, le=180)

class UbicacionCreate(UbicacionBase):
    pass

class Ubicacion(UbicacionBase):
    id_ubicacion: int

    class Config:
        from_attributes = True


# ============ FABRICANTES ============
class FabricanteBase(BaseModel):
    nombre: str

class FabricanteCreate(FabricanteBase):
    pass

class Fabricante(FabricanteBase):
    id_fabricante: int

    class Config:
        from_attributes = True


# ============ INSTALACIONES ============
class InstalacionSolarBase(BaseModel):
    id_ubicacion: int
    nombre: str
    fecha_instalacion: date
    estado: str = Field(pattern="^(Activa|Inactiva|Mantenimiento)$")

class InstalacionSolarCreate(InstalacionSolarBase):
    pass

class InstalacionSolar(InstalacionSolarBase):
    id_instalacion: int
    ubicacion_nombre: Optional[str] = None

    class Config:
        from_attributes = True


# ============ MODELOS DE PANELES ============
class ModeloPanelBase(BaseModel):
    id_fabricante: int
    modelo: str
    potencia_nominal_w: PositiveFloat
    eficiencia_nominal: float = Field(gt=0, le=100)
    voltaje_nominal_v: PositiveFloat
    corriente_nominal_a: PositiveFloat

class ModeloPanelCreate(ModeloPanelBase):
    pass

class ModeloPanel(ModeloPanelBase):
    id_modelo_panel: int
    fabricante_nombre: Optional[str] = None

    class Config:
        from_attributes = True


# ============ MODELOS DE INVERSORES ============
class ModeloInversorBase(BaseModel):
    id_fabricante: int
    modelo: str
    potencia_nominal_w: PositiveFloat
    eficiencia_nominal: float = Field(gt=0, le=100)
    voltaje_maximo_v: PositiveFloat

class ModeloInversorCreate(ModeloInversorBase):
    pass

class ModeloInversor(ModeloInversorBase):
    id_modelo_inversor: int
    fabricante_nombre: Optional[str] = None

    class Config:
        from_attributes = True


# ============ PANELES ============
class PanelBase(BaseModel):
    id_instalacion: int
    id_modelo_panel: int
    numero_serie: str
    fecha_instalacion: date
    estado: str = Field(pattern="^(Activo|Inactivo|Mantenimiento)$")

class PanelCreate(PanelBase):
    pass

class Panel(PanelBase):
    id_panel: int
    instalacion_nombre: Optional[str] = None
    modelo_panel_nombre: Optional[str] = None

    class Config:
        from_attributes = True


# ============ INVERSORES ============
class InversorBase(BaseModel):
    id_instalacion: int
    id_modelo_inversor: int
    numero_serie: str
    fecha_instalacion: date
    estado: str = Field(pattern="^(Activo|Inactivo|Mantenimiento)$")

class InversorCreate(InversorBase):
    pass

class Inversor(InversorBase):
    id_inversor: int
    instalacion_nombre: Optional[str] = None
    modelo_inversor_nombre: Optional[str] = None

    class Config:
        from_attributes = True


# ============ MEDICIONES ENERGÉTICAS ============
class MedicionEnergeticaBase(BaseModel):
    id_instalacion: int
    fecha_hora: datetime
    energia_generada_kwh: float = Field(ge=0)
    energia_consumida_kwh: float = Field(ge=0)

class MedicionEnergeticaCreate(MedicionEnergeticaBase):
    pass

class MedicionEnergetica(MedicionEnergeticaBase):
    id_medicion: int
    instalacion_nombre: Optional[str] = None

    class Config:
        from_attributes = True


# ============ CONDICIONES AMBIENTALES ============
class CondicionAmbientalBase(BaseModel):
    id_instalacion: int
    fecha_hora: datetime
    radiacion_solar_w_m2: float = Field(ge=0)
    temperatura_c: float
    humedad_porcentaje: float = Field(ge=0, le=100)
    velocidad_viento_m_s: float = Field(ge=0)

class CondicionAmbientalCreate(CondicionAmbientalBase):
    pass

class CondicionAmbiental(CondicionAmbientalBase):
    id_condicion: int
    instalacion_nombre: Optional[str] = None

    class Config:
        from_attributes = True


# ============ CONFIGURACIONES DE INSTALACIÓN ============
class ConfiguracionInstalacionBase(BaseModel):
    id_instalacion: int
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    inclinacion_grados: float = Field(ge=0, le=90)
    azimut_grados: float = Field(ge=0, lt=360)

    @model_validator(mode='after')
    def validate_fechas(self):
        if self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValueError('fecha_fin debe ser mayor o igual a fecha_inicio')
        return self

class ConfiguracionInstalacionCreate(ConfiguracionInstalacionBase):
    pass

class ConfiguracionInstalacion(ConfiguracionInstalacionBase):
    id_configuracion: int
    instalacion_nombre: Optional[str] = None

    class Config:
        from_attributes = True

class AsistenteChat(BaseModel):
    mensaje: str = Field(
        min_length=1,
        max_length=5000
    )

    conversation_id: str = Field(
        default="default",
        min_length=1,
        max_length=200
    )


class AsistenteRespuesta(BaseModel):
    respuesta: str
    conversation_id: str