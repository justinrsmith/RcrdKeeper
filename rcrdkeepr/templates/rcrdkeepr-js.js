$('.sub').click(function(e){
    e.preventDefault()
    console.log('hi')
    $('.new_record').ajaxSubmit({
        success: function(r){
            console.log(r)
            $('.albums').append(r)
            $('.messages').empty()
            $('.messages').addClass('alert alert-success alert-dismissable')
            $('.messages').append('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>Record Successfully Added')
        },
        error: function(e){
            console.log(e)
        }
    })
})

$(document).on('dblclick', '.get_details', function(){
    var id = $(this).attr('id')
    $('#infoModal' + id).modal('show')
})

$('.get_details').tooltip({trigger: 'hover'})

$('.save_edit').click(function(e){
    e.preventDefault()
    console.log('hi')
    var id = $(this).attr('id')
    $(this).parents('.edit_record').ajaxSubmit({
        success: function(data){
            $('.'+id).attr('src', data)
            window.location.reload()
        },
        error: function(e){
            //console.log(e)
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
        $('.messages').empty()
        $('.messages').append('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>Record Successfully Deleted')
    }
    else {
        console.log('dont delete')
    }
})

$(document).ready(function(){
    $('#record_search').select2({ maximumSelectionSize: 1 }) 
})

$(document).ready(function(){
    $("#album").select2({
        data:[
        ],
        width: '200px'
    })
})

$('.search').click(function(){
    var artist = $('#record_search option:selected').val()
    $.get('/get_records/' + artist, function(data){
        $('.albums').empty()
        $('.albums').append(data)
    })
})

$(document).on('click', '.register', function(e){
    var hasError = false
    var passwordVal = $('#register_password').val()
    var checkVal = $('#verify_password').val()
    var pattern = new RegExp(/^[+a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/i)
    var email = $(this).parent().siblings().children('.email').children('input')
    var valid_email = pattern.test(email.val())
    var form = $(this).parent('div').attr('id')
    console.log(form)

    $('.error').hide()
    if (passwordVal == '') {
        $('#register_password').after('<span class="error">Please enter a password.</span>')
        hasError = true
    } else if (checkVal == '') {
        $('#verify_password').after('<span class="error">Please re-enter your password.</span>')
        hasError = true
    } else if (passwordVal != checkVal) {
        $('#verify_password').after('<span class="error">Passwords do not match.</span>')
        hasError = true
    } else if (valid_email != true && form != 'reset_register') {
        $(email).after('<span class="error">Please enter a valid email.</span>')
        hasError = true
    } else if (hasError == true){
        return false
    } else {
        ('.messages').empty()
        $('.messages').addClass('alert alert-success alert-dismissable')
        $('.messages').append('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>Registration successful you will shortly receive a confirmation email for your records.')
    }
    //if(hasError == true) {return false}
})

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

$('#artist').change(function(){
    var artist = $(this).val()
    console.log(artist)

    $.ajax({
        url: '/get_albums/' + artist,
        type: 'GET',    
        data: artist,
        success: function(data){
            var length = (data.albums.length)
            var options = []

            for(var i=0; i < length; i++){
                options.push(data.albums[i])
            }
            options.sort(function(a,b){
                var textA = a.text.toUpperCase()
                var textB = b.text.toUpperCase()
                return (textA < textB) ? -1 : (textA > textB) ? 1 : 0
            })
            $(document).ready(function(){
                $("#album").select2({
                    data: options,
                    createSearchChoice:function(term, data) {
                        if ($(data).filter(function() {
                            return this.text.localeCompare(term)===0; }).length===0) {
                                return {id:term, text:term};
                            }
                        },
                })
            })
        }
    })
})

//pagination
$('.next').click(function(){
    
    var page = $('.link_next').attr('href').replace('/home/','')
    page++
    console.log(page)
    $('.link_next').attr('href', '/home/' + page)
})

$('.previous').click(function(){
    var page = $('.link_previous').attr('href').replace('/home/','')
    page--
    console.log(page)
    $('.link_previous').attr('href', '/home/' + page)
})

$('.pagination .disabled a, .pagination .active a').on('click', function(e) {
    e.preventDefault()
})
