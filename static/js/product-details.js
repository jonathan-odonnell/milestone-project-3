// If the value of search item in the browser's local storage is not null, updates the back link HTML. Code for local storage is from https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage and code for left chevron icon is from https://fontawesome.com/icons/chevron-left?style=solid

$(document).ready(function () {
    if (localStorage.getItem('search') !== null) {
        let html = localStorage.getItem('search')
        let url = localStorage.getItem('search_url')
        $('#current-search').html('<i class="fas fa-chevron-left pr-2 aria-hidden="true"></i>Back to ' + html).attr('href', url);
    }
})

// When the upvote button is clicked, posts the review id to the /upvote url, changes the upvote icon to the solid one, disables the upvote button and updates the vote count on the relevant review to the new value when a success status and the new vote count has been returned. Code is from https://stackoverflow.com/questions/7426085/jquery-getting-form-values-for-ajax-post, https://stackoverflow.com/questions/23597913/disable-button-after-click-in-jquery, and https://stackoverflow.com/questions/3239598/how-can-i-get-the-id-of-an-element-using-jquery. Icon CSS classes are from https://fontawesome.com/icons/thumbs-up?style=regular and https://fontawesome.com/icons/thumbs-up?style=solid


$('.upvote').on('click', function () {
    let review_id = $(this).closest('.row').attr('id')
    $.post("/up_vote", { "review_id": review_id }).done(function (data) {
        $("#" + review_id).find('.upvote i').removeClass('far').addClass('fas')
        $("#" + review_id).find('.upvote').siblings('span').text(data.up_vote)
        $("#" + review_id).find('.upvote').prop('disabled', true)
    })
});

// When the downvote button is clicked, posts the review id to the /downvote url, changes the downvote icon to the solid one, disables the upvote button and updates the vote count on the relevant review to the new value when a success status and the new vote count has been returned. Code is from https://stackoverflow.com/questions/7426085/jquery-getting-form-values-for-ajax-post, https://api.jquery.com/jquery.post/, https://stackoverflow.com/questions/23597913/disable-button-after-click-in-jquery and https://stackoverflow.com/questions/3239598/how-can-i-get-the-id-of-an-element-using-jquery. Icon CSS classes are from https://fontawesome.com/icons/thumbs-down?style=regular and https://fontawesome.com/icons/thumbs-down?style=solid

$('.downvote').on('click', function () {
    let review_id = $(this).closest('.row').attr('id')
    $.post("/down_vote", { "review_id": review_id }).done(function (data) {
        $("#" + review_id).find('.downvote i').removeClass('far').addClass('fas')
        $("#" + review_id).find('.downvote').siblings('span').text(data.down_vote)
        $("#" + review_id).find('.downvote').prop('disabled', true)
    });
});