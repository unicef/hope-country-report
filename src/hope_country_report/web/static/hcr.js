$(function () {

    $("#close-sidebar").on("click", function () {
        $("#sidebar").addClass("w-16").removeClass("w-52");
        $("#open-sidebar").removeClass("hidden");
        $(".display-open").hide()
    })
    $("#open-sidebar").on("click", function () {
        $("#sidebar").addClass("w-52").removeClass("w-16");
        $("#logo").addClass("hidden");
        $("#open-sidebar").addClass("hidden");
        $(".display-open").show()
    })
    $('#select-tenant select').on('change', function () {
        $('#select-tenant').submit();
    })
    var currentPage = $('meta[name=view]').attr("content");
    if (currentPage) {
        $(`.${currentPage}`).addClass("selected");
    }
});
