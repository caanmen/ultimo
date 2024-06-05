from flask_cors import CORS
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time

app = Flask(__name__)
app.secret_key = 'tu_super_secreto'
CORS(app, resources={r"/*": {"origins": "*"}})  # Permitir solicitudes desde cualquier origen

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/rest'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__ = 'usuarios'  # Nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(100), nullable=False)

class Reserva(db.Model):
    __tablename__ = 'reservas'  # Nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(50), nullable=False)
    hora = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    detalle = db.Column(db.String(200), nullable=False)
    usuario_responsable = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    numero_mesa = db.Column(db.Integer, nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('reservas', lazy=True))

class ResponseFactory:
    @staticmethod
    def create_response(response_type, message, data=None):
        if data:
            data = serialize_data(data)
        if response_type == 'success':
            return jsonify({'status': 'success', 'message': message, 'data': data}), 200
        elif response_type == 'error':
            return jsonify({'status': 'error', 'message': message}), 400
        elif response_type == 'not_found':
            return jsonify({'status': 'not_found', 'message': message}), 404

def serialize_data(data):
    if isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}
    elif isinstance(data, (datetime, date, time)):
        return data.isoformat()
    return data

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    return response

def _corsify_actual_response(response):
    if not isinstance(response, tuple):
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    else:
        resp, status = response
        response = make_response(resp, status)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

@app.route('/')
def home():
    return 'Bienvenido a la API de ReservaFacil!'

@app.route('/reservas', methods=['GET', 'OPTIONS'])
def get_reservas():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    try:
        reservas = db.session.query(
            Reserva.id,
            Reserva.fecha,
            Reserva.hora,
            Reserva.estado,
            Reserva.detalle,
            Usuario.correo.label('usuario_responsable_correo'),
            Reserva.numero_mesa
        ).join(Usuario, Reserva.usuario_responsable == Usuario.id).all()

        reservas_list = [
            {
                'id': r.id,
                'fecha': r.fecha,
                'hora': r.hora,
                'estado': r.estado,
                'detalle': r.detalle,
                'usuario_responsable_correo': r.usuario_responsable_correo,
                'numero_mesa': r.numero_mesa
            } for r in reservas
        ]
        response = ResponseFactory.create_response('success', 'Reservas obtenidas con éxito', reservas_list)
        return _corsify_actual_response(response)
    except Exception as e:
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)

@app.route('/create_reserva', methods=['POST', 'OPTIONS'])
def create_reserva():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    data = request.get_json()
    try:
        # Verificar si ya existe una reserva para la mesa en la fecha y hora seleccionadas
        existing_reserva = db.session.query(Reserva).filter_by(
            fecha=data['fecha'], hora=data['hora'], numero_mesa=data['numero_mesa']
        ).first()
        if existing_reserva:
            response = ResponseFactory.create_response('error', 'Ya existe una reserva para esta mesa en la fecha y hora seleccionadas.')
            return _corsify_actual_response(response)
        
        new_reserva = Reserva(
            fecha=data['fecha'],
            hora=data['hora'],
            estado=data['estado'],
            detalle=data['detalle'],
            usuario_responsable=data['usuario_responsable'],
            numero_mesa=data['numero_mesa']
        )
        db.session.add(new_reserva)
        db.session.commit()
        
        response_data = {
            'id': new_reserva.id,
            'fecha': new_reserva.fecha,
            'hora': new_reserva.hora,
            'estado': new_reserva.estado,
            'detalle': new_reserva.detalle,
            'usuario_responsable_correo': db.session.query(Usuario.correo).filter_by(id=new_reserva.usuario_responsable).scalar(),
            'numero_mesa': new_reserva.numero_mesa
        }
        response = ResponseFactory.create_response('success', 'Reserva creada con éxito', response_data)
        return _corsify_actual_response(response)
    except Exception as e:
        db.session.rollback()
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)

@app.route('/update_reserva/<int:reserva_id>', methods=['PUT', 'OPTIONS'])
def update_reserva(reserva_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    data = request.get_json()
    try:
        # Verificar si ya existe una reserva para la mesa en la fecha y hora seleccionadas
        existing_reserva = db.session.query(Reserva).filter(
            Reserva.fecha == data['fecha'],
            Reserva.hora == data['hora'],
            Reserva.numero_mesa == data['numero_mesa'],
            Reserva.id != reserva_id
        ).first()
        if existing_reserva:
            response = ResponseFactory.create_response('error', 'Ya existe una reserva para esta mesa en la fecha y hora seleccionadas.')
            return _corsify_actual_response(response)
        
        reserva = db.session.query(Reserva).filter_by(id=reserva_id).first()
        if not reserva:
            response = ResponseFactory.create_response('not_found', 'Reserva no encontrada')
            return _corsify_actual_response(response)
        
        reserva.fecha = data['fecha']
        reserva.hora = data['hora']
        reserva.estado = data['estado']
        reserva.detalle = data['detalle']
        reserva.usuario_responsable = data['usuario_responsable']
        reserva.numero_mesa = data['numero_mesa']
        db.session.commit()
        
        response_data = {
            'id': reserva.id,
            'fecha': reserva.fecha,
            'hora': reserva.hora,
            'estado': reserva.estado,
            'detalle': reserva.detalle,
            'usuario_responsable_correo': db.session.query(Usuario.correo).filter_by(id=reserva.usuario_responsable).scalar(),
            'numero_mesa': reserva.numero_mesa
        }
        response = ResponseFactory.create_response('success', 'Reserva actualizada con éxito', response_data)
        return _corsify_actual_response(response)
    except Exception as e:
        db.session.rollback()
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)

@app.route('/delete_reserva/<int:reserva_id>', methods=['DELETE', 'OPTIONS'])
def delete_reserva(reserva_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    try:
        reserva = db.session.query(Reserva).filter_by(id=reserva_id).first()
        if reserva:
            numero_mesa = reserva.numero_mesa
            db.session.delete(reserva)
            db.session.commit()
            # Actualizar el estado de la mesa
            db.session.query(Mesa).filter_by(numero_mesa=numero_mesa).update({'disponible': True})
            db.session.commit()
            response = ResponseFactory.create_response('success', 'Reserva eliminada con éxito')
            return _corsify_actual_response(response)
        else:
            response = ResponseFactory.create_response('not_found', 'Reserva no encontrada')
            return _corsify_actual_response(response)
    except Exception as e:
        db.session.rollback()
        response = ResponseFactory.create_response('error', str(e))
        return _corsify_actual_response(response)

if __name__ == '__main__':
    app.run(debug=True, port=3100)
