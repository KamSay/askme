$(document).on("click", ".js-vote", function (e) {
  e.preventDefault();
  e.stopPropagation();

  const $btn = $(this);
  const $wrap = $btn.closest("[data-question-id]");
  const questionId = $wrap.data("question-id");
  const voteType = $btn.data("vote");
  const $rating = $wrap.find(".js-rating");

  if ($wrap.data("voteBusy")) return;
  $wrap.data("voteBusy", true);


  $.ajax({
    url: `/questions/${questionId}/vote/`,
    method: "POST",
    dataType: "json",
    data: { type: voteType },

    success: function (resp) {
      if (!(resp && resp.ok)) {
        $wrap.find(".js-vote").prop("disabled", false);
        return;
      }

      $rating.text(resp.rating);

      const v = Number(resp.user_vote); // 1 или -1

      const $likeBtn = $wrap.find('.js-vote[data-vote="like"]');
      const $dislikeBtn = $wrap.find('.js-vote[data-vote="dislike"]');
      const $likeIcon = $likeBtn.find("i");
      const $dislikeIcon = $dislikeBtn.find("i");

      if (v === 1) {
        $likeIcon.removeClass("bi-caret-up").addClass("bi-caret-up-fill");
        $dislikeIcon.removeClass("bi-caret-down-fill").addClass("bi-caret-down");
      } else if (v === -1) {
        $dislikeIcon.removeClass("bi-caret-down").addClass("bi-caret-down-fill");
        $likeIcon.removeClass("bi-caret-up-fill").addClass("bi-caret-up");
      } else {
        $likeIcon.removeClass("bi-caret-up-fill").addClass("bi-caret-up");
        $dislikeIcon.removeClass("bi-caret-down-fill").addClass("bi-caret-down");
      }
    },

    error: function () {
      $wrap.find(".js-vote").prop("disabled", false);
    },

    complete: function () {
      $wrap.data("voteBusy", false);
    }
  });
});
