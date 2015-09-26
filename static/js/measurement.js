var modules = modules || {};
modules.measurement = (function() {
  function init(root, units) {
    root = $(root);

    var fmt = "dddd MMMM Do HH:mm",
        timeValue = "now";
    
    root.find("ul.nav-tabs a").click(function(e) {
      console.log("activated tab:");
      console.log(this);
      e.preventDefault();
      $(this).tab("show");
    });

    root.find(".qs-measurement-datetimepicker").datetimepicker({
      minuteStep: 5,
      linkField: "qs-measurement-time",
    });

    root.find(".qs-measurement-accept-datetimepicker").click(function() {
      timeValue = moment($("#qs-measurement-time").val());
      $(".qs-measurement-time-button").html("at " + timeValue.format(fmt));
      $("#qs-modal-measurement-datetimepicker").modal("hide");
    });

    root.find(".qs-measurement-time-now").click(function() {
      timeValue = "now";
      $(".qs-measurement-time-button").html("now");
      $("#qs-modal-measurement-datetimepicker").modal("hide");
    });

    function die() {
      console.log("measurement control wrapping up.");
    }

    return {
      die: die,
    }
  }

  return {
    init: init,
  }
})();
