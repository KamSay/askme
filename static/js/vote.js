$(document).on("click", ".js-vote", function (e) {
  e.preventDefault();

  const $wrap = $(this).closest("[data-question-id]");
  const $rating = $wrap.find(".js-rating");
  const url = $wrap.data("vote-url");
  const voteType = $(this).data("vote");

  $.ajax({
    url,
    method: "POST",
    dataType: "json",
    data: { type: voteType },

    success: function (resp) {
      if (!resp?.ok) return;

      $rating.text(resp.rating);

      const v = Number(resp.user_vote);

      const $likeIcon = $wrap.find('.js-vote[data-vote="like"] i');
      const $dislikeIcon = $wrap.find('.js-vote[data-vote="dislike"] i');

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
  });
});

$(document).on("change", ".js-correct", function () {
  const $cb = $(this);
  const url = $cb.data("url");
  const checked = $cb.is(":checked");

  $cb.prop("disabled", true);

  $.ajax({
    url,
    method: "POST",
    dataType: "json",
    data: { is_correct: checked ? "true" : "false" },

    success: function (resp) {
      if (!resp?.ok) $cb.prop("checked", !checked);
    },

    error: function () {
      $cb.prop("checked", !checked);
    },

    complete: function () {
      $cb.prop("disabled", false);
    },
  });
});
