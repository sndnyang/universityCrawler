# -*- coding:utf-8 -*-

import os
import re
import traceback

from flask import request, render_template, session, json, Blueprint
from sqlalchemy.exc import InvalidRequestError
from wtforms import StringField, validators
from sqlalchemy import asc
from sqlalchemy.orm.exc import MultipleResultsFound

from ..validation import *
from mindmap import app, db

from models import *
from crawler import ResearchCrawler
from views import getCollegeRedis


research_page = Blueprint('research_page', __name__,
                          template_folder=os.path.join(
                             os.path.dirname(__file__), 'templates'),
                          static_folder="static")


@research_page.route('/research.html')
@research_page.route('/research')
def research_index():
    meta = {'title': u'学者研究兴趣 知维图 -- 互联网学习实验室',
            'description': u'学者研究兴趣信息库，主要就是学校、主页、研究方向、招生与否',
            'keywords': u'zhimind 美国 大学 CS 研究方向 research interests 招生'}
    return render_template('research.html', meta=meta, temp=0,
                           types="research")


@research_page.route('/researchList')
def research_list_page():
    research_set = []
    results = Professor.query.limit(20)
    for ele in results:        
        tags = [tag.name for tag in ele.interests]
        research_set.append({'name': ele.name, 'school': ele.school, 'major': ele.major,
                             'link': ele.school_url, 'website': ele.home_page,
                             'position': ele.position, 'term': ele.term, 'tags': tags})
    return json.dumps(research_set, ensure_ascii=False)


@research_page.route('/getProfessorsList/<school>/<major>', methods=['POST'])
def get_professor_list(school, major):
    research_set = []
    tag = request.json.get("tag", None)
    position = request.json.get("position", None)
    if tag:
        results = Professor.query.filter(Professor.interests.any(name=tag))
    else:
        results = Professor.query.filter_by(major=major)
    if school != '0':
        results = results.filter_by(school=school)
    if position:
        results = results.filter_by(position=True)

    for ele in results:        
        tags = [tag.name for tag in ele.interests]
        research_set.append({'name': ele.name, 'school': ele.school, 'major': ele.major,
                             'link': ele.school_url, 'website': ele.home_page,
                             'position': ele.position, 'term': ele.term, 'tags': tags})
    return json.dumps({"list": research_set}, ensure_ascii=False)


@research_page.route('/getProfessorByInterests/<major>/<interest>')
def get_professor_by_interests(major, interest):
    research_set = []
    results = Professor.query.filter(Professor.interests.any(name=interest)).filter_by(major=major).all()
    for ele in results:        
        tags = [tag.name for tag in ele.interests]
        research_set.append({'name': ele.name, 'school': ele.school, 'major': ele.major,
                             'link': ele.school_url, 'website': ele.home_page,
                             'position': ele.position, 'term': ele.term, 'tags': tags})
    return json.dumps({"list": research_set}, ensure_ascii=False)


@research_page.route('/getMajorInterestsList/<major>')
def get_major_interests_list(major):
    research_set = []
    results = Interests.query.filter_by(major=major).order_by(asc(Interests.name)).all()
    for ele in results:
        research_set.append({'name': ele.name, 'zh': ele.zh_name, 'category_name': ele.category_name})
    return json.dumps({"list": research_set}, ensure_ascii=False)


@research_page.route('/research_form.html')
def research_form():
    meta = {'title': u'学者研究兴趣 知维图 -- 互联网学习实验室',
            'description': u'学者研究兴趣信息库，主要就是学校、主页、研究方向、招生与否',
            'keywords': u'zhimind 美国 大学 CS 研究方向 research interests 招生'}
    verification_code = StringField(u'验证码', 
                                    validators=[validators.DataRequired(),
                                                validators.Length
                                                (4, 4, message=u'填写4位验证码')])
    return render_template('research_form.html', veri=verification_code, meta=meta,
                           types="research")


@research_page.route('/getResearchProgress', methods=['POST'])
def process():
    url = request.json.get("url", None)
    if not url:
        return json.dumps({'error': "%s not received" % url}, ensure_ascii=False)

    return json.dumps({'info': session['research_process'+url]}, ensure_ascii=False)


def query_add_interests(tag, major):
    try:
        result = Interests.query.filter_by(name=tag, major=major).one_or_none()
        if result is None and len(tag) < 50:
            result = Interests(tag, major)
            db.session.add(result)
        return result
    except MultipleResultsFound:
        return None


def query_add_professor(name, college_name, major):
    try:
        result = Professor.query.filter_by(name=name, school=college_name, 
                                           major=major).one_or_none()
        if result is None:
            # app.logger.info("%s not exists, create" % name)
            if name > 29:
                words = re.findall("(\w+)", name)
                name = words[0] + ' ' + words[-1]
            if college_name > 59:
                college_name = college_name[:57] + '..)'
            result = Professor(name, college_name, major)
            db.session.add(result)
        else:
            # app.logger.info("%s not exists, not create" % name)
            pass
        return result
    except MultipleResultsFound:
        return None


def is_exist_college(c_list, name):
    for c in c_list:
        if c['name'] == name:
            return True
    return False


@research_page.route('/custom_crawler.html')
def custom_crawler():
    verification_code = StringField(u'验证码', 
                                    validators=[validators.DataRequired(),
                                                validators.Length
                                                (4, 4, message=u'填写4位验证码')])
    meta = {'title': u'学者研究兴趣 知维图 -- 互联网学习实验室',
            'description': u'学者研究兴趣信息库，主要就是学校、主页、研究方向、招生与否',
            'keywords': u'zhimind 美国 大学 CS 研究方向 research interests 招生'}
    return render_template('custom_crawler.html', meta=meta, temp=0,
                           veri=verification_code, types="research")


def validate_and_extract(request):
    if not app.debug:
        verification_code = request.form['verification_code']
        code_text = session['code_text']
        if verification_code != code_text:
            return u'Error at 验证码错误', None, None, None

    major = request.form['major']
    college_name = request.form['college_name']
    directory_url = request.form['directory_url']
    professor_url = request.form['professor_url']
    
   #if major == '0' or not college_name.strip() or not directory_url.strip() or\
   #   not professor_url.strip():
   #    return u'Error at 信息不全', None, None, None

    return college_name, major, directory_url, professor_url


def query_and_create_task(college, major):
    try:
        entity = app.redis.get('college')
        if entity and eval(entity):
            entity = eval(entity)
            flag = is_exist_college(entity, college)
        else:
            college_set = getCollegeRedis()
            app.redis.set('college', college_set)
            flag = is_exist_college(entity, college_set)
        if not flag:
            return u'Error at 数据有误，不存在该学校，请确认校名或联系开发者'
        task = CrawlTask.query.filter_by(school=college, major=major).one_or_none()
        if task:
            return u'Error at 该校该专业爬取任务已存在，数据错误问题请联系开发者'
    except MultipleResultsFound:
        return u'Error at 数据有误，存在多所同名学校，请联系开发者'
    return task


def crawl_directory(crawl, faculty_list, major, directory_url, count, flag):
    app.redis.set('process of %s %s' % (directory_url, major), "%d,0" % count)
    i = 0
    link_list = []
    for link in faculty_list:
        link_list.append(crawl.dive_into_page(link, flag))
        i += 1
        app.redis.set('process of %s %s' % (directory_url, major), "%d,%d" % (count, i))
    app.logger.info('research process %s %s ' % (directory_url, major) + "  finish")
    app.redis.set('%s-%s' % (directory_url, major), link_list)
    return link_list


def submit_professors(college_name, major, directory_url):
    entity = eval(app.redis.get('%s-%s' % (directory_url, major)))
    for ele in entity:
        professor = None
        if ele.get("name", None):
            professor = query_add_professor(ele.get("name"), college_name, major)
        if ele.get('tags'):
            for tag in ele.get('tags', []):
                tag_obj = query_add_interests(tag, major)
                if professor and tag_obj:
                    professor.interests.append(tag_obj)
        if professor:
            professor.position = ele.get("position")
            professor.term = ele.get("term")
            professor.school_url = ele.get("link", "")
            professor.home_page = ele.get("website", "")
    try:
        db.session.commit()
    except InvalidRequestError:
        app.logger.info(traceback.print_exc())
        return "Error at 我也不知道提交出了什么错"
    return ""


def update_key_words(form, crawl):
    key_words = crawl.key_words
    flag = False
    for k in key_words:
        if k not in form:
            continue
        if ','.join(key_words[k]) == form[k]:
            continue
        key_words[k] = form[k].split(',')
        flag = True

    return flag, key_words

@research_page.route('/custom_crawler/<int:step>', methods=['POST'])
def custom_crawler_step(step):
    college, major, directory_url, prof_url = validate_and_extract(request)
    code_img, code_string = create_validate_code()
    session['code_text'] = code_string
    task = query_and_create_task(college, major)
    crawl = ResearchCrawler(directory_url, prof_url)
    flag, key_words = update_key_words(request.form, crawl)
    if flag:
        crawl.key_words = key_words
        temp = crawl.save_key()
        if temp and temp.startswith("Error"):
            return json.dumps({'error': temp}, ensure_ascii=False)

    count, faculty_list = crawl.crawl_faculty_list(directory_url, prof_url)

    if step == 1:
        link_list = []
        for link in faculty_list:
            link_list.append(link.get("href") + "|" + link.string)
        return json.dumps({'info': u'成功', "list": link_list, 'keywords': crawl.key_words},
                          ensure_ascii=False)
    elif step == 2:
        app.logger.info("%s %s total %d, start" % (directory_url, major, count))
        link_list = crawl_directory(crawl, faculty_list, major, directory_url, count, True)
        app.logger.info("%s %s total %d, finish" % (directory_url, major, count))
        return json.dumps({'info': u'成功', "list": link_list, 'keywords': crawl.key_words},
                          ensure_ascii=False)
    elif step == 3:
        code_img, code_string = create_validate_code()
        session['code_text'] = code_string
        if task is None:
            task = CrawlTask(college, major, directory_url, prof_url)
            db.session.add(task)
        result = submit_professors(college, major, directory_url)
        if result.startswith("Error"):
            return json.dumps({'error': result}, ensure_ascii=False)
        return json.dumps({'info': u'成功'}, ensure_ascii=False)

    return json.dumps("Error , step 4 ?")
        

@research_page.route('/research_submitted', methods=['POST'])
def submitted_research():
    college, major, directory_url, prof_url = validate_and_extract(request)
    task = query_and_create_task(college, major)
    if isinstance(task, (str, unicode)):
        return json.dumps({'error': task}, ensure_ascii=False)

    app.logger.info(directory_url)

    approve = request.form['approve']
    if approve == '1':
        code_img, code_string = create_validate_code()
        session['code_text'] = code_string
        if task is None:
            task = CrawlTask(college, major, directory_url, prof_url)
            db.session.add(task)
        result = submit_professors(college, major, directory_url)
        if result.startswith("Error"):
            return json.dumps({'error': result}, ensure_ascii=False)
        return json.dumps({'info': u'成功'}, ensure_ascii=False)

    crawl = ResearchCrawler(directory_url, prof_url)
    count, faculty_list = crawl.crawl_faculty_list(directory_url, prof_url)
    app.logger.info("%s %s total %d, start" % (directory_url, major, count))
    link_list = crawl_directory(crawl, faculty_list, major,  directory_url, count, False)
    app.logger.info("%s %s total %d, finish" % (directory_url, major, count))
    return json.dumps({'info': u'成功', "list": link_list}, ensure_ascii=False)


@research_page.route('/interests.html')
def interests_page():
    meta = {'title': u'学者研究兴趣 知维图 -- 互联网学习实验室',
            'description': u'学者研究兴趣信息库，主要就是学校、主页、研究方向、招生与否',
            'keywords': u'zhimind 美国 大学 CS 研究方向 research interests 招生'}
    return render_template('interests.html', meta=meta, temp=0,
                           types="research")


@research_page.route('/modifyInterests', methods=['POST'])
def modify_interests():

    name = request.json.get('name', None)

    action = str(request.json.get('type', None))
    if not name or not action:
        return json.dumps({'error': '%s %s not right' % (name, action)}, ensure_ascii=False)

    try:
        interest = Interests.query.filter_by(name=name).one_or_none()
        if action == "1":
            if interest:
                results = Professor.query.filter(Professor.interests.any(name=name)).all()
                for ele in results:
                    ele.interests.remove(interest)
                db.session.delete(interest)
            else:
                return json.dumps({'error': 'not find' + name}, ensure_ascii=False)
        else:
            if interest is None:
                return json.dumps({'error': 'not find' + name}, ensure_ascii=False)
            else:
                interest.zh_name = request.json.get('zh', None)
                interest.category_name = request.json.get('category', None)
        db.session.commit()
        return json.dumps({'info': 'success'}, ensure_ascii=False)
    except Exception, e:
        app.logger.info(traceback.print_exc())
    return json.dumps({'error': 'not find'}, ensure_ascii=False)
