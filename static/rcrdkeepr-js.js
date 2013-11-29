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
    console.log(id)
    $('#infoModal' + id).modal('show')
})
