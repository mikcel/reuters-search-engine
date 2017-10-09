$(function () {

    $(".dropdown-opts.dropdown-menu > li").click(function () {

        var search_btn = $(".input-search-box > button.dropdown-toggle");
        search_btn.text($(this).text());
        search_btn.val($(this).text());

    });

    $('.smooth').smoothScroll({
        speed: 700,
        autoCoefficient: 1
    });

});