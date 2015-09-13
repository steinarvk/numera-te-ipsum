var modules = modules || {};
modules.eventreporting = (function() {
  function init(root) {
    root = $(root);

    var rangestart_raw = root.find(".qs-event-t0").val(),
        rangeend_raw = root.find(".qs-event-t1").val(),
        rangestart = moment(rangestart_raw),
        rangeend = null,
        timerId = null,
        fmt = "dddd MMMM Do HH:mm",
        currentResult = null;

    function updateLabels() {
      var age;

      if (rangeend_raw === "now") {
        rangeend = moment();
      }

      age = rangeend.from(rangestart, true);
      root.find(".qs-event-query-time-duration").html(age);
    }

    root.find(".qs-event-query-begin-time").html(rangestart.format(fmt));

    if (rangeend_raw === "now") {
      root.find(".qs-event-query-end-time").html("now");
      timerId = setInterval(updateLabels, 5000);
      updateLabels();
    } else {
      rangeend = moment(rangeend_raw);
      root.find(".qs-event-query-end-time").html(rangeend.format(fmt));
      updateLabels();
    }

    root.find(".qs-event-datetimepicker").datetimepicker({
      minuteStep: 5,
      todayBtn: true,
      linkField: "qs-event-start-datetime-hidden",
      startDate: rangestart.toDate(),
      endDate: (rangeend !== null) ? rangeend.toDate() : null,
    });
    root.find(".qs-event-options").on("change", "input[type=radio]", function() {
      console.log("reacting to radio button");

      var is_yes = $(this).hasClass("qs-event-yes-at");
      root.find(".qs-event-yes-details").toggle(is_yes);
      if (is_yes) {
        currentResult = null;
      } else if ($(this).hasClass("qs-event-unknown")) {
        currentResult = { "result": "unknown" };
      } else if ($(this).hasClass("qs-event-no")) {
        currentResult = { "result": "no" };
      }
    });
    root.find(".qs-event-accept-datetimepicker").click(function() {
      console.log("reacting to accept");
      var x = moment(root.find("#qs-event-start-datetime-hidden").val());
      console.log("value string is: " + x);
      root.find(".qs-event-details-start-time").html(x.format(fmt));
      root.find("#qs-modal-event-datetimepicker").modal("hide");
      updateChosenRange();
    });
    root.find(".qs-event-duration-mins").change(function() {
      console.log("reacting to duration change");
      updateChosenRange();
    });

    function getComment() {
      var s = root.find(".qs-event-comment").val().trim();
      if (s.length > 0) {
        return s;
      }

      return null;
    }

    function updateChosenRange() {
      console.log("updating chosen range");

      var m = parseInt(root.find(".qs-event-duration-mins").val(), 10),
          t0 = moment(root.find("#qs-event-start-datetime-hidden").val()),
          t1;

      console.log("trying to update");
      console.log(m);
      
      if (root.find(".qs-event-is-instant").val() === "yes") {
        currentResult = {
          "result": "yes",
          "instant": "yes",
          "duration_minutes": 0,
          "t0": t0,
          "t1": t0,
        };
      } else if (m > 0) {
        t1 = moment(t0).add(m, "minutes");
        console.log(t1);
        $(".qs-event-end-time").html(t1.format(fmt));

        currentResult = {
          "result": "yes",
          "t0": t0,
          "duration_minutes": m,
          "t1": t1,
        };
      }
    }

    function die() {
      console.log("tearing down event reporting panel");

      if (timerId !== null) {
        clearInterval(timerId);
        timerId = null;
      }
    }

    function getChosen() {
      if (currentResult) {
        currentResult.comment = getComment();
      }
      return currentResult;
    }

    function getRangeStart() {
      return rangestart;
    }

    function getRangeEnd() {
      return rangeend;
    }

    return {
      die: die,
      result: getChosen,
      rangestart: getRangeStart,
      rangeend: getRangeEnd,
    };
  }

  return {
    init: init,
  }
})();
