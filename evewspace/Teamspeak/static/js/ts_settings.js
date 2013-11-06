//    eve w-space
//    copyright (c) 2013  andrew austin and other contributors
//
//    this program is free software: you can redistribute it and/or modify
//    it under the terms of the gnu general public license as published by
//    the free software foundation, either version 3 of the license, or
//    (at your option) any later version. an additional term under section
//    7 of the gpl is included in the license file.
//
//    this program is distributed in the hope that it will be useful,
//    but without any warranty; without even the implied warranty of
//    merchantability or fitness for a particular purpose.  see the
//    gnu general public license for more details.
//
//    you should have received a copy of the gnu general public license
//    along with this program.  if not, see <http://www.gnu.org/licenses/>.

$(document).ready(function(){
    GetTSSettings();
    GetTSGroupSettings();
});

function GetTSSettings(){
    $.ajax({
       type: "GET",
       url: "/teamspeak/settings/general/",
       success: function(data){
           $("#ts3generalsettings").html(data);
       },
       error: function(data){
            alert("There was an error loading the general settings.");
       }
    });
}

function SaveTSSettings(){
    $.ajax({
        type: "POST",
        data: $('#ts3GeneralSettingsForm').serialize(),
        url: "/teamspeak/settings/general/",
        success: function(data){
            $("#ts3generalsettings").html(data);             
        },
        error: function(){alert("Invalid values, please make sure only integers are used.");}
    });
}
function GetTSGroupSettings(){
    $.ajax({
       type: "GET",
       url: "/teamspeak/show_groupmapping/",
       success: function(data){
           $("#show_ts_groups").html(data);
       },
       error: function(data){
            alert("There was an error loading the general settings.");
       }
    });
}

function SaveTSGroupSettings(){
    $.ajax({
        type: "POST",
        data: $('#ts3GroupSettingsForm').serialize(),
        url: "/teamspeak/settings/addgroupmap/",
        success: window.location.href = "/settings/",
        error: function(){alert("Error while adding Groupmap");}
    });
}

function DeleteTSGroupMap(id){
    $.ajax({
        type: "POST",
        data: { groupmapid: id },
        url: "/teamspeak/settings/delgroupmap/",
        success: window.location.href = "/settings/",
        error: function(){alert("Invalid values, please make sure only integers are used.");}
    });
}
function deleteGroupMap(id,djangogroup,tsgroup){
    var conf = confirm("Are you sure you want to delete " + djangogroup + " <> " +tsgroup + " ?");
    if(conf == true){
         DeleteTSGroupMap(id);
    }
}