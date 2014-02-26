$('.sub').click(function(e){
    e.preventDefault()
    var artist = $(this).parents('div.record_input').find('#artist').val()
    var album = $(this).parents('div.record_input').find('#album').val()

    if($('.albums').find('table.list').attr('class') !== undefined){
        $('.new_record').attr('action', '/submit/list')

        $('.new_record').ajaxSubmit({
            success: function(data){
                $('.list tr:last').after(data)
                $('.data').empty()
                $('.data').append(artist + ' - ' + album)
                $('.record_added').fadeIn('slow').delay(3000).fadeOut('slow')
            }
        })
    }
    else{
        $('.new_record').ajaxSubmit({
            success: function(data){
                $('.albums').append(data)
                $('.data').empty()
                $('.data').append(artist + ' - ' + album)
                $('.record_added').fadeIn('slow').delay(3000).fadeOut('slow')
            }
        })
    }
})

$(document).on('dblclick', '.get_details', function(){
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
            window.location.reload()
        }
    })
})

$(document).on('click' ,'.delete', function(){
    var conf = confirm('Are you sure you want to delete?')

    if (conf == true){
        var record_id = $(this).parents('div:first').attr('id')
        $(this).parents('div').parents('div:first').remove()

        $.post('/delete/' + record_id, function(data){
            $('.data').empty()
            $('.data').append(data)
            $('.record_deleted').fadeIn('slow').delay(3000).fadeOut('slow')
        })        
    }
})

$(document).on('click' ,'.delete_from_list', function(){
    var conf = confirm('Are you sure you want to delete?')

    if (conf == true){
        var record_id = $(this).parents('tr').attr('id')
        $(this).parents('tr').slideToggle('slow')
        $.ajax({
            url: '/delete/' + record_id,
            type: 'post'
        })
        $.post('/delete/' + record_id, function(data){
            $('.data').append(data)
        })

        $('.data').empty()
        $('.record_deleted').fadeIn('slow').delay(3000).fadeOut('slow')
    }
})

$(document).ready(function(){
    $('#record_search').select2({ maximumSelectionSize: 1 }) 
})

$('#album').prop('disabled', true)

$(document).ready(function(){
    $('#album').select2({
        data:[
        ]
    })
})

$('#record_search').change(function(){
    var artist = $('#record_search option:selected').val()
    $.get('/get_records/1/' + artist, function(data){
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
    console.log(passwordVal.length)
    console.log('hi')
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
    } else if (passwordVal.length < 8){
        $('#register_password').after('<span class="error">Password most be at least 8 characters.</span>')
        hasError = true
    } else if (hasError == true){
        return false
    }
    if(hasError == true) {return false}
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

    $('body').css('cursor', 'progress')
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
                $('#album').select2({
                    data: options,
                    createSearchChoice:function(term, data) {
                        if ($(data).filter(function() {
                            return this.text.localeCompare(term)===0; }).length===0) {
                                return {id:term, text:term};
                            }
                        },
                })
                $('#album').prop('disabled', false)
            })
            $('body').css('cursor', 'default');
        }
    })
})

//pagination
$('.next').click(function(e){
    e.preventDefault()
    var page = $('.link_next').attr('href').replace('/home/','')
    page++

    $.get('/get_records/' + page, function(data){
        $('.albums').empty()
        $('.albums').append(data)
    })
})

$('.previous').click(function(){
    var page = $('.link_previous').attr('href').replace('/home/','')
    page--
    
    $.get('/get_records/' + page, function(data){
        $('.albums').empty()
        $('.albums').append(data)
    })
})

$('.pagination .disabled a, .pagination .active a').on('click', function(e) {
    e.preventDefault()
})

$(document).on('click', '.list_view', function(e){
    e.preventDefault()

    $('.refresh').addClass('list')

    $.get('/list_records', function(data){
        $('.albums').empty()
        $('.albums').append(data)
        $(document).ready(function(){
            //$('.view_holder').empty()
            $('.controls').children('.view').remove()
            $('.controls').append('<button type="button" class="view grid_view btn btn-default btn-ms"> \
                    <span class="glyphicon glyphicon-th"></span> \
                </button>')
        })
    })
})

$(document).on('click', '.grid_view', function(e){
    e.preventDefault()

    $.get('/get_records/1', function(data){
        $('.albums').empty()
        $('.albums').append(data)
        //$('.view_holder').empty()
        $('.controls').children('.view').remove()
        $('.controls').append('<button type="button" class="view list_view btn btn-default btn-ms"> \
                <span class="glyphicon glyphicon-list"></span> \
            </button>')
    })
})

$(document).on('click', '.refresh', function(e){
    e.preventDefault()

    if(($(this).hasClass('list'))){
        $.get('/list_records', function(data){
            $('.albums').empty()
            $('.albums').append(data)
            $(document).ready(function(){
                //$('.view_holder').empty()
                $('.controls').children('.view').remove()
                $('.controls').append('<button type="button" class="view grid_view btn btn-default btn-ms"> \
                        <span class="glyphicon glyphicon-th"></span> \
                    </button>')
            })
        })
    }
    else{
        $.get('/get_records/1', function(data){
            $('.albums').empty()
            $('.albums').append(data)
        })
    }
})

$(document).on('click', '#contact_sub', function(e){
    e.preventDefault()
    var data = {}
    var that = $(this).parents('.contact').find('select')

    $.each($(this).parents('.contact').find('input'), function(){
        data[$(this).attr('id')] = $(this).val()
    })
    data[that.attr('id')] = that.val()

    $.post('/contact', data, function(){
        $('.messages').append('<div class="alert alert-success alert-dismissable">Thank you for contacting us we will response as soon as we can.</div>')
    })
})

$(document).on('click', '.add', function(){
    $('#input').removeClass('hidden-xs')
    $('.new_record').css('visibility','visible').hide().fadeIn('slow')
    $(this).remove()
    $('.add_button').append('<button class="btn btn-default btn-md hide_add"><span class="glyphicon glyphicon-minus"></span></button>')
})

$(document).on('click', '.hide_add', function(){
    $('.new_record').fadeOut('slow')
    $(this).remove()
    $('.add_button').append('<button class="btn btn-default btn-md add"><span class="glyphicon glyphicon-plus"></span></button>')
})
