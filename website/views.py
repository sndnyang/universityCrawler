# -*- coding:utf-8 -*-

import os
import traceback

from flask import request, render_template, g, session, json, Blueprint, abort
from flask_login import login_required
from sqlalchemy.orm.exc import NoResultFound
from wtforms import StringField, validators

from ..validation import *
from mindmap import app, db

from models import College, TempCollege, University, TempUniversity


uni_major_page = Blueprint('uni_major_page', __name__,
                         template_folder=os.path.join(
                             os.path.dirname(__file__), 'templates'),
                         static_folder="static")

version = 2

@uni_major_page.route('/college.html')
@uni_major_page.route('/college')
def college_page():
    meta = {'title': u'美国大学库 知维图 -- 互联网学习实验室',
            'description': u'美国大学申请信息库，包括GPA、英语成绩、截止日期、学费等',
            'keywords': u'zhimind 美国 大学 CS 学费 截止日期'}
    return render_template('universityList.html', meta=meta, temp=0,
                           version=version)


@uni_major_page.route('/tempcollege.html')
@login_required
def temp_college_page():
    if g.user.get_name() != 'sndnyang':
        abort(404)
    meta = {'title': u'美国大学库 知维图 -- 互联网学习实验室',
            'description': u'美国大学申请信息库，包括GPA、英语成绩、截止日期、学费等',
            'keywords': u'zhimind 美国 大学 CS 学费 截止日期'}
    return render_template('universityList.html', meta=meta, temp=1,
                           version=version)


@uni_major_page.route('/major.html')
@uni_major_page.route('/major.html/<int:temp>')
@uni_major_page.route('/major')
def major_page(temp=0):
    if temp == 1 and (g.user is None or not g.user.is_authenticated)\
            and g.user.get_name() != 'sndnyang':
        return u"用户不支持访问"

    meta = {'title': u'美国大学库 知维图 -- 互联网学习实验室',
            'description': u'美国大学申请信息库，包括GPA、英语成绩、截止日期、学费等',
            'keywords': u'zhimind 美国 大学 CS 学费 截止日期'}
    if temp != 1:
        temp = 0
    return render_template('majorList.html', meta=meta, temp=temp,
                           version=version, types="major")


def convert_dict(e):
    item = {'id': e.id,
            'name': e.name,
            'degree': e.degree,
            'major': e.major,
            'program_name': e.program_name,
            'site_url': e.site_url,
            'gpa': e.gpa,
            'gpa_url': e.gpa_url,
            'tuition': e.tuition,
            'tuition_url': e.tuition_url,
            'fall': e.fall,
            'spring': e.spring,
            'deadline_url': e.deadline_url,
            'toefl': e.toefl,
            'ielts': e.ielts,
            'eng_url': e.eng_url,
            'gre': e.gre,
            'gre_url': e.gre_url,
            'rl': e.rl,
            'evalue': e.evalue,
            'finance': e.finance,
            'docum_url': e.docum_url,
            'info': e.info,
            'int_docum_url': e.int_docum_url
            }
    return item


def getCollegeRedis():
    base_dir = os.path.dirname(__file__)
    fname = os.path.join(base_dir, '..', '..', 'static', 'data', 'college.json')
    college_set = []
    name_list = []

    try:
        data = json.load(open(fname))
        # uni_major_page = University.query.paginate(int(pageno), 25).items
        uni_major_page = University.query.all()
        for e in uni_major_page:
            college_set.append({'id': e.id, 'name': e.name, 'info': e.info})
            name_list.append(e.name)
    except Exception, e:
        app.logger.debug(traceback.print_exc())
    return college_set


@uni_major_page.route('/collegeList')
@uni_major_page.route('/collegeList/<int:pageno>')
def collegeListPage(pageno = 1):
    entity = app.redis.get('college')
    if entity and eval(entity):
        entity = eval(entity)
        return json.dumps(entity, ensure_ascii=False)

    college_set = getCollegeRedis()
    app.redis.set('college', college_set)

    return json.dumps(college_set, ensure_ascii=False)


@uni_major_page.route('/majorList')
@uni_major_page.route('/majorList/<int:pageno>')
def majorListPage(pageno = 1):
    base_dir = os.path.dirname(__file__)
    # fname = os.path.join(base_dir, '..', 'static', 'data', 'college.json')
    major_set = []
    try:
        # data = json.load(open(fname))
        if pageno == 0:
            major_list = TempCollege.query.all()
        else:
            major_list = College.query.all()
        for e in major_list:
            major_set.append(convert_dict(e))
    #   for e in data:
    #       major_set.append(e)
    except Exception, e:
        app.logger.debug(traceback.print_exc())

    return json.dumps(major_set, ensure_ascii=False)


@uni_major_page.route('/majorList1')
def temp_major_list():
    major_set = []
    try:
        major_list = TempCollege.query.all()
        for e in major_list:
            major_set.append(convert_dict(e))
    except Exception, e:
        app.logger.debug(traceback.print_exc())
        return json.dumps({'error': 'error'})
    return json.dumps(major_set, ensure_ascii=False)


@uni_major_page.route('/collegeList1')
def temp_college_list():
    college_set = []
    try:
        uni_major_page = TempUniversity.query.all()
        for e in uni_major_page:
            college_set.append(convert_dict(e))
    except Exception, e:
        app.logger.debug(traceback.print_exc())
        return json.dumps({'error': 'error'})
    return json.dumps(college_set, ensure_ascii=False)


@uni_major_page.route('/college/<cid>')
def university(cid):
    try:
        e = University.query.get(cid)
        return json.dumps({'id': e.id, 'name': e.name, 'info': e.info}, ensure_ascii=False)
    except NoResultFound:
        app.logger.debug(traceback.print_exc())
    return json.dumps({'error': 'not find'}, ensure_ascii=False)


@uni_major_page.route('/major/<cid>')
def single_major(cid):
    try:
        college = College.query.get(cid)
        return json.dumps(convert_dict(college), ensure_ascii=False)
    except NoResultFound:
        app.logger.debug(traceback.print_exc())
    return json.dumps({'error': 'not find'}, ensure_ascii=False)


@uni_major_page.route('/collegeForm/<name>')
def college_form(name):
    meta = {'title': u'美国大学库 知维图 -- 互联网学习实验室',
            'description': u'美国大学申请信息库，包括GPA、英语成绩、截止日期、学费等',
            'keywords': u'zhimind 美国 大学 CS 学费 截止日期'}

    verification_code = StringField(u'验证码', 
                                    validators=[validators.Required(),
                                                validators.Length
                                                (4, 4, message=u'填写4位验证码')])
    return render_template('college_form.html', veri=verification_code, meta=meta)


@uni_major_page.route('/majorForm/<name>')
def major_form(name):
    meta = {'title': u'美国大学库 知维图 -- 互联网学习实验室',
            'description': u'美国大学申请信息库，包括GPA、英语成绩、截止日期、学费等',
            'keywords': u'zhimind 美国 大学 CS 学费 截止日期'}

    verification_code = StringField(u'验证码', 
                                    validators=[validators.Required(),
                                                validators.Length
                                                (4, 4, message=u'填写4位验证码')])
    return render_template('major_form.html', veri=verification_code, meta=meta)


@uni_major_page.route('/college_submitted', methods=['POST'])
def submitted_college():
    verification_code = request.form['verification_code']
    code_text = session['code_text']
    if verification_code != code_text and not (g.user and 
       g.user.is_authenticated and g.user.get_name() == 'sndnyang'):
        return json.dumps({'error': u'验证码错误'}, ensure_ascii=False)
    code_img, code_string = create_validate_code()
    session['code_text'] = code_string
    try:
        name = request.form['name']
        info = {u'city': request.form.get('cityinput', '')}
        for i in range(len(request.form.keys())/2):
            if 'label%d' % (i+1) not in request.form:
                break
            info['label%d' % (i+1)] = request.form['label%d' % (i+1)]
            info['input%d' % (i+1)] = request.form['input%d' % (i+1)]

        if not name:
            return json.dumps({'error': u'校名缺失'}, ensure_ascii=False)
        result = University.query.filter_by(name=name).one_or_none()
        if result is None:
            if g.user and g.user.is_authenticated and g.user.get_name() == 'sndnyang':
                college = University(name, info)
            else:
                college = TempUniversity(name, info)
        else:
            college = result
            import copy
            new_info = copy.deepcopy(college.info)
            for e in info:
                new_info[e] = info[e]
            college.info = new_info

        if result is None:
            db.session.add(college)
        db.session.commit()
        college_set = getCollegeRedis()
        app.redis.set('college', college_set)
    except Exception, e:
        app.logger.debug(traceback.print_exc())
        return json.dumps({'error': u'错误'}, ensure_ascii=False)

    # comments = request.form['comments']
    return json.dumps({'info': u'成功'}, ensure_ascii=False)


@uni_major_page.route('/major_submitted', methods=['POST'])
def submitted_major():
    verification_code = request.form['verification_code']
    code_text = session['code_text']
    if verification_code != code_text:
        return json.dumps({'error': u'验证码错误'}, ensure_ascii=False)
    code_img, code_string = create_validate_code()
    session['code_text'] = code_string
    try:
        cid = request.form['id']
        name = request.form['name']
        degree = request.form['degree']
        major = request.form['major']
        program_name = request.form['program_name']
        site_url = request.form['site_url']
        if not name or not degree or not major:
            return json.dumps({'error': u'关键信息缺失'}, ensure_ascii=False)
        result = College.query.get(cid)
        if result is None:
            result = College.query.filter_by(name=name, major=major,
                                             degree=degree, program_name=program_name
                                             ).one_or_none()
        if result is None:
            if g.user and g.user.is_authenticated and g.user.get_name() == 'sndnyang':
                college = College(name, degree, major, site_url, program_name)
            else:
                college = TempCollege(name, degree, major, site_url, program_name)
        else:
            college = result

        college.program_name = program_name
        college.gpa = request.form['gpa'] if request.form['gpa'] else 6.6
        college.gpa_url = request.form['gpa_url']
        college.tuition = request.form['tuition'] if request.form['tuition'] else 66666

        college.tuition_url = request.form['tuition_url']
        college.deadline_url = request.form['deadline_url']
        college.fall = request.form['fall']
        college.spring = request.form['spring']
        college.gre = request.form['gre']
        college.gre_url = request.form['gre_url']
        college.toefl = request.form['toefl'] if request.form['toefl'] else 6.6

        college.ielts = request.form['ielts'] if request.form['ielts'] else 6.6

        college.eng_url = request.form['eng_url']
        college.rl = request.form['rl']
        college.evalue = request.form['evalue']
        college.finance = request.form['finance']
        college.docum_url = request.form['docum_url']
        college.int_docum_url = request.form['int_docum_url']

        info = {}
        l = (len(request.form.keys()) - 23) / 2
        for i in range(l):
            info['label%d' % i] = request.form.get('label%d' % i, '')
            info['input%d' % i] = request.form.get('input%d' % i, '')
        college.info = info

        if result is None:
            db.session.add(college)
        db.session.commit()
    except Exception, e:
        app.logger.debug(traceback.print_exc())
        return json.dumps({'error': u'错误'}, ensure_ascii=False)

    # comments = request.form['comments']

    return json.dumps({'info': u'成功'}, ensure_ascii=False)


@uni_major_page.route('/collegeData/approve', methods=['POST'])
@login_required
def college_approve():
    if g.user.get_name() != 'sndnyang':
        abort(404)
    no = request.json.get('id', None)
    action = str(request.json.get('type', None))
    if not no or not action:
        return json.dumps({'error': '%s %s not right' % (no, action)}, ensure_ascii=False)

    app.logger.debug(no + ' ' + action)
    try:
        college = TempUniversity.query.get(no)
        if action == "1":
            db.session.delete(college)
        else:
            result = University.query.filter_by(name=college.name).one_or_none()
            if result is None:
                result = University(college.name, college.info)
                result.set(college)
                db.session.add(result)
            else:
                result.set(college)
        db.session.commit()
        return json.dumps({'info': 'success'}, ensure_ascii=False)
    except Exception, e:
        app.logger.debug(traceback.print_exc())
    return json.dumps({'error': 'not find'}, ensure_ascii=False)


@uni_major_page.route('/majorData/approve', methods=['POST'])
@login_required
def major_approve():
    if g.user.get_name() != 'sndnyang':
        abort(404)
    no = request.json.get('id', None)
    action = str(request.json.get('type', None))
    if not no or not action:
        return json.dumps({'error': '%s %s not right' % (no, action)}, ensure_ascii=False)

    app.logger.debug(no + ' ' + action)
    try:
        college = TempCollege.query.get(no)
        if action == 1:
            db.session.delete(college)
        else:
            result = College.query.filter_by(name=college.name, major=
                    college.major, degree=college.degree).one_or_none()
            if result is None:
                result = College(college.name, college.degree, college.major,
                        college.site_url, college.program_name)
                result.set(college)
                db.session.add(result)
            else:
                result.set(college)
            db.session.delete(college)
        db.session.commit()
        return json.dumps({'info': 'success'}, ensure_ascii=False)
    except Exception, e:
        app.logger.debug(traceback.print_exc())
    return json.dumps({'error': 'not find'}, ensure_ascii=False)
