var modules = modules || {};
modules.util = (function() {
  function fmtSeconds(s) {
    var h, m, rv = [];

    if (s >= Infinity) {
      return "\u221e";
    }

    if (s === 0) {
      return "0";
    }

    if (s < 0) {
      return "-" + fmtSeconds(-s);
    }

    s = Math.round(s);
    h = Math.floor(s / 3600);
    s -= h * 3600;
    m = Math.floor(s / 60);
    s -= m * 60;

    if (h > 0) {
      rv.push("" + h + "h");
    }

    if (m > 0) {
      rv.push("" + m + "m");
    }

    if (s > 0) {
      rv.push("" + s + "s");
    }

    return rv.join(" ");
  }

  function formatTimeDiff(a, b) {
    return fmtSeconds(b.diff(a, "seconds"));
  }

  return {
    formatTimeDiff: formatTimeDiff,
  };
})();
