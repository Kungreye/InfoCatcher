import "./css/font.css";
import "./follow";


var $likeBtn = $('.like-button');
var $isLiked = $likeBtn.hasClass('liked');
var $collectBtn = $('.collect-button');
var $isCollected = $collectBtn.hasClass('collected');


$likeBtn.on('click', (event) => {
    let $this = $(event.currentTarget);
    let url = $this.data('url');

    $.ajax({
        url: `/api/${url}`,
        type: $isLiked ? 'DELETE' : 'POST',
        data: {},
        success: function(rs) {
            if (!rs.r) {
                let isLiked = rs.data.is_liked;
                if ($isLiked != isLiked) {
                    $isLiked = isLiked;
                    $this.toggleClass('liked');
                    $this.find('span').text(rs.data.n_likes);
                    if (isLiked) {
                        $this.find('i').addClass('InfoCatcher-liked').removeClass('InfoCatcher-like');
                    }
                    else {
                        $this.find('i').removeClass('InfoCatcher-liked').addClass('InfoCatcher-like');
                    }
                }
            }
            else {
                alert('Your Upvote operation failed, please try later.');
            }
        }
    });
});


$collectBtn.on('click', (event) => {
    let $this = $(event.currentTarget);
    let url = $this.data('url');

    $.ajax({
        url: `/api/${url}`,
        type: $isCollected ? 'DELETE' : 'POST',
        data: {},
        success: function(rs) {
            if (!rs.r) {
                let isCollected = rs.data.is_collected;
                if ($isCollected != isCollected) {
                    $isCollected = isCollected;
                    $this.toggleClass('collected');
                    if (isCollected) {
                        $this.find('i').addClass('InfoCatcher-collected').removeClass('InfoCatcher-collect');
                    }
                    else {
                        $this.find('i').removeClass('InfoCatcher-collected').addClass('InfoCatcher-collect');
                    }
                }
            }
            else {
                alert('Your Collect operation failed, please try later.');
            }
        }
    });
});
