modules = modules || {};
modules.slider = (function(){
  function init(root) {
    root = $(root);

    var data = {value: null},
        origin = null,
        width = null,
        clicking = false,
        touching = null,
        didMove = false,
        target = root.find(".progress"),
        minScale = 0,
        maxScale = 100;

    function onMouseUp() {
      clicking = false;
    }

    function onMouseMove(ev) {
      var delta;

      if(clicking) {
        delta = (ev.pageX - origin) / width;
        origin = ev.pageX;
        setValue(data.value + delta);
      }
    }

    function onMouseDown(ev) {
      var offset = target.offset().left;

      clicking = true;
      origin = ev.pageX;
      width = target.width();

      setValue((origin - offset) / width);
      
      return false;
    }

    function setupMouse() {
      $(document).on("mouseup", onMouseUp);
      $(document).on("mousemove", onMouseMove);
      root.on("mousedown", ".progress", onMouseDown);
    }
    function teardownMouse() {
      $(document).off("mouseup", onMouseUp);
      $(document).off("mousemove", onMouseMove);
      root.off("mousedown", ".progress", onMouseDown);
    }

    function each(l, f) {
      var i = 0;
      while (i < l.length) {
        f(l[i]);
        i++;
      }
    }

    function onTouchStart(ev) {
      ev.preventDefault();
      console.log("touchstart");
      console.log("touchign is " + touching);
      each(ev.originalEvent.touches, function(touch) {
        var offset = target.offset().left;
        console.log("touch " + touch.identifier);
        console.log("at: " + touch.pageX);

        if (touching === null) {
          touching = touch.identifier;

          origin = touch.pageX;
          width = target.width();
          didMove = false;

          if (data.value === null) {
            setValue(0.5);
          }
        }
      });
    }

    function onTouchMove(ev) {
      ev.preventDefault();
      each(ev.originalEvent.touches, function(touch) {
        var delta;

        if (touching === touch.identifier) {
          delta = (touch.pageX - origin) / width;

          if (didMove || Math.abs(delta) > 0.01) {
            origin = touch.pageX;
            didMove = true;

            setValue(data.value + delta);
          }
        }
      });
    }

    function onTouchEndOrCancel(ev) {
      var saw = false;
      ev.preventDefault();

      each(ev.originalEvent.touches, function(touch) {
        if (touching === touch.identifier) {
          saw = true;
        }
      });

      if (!saw) {
        if (!didMove) {
          setValue((origin - target.offset().left) / width);
        }

        touching = null;
      };
    }

    function setupTouch() {
      root.on("touchstart", ".progress", onTouchStart);
      root.on("touchmove", ".progress", onTouchMove);
      root.on("touchend touchcancel", ".progress", onTouchEndOrCancel);
    }
    function teardownTouch() {
      root.off("touchstart", ".progress", onTouchStart);
      root.off("touchmove", ".progress", onTouchMove);
      root.off("touchend touchcancel", ".progress", onTouchEndOrCancel);
    }

    function rounded(x) {
      return Math.round(x * (maxScale - minScale)) + minScale;
    }

    function roundedSnapTo(x) {
      var totalSteps = 100,
          bigSteps = 20,
          k = totalSteps / bigSteps,
          tolerance = 0.9,
          closestBigStep = Math.round(bigSteps * x),
          stepOffset = (bigSteps * x - closestBigStep) * k,
          withinMargin = Math.abs(stepOffset) < tolerance,
          snapPoint = closestBigStep/bigSteps * (maxScale - minScale) + minScale;

      if (withinMargin) {
        return Math.round(snapPoint);
      }

      return rounded(x);
    }

    function normalize(v) {
      if (v < 0) {
        return 0;
      } else if (v > 1) {
        return 1;
      }
      return v;
    }

    function setValue(v) {
      if (isNaN(v)) {
        return;
      }
      data.value = normalize(v);

      root.find(".progress-bar").width(getValue() + "%");
      root.find(".qs-progress-label").html("" + getValue() + "%");
    }

    function getValue() {
      if (data.value === null) {
        return null;
      }
      return roundedSnapTo(data.value);
    }

    console.log("setting up touch handlers");
    setupMouse();
    setupTouch();

    function die() {
      console.log("tearing down touch handlers");
      teardownMouse();
      teardownTouch();
    }

    return {
      getValue: getValue,
      die: die,
    }
  }

  return {
    init: init,
  }
})();
