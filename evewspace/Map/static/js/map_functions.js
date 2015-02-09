//   Eve W-Space
//   Copyright 2014 Andrew Austin and contributors
//
//   Licensed under the Apache License, Version 2.0 (the "License");
//   you may not use this file except in compliance with the License.
//   You may obtain a copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
//   Unless required by applicable law or agreed to in writing, software
//   distributed under the License is distributed on an "AS IS" BASIS,
//   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//   See the License for the specific language governing permissions and
//   limitations under the License.
//  
//  Portions Copyright (c) 2011 Georgi Kolev (arcanis@wiadvice.com). Licensed under the Apache 2.0 license.


var loadtime = null;
var paper = null;
var objSystems = [];
var focusMS;
var sigTimerID;
var updateTimerID;
var refreshTimerID;
var systemsJSON;
var activityLimit = 100;
var scalingFactor = 1; //scale the interface
var textFontSize = 11; // The base font size
var indentX = 150; // The amount of space (in px) between system ellipses on the X axis. Should be between 120 and 180
var indentY = 70; // The amount of space (in px) between system ellipses on the Y axis.
var strokeWidth = 3; // The width in px of the line connecting wormholes
var interestWidth = 3; // The width in px of the line connecting wormholes when interest is on
var renderWormholeTags = true; // Determines whether wormhole types are shown on the map
var sliceLastChars = false; // Friendly name should show last 8 chars if over 8, shows first 8 if false
var showPilotList = true; // Show pilot names under systems
var highlightActivePilots = false; // Draw a notification ring around systems with active pilots.
var goodColor = "#00FF00"; // Color of good status connections
var goodColor_zen = "#999"; // Color of good status connections
var badColor = "#FF0000"; // Color of first shrink connections
var bubbledColor = "#FF0000"; // Color of first shrink connections
var clearWhColor = "#BBFFBB"; // Color of good status connections
var warningColor = "#FF00FF"; // Color of mass critical connections
var eolColor = "#F0FF00"; //color for eol
var sysColor_zen = "#222"; //color for eol
var frigWhColor = "#FFFFFF"; // Color of Hyperion Frigate Hole
var frigWhColor_zen = "#71cbff"; // Color of Hyperion Frigate Hole
var textColorSelect = "#FFF"; //selected system text colour
var textColorSelect_zen = "#FFFC00"; //selected system text colour (zen mode)
var effectColorWolfRayet = "#ff5500";
var effectColorPulsar = "0000ff";
var effectColorMagnetar = "#ff0000";
var effectColorRedGiant = "#ff00ff";
var effectColorCataclysmic = "#5555ff";
var effectColorBlackHole = "#000";
var borderColorSelect = "#FFFC00"; //selected system
var borderColorSelect_zen = "#FFFC00"; //selected system
var shatteredBorderColor = "#FFA500";
var colorNullSec = "#CC0000";
var colorHighSec = "#009F00";
var colorLowSec = "#93841E";
var colorC6 = "#0022FF";
var colorC5 = "#0044FF";
var colorC4 = "#0066FF";
var colorC3 = "#0088FF";
var colorC2 = "#00AAFF";
var colorC1 = "#00CDFF";
var colorThera = "#800080";
var colorSmallShipHole = "#FFA500";
var borderColorNullSec = "#990000"; //(border colours not used in zen mode. In zen mode, the above colours are used for border instead.), border colours are overridden by wormhole effects
var borderColorLowSec = "#60510A";
var borderColorHighSec = "#006B00";
var borderColorC6 = "#0000FF";
var borderColorC5 = "#0000FF";
var borderColorC4 = "#0022FF";
var borderColorC3 = "#0044FF";
var borderColorC2 = "#0066FF";
var borderColorC1 = "#0088FF";
var borderColorThera = "#7F3939";
var borderColorSmallShipHole = "#7f5200";
var systemTextColor = "#fff";
var pilotColor = "#fff";
var renderCollapsedConnections = false; // Are collapsed connections shown?
var autoRefresh = true; // Does map automatically refresh every 15s?
var silentSystem = true; // Are systems added automatically wihthout a pop-up?
var kspaceIGBMapping = false; // Do we map K<>K connections from the IGB?
var zenMode = false;



function s(n) { //apply scaling factor, short function name so it's quick to type
    return Math.ceil(n * scalingFactor)
}

$(document).ready(function () {
    $('.slider').slider().on('slide', function(ev) {
        scale(ev.value);
    });
    updateTimerID = setInterval(doMapAjaxCheckin, 5000);
    if (autoRefresh === true) {
        refreshTimerID = setInterval(RefreshMap, 15000);
    }
    if (silentSystem === true) {
        $('#btnSilentAdd').text('Silent IGB Mapping: ON');
    }
    if (kspaceIGBMapping === true) {
        $('#btnKspaceIGB').text('Map K-Space Connections: ON');
    } else {
        $('#btnKspaceIGB').text('Map K-Space Connections: OFF');
    }
    if (zenMode) {
        $('#btnZen').text("Zen: ON");
    } else {
        $('#btnZen').text("Zen: OFF");
    }
    if (showPilotList) {
        $('#btnPilotList').text("Pilot List: ON");
    } else {
        $('#btnPilotList').text("Pilot List: OFF");
    }
});

$(document).ready(function () {
    $('#mapDiv').html(ajax_image);
    RefreshMap();
});


//Make sure timers stop when unloading the page
$(document).ready(function () {
    $(window).bind('unload', function () {
        if (sigTimerID) {
            clearTimeout(sigTimerID);
        }
        clearTimeout(updateTimerID);
    });
});

function processAjax(data) {
    if (data.dialogHTML) {
        if (data.dialogHTML !== 'silent') {
            var modalHolder = $('#modalHolder');
            modalHolder.empty();
            modalHolder.html(data.dialogHTML);
            modalHolder.modal('show');
        } else {
            RefreshMap();
        }
    }

    if (data.logs) {
        var logDiv = $('#logDiv');
        logDiv.empty();
        logDiv.html(data.logs);
    }
}

function doMapAjaxCheckin() {
    var currentPath = "update/";
    $.ajax({
        type: "POST",
        url: currentPath,
        data: {"loadtime": loadtime, "silent": silentSystem, 'kspace': kspaceIGBMapping},
        success: processAjax
    });
}

function HideSystemDetails() {
    clearTimeout(sigTimerID);
    $('#sysInfoDiv').empty();
}

function ToggleSilentAdd() {
    if (silentSystem === false) {
        silentSystem = true;
        $('#btnSilentAdd').text('Silent IGB Mapping: ON');
    } else {
        silentSystem = false;
        $('#btnSilentAdd').text('Silent IGB Mapping: OFF');
    }
}

function ToggleKspaceMapping() {
    if (kspaceIGBMapping === false) {
        kspaceIGBMapping = true;
        $('#btnKspaceIGB').text('Map K-Space Connections: ON');
    } else {
        kspaceIGBMapping = false;
        $('#btnKspaceIGB').text('Map K-Space Connections: OFF');
    }
}

function ToggleAutoRefresh() {
    if (autoRefresh === true) {
        autoRefresh = false;
        clearTimeout(refreshTimerID);
        $('#btnRefreshToggle').text('Auto Refresh: OFF');
    } else {
        autoRefresh = true;
        refreshTimerID = setInterval(RefreshMap, 15000);
        $('#btnRefreshToggle').text('Auto Refresh: ON');
    }
}

function DisplaySystemDetails(msID, sysID) {
    var address = "system/" + msID + "/";
    $.ajax({
        type: "GET",
        url: address,
        success: function (data) {
            $('#sysInfoDiv').empty().html(data);
            LoadSignatures(msID, true);
            $.ajax({
                type: "GET",
                url: "system/" + msID + "/signatures/new/",
                success: function (data) {
                    $('#sys' + msID + 'SigAddForm').empty().html(data);
                    $('#sysInfoDiv').focus();
                }
            });
            GetPOSList(sysID);
            GetDestinations(msID);
            $('#btnImport').off();
            $('#btnImport').click(function(e){
                BulkImport(msID);
            });
            focusMS = msID;
            StartDrawing();
        }
    });
}

function GetPOSList(sysID) {
    var address = "/pos/" + sysID + "/";
    $.ajax({
        type: "GET",
        url: address,
        success: function (data) {
            var POSlist = $('#sys' + sysID + "POSDiv");
            POSlist.empty();
            POSlist.html(data);
        }
    });
}

function GetDestinations(msID) {
    var address = "system/" + msID + "/destinations/";
    $.ajax({
        type: "GET",
        url: address,
        success: function (data) {
            var destinations = $('#systemDestinationsDiv');
            destinations.empty();
            destinations.html(data);
        }
    });
}

function DisplaySystemMenu(msID) {
    var address = "system/" + msID + "/menu/";
    $.ajax({
        type: "GET",
        url: address,
        success: function (data) {
            $('#sysMenu').html(data);
        }
    });
}

function GetExportMap(mapID) {
    var address = "export/";
    $.ajax({
        url: address,
        type: "GET",
        success: function (data) {
            var modalHolder = $('#modalHolder');
            modalHolder.html(data);
            modalHolder.modal('show');
        },
        error: function (error) {
            alert('Could not get the export dialog:\n\n' + error.responseText);
        }
    });
}

function MarkScanned(msid, frompanel, sysid) {
    var address = "system/" + msid + "/scanned/";
    $.ajax({
        type: "post",
        url: address,
        async: false,
        data: {},
        success: function (data) {
            getsystemtooltips();
            if (frompanel) {
                loadsignatures(msid, false);
            }
        }
    });
}

function SetImportance(msid, sysid,importance) {
    var address = "system/" + msid + "/importance/";
    $.ajax({
        type: "post",
        url: address,
        async: false,
        data: {'importance':importance},
        success: function (data) {
            DisplaySystemMenu(msid);
            RefreshMap();
        }
    });
}

function CollapseSystem(msID) {
    var address = "system/" + msID + "/collapse/";
    $.ajax({
        type: "post",
        url: address,
        async: false,
        success: function (data) {
            DisplaySystemMenu(msID);
            RefreshMap();
        }
    });
}

function SetInterest(msID) {
    var address = "system/" + msID + "/interest/";
    $.ajax({
        type: "post",
        url: address,
        async: false,
        data: {"action": "set"},
        success: function (data) {
            DisplaySystemMenu(msID);
            RefreshMap();
        }
    });
}

function ResurrectSystem(msID) {
    var address = "system/" + msID + "/resurrect/";
    $.ajax({
        type: "post",
        url: address,
        async: false,
        success: function (data) {
            DisplaySystemMenu(msID);
            RefreshMap();
        }
    });
}

function RemoveInterest(msID) {
    var address = "system/" + msID + "/interest/";
    $.ajax({
        type: "POST",
        url: address,
        async: false,
        data: {"action": "remove"},
        success: function (data) {
            DisplaySystemMenu(msID);
            RefreshMap();
        }
    });
}

function AssertLocation(msID) {
    var address = "system/" + msID + "/location/";
    $.ajax({
        type: "POST",
        url: address,
        async: true,
        data: {},
        success: function (data) {
            RefreshMap();
        }
    });
}

function GetSystemTooltips() {
    var address = "system/tooltips/";
    $.ajax({
        type: "GET",
        url: address,
        success: function (data) {
            $('#systemTooltipHolder').html(data);
            $('#systemTooltipHolder>div').off();
            //clicking the tooltip acts as clicking the system 
            //(IG browser can be sloppy)
            $('#systemTooltipHolder>div').click(function(){
                var msID = parseInt(this.id.substr(3,this.id.length -6));
                var sysID = GetSysID(msID);
                DisplaySystemDetails(msID, sysID);
                var div = $('#sys' + msID + "Tip").hide();

                if (div[0]) {
                    div.hide();
                }
            });
        }
    });
}

function GetAddPOSDialog(sysID) {
    var address = "/pos/" + sysID + "/add/";
    $.ajax({
        url: address,
        type: "GET",
        success: function (data) {
            var modalHolder = $('#modalHolder');
            modalHolder.empty();
            modalHolder.html(data);
            modalHolder.modal('show');
        }
    });
}

function GetSiteSpawns(msID, sigID) {
    var address = "system/" + msID + "/signatures/" + sigID + /spawns/;
    $.ajax({
        url: address,
        type: "GET",
        success: function (data) {
            var modalHolder = $('#modalHolder');
            modalHolder.empty();
            modalHolder.html(data);
            modalHolder.modal('show');
        }
    });
}

function AddPOS(sysID) {
    //This function adds a system using the information in a form named #sysAddForm
    var address = "/pos/" + sysID + "/add/";
    var btnAddPOS = $('#btnAddPOS');
    var pos_message = $('#pos_message');
    pos_message.hide();
    btnAddPOS.html('Saving...');
    btnAddPOS.addClass('disabled');
    $.ajax({
        type: "POST",
        url: address,
        data: $('#addPOSForm').serialize(),
        success: function (data) {
            GetPOSList(sysID);
            $('#modalHolder').modal('hide');
            btnAddPOS.html('Add POS');
            btnAddPOS.removeClass('disabled');
        },
        error: function (error) {
            pos_message.html(error.responseText);
            pos_message.show();
            btnAddPOS.html('Add POS');
            btnAddPOS.removeClass('disabled');
        }
    });
}

function DeletePOS(posID, sysID) {
    var address = "/pos/" + sysID + "/" + posID + "/remove/";
    $.ajax({
        type: "POST",
        url: address,
        success: function () {
            GetPOSList(sysID);
        }
    });
}

function GetEditPOSDialog(posID, sysID) {
    var address = "/pos/" + sysID + "/" + posID + "/edit/";
    $.ajax({
        url: address,
        type: "GET",
        success: function (data) {
            var modalHolder = $('#modalHolder');
            modalHolder.empty();
            modalHolder.html(data);
            modalHolder.modal('show');
        }
    });
}

function EditPOS(posID, sysID) {
    var address = "/pos/" + sysID + "/" + posID + "/edit/";
    var btnEditPOS = $('#btnAddPOS');
    $('#pos_message').hide();
    btnEditPOS.html('Saving...');
    btnEditPOS.addClass('disabled');
    $.ajax({
        type: "POST",
        url: address,
        data: $('#editPOSForm').serialize(),
        success: function (data) {
            GetPOSList(sysID);
            $('#modalHolder').modal('hide');
            btnEditPOS.html('Save POS');
            btnEditPOS.removeClass('disabled');
        },
        error: function (error) {
            $('#pos_error').html(error.responseText);
            $('#pos_message').show();
            btnEditPOS.html('Save POS');
            btnEditPOS.removeClass('disabled');
        }
    });
}

function GetWormholeTooltips() {
    var address = "wormhole/tooltips/";
    $.ajax({
        type: "GET",
        url: address,
        success: function (data) {
            $('#wormholeTooltipHolder').html(data);
        }
    });
}

function RefreshMap() {
    var address = "refresh/";
    $.ajax({
        type: "GET",
        url: address,
        success: function (data) {
            objSystems = [];
            var newData = $.parseJSON(data);
            systemsJSON = $.parseJSON(newData[1]);
            loadtime = newData[0];
            GetWormholeTooltips();
            GetSystemTooltips();
            StartDrawing();
        }
    });
}

function EditSignature(msID, sigID) {
    var address = "system/" + msID + "/signatures/" + sigID + "/edit/";
    $.ajax({
        url: address,
        type: "POST",
        data: $("#sigEditForm").serialize(),
        success: function (data) {
            var sigAddForm = $('#sys' + msID + "SigAddForm");
            sigAddForm.empty();
            sigAddForm.html(data);
            LoadSignatures(msID, false);
        }
    });
}

function PurgeSignatures(msID) {
    var address = "system/" + msID + "/signatures/purge/";
    $.ajax({
        url: address,
        type: "POST",
        success: function (data) {
            LoadSignatures(msID, false);
            $('#btnReallyPurgeSigs').hide();
            $('#btnPurgeSigs').show();
        },
        error: function (err) {
            alert("Unable to purge signatures: \n\n" + err.responseText);
        }
    });
}

function OwnSignature(msID, sigID) {
    var address = "system/" + msID + "/signatures/" + sigID + "/own/";
    $.ajax({
        url: address,
        type: "POST",
        success: function (data) {
            LoadSignatures(msID, false);
        }
    });
}

function GetEditSignatureBox(msID, sigID) {
    var address = "system/" + msID + "/signatures/" + sigID + "/edit/";
    $.ajax({
        url: address,
        type: "GET",
        success: function (data) {
            var sigAddForm = $('#sys' + msID + "SigAddForm");
            sigAddForm.empty();
            sigAddForm.html(data);
            LoadSignatures(msID, false);
        }
    });
}

function AddSignature(msID) {
    var address = "system/" + msID + "/signatures/new/";
    $.ajax({
        url: address,
        type: "POST",
        data: $("#sigAddForm").serialize(),
        success: function (data) {
            var sigAddForm = $('#sys' + msID + "SigAddForm");
            sigAddForm.empty();
            sigAddForm.html(data);
            LoadSignatures(msID, false);
            $('#id_sigid').focus();
        }
    });
}

function LoadSignatures(msID, startTimer) {
    var address = "system/" + msID + "/signatures/";
    $.ajax({
        url: address,
        type: "GET",
        success: function (data) {
            var signatures = $('#sys' + msID + "Signatures");
            signatures.empty();
            signatures.html(data);
            if (startTimer) {
                //Cancel currently running timer if any
                if (sigTimerID) {
                    clearTimeout(sigTimerID);
                }
                sigTimerID = setInterval(function () {
                    if (signatures[0]) {
                        LoadSignatures(msID, true);
                    }
                }, 5000);
            }
        }
    });
}

function MarkCleared(sigID, msID) {
    var address = "system/" + msID + "/signatures/" + sigID + "/clear/";
    $.ajax({
        url: address,
        type: "POST",
        success: function () {
            LoadSignatures(msID, false);
        }
    });
}

function MarkEscalated(sigID, msID) {
    var address = "system/" + msID + "/signatures/" + sigID + "/escalate/";
    $.ajax({
        url: address,
        type: "POST",
        success: function () {
            LoadSignatures(msID, false);
        }
    });
}

function MarkActivated(sigID, msID) {
    var address = "system/" + msID + "/signatures/" + sigID + "/activate/";
    $.ajax({
        url: address,
        type: "POST",
        success: function () {
            LoadSignatures(msID, false);
        }
    });
}

function DeleteSignature(sigID, msID) {
    var address = "system/" + msID + "/signatures/" + sigID + "/remove/";
    $.ajax({
        url: address,
        type: "POST",
        success: function () {
            LoadSignatures(msID, false);
        }
    });
}

function GetAddSystemDialog(msID) {
    // This function gets the dialog for manual system adding with msID being the parent's msID
    var address = "system/" + msID + "/addchild/";
    $.ajax({
        url: address,
        type: "GET",
        success: function (data) {
            var modalHolder = $('#modalHolder');
            modalHolder.empty();
            modalHolder.html(data);
            modalHolder.modal('show');
        }
    });
}

function AddSystem() {
    //This function adds a system using the information in a form named #sysAddForm
    var address = "system/new/";
    $.ajax({
        type: "POST",
        url: address,
        data: $('#sysAddForm').serialize(),
        success: function (data) {
            setTimeout(function () {
                RefreshMap();
            }, 500);
        }
    });
}

function BulkImport(msID) {
    var address = "system/" + msID + "/signatures/bulkadd/";
    $.ajax({
        type: "POST",
        url: address,
        data: $('#bulkSigForm').serialize(),
        success: function (data) {
            LoadSignatures(msID, false);
        },
        error: function (data) {
            alert(data.responseText);
        }
    });
}

function GetBulkImport(msID) {
    var address = "system/" + msID + "/signatures/bulkadd/";
    $.ajax({
        url: address,
        type: "GET",
        success: function (data) {
            var modalHolder = $('#modalHolder');
            modalHolder.empty();
            modalHolder.html(data);
            modalHolder.modal('show');
        }
    });
}

function GetEditWormholeDialog(whID) {
    var address = "wormhole/" + whID + "/edit/";
    $.ajax({
        url: address,
        type: "GET",
        success: function (data) {
            var modalHolder = $('#modalHolder');
            modalHolder.empty();
            modalHolder.html(data);
            modalHolder.modal('show');
        }
    });

}

function EditWormhole(whID) {
    var address = "wormhole/" + whID + "/edit/";
    $.ajax({
        type: 'POST',
        url: address,
        data: $('#editWormholeForm').serialize(),
        success: function () {
            RefreshMap();
        }
    });
}

function GetEditSystemDialog(msID) {
    var address = "system/" + msID + "/edit/";
    $.ajax({
        url: address,
        type: "GET",
        success: function (data) {
            var modalHolder = $('#modalHolder');
            modalHolder.empty();
            modalHolder.html(data);
            modalHolder.modal('show');
        }
    });
}

function EditSystem(msID, sysID) {
    var address = "system/" + msID + "/edit/";
    $.ajax({
        type: 'POST',
        url: address,
        data: $('#editSystemForm').serialize(),
        success: function () {
            RefreshMap();
            DisplaySystemDetails(msID, sysID);
        }
    });
}

function DeleteSystem(msID) {
    var address = "system/" + msID + "/remove/";
    $.ajax({
        type: "POST",
        url: address,
        success: function () {
            if (msID == focusMS) {
                HideSystemDetails();
            }
            setTimeout(function () {
                RefreshMap();
            }, 500);
        }
    });
}

function PromoteSystem(msID) {
    var address = "system/" + msID + "/promote/";
    $.ajax({
        type: "POST",
        url: address,
        success: function () {
            if (msID == focusMS) {
                HideSystemDetails();
            }
            setTimeout(function () {
                RefreshMap();
            }, 500);
        }
    });
}

function StartDrawing() {
    if ((typeof (systemsJSON) != "undefined") && (systemsJSON != null)) {
        var stellarSystemsLength = systemsJSON.length;
        $('#mapDiv').empty();
        if (stellarSystemsLength > 0) {
            InitializeRaphael();
            for (var i = 0; i < stellarSystemsLength; i++) {
                var stellarSystem = systemsJSON[i];
                DrawSystem(stellarSystem)
            }
        }
    }
}


function GetSysID(msID) {
    //get systemID from msID
    for (var i = 0; i < systemsJSON.length; i++) {
        if (systemsJSON[i].msID == msID) return systemsJSON[i].sysID;
    }
    return null;
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
        p = [{x: bb1.x + bb1.width / 2, y: bb1.y - 1},
            {x: bb1.x + bb1.width / 2, y: bb1.y + bb1.height + 1},
            {x: bb1.x - 1, y: bb1.y + bb1.height / 2},
            {x: bb1.x + bb1.width + 1, y: bb1.y + bb1.height / 2},
            {x: bb2.x + bb2.width / 2, y: bb2.y - 1},
            {x: bb2.x + bb2.width / 2, y: bb2.y + bb2.height + 1},
            {x: bb2.x - 1, y: bb2.y + bb2.height / 2},
            {x: bb2.x + bb2.width + 1, y: bb2.y + bb2.height / 2}],
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
        line.bg && line.bg.attr({path: path});
        line.line.attr({path: path});
    } else {
        var color = typeof line == "string" ? line : "#000";
        if (!renderWormholeTags) {
            if (systemTo.WhFromParentBubbled || systemTo.WhToParentBubbled) {
                color = "#FF9900";
            }
        }
        var lineObj;
        if (interest == true) {
            lineObj = paper.path(path).attr({
                stroke: color,
                fill: "none",
                "stroke-dasharray": dasharray,
                "stroke-width": interestWidth,
            });
        } else {
            lineObj = paper.path(path).attr({
                stroke: color,
                fill: "none",
                "stroke-dasharray": dasharray,
                "stroke-width": strokeWidth
            });
        }

        lineObj.toBack();
        lineObj.mouseover(onWhOver);
        lineObj.mouseout(onWhOut);
        lineObj.whID = systemTo.whID;
        lineObj.click(function () {
            GetEditWormholeDialog(lineObj.whID);
        });
    }
}

function InitializeRaphael() {
    var stellarSystemsLength = systemsJSON.length;
    var maxLevelX = 0;
    var maxLevelY = 0;

    for (var i = 0; i < stellarSystemsLength; i++) {
        var stellarSystem = systemsJSON[i];

        if (stellarSystem.LevelX > maxLevelX) {
            maxLevelX = stellarSystem.LevelX;
        }
        if (stellarSystem.LevelY > maxLevelY) {
            maxLevelY = stellarSystem.LevelY;
        }
    }
    var holderHeight = s(90) + maxLevelY * indentY;
    var holderWidth = s(170) + maxLevelX * (indentX + s(20));
    if (paper) {
        paper.clear();
        paper.remove();
    }
    paper = Raphael("mapDiv", holderWidth, holderHeight);
    var holder = document.getElementById("mapDiv");
    holder.style.height = holderHeight + "px";
    holder.style.width = holderWidth + "px";
}

function GetSystemX(system) {
    if (system) {
        var startX = s(70);
        return startX + indentX * system.LevelX;
    } else {
        alert("GetSystemX: System is null or undefined");
    }
}

function GetSystemY(system) {
    if (system) {
        var startY = s(40);
        return startY + indentY * system.LevelY;
    } else {
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
    switch (system.SysClass) {
        case 7:
            classString = "H";
            break;
        case 8:
            classString = "L";
            break;
        case 9:
            classString = "N";
            break;
        case 12:
            classString = "T";
            break;
        case 13:
            classString = "SS";
            break;
        default:
            classString = "C" + system.SysClass;
            break;
    }
    var effectString;
    switch (system.effect) {
        case "Wolf-Rayet Star":
            effectString = "+W"
            break;
        case "Pulsar":
            effectString = "+P"
            break;
        case "Magnetar":
            effectString = "+M"
            break;
        case "Red Giant":
            effectString = "+R"
            break;
        case "Cataclysmic Variable":
            effectString = "+C"
            break;
        case "Black Hole":
            effectString = "+B"
            break;
        default:
            effectString = "";
            break;
    }
    var friendly = "";
    if (system.Friendly) {
        if (system.Friendly.length > 6) {
            if ((sliceLastChars == true) || (zenMode)) {
                system.Friendly = "." + system.Friendly.slice(-6);
            } else {
                system.Friendly = system.Friendly.slice(0, 6) + ".";
            }
        }
        friendly = system.Friendly + "\n";
    }
    var sysName = friendly + system.Name + "\n" + classString + effectString + "(" + system.activePilots + ")";
    if (zenMode) {
        if ((classString == "H") || (classString == "N") || (classString == "L") || (classString == "T")) {
            sysName = friendly + system.Name.substr(0,6);
        } else {
            sysName = friendly + classString;
        }
    }
    var pilotText = "";
    var pilotsadded = 0;
    if (system.activePilots) {
        if (system.activePilots == 1) {
            pilotText += system.pilot_list[0];
        } else {
            for (var i = 0; i < system.pilot_list.length; i++) {
                var pilot = system.pilot_list[i].substr(0,5);
                pilotsadded++;
                if (pilotText != "") pilotText += ",";
                pilotText += pilot;
                if (pilotText.length > 18) {
                    if  (system.pilot_list_length > pilotsadded) {
                        pilotText += "+" + (system.pilot_list.length - pilotsadded);
                    }
                    break;
                }
            }
        }
    }
    var sysText;
    if (system.LevelX != null && system.LevelX > 0) {
        var childSys = paper.ellipse(sysX, sysY, s(40), s(28));
        if (system.activePilots > 0 && highlightActivePilots === true) {
            var notificationRing = paper.ellipse(sysX, sysY, s(45), s(33));
            notificationRing.attr({'stroke-dasharray': '--', 'stroke-width': s(1), 'stroke': '#ffffff'});
        }
        childSys.msID = system.msID;
        childSys.whID = system.whID;
        childSys.sysID = system.sysID;
        childSys.WhFromParentBubbled = system.WhFromParentBubbled;
        childSys.WhToParentBubbled = system.WhToParentBubbled;
        childSys.click(onSysClick);

        // Don't even get me started...
        if (system.backgroundImageURL) {
            paper.image(system.backgroundImageURL, childSys.attr("cx") - s(28), childSys.attr("cy") - s(28), s(55), s(55));
        }
        sysText = paper.text(sysX, sysY, sysName);
        sysText.attr({"font-weight": 'bold'}); 
        sysText.msID = system.msID;
        sysText.sysID = system.sysID;
        sysText.click(onSysClick);
        if (is_igb === true) {
            childSys.dblclick(onSysDblClick);
            sysText.dblclick(onSysDblClick);
        }
        if (showPilotList) {
            pilotText = paper.text(sysX, sysY+s(32), pilotText);
            pilotText.msID = system.msID;
            pilotText.sysID = system.sysID;
            pilotText.click(onSysClick);
        } else {
            pilotText = null;
        }
        ColorSystem(system, childSys, sysText, pilotText);
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
            if (system.interestpath === true || system.interest === true) {
                interest = true;
            }
            if (childSys.collapsed === false || renderCollapsedConnections === true) {
                ConnectSystems(parentSysEllipse, childSys, lineColor, "#fff", interest, dasharray);
                DrawWormholes(parentSys, system, whColor);
            }
        } else {
            alert("Error processing system " + system.Name);
        }
    } else {
        var rootSys = paper.ellipse(sysX, sysY, s(40), s(30));
        rootSys.msID = system.msID;
        rootSys.sysID = system.sysID;
        // Don't even get me started...
        if (system.backgroundImageURL) {
            paper.image(system.backgroundImageURL, rootSys.attr("cx") - s(28), rootSys.attr("cy") - s(28), s(55), s(55));
        }
        rootSys.click(onSysClick);
        sysText = paper.text(sysX, sysY, sysName);
        sysText.attr({"font-weight": 'bold'}); 
        sysText.msID = system.msID;
        sysText.sysID = system.sysID;
        sysText.click(onSysClick);
        if (is_igb === true) {
            rootSys.dblclick(onSysDblClick);
            sysText.dblclick(onSysDblClick);
        }
        if (showPilotList) {
            pilotText = paper.text(sysX, sysY+s(35), pilotText);
            pilotText.msID = system.msID;
            pilotText.sysID = system.sysID;
            pilotText.click(onSysClick);
        } else {
            pilotText = null;
        }
        ColorSystem(system, rootSys, sysText, pilotText);
        objSystems.push(rootSys);
    }
}

function GetConnectionDash(system) {
    var eolDash = "-";
    var interestDash = "--";
    if (system.WhTimeStatus == 1) {
        return eolDash;
    }
    if (system.interestpath == true || system.interest == true) {
        return interestDash;
    }
    return "none";
}

function GetConnectionColor(system) {
    if (!system) {
        return "#000";
    }
    if (system.LevelX < 1) {
        return "#000";
    }
    var badFlag = false;
    var warningFlag = false;
    if (system.WhMassStatus == 2) {
        badFlag = true;
    }
    if (system.WhMassStatus == 1) {
        warningFlag = true;
    }
    if (badFlag == true) {
        return badColor;
    }
    if (warningFlag == true) {
        return warningColor;
    }
    if (system.WhTimeStatus == 1) {
        return eolColor;
    }
    // If jump mass is not 0 (K162 / Gate), but less than 10M,
    // we have a Hyperion frigate-sized hole
    if (0 < system.WhJumpMass && system.WhJumpMass < 10000000) {
        if (zenMode) {
            return frigWhColor_zen;
        } else {
            return frigWhColor;
        }
    }
    if (zenMode) {
        return goodColor_zen;
    } else {
        return goodColor;
    }
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
    if (system.WhToParentBubbled == true && system.WhFromParentBubbled == true) {
        return badColor;
    } else {
        return goodColor;
    }
}

function ColorSystem(system, ellipseSystem, textSysName, textPilot) {
    if (!system) {
        alert("system is null or undefined");
        return;
    }
    var selected = false;
    var sysColor = "#f00";
    var sysStroke = "#fff";
    var sysStrokeWidth = s(2);
    var sysStrokeDashArray = "none";
    var textColor = "#000";
    if (system.interest == true) {
        sysStrokeWidth = s(7);
        sysStrokeDashArray = "--";
    }
    if (system.msID === focusMS) {
        textColor = "#f0ff00";
        if (system.interest) {
            sysStrokeWidth = s(7);
        } else {
            sysStrokeWidth = s(4);
        }
        sysStrokeDashArray = "- ";
    }

    // not selected
    switch (system.SysClass) {
        // Null
        case 9:
            sysColor = colorNullSec; 
            sysStroke = borderColorNullSec; 
            textColor = systemTextColor;
            break;
        // Low
        case 8:
            sysColor = colorLowSec ;
            sysStroke = borderColorLowSec; 
            textColor = systemTextColor;
            break;
        // High
        case 7:
            sysColor = colorHighSec; 
            sysStroke = borderColorHighSec; 
            textColor = systemTextColor;
            break;
         case 6:
            sysColor = colorC6; 
            sysStroke = WormholeEffectColor(system,borderColorC6);
            if ((sysStroke != borderColorC6) && (!zenMode)) sysStrokeWidth = s(4);
            textColor = systemTextColor;
            break;
         case 5:
            sysColor = colorC5; 
            sysStroke = WormholeEffectColor(system,borderColorC5);
            if ((sysStroke != borderColorC5) && (!zenMode)) sysStrokeWidth = s(4);
            textColor = systemTextColor;
            break; 
        case 4:
            sysColor = colorC4; 
            sysStroke = WormholeEffectColor(system,borderColorC4);
            if ((sysStroke != borderColorC4) && (!zenMode)) sysStrokeWidth = s(4);
            textColor = systemTextColor;
            break;
        case 3:
            sysColor = colorC3;
            sysStroke = WormholeEffectColor(system,borderColorC3);
            if ((sysStroke != borderColorC3) && (!zenMode)) sysStrokeWidth = s(4);
            textColor = systemTextColor;
            break;
         case 2:
            sysColor = colorC2;
            sysStroke = WormholeEffectColor(system,borderColorC2);
            if ((sysStroke != borderColorC2) && (!zenMode)) sysStrokeWidth = s(4);
            textColor = systemTextColor;
            break;
         case 1:
            sysColor = colorC1; 
            sysStroke = WormholeEffectColor(system,borderColorC1);
            if ((sysStroke != borderColorC1) && (!zenMode)) sysStrokeWidth = s(4);
            textColor = systemTextColor; 
            break;
         // Thera
         case 12:
            sysColor = colorThera; 
            sysStroke = borderColorThera;
            textColor = systemTextColor;
            break;
         // Small Ship Hole
         case 13:
            sysColor = colorSmallShipHole; 
            sysStroke = borderColorSmallShipHole; 
            textColor = systemTextColor;
            break;
        default:
            sysColor = "#000";
            sysStroke = "#fff";
            textColor = systemTextColor;
            break;
    }


    if (system.shattered) {
        if (shatteredBorderColor != null) {
            sysStroke = shatteredBorderColor; 
        }
        if (sysStrokeWidth < s(3)) {
            sysStrokeWidth = s(3);
        }
        sysStrokeDashArray = "- ";
    }
    var labelFontSize = textFontSize;
    if (zenMode) {
        textColor = sysColor;
        sysColor = sysColor_zen;
        labelFontSize = s(16);
    }
    if (system.msID === focusMS) {
        if (zenMode) {
            textColor = textColorSelect_zen; 
            sysStroke = borderColorSelect_zen;
        } else {
            textColor = textColorSelect;
            sysStroke = borderColorSelect;
        }
        sysStrokeDashArray = "--"
    }
    var iconX = ellipseSystem.attr("cx")+s(40);
    var iconY = ellipseSystem.attr("cy")-s(35);
    if (system.iconImageURL) {
        paper.image(system.iconImageURL, iconX, iconY, 25, 25);
    }
    ellipseSystem.attr({
        fill: sysColor,
        stroke: sysStroke,
        "stroke-width": sysStrokeWidth,
        cursor: "pointer",
        "stroke-dasharray": sysStrokeDashArray
    });
    textSysName.attr({fill: textColor, "font-size": labelFontSize, cursor: "pointer"});
    if (textPilot != null) textPilot.attr({fill: pilotColor, "font-size": textFontSize-s(1), cursor: "pointer"});



    if (selected == false) {
        ellipseSystem.sysInfoPnlID = 0;
        textSysName.sysInfoPnlID = 0;

        ellipseSystem.hover(onSysOver, onSysOut);
        textSysName.ellipseIndex = objSystems.length;
        textSysName.hover(onSysOver, onSysOut);
    }
}

/*
 * Colors wormhole systems by effect.
 */
function WormholeEffectColor(system, defaultcolor) {
    switch (system.effect) {
        case "Wolf-Rayet Star":
            return effectColorWolfRayet;
            break;
        case "Pulsar":
            return effectColorPulsar;
            break;
        case "Magnetar":
            return effectColorMagnetar;
            break;
        case "Red Giant":
            return effectColorRedGiant;
            break;
        case "Cataclysmic Variable":
            return effectColorCataclysmic;
            break;
        case "Black Hole":
            return effectColorBlackHole;
            break;
        default:
            return defaultcolor;
            break;
    }
}

// Currently unused, needs implementation.
function GetBorderColor(startR, startB, startG, endR, endB, endG, system) {
    var diffR, diffB, diffG, factor, newR, newB, newG;
    diffR = startR - endR;
    diffB = startB - endB;
    diffG = startG - endG;
    factor = system.activity / activityLimit;
    if (factor < 1) {
        newR = startR - (diffR * factor);
        newB = startB - (diffB * factor);
        newG = startG - (diffG * factor);
    } else {
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
    textCenterX = textCenterX + s(10);
    var textCenterY = (sysY1 + sysY2) / 2;

    var whFromSysX = textCenterX;
    var whFromSysY = textCenterY;

    var whToSysX = textCenterX;
    var whToSysY = textCenterY;

    if (sysY1 != sysY2) {
        textCenterX = textCenterX - s(10);
        whFromSysX = textCenterX + s(23);
        whToSysX = textCenterX - s(23);
    } else {
        whFromSysY = textCenterY - s(10);
        whToSysY = textCenterY + s(10);
    }

    // draws labels near systemTo ellipse if previous same Level X system's levelY = systemTo.levelY - 1
    if (!zenMode) {
        if (changePos == true) {

            textCenterX = sysX2 - s(73);
            textCenterY = sysY2 - s(30);
            if (renderWormholeTags) {
                whFromSysX = textCenterX + s(23);
                whToSysX = textCenterX - s(23);
            } else {
                whFromSysX = textCenterX + s(35);
                whToSysX = textCenterX - s(10);
            }
            whFromSysY = textCenterY;
            whToSysY = textCenterY;
        }

        var whFromSys = null;
        var whToSys = null;
        var whFromColor = null;
        var whToColor = null;
        var decoration = null;

        if (systemTo.WhFromParentBubbled == true) {
            whFromColor = bubbledColor;
            decoration = "bold";
        } else {
            whFromColor = clearWhColor;
        }

        if (systemTo.WhToParentBubbled == true) {
            whToColor = bubbledColor;
            decoration = "bold";
        } else {
            whToColor = clearWhColor;
        }

        if (systemTo.WhFromParent) {
            var whFromText, whToText;
            if (!renderWormholeTags) {
                whFromText = ">";
                whToText = "<";
            } else {
                whFromText = systemTo.WhFromParent + " >";
                whToText = "< " + systemTo.WhToParent;
            }

            whFromSys = paper.text(whFromSysX, whFromSysY, whFromText);
            whFromSys.attr({fill: whFromColor, cursor: "pointer", "font-size": s(11), "font-weight": decoration});  //stroke: "#fff"
            whFromSys.click(function () {
                GetEditWormholeDialog(systemTo.whID);
            });
            whFromSys.whID = systemTo.whID;
            whFromSys.mouseover(onWhOver);
            whFromSys.mouseout(onWhOut);
        }

        if (systemTo.WhToParent) {
            whToSys = paper.text(whToSysX, whToSysY, whToText);
            whToSys.attr({fill: whToColor, cursor: "pointer", "font-size": s(11), "font-weight": decoration});

            whToSys.whID = systemTo.whID;
            whToSys.click(function () {
                GetEditWormholeDialog(systemTo.whID);
            });
            whToSys.mouseover(onWhOver);
            whToSys.mouseout(onWhOut);
        }
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
    var index = -1;
    for (var i = 0; i < stellarSystemsLength; i++) {
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
    var scrOfY = 0;
    if (typeof (window.pageYOffset) == 'number') {
        //Netscape compliant
        scrOfY = window.pageYOffset;
    } else if (document.body && (document.body.scrollLeft || document.body.scrollTop)) {
        //DOM compliant
        scrOfY = document.body.scrollTop;
    } else if (document.documentElement && (document.documentElement.scrollLeft || document.documentElement.scrollTop)) {
        //IE6 standards compliant mode
        scrOfY = document.documentElement.scrollTop;
    }
    return scrOfY;
}

function getScrollX() {
    var scrOfX = 0;
    if (typeof (window.pageYOffset) == 'number') {
        //Netscape compliant
        scrOfX = window.pageXOffset;
    } else if (document.body && (document.body.scrollLeft || document.body.scrollTop)) {
        //DOM compliant
        scrOfX = document.body.scrollLeft;
    } else if (document.documentElement && (document.documentElement.scrollLeft || document.documentElement.scrollTop)) {
        //IE6 standards compliant mode
        scrOfX = document.documentElement.scrollLeft;
    }
    return scrOfX;
}

function onSysClick() {
    DisplaySystemDetails(this.msID, this.sysID);
    var div = $('#sys' + this.msID + "Tip").hide();

    if (div[0]) {
        div.hide();
    }
}

function onSysDblClick() {
    CCPEVE.showInfo(5, this.sysID);
}

function onWhOver(e) {
    var div = $('#wh' + this.whID + "Tip");

    if (div[0]){
        var mouseX = e.clientX + getScrollX();
        var mouseY = e.clientY + getScrollY();

        div.css({position: "absolute", top: mouseY + 20 + "px", left: mouseX + 20 + "px"});
        div.show();
    }
}

function onWhOut() {
    var div = $('#wh' + this.whID + "Tip");

    if (div[0]) {
        div.hide();
    }
}

function onSysOver(e) {
    var div = $('#sys' + this.msID + "Tip");
    if (div[0]){
        var mouseX = e.clientX + getScrollX();
        var mouseY = e.clientY + getScrollY();

        div.css({position: "absolute", top: mouseY + 20 + "px", left: mouseX + 20 + "px"});
        div.show();
    }
}

function onSysOut() {
    var div = $('#sys' + this.msID + "Tip");

    if (div[0]){
        div.hide();
    }
}

function scale(factor) {
    scalingFactor = factor;
    textFontSize = s(11); // The base font size
    indentX = s(150); // The amount of space (in px) between system ellipses on the X axis. Should be between 120 and 180
    indentY = s(70); // The amount of space (in px) between system ellipses on the Y axis.
    strokeWidth = s(3); // The width in px of the line connecting wormholes
    interestWidth = s(3); // The width in px of the line connecting wormholes when interest is on
    RefreshMap();
}

function togglezen() {
    if (zenMode == true) {
        zenMode = false;
        $('#btnZen').text("Zen: OFF");
    } else {
        zenMode = true;
        $('#btnZen').text("Zen: ON");
    }
    RefreshMap();
}

function togglepilotlist() {
    if (showPilotList == true) {
        showPilotList = false;
        highlightActivePilots = true;
        $('#btnPilotList').text("Pilot List: OFF");
    } else {
        showPilotList = true;
        highlightActivePilots = false;
        $('#btnPilotList').text("Pilot List: ON");
    }
    RefreshMap();
}
