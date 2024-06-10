#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return ''

class Scientists(Resource): 
    def get(self):
        scientists = []
        for scientist in Scientist.query.all():
            scientists.append(scientist.to_dict(rules=('-missions',))) 
        return make_response(scientists)
        
    def post(self):
        params = request.json
        try:
            scientist = Scientist(name=params.get('name'), field_of_study=params.get('field_of_study'))
            db.session.add(scientist)
            db.session.commit()
            return make_response(scientist.to_dict())
        except ValueError as v_error:
            # return make_response({"errors": [str(v_error)]}, 400)
            return make_response({"errors": ["validation errors"]}, 400)

# @app.route('/scientists', methods=['GET', 'POST'])
# def scientist():
#     if request.method == 'GET':
#         scientists = []
#         for scientist in Scientist.query.all():
#             scientists.append(scientist.to_dict()) 
#         return make_response(scientists)
#     elif request.method == 'POST':
#         data = request.json
#         try:
#           new_scientist = Scientist(name=data['name'], field_of_study=data['field_of_study'])
#           db.session.add(new_scientist)
#           db.session.commit()
#           return make_response(new_scientist.to_dict(), 204)
#       except ValueError as v_error:
            # return make_response({"errors": [str(v_error)]}, 422)

api.add_resource(Scientists,'/scientists')

class ScientistById(Resource): 
    def get(self, id):
        scientist = db.session.get(Scientist, id)
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        return make_response(scientist.to_dict())
    
    def patch(self, id):
        scientist = db.session.get(Scientist, id)
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        try:
            params = request.json
            for attr in params:
                setattr(scientist, attr, params[attr])
            db.session.commit()
            return make_response(scientist.to_dict(), 202)
        except ValueError as v_error:
            # return make_response({"errors": [str(v_error)]})
            return make_response({"errors": ["validation errors"]}, 400)
    
    def delete(self, id):
        scientist = db.session.get(Scientist, id)
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        db.session.delete(scientist)
        db.session.commit()
        return make_response({}, 204)
        
api.add_resource(ScientistById,'/scientists/<int:id>')


# @app.route('/scientists/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
# def scientistById(id):
#     scientist = db.session.get(Scientist, id)
#     if request.method == 'GET':
#         if scientist:
#             return make_response(scientist.to_dict())
#         else: 
#             return make_response({"error": "Scientist not found"},404)
#     elif request.method == 'PATCH':
#         if scientist:
#         try:
#             params = request.json
#             for attr in params:
#                 setattr(scientist, attr, params[attr])
#             db.session.commit()
#             return make_response(scientist.to_dict(), 202)
#         except ValueError as v_error:
#             return make_response({"errors": [str(v_error)]}, ) 
#         else:
#             return make_response({"error": "Scientist not found"})
#     elif request.method == 'DELETE':
#         if scientist:
#             db.session.delete(scientist)
#             db.session.commit()
#             return make_response({'', 204}) 

class Planets(Resource): 
    def get(self):
        planets = [planet.to_dict() for planet in Planet.query.all()]
        return make_response(planets)
    
# @app.route('/planets', methods=['GET'])
# def planets():
#     if request.method == 'GET':
#         planets = []
#         for planet in Planets.query.all():
#             planets.append(planet.to_dict()) 
#         return make_response(planets)

api.add_resource(Planets,'/planets')


class Missions(Resource): 
    def post(self):
        params = request.json
        try:
            mission = Mission(name=params['name'],scientist_id=params['scientist_id'],planet_id=params['planet_id'])
            db.session.add(mission)
            db.session.commit()
            return make_response(mission.to_dict(), 201)
        except ValueError:
            # return make_response({"errors": [str(v_error)]})
            return make_response({"errors": ["validation errors"]}, 400)
    
# @app.route('/missions', methods=['POST'])
# def missions():
#         data = request.json
#         if data:
#             new_missions = Mission(name=data['name'], scientist_id=data['scientist_id'], planet_id=data['planet_id'])
#             db.session.add(new_missions)
#             db.session.commit()
#             return make_response(new_missions.to_dict(), 201)
#         else: 
#             return make_response({"errors": ["validation errors"]})        
api.add_resource(Missions,'/missions')

    
if __name__ == '__main__':
    app.run(port=5555, debug=True)
