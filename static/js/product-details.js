$(document).ready(function () {
        if (localStorage.getItem('search') !== null) {
            let html = localStorage.getItem('search')
            let url = localStorage.getItem('search_url')
            $('#current-search').html('<i class="fas fa-chevron-left pr-2"></i>Back to ' + html).attr('href', url);
            localStorage.setItem('product', $('h2').html())
        }
    })
    $('.upvote').on('click', function () {
        let review_id = $(this).closest('.row').attr('id')
        $.post("/up_vote", { "review_id": review_id }).done(function (data) {
            $("#" + review_id).find('.upvote i').removeClass('far').addClass('fas')
            $("#" + review_id).find('.upvote').siblings('span').text(data.up_vote)
            // https://stackoverflow.com/questions/23597913/disable-button-after-click-in-jquery
            $("#" + review_id).find('.upvote').prop('disabled', true)
        })
    });
    $('.downvote').on('click', function () {
        let review_id = $(this).closest('.row').attr('id')
        $.post("/down_vote", { "review_id": review_id }).done(function (data) {
            $("#" + review_id).find('.downvote i').removeClass('far').addClass('fas')
            $("#" + review_id).find('.downvote').siblings('span').text(data.down_vote)
            // https://stackoverflow.com/questions/23597913/disable-button-after-click-in-jquery
            $("#" + review_id).find('.downvote').prop('disabled', true)
        });
    });