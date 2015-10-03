# -*- coding: utf-8 -*-
import json
import os
import unittest
from flask.ext.testing import TestCase

from traffic_light import app
from traffic_light import basedir
from traffic_light import db
from traffic_light.models import CODES


class BaseTestCase(TestCase):

    def create_app(self):
        self.headers = {'Content-Type': 'application/json'}
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_sequence(self):
        kwargs = dict(data=json.dumps({}), headers=self.headers)
        response = self.client.post('/sequence/create', **kwargs)
        assert response.json['status'] == 'ok'
        return response.json['response']['sequence']

    def send_observation(self, data):
        kwargs = dict(data=json.dumps(data), headers=self.headers)
        return self.client.post('/observation/add', **kwargs)

    def clear(self):
        kwargs = dict(data=json.dumps({}), headers=self.headers)
        response = self.client.post('/clear', **kwargs)
        assert response.json['status'] == 'ok'
        assert response.json['response'] == 'ok'


class ErrorTestCase(BaseTestCase):

    def test_missed_observation(self):
        sequence = self.create_sequence()

        response = self.send_observation({
            "observation": {
                "color": "green",
                "numbers": ["1110111", "1111111"]
            },
            "sequence": sequence
        })
        assert response.json['status'] == 'ok'
        assert response.json['response']['missing'] == ['0000000', '0000000']
        assert response.json['response']['start'] == [8, 88]

        response = self.send_observation({
            "observation": {
                "color": "green",
                "numbers": ["1110111", "1101111"]
            },
            "sequence": sequence
        })
        assert response.json['status'] == 'error'
        assert response.json['msg'] == 'No solutions found'

    def test_double_observation(self):
        sequence = self.create_sequence()

        response = self.send_observation({
            "observation": {
                "color": "green",
                "numbers": ["1110111", "1111111"]
            },
            "sequence": sequence
        })
        assert response.json['status'] == 'ok'
        assert response.json['response']['missing'] == ['0000000', '0000000']
        assert response.json['response']['start'] == [8, 88]

        response = self.send_observation({
            "observation": {
                "color": "green",
                "numbers": ["1110111", "1111111"]
            },
            "sequence": sequence
        })
        assert response.json['status'] == 'error'
        assert response.json['msg'] == 'No solutions found'

    def test_messed_observation(self):
        sequence = self.create_sequence()

        response = self.send_observation({
            "observation": {
                "color": "green",
                "numbers": ["1110111", "1111111"]
            },
            "sequence": sequence
        })
        assert response.json['status'] == 'ok'
        assert response.json['response']['missing'] == ['0000000', '0000000']
        assert response.json['response']['start'] == [8, 88]

        response = self.send_observation({
            "observation": {
                "color": "green",
                "numbers": ["1110111", "1111011"]
            },
            "sequence": sequence
        })
        assert response.json['status'] == 'error'
        assert response.json['msg'] == 'No solutions found'

    def test_sequence_didnt_find(self):
        response = self.send_observation({
            "observation": {
                "color": "green",
                "numbers": ["1110111", "1101111"]
            },
            "sequence": "no-sequence"
        })
        assert response.json['status'] == 'error'
        assert response.json['msg'] == 'The sequence isn\'t found'

    def test_first_is_red_light(self):
        sequence = self.create_sequence()

        response = self.send_observation({
            "observation": {
                "color": "red",
            },
            "sequence": sequence
        })
        assert response.json['status'] == 'error'
        assert response.json['msg'] == 'There isn\'t enough data'

    def test_observation_after_red_light(self):
        sequence = self.create_sequence()

        response = self.send_observation({
            "observation": {
                "color": "green",
                "numbers": ["1110111", "0010000"]
            },
            "sequence": sequence
        })
        assert response.json['status'] == 'ok'
        assert response.json['response']['missing'] == ['0000000', '0000000']
        assert response.json['response']['start'] == [1, 2, 3, 4, 7, 8, 9, 80, 81, 82, 83, 84, 87, 88, 89]

        response = self.send_observation({
            "observation": {
                "color": "red",
            },
            "sequence": sequence
        })
        assert response.json['status'] == 'ok'
        assert response.json['response']['missing'] == ['0000000', '0000010']
        assert response.json['response']['start'] == [1]

        response = self.send_observation({
            "observation": {
                "color": "green",
                "numbers": ["1110111", "1110111"]
            },
            "sequence": sequence
        })
        assert response.json['status'] == 'error'
        assert response.json['msg'] == 'The red observation should be the last'


class AcceptenceTestCase(BaseTestCase):

    def test_example(self):
        sequence = self.create_sequence()

        response = self.send_observation({
            "observation": {
                "color": "green",
                "numbers": ["1110111", "0011101"]
            },
            "sequence": sequence
        })
        assert response.json['status'] == 'ok'
        assert response.json['response']['missing'] == ['0000000', '1000000']
        assert response.json['response']['start'] == [2, 8, 82, 88]

        response = self.send_observation({
            "observation": {
                "color": "green",
                "numbers": ["1110111", "0010000"]
            },
            "sequence": sequence
        })
        assert response.json['status'] == 'ok'
        assert response.json['response']['missing'] == ['0000000', '1000010']
        assert response.json['response']['start'] == [2, 8, 82, 88]

        response = self.send_observation({
            "observation": {
                "color": "red"
            },
            "sequence": sequence
        })
        assert response.json['status'] == 'ok'
        assert response.json['response']['missing'] == ['0000000', '1000010']
        assert response.json['response']['start'] == [2]

    def observation_cycle(self, start, left_missing, right_missing):
        sequence = self.create_sequence()

        ret = None
        steps = 0
        for i in xrange(start, -1, -1):
            steps += 1

            left_number = (CODES[i / 10] | left_missing) ^ left_missing
            right_number = (CODES[i % 10] | right_missing) ^ right_missing

            response = self.send_observation({
                "observation": {
                    "color": 'green' if i > 0 else 'red',
                    "numbers": [
                        '{0:07b}'.format(left_number),
                        '{0:07b}'.format(right_number)
                    ]
                },
                "sequence": sequence
            })

            if response.json['status'] == 'error':
                ret = response.json['msg']
                break

            ret = response.json['response']
            if ret['start'] == [start]:
                break
        return start, steps, ret

    # def test_acceptence(self):
    #     print 'END', self.observation_cycle(2, 0, 0b1000010 )
    #     print 'END', self.observation_cycle(32, 0, 0)
    #     print 'END', self.observation_cycle(88, 0, 1)


if __name__ == '__main__':
    unittest.main()
