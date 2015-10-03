# -*- coding: utf-8 -*-
import uuid
from traffic_light import db


CODES = (
    0b1110111,
    0b0010010,
    0b1011101,
    0b1011011,
    0b0111010,
    0b1101011,
    0b1101111,
    0b1010010,
    0b1111111,
    0b1111011
)


class Number(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'))
    value = db.Column(db.Integer)
    left_missing = db.Column(db.Integer, default=0)
    right_missing = db.Column(db.Integer, default=0)

    def __init__(self, state, value):
        self.state = state
        self.value = value

    @classmethod
    def check(cls, code, number):
        real_code = CODES[number]
        return (real_code | code) == real_code, real_code ^ code

    def left_is_suitable(self, code, number):
        number = number / 10
        is_suitable, missing = Number.check(code, number)
        if is_suitable:
            self.left_missing |= missing
        return is_suitable

    def right_is_suitable(self, code, number):
        number = number % 10
        is_suitable, missing = Number.check(code, number)
        if is_suitable:
            self.right_missing |= missing
        return is_suitable


class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sequence = db.Column(db.String(64), unique=True)
    step = db.Column(db.Integer, default=1)
    start = db.relationship('Number', backref='state', lazy='dynamic')

    def __init__(self):
        self.sequence = str(uuid.uuid4())

    def missing_format(self, left, right):
        return '{0:07b}'.format(left), '{0:07b}'.format(right)

    def begin(self):
        for value in xrange(100):
            number = Number(state=self, value=value)
            db.session.add(number)
        db.session.commit()

    def green_light(self, left_code, right_code):
        unsuitable_values = []
        left_missing, right_missing = [0b1111111] * 2
        for number in self.start.all():

            if number.value in unsuitable_values:
                continue

            current_number = number.value - self.step + 1
            if current_number <= 0:
                unsuitable_values.append(number.value)
                continue

            if not number.right_is_suitable(right_code, current_number):
                right = number.value % 10
                unsuitable_values += [i * 10 + right for i in xrange(10)]
                continue
            right_missing &= number.right_missing

            if not number.left_is_suitable(left_code, current_number):
                unsuitable_values.append(number.value)
                continue
            left_missing &= number.left_missing

        self.step += 1
        db.session.commit()

        values = None
        if unsuitable_values:
            values = Number.value.in_(unsuitable_values)
        self.start.filter(values).delete(synchronize_session=False)
        db.session.commit()

        start_list = [number.value for number in self.start.all()]
        return start_list, self.missing_format(left_missing, right_missing)

    def red_light(self):
        value = self.step - 1

        unsuitable_values = Number.value != value
        self.start.filter(unsuitable_values).delete(synchronize_session=False)
        db.session.commit()

        left_missing, right_missing = [0b1111111] * 2
        for number in self.start.all():
            right_missing &= number.right_missing
            left_missing &= number.left_missing

        self.step = 0
        db.session.commit()

        start_list = [value]
        return start_list, self.missing_format(left_missing, right_missing)

    def process_observation(self, color, left_code, right_code):
        if color == 'red':
            return self.red_light()
        return self.green_light(left_code, right_code)
