var rankBy = 'Q.S.';
var filterList = null;
var collegeList = null;
var major_map = null;
var detail_major = null;

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

function fillResearchInformation(item, showSchool) {
    var temp, tr = $("<tr></tr>"),
        select = $("<select></select>"),
        option_tmp = "<option>{0}</option>";

    for (var j in item.tags) {
        select.append($(option_tmp.format(item.tags[j])));
    }
    temp = item.name.trim();
    if (temp.length > 16) {
        var parts = temp.split(/\W/g);
        temp = '';
        for (var i in parts) {
            if (i == 0 || i == parts.length-1) {
                if (parts[i].length > 10)
                    parts[i] = parts[i].substring(0, 5);
            } else if (parts[i].length > 4) {
                parts[i] = parts[i].substring(0, 2) + '.';
            }
            temp += parts[i] + ' ';
        }
    }
    tr.append($("<td>{0}</td>".format(temp)));
    if (showSchool) {
        temp = item.school;
        if (temp && temp.indexOf("(") > -1)
            temp = temp.substring(temp.indexOf('(')+1, temp.indexOf(')'));
        tr.append($("<td>{0}</td>".format(temp)));
        if (item.major in detail_major)
            temp = detail_major[item.major];
        else
            temp = item.major;
        if (screen.width < 767) {
            var index = temp.indexOf('(');
            if (index >= 0) {
                temp = temp.substring(temp.indexOf('(')+1, temp.indexOf(')'));
            }
        }
        tr.append($("<td>{0}</td>".format(temp)));
    }
    tr.append($("<td><a href='{0}' target='_blank'>主页</a></td>".format(item.link)));
    if (item.website)
        tr.append($("<td><a href='{0}' target='_blank'>个人页</a></td>".format(item.website)));
    else {
        tr.append($("<td></td>"));
        
    }
    var td = $("<td></td>").append(select)
    tr.append(td);
    temp = item.position;
    var btn = $('<a class="btn btn-success"></a>');
    btn.attr("onclick", "togglePosition(this, '{0}')");
    if (temp) {
        temp = "在招";
        btn.html("招满");
    }
    else {
        temp = "";
        btn.html("来招");
    }

    tr.append($("<td>{0}</td>".format(temp)));
    tr.append($("<td>{0}</td>".format(item.term || "")));
    // tr.append($("<td></td>").append(btn));
    return tr;
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

    var degree_map = {'1': '本科', '2': '硕士', '3': '博士'};

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
    var params = getSharpParam();
    if (params)
        params['sortBy'] = col;
    else {
        params = {'sortBy': col};
    }
    var temp = "{0}#{1}".format(document.URL.split("#")[0], jsonToSharpParam(params));
    window.location.href = temp;
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
    var params = getSharpParam();
    if (params)
        params['filterBy'+col] = v;
    else {
        params = {};
        params['filterBy'+col] = v;
    }
    
    var temp = "{0}#{1}".format(document.URL.split("#")[0], jsonToSharpParam(params));
    window.location.href = temp;
    pageIt(newList, "college", 0);
}

function filterByName(obj, type) {
    var name = $(obj).val();
    if (!rankBy) rankBy = "Q.S.";
    var newList = filterCollege(filterList, 'name', name);
    var params = getSharpParam();
    if (params)
        params['filterByName'] = name;
    else {
        params = {'filterByName': name};
    }
    var temp = "{0}#{1}".format(document.URL.split("#")[0], jsonToSharpParam(params));
    window.location.href = temp;
    
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

    var params = getSharpParam() || {};
    if (degree != "") {
        params["学历"] = degree;
    }
    if (major != 0) {
        params["专业"] = major;
    }
    if (evalue != "") {
        params["成绩单认证"] = degree;
    }
    if (rl != "0") {
        params["推荐信"] = degree;
    }

    var temp = "{0}#{1}".format(document.URL.split("#")[0], jsonToSharpParam(params));
    window.location.href = temp;

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

function showCollegeKeyWords(data) {
    
    var showTags = ['招生录取URL不可能包含', '招生录取URL可能包含', 
                    '院系教员URL不可能包含', '院系教员URL可能包含'];
    $("#keyWords").html("<p>爬虫抽取信息关键词(以逗号,隔开， 正则表达式匹配):</p>");
    
    showKeyWordsList(data, showTags);
}

function extract_uniq_part(parts, id) {
    var uniq_parts = [];
    for (var i in parts) {
        var flag = false, re = new RegExp("\\b" + parts[i] + "\\b","i");
        for (var j in filterList.list) {
            if (j == id)
                continue;
            if (filterList.list[j].match(re)) {
                console.log(parts[i] + ' contains in ' + filterList.list[j]);
                flag = true;
                break;
            }
        }
        if (!flag) {
            console.log(parts[i] + ' is uniq');
            uniq_parts.push(parts[i]);
        }
    }
    return uniq_parts;
}

function delete_btn_update(obj) {
    var ele = $(obj).parent().parent(), url = $($(ele.children("td")[2]).children("a")[0]).html(),
        id = $(ele.children("td")[0]).html();
    console.log(url);
    var parts = url.split(/\W/g);
    console.log(parts);

    var uniq_parts = extract_uniq_part(parts, id);
    var input = $($("#keyWords").children("div").children("input")[0]),
        words = input.val();
    for (var i in uniq_parts) {
        words = uniq_parts[i] + ',' + words;
    }
    input.val(words);
    ele.remove();
}

function showCollegeCrawlerResult(data) {
    var showTags, list = data.list, table = $("<table class='table table-striped'></table>");
    showCollegeKeyWords(data);


    for (var i in list) {
        var tr = $("<tr></tr>"), td = $("<td></td>"), toggle = null;
        var url = list[i].split("|")[0], name = list[i].split("|")[1];
        var btn = $("<a class='btn btn-danger'>删除该链接</a>");
        btn.attr("onclick", "delete_btn_update(this)");
        td.append("<span>链接URL为：</span>");
        td.append('<a href="{0}" target="_blank">{1}</a>'.format(url, url));
        tr.append("<td>{0}</td>".format(i));
        tr.append("<td>链接名字显示为：{0}</td>".format(name));
        tr.append(td);
        tr.append($("<td></td>").append(btn));
        table.append(tr);
        if (toggle) {
            table.append(toggle);
        }
    }
    $("#crawlResult").append(table);
}

function submitRedirect(obj, type, url) {
    var options = {
        dataType: 'json',
        success: function (data) {
            $("#loadingDiv").remove();
            if (data.error) {
                alert(data.error);
                document.getElementById("vericode")
                    .setAttribute('src','/verifycode?random='+Math.random());
                $("#loadingDiv").remove();
                return;
            }
            console.log(data.info);
            if (type.indexOf("college") > -1) {
                $("#loadingDiv").remove();
                filterList = data;
                showCollegeCrawlerResult(data);
                document.getElementById("vericode")
                    .setAttribute('src','/verifycode?random='+Math.random());
                return;
            }
            if (type.indexOf("crawler") > -1) {
                $("#loadingDiv").remove();
                if (type.split("-")[1] != '3') {
                    filterList = data;
                    showCrawlerResult(data, type.split("-")[1]);
                    document.getElementById("vericode")
                        .setAttribute('src','/verifycode?random='+Math.random());
                    return;
                }
                window.location.href = "{0}.html".format(url);
                return;
            }

            $("#loadingDiv").remove();
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
                $("#loadingDiv").remove();
            }
        },  
        //请求出错的处理  
        error: function(){  
            $("#loadingDiv").remove();
            alert("出错");  
            document.getElementById("vericode")
                .setAttribute('src','/verifycode?random='+Math.random());
            $("#loadingDiv").remove();
        }
    };
    if ($("#approveIt").val() == 0 || type.indexOf("crawler") > -1) {
        $("#crawlResult").html("");
        // timerId = window.setInterval(getProcess, 2000);  
        
        // var loadingDiv = createLoadingDiv('总共{0}位可能学者，正在爬取第{0}位')
        var loadingDiv = createLoadingDiv('正在处理中，估计需要几分钟~~~没开发进度监视');
        
        // 呈现loading效果
        $(".container-fluid").append(loadingDiv);
        /* setTimeout(function() {
            if (typeof($("#loadingDiv")) != "undefined")
                $("#loadingDiv").remove();
        }, 18000);*/
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
        url : "/oversea/collegeList",
        contentType: 'application/json',
        dataType: "json",
        success : function (result){
            result.sort(compare('name', true, false));
            collegeList = result;
            var param = unescape(document.URL.split('/')[5]);
            if (param == "new") {
                var data = collegeList;
                for (var i in data) {
                    var item = data[i].name, 
                        option = $('<option value="{0}">{1}</option>'.format(item, item));

                    if (param === item) {
                        option.attr("selected", true); 
                    }
                    $('#collegeName').append(option);
                }
            }
        }
    });

    $("#directoryUrl").on("paste", function(){
        setTimeout(function() {
            var url = $("#directoryUrl").val();
            var parts = url.split("/")[2].split(".");
            for (var i in parts) {
                var p = parts[i], flag = false;
                if (p == 'edu' || p == 'www')
                    continue;
                var re = new RegExp("\\b" + p + ".edu\\b","i");
                for (var j in collegeList) {
                    var univ = collegeList[j];
                    if ('info' in univ && 'webpage' in univ.info) {
                        if (univ.info.webpage.match(re)) {
                            console.log(p+ ' contains in ' + univ.name);
                            $("#collegeName").val(univ.name);
                            flag = true;
                            break;
                        }
                    }
                }
                if (flag)
                    break;
            }
        });
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
                if (item.toLowerCase().indexOf(text) >= 0) {
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

function sortMajorIndex(a, b) {
    var temp = 0;
    if (a == "") a = temp;
    if (b == "") b = temp;
    if (typeof(a) == "string") {
        temp = parseInt(a.split("-")[0]);
        if (a.split("-").length == 2) {
            temp += parseInt(a.split("-")[1]) * 0.1;
        }
        a = temp;
    }
    if (typeof(b) == "string") {
        temp = parseInt(b.split("-")[0]);
        if (b.split("-").length == 2) {
            temp += parseInt(b.split("-")[1]) * 0.1;
        }
        b = temp;
    }
    return a-b;
}

function getProperty(type, callback) {
    var url = '/qnfile/zcollege-college.txt';
    $.ajax({
        method: "get",
        url : url,
        contentType: 'application/json',
        dataType: "json",
        success : function (data) {
            var t = '<option value="{0}">{1}</option>';
            for (var i in data.nation) {
                var nation = data.nation[i];
                $("#degreeName").append($(t.format(nation, nation))); 
            }
            for (var i in data['sort']) {
                var rank = data['sort'][i];
                $("#sortName").append($(t.format(rank, rank))); 
            }
            detail_major = data["detail_major"];
            if (type != "") {
                major_map = data[type];

                var keys = [];
                for (var i in major_map) {
                    keys.push(i);
                }
                keys.sort(sortMajorIndex);
                for (var i in keys) {
                    var option = t.format(keys[i], major_map[keys[i]]);
                    $("#majorName").append(option);
                }
            }
            callback();
        }
    });
}
