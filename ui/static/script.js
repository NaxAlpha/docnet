
window.data = []

$('form').on('submit', function (e) {
    e.preventDefault();
    $("#btn-submit").attr("disabled", true);

    $.ajax({
      type : 'POST',
      url : '/create',
      data: new FormData($('form')[0]),
      processData: false,
      contentType: false,
      success: function (data) {
        $("#btn-submit").attr("disabled", false);
        window.data.push({status: false, id: data.id, class: 'UNKNOWN', score: 0});
        window.setTimeout(update_status, 500);
    }})
});


function render() {
    output = ''
    seg0 = '<li class="list-group-item" onclick="item_click('
    seg1 = ');"><div class="md-v-line"></div><i class="fas '
    seg2 = ' mr-4 pr-3"></i><code>'
    seg3 = '</li>'
    idx = 0
    for (var entry of window.data){
        if(entry.status)
            icon = 'fa-check'
        else
            icon = 'fa-spinner'
        output += seg0 + idx + seg1 + icon + seg2 + entry.id + '</code> | ' + entry.class + ' (' + entry.score + ')' + seg3
        idx += 1
    }
    $('#queue').html(output)
}


function item_click(idx){
    $('img').attr('src', '/serve/' + window.data[idx].id)
}

function update_status() {
    idx = 0
    to_check = {}
    for(var item of window.data){
        if(!item.status)
            to_check[item.id] = idx
        idx += 1
    }
    ids = Object.keys(to_check)
    if(ids.length==0)
        return
    $.post('/status', JSON.stringify(ids), function(data) {
        for (var entry of data) {
            window.data[to_check[entry.id]] = entry
        }
        update_status();
    })
}

$(document).ready(function(){
    window.setInterval(render, 500)
})