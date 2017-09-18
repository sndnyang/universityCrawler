#!/usr/bin/env python 
# coding=utf-8
 
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import UniqueConstraint

from mindmap import db
from ..models import uuid_gen


class College(db.Model):
    __tablename__ = 'college'
    id = db.Column('college_id', db.String, primary_key=True, default=uuid_gen)
    name = db.Column(db.String(70))
    degree = db.Column(db.Integer)
    major = db.Column(db.String(10))
    program_name = db.Column(db.String(70))
    site_url = db.Column(db.String(250))
    gpa = db.Column(db.Float)
    gpa_url = db.Column(db.String(250))
    tuition = db.Column(db.Float)
    tuition_url = db.Column(db.String(250))
    fall = db.Column(db.String(20))
    spring = db.Column(db.String(20))
    deadline_url = db.Column(db.String(250))
    toefl = db.Column(db.Integer)
    ielts = db.Column(db.Float)
    eng_url = db.Column(db.String(250))
    gre = db.Column(db.String(20))
    gre_url = db.Column(db.String(250))
    rl = db.Column(db.String(10))
    evalue = db.Column(db.String(10))
    finance = db.Column(db.String(10))
    docum_url = db.Column(db.String(250))
    int_docum_url = db.Column(db.String(250))
    info = db.Column(JSON)
    __table_args__ = (UniqueConstraint('name', 'degree', 'major', 'program_name',
                      name='_degree_major'),)
    
    def __init__(self, name, degree, major, site_url, pname=''):
        self.name = name
        self.degree = degree
        self.major = major
        self.site_url = site_url
        self.program_name = pname

    def set(self, college):
        self.gpa = college.gpa
        self.gpa_url = college.gpa_url
        self.tuition = college.tuition
        self.tuition_url = college.tuition_url
        self.fall = college.fall
        self.spring = college.spring
        self.deadline_url = college.deadline_url
        self.toefl = college.toefl
        self.ielts = college.ielts
        self.eng_url = college.eng_url
        self.gre = college.gre
        self.gre_url = college.gre_url
        self.rl = college.rl
        self.evalue = college.evalue
        self.finance = college.finance
        self.docum_url = college.docum_url
        self.int_docum_url = college.int_docum_url
        self.info = college.info


class TempCollege(db.Model):
    __tablename__ = 'temp_college'
    id = db.Column('college_id', db.String, primary_key=True, default=uuid_gen)
    name = db.Column(db.String(70))
    degree = db.Column(db.Integer)
    major = db.Column(db.String(10))
    program_name = db.Column(db.String(70))
    site_url = db.Column(db.String(250))
    gpa = db.Column(db.Float)
    gpa_url = db.Column(db.String(250))
    tuition = db.Column(db.Float)
    tuition_url = db.Column(db.String(250))
    fall = db.Column(db.String(20))
    spring = db.Column(db.String(20))
    deadline_url = db.Column(db.String(250))
    toefl = db.Column(db.Integer)
    ielts = db.Column(db.Float)
    eng_url = db.Column(db.String(250))
    gre = db.Column(db.String(20))
    gre_url = db.Column(db.String(250))
    rl = db.Column(db.String(10))
    evalue = db.Column(db.String(10))
    finance = db.Column(db.String(10))
    docum_url = db.Column(db.String(250))
    int_docum_url = db.Column(db.String(250))
    info = db.Column(JSON)
    
    def __init__(self, name, degree, major, site_url):
        self.name = name
        self.degree = degree
        self.major = major
        self.site_url = site_url


class University(db.Model):
    __tablename__ = 'university'
    id = db.Column('university_id', db.String, primary_key=True, default=uuid_gen)
    name = db.Column(db.String(70), unique=True)
    info = db.Column(JSON)

    def __init__(self, name, info):
        self.name = name
        self.info = info


class TempUniversity(db.Model):
    __tablename__ = 'temp_university'
    id = db.Column('university_id', db.String, primary_key=True, default=uuid_gen)
    name = db.Column(db.String(70), unique=True)
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
    name = db.Column(db.String(50))
    zh_name = db.Column(db.String(20))
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
