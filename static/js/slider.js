function addSlider(par, opts) {
  var arenaElement = document.createElement("div"),
      labelElement = document.createElement("div"),
      barElement = document.createElement("div"),
      hammer = new Hammer(arenaElement, {}),
      maxScale = opts.maxScale || 100,
      minScale = opts.minScale || 0,
      speedMul = opts.speedMultiplier || 1.0,
      roundingFunction = opts.snapTo ? roundedSnapTo : rounded,
      value = null,
      origin;

  arenaElement.className = opts.arenaClass || "sliderBackground";
  labelElement.className = opts.labelClass || "sliderLabel";
  barElement.className = opts.barClass || "sliderBar";

  par.append(arenaElement);
  $(arenaElement).append(labelElement);
  $(arenaElement).append(barElement);

  function reset() {
    value = null;
    $(labelElement).html("");
    $(barElement).css("width", "0px");
    $(arenaElement).toggleClass("sliderInactive", true);
  }

  function hasValue() {
    return value !== null;
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

  function formatted(v) {
    return "" + v + "%";
  }

  function getValue() {
    if (value === null) {
      return null;
    }
    return roundingFunction(value);
  }

  function setValue(v) {
    if (isNaN(v)) {
      return;
    }
    $(arenaElement).toggleClass("sliderInactive", false);
    var wid = $(arenaElement).width();
    if (v < 0) {
      v = 0;
    } else if (v > 1) {
      v = 1;
    }
    value = v;
    $(labelElement).html(formatted(roundingFunction(value)));
    $(barElement).css("width", (value * wid) + "px");

    if (opts.onChange) {
      opts.onChange(getValue());
    }
  }

  $(arenaElement).on("mousedown vmousedown", function(ev) {
    var targetOffset = $(ev.target).offset(),
        offset = ev.pageX - targetOffset.left;
    setValue(offset / $(arenaElement).width());
  });
  $(arenaElement).on("touchstart touchmove", function(ev) {
    console.log("foo");
  });

  return {
    getValue: getValue,
    reset: reset,
    isSet: hasValue,
  };
};
