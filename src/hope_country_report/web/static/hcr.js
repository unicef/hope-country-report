(function ($) {

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


        function delay(callback, ms) {
            var timer = 0;
            return function () {
                var context = this, args = arguments;
                clearTimeout(timer);
                timer = setTimeout(function () {
                    callback.apply(context, args);
                }, ms || 0);
            };
        }

        $("#filterInput").on("keyup", delay(function () {
            let filter = this.value.toUpperCase();
            $("table.searchable tr").each(function (i, el) {
                let txt = $(el).find("td,caption").text();
                if (txt.toUpperCase().indexOf(filter) > -1) {
                    $(el).closest(".section").show();
                    $(el).show();
                } else {
                    $(el).hide();
                }
                $("table.section").each(function (i, t) {
                    if ($(t).find("tr:visible").length === 0) {
                        $(t).hide();
                    }
                });
            });
        }, 300)).trigger("keyup").focus();

    })
})(jQuery || django.jQuery)
