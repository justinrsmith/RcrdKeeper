$('.sub').click(function(e){
    e.preventDefault()
    var artist = $('#artist').val()
    var album = $('#album').val()

    if($('.albums').find('table.list').attr('class') !== undefined){
        $('.new_record').attr('action', '/submit/list')

        $('.new_record').ajaxSubmit({
            success: function(data){
                $('.list tr:last').after(data)
                $('.data').empty()
                $('.data').append(artist + ' - ' + album)
                $('.record_added').fadeIn('slow').delay(3000).fadeOut('slow')
                $('#artist').val('')
                $('#album').select2('data', null)
                $('#album').prop('disabled', true)
            }
        })
    }
    else{
        $('.new_record').ajaxSubmit({
            success: function(data){
                var that = $('.albums').append(data)
                $('.data').empty()
                $('.data').append(artist + ' - ' + album)
                $('.record_added').fadeIn('slow').delay(3000).fadeOut('slow')
                $('#artist').val('')
                $('#album').select2('data', null)
                $('#album').prop('disabled', true)
            }
        })
    }
})

$(document).on('click', '.get_details', function(){
    var id = $(this).attr('id')
    $('#infoModal' + id).modal('show')
})

$('.get_details').tooltip({trigger: 'hover'})

$(document).on('click', '.save_edit', function(e){
    e.preventDefault()
    var that = $(this)
    var id
    $(this).parents('.edit_record').ajaxSubmit({
        success: function(data){
            id = $(this).attr('id')
            $('.'+id).attr('src', data)
            if($(that).parents('div.modal').hasClass('list')){
                $.get('/list_records', function(data){
                    $('.albums').empty()
                    $('.albums').append(data)
                    $(document).ready(function(){
                        $('.view_controls').children('.view').remove()
                        $('.view_controls').append('<button type="button" class="view grid_view btn btn-default btn-ms"> \
                                <span class="glyphicon glyphicon-th"></span> \
                            </button>')
                    })
                })
            }
            else{
                $.get('/get_records/1', function(data){
                    $('.albums').empty()
                    $('.albums').append(data)
                    $('.view_controls').children('.view').remove()
                    $('.view_controls').append('<button type="button" class="view list_view btn btn-default btn-ms"> \
                            <span class="glyphicon glyphicon-list"></span> \
                        </button>')
                })
            }
            $('.data').empty()
            //$('.data').append(data)
            $('.record_edited').fadeIn('slow').delay(3000).fadeOut('slow')
        }
    })
    $('.modal').modal('hide')
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

    if($(this).hasClass('list')){
        $.get('/list_records/' + artist, function(data){
            $('.albums').empty()
            $('.albums').append(data)
            $(document).ready(function(){
                $('.view_controls').children('.view').remove()
                $('.view_controls').append('<button type="button" class="view grid_view btn btn-default btn-ms"> \
                        <span class="glyphicon glyphicon-th"></span> \
                    </button>')
            })
        })
    }
    else{
        $.get('/get_records/1/' + artist, function(data){
            $('.albums').empty()
            $('.albums').append(data)
        })
    }
})

$(document).on('click', '.register', function(e){
    var hasError = false
    var passwordVal = $('#register_password').val()
    var checkVal = $('#verify_password').val()
    var pattern = new RegExp(/^[+a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/i)
    var email = $(this).parent().siblings().children('.email').children('input')
    var valid_email = pattern.test(email.val())
    var form = $(this).parent('div').attr('id')

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
    $("#password_forgot").popover()
})

$(document).on('click', '.forgot_pw', function(e){
    e.preventDefault()
    var email = {'email': $('#forgot_email').val()}

    $.ajax({
        url: '/forgot',
        type: 'POST',
        data: email,
        success: function(){
        }
    })

    $('#password_forgot').popover('hide')
    $('.data').empty()
    $('.data').append(email['email'])
    $('.password_reset').fadeIn('slow').delay(3000).fadeOut('slow')
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

var page = 1

//pagination
$('.next').click(function(e){
    e.preventDefault()
    
    if($('.previous').hasClass('disabled')){
        $('.previous').removeClass('disabled')
    }
    if(!$(this).hasClass('disabled')){
        page++
        $.get('/get_records/' + page, function(data){
            $('.albums').empty()
            $('.albums').append(data)
            that = data
            $(that).find('div')
        })
    }
})

$('.previous').click(function(){
    if(!$(this).hasClass('disabled')){
        page--
        $.get('/get_records/' + page, function(data){
            $('.albums').empty()
            $('.albums').append(data)
        })
        if(page==1){
            $('.previous').addClass('disabled')
            $('.next').removeClass('disabled')
        }
    }
})

$(document).on('click', '.list_view', function(e){
    e.preventDefault()

    $('.refresh').addClass('list')

    $('#record_search').addClass('list')

    $('.paginate_holder').hide()

    $.get('/list_records', function(data){
        $('.albums').empty()
        $('.albums').append(data)
        $(document).ready(function(){
            $('.view_controls').children('.view').remove()
            $('.view_controls').append('<button type="button" class="view grid_view btn btn-default btn-ms"> \
                    <span class="glyphicon glyphicon-th"></span> \
                </button>')
        })
    })
})

$(document).on('click', '.grid_view', function(e){
    e.preventDefault()

    $('.paginate_holder').show()

    $('.refresh').removeClass('list')

    $.get('/get_records/1', function(data){
        $('.albums').empty()
        $('.albums').append(data)
        $('.view_controls').children('.view').remove()
        $('.view_controls').append('<button type="button" class="view list_view btn btn-default btn-ms"> \
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
                $('.view_controls').children('.view').remove()
                $('.view_controls').append('<button type="button" class="view grid_view btn btn-default btn-ms"> \
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
    if(!$('.search_moblie').hasClass('hide_add')){
        $('.search_moblie').addClass('hide_add')
        $('#record_search').parent('div').addClass('hidden-xs')
        $('#record_search').parent('div').fadeOut('slow')
        $(this).removeClass('hide_search')
        $('#record_search').parent('div').addClass('hidden-xs')
    }
    $('#welcome').remove()
    $('.new_record').css('height', 'auto')
    $('#input').removeClass('hidden-xs').children('div:first').removeClass('hidden-xs')
    $('.new_record').css('visibility','visible').hide().fadeIn('slow')
    $(this).removeClass('add')
    $(this).addClass('hide_add')
    $(this).children('span').remove()
    $(this).append('<span class="glyphicon glyphicon-minus"></span>')
})

$(document).on('click', '.hide_add', function(){
    $('.new_record').fadeOut('slow')
    $(this).removeClass('hide_add')
    $(this).addClass('add')
    $(this).children('span').remove()
    $(this).append('<span class="glyphicon glyphicon-plus"></span>')
})

$(document).on('click', '.search_mobile', function(){
    $('.new_record').hide()
    $('.hide_add').addClass('add')
    $('.hide_add').children('span').remove()
    $('.hide_add').append('<span class="glyphicon glyphicon-plus"></span>')
    $('.hide_add').removeClass('hide_add')
    
    if($(this).hasClass('hide_search')){
        $('#record_search').parent('div').addClass('hidden-xs')
        $('#record_search').parent('div').fadeOut('slow')
        $(this).removeClass('hide_search')
        $('#record_search').parent('div').addClass('hidden-xs')

    }
    else{
        $('#record_search').parents('div').removeClass('hidden-xs')
        $('#record_search').css('visibility','visible').hide().fadeIn('slow')
        $(this).addClass('hide_search')
    }
})


