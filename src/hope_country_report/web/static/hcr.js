$(function () {

    $("#hide-sidebar").on("click", function () {
        $("#sidebar").addClass("hidden");
        $("#show-sidebar").removeClass("hidden");
    })
    $("#show-sidebar").on("click", function () {
        $("#sidebar").removeClass("hidden");
        $("#show-sidebar").addClass("hidden");
    })
    $('#select-tenant select').on('change', function () {
        $('#select-tenant').submit();
    })
    var currentPage = $('meta[name=view]').attr("content");
    if (currentPage) {
        $(`.${currentPage}`).addClass("selected");
    }
});
