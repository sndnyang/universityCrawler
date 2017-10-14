# -*- coding:utf-8 -*-

import os
import re
import traceback

from flask import request, render_template, session, json, Blueprint, g
from sqlalchemy.exc import InvalidRequestError
from wtforms import StringField, validators
from sqlalchemy import asc, or_
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.exc import IntegrityError

from ..validation import *
from mindmap import app, db

from models import *
from crawler import ResearchCrawler
from views import getCollegeRedis


research_page = Blueprint('research_page', __name__,
                          template_folder=os.path.join(
                             os.path.dirname(__file__), 'templates'),
                          static_folder="static")
version = 2

@research_page.route('/research.html')
@research_page.route('/research')
def research_index():
    meta = {'title': u'学者研究兴趣 知维图 -- 互联网学习实验室',
            'description': u'学者研究兴趣信息库，主要就是学校、主页、研究方向、招生与否',
            'keywords': u'zhimind 美国 大学 CS 研究方向 research interests 招生'}
    return render_template('research.html', meta=meta, temp=0,
                           types="research", version=version)


def convertToDict(ele, tags):
    data = {'id': ele.id, 'name': ele.name, 'school': ele.school, 
            'major': ele.major,
            'link': ele.school_url, 'website': ele.home_page,
            'position': ele.position, 'term': ele.term, 'tags': tags}
    return data


@research_page.route('/researchList')
def research_list_page():
    research_set = []
    results = Professor.query.filter_by(position=True).limit(20)
    for ele in results:        
        tags = [tag.name for tag in ele.interests]
        research_set.append(convertToDict(ele, tags))
    return json.dumps(research_set, ensure_ascii=False)


@research_page.route('/getProfessorsList/<school>/<major>', methods=['POST'])
def get_professor_list(school, major):
    research_set = []
    tag = request.json.get("tag", None)
    position = request.json.get("position", None)
    if tag:
        rule = or_(Professor.interests.any(name=tag), Professor.interests.any(category_name=tag))
        results = Professor.query.filter(rule)
    else:
        rule = or_(Professor.major == major, Professor.major.like("%s-%%" % major))
        results = Professor.query.filter(rule)
    if school != '0':
        results = results.filter_by(school=school)
    if position:
        results = results.filter_by(position=True)

    for ele in results:        
        tags = [tag.name for tag in ele.interests]
        research_set.append(convertToDict(ele, tags))
    research_set.sort(key=lambda x:x['name'])
    return json.dumps({"list": research_set}, ensure_ascii=False)


@research_page.route('/getProfessorByInterests/<major>/<interest>')
def get_professor_by_interests(major, interest):
    research_set = []
    rule = or_(Professor.interests.any(name=interest), Professor.interests.any(category_name=interest))
    results = Professor.query.filter(rule).filter_by(major=major).all()
    for ele in results:        
        tags = [tag.name for tag in ele.interests]
        research_set.append(convertToDict(ele, tags))
    return json.dumps({"list": research_set}, ensure_ascii=False)


@research_page.route('/getMajorInterestsList/<major>')
def get_major_interests_list(major):
    research_set = []
    rule = or_(Interests.major == major, Interests.major.like("%s-%%" % major))
    results = Interests.query.filter(rule).order_by(asc(Interests.name)).all()
    # results = Interests.query.filter_by(major=major)
    for ele in results:
        research_set.append({'id': ele.id, 'name': ele.name, 'zh': ele.zh_name, 
                            'category_name': ele.category_name})
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
    return render_template('research_form.html', veri=verification_code, 
                           meta=meta, types="research", version=version)


@research_page.route('/getResearchProgress', methods=['POST'])
def process():
    url = request.json.get("url", None)
    if not url:
        return json.dumps({'error': "%s not received" % url}, ensure_ascii=False)

    return json.dumps({'info': session['research_process'+url]}, ensure_ascii=False)


def query_add_interests(tag, major):
    try:
        result = Interests.query.filter_by(name=tag, major=major.split('-')[0]).one_or_none()
        if result is None and len(tag) < 50:
            result = Interests(tag, major.split('-')[0])
            db.session.add(result)
            db.session.commit()
        return result
    except MultipleResultsFound:
        return None


def query_add_professor(name, college_name, major):
    try:
        result = Professor.query.filter_by(name=name, school=college_name, 
                                           major=major).one_or_none()
        if result is None:
            if len(name) > 29:
                words = re.findall("(\w+)", name)
                name = words[0] + ' ' + words[-1]
            if len(college_name) > 59:
                college_name = college_name[:57] + '..)'
            result = Professor(name, college_name, major)
            db.session.add(result)
        else:
            pass
        return result
    except MultipleResultsFound:
        app.logger.info("%s find multi" % name)
        return None


def is_exist_college(c_list, name):
    for c in c_list:
        if c['name'] == name:
            return True
    return False


@research_page.route('/research_task.html')
def research_task():
    meta = {'title': u'学者研究兴趣 知维图 -- 互联网学习实验室',
            'description': u'学者研究兴趣信息库，主要就是学校、主页、研究方向、招生与否',
            'keywords': u'zhimind 美国 大学 CS 研究方向 research interests 招生'}
    tasks = CrawlTask.query.all()
    return render_template('research_task.html', meta=meta, tasks=tasks,
                           version=version)


@research_page.route('/custom_crawler.html/<task_id>')
@research_page.route('/custom_crawler.html')
def custom_crawler(task_id=None):
    verification_code = StringField(u'验证码', 
                                    validators=[validators.DataRequired(),
                                                validators.Length
                                                (4, 4, message=u'填写4位验证码')])
    meta = {'title': u'学者研究兴趣 知维图 -- 互联网学习实验室',
            'description': u'学者研究兴趣信息库，主要就是学校、主页、研究方向、招生与否',
            'keywords': u'zhimind 美国 大学 CS 研究方向 research interests 招生'}
    task = {'school': '', 'example': '', 'school': '', 'major': '0'}
    if task_id:
        task = CrawlTask.query.get(task_id)
    return render_template('custom_crawler.html', meta=meta, temp=0,
                           veri=verification_code, types="research",
                           task=task, version=version)


def validate_and_extract(form):
    if not (g.user and g.user.is_authenticated and 
            g.user.get_name() == 'sndnyang'):
        verification_code = form['verification_code']
        code_text = session['code_text']
        if verification_code != code_text:
            return u'Error at 验证码错误', None, None, None

    major = form.get('major', "0")
    college_name = form.get('college_name', "")
    directory_url = form.get('directory_url', "")
    professor_url = form.get('professor_url', "")
    
    if major == '0' or not college_name.strip() or not directory_url.strip()\
       or not professor_url.strip():
        return u'Error at 信息不全', None, None, None

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
        return CrawlTask.query.filter_by(school=college, major=major).one_or_none()
        
    except MultipleResultsFound:
        return u'Error at 数据有误，存在多所同名学校，请联系开发者'


def crawl_directory(crawl, faculty_list, major, directory_url, count, flag):
    # app.redis.set('process of %s %s' % (directory_url, major), "%d,0" % count)
    app.logger.info('process of %s %s' % (directory_url, major))
    i = 0
    link_list = []
    for link in faculty_list:
        try:
            link_list.append(crawl.dive_into_page(link, flag))
            # app.redis.set('process of %s %s' % (directory_url, major), "%d,%d" % (count, i))
            app.logger.info('process of %s %s' % (link, major) + " %d,%d" % (count, i))
        except:
            app.logger.info(traceback.print_exc())
            app.logger.info('process of %s %s fail' % (link, major) + " %d,%d" % (count, i))
        i += 1

    app.logger.info('research process %s %s ' % (directory_url, major) + "  finish")
    app.redis.set('%s-%s' % (directory_url, major), link_list)
    return link_list


def submit_professors(college_name, major, directory_url):
    entity = eval(app.redis.get('%s-%s' % (directory_url, major)))
    for ele in entity:
        professor = None
        try:
            if ele.get("name", None):
                name = ele.get("name").strip()
                professor = query_add_professor(name, college_name, major)
                if professor:
                    professor.position = ele.get("position")
                    professor.term = ele.get("term")
                    professor.school_url = ele.get("link", "")
                    if ele.get("website", ""):
                        professor.home_page = ele.get("website", "")
                    db.session.commit()
            if ele.get('tags'):
                for tag in ele.get('tags', []):
                    tag_obj = query_add_interests(tag, major)
                    exist = Professor.query.filter_by(name=name, 
                                                      school=college_name, 
                                                      major=major)\
                                     .filter(Professor.interests.any(name=tag)
                                             ).one_or_none()
                    # app.logger.info("tag %s exist in %s? %s" % (tag, ele.get("name"), str(exist is not None)))
                    if professor and tag_obj and exist is None:
                        professor.interests.append(tag_obj)
        except IntegrityError:
            app.logger.info(traceback.print_exc())
            app.logger.info(" professor %s roll back" % ele.get("name"))
            db.session.rollback()
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
        if form[k].strip() and form[k].strip()[-1] == ',':
            return u"Error at %s 的最后一个符号是逗号" % k
        if ','.join(key_words[k]) == form[k]:
            continue
        key_words[k] = form[k].split(',')
        flag = True

    if flag:
        crawl.key_words = key_words
        temp = crawl.save_key()
        if temp and temp.startswith("Error"):
            return temp
    return None


@research_page.route('/custom_crawler/<int:step>', methods=['POST'])
def custom_crawler_step(step):
    college, major, directory_url, prof_url = validate_and_extract(request.form)
    if major is None:
        return json.dumps({'error': college}, ensure_ascii=False)
    task = query_and_create_task(college, major)
    if isinstance(task, unicode) and task.startswith("Error at"):
        return json.dumps({'error': task}, ensure_ascii=False)

    if task is None:
        task = CrawlTask(college, major, directory_url, prof_url)
        db.session.add(task)
        db.session.commit()


    crawl = ResearchCrawler(directory_url, prof_url, major)
    flag = update_key_words(request.form, crawl)
    if flag:
        return json.dumps({'error': flag}, ensure_ascii=False)

    force = False
    if step == 1:
        force = True
    count, faculty_list = crawl.crawl_faculty_list(directory_url, prof_url, force=force, major=major)
    if not isinstance(faculty_list, list):
        return json.dumps({'error': faculty_list})

    if step == 1:
        link_list = []
        for link in faculty_list:
            link_list.append(link.get("href") + "|" + str(link.get_text()))
        return json.dumps({'info': u'成功', "list": link_list, 'keywords': crawl.key_words},
                          ensure_ascii=False)
    elif step == 2:
        app.logger.info("%s %s total %d, start" % (directory_url, major, count))
        link_list = crawl_directory(crawl, faculty_list, major, directory_url, count, True)
        app.logger.info("%s %s total %d, finish" % (directory_url, major, count))
        return json.dumps({'info': u'成功', "list": link_list, 'keywords': crawl.key_words},
                          ensure_ascii=False)
    elif step == 3:
        if task and (task.school_url != directory_url or task.example != prof_url):
            task.school_url = directory_url
            task.example = prof_url
            db.session.commit()
        result = submit_professors(college, major, directory_url)
        if result.startswith("Error"):
            return json.dumps({'error': result}, ensure_ascii=False)
        return json.dumps({'info': u'成功'}, ensure_ascii=False)

    return json.dumps("Error , step 4 ?")
        

@research_page.route('/research_submitted', methods=['POST'])
def submitted_research():
    college, major, directory_url, prof_url = validate_and_extract(request.form)
    if major is None:
        return json.dumps({'error': college}, ensure_ascii=False)
    task = query_and_create_task(college, major)
    if isinstance(task, (str, unicode)):
        return json.dumps({'error': task}, ensure_ascii=False)

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

    crawl = ResearchCrawler(directory_url, prof_url, major)
    count, faculty_list = crawl.crawl_faculty_list(directory_url, prof_url)
    link_list = crawl_directory(crawl, faculty_list, major,  directory_url, count, False)
    return json.dumps({'info': u'成功', "list": link_list}, ensure_ascii=False)


@research_page.route('/interests.html')
def interests_page():
    meta = {'title': u'学者研究兴趣 知维图 -- 互联网学习实验室',
            'description': u'学者研究兴趣信息库，主要就是学校、主页、研究方向、招生与否',
            'keywords': u'zhimind 美国 大学 CS 研究方向 research interests 招生'}
    return render_template('interests.html', meta=meta, temp=0,
                           types="research", version=version)


@research_page.route('/togglePosition', methods=['POST'])
def query_position():
    pid = request.json.get("pid")
    if not pid:
        return json.dumps({'error': 'pid %s not right' % pid}, ensure_ascii=False)

    p = None
    t = ""
    text = ""
    try:
        prof = Professor.query.get(pid)
        school = prof.school
        major = prof.major

        task = CrawlTask.query.filter_by(school=school, major=major).one_or_none()

        if not task:
            return json.dumps({'error': 'school %s, major %s find multiple, email me!'
                                % (school, major)}, ensure_ascii=False)

        url = request.json.get("url")
        if url:
            prof.home_page = url if url.startswith("http") else "http://" + url
            db.session.commit()

        crawler = ResearchCrawler(prof.school_url, "", major)
        p, t, text = crawler.query_position_status(prof.school_url, 
                                                   prof.home_page)
        
        if p is None and text.startswith('Error'):
            return json.dumps({'error': '%s and %s not open' % 
                               (prof.school_url, prof.home_page)}, 
                               ensure_ascii=False)

    except MultipleResultsFound:
        return json.dumps({'error': 'school %s, major %s find multiple, email me!'
                            % (school, major)}, ensure_ascii=False)

    return json.dumps({'status': True, "position": p, "term": t, "text": text}, 
                      ensure_ascii=False)


def delete_tag_in_relation(ele, tid):
    cursor = db.session.query(professor_interests_table)\
               .filter(professor_interests_table.c.professor_id==ele.id,
                       professor_interests_table.c.interests_id==tid)
    es = cursor.all()
    # print "%s professor_id = '%s' and interests_id = '%s'" % (ele.name, ele.id, tid)
    cursor.delete(synchronize_session=False)


@research_page.route('/modifyInterests', methods=['POST'])
def modify_interests():

    tid = request.json.get('id', None)
    name = request.json.get('name', None)

    action = str(request.json.get('type', None))
    if not name or not action:
        return json.dumps({'error': '%s %s not right' % (name, action)}, ensure_ascii=False)

    try:
        old_interest = Interests.query.get(tid)
        new_interest = Interests.query.filter_by(name=name, major=old_interest.major).one_or_none()
        if action == "1":
            if old_interest is None:
                return json.dumps({'error': 'not find id %s name %s'%(tid,name)}, ensure_ascii=False)
            results = Professor.query.filter(Professor.interests.any(name=old_interest.name)).all()
            for ele in results:
                delete_tag_in_relation(ele, tid)

            db.session.delete(old_interest)
        else:
            if old_interest is None:
                return json.dumps({'error': 'not find id %s name %s'%(tid,name)}, ensure_ascii=False)
            
            if old_interest.name != name and new_interest is None:
                old_interest.name = name
                zh = request.json.get('zh')
                if zh:
                    old_interest.zh_name = zh
                old_interest.category_name = request.json.get('category', None)
            elif old_interest.name == name:
                old_interest.zh_name = request.json.get('zh', None)
                old_interest.category_name = request.json.get('category', None)
            elif old_interest.name != name and new_interest is not None:
                results = Professor.query.filter(Professor.interests.any(name=old_interest.name)).all()
                for ele in results:
                    delete_tag_in_relation(ele, tid)
                    if not Professor.query.filter(Professor.interests.any(name=name))\
                       .filter_by(id=ele.id).one_or_none():
                        ele.interests.append(new_interest)
                zh = request.json.get('zh')
                if zh and new_interest.zh_name is None:
                    new_interest.zh_name = zh
                db.session.delete(old_interest)
        db.session.commit()
        return json.dumps({'info': 'success'}, ensure_ascii=False)
    except Exception:
        app.logger.info(traceback.print_exc())
    return json.dumps({'error': 'not find'}, ensure_ascii=False)
