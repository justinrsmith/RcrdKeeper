$('.sub').click(function(e){
    e.preventDefault()
    console.log('hi')
    $('.new_record').ajaxSubmit({
        success: function(r){
            $('.albums').append(r)
            $('.messages').addClass('alert alert-success alert-dismissable')
            $('.messages').append('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>Record Successfully Added')
        },
        error: function(e){
            console.log(e)
        }
    })
})

$('.get_details').dblclick(function(){
    var id = $(this).attr('id')
    $('#infoModal' + id).modal('show')
})

$('.get_details').tooltip({trigger: 'hover'})

$('.save_edit').click(function(e){
    e.preventDefault()
    var id = $(this).attr('id')
    $(this).parents('.edit_record').ajaxSubmit({
        success: function(data){
            $('.'+id).attr('src', data)
        },
        error: function(e){
            console.log(e)
        }
    })
})

$('.delete').click(function(){
    var conf = confirm('Are you sure you want to delete?')
    if (conf == true){
        var record_id = $(this).parents('div:first').attr('id')
        $(this).parents('div').parents('div:first').remove()
        $.ajax({
            url: '/delete/' + record_id,
            type: 'post'
        })
        $('.messages').addClass('alert alert-success alert-dismissable')
            $('.messages').append('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>Record Successfully Deleted')
    }
    else {
        console.log('dont delete')
    }
})

$(document).ready(function(){
    $('#record_search').select2({ maximumSelectionSize: 1 }) 
})


$('.search').click(function(){
    var artist = $('#record_search option:selected').val()
    $.get('/get_records/' + artist, function(data){
        $('.albums').empty()
        $('.albums').append(data)
    })
})

$('.register').click(function(){
        //$("#submit").click(function(){
        //$(".error").hide();
        console.log($("#register_password").val())
        var hasError = false;
        var passwordVal = $("#register_password").val();
        var checkVal = $("#verify_password").val();
        if (passwordVal == '') {
            $("#register_password").after('<span class="error">Please enter a password.</span>');
            hasError = true;
        } else if (checkVal == '') {
            $("#verify_password").after('<span class="error">Please re-enter your password.</span>');
            hasError = true;
        } else if (passwordVal != checkVal ) {
            $("#verify_password").after('<span class="error">Passwords do not match.</span>');
            hasError = true;
        }
        if(hasError == true) {return false;}
    });

$(function (){
    $("#example").popover()
})

$(document).on('click', '.forgot_pw', function(e){
    e.preventDefault()
    var email = {'email': $('#forgot_email').val()}

    $.ajax({
        url: '/forgot',
        type: 'POST',
        data: email,
        success: function(){
            console.log('did it')
        }
    })
})
/*
$('#artist').keyup(function(){
    console.log($(this).val())
})
*/