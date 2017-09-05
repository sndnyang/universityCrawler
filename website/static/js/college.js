var rankBy = 'Q.S.';
var filterList = null;
var collegeList = null;

function filterCollege(l, col, t) {
    var data = [], prefix = t+'-';
    for (var i in l) {
        if (col == 'deadline' && (('fall' in l[i] && l[i].fall)
                    || ('spring' in l[i] && l[i].spring))) {
            // 截止日期过滤
            data.push(l[i]); 
            continue;
        }
        if (col == 'name') {
            if (!t) {
                data.push(l[i]);
                continue;
            }
            t = t.toLowerCase();
            if (l[i][col].toLowerCase().indexOf(t) > -1) {
                data.push(l[i]);
                continue;
            }
            if ('info' in l[i] && l[i].info) {
                if ('cn' in l[i].info && l[i].info.cn
                        && l[i].info.cn.indexOf(t) > -1) {
                    data.push(l[i]);
                    continue;
                }
                if ('abbr' in l[i].info && l[i].info.abbr
                        && l[i].info.abbr.toLowerCase().indexOf(t) > -1) {
                    data.push(l[i]);
                    continue;
                }

            }
        }
        
        if (t) {              
            if (col !== 'deadline' && col in l[i]) {
                if (l[i][col] == t || 
                      l[i][col].toString().substr(0, prefix.length) == prefix)
                   data.push(l[i]);
                if (col === 'rl' && t == -1 && l[i][col] == 0) {
                    data.push(l[i]);
                }
            }
            else if (l[i].info && col in l[i].info && l[i].info[col].indexOf(t) > -1) {
                    data.push(l[i]);
            }
        } 
        else {
            data.push(l[i]);
        }
    }
    return data;
}

function appendButton(item, tr, n, url) {
    if (n) {
        var pass = $('<td><a href="javascript:void(0);" onclick="approve(\'{0}\', \'{1}\',0)" class="btn btn-success">通过</a></td>'.format(url, item.id));
        var rej = $('<td><a href="javascript:void(0);" onclick="approve(\'{0}\', \'{1}\',1)" class="btn btn-danger">删除</a></td>'.format(url, item.id));
        tr.append(pass);
        tr.append(rej);
    } else {
        var edit_url = url + "Form/";
           
        if (item.id) {
            edit_url += item.id;
        } else {
            edit_url += item.name;
        }
        edit = $('<td><a href="{0}" target="_blank" class="btn btn-success">编辑</a></td>'.format(edit_url));
        tr.append(edit);
    }
}

function fillName(name) {
    var temp;
    if (screen.width < 767) {
        var index = name.indexOf('(');
        if (index < 0) {
            temp = name;
        } else {
            temp = name;
            temp = temp.substring(temp.indexOf('(')+1, temp.indexOf(')'));
        }
    } else {
        temp = name;
    }
    return $('<td>{0}</td>'.format(temp || ''));
}


function fillCollegeInformation(item, i, n, backend) {
    var name, temp, expand, tr = $('<tr></tr>');

    name = fillName(item.name);

    temp = '';
    if (item.info && (item.info['城市'] || item.info['city']))
        temp = item.info['城市'] || item.info['city'];
    nation = $('<td>{0}</td>'.format(temp));

    temp = '';
    if (item.info && item.info[rankBy])
        temp = item.info[rankBy].split('.')[0];

    qsrank = $('<td>{0}</td>'.format(temp));

    expand = $('<td><a data-toggle="collapse" aria-expanded="false" class="False collapsed btn btn-success" href="#collapse{0}" aria-controls="collapse{1}">展开</a></td>'.format(i, i));
    tr.append(name);
    tr.append(nation);
    tr.append(qsrank);
    tr.append(expand);

    appendButton(item, tr, n, backend);

    return tr;
}

function fillInformation(item, i, n, backend) {
    var name, degree, major, gpa, tuition, deadline, other,
        temp, expand, edit, tr = $('<tr></tr>');
    name = fillName(item.name);

    var degree_map = {'1': '本科', '2': '硕士', '3': '博士'},
        major_map = {"1-1": "计算机科学(CS)",
                      "1-2": "计算机工程(CE)", 
                      "1-3": "软件工程(SE)", 
                      "1-4": "信息技术(IT)",
                      "2": "航空航天",
                      "3": "Chemical/Petroleum",
                      "4": "Civil/Construction/Structural",
                      "5": "Electrical/Electronics/Telecomm",
                      "6": "Industrial/Operations",
                      "7": "Mechanical/Automobile",
                      "8": "Biomedical/Biotechnical",
                      "9": "Management Information System (MIS)",
                      "10": "Biological/Agricultural",
                      "11": "Engineering Management (MEM)",
                      "12": "Environmental/Mining",
                      "13": "Financial Engineering",
                      "14": "Material Science and Engineering",
                      "15": "Analytics",
                      "16": "Nano/Nuclear/Power",
                      "17": "Healthcare",
                      "18": "Nursing",
                      "19": "Dental",
                      "20": "Veterinary Science",
                      "21": "Pharmacy",
                      "22": "Commerce/Finance/Actuarial",
                      "23": "Government/Administrative",
                      "24": "Pure Sciences",
                      "25": "Arts/Media",
                      "26": "Education/Languages/Counselling",
                      "27": "Humanities/Journalism",
                      "28": "Management",
                      "29": "Finance",
                      "30": "Marketing",
                      "31": "Human Resources",
                      "32": "International Management",
                      "33": "General Law",
                      "34": "International Law",
                      "35": "Architecture"}

    temp = degree_map[item.degree] || '';
    if (screen.width < 767) {
        temp = temp.substr(0,1);
    }
    degree = $('<td>{0}</td>'.format(temp));

    temp = major_map[item.major] || '';
    if (screen.width < 767) {
        var index = temp.indexOf('(');
        if (index >= 0) {
            temp = temp.substring(temp.indexOf('(')+1, temp.indexOf(')'));
        }
    }
    major = $('<td>{0}</td>'.format(temp));
    program_name = $('<td>{0}</td>'.format(item.program_name || ''));
    gpa = $('<td>{0}</td>'.format(item.gpa || ''));
    tuition = $('<td>{0}</td>'.format(item.tuition || ''));

    var md = getmd(), tmp_dl = item.fall || '';
    if (tmp_dl) tmp_dl += '(秋)';
    if ('fall' in item && item.fall > md)
        tmp_dl = item.fall + '(秋)';
    else if ('spring' in item && item.spring > md)
        tmp_dl = item.spring + '(春)';

    deadline = $('<td>{0}</td>'.format(tmp_dl));
    expand = $('<td><a data-toggle="collapse" aria-expanded="false" class="False collapsed btn btn-success" href="#collapse{0}" aria-controls="collapse{1}">展开</a></td>'.format(i, i));
    tr.append(name);
    tr.append(degree);
    tr.append(major);
    tr.append(gpa);
    tr.append(tuition);
    tr.append(deadline);
    tr.append(expand);

    appendButton(item, tr, n, backend);
    return tr;
}

function removeExtra(obj) {
    $(obj).parent().remove();
    return false;
}

function addOneInfo(key, item, i) {
    if (i === -1) {
        i = $(".info-item").length;
    }
    var div = $('<div class="info-item"></div>');
    var label = $('<label for="label{0}">信息名称: </label>'.format(i));
    var input = $('<input type="text" name="label{0}" value="{1}">'.format(i, key));
    var label2 = $('<label for="input{0}">内容: </label>'.format(i));
    var input2 = $('<input type="text" name="input{0}" value="{1}">'.format(i, item));
    var del_btn = $('<a href="javascript:void(0);" onclick="removeExtra(this)">删除</a>');
    del_btn.attr("class", "btn btn-danger");
    
    div.append(label);
    div.append(input);
    div.append(label2);
    div.append(input2);
    div.append(del_btn);
    $(".info").append(div);
}

function approve(type, id, n) {
    $.ajax({
        method: "post",
        url : '/oversea/' + type + 'Data/approve',
        contentType: 'application/json',
        dataType: "json",
        data: JSON.stringify({'id': id, 'type': n}),
        success : function (result){
            var data = result;
            if (data.error) {
                alert(data.error);
                return;
            }
            alert('success');
        }
    });
}

function fillItemInfo(toggle, item) {
    for (var e in item) {
        if (e.substring(0, 5) === 'input') continue;
        else if (e.substring(0, 5) === 'label') {
            var j = e.substring(5, e.length);
            var temp = item['input' + j];
            if (j == "0") {
                if (temp == 'no' || temp == '')
                    continue;
                if (temp == 'yes')
                    temp = '需要';
            }
            toggle.append($('<p>{0} : {1}</p>'.format(item['label' + j], 
                        temp)));
        }
        else {
            var key = e, value = item[e];
            if (key === 'Q.S.') value = value.split('.')[0];
            if (key === 'cn') key = '中文名';
            if (key === 'loc') key = '位置';
            if (key === 'webpage') {
                key = '主页';
                if (value.substring(0, 4) != 'http') 
                    value = '//'+value;
                value = '<a href={0} target=_blank>链接</a>'.format(value);
            }
            toggle.append($('<p>{0} : {1}</p>'.format(key, value)));
        }
    }
    return toggle;
}

function fillExtraInfo(item, i) {
    var toggle = $('<div class="panel-collapse collapse" data-expanded="false" role="tabpanel" id="collapse{0}" aria-labelledby="heading{1}" aria-expanded="false" style="height: 0px;"></div>'.format(i, i));
    var toefl, ielts, gre, evalue, rl, finance, page, program_name,
        gpa_p, gre_p, eng_p, deadline_p, docum_p, int_docum_p;

    program_name = item.program_name || '';
    rl = item.rl || '';
    gre = item.gre || '';
    toefl = item.toefl || '';
    ielts = item.ielts || '';
    evalue = item.evalue || '';
    finance = item.finance || '';

    var other = $('<p></p>'), page = $('<p></p>'),
        url = '<p><a href="{0}" target="_blank">{1}</a></p>';
    page = fillItemInfo(page, item.info);

    if (item.site_url)
        page.append($(url.format(item.site_url, '官方主页')));
    if (item.gpa_url)
        page.append($(url.format(item.gpa_url, 'GPA网页')));
    if (item.gre_url)
        page.append($(url.format(item.gre_url, 'GRE网页')));
    if (item.eng_url)
        page.append($(url.format(item.eng_url, '英文要求网页')));
    if (item.tuition_url)
        page.append($(url.format(item.tuition_url, '学费网页')));
    if (item.deadline_url)
        page.append($(url.format(item.deadline_url, '截止日期网页')));
    if (item.docum_url)
        page.append($(url.format(item.docum_url, '申请材料网页')));
    if (item.int_docum_url)
        page.append($(url.format(item.int_docum_url, '国际生材料网页')));

    if (item.program_name) {
        toggle.html("<p>项目名: {0}</p>".format(item.program_name));
        toggle.append('<p>托福：{0},  雅思：{1},  GRE: {2}</p>'.format(toefl, ielts, gre));
    } else {
        toggle.html('<p>托福：{0},  雅思：{1},  GRE: {2}</p>'.format(toefl, ielts, gre));
    }
    
    if (evalue == 'no') evalue = '不需要';
    else if (evalue == 'yes') evalue = '需要';
    if (rl == 0 || rl == -1) rl = '可免';
    else rl += '封';
    if (finance == 'no') finance = '不需要';
    else if (finance == 'yes') finance = '需要';
    other.append('成绩单认证：{0},  推荐信：{1},  存款证明：{2}'.format(evalue, rl, finance));
    toggle.append(other);
    toggle.append(page);
    return toggle;
}

function fillCollegeExtraInfo(item, i) {
    if (!item) return '';

    var toggle = $('<div class="panel-collapse collapse" data-expanded="false" role="tabpanel" id="collapse{0}" aria-labelledby="heading{1}" aria-expanded="false" style="height: 0px;"></div>'.format(i, i));
    toggle = fillItemInfo(toggle, item)

    return toggle;
}

function pageIt(data, name, n) {
    $("#collegeList").html("");
    $('#pagination-container').pagination({
        dataSource: data,
        callback: function(data, pagination) {
            $("#collegeList").html("");
            var items = pageTemplate(data, name, n);
            for (var i in items) {
                $("#collegeList").append(items[i]);
            }
        },
    });
}

function compare(property, isstring, ininfo) {
    return function (a, b) {
        var va = ininfo? a.info[property]:a[property], 
            vb = ininfo? b.info[property]:b[property];
        if (property === "deadline") {
            return sortDeadline(a, b);
        } else if(isstring || property === 'name'){
            return va > vb ? 1:-1;
        } else {
            va = parseFloat(va) || 1000000, vb = parseFloat(vb) || 1000000;
            return va > vb ? 1:-1;
        }
    }
}

function getDataList(name, n) {
    if (n == 0) n = ''; 
    $.ajax({
        method: "get",
        url : name + "List" + n,
        contentType: 'application/json',
        dataType: "json",
        success : function (result){
            // var data = result.sort(sortName);
            var data = result.sort(compare('name', true, false));
            if (name === "college")
                data = data.sort(compare('Q.S.', false, true));
            // collegeList = result;
            filterList = result;
            pageIt(data, name, n);
        }
    });   
}

function validate_deadline(obj) {
    var s = $(obj).val(), ext,
        date = s.substr(0, 5);
    if (!/(0[1-9]|1[0-2]).(0[1-9]|3[01]|[12][0-9])/.test(date)) {
        alert('截止日期格式不对 ' + s);
        $(obj).focus();
    }
    if (s.length > 5 && (s.length < 12 || s[5] != '(' || 
         !/(0[1-9]|1[0-2]).(0[1-9]|3[01]|[12][0-9])/.test(s.substr(5, 7)))) {
        alert('申奖截止日期格式不对 ' + s.substring(5, s.length));
        $(obj).focus();
    }
}

function getmd() {
    var date = new Date(), month = date.getMonth(), day = date.getDate(),
        md;
    if (month < 10) month = '0'+(month+1);
    if (day < 10) day = '0'+day;
    md = '{0}.{1}'.format(month, day);
    return md
}

function sortDeadline(a, b) {
    var md = getmd(), da = a.fall || '13.01', db = b.fall || '13.02';
    if (a.fall > md) {
        da = a.fall
    } else if (a.fall <= md && a.spring > md) {
        da = a.spring
    } else if (a.fall <= md && a.spring < md) {
        da = 14 + ' ' + a.fall;
    }
    if (b.fall > md) {
        db = b.fall
    } else if (b.fall <= md && b.spring > md) {
        db = b.spring
    } else if (b.fall <= md && b.spring <= md) {
        db = 14 + ' ' + b.fall;
    }
    return da+'' > db+'' ? 1:-1;
}

function sortCollege(name, col, ininfo) {
    var data = [], temp = filterCollege(filterMajorByAll(), col, 0);
    if (col == "deadline") {
        col = "fall";
    }
    for (var i in temp) {
        if ((col in temp[i] && temp[i][col]) 
            || ('info' in temp[i] && temp[i].info && col in temp[i].info)) {
            data.push(temp[i]);
        }
    }
    var ranks = $("#sortName option").map(function() {return this.value;}).get();
    if (ranks.indexOf(col) > -1) {
        rankBy = col;
        $("#rankName").html(rankBy.replace(/\./g, '') + '排名');
    }
    if (col == 'fall') col = 'deadline';
    data.sort(compare(col, false, ininfo));
    pageIt(data, name, 0);
}

function pageTemplate(data, name, n) {
    var list = [];
    $.each(data, function (i, item) {
        if (name.indexOf('major') > -1 && !('degree' in item)) {
            return;
        }
        var row = null, toggle = null;
        if (name.indexOf('college') > -1) {
            row = fillCollegeInformation(item, i, n, name);
            toggle = fillCollegeExtraInfo(item.info, i);
        }
        else if (name.indexOf('major') > -1) {
            row = fillInformation(item, i, n, name);
            toggle = fillExtraInfo(item, i);
        } else if (name.indexOf('research') > -1) {
            row = fillResearchInformation(item, true);
        }
        list.push(row);
        if (toggle) {
            list.push(toggle);
        }
    });
    return list;
}

function filterBy(v, t, col) {
    var newList = filterCollege(filterList, col, v);
    pageIt(newList, "college", 0);
}

function filterByName(obj, type) {
    var name = $(obj).val();
    if (!rankBy) rankBy = "Q.S.";
    var newList = filterCollege(filterList, 'name', name);
    if (type == "research") {
        filterProfessors('school', name);
        return;
    }

    if (!name && type == "college")
        sortCollege(type, rankBy, true);
    else
        pageIt(newList, type, 0);
}

function filterMajorByAll() {
    var degree = parseInt($("#degreeName").val()), 
        major = parseInt($("#majorName").val()),
        evalue = $("#evalueName").val(),
        transcript = $("#transcriptName").val(),
        rl = parseInt($("#rlName").val());
    var newList = filterCollege(filterCollege(
        filterCollege(
            filterCollege(
                filterCollege(filterList, 'evalue', evalue),
                 'input0', transcript),
            'degree', degree),
        'major',major),
    'rl', rl);
    return newList;
}
function filterByMajor(type) {
    if (type.indexOf("research") > -1) {
        getMajorInterestsList();
        return;
    }
    var newList = filterMajorByAll();
    pageIt(newList, "major", 0);
}

function submitRedirect(obj, type, url) {
    var options = {
        dataType: 'json',
        success: function (data) {
            console.log(data);
            $("#loadingDiv").remove();
            if (data.error) {
                alert(data.error);
                document.getElementById("vericode")
                    .setAttribute('src','/verifycode?random='+Math.random());
                return;
            }
            if (type.indexOf("crawler") > -1) {
                if (type.split("-")[1] != '3') {
                    var list = data.list;
                    filterList = data;
                    showCrawlerResult(data, type.split("-")[1]);
                    return;
                }
                window.location.href = "{0}.html".format(url);
                return;
            }

            if (type.indexOf("research") == -1 || (type.indexOf("research") > -1 && $("#approveIt").val() == 1)) {
            // if (type != "research") {
                alert('请等待审核，准备跳转...');
                window.location.href = "{0}.html".format(url);
            } else {
                $("#researchSubmit").html("点击确认");
                $("#approveIt").val(1);

                var list = data.list;
                var table = $("<table class='table table-striped'></table>");
                for (var i in list) {
                    var tr = fillResearchInformation(list[i], false);
                    table.append(tr);
                }
                $("#crawlResult").append(table);
            }
        },  
        //请求出错的处理  
        error: function(){  
            $("#loadingDiv").remove();
            alert("出错");  
        }
    };
    if ($("#approveIt").val() == 0) {
        $("#crawlResult").html("");
        // timerId = window.setInterval(getProcess, 2000);  
        
        //var loadingDiv = createLoadingDiv('总共{0}位可能学者，正在爬取第{0}位')
        var loadingDiv = createLoadingDiv('正在处理中，请稍等');
        
        // 呈现loading效果
        $(".container-fluid").append(loadingDiv);
    }

    $(obj).ajaxSubmit(options);
    return false;
}

$(document).ready(function () {
    $("#addInfo").click(function() {
        return false;
    });

    $.ajax({
        method: "get",
        url : '/static/data/college.json',
        contentType: 'application/json',
        dataType: "json",
        success : function (result){
            collegeList = result.sort(compare('name', true, false));
        }
    });

    $("#collegeName").keyup(function (event) {
        var text = $("#collegeName").val().toLowerCase();
        if (text.length == 3 || (text.length == 2 &&
                    (text[0] == 'u' || text[0] == 'c' || text[1] == 'u' || text[1] == 'c'))) {
            $("#collegeNameList").html("");
            for (var i in collegeList) {
                var item = collegeList[i].name;
                if (item.toLowerCase().indexOf("("+text) > 0) {
                    var option = $('<option value="{0}">{1}</option>'.format(item, item));
                    $("#collegeNameList").append(option);
                }
            }
        }
        if (text.length > 3 && "university".indexOf(text) == -1 && "college".indexOf(text) == -1) {
            $("#collegeNameList").html("");
            for (var i in collegeList) {
                var item = collegeList[i].name;
                if (item.toLowerCase().indexOf(text) > 0) {
                    var option = $('<option value="{0}">{1}</option>'.format(item, item));
                    $("#collegeNameList").append(option);
                }
            }
        }
        if(event.keyCode == "13" && document.URL.indexOf("research") > 0 && 
                document.URL.indexOf("form") == -1) { 
            getProfessorsList('school');
        }
    });
});

function getProperty() {
    var url = '/qnfile/zcollege-college.txt';
    $.ajax({
        method: "get",
        url : url,
        contentType: 'application/json',
        dataType: "json",
        success : function (data) {
            var t = '<option value="{0}">{1}</option>';
            for (var i in data.nation) {
                var nation = data.nation[i]
                $("#degreeName").append($(t.format(nation, nation))); 
            }
            for (var i in data['sort']) {
                var rank = data['sort'][i]
                $("#sortName").append($(t.format(rank, rank))); 
            }
        }
    });
}
