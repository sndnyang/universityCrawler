# -*- coding: utf-8 -*-
import sys

import re
import json
import traceback

from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.exc import InvalidRequestError

import nltk.stem
s = nltk.stem.SnowballStemmer('english')

from trim_models import *

def get_shortest_stem():
    temp = None
    with open("stem_maps.json") as fp:
        temp = json.load(fp, strict=False)
    return temp


def update_shortest_stem(tag_set, stem_shortest):
    for tag in tag_set:
        w = tag["name"]
        if re.search("\d+", w) and not re.search("3D", w, re.I):
            continue
        for e in re.split("(\w+)", w):
            e = e.strip()
            if not e:
                continue
            stem = s.stem(e)
            # print e, stem
            if stem not in stem_shortest:
                stem_shortest[stem] = e
            if len(e) < len(stem_shortest[stem]):
                # print stem, stem_shortest[stem], e
                stem_shortest[stem] = e


def gen_tag_set():
    tag_set = []
    results = Interests.query.all()
    for e in results:
        tag_set.append({'name': e.name, 'up': e.category_name, 'zh': e.zh_name})
    print len(tag_set)
    return tag_set
        

def merge_word_id(old_id, new_id):
    if old_id == new_id:
        return
    print("'%s' to '%s'" % (old_id, new_id))
    old_tag = Interests.query.get(old_id)
    new_tag = Interests.query.get(new_id)
    results = Professor.query.filter(Professor.interests.any(name=old_tag.name)).all()
    print 'has %d professor' % len(results)
    
    for ele in results:
        try:
            ele.interests.remove(old_tag)
            ele.interests.append(new_tag)
        except ValueError:
            continue
    db.session.delete(old_tag)
    db.session.commit()
    print "delete %s" % old_id
    return new_tag
    

def delete_tag_in_relation(ele, tid):
    cursor = db.session.query(professor_interests_table)\
               .filter(professor_interests_table.c.professor_id==ele.id,
                       professor_interests_table.c.interests_id==tid)
    es = cursor.all()
    print "%s professor_id = '%s' and interests_id = '%s'" % (ele.name, ele.id, tid)
    cursor.delete(synchronize_session=False)


def delete_tag_by_id(tid):
    old_tag = Interests.query.get(tid)
    results = Professor.query.filter(Professor.interests.any(id=tid)).all()
    try:
        for ele in results:
            delete_tag_in_relation(ele, tid)
        db.session.delete(old_tag)
        db.session.commit()
    except InvalidRequestError:
        print "old_tag not remove", old_tag.name
        db.session.rollback()


def delete_tag_by_name(name):
    tags = Interests.query.filter_by(name=name).all()
    for t in tags:
        delete_tag_by_id(t.id)


def delete_tag_by_pattern(tag_set, pattern, d=0):
    for t in tag_set:
        if re.search(r"%s" % pattern, t["name"]):
            print t["name"]
            if d:
                a = raw_input("do you want to delete %s ?(y/n)[n]" % t["name"])
                if a != 'y':
                    continue
                delete_tag_by_name(t["name"])
                tag_set.remove(t)
        # else:
        #     query_name(t)
    

def merge_word_all_major(old, old_tag, new_word):
    try:
        new_tag = Interests.query.filter_by(name=new_word, major=old_tag.major).one_or_none()
    except MultipleResultsFound:
        tags = Interests.query.filter_by(name=new_word).all()
        print len(tags)
        from itertools import permutations
        for a, b in permutations(range(len(tags)), 2):
            print "%s and %s" % (tags[a].major, tags[b].major)
            if tags[b].major.startswith(tags[a].major):
                new_tag = merge_word_id(tags[a].id, tags[b].id)
        new_tag = Interests.query.filter_by(name=new_word, major=old_tag.major.split('-')[0]).one_or_none()

    if not new_tag:
        old_tag.name = new_word
        print("change a name")
        db.session.commit()
        return
    results = Professor.query.filter(Professor.interests.any(name=old)).all()
    print len(results)
    try:
        for ele in results:
            delete_tag_in_relation(ele, old_tag.id)
            ele.interests.append(new_tag)

        db.session.delete(old_tag)
        db.session.commit()
    except Exception, e:
        traceback.print_exc()
        print old, old_tag["name"]


def merge_word(old, new_word):
    if old == new_word or not new_word:
        return
    print("'%s' to '%s'" % (old, new_word))
    try:
        old_tag = Interests.query.filter_by(name=old).one_or_none()
        if not old_tag:
            print("can't trans")
            return
        merge_word_all_major(old, old_tag, new_word)
    except MultipleResultsFound:
        tags = Interests.query.filter_by(name=old).all()
        print len(tags)
        from itertools import permutations
        for a, b in permutations(range(len(tags)), 2):
            print "%s and %s" % (tags[a].major, tags[b].major)
            if tags[b].major.startswith(tags[a].major):
                old_tag = merge_word_id(tags[a].id, tags[b].id)
        tags = Interests.query.filter_by(name=old).all()
        for old_tag in tags:
            merge_word_all_major(old, old_tag, new_word)
    

def generate_stem(w, stem_shortest):
    words = []
    for e in re.split("(\w+)", w):
        if e.strip():
            if e not in ['P2P', 'K12', '3D', '2D', '1D', '4G', '5G']:
                e = str(s.stem(e.strip()))

            if e not in stem_shortest:
                words.append(e)
            else:
                words.append(stem_shortest[e])
    stems = ' '.join(words)
    if re.search("[1-3]\s*d ", stems, re.I):
        stems = re.sub("3\s*d ", "3D ", stems)
    if re.search("k\s*12 ", stems, re.I):
        stems = re.sub("k\s*12 ", "K12 ", stems)
    if re.search(r"\bp2p\b", stems):
        stems = re.sub(r"\bp2p\b", "P2P", stems)
    return stems

def convert_stem(tag_set, stem_shortest):
    for tag in tag_set:
        w = tag["name"]
        if re.search(r"\d+", w) and not re.search("[1-3]\s*d", w, re.I)\
            and not re.search(r"\bp2p\b", w, re.I) and not re.search("k\s*12 ", w, re.I):
            a = raw_input("do you want to delete %s ?(y/n)[n]" % w)
            if a == 'y':
                delete_tag_by_name(w)
                continue
        try:
            t = w.replace(u"−", " ").replace(u"•", " ")
            stems = generate_stem(t, stem_shortest)
            if w != stems:
                print w, stems
                merge_word(w, stems)
        except UnicodeEncodeError:
            pass


def update_to_category_major(e):
    name = e['name']
    major = e['major']
    try:
        old_tag = Interests.query.filter_by(name=name, major=major).one_or_none()
        if not old_tag:
            print("can't trans")
            return
        new_tag = Interests.query.filter_by(name=name, major=major.split('-')[0]).one_or_none()

    except MultipleResultsFound:
        print "%s and %s has duplicate" % (name, major)
        return

    if not new_tag:
        old_tag.major = major.split('-')[0]
        print("change major of %s and %s " % (name, major))
        db.session.commit()
        return
    results = Professor.query.filter(Professor.interests.any(name=name, major=major)).all()
    print len(results)
    try:
        for ele in results:
            try:
                ele.interests.remove(old_tag)
            except ValueError:
                continue
            ele.interests.append(new_tag)

        db.session.delete(old_tag)
        db.session.commit()
    except Exception,e:
        traceback.print_exc()
        print name, old_tag.major, new_tag.major


def merge_major():
    tag_set = []
    results = Interests.query.all()
    for e in results:
        tag_set.append({'name': e["name"], 'major': e.major})
    for e in tag_set:
        if '-' not in e['major']:
            continue
        print e['major']
        update_to_category_major(e)


def process():
    tag_set = gen_tag_set()
    stem_shortest = get_shortest_stem()
    update_shortest_stem(tag_set, stem_shortest)
    convert_stem(tag_set, stem_shortest)


def query_name(tag_set, name):

    # tags = Interests.query.filter_by(name=name).all()
    for tag in tag_set:
        if name != tag['name']:
            continue
        print(u"研究方向 %s " % name)
        ps = Professor.query.filter(Professor.interests.any(name=tag['name'])).all()
        print u"有 %d 位教授在研究， 他们分别是" % len(ps)
        for p in ps:
            print("   %s  %s %s" % (p.name, p.school, p.major))
            print(u"  有 %d 个研究方向" % len(p.interests))
            for t in p.interests:
                print(t.name)


def set_same_name_by_name(name, zh, up):
    tags = Interests.query.filter_by(name=name).all()
    print(u"研究方向 %s " % name)
    
    for tag in tags:
        flag = False
        if tag.zh_name != zh:
            tag.zh_name = zh
            flag = True
        if tag.category_name != up:
            tag.category_name = up
            flag = True
        if flag:
            db.session.commit()


if __name__ == '__main__':
    process()
