# coding: utf-8

import os
import re
import json

from crawler import ResearchCrawler

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
                'https://www.uml.edu/Sciences/computer-science/faculty/levkowitz-haim.aspx'
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

                 }
    import cProfile

    for url in urls[8:9]:
        print url

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
