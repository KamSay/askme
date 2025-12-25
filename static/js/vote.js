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

   const url = $wrap.data("vote-url");


  $.ajax({
    url: url,
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


$(document).on("change", ".js-correct", function () {
  const $cb = $(this);
  const url = $cb.data("url");
  const checked = $cb.is(":checked");

  if ($cb.data("busy")) return;
  $cb.data("busy", true);
  $cb.prop("disabled", true);

  $.ajax({
    url: url,
    method: "POST",
    dataType: "json",
    data: { is_correct: checked ? "true" : "false" },

    success: function (resp) {
      if (!(resp && resp.ok)) {
        $cb.prop("checked", !checked);
      }
    },

    error: function () {
      $cb.prop("checked", !checked);
    },

    complete: function () {
      $cb.prop("disabled", false);
      $cb.data("busy", false);
    }
  });
});
