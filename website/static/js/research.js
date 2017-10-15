var timerId;
var keyWords = null;

function filterProfessors(col, value) {
    var newList = [], prefix = t+'-';
    for (var i in filterList) {
        if (!value) {
            newList.push(filterList[i]);
            continue;
        }
        if (col in filterList[i] && (filterList[i][col].toLowerCase().indexOf(value) > -1
                || filterList[i][col].toString().substr(0, prefix.length) == prefix)) {
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

function togglePosition(obj, pid) {
    var url = "", tr = $(obj).parent().parent(), webtd = $(tr.children()[4]);
    console.log(webtd.html());
    if (!webtd.html().trim()) {
        url = prompt("添加个人页？留空则不添加");
    }
    $.ajax({  
        type: "post", //请求方式  
        url: "togglePosition", //发送请求地址  
        timeout: 30000,//超时时间：30秒
        contentType: 'application/json',
        dataType: "json",
        data: JSON.stringify({"pid": pid, "url": url}),
        //请求成功后的回调函数 data为json格式  
        success:function(data){
            if (data.error) {
                alert(data.error);
                return;
            }
            console.log(data.position);
            if (data.status) {
                var text = $(tr.children()[6]).html().trim();
                if (text == "招生中" && !data.position) {
                    text = "";
                    $(obj).html("招生中");
                    $(tr.children()[6]).html(text);
                } else if (text == "" && data.position){
                    text = "招生中";
                    $(obj).html("已招满");
                    $(tr.children()[6]).html(text);
                } else {
                    alert("主页招生状态与请求不一致");
                }
                
            } else {
                alert("没道理，请联系开发者");
            }
            if (url) {
                var a = $('<a href="{0}">个人页</a>'.format(url));
                webtd.append(a);
            }
        },  
        //请求出错的处理  
        error: function(){  
            alert("请求出错");  
        }
    });  

}

function getProfessorsList(col) {
    var major = parseInt($("#majorName").val()),
        interest = $("#researchName").val(),
        college = $("#collegeName").val(),
        position = $("#positionName").val(),
        param = "";

    if (col == 'position' && !position) {
        filterProfessorByPosition();
        return;
    }
    if (col == 'interest' && !interest) {
        filterProfessors('school', '');
        return;
    }
    if (major == '0' || major == '') {
        alert("起码先选择专业");
        return;
    }
    var params = getSharpParam() || {};
    if (college.length > 4) {
        params["学校"] = college;
    }
    if (major != 0) {
        params["专业"] = major;
    }
    if (interest != "") {
        params["研究方向"] = interest;
    }
    if (position != "") {
        params["招生意向"] = position;
    }
    var temp = "{0}#{1}".format(document.URL.split("#")[0], jsonToSharpParam(params));
    window.location.href = temp;
    if (college)
        param = "学校={0}".format(college);
    param = "专业={0}".format(major);
    if (interest)
        param = "研究方向={0}".format(interest);
    if (position)
        param = "招生={0}".format(position);

    window.location.href = "{0}#{1}".format(document.URL.split("#")[0], param);

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

function interests_modify(obj, id, val) {
    var data = {}, tr = $(obj).parent().parent(),
            name = $($(tr.children("td")[0]).children("input")).val();
    if (val == 1) {
        // 删除
        var r = confirm("确认删除？");
        if (r == false) {
            return;
        }
        data = {'id': id, 'name': name, 'type': 1};

    } else {
        $(obj).html("更新中");
        var zh = $($(tr.children("td")[1]).children("input")).val(),
            category = $($(tr.children("td")[2]).children("input")).val();
        data = {'id': id, 'name': name, 'zh': zh, 'category': category, 'type': 0};
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
            
            if (val == 1) {
                tr.remove();
            } else {
                $(obj).html("更新成功");
                setTimeout(function() {$(obj).html("更新");}, 1000);
            }
        }
    });   
}
function getMajorInterestsList() {
    $("#collegeList").html("");
    var major = parseInt($("#majorName").val());
    if (major == 0) {
        $("#researchName").html("<option value=''>不限</option>");
        return;
    }
    var temp = "{0}#专业={1}".format(document.URL.split("#")[0], major);
    window.location.href = temp;
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
                    var btn_update = $('<a href="javascript:void(0)" class="btn btn-success">更新</a>');
                    var btn_delete = $('<a href="javascript:void(0)" class="btn btn-danger">删除</a>');
                    btn_update.attr("onclick", 'interests_modify(this, "{0}", 0)'.format(data.list[i].id));
                    btn_delete.attr("onclick", 'interests_modify(this, "{0}", 1)'.format(data.list[i].id));

                    tr.append($("<td><input type='text' value='{0}' class='form-control'/></td>".format(data.list[i].name)));
                    tr.append($("<td><input type='text' value='{0}' class='form-control'/></td>".format(data.list[i].zh || '')));
                    tr.append($("<td><input type='text' value='{0}' class='form-control'/></td>".format(data.list[i].category_name || '')));
                    var pass = $('<td></td>').append(btn_update);
                    var del = $('<td></td>').append(btn_delete);
                    tr.append(pass);
                    tr.append(del);
                    $("#collegeList").append(tr);
                }
            } else {
                for (var i in data.list) {
                    if (data.list[i].category_name != '' && 
                        data.list[i].name != data.list[i].category_name) {
                        continue;
                    }
                    if (i > 0 && data.list[i].name == data.list[i-1].name &&
                        data.list[i].category_name == data.list[i-1].category_name) {
                        continue;
                    }
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
    var url = $("#directoryUrl").val(), 
        major = $("#majorName").val();
    //使用JQuery从后台获取JSON格式的数据
    $.ajax({  
        type: "post",//请求方式  
        url: "getResearchProgress",//发送请求地址  
        timeout: 30000,//超时时间：30秒
        contentType: 'application/json',
        dataType: "json",
        data: JSON.stringify({"url": url, "major": major}),
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

function showKeyWordsList(data, showTags) {
    keyWords = data.keywords;
    var json = keyWords;
    
    for (var i in showTags) {
        var e = showTags[i];
        var group = $('<div class="input-group input-group-sm"></div>');
        var span = $("<span class='input-group-addon'>{0} </span>".format(e));
        var input = '<input type="text" name="{0}" value="{1}" class="form-control">'.format(e, json[e]);
        group.append(span);
        group.append(input);
        $("#keyWords").append(group);
    }
}

function showKeyWords(data, step) {
    $("#keyWords").html("<p>爬虫抽取信息关键词(以逗号,隔开， 正则表达式匹配):</p>");
    if (step == "1") {
        showTags = ['教员URL可能包含', '教员URL不可能包含'];
        $("#keyWords").append("<p>先根据关键词选出所有可能的URL,再过滤不可能的URL</p>");
    }
    else if (step == "2") {
        showTags = ['个人主页URL不可能包含', '个人主页URL可能包含', 
                '教授个人主页可能显示为', '文件而不是网页', "人名不可能是",
                '有些方向的前缀', '其他可能的研究兴趣短语',
                '其他可能的研究兴趣单词', '一段研究兴趣的起始词', 
                '非研究兴趣的词', '该句开始不再是研究兴趣', 
                '招生意向关键词', '长期招生关键词']
        $("#keyWords").append("<p>先根据关键词过滤不可能的URL,再选择可能的</p>");
    }
    showKeyWordsList(data, showTags);
}

function fillResearchInformationByGrid(no, item) {
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
                if (parts[i].length > 6)
                    parts[i] = parts[i].substring(0, 5);
            }
            temp += parts[i] + ' ';
        }
    }
    tr.append($(td_tmp.format(1, no)));
    tr.append($(td_tmp.format(2, temp)));
    var anchor = "<a href='{0}' target='_blank'>索引页</a>".format(item.link);
    tr.append($(td_tmp.format(1, anchor)));
    if (item.website) {
        anchor = "<a href='{0}' target='_blank'>个人页</a>".format(item.website);
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

    temp = item.term;
    if (temp) temp = "Y";
    else temp = "";
    tr.append($(td_tmp.format(1,  temp)));

    return tr;
}

function fillSourceInfo(toggle, item) {
    var side = $("<div class='col-xs-2 col-md-2 col-lg-2'></div>"),
        main = $("<div class='col-xs-10 col-md-10 col-lg-10'></div>"),
        key = ['source_name/目录页链接名字', 'source_name/链接URL',
        'source_website/个人主页名字', 'source_website/个人主页链接URL',
        '招生意向说明部分原文', '研究方向部分原文'],
        p_tmp = '<p>{0} : {1}</p>';
    for (var i in key) {
        var e = key[i];        
        if (e.indexOf("/") > -1) {
            var head = e.split("/")[0], tail = e.split("/")[1];
            if (!(head in item && tail in item[head])) {
                continue;
            }
            main.append($(p_tmp.format(tail, item[head][tail])));
            continue;
        }
        if (!(e in item)) {
            continue;
        }
        main.append($(p_tmp.format(e, item[e])));
    }
    toggle.append(side);
    toggle.append(main);
    return toggle;
}

function recrawl(obj, i) {
    var url = $("#directoryUrl").val(),
        major = parseInt($("#majorName").val()),
        prof = parseInt($("#professorUrl").val()),
        college = $("#collegeName").val();
    var data = {'directory_url': url, 'major': major, 'college_name': college,
                'professor_url': prof, 'no': i};

    $.ajax({  
        type: "post", //请求方式  
        url: "recrawlaFaculty", //发送请求地址  
        timeout: 30000,//超时时间：30秒
        contentType: 'application/json',
        dataType: "json",
        data: JSON.stringify(data),
        //请求成功后的回调函数 data为json格式  
        success:function(data){
            if (data.error) {
                window.clearInterval(timerId);
                alert(data.error);
                return;
            }
            
        },  
        //请求出错的处理  
        error: function(){  
            window.clearInterval(timerId);
            alert("请求出错");  
        }
    }); 
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
        tr = fillResearchInformationByGrid('', head);
        var expand = $('<div class="col-md-1">展开</div>');
        tr.append(expand);  

        // var td_tmp = '<div class="col-md-{0}">{1}</div>';
        // tr.append($(td_tmp.format(1, "重新爬")));
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
            tr = fillResearchInformationByGrid(i, list[i]);
            var anchor = '<a data-toggle="collapse" aria-expanded="false" class="False collapsed btn btn-success" href="#collapse{0}" aria-controls="collapse{1}">展开</a>'.format(i, i)
            var expand = $('<div class="col-md-1"></div>');
            expand.append(anchor);
            tr.append(expand);

            //var recrawl = $('<a href="javascript:void(0)" class="btn btn-danger">重新爬</a>');
            //recrawl.attr("onclick", "recrawl(this, {0})".format(i));
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

