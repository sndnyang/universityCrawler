var timerId;
var keyWords = null;

function filterProfessors(col, value) {
    var newList = [];
    for (var i in filterList) {
        if (!value) {
            newList.push(filterList[i]);
            continue;
        }
        if (col in filterList[i] && filterList[i][col].toLowerCase().indexOf(value) > -1) {
            newList.push(filterList[i]);
        }
    }
    pageIt(newList, "research", 0);
}

function filterProfessorByPosition() {
    var value = $("#positionName").val();

    var newList = [];
    for (var i in filterList) {
        if (!value) {
            newList.push(filterList[i]);
            continue;
        }
        if (filterList[i].position == true) {
            if (value == "always") {
                if (filterList[i].term == "always")
                    newList.push(filterList[i]);
            } else {
                newList.push(filterList[i]);
            }
        }
    }
    pageIt(newList, "research", 0);
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
        tr.append($("<td>{0}</td>".format(item.major)));
    }
    tr.append($("<td><a href='{0}'>主页</a></td>".format(item.link)));
    if (item.website)
        tr.append($("<td><a href='{0}'>个人页</a></td>".format(item.website)));
    else {
        tr.append($("<td></td>"));
        
    }
    var td = $("<td></td>").append(select)
    tr.append(td);
    temp = item.position;
    if (temp) temp = "在招";
    else temp = "";
    tr.append($("<td>{0}</td>".format(temp)));
    tr.append($("<td>{0}</td>".format(item.term || "")));

    return tr;
}

function getProfessorsList(col) {
    var major = parseInt($("#majorName").val()),
        interest = $("#researchName").val(),
        college = $("#collegeName").val(),
        position = $("#positionName").val();
    if (col == 'position' && !position) {
        filterProfessorByPosition();
        return;
    }
    if (col == 'interest' && !interest) {
        filterProfessors('school', '');
        return;
    }
    if (major == '0') {
        alert("起码先选择专业");
        return;
    }
    if (!college) {
        college = 0;
    }
    var data = {'tag': interest, 'position': position};

    $.ajax({
        type: "post",//请求方式  
        url: "getProfessorsList/{0}/{1}".format(college, major),
        contentType: 'application/json',
        dataType: "json",
        data: JSON.stringify(data),
        success: function(data) {  
            var info = data.error;
            if (data.error) {
                alert(data.error);
                return;
            }
            filterList = data.list;
            pageIt(data.list, "research", 0);
        }
    });
}

function getProfessorByInterests() {
    var major = parseInt($("#majorName").val()),
        interests = $("#researchName").val();
    $.ajax({
        type: "get",//请求方式  
        url: "getProfessorByInterests/" + major + "/" + interests,//发送请求地址  
        timeout: 30000,//超时时间：30秒
        dataType: "json",//设置返回数据的格式
        success: function(data) {  
            var info = data.error;
            if (data.error) {
                alert(data.error);
                return;
            }
            filterList = data.list;
            pageIt(data.list, "research", 0);
        }
    });
}

function interests_modify(obj, val) {
    var data = {}, tr = $(obj).parent().parent(),
            name = $(tr.children("td")[0]).html();
    if (val == 1) {
        // 删除
        data = {'name': name, 'type': 1};
    } else {
        var zh = $($(tr.children("td")[1]).children("input")).val(),
            category = $($(tr.children("td")[2]).children("input")).val();
        data = {'name': name, 'zh': zh, 'category': category, 'type': 0};
    }
    console.log(data);
    $.ajax({
        method: "post",
        url : 'modifyInterests',
        contentType: 'application/json',
        dataType: "json",
        data: JSON.stringify(data),
        success : function (result){
            var data = result;
            if (data.error) {
                alert(data.error);
                return;
            }
            alert('success');
            if (val == 1) {
                tr.remove();
            }
        }
    });   
}
function getMajorInterestsList() {
    var major = parseInt($("#majorName").val());
    if (major == 0) {
        $("#researchName").html("<option value=''>不限</option>");
        return;
    }
    $.ajax({
        type: "get",//请求方式  
        url: "getMajorInterestsList/" + major,//发送请求地址  
        timeout: 30000,//超时时间：30秒
        dataType: "json",//设置返回数据的格式
        success: function(data) {  
            var info = data.error;
            if (data.error) {
                alert(data.error);
                return;
            }
            
            $("#researchName").html("<option value=''>不限</option>");
            if (document.URL.indexOf("interests.html") > 0) {
                var category = [];
                for (var i in data.list) {
                    if (!data.list[i].category_name) {
                        category.push(data.list[i].name);
                    }
                }
                console.log(data.list);
                for (var i in data.list) {
                    var tr = $("<tr></tr>");

                    tr.append($("<td>{0}</td>".format(data.list[i].name)));
                    tr.append($("<td><input type='text' value='{0}' class='form-control'/></td>".format(data.list[i].zh || '')));
                    tr.append($("<td><input type='text' value='{0}' class='form-control'/></td>".format(data.list[i].category_name || '')));
                    var pass = $('<td><a href="javascript:void(0);" onclick="interests_modify(this, 0)" class="btn btn-success">更新</a></td>');
                    var del = $('<td><a href="javascript:void(0);" onclick="interests_modify(this, 1)" class="btn btn-danger">删除</a></td>');
                    tr.append(pass);
                    tr.append(del);
                    $("#collegeList").append(tr);
                }
            } else {
                for (var i in data.list) {
                
                    if (data.list[i].zh) 
                        $("#researchName").append('<option value="{0}">{1}</option>'.format(
                            data.list[i].name, data.list[i].zh));
                    else
                        $("#researchName").append('<option value="{0}">{1}</option>'.format(
                            data.list[i].name, data.list[i].name));
                }

            }
        }
    })
}

function getProcess() {
    var url = $("#directoryUrl").val()
    //使用JQuery从后台获取JSON格式的数据
    $.ajax({  
        type: "post",//请求方式  
        url: "getResearchProgress",//发送请求地址  
        timeout: 30000,//超时时间：30秒
        contentType: 'application/json',
        dataType: "json",
        data: JSON.stringify({"url": url}),
        //请求成功后的回调函数 data为json格式  
        success:function(data){
            if (data.error) {
                window.clearInterval(timerId);
                alert(data.error);
                return;
            }
            var info = data.info, total = info.split(",")[0], now = info.split(',')[1];
            console.log(info);
            if (total == now) {
                window.clearInterval(timerId);
                // $("#loadingDiv").remove();
                return;
            }
            $("#loadingDiv").remove();
            var loadingDiv = createLoadingDiv('总共{0}位可能学者，正在爬取第{0}位'.format(total, now))                    
            //呈现loading效果
            $(".container-fluid").append(loadingDiv);
        },  
        //请求出错的处理  
        error: function(){  
            window.clearInterval(timerId);
            alert("请求出错");  
        }
    });  
}

function showKeyWords(data, step) {
    if (step == "1") {
        showTags = ['该URL可能是教员', '该URL不可能是教员'];
        console.log(keyWords);
    }
    else if (step == "2") {
        showTags = ['该词不可能是名字', '该名字可能是教授个人主页',
                '文件而不是网页', '有些方向的前缀', '其他可能的研究兴趣标语',
                    '这个标题不是研究兴趣', '一段研究兴趣的起始词', '研究兴趣需要替换的词',
                    '该句开始不再是研究兴趣', '招生意向关键词', '长期招生关键词']
    }
    keyWords = data.keywords;
    var json = keyWords;
    $("#keyWords").html("<p>爬虫抽取信息关键词(以逗号,隔开， 正则表达式匹配):</p>");
    $("#keyWords").append("<p>描述指：带该关键词的就 如何如何， 名字指显示链接显示文本， URL指实际链接地址</p>")
    for (var i in showTags) {
        var e = showTags[i];
        var group = $('<div class="input-group input-group-sm"></div>');
        var span = $("<span class='input-group-addon'>{0} </span>".format(e));
        var input = '<input type="url" name="{0}" value="{1}" class="form-control">'.format(e, json[e]);
        group.append(span);
        group.append(input);
        $("#keyWords").append(group);
    }
}

function fillResearchInformationByGrid(item) {
    var tr = $('<div class="row-fluid"></div>'), 
        td_tmp = '<div class="col-md-{0}">{1}</div>',
        select = $("<select></select>"),
        option_tmp = "<option>{0}</option>";
    if (typeof(item.tags) != "string") {
        for (var j in item.tags) {
            select.append($(option_tmp.format(item.tags[j])));
        }
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
    tr.append($(td_tmp.format(2, temp)));
    var anchor = "<a href='{0}'>教员目录页</a>".format(item.link);
    tr.append($(td_tmp.format(2, anchor)));
    if (item.website) {
        anchor = "<a href='{0}'>个人页</a>".format(item.website);
        tr.append($(td_tmp.format(1, anchor)));
    }
    else {
        tr.append($(td_tmp.format(1, "")));
    }
    if (typeof(item.tags) == "string") {
        tr.append($(td_tmp.format(4, item.tags)));
    }
    else {
        var select_td = $(td_tmp.format(4, "")).append(select)
        tr.append(select_td);
    }
    temp = item.position;
    if (temp) temp = "在招";
    else temp = "";
    tr.append($(td_tmp.format(1, temp)));
    tr.append($(td_tmp.format(1, item.term || "")));

    return tr;
}

function fillSourceInfo(toggle, item) {
    var key = ['source_name/目录页链接名字', 'source_name/目录页链接',
        'source_website/个人主页名字', 'source_website/个人主页链接',
        'source_position', 'source_term', 'source_interest'],
        p_tmp = '<p>{0} : {1}</p>';
    for (var i in key) {
        var e = item[i];
        if (!(e in item)) {
            continue;
        }
        if (e.indexOf("/") > -1) {
            var head = e.split("/")[0], tail = e.split("/")[1];
            toggle.append($(p_tmp.format(tail, item[head][tail])));
            continue;
        }
        toggle.append($(p_tmp.format(e, item[e])));
    }
    return toggle;
}

function showCrawlerResult(data, step) {
    var showTags, list = data.list, table = $("<table class='table table-striped'></table>");
    showKeyWords(data, step);

    // console.log(data.list);
    $("#crawlResult").html("");
    if (step == "1") {
        $("#crawlResult").append("<p>总共查到教员 {0} 个".format(list.length));
    }
    if (step == "2") {
        var head = {'name': '名字', 'link': '学校页', 'website': '个人页', 
                    'tags': '研究方向', 'position': '招生意向', 'term': '招生期'}
        tr = fillResearchInformationByGrid(head);
        var expand = $('<div class="col-md-1">展开</div>');
        tr.append(expand);  
        table.append(tr);
    }
    for (var i in list) {
        var tr = $("<tr></tr>"), td = $("<td></td>"), toggle = null;
        if (step == "1") {
            var url = list[i].split("|")[0], name = list[i].split("|")[1];
            td.append("<span>链接URL为：</span>");
            td.append('<a href="{0}" target="_blank">{1}</a>'.format(url, url));
            tr.append(td);
            tr.append("<td>链接名字显示为：{0}</td>".format(name));
        } else if (step == '2') {
            tr = fillResearchInformationByGrid(list[i]);
            var anchor = '<a data-toggle="collapse" aria-expanded="false" class="False collapsed btn btn-success" href="#collapse{0}" aria-controls="collapse{1}">展开</a>'.format(i, i)
            var expand = $('<div class="col-md-1"></div>');
            expand.append(anchor);
            tr.append(expand);
            toggle = $('<div class="panel-collapse collapse" data-expanded="false" role="tabpanel" id="collapse{0}" aria-labelledby="heading{1}" aria-expanded="false""></div>'.format(i, i));
            toggle = fillSourceInfo(toggle, list[i])
        }
        table.append(tr);
        if (toggle) {
            table.append(toggle);
        }
    }
    $("#crawlResult").append(table);
}

