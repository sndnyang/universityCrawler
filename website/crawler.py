# coding: utf-8

import os
import re
import json
import logging
import urllib2
import urlparse
import HTMLParser

import requests
from bs4.element import Comment
from bs4 import BeautifulSoup

from requests import ConnectionError, HTTPError
import nltk

debug_level = ""

logger = logging.getLogger('crawler')
fmter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
log_file_name = os.path.join(os.environ.get('OPENSHIFT_PYTHON_LOG_DIR', '.'),
                             'crawl.log')
hdlr = logging.FileHandler(log_file_name, mode='a')
hdlr.setLevel(logging.INFO)
hdlr.setFormatter(fmter)

# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# ch.setFormatter(fmter)
logger.addHandler(hdlr)
# logger.addHandler(ch)
logger.setLevel(logging.INFO)


def replace_html(s):
    s = s.replace('&quot;', '"')
    s = s.replace('&amp;', '&')
    s = s.replace('&lt;', '<')
    s = s.replace('&gt;', '>')
    s = s.replace('&nbsp;', ' ')
    return s


def contain_keys(href, keys, is_name=False, return_obj=False):
    """

    """
    if not href or not keys:
        return False
    if '~' in keys and '~' in href:
        return True

    words = "(%s)" % '|'.join(e for e in keys)
    if is_name:
        r = re.search('%s' % words, href, re.I)
        if r:
            if return_obj:
                return r
            return True
    # if debug_level.find("contain") > 0: print words
    r = re.search(r'\b%s\b' % words, href, re.I)
    if r:
        if return_obj:
            return r
        return True
    r = re.search(r'_%s' % words, href, re.I)
    if r:
        if return_obj:
            return r
        return True
    r = re.search(r'%s_' % words, href, re.I)
    if r:
        if return_obj:
            return r
        return True
    return False


def extract_name_from_url(page_url, dir_name):
    fname = page_url.split('/')[-1]
    if fname == '':
        fname = page_url.split('/')[-2]
    if fname.find("index") > -1:
        fname = '_'.join(page_url.split('/')[3:])
    if len(fname) > 20:
        fname = fname[:20]
    file_name = re.sub("[?%=]", "", dir_name + '/' + fname + '.html')
    return file_name


def get_and_store_page(page_url, university, major='1-1',force=False, 
                       name=''):
    """

    :rtype: string
    """
    # if debug_level.find("open") > 0: print("now open page url %s" % page_url)
    dir_name = os.path.join(os.environ.get('OPENSHIFT_PYTHON_LOG_DIR', '.'), 'data', university, major)
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    if name:
        file_name = extract_name_from_url(name, dir_name)
    else:
        file_name = extract_name_from_url(page_url, dir_name)

    # if debug_level.find("open") > 0: print("now save it to %s" % file_name)

    # if debug_level.find("open") > 0: print("now open page url %s" % file_name)
    if os.path.isfile(file_name) and not force:
        with open(file_name) as fp:
            html = fp.read()
    else:
        try:
            # proxies = {
            #     "http": "http://127.0.0.1:1081",
            #     "https": "http://127.0.0.1:1081",
            # }
            # if os.environ.get("DEBUG_MODE"):
            #     r = requests.get(page_url, proxies=proxies, verify=False)
            # else:
            if '?' in page_url:
                query = page_url.split('?')[1]
                page_url = page_url.split('?')[0]
                params = {}
                for e in query.split("&"):
                    parts = e.split("=")
                    if len(parts) < 2:
                        continue
                    params[parts[0]] = parts[1]
                r = requests.get(page_url, params=params, verify=False, timeout=30)
            else:
                r = requests.get(page_url, verify=False, timeout=30)
            html = r.content
        except (ConnectionError, HTTPError):
            html = "Error at " + page_url

        try:
            with open(file_name, 'w') as fp:
                fp.write(html)
        except TypeError:
            pass
    return html


def onsocial(href):
    for e in ['facebook', 'twitter', 'youtube', 'calendar', 'linkedin']:
        if e in href:
            return True
    return False


def find_all_anchor(soup):
    """

    """
    l = soup.find_all('a')
    return l


def find_example_index(l, a, index):
    logger.info("diff '%s'    with" % a)
    # if debug_level.find("list") > 0: print a
    a = a.strip().replace(" ", "%20")
    for i in range(len(l)):
        href = l[i].get("href")
        if not href:
            continue
        href = urlparse.urljoin(index, l[i].get("href")).replace(" ", "%20")
        # logger.info("diff '%s' " % href)
        # if debug_level.find("list") > 0: print href
        if href.strip() == a:
            # if debug_level.find("list") > 0: print ("find %s at %d" % (href, i))
            logger.info("find %s at %d" % (href, i))
            return i
    logger.info("find it at %d" % i)
    return -1


def filter_research_interests(alist):
    """
    暂时只想到这么多条件
    """
    result = []
    for e in alist:
        if e.parent.name == 'a':
            continue
        result.append(e)
    return result


def load_key(config, default='key.json'):
    with open(os.path.join(os.path.dirname(__file__), default)) as fp:
        key_words = json.loads(fp.read(), strict=False)
    if os.path.isfile(config):
        with open(config) as fp:
            key_words.update(json.loads(fp.read(), strict=False))
    if key_words is None:
        return u"Error at 爬虫关键词文件读取错误"
    return key_words

def save_json_file(fpath, data):
    if not fpath:
        return u"Error at 爬虫关键词文件路径错误"
    try:
        with open(fpath, 'w') as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)
    except:
        return "Error at 写入定制关键词失败"
    return None

def load_url_list(config):
    access_urls = {"access": [], "adm": [], "dir": []}
    if os.path.isfile(config):
        with open(config) as fp:
            access_urls = json.loads(fp.read(), strict=False)
    if access_urls is None:
        return u"Error at 爬虫爬取记录文件读取错误"
    return access_urls


def filter_url(e, index_url, key_words, access_urls):
    href = e.get("href")
    if not href or href == index_url:
        return False
    domain = re.search('(\w+).edu', index_url).group(1)
    href = href.strip()
    if href.find("mailto") > -1 or href.find("#") > -1:
        return False
    if href.find("javascript:void") > -1:
        return False
    # if debug_level.find("filter") > 0: print("filter %s" % href)
    href = urlparse.urljoin(index_url, href).strip()
    # logger.info(href)
    # if debug_level.find("filter") > 0: print("format to %s" % href)
    if href in access_urls:
        return False
    if href.find(domain) == -1:
        return False

    e['href'] = href
    return True


def classify_url(e, key_words):
    href = e.get("href")
    if contain_keys(href, key_words[u'院系教员目录URL可能包含']):
        return 2 
    if contain_keys(href, key_words[u'招生录取URL可能包含']):
        return 3
    if contain_keys(href, key_words[u'有用URL不可能包含']):
        return 4
    text = e.get("text")
    if contain_keys(text, key_words[u'有用URL文本不可能包含']):
        return 4
    return 1


class CollegeCrawler:
    """
    """
    def __init__(self, name, index_url):
        self.name = name
        self.index_url = index_url
        self.university_name = re.search('(\w+).edu', self.index_url).group(1)
        dir_path = os.path.join(os.path.dirname(__file__), 'crawler', self.university_name)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        self.config = os.path.join(dir_path, 'college_key.json')
        self.key_words = load_key(self.config, 'college_key.json')
        self.access_file = os.path.join(dir_path, 'access_url.json')
        self.access_url = load_url_list(self.access_file)
        self.access_url["0"] = [index_url]

    def filter_urls(self, url_list, cstep):
        access_url = []
        for i in range(cstep):
            access_url += self.access_url[str(i)]
        a_list = filter(lambda e: filter_url(e, self.index_url, 
                                             self.key_words, access_url
                                             ), url_list)
        for e in a_list:
            e['class'] = classify_url(e, self.key_words)
        return a_list

    def crawl_bfs(self, url_list, cstep, force=False):
        temp_list = []
        for e in url_list:
            url = e.get("href")
            logger.info("%s to pass" % url)
            html = get_and_store_page(url, force=force,
                                      university=self.university_name)
            if html.startswith("Error at "):
                continue
            soup = BeautifulSoup(html, 'html.parser')
            a_list = find_all_anchor(soup)
            for e in a_list:
                e['text'] = str(e.get_text()).strip()
            a_list = self.filter_urls(a_list, cstep)
            logger.info("%s has %d url to pass" % (url, len(a_list)))
            temp_list += a_list

        urls = []
        final_list = []
        for e in temp_list:
            if e['href'] not in urls:
                urls.append(e['href'])
                final_list.append(e)

        for e in final_list:
            e['class'] = classify_url(e, self.key_words)

        self.access_url[str(cstep)] = urls
        self.save_url()

        return final_list

    def save_key(self):
        return save_json_file(self.config, self.key_words)

    def save_url(self):
        return save_json_file(self.access_file, self.access_url)


def select_line_part(line, flags):
    pos = 0
    for flag in flags:
        obj = re.search("(%s)" % flag, line, re.I)
        if not obj:
            continue
        new_pos = obj.span(1)
        if new_pos[0] > pos:
            pos = new_pos[0] + len(flag)
    return line[pos:]


class ResearchCrawler:
    """
    从院系的Faculty目录中爬取有内容的教授信息
    如研究兴趣、招生机会
    """

    def __init__(self, directory_url, example, major='1-1'):
        self.example = example
        self.url = directory_url
        self.university_name = re.search('(\w+).edu', self.url).group(1)
        self.domain = '/'.join(directory_url.split("/")[:3])
        dir_path = os.path.join(os.path.dirname(__file__), 'crawler', self.university_name, major)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        self.config = os.path.join(dir_path, 'key.json')

        self.key_words = load_key(self.config)

    def open_page(self, page_url, force=False, major='1-1'):
        """

        """
        # if debug_level.find("open") > 0: print "open url", page_url
        html = get_and_store_page(page_url, force=force, major=major,
                                  university=self.university_name)
        if html.startswith("Error at "):
            return "Error to load %s " % html, None
        soup = BeautifulSoup(html, 'html.parser')
        redirect = soup.find(attrs={"http-equiv": "refresh"})
        e = None
        iframes = soup.find_all("iframe")
        for e in iframes:
            if e.parent.name != 'noscript':
                break
        else:
            e = None
        if redirect and not contain_keys(redirect['content'].split("=")[1],
                                         ['your', 'browser'], True):
            redir = redirect['content'].split("=")[1]
            origin_url = page_url
            page_url = urlparse.urljoin(page_url, redir)
            name = ''
            if self.university_name+'.edu' not in page_url.split("?")[0]:
                name = origin_url.split("?")[0][:-1] + '-2'
            # if debug_level.find("open") > 0: print("now refres %s" % page_url)
            html = get_and_store_page(page_url, force=force, major=major, 
                                      university=self.university_name,
                                      name=name)
            soup = BeautifulSoup(html, 'html.parser')
        elif soup.find("frameset"):
            frames = soup.find_all("frame")
            # if debug_level.find("frame") > 0: print("frame get %d", len(frames))
            for e in frames[1:]:
                # if debug_level.find("frame") > 0: print("frame get ", e.get("src"))
                if contain_keys(e.get("src"), self.key_words["frameset_pass"]):
                    continue
                # if debug_level.find("debug") > 0: print("frame import ", e.get("src"))
                origin_url = page_url
                page_url = urlparse.urljoin(page_url, e.get("src"))
                name = ''
                if self.university_name+'.edu' not in page_url.split("?")[0]:
                    name = origin_url.split("?")[0][:-1] + '-2'
                # if debug_level.find("open") > 0: print("now frameset %s" % page_url)
                html = get_and_store_page(page_url, force=force, major=major,
                                          university=self.university_name,
                                          name=name)
                soup = BeautifulSoup(html, 'html.parser')
        elif e:
            origin_url = page_url
            # if debug_level.find("open") > 0: print(" origin %s " % page_url)
            page_url = urlparse.urljoin(page_url, e.get("src"))
            name = ''
            if self.university_name+'.edu' not in page_url.split("?")[0]:
                name = origin_url.split("?")[0][:-1] + '-2'
            # if debug_level.find("open") > 0: print("i frame %s and %s" % (page_url, name))
            html = get_and_store_page(page_url, force=force, major=major,
                                      university=self.university_name,
                                      name=name)
            soup = BeautifulSoup(html, 'html.parser')
        return html, soup

    def crawl_faculty_list(self, directory_url, example, force=False, major='1-1'):

        content, soup = self.open_page(directory_url, force=force, major=major)
        if content.startswith("Error at "):
            return 0, "Error to load %s " % content
        anchors = find_all_anchor(soup)
        # if debug_level.find("list") > 0: print directory_url, len(anchors)
        index = find_example_index(anchors, example, directory_url)
        # if debug_level.find("list") > 0: print directory_url, len(anchors[index:]), 

        # 第一个教授主页的作用主要在这里——如果能再来一个更好
        # 求共同祖先
        count, faculty_list = self.find_faculty_list(anchors[index:], directory_url)
        return count, faculty_list

    def crawl_from_directory(self, directory_url, example):
        """
        从目录爬
        """

        count, faculty_list = self.crawl_faculty_list(directory_url, example)
        # assert count >= url_check[url]
        result = []
        for one in faculty_list:
            person = self.dive_into_page(one, False)
            result.append(person)
        return result

    def save_key(self):
        return save_json_file(self.config, self.key_words)

    def filter_list(self, e):
        href = e.get('href')
        if not href or len(href) < 5:
            return True
        # if debug_level.find("list") > 0: print href
        if href:
            if href.startswith('mailto:'):
                return True
            if contain_keys(href, self.key_words[u'教员URL不可能包含']):
                # if debug_level.find("debug") > 0: print " %s filter in not prof" % href
                return True
            if not contain_keys(href, self.key_words[u'教员URL可能包含']):
                # if debug_level.find("debug") > 0: print " %s filter in keys" % href
                return True

        return False

    def get_personal_website(self, l, page_url, name):
        # if debug_level.find("website") > 0: print('page_url: ' + page_url)

        potential_name = []
        if name:
            p = name.split()
            potential_name += [e[:5] for e in p]
            potential_name += [e for e in p]
            if len(p) == 2:
                potential_name.append(p[0][0]+p[1])
                potential_name.append(p[0]+p[1][0])
        key_words = self.key_words
        potential_name += key_words[u"个人主页URL可能包含"]

        potential_name = [e for e in potential_name if len(e) > 2 and
                          not contain_keys(e, key_words[u'教员URL可能包含'] +
                                           key_words[u'教员URL不可能包含'] +
                                           [self.university_name] +
                                           re.findall("(\w+)", self.url) +
                                           re.findall("([A-Z]*[a-z]+)", self.url)
                                           )
                          ]
        # if debug_level.find("website") > 0: print('potential name: ' + str(potential_name))

        faculty_page = ''
        page_name = ''
        mail = ''

        for a in l:
            href = a.get('href')
            if not href or len(href) < 5:
                continue
            href = urlparse.urljoin(page_url, urllib2.unquote(href.strip()))
            # if debug_level.find("website") > 0: print(' href: ' + str(href))

            suffix = href.split('.')[-1]
            if len(suffix) < 5 and contain_keys(suffix, self.key_words[u'文件而不是网页']):
                # if debug_level.find("website") > 0: print(' is a file')
                continue

            if faculty_page and mail:
                break
            
            if href in page_url or page_url in href or onsocial(href):
                # if debug_level.find("website") > 0: print(' is social network')
                continue

            if contain_keys(href, self.key_words[u'个人主页URL不可能包含']):
                # if debug_level.find("website") > 0: print(' wont contain')
                continue

            # if debug_level.find("website") > 0: print(' href: ' + str(href))
            if contain_keys(href, potential_name, True) or \
                    contain_keys(a.get_text(), potential_name + 
                                 self.key_words[u'教授个人主页可能显示为'],
                                 True):
                # if debug_level.find("website") > 0: print(' search it ok : ' + href)
                if href.find('@') > -1 or href.find("mailto") > -1:
                    mail = href
                    if '.' not in mail:
                        mail = re.sub("DOT", ".", mail)
                    if '@' not in mail:
                        mail = re.sub("AT", "@", mail)
                else:
                    faculty_page = href.strip()
                    page_name = a.get_text()

        # if debug_level.find("website") > 0: print(' final link: ' + faculty_page)
        return faculty_page, mail, page_name

    def find_faculty_list(self, l, faculty_url):
        """

        """
        count = 0
        links = []
        faculty_list = []
        # names = find_name_in_emails(l)
        # print names
        for e in l:
            if self.filter_list(e):
                continue
            href = e.get('href').strip()
            faculty_link = urlparse.urljoin(self.url, href)
            # if debug_level.find("list") > 0: print faculty_link

            if faculty_link == faculty_url:
                continue

            if faculty_link in links:
                name = e.get_text()
                # print name
                # if debug_level.find('faculty_list') > 0: print('replicate %s %s' % (name, faculty_link))
                i = links.index(faculty_link)
                if name and not faculty_list[i].string:
                    e['href'] = faculty_link
                    faculty_list[i] = e
                continue
            if e.string and contain_keys(e.string, self.key_words[u'教员URL不可能包含']):
                continue
            links.append(faculty_link)
            e['href'] = faculty_link.strip()
            faculty_list.append(e)
            count += 1
        return count, faculty_list

    def replace_words(self, line):
        line = re.sub("\s+", " ", line)
        line = line.replace("(", "").replace(")", "")
        for x in self.key_words[u'非研究兴趣的词'] + nltk.corpus.stopwords.words('english'):
            line = re.sub(r'\b%s\b' % x + '(?i)', ',', line, re.I)
        return line

    def get_open_position(self, soup):
        """

        :rtype: Boolean, Boolean, string
        """
        open_position = False
        open_term = ""
        position_text = ""
        text = re.sub("[,\s]+", " ", soup.get_text(" ", strip=True))
        # if debug_level.find("position") > 0: print(text)
        search_obj = contain_keys(text, self.key_words[u'招生意向关键词'], True, True)
        if search_obj:
            open_position = True
            index = text.find(search_obj.group(1))
            index = index - 20 if index > 20 else index
            position_text = text[index:index + 80] if len(text) > index + 80 else text[index:]
            if contain_keys(position_text, self.key_words[u"长期招生关键词"], True):
                open_term = "always"
        return open_position, open_term, position_text

    def extract_from_line(self, line, tags, tag_text):
        pref = self.key_words[u'有些方向的前缀']
        temp_sent = ''
        # if debug_level.find("extract") > 0: print(" line %s" % unicode(line.split('.')))
        for sent in line.split('.'):
            # if debug_level.find("extract") > 0: print(" sentence '%s'" % sent.strip())
            if not sent.strip():
                continue
            temp_sent += sent + "<br>"
            if contain_keys(sent, self.key_words[u'该句开始不再是研究兴趣'], True):
                break
            sent = replace_html(re.sub("\s+", " ", sent))
            sent = self.replace_words(sent)
            # if debug_level.find("extract") > 0: print("convert to %s" % sent)
            for x in re.split("[,:;?!]", sent):
                if not x or not x.strip():
                    continue
                tag = x.strip().replace("&", " and ")
                tag = re.sub(r"[+.*#_]", ' ', tag)
                tag = re.sub(r"[{}\[\]%&'=\"]", ',', tag)
                tag = re.sub(r"[-]", ' ', tag)
                tag = re.sub(r"[/\\|]", ' and ', tag)
                tag = re.sub(r"(\s+)", " ", tag)
                and_tags = [e.strip() for e in re.sub(r"\band\b", ",", tag).split(",") if e]
                for i in range(1, len(and_tags)):
                    if not and_tags[i] or not and_tags[i - 1]:
                        continue
                    if ' ' not in and_tags[i - 1] and (len(and_tags[i - 1]) < 9
                                                       or and_tags[i - 1].endswith('al')):
                        and_tags[i - 1] = "%s and %s" % (and_tags[i - 1], and_tags[i])
                and_tags = sorted(and_tags)
                # if debug_level.find('interests') > 0: print(str(tags) + ' ' + str(and_tags))
                for i in range(len(and_tags)):
                    tag = ' '.join(w if w.isupper() else w.lower()
                                   for w in and_tags[i].replace('-', ' ').split())
                    if tag.count(' ') >= 4 or len(tag) > 45:
                        continue
                    if contain_keys(tag, tags, True):
                        continue
                    if ' ' in tag or contain_keys(tag, pref, True):
                        tags.append(tag)

        if temp_sent and temp_sent not in tag_text:
            tag_text.append(temp_sent)
        return tags

    def extract_from_sibling(self, node, tags, tag_text, words):

        slog = replace_html(node.string.strip())
        node = node.parent
        pnode_text = replace_html(node.get_text()).strip()
        while pnode_text.endswith(slog):
            node = node.parent
            pnode_text = replace_html(node.get_text()).strip()

        # if debug_level.find("sibling") > 0: print("%s' '%s" % (node.get_text(), slog))
        # if debug_level.find("sibling") > 0: print("%s' '%s" % (node.get_text(), slog))

        text = re.sub("[\n\r]+", " ", unicode(node.get_text(".", strip=True)))
        if words == "interest":
            text = select_line_part(text, ["research\*interest"] + 
                                    self.key_words[u'一段研究兴趣的起始词'])
        else: 
            text = select_line_part(text, self.key_words[words] + 
                                    self.key_words[u'一段研究兴趣的起始词'])

        # text = re.sub("(</?\w+[^>]*>)+", ".", unicode(node).strip(), re.M)
        # if debug_level.find("sibling") > 0: print(" now text is " + text)

        # if debug_level.find("interests") > 0: print(" now line is " + text)

        tags = self.extract_from_line(text, tags, tag_text)
        # if debug_level.find("interests") > 0: print(" now tags is " + str(tags))

        return tags

    def find_paragraph_interests(self, result, tags, tag_text, words):
        key_words = self.key_words[u'一段研究兴趣的起始词'][:]
        if words == 'interest':
            pos_words = "(interests?)"
            key_words += ["research\*interests?"]
        else:
            pos_words = "(%s)" % '|'.join(e for e in self.key_words[words])
            key_words += self.key_words[words]

        if len(result) == 1:
            # if debug_level.find('interests') > 0: print('search the words %s ' % words)
            r = re.search(pos_words, result[0], re.I).group(1).lower()
            # if debug_level.find('interests') > 0: print(' r %s ' % r)
            if len(result[0]) > result[0].lower().find(r) + len(r) + 35:
                line = select_line_part(re.sub("\n", ".", result[0]),
                                        key_words
                                        )
                # if debug_level.find('interests') > 0: print('from the line %s ' % line)
                tags = self.extract_from_line(line, tags, tag_text)
                # if debug_level.find('interests') > 0: print("line %d ge" % len(tags))
                if tags:
                    return tags, tag_text
            node = result[0]
            # if debug_level.find('interests') > 0: print(' to find sibling %s ' % str(node))
            tags = self.extract_from_sibling(node, tags, tag_text, words)
            return tags, tag_text
        elif len(result) > 1:
            # 多个的情况太复杂，不处理了
            for node in result:
                # if debug_level.find('comment') > 0: print("type is " + str(type(node.parent)) + ' ' + str(type(node)))
                # if debug_level.find("debug") > 0: print node.name, node.parent.name
                if node.parent.name == 'a' or isinstance(node, Comment) \
                        or isinstance(node.parent, Comment):
                    continue
                if len(node) > 30:
                    node = select_line_part(re.sub("\n", ".", node), 
                                            key_words)
                    # if debug_level.find("debug") > 0: print(" extract from line %s " % node)
                    tags = self.extract_from_line(node, tags, tag_text)
                    # if debug_level.find("debug") > 0: print(" extract from line %d  ge " % len(tags))
                    return tags, tag_text
                tags = self.extract_from_sibling(node, tags, tag_text, words)
                # if debug_level.find("debug") > 0: print("extract from sibling %d  ge " % len(tags), tags)
                return tags, tag_text
        return tags, tag_text

    def get_research_interests(self, soup, tags, website, tag_text):
        """
        
        """
        # 先用 完整的 research interest 找
        result = soup.find_all(string=re.compile("research\s+interest", re.I))
        # if debug_level.find('interests') > 0: print("re in has %d at %s" % (len(result), website))
        # logger.info("re in has %d at %s" % (len(result), website))
        tags, tag_text = self.find_paragraph_interests(result, tags, tag_text, "interest")
        if result and tags:
            return tags, tag_text

        # 再用 current research|interests 找
        words = "(%s)" % '|'.join(e for e in self.key_words[u'其他可能的研究兴趣短语'])
        result = soup.find_all(string=re.compile(words, re.I))
        # if debug_level.find('interests') > 0: print("other has %d at %s" % (len(result), website))
        # logger.info("other has %d at %s" % (len(result), website))
        tags, tag_text = self.find_paragraph_interests(result, tags, tag_text, u'其他可能的研究兴趣短语')
        # if debug_level.find('interests') > 0: print("get tags %s" % str(tags))
        if result and tags:
            return tags, tag_text

        # 再用 research or interests等标语 to find then filter it by some rules
        words = "(%s)" % '|'.join(e for e in self.key_words[u'其他可能的研究兴趣单词'])
        result = soup.find_all(string=re.compile(words, re.I))
        # if debug_level.find('interests') > 0: print("single has %d at %s" % (len(result), website))
        nodes = filter_research_interests(result)
        # if debug_level.find("debug") > 0: print("only one has %d at %s " % (len(nodes),  website))

        if len(nodes) == 1:
            if len(nodes[0]) > 35:
                # print "by line",
                research_tags = self.extract_from_line(nodes[0], tags, tag_text)
                if research_tags:
                    return research_tags, tag_text

            # if debug_level.find("debug") > 0: print(' ' * 2 * debug_level + "need to sibling")
            tags = self.extract_from_sibling(nodes[0], tags, tag_text, u'其他可能的研究兴趣单词')
            return tags, tag_text
        elif len(nodes) < 5:
            if website == '':
                for node in nodes:
                    if node.parent.name == "a" or re.search('\d', node):
                        continue
                    if isinstance(node, Comment) or isinstance(node.parent, Comment):
                        continue
                    if len(node) > 35:
                        # if debug_level.find("debug") > 0: print (" from the line " + node)
                        tags = self.extract_from_line(node, tags, tag_text)
                        continue
                    tags = self.extract_from_sibling(node, tags, tag_text, u'其他可能的研究兴趣单词')
            elif website:
                for node in nodes:
                    if node.parent.name != "a":
                        continue
                    research_link = urlparse.urljoin(website, node.parent.get("href"))
                    if research_link == website:
                        continue
                    re_content, re_soup = self.open_page(research_link)
                    tags, tag_text = self.get_research_interests(re_soup, tags, research_link, tag_text)

        if not len(tags):
            return [u"I'm so stupid to found it,我太蠢了找不到"], []
        return tags, tag_text

    def extract_name_from_node(self, faculty_ele, person, flag):
        # 搞名字
        faculty_link = faculty_ele.get("href")
        name = ''
        for e in faculty_ele.get_text("#", strip=True).split("#"):
            if e:
                name = e
                break
        # if debug_level.find('name') > 0: print(' name is ' + name)
        if flag:
            person['source_name'] = {u'目录页链接名字': name,
                                     u'链接URL': faculty_link}

        if not name:
            name = ''

        # if debug_level.find('name') > 0: print(' name is ' + name)
        if name:
            name = re.sub("(Ph\.?D|M\.?S)", "", name, re.I)
            name = re.sub("(\([^)]*\))", "", name, re.I)
            name = ' '.join(e.capitalize() for e in re.findall('(\w+)', name)
                            if not contain_keys(e, self.key_words[u'人名不可能是']+
                                                [self.university_name]))

        if not name:
            # if debug_level.find('name') > 0: print(' link is ' + faculty_link)
            name = faculty_link.split('/')[-1] if faculty_link.strip()[-1] != '/' else faculty_link.split('/')[-2]

        # if debug_level.find('name') > 0: print(' name is ' + name)
        if name:
            name = re.sub("(Ph\.?D|M\.?S)", "", name, re.I)
            name = re.sub("(\([^)]*\))", "", name, re.I)
            name = ' '.join(e.capitalize() for e in re.findall('(\w+)', name)
                            if not contain_keys(e, self.key_words[u'人名不可能是']+
                                                [self.university_name]))
            # if debug_level.find('name') > 0: print(' name is ' + name)
        if not name:
            name = faculty_link
            name = re.sub("(Ph\.?D|M\.?S)", "", name, re.I)
            name = re.sub("([0-9]+)", "", name, re.I)
            name = ' '.join(e.capitalize() for e in re.findall('(\w+)', name)
                            if not contain_keys(e, self.key_words[u'人名不可能是']+
                                                [self.university_name]))

        if name:
            person['name'] = name

        return person

    def query_position_status(self, faculty_link, faculty_page):
        content, soup = self.open_page(faculty_link, True)
        if content.startswith('Error to load'):
            # print "Error!!!!!! at the link", faculty_link
            return "Error %s " % content
        position, term, position_text = self.get_open_position(soup)
        if not position:
            page_c, page_soup = self.open_page(faculty_page, True)
            if page_c.startswith('Error to load'):
                return "Error %s " % page_c
            position, term, position_text = self.get_open_position(page_soup)
        return position

    def dive_into_page(self, faculty_ele, flag):
        faculty_link = faculty_ele.get("href")
        person = {'name': '', 'link': faculty_link, 'tags': None,
                  'position': False, 'term': '', 'website': ''}

        person = self.extract_name_from_node(faculty_ele, person, flag)
        # if debug_level.find("debug") > 0: print(' name is ' + person['name'])

        if contain_keys(faculty_link.split('/')[-1], self.key_words[u'文件而不是网页']):
            return person

        # 打开教员索引主页
        content, soup = self.open_page(faculty_link)
        if content.startswith('Error to load'):
            # print "Error!!!!!! at the link", faculty_link
            return person

        tags, tag_text = self.get_research_interests(soup, [], "", [])
        # if debug_level.find('tags') > 0: print("find tags %d ge " % len(tags) + str(tags))
        if tags:
            person[u'研究方向部分原文'] = tag_text

        position, term, position_text = self.get_open_position(soup)
        person['position'] = position
        person['term'] = term
        if flag and position_text:
            person[u'招生意向说明部分原文'] = position_text

        anchors = find_all_anchor(soup)
        faculty_page, mail, page_name = self.get_personal_website(anchors,
                                                                  faculty_link, person['name'])
        if flag:
            person['source_website'] = {u'个人主页名字': page_name,
                                        u'个人主页链接URL': faculty_page}

        if faculty_page:
            # if debug_level.find("website") > 0: print 'website page url: ',faculty_page
            faculty_page = urlparse.urljoin(faculty_link, faculty_page)
            # if debug_level.find("website") > 0: print 'website page url: ',faculty_page
            page_c, page_soup = self.open_page(faculty_page)
            if page_c.startswith('Error to load'):
                faculty_page += u"#哟！打不开"
                # print "Error!!!!!! at the page", faculty_page
            else:
                tags, tag_text = self.get_research_interests(page_soup, tags,
                                                             faculty_page, tag_text)
                if tags:
                    person[u'研究方向部分原文'] = tag_text

                # if debug_level.find("website") > 0: print 'website page open position',faculty_page
                position, term, position_text = self.get_open_position(page_soup)
                if position:
                    person['position'] = position
                    if flag and position_text:
                        person[u'招生意向说明部分原文'] = position_text
                if term:
                    person['term'] = term

        if len(tags) > 1 and tags[0].startswith("I'm so stupid to"):
            tags = tags[1:]
        if len(tags) == 1 and tags[0].startswith("I'm so stupid to"):
            tags = []

        person['website'] = faculty_page
        person['mail'] = mail
        person['tags'] = tags
        if not person['name'] and mail:
            if mail.startswith("mailto:"):
                person['name'] = mail[mail.find(':') + 1: mail.find('@')].capitalize()
            elif '@' in mail:
                person['name'] = mail[: mail.find('@')].capitalize()

        return person


if __name__ == "__main__":
    # url = "http://cs.mines.edu/CS-Faculty"

    urls = ['http://cs.mines.edu/CS-Faculty',
            'http://science.iit.edu/computer-science/people/faculty',
            'http://cms.bsu.edu/academics/collegesanddepartments/computerscience/facultyandstaff/faculty',
            'http://www.memphis.edu/cs/people/index.php',
            'http://www.smu.edu/Lyle/Departments/CSE/People/Faculty',
            'https://www.csuohio.edu/engineering/eecs/faculty-staff',
            'http://computerscience.engineering.unt.edu/content/faculty',
            'https://www.odu.edu/compsci/research',
            'http://www.cs.ucf.edu/people/index.php',
            'https://www.binghamton.edu/cs/people/faculty-and-staff.html',
            'http://www.lsu.edu/eng/ece/people/index.php',
            'http://www.uwyo.edu/cosc/cosc-directory/',
            'http://www.cs.siu.edu/faculty-staff/continuing_faculty.php',
            'https://www.uml.edu/Sciences/computer-science/faculty/',
            'http://cs.gmu.edu/directory/by-category/faculty/',
            ]
    examples = ['https://inside.mines.edu/CS-Faculty-and-Staff/TracyCamp',
                'http://science.iit.edu/people/faculty/eunice-santos',
                'http://cms.bsu.edu/academics/collegesanddepartments/computerscience/facultyandstaff/faculty/buispaul',
                'http://www.memphis.edu/cs/people/faculty_pages/william-baggett.php',
                'http://www.smu.edu/Lyle/Departments/CSE/People/Faculty/ThorntonMitchell',
                'https://www.csuohio.edu/engineering/charles-k-alexander-professor',
                'http://www.cse.unt.edu/~rakl',
                'https://www.odu.edu/directory/people/a/achernik',
                'http://www.cs.ucf.edu/~bagci',
                'https://www.binghamton.edu/cs/people/kchiu.html',
                'http://www.lsu.edu/eng/ece/people/Faculty/brown.php',
                'http://www.uwyo.edu/cosc/cosc-directory/jlc/index.html',
                'http://www.cs.siu.edu/~abosu',
                'https://www.uml.edu/Sciences/computer-science/faculty/levkowitz-haim.aspx',
                'http://cs.gmu.edu/~jallbeck/',
                ]

    url_check = {'http://cs.mines.edu/CS-Faculty': 15,
                 'http://science.iit.edu/computer-science/people/faculty': 52,
                 'http://cms.bsu.edu/academics/collegesanddepartments/computerscience/facultyandstaff/faculty': 19,
                 'http://www.memphis.edu/cs/people/index.php': 16,
                 'http://www.smu.edu/Lyle/Departments/CSE/People/Faculty': 17,
                 'https://www.csuohio.edu/engineering/eecs/faculty-staff': 32,
                 'http://computerscience.engineering.unt.edu/content/faculty': 34,
                 'https://www.odu.edu/compsci/research': 15,
                 'http://www.cs.ucf.edu/people/index.php': 54,
                 'https://www.binghamton.edu/cs/people/faculty-and-staff.html': 33,
                 'http://www.lsu.edu/eng/ece/people/index.php': 34,
                 'http://www.uwyo.edu/cosc/cosc-directory/': 11,
                 'http://www.cs.siu.edu/faculty-staff/continuing_faculty.php': 10,
                 'https://www.uml.edu/Sciences/computer-science/faculty/': 18,
                 'http://cs.gmu.edu/directory/by-category/faculty/': 43

                 }
    import cProfile

    for url in urls[14:15]:

        crawler = ResearchCrawler(url, examples[urls.index(url)])
        cProfile.run("crawler.crawl_from_directory(url, examples[urls.index(url)])", "prof.log")

        # i = 1
        # directory_url = urls[i]
        # example = examples[i]
        # self.university_name = re.search('(\w+).edu', directory_url).group(1)
        # soup, anchors = find_all_anchor(self.open_page(directory_url))
        # print directory_url, len(anchors)
        # count, links = find_faculty_list(anchors, directory_url, example)
        # print count, url_check[directory_url]
        # assert count >= url_check[directory_url]

        # soup, anchors = find_all_faculty_tag(self.open_page(self.url))
        # for d in anchors:
        #     try:
        #         print d.parent.name, d.parent.find_all('a')
        #     except:
        #         pass
