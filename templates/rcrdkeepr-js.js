$('.sub').click(function(e){
    e.preventDefault()
    $('.new_record').ajaxSubmit({
        success: function(r){
            console.log(r)
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