import "./scss/post.scss";
import "./css/font.css";

import "./card";    // card.js


var $comments = $('#comments');
var $submitBtn = $('#comment-submit');
var $commentForm = $('#comment-form');

$commentForm.on('submit', (event) => {
    event.preventDefault();
    let $this = $(event.currentTarget);
    let $content = $this.find('#comment-content');
    let url = $this.data('url');

    $.ajax({
        url: `/api/${url}`,
        type: 'POST',
        data: {content: $content.val()},
        success: function(rs) {
            if (!rs.r) {
                $content.val('');   // clear <textarea></textarea>
                $(rs.data.html).hide().prependTo($comments).fadeIn(1000);
            }
            else {
                alert('Your Comment operation failed, please try later.');
            }
        }
    });
    return false;
});
