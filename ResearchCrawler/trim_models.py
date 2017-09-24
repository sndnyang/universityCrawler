#!/usr/bin/env python 
# coding=utf-8

import uuid
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON

app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')
db = SQLAlchemy(app)

def uuid_gen():
    return str(uuid.uuid4())


class University(db.Model):
    __tablename__ = 'university'
    id = db.Column('university_id', db.String, primary_key=True,
            default=uuid_gen)
    name = db.Column(db.String(81), unique=True)
    info = db.Column(JSON)

    def __init__(self, name, info):
        self.name = name
        self.info = info

professor_interests_table = db.Table('professor_interests', db.Model.metadata,
                                     db.Column('professor_id', db.String, 
                                        db.ForeignKey('Professor.professor_id')),
                                     db.Column('interests_id', db.String, 
                                        db.ForeignKey('Interests.interests_id'))
                                    )


class Professor(db.Model):
    __tablename__ = 'Professor'
    id = db.Column('professor_id', db.String, primary_key=True, default=uuid_gen)
    name = db.Column(db.String(30))
    school = db.Column(db.String(60))
    major = db.Column(db.String(4))
    school_url = db.Column(db.String(150))
    home_page = db.Column(db.String(150))
    position = db.Column(db.Boolean)
    term = db.Column(db.String(20))
    interests = db.relationship('Interests', secondary=professor_interests_table,
        backref=db.backref('Professor', lazy='dynamic'))
    __table_args__ = (UniqueConstraint('name', 'school', 'major',
                      name='_professor_uniq'),)

    def __init__(self, name, school, major):
        self.name = name
        self.school = school
        self.major = major


class Interests(db.Model):
    __tablename__ = 'Interests'
    id = db.Column('interests_id', db.String, primary_key=True, default=uuid_gen)
    name = db.Column(db.String(50), unique=True)
    zh_name = db.Column(db.String(20), unique=True)
    major = db.Column(db.String(4))
    category_name = db.Column(db.String(50), default='')
    __table_args__ = (UniqueConstraint('name', 'major', name='_interests_uniq'),)

    def __init__(self, name, major):
        self.name = name
        self.major = major


class CrawlTask(db.Model):
    __tablename__ = 'interests_task'
    id = db.Column('task_id', db.String, primary_key=True, default=uuid_gen)
    school = db.Column(db.String(70))
    major = db.Column(db.String(4))
    school_url = db.Column(db.String(150))
    example = db.Column(db.String(150))
    __table_args__ = (UniqueConstraint('school', 'major',
                      name='_school_major_uniq'),)

    def __init__(self, school, major, url, example):
        self.school = school
        self.major = major
        self.school_url = url
        self.example = example
