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

function SubmitTSProfSettingsForm(){
    $.ajax({
        type: "POST",
        data: $('#TSProfSettingsForm').serialize(),
        url: "/teamspeak/user_profile/",
        success: function(data){
            $('#TSProfSettingsHolder').html(data);
        }
    });
}
