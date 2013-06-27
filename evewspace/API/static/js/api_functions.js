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

function GetAPIKeyDialog(){
    $.ajax({
        url: '/api/key/',
        type: 'GET',
        success: function(data){
            $('#modalHolder').empty().html(data).modal('show');
            GetNewAPIKeyForm();
        }
    });
}

function GetNewAPIKeyForm(){
    $.ajax({
        url: '/api/key/new/',
        type: 'GET',
        success: function(data){
            $('#apiKeyFormHolder').html(data);
        }
    });
}

function SaveAPIKey(key_id){
    $.ajax({
        url: '/api/key/' + key_id + '/edit/',
        type: 'POST',
        data: $('#apiKeyForm').serialize(),
        success: function(data){
            GetAPIKeyDialog();
        }
    });
}

function SaveNewAPIKey(){
    $.ajax({
        url: '/api/key/new/',
        type: 'POST',
        data: $('#apiKeyForm').serialize(),
        success: function(data){
            GetAPIKeyDialog();
        }
    });
}

function APIEditKey(key_id){
    $.ajax({
        url: '/api/key/' + key_id + '/edit/',
        type: 'GET',
        success: function(data){
            $('#apiKeyFormHolder').html(data);
        }
    });
}

function APIDeleteKey(key_id){
    $.ajax({
        url: 'api/key/' + key_id + '/delete/',
        type: 'POST',
        success: function(data){
            GetAPIKeyDialog();
        }
    });
}
