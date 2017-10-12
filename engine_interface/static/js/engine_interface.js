/**
 * Document Ready Function
 * - Sets the handler for the input box dropdown (AND/OR)
 * - Define event handler for input search box
 */
$(function () {

    $(".dropdown-opts.dropdown-menu > li").click(function () {
        var search_btn = $(".input-search-box > button.dropdown-toggle");
        search_btn.text($(this).text());
        search_btn.val($(this).text());
    });


    $("#ipt-search-box").on('keyup', function (e) {
        if (e.keyCode === 13) {
            search_collect();
        }
    });

});

/**
 * Function to process query
 * - Perform validation for the query
 * - AJAX request to search the index
 */
function search_collect(){

    var query = $("#ipt-search-box").val().trim();

    if(query.length <= 0){
        msg_modal_setup("No Query Entered", "Please enter a valid query.");
        return false;
    }

    var query_time = new Date().getTime();
    var results_contn = $("#results-container");
    $.ajax({
        url: 'search_query',
        method: 'GET',
        data: {
            query_string: query,
            option: $(".input-search-box > button.dropdown-toggle").val()
        },
        beforeSend: function(){
            $("#search-btn").hide();
            $("#loading-img").show();
        },
        success: function(results_data){
            results_contn.find("div.container-body").first().html($.parseHTML(results_data));
            results_contn.show();
            scroll_to_container("#results-container");
            $("#results-details > span.time").text((new Date().getTime() - query_time)/1000 + "s");
            $("#results-details > span.doc-no-retrieved").text($("#tbl-results tr").length);
        },
        error: function(err){
            results_contn.hide();
            msg_modal_setup("Error while processing query", err.responseText);
        },
        complete: function(){
            $("#loading-img").hide();
            $("#search-btn").show();
        }
    });

}

/**
 * Method called when click on document title to show complete doc body
 * @param doc_id - doc id to fetch complete text
 */
function expand_doc(doc_id){

    var doc_row = $("#reuters-doc-" + doc_id).find("td").first();

    var doc_title = doc_row.find("div.doc-title").first().clone();
    doc_title.find("span.doc-date").first().remove();
    $("#doc-modal-title").html(doc_title.html());
    $("#doc-modal-date").html(doc_row.find("span.doc-date").first().html());
    $("#doc-modal-text").html(doc_row.find("div.doc-body").first().html());

    $("#doc-modal").modal("show");

}

/**
 * Sets the message modal through passed parameters
 * @param msg_title - Title for the modal
 * @param msg_message - Message body for the modal
 * @param msg_icon_class - Font-Awesome icon class to user (default = fa-warning )
 */
function msg_modal_setup(msg_title, msg_message, msg_icon_class){

    $("#msg-title").text(msg_title);
    $("#msg-text").text(msg_message);

    var msg_icon_obj = $("#msg-icon > i");

    // Check if an icon class was added previously
    var obj_classes = msg_icon_obj.attr('class').split(' ');
    if (obj_classes.length > 1){
        msg_icon_obj.removeClass(obj_classes.pop());
    }

    if(msg_icon_class === undefined || msg_icon_class === ""){
        msg_icon_obj.addClass("fa-warning");
    }else{
        msg_icon_obj.addClass(msg_icon_class);
    }

    $("#msg-modal").modal('show');

}

function scroll_to_container(container_selector){
    $('html, body').animate({
        scrollTop: $(container_selector).offset().top
    }, 700);
}