/**
 * Document Ready Function
 * - Sets the handler for the input box dropdown (AND/OR)
 * - Sets smooth scrolling for all elements in the class smooth
 */
$(function () {

    $(".dropdown-opts.dropdown-menu > li").click(function () {
        var search_btn = $(".input-search-box > button.dropdown-toggle");
        search_btn.text($(this).text());
        search_btn.val($(this).text());
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

    $.ajax({
        url: 'search_query',
        method: 'GET',
        data: {
            query_string: query
        },
        beforeSend: function(){
            //Loading Icon
        },
        success: function(){
            set_scrolling_btn("#results-container");
        },
        complete: function(){
            // Loading Icon (if necessary)
        }
    });

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

        console.log(msg_icon_class);
    if(msg_icon_class === undefined || msg_icon_class === ""){
        msg_icon_obj.addClass("fa-warning");
    }else{
        msg_icon_obj.addClass(msg_icon_class);
    }

    $("#msg-modal").modal('show');

}

function set_scrolling_btn(container_selector){
    $('html, body').animate({
        scrollTop: $(container_selector).offset().top
    }, 700);
}