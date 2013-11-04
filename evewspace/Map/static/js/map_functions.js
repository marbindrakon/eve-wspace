//    Eve W-Space
//    Copyright (C) 2013  Andrew Austin and other contributors
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version. An additional term under section
//    7 of the GPL is included in the LICENSE file.
//
//   This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.
//  
//  Portions Copyright (c) 2011 Georgi Kolev (arcanis@wiadvice.com). Licensed under the GPL (http://www.gnu.org/copyleft/gpl.html) license.

var loadtime = null;
var paper = null;
var objSystems = [];
var focusMS;
var sigTimerID;
var updateTimerID;
var activityLimit = 100;
var indentX = 150; //The amount of space (in px) between system ellipses on the X axis. Should be between 120 and 180.
var indentY = 70; // The amount of space (in px) between system ellipses on the Y axis
var renderWormholeTags = true; // Determines whether wormhole types are shown on the map.
var sliceLastChars = false; // Friendly name should show last 8 chars if over 8, shows first 8 if false
var highlightActivePilots = true; // Draw a notification ring around systems with active pilots.
var goodColor = "#00FF00"; // Color of good status connections
var badColor = "#FF0000"; // Color of first shrink connections
var bubbledColor = "#FF0000"; // Color of first shrink connections
var clearWhColor = "#00FF00"; // Color of good status connections
var warningColor = "#FF00FF"; // Color of mass critical connections
var renderCollapsedConnections = false; // Are collapsed connections shown?
var autoRefresh = true; // Does map automatically refresh every 15s?
var silentSystem = false; // Are systems added automatically wihthout a pop-up?

$(document).ready(function(){
    updateTimerID = setInterval(doMapAjaxCheckin, 5000);
    if (autoRefresh === true){
        refreshTimerID = setInterval(RefreshMap, 15000);
    }
});

$(document).ready(function(){
    $('#mapDiv').html(ajax_image);
    RefreshMap();
});

//Make sure timers stop when unloading the page
$(document).ready(function(){
    $(window).bind('unload', function(){
        if (sigTimerID){
            clearTimeout(sigTimerID);
        }
        clearTimeout(updateTimerID);
    });
});

function processAjax(data){
    if (data.dialogHTML){
        if (data.dialogHTML !== 'silent'){
                $('#modalHolder').empty();
                $('#modalHolder').html(data.dialogHTML);
                $('#modalHolder').modal('show');
        }else{
            RefreshMap();
        }
    }
    if (data.logs){
        $('#logDiv').empty();
        $('#logDiv').html(data.logs);
    }
    
}


function doMapAjaxCheckin() {
    var currentpath = "update/";
    $.ajax({
        type: "POST",
        url: currentpath,
        data: {"loadtime": loadtime, "silent": silentSystem},
        success: processAjax,
        error: function(error){
            alert('An error ocurred posting back to the server: \n\n' + error.responseText);
        }
        });
}


function HideSystemDetails(){
    clearTimeout(sigTimerID);
    $('#sysInfoDiv').empty();
}


function ToggleSilentAdd(){
    if (silentSystem === false){
        silentSystem = true;
        $('#btnSilentAdd').text('Silent IGB Mapping: ON');
    }else{
        silentSystem = false;
        $('#btnSilentAdd').text('Silent IGB Mapping: OFF');
    }
}


function ToggleAutoRefresh(){
    if (autoRefresh === true){
        autoRefresh = false;
        clearTimeout(refreshTimerID);
        $('#btnRefreshToggle').text('Auto Refresh: OFF');
    }else{
        autoRefresh = true;
        refreshTimerID = setInterval(RefreshMap, 15000);
        $('#btnRefreshToggle').text('Auto Refresh: ON');
    }
}


function DisplaySystemDetails(msID, sysID){
    address = "system/" + msID + "/";
    $.ajax({
        type: "GET",
        url: address,
        success: function(data){
            $('#sysInfoDiv').empty().html(data);
            LoadSignatures(msID, true);
            $.ajax({
                type: "GET",
                url: "system/" + msID +  "/signatures/new/",
                success: function(data){
                    $('#sys'+msID+'SigAddForm').empty().html(data);
                    $('#id_sigid').focus();
                }
            });
            GetPOSList(sysID);
            GetDestinations(msID);
            focusMS = msID;
            StartDrawing();
        }
    });
}


function GetPOSList(sysID){
    address = "/pos/" + sysID + "/";
    $.ajax({
        type: "GET",
        url: address,
        success: function(data){
            $('#sys' + sysID + "POSDiv").empty();
            $('#sys' + sysID + "POSDiv").html(data);
        }
    });
}


function GetDestinations(msID){
    address = "system/" + msID + "/destinations/";
    $.ajax({
        type: "GET",
        url: address,
        success: function(data){
            $('#systemDestinationsDiv').empty();
            $('#systemDestinationsDiv').html(data);
        }
    });
}


function DisplaySystemMenu(msID){
    address = "system/" + msID + "/menu/";
    $.ajax({
        type: "GET",
        url: address,
        success: function(data) { 
            $('#sysMenu').html(data);
        }
    });
}


function MarkScanned(msID, fromPanel, sysID){
    address = "system/" + msID + "/scanned/";
    $.ajax({
        type: "POST",
        url: address,
        async: false,
        data: {},
        success: function(data) { 
            GetSystemTooltips();
            if (fromPanel){
                LoadSignatures(msID, false);
            }

        }
    });
}
function CollapseSystem(msid){
    address = "system/" + msid + "/collapse/";
    $.ajax({
        type: "post",
        url: address,
        async: false,
        success: function(data) {
            DisplaySystemMenu(msid);
            RefreshMap();
        }
    });
   
}
function SetInterest(msid){
    address = "system/" + msid + "/interest/";
    $.ajax({
        type: "post",
        url: address,
        async: false,
        data: {"action": "set"},
        success: function(data) {
            DisplaySystemMenu(msid);
            RefreshMap();
        }
    });
   
}

function ResurrectSystem(msid){
    address = "system/" + msid + "/resurrect/";
    $.ajax({
        type: "post",
        url: address,
        async: false,
        success: function(data) {
            DisplaySystemMenu(msid);
            RefreshMap();
        }
    });
   
}

function RemoveInterest(msID){
    address = "system/" + msID + "/interest/";
    $.ajax({
        type: "POST",
        url: address,
        async: false,
        data: {"action": "remove"},
        success: function(data) { 
            DisplaySystemMenu(msID);
            RefreshMap();
        }
    });

}

function AssertLocation(msID){
    address = "system/" + msID + "/location/";
    $.ajax({
        type: "POST",
        url: address,
        async: true,
        data: {},
        success: function(data) { 
            RefreshMap();
        }
    });
}

function GetSystemTooltips(){
    address = "system/tooltips/";
    $.ajax({
        type: "GET",
        url: address,
        success: function(data){
            $('#systemTooltipHolder').html(data);
        }
            });
}


function GetAddPOSDialog(sysID){
    address = "/pos/" + sysID + "/add/";
   $.ajax({
        url: address,
        type: "GET",
        success: function(data){
            $('#modalHolder').empty()
            $('#modalHolder').html(data);
            $('#modalHolder').modal('show');
        }
    });
}


function GetSiteSpawns(msID, sigID){
    address = "system/" + msID + "/signatures/" + sigID + /spawns/;
   $.ajax({
        url: address,
        type: "GET",
        success: function(data){
            $('#modalHolder').empty()
            $('#modalHolder').html(data);
            $('#modalHolder').modal('show');
        }
    });

}



function AddPOS(sysID){
    //This function adds a system using the information in a form named #sysAddForm
    address = "/pos/" + sysID + "/add/";
    $.ajax({
        type: "POST",
        url: address,
        data: $('#addPOSForm').serialize(),
        success: function(data){
            GetPOSList(sysID);
        }
    });
}


function DeletePOS(posID, sysID){
    address = "/pos/" + sysID + "/" + posID + "/remove/";
    $.ajax({
        type: "POST",
        url: address,
        success: function(){
            GetPOSList(sysID);
        }
    });
}


function GetEditPOSDialog(posID, sysID){
    address= "/pos/" + sysID + "/" + posID + "/edit/";
         $.ajax({
        url: address,
        type: "GET",
        success: function(data){
            $('#modalHolder').empty()
            $('#modalHolder').html(data);
            $('#modalHolder').modal('show');
        }
    });
}


function EditPOS(posID, sysID){
    //This function adds a system using the information in a form named #sysAddForm
    address = "/pos/" + sysID + "/" + posID + "/edit/";
    $.ajax({
        type: "POST",
        url: address,
        data: $('#editPOSForm').serialize(),
        success: function(data){
            GetPOSList(sysID);
        }
    });
}


function GetWormholeTooltips(){
    address = "wormhole/tooltips/";
    $.ajax({
        type: "GET",
        url: address,
        success: function(data){
            $('#wormholeTooltipHolder').html(data);
        }
            });
}


function RefreshMap(){
    address = "refresh/";
    $.ajax({
        type: "GET",
        url: address,
        success: function(data){
            objSystems = new Array();
            newData = $.parseJSON(data);
            systemsJSON = $.parseJSON(newData[1]);
            loadtime = newData[0];
            GetWormholeTooltips();
            GetSystemTooltips();
            StartDrawing();
        }
    });
}


function EditSignature(msID, sigID){
    address = "system/" + msID + "/signatures/" + sigID + "/edit/";
    $.ajax({
        url: address,
        type: "POST",
        data: $("#sigEditForm").serialize(),
        success: function(data){
            $('#sys' + msID + "SigAddForm").empty();
            $('#sys' + msID + "SigAddForm").html(data);
            LoadSignatures(msID, false);
        }
    });
}


function PurgeSignatures(msID){
    address = "system/" + msID + "/signatures/purge/";
    $.ajax({
        url: address,
        type: "POST",
        success: function(data){
            LoadSignatures(msID, false);
            $('#btnReallyPurgeSigs').hide();
            $('#btnPurgeSigs').show();
        },
        error: function(err){
            alert("Unable to purge signatures: \n\n" + err.responseText);
        }
    });
}


function OwnSignature(msID, sigID){
    address = "system/" + msID + "/signatures/" + sigID + "/own/";
    $.ajax({
        url: address,
        type: "POST",
        success: function(data){
            LoadSignatures(msID, false);
        }
    });
}


function GetEditSignatureBox(msID, sigID){
    address = "system/" + msID + "/signatures/" + sigID + "/edit/";
    $.ajax({
        url: address,
        type: "GET",
        success: function(data){
            $('#sys' + msID + "SigAddFOrm").empty();
            $('#sys' + msID + "SigAddForm").html(data);
            LoadSignatures(msID, false);
        }
    });
}


function AddSignature(msID){
    address = "system/" + msID + "/signatures/new/";
    $.ajax({
        url: address,
        type: "POST",
        data: $("#sigAddForm").serialize(),
        success: function(data){
            $('#sys' + msID + "SigAddFOrm").empty();
            $('#sys' + msID + "SigAddForm").html(data);
            LoadSignatures(msID, false);
            $('#id_sigid').focus();
        }
    });
}


function LoadSignatures(msID, startTimer){
    address = "system/" + msID + "/signatures/";
    $.ajax({
        url: address,
        type: "GET",
        success: function(data){
            $('#sys' + msID + "Signatures").empty();
            $('#sys' + msID + "Signatures").html(data);
            if (startTimer){
                //Cancel currently running timer if any
                if (sigTimerID){
                    clearTimeout(sigTimerID);
                }
                sigTimerID = setInterval(function(){
                    if (document.getElementById("sys" + msID + "Signatures")){
                    LoadSignatures(msID, true);
                    }
                }, 5000);
            }
        }
    });
}


function MarkCleared(sigID, msID){
    address = "system/" + msID + "/signatures/" + sigID + "/clear/";
    $.ajax({
        url: address,
        type: "POST",
        success: function(){
            LoadSignatures(msID, false);
        }
    });
}


function MarkEscalated(sigID, msID){
    address = "system/" + msID + "/signatures/" + sigID + "/escalate/";
    $.ajax({
        url: address,
        type: "POST",
        success: function(){
            LoadSignatures(msID, false);
        }
    });
}


function MarkActivated(sigID, msID){
    address = "system/" + msID + "/signatures/" + sigID + "/activate/";
    $.ajax({
        url: address,
        type: "POST",
        success: function(){
            LoadSignatures(msID, false);
        }
    });
}


function DeleteSignature(sigID, msID){
    address = "system/" + msID + "/signatures/" + sigID + "/remove/";
    $.ajax({
        url: address,
        type: "POST",
        success: function(){
            LoadSignatures(msID, false);
        }
    });
}


function GetAddSystemDialog(msID){
    //This funciton gets the dialog for manual system adding with msID being
    //the parent's msID
    address = "system/" + msID + "/addchild/";
    $.ajax({
        url: address,
        type: "GET",
        success: function(data){
            $('#modalHolder').empty()
            $('#modalHolder').html(data);
            $('#modalHolder').modal('show');
        }
    });
}


function AddSystem(){
    //This function adds a system using the information in a form named #sysAddForm
    address = "system/new/";
    $.ajax({
        type: "POST",
        url: address,
        data: $('#sysAddForm').serialize(),
        success: function(data){
            setTimeout(function(){RefreshMap();}, 500);
        }
    });
}


function BulkImport(msID){
    address = "system/" + msID + "/signatures/bulkadd/";
    $.ajax({
        type: "POST",
        url: address,
        data: $('#bulkSigForm').serialize(),
        success: function(data){
            LoadSignatures(msID, false);
        },
        error: function(data){
            alert(data.responseText);
        }
    });
}


function GetBulkImport(msID){
    address= "system/" + msID + "/signatures/bulkadd/";
     $.ajax({
        url: address,
        type: "GET",
        success: function(data){
            $('#modalHolder').empty()
            $('#modalHolder').html(data);
            $('#modalHolder').modal('show');
        }
    });
}


function GetEditWormholeDialog(whID){
    address= "wormhole/" + whID + "/edit/";
     $.ajax({
        url: address,
        type: "GET",
        success: function(data){
            $('#modalHolder').empty()
            $('#modalHolder').html(data);
            $('#modalHolder').modal('show');
        }
    });

}


function EditWormhole(whID){
    address = "wormhole/" + whID + "/edit/";
    $.ajax({
        type: 'POST',
        url: address,
        data: $('#editWormholeForm').serialize(),
        success: function(){
            RefreshMap();
        }
    });
}


function GetEditSystemDialog(msID){
    address= "system/" + msID + "/edit/";
       $.ajax({
        url: address,
        type: "GET",
        success: function(data){
            $('#modalHolder').empty()
            $('#modalHolder').html(data);
            $('#modalHolder').modal('show');
        }
    });
}


function EditSystem(msID, sysID){
    address = "system/" + msID + "/edit/";
    $.ajax({
        type: 'POST',
        url: address,
        data: $('#editSystemForm').serialize(),
        success: function(){
            RefreshMap();
            DisplaySystemDetails(msID, sysID);
        }
    });
}


function DeleteSystem(msID){
    address = "system/" + msID + "/remove/";
    $.ajax({
        type: "POST",
        url: address,
        success: function(){
            if (msID == focusMS){
                HideSystemDetails();            
            }
            setTimeout(function(){RefreshMap();}, 500);
        }
    });
}


function StartDrawing() {
    if ((typeof (systemsJSON) != "undefined") && (systemsJSON != null)) {
        var stellarSystemsLength = systemsJSON.length;
        $('#mapDiv').empty();
        if (stellarSystemsLength > 0) {
            InitializeRaphael();

            var i = 0;
            for (i = 0; i < stellarSystemsLength; i++){
                var stellarSystem = systemsJSON[i];
                DrawSystem(stellarSystem)
            }
        }
    }
}


function ConnectSystems(obj1, obj2, line, bg, interest, dasharray) {
    var systemTo = obj2;
    if (obj1.line && obj1.from && obj1.to) {
        line = obj1;
        obj1 = line.from;
        obj2 = line.to;
    }
    var bb1 = obj1.getBBox(),
        bb2 = obj2.getBBox(),
        p = [{ x: bb1.x + bb1.width / 2, y: bb1.y - 1 },
        { x: bb1.x + bb1.width / 2, y: bb1.y + bb1.height + 1 },
        { x: bb1.x - 1, y: bb1.y + bb1.height / 2 },
        { x: bb1.x + bb1.width + 1, y: bb1.y + bb1.height / 2 },
        { x: bb2.x + bb2.width / 2, y: bb2.y - 1 },
        { x: bb2.x + bb2.width / 2, y: bb2.y + bb2.height + 1 },
        { x: bb2.x - 1, y: bb2.y + bb2.height / 2 },
        { x: bb2.x + bb2.width + 1, y: bb2.y + bb2.height / 2}],
        d = {}, dis = [];
    for (var i = 0; i < 4; i++) {
        for (var j = 4; j < 8; j++) {
            var dx = Math.abs(p[i].x - p[j].x),
        dy = Math.abs(p[i].y - p[j].y);
            if ((i == j - 4) || (((i != 3 && j != 6) || p[i].x < p[j].x) && ((i != 2 && j != 7) || p[i].x > p[j].x) && ((i != 0 && j != 5) || p[i].y > p[j].y) && ((i != 1 && j != 4) || p[i].y < p[j].y))) {
                dis.push(dx + dy);
                d[dis[dis.length - 1]] = [i, j];
            }
        }
    }
    if (dis.length == 0) {
        var res = [0, 4];
    } else {
        res = d[Math.min.apply(Math, dis)];
    }
    var x1 = p[res[0]].x,
        y1 = p[res[0]].y,
        x4 = p[res[1]].x,
        y4 = p[res[1]].y;
    dx = Math.max(Math.abs(x1 - x4) / 2, 10);
    dy = Math.max(Math.abs(y1 - y4) / 2, 10);
    var x2 = [x1, x1, x1 - dx, x1 + dx][res[0]].toFixed(3),
        y2 = [y1 - dy, y1 + dy, y1, y1][res[0]].toFixed(3),
        x3 = [0, 0, 0, 0, x4, x4, x4 - dx, x4 + dx][res[1]].toFixed(3),
        y3 = [0, 0, 0, 0, y1 + dy, y1 - dy, y4, y4][res[1]].toFixed(3);

    var path = ["M", x1.toFixed(3), y1.toFixed(3), "C", x2, y2, x3, y3, x4.toFixed(3), y4.toFixed(3)].join(",");


    if (line && line.line) {
        line.bg && line.bg.attr({ path: path });
        line.line.attr({ path: path });
    } else {
        var color = typeof line == "string" ? line : "#000";
        if (renderWormholeTags){
            strokeWidth = 3;
            interestWidth = 3;
        } else {
            strokeWidth = 3;
            interestWidth = 3;
            if (systemTo.WhFromParentBubbled || systemTo.WhToParentBubbled){
                color = "#FF9900";
            }
        }
        if (interest == true) {
            var lineObj = paper.path(path).attr({ stroke: color, fill: "none", "stroke-dasharray": dasharray, "stroke-width": interestWidth });
        } else {
            var lineObj = paper.path(path).attr({ stroke: color, fill: "none", "stroke-dasharray": dasharray, "stroke-width": strokeWidth });
        }
        lineObj.toBack();
        lineObj.mouseover(OnWhOver);
        lineObj.mouseout(OnWhOut);
        lineObj.whID = systemTo.whID;
        lineObj.click(function(){ GetEditWormholeDialog(lineObj.whID);});
    }


};
function InitializeRaphael() {
    var stellarSystemsLength = systemsJSON.length;
    var maxLevelX = 0;
    var maxLevelY = 0;

    var i = 0;
    for (i = 0; i < stellarSystemsLength; i++){
        var stellarSystem = systemsJSON[i];

        if (stellarSystem.LevelX > maxLevelX) {
            maxLevelX = stellarSystem.LevelX;
        }
        if (stellarSystem.LevelY > maxLevelY) {
            maxLevelY = stellarSystem.LevelY;
        }
    }
    var holderHeight = 90 + maxLevelY * indentY;
    var holderWidth = 170 + maxLevelX * (indentX + 20);
    if (paper){
        paper.clear();
        paper.remove();
    }
    paper = Raphael("mapDiv", holderWidth, holderHeight);
    holder = document.getElementById("mapDiv");
    holder.style.height = holderHeight + "px";
    holder.style.width = holderWidth + "px";
}


function GetSystemX(system){
    if (system){
        var startX = 70;

        var sysX = startX + indentX * system.LevelX;
        return sysX;
    }else{
        alert("GetSystemX: System is null or undefined");
    }
}


function GetSystemY(system){
    if (system){
        var startY = 40;
        var sysY = startY + indentY * system.LevelY;
        return sysY;
    }else{
        alert("GetSystemY: System is null or undefined.");
    }
}


function DrawSystem(system) {
    if (system == null) {
        return;
    }

    var sysX = GetSystemX(system);
    var sysY = GetSystemY(system);
    var classString;
    switch (system.SysClass){
        case 7:
            classString = "H";
            break;
        case 8:
            classString = "L";
            break;
        case 9:
            classString = "N";
            break;
        default:
            classString = "C"+system.SysClass;
            break;
    }
    if (system.Friendly){
        if (system.Friendly.length > 8){
            if (sliceLastChars == true){
                system.Friendly = ".." + system.Friendly.slice(-8);
            }else{
                system.Friendly = system.Friendly.slice(0,8) + "..";
            }
        }
        var friendly = system.Friendly + "\n";
    }else{
        var friendly = "";
    }
    var sysName = friendly + system.Name;
    sysName += "\n("+classString+"+"+system.activePilots+"P)";
    var sysText;
    if (system.LevelX != null && system.LevelX > 0) {
        var childSys = paper.ellipse(sysX, sysY, 40, 28);
        if (system.activePilots > 0 && highlightActivePilots === true){
            notificationRing = paper.ellipse(sysX, sysY, 45, 33);
            notificationRing.attr({'stroke-dasharray':'--', 'stroke-width': 2, 'stroke': '#ADFF2F'});
        }
        childSys.msID = system.msID;
        childSys.whID = system.whID;
        childSys.sysID = system.sysID;
        childSys.WhFromParentBubbled = system.WhFromParentBubbled;
        childSys.WhToParentBubbled = system.WhToParentBubbled;
        childSys.click(onSysClick);
        sysText = paper.text(sysX, sysY, sysName);
        sysText.msID = system.msID;
        sysText.sysID = system.sysID;
        sysText.click(onSysClick);
         if (is_igb === true){
            childSys.dblclick(onSysDblClick);
            sysText.dblclick(onSysDblClick);
        }
        ColorSystem(system, childSys, sysText);
        childSys.collapsed = system.collapsed;
        objSystems.push(childSys);
        var parentIndex = GetSystemIndex(system.ParentID);
        var parentSys = systemsJSON[parentIndex];
        var parentSysEllipse = objSystems[parentIndex];

        if (parentSysEllipse) {
            var lineColor = GetConnectionColor(system);
            var whColor = GetWormholeColor(system);
            var dasharray = GetConnectionDash(system);
            var interest = false;
            if (system.interestpath === true || system.interest === true){
                interest = true;
            }
            if(childSys.collapsed === false || renderCollapsedConnections === true){
                ConnectSystems(parentSysEllipse, childSys, lineColor, "#fff", interest, dasharray);
                DrawWormholes(parentSys, system, whColor);
            }
        }else{
            alert("Error processing system " + system.Name);
        }
    }else{
        var rootSys = paper.ellipse(sysX, sysY, 40, 30);
        rootSys.msID = system.msID;
        rootSys.sysID = system.sysID;
        rootSys.click(onSysClick);
        sysText = paper.text(sysX, sysY, sysName);
        sysText.msID = system.msID;
        sysText.sysID = system.sysID;
        sysText.click(onSysClick);
        if (is_igb === true){
            rootSys.dblclick(onSysDblClick);
            sysText.dblclick(onSysDblClick);
        }
        ColorSystem(system, rootSys, sysText);

        objSystems.push(rootSys);
    }
}


function GetConnectionDash(system){
    var eolDash = "-";
    var interestDash = "--";
    if (system.WhTimeStatus == 1){
        return eolDash
    }
   if (system.interestpath == true || system.interest == true){
        return interestDash;
    }
    return "none";
}


function GetConnectionColor(system){
    if (!system){
        return "#000";
    }
    if (system.LevelX < 1) {
        return "#000";
    }
    var badFlag = false;
    var warningFlag = false;
    if (system.WhMassStatus == 2){
        badFlag = true;
    }
    if (system.WhMassStatus == 1){
        warningFlag = true;
    }
    if (badFlag == true){
        return badColor;
    }
    if (warningFlag == true){
        return warningColor;
    }
    return goodColor;
}

function GetWormholeColor(system) {
    var goodColor = "#009900";
    var badColor = "#FF3300";
    if (!system) {
        return "#000";
    }

    if (system.LevelX < 1) {
        return "#000";
    }
    if (system.WhToParentBubbled == true && system.WhFromParentBubbled == true){
        return badColor;
    }else{
        return goodColor;
    }
}


function ColorSystem(system, ellipseSystem, textSysName) {

    if (!system) {
        alert("system is null or undefined");
        return;
    }

    var selected = false;
    var sysColor = "#f00";
    var sysStroke = "#fff";
    var sysStrokeWidth = 2;
    var textFontSize = 12;
    var sysStrokeDashArray = "none";
    var textColor = "#000";
    if (system.interest == true) {
        sysStrokeWidth = 7;
        sysStrokeDashArray = "--";
    }
    if (system.msID === focusMS){
        if (system.interest){
            sysStrokeWidth = 7;
        }else{
            sysStrokeWidth = 4;
        }
        sysStrokeDashArray = "- ";
    }

        // not selected
        switch (system.SysClass) {

            case 9:
                sysColor = "#CC0000";
                sysStroke = "#990000";
                textColor = "#fff";
                break;
            case 8:
                sysColor = "#93841E";
                sysStroke = "#60510A";
                textColor = "#fff";
                break;
            case 7:
                sysColor = "#009F00";
                sysStroke = "#006B00";
                textColor = "#fff";
                break;
             case 6:
                sysColor = "#0022FF";
                sysStroke = "#0000FF";
                textColor = "#FFF";
                break;
             case 5:
                sysColor = "#0044FF";
                sysStroke = "#0000FF";
                textColor = "#FFF";
                break; 
            case 4:
                sysColor = "#0066FF";
                sysStroke = "#0022FF";
                textColor = "#FFF";
                break;
            case 3:
                sysColor = "#0088FF";
                sysStroke = "#0044FF";
                textColor = "#FFF";
                break;
             case 2:
                sysColor = "#00AAFF";
                sysStroke = "#0066FF";
                textColor = "#FFF";
                break;
             case 1:
                sysColor = "#00CDFF";
                sysStroke = "#0088FF";
                textColor = "#FFF"; 
                break;
           default:
                sysColor = "#F2F4FF";
                sysStroke = "#0657B9";
                textColor = "#0974EA";
                break;
        }
    iconX = ellipseSystem.attr("cx")+40;
    iconY = ellipseSystem.attr("cy")-35;
    if (system.imageURL){
        paper.image(system.imageURL, iconX, iconY, 25, 25);
    }
    ellipseSystem.attr({ fill: sysColor, stroke: sysStroke, "stroke-width": sysStrokeWidth, cursor: "pointer", "stroke-dasharray": sysStrokeDashArray });
    textSysName.attr({ fill: textColor, "font-size": textFontSize, cursor: "pointer" });

    if (selected == false) {

        ellipseSystem.sysInfoPnlID = 0;
        textSysName.sysInfoPnlID = 0;

        
        ellipseSystem.hover(OnSysOver, OnSysOut); 
        textSysName.ellipseIndex = objSystems.length;
        textSysName.hover(OnSysOver, OnSysOut);
        
    }
}


function WormholeEffectColor(system, defaultcolor){
    switch (system.effect){
        case "Wolf-Rayet Star":
            return "#FF5500"
            break;
        case "Pulsar":
            return "#0000FF"
            break;
        case "Magnetar":
            return "#FF0000"
            break;
        case "Red Giant":
            return "#FF00FF"
            break;
        case "Cataclysmic Variable":
            return "#5555FF"
            break;
        case "Black Hole":
            return "#000000"
            break;
        default:
            return defaultcolor
            break;
    }
}


function GetBorderColor(startR, startB, startG, endR, endB, endG, system){
    diffR = startR - endR;
    diffB = startB - endB;
    diffG = startG - endG;
    factor = system.activity / activityLimit;
    if (factor < 1){
        newR = startR - (diffR * factor);
        newB = startB - (diffB * factor);
        newG = startG - (diffG * factor);
    }else{
        newR = endR;
        newB = endB;
        newG = endG;
    }
    return {'R': newR, 'G': newG, 'B': newB}
}


function DrawWormholes(systemFrom, systemTo, textColor) {

    var sysY1 = GetSystemY(systemFrom);
    var sysY2 = GetSystemY(systemTo);

    var sysX1 = GetSystemX(systemFrom);
    var sysX2 = GetSystemX(systemTo);

    var changePos = ChangeSysWormholePosition(systemTo, systemFrom);

    var textCenterX = (sysX1 + sysX2) / 2;
    textCenterX = textCenterX + 10;
    var textCenterY = (sysY1 + sysY2) / 2;

    var whFromSysX = textCenterX;
    var whFromSysY = textCenterY;

    var whToSysX = textCenterX;
    var whToSysY = textCenterY;

    if (sysY1 != sysY2) {
        textCenterX = textCenterX - 10;
        whFromSysX = textCenterX + 23;
        whToSysX = textCenterX - 23;

    } else {

        whFromSysY = textCenterY - 10;
        whToSysY = textCenterY + 10;
    }

    // draws labels near systemTo ellipse if previous same Level X system's levelY = systemTo.levelY - 1
    if (changePos == true) {

        textCenterX = sysX2 - 73;
        textCenterY = sysY2 - 30;
        if (renderWormholeTags){
            whFromSysX = textCenterX + 23;
            whToSysX = textCenterX - 23;
        }else{
            whFromSysX = textCenterX + 35;
            whToSysX = textCenterX - 10;
        }
        whFromSysY = textCenterY;
        whToSysY = textCenterY;
    } 
    

    var whFromSys = null;
    var whToSys = null;
    var whFromColor = null;
    var whToColor = null;
    var decoration = null;
    if (systemTo.WhFromParentBubbled == true){
        whFromColor = bubbledColor;
        decoration = "bold";
    }else{
        whFromColor = clearWhColor;
    }

    if (systemTo.WhToParentBubbled == true){
        whToColor = bubbledColor;
        decoration = "bold";
    }else{
        whToColor = clearWhColor;
    }
    
    if (systemTo.WhFromParent) {
        if (!renderWormholeTags){
            whFromText = ">";
            whToText = "<";
        }else{
            whFromText = systemTo.WhFromParent + " >";
            whToText = "< " + systemTo.WhToParent;
        }
        whFromSys = paper.text(whFromSysX, whFromSysY, whFromText);
        whFromSys.attr({ fill: whFromColor, cursor: "pointer", "font-size": 11, "font-weight": decoration });  //stroke: "#fff"
        whFromSys.click(function(){GetEditWormholeDialog(systemTo.whID);});
        whFromSys.whID = systemTo.whID;
        whFromSys.mouseover(OnWhOver);
        whFromSys.mouseout(OnWhOut);
    }
    if (systemTo.WhToParent) {
        whToSys = paper.text(whToSysX, whToSysY, whToText);
        whToSys.attr({ fill: whToColor, cursor: "pointer", "font-size": 11, "font-weight": decoration });

        whToSys.whID = systemTo.whID;
        whToSys.click(function(){GetEditWormholeDialog(systemTo.whID);});
        whToSys.mouseover(OnWhOver);
        whToSys.mouseout(OnWhOut);
    }
}


function ChangeSysWormholePosition(system, parent) {

    var change = false;
    var parentY = parent.LevelY;
    var currSysY = system.LevelY;

    if (currSysY > parentY + 1) {
        change = true;
    }

    return change;
}

function GetSystemIndex(systemID) {

    var stellarSystemsLength = systemsJSON.length;

    var i = 0;
    var index = -1;
    for (i = 0; i < stellarSystemsLength; i++) {
        var stellarSystem = systemsJSON[i];

        if (stellarSystem.msID == systemID) {
            index = i;
            return index;
        }
    }

    if (index < 1) {
        alert("could not find system with ID = " + systemID);
    }

}


function getScrollY() {
var scrOfX = 0, scrOfY = 0;
if (typeof (window.pageYOffset) == 'number') {
//Netscape compliant
scrOfY = window.pageYOffset;
scrOfX = window.pageXOffset;
} else if (document.body && (document.body.scrollLeft || document.body.scrollTop)) {
//DOM compliant
scrOfY = document.body.scrollTop;
scrOfX = document.body.scrollLeft;
} else if (document.documentElement && (document.documentElement.scrollLeft || document.documentElement.scrollTop)) {
//IE6 standards compliant mode
scrOfY = document.documentElement.scrollTop;
scrOfX = document.documentElement.scrollLeft;
}
//return [scrOfX, scrOfY];
return scrOfY;
}

function getScrollX() {
var scrOfX = 0, scrOfY = 0;
if (typeof (window.pageYOffset) == 'number') {
//Netscape compliant
scrOfY = window.pageYOffset;
scrOfX = window.pageXOffset;
} else if (document.body && (document.body.scrollLeft || document.body.scrollTop)) {
//DOM compliant
scrOfY = document.body.scrollTop;
scrOfX = document.body.scrollLeft;
} else if (document.documentElement && (document.documentElement.scrollLeft || document.documentElement.scrollTop)) {
//IE6 standards compliant mode
scrOfY = document.documentElement.scrollTop;
scrOfX = document.documentElement.scrollLeft;
}
//return [scrOfX, scrOfY];
return scrOfX;
}

function GetSelectedSysID() {
    return;
}

function onSysClick(e) {
    var x = e.pageX;
    var y = e.pageY;
    DisplaySystemDetails(this.msID, this.sysID);
    var div = document.getElementById("sys"+this.msID+"Tip");
    div.style.display = 'none';
}

function onSysDblClick(e) {
    CCPEVE.showInfo(5, this.sysID);
}

function OnWhOver(e) {
    var divName = "wh" + this.whID + "Tip";
    var div = document.getElementById(divName);

    if (div){
    
        var mouseX = e.clientX + getScrollX();
        var mouseY = e.clientY + getScrollY();

        div.style.position = "absolute";
        div.style.top = mouseY + "px";
        div.style.left = mouseX + 10 + "px";
        div.style.display = 'block';
    }
}

function OnWhOut() {
    var divName = "wh" + this.whID + "Tip";
    var div = document.getElementById(divName);

    if (div) {
        div.style.display = 'none';
    }
}

function OnSysOver(e) {
    var divName = "sys" + this.msID + "Tip";
    var div = document.getElementById(divName);
    if (div){
    
        var mouseX = e.clientX + getScrollX();
        var mouseY = e.clientY + getScrollY();

        div.style.position = "absolute";
        div.style.top = mouseY + "px";
        div.style.left = mouseX + 10 + "px";
        div.style.display = 'block';
    }
}

function OnSysOut() {
    var divName = "sys" + this.msID + "Tip";
    var div = document.getElementById(divName);
    if (div){
        div.style.display = 'none';
    }
}
