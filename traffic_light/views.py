# -*- coding: utf-8 -*-
from flask import jsonify
from flask import request

from traffic_light import app
from traffic_light import db
from traffic_light.models import State


def ok_response(response):
    return jsonify({'status': 'ok', 'response': response})


def error_response(msg):
    return jsonify({'status': 'error', 'msg': msg})


@app.route('/sequence/create', methods=['POST'])
def create_sequence():
    db.create_all()

    state = State()
    db.session.add(state)
    db.session.commit()

    state.begin()
    return ok_response({'sequence': state.sequence})


@app.route('/observation/add', methods=['POST'])
def add_observation():
    data = request.get_json()

    # Validation
    sequence = data.get('sequence')
    color, left_code, right_code = None, None, None
    try:
        observation = data['observation']
        color = observation['color']
        if color not in ('red', 'green'):
            raise Exception('Wrong color')
        if color == 'green':
            left_code = int(observation['numbers'][0], 2)
            right_code = int(observation['numbers'][1], 2)
    except:
        return error_response('Bad format')

    # Get a current state
    state = State.query.filter_by(sequence=sequence).first()
    if state is None:
        return error_response('The sequence isn\'t found')
    if state.step == 0:
        return error_response('The red observation should be the last')
    if state.step == 1 and color == 'red':
        return error_response('There isn\'t enough data')

    # Process an observation
    start, missing = state.process_observation(color, left_code, right_code)
    if not start:
        return error_response('No solutions found')

    return ok_response({'start': start, 'missing': missing})


@app.route('/clear', methods=['POST'])
def clear():
    db.drop_all()
    db.create_all()
    return ok_response('ok')
