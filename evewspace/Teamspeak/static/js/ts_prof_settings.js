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
