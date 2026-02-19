from datetime import datetime, date
from flask_login import UserMixin
from sqlalchemy import event
from extensions import db


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    avisos = db.relationship('Aviso', backref='creado_por', lazy=True,
                             foreign_keys='Aviso.created_by')


ESTADOS = [
    ('pendiente', 'Pendiente'),
    ('hoy', 'Hoy'),
    ('esperando_material', 'Esperando material'),
    ('segunda_visita', 'Segunda visita'),
    ('finalizado', 'Finalizado'),
]

ELECTRODOMESTICOS = [
    'Lavadora', 'Secadora', 'Lavavajillas', 'Frigorífico', 'Congelador',
    'Horno', 'Microondas', 'Vitrocerámica', 'Cocina gas', 'Campana extractora',
    'Aire acondicionado', 'Caldera', 'Calentador', 'Termo eléctrico',
    'Televisión', 'Lava-secadora', 'Otro',
]


class Aviso(db.Model):
    __tablename__ = 'aviso'

    id = db.Column(db.Integer, primary_key=True)

    # Datos del cliente
    nombre_cliente = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(20), nullable=False, index=True)
    calle = db.Column(db.String(200))
    localidad = db.Column(db.String(100))

    # Datos del electrodoméstico
    electrodomestico = db.Column(db.String(100))
    marca = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    notas = db.Column(db.Text)

    # Fechas
    fecha_aviso = db.Column(db.Date, nullable=False, default=date.today)
    fecha_cita = db.Column(db.Date, nullable=True)

    # Estado
    estado = db.Column(db.String(30), nullable=False, default='pendiente', index=True)

    # Económico
    precio_mano_obra = db.Column(db.Float, nullable=True)   # € cobrado al cliente
    coste_materiales = db.Column(db.Float, nullable=True)   # € gastado en piezas
    materiales_desc   = db.Column(db.Text, nullable=True)   # descripción de piezas usadas

    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # Relaciones
    photos = db.relationship('Photo', backref='aviso', lazy=True,
                             cascade='all, delete-orphan')

    def estado_label(self):
        for key, label in ESTADOS:
            if key == self.estado:
                return label
        return self.estado

    @property
    def beneficio(self):
        """Beneficio neto = precio cobrado - coste materiales."""
        ingresos = self.precio_mano_obra or 0.0
        costes   = self.coste_materiales or 0.0
        return round(ingresos - costes, 2)

    @property
    def tiene_datos_economicos(self):
        return self.precio_mano_obra is not None or self.coste_materiales is not None

    def estado_badge_class(self):
        clases = {
            'pendiente': 'bg-warning text-dark',
            'hoy': 'bg-danger',
            'esperando_material': 'bg-info text-dark',
            'segunda_visita': 'bg-primary',
            'finalizado': 'bg-success',
        }
        return clases.get(self.estado, 'bg-secondary')


@event.listens_for(Aviso, 'before_update')
def update_timestamp(mapper, connection, target):
    target.updated_at = datetime.utcnow()


class Photo(db.Model):
    __tablename__ = 'photo'

    id = db.Column(db.Integer, primary_key=True)
    aviso_id = db.Column(db.Integer, db.ForeignKey('aviso.id'), nullable=False)
    filename = db.Column(db.String(256), nullable=False)
    original_name = db.Column(db.String(256))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
