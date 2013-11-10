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
    GetTSProfSettingsForm();
});

function GetTSProfSettingsForm(){
    $.ajax({
        type: "GET",
        url: "/teamspeak/user_profile/",
        success: function(data){
            $('#TSProfSettingsHolder').html(data);
        }
    });
}

function RequestToken(tsserverid){
    $.ajax({
        type: "POST",
        data: { serverid: tsserverid },
        url: "/teamspeak/settings/generate_token/",
        success: window.location.href = "/settings/"
    });
}
