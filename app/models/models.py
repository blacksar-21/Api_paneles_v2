from sqlalchemy import (
    Column, BigInteger, String, Date, DateTime, 
    Numeric, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database.database import Base


class Ubicacion(Base):
    __tablename__ = "ubicaciones"

    id_ubicacion = Column(BigInteger, primary_key=True, autoincrement=True)
    nombre_ubicacion = Column(String(100), nullable=False)
    direccion = Column(String(200), nullable=False)
    latitud = Column(Numeric(9, 6), nullable=False)
    longitud = Column(Numeric(9, 6), nullable=False)

    instalaciones = relationship("InstalacionSolar", back_populates="ubicacion")


class Fabricante(Base):
    __tablename__ = "fabricantes"

    id_fabricante = Column(BigInteger, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)

    modelos_paneles = relationship("ModeloPanel", back_populates="fabricante")
    modelos_inversores = relationship("ModeloInversor", back_populates="fabricante")


class InstalacionSolar(Base):
    __tablename__ = "instalaciones_solares"

    id_instalacion = Column(BigInteger, primary_key=True, autoincrement=True)
    id_ubicacion = Column(BigInteger, ForeignKey("ubicaciones.id_ubicacion", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    nombre = Column(String(100), nullable=False)
    fecha_instalacion = Column(Date, nullable=False)
    estado = Column(String(20), nullable=False)

    ubicacion = relationship("Ubicacion", back_populates="instalaciones")
    paneles = relationship("Panel", back_populates="instalacion")
    inversores = relationship("Inversor", back_populates="instalacion")
    mediciones = relationship("MedicionEnergetica", back_populates="instalacion")
    condiciones = relationship("CondicionAmbiental", back_populates="instalacion")
    configuraciones = relationship("ConfiguracionInstalacion", back_populates="instalacion")


class ModeloPanel(Base):
    __tablename__ = "modelos_paneles"

    id_modelo_panel = Column(BigInteger, primary_key=True, autoincrement=True)
    id_fabricante = Column(BigInteger, ForeignKey("fabricantes.id_fabricante", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    modelo = Column(String(100), nullable=False)
    potencia_nominal_w = Column(Numeric(8, 2), nullable=False)
    eficiencia_nominal = Column(Numeric(5, 2), nullable=False)
    voltaje_nominal_v = Column(Numeric(8, 2), nullable=False)
    corriente_nominal_a = Column(Numeric(8, 2), nullable=False)

    fabricante = relationship("Fabricante", back_populates="modelos_paneles")
    paneles = relationship("Panel", back_populates="modelo_panel")

    __table_args__ = (
        UniqueConstraint('id_fabricante', 'modelo', name='uq_modelos_paneles_fabricante_modelo'),
    )


class ModeloInversor(Base):
    __tablename__ = "modelos_inversores"

    id_modelo_inversor = Column(BigInteger, primary_key=True, autoincrement=True)
    id_fabricante = Column(BigInteger, ForeignKey("fabricantes.id_fabricante", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    modelo = Column(String(100), nullable=False)
    potencia_nominal_w = Column(Numeric(10, 2), nullable=False)
    eficiencia_nominal = Column(Numeric(5, 2), nullable=False)
    voltaje_maximo_v = Column(Numeric(10, 2), nullable=False)

    fabricante = relationship("Fabricante", back_populates="modelos_inversores")
    inversores = relationship("Inversor", back_populates="modelo_inversor")

    __table_args__ = (
        UniqueConstraint('id_fabricante', 'modelo', name='uq_modelos_inversores_fabricante_modelo'),
    )


class Panel(Base):
    __tablename__ = "paneles"

    id_panel = Column(BigInteger, primary_key=True, autoincrement=True)
    id_instalacion = Column(BigInteger, ForeignKey("instalaciones_solares.id_instalacion", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    id_modelo_panel = Column(BigInteger, ForeignKey("modelos_paneles.id_modelo_panel", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    numero_serie = Column(String(100), nullable=False, unique=True)
    fecha_instalacion = Column(Date, nullable=False)
    estado = Column(String(20), nullable=False)

    instalacion = relationship("InstalacionSolar", back_populates="paneles")
    modelo_panel = relationship("ModeloPanel", back_populates="paneles")


class Inversor(Base):
    __tablename__ = "inversores"

    id_inversor = Column(BigInteger, primary_key=True, autoincrement=True)
    id_instalacion = Column(BigInteger, ForeignKey("instalaciones_solares.id_instalacion", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    id_modelo_inversor = Column(BigInteger, ForeignKey("modelos_inversores.id_modelo_inversor", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    numero_serie = Column(String(100), nullable=False, unique=True)
    fecha_instalacion = Column(Date, nullable=False)
    estado = Column(String(20), nullable=False)

    instalacion = relationship("InstalacionSolar", back_populates="inversores")
    modelo_inversor = relationship("ModeloInversor", back_populates="inversores")


class MedicionEnergetica(Base):
    __tablename__ = "mediciones_energeticas"

    id_medicion = Column(BigInteger, primary_key=True, autoincrement=True)
    id_instalacion = Column(BigInteger, ForeignKey("instalaciones_solares.id_instalacion", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    energia_generada_kwh = Column(Numeric(12, 3), nullable=False)
    energia_consumida_kwh = Column(Numeric(12, 3), nullable=False)

    instalacion = relationship("InstalacionSolar", back_populates="mediciones")

    __table_args__ = (
        UniqueConstraint('id_instalacion', 'fecha_hora', name='uq_mediciones_instalacion_fecha'),
    )


class CondicionAmbiental(Base):
    __tablename__ = "condiciones_ambientales"

    id_condicion = Column(BigInteger, primary_key=True, autoincrement=True)
    id_instalacion = Column(BigInteger, ForeignKey("instalaciones_solares.id_instalacion", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    radiacion_solar_w_m2 = Column(Numeric(10, 2), nullable=False)
    temperatura_c = Column(Numeric(5, 2), nullable=False)
    humedad_porcentaje = Column(Numeric(5, 2), nullable=False)
    velocidad_viento_m_s = Column(Numeric(6, 2), nullable=False)

    instalacion = relationship("InstalacionSolar", back_populates="condiciones")

    __table_args__ = (
        UniqueConstraint('id_instalacion', 'fecha_hora', name='uq_condiciones_instalacion_fecha'),
    )


class ConfiguracionInstalacion(Base):
    __tablename__ = "configuraciones_instalacion"

    id_configuracion = Column(BigInteger, primary_key=True, autoincrement=True)
    id_instalacion = Column(BigInteger, ForeignKey("instalaciones_solares.id_instalacion", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=True)
    inclinacion_grados = Column(Numeric(5, 2), nullable=False)
    azimut_grados = Column(Numeric(6, 2), nullable=False)

    instalacion = relationship("InstalacionSolar", back_populates="configuraciones")