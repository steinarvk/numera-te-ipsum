$(function() {
  var body = $(document.body);
  body.append(soy.renderAsElement(qs.core.message, {text: "Hello world!"}));
  body.append(soy.renderAsElement(qs.core.message, {text: "This is an <b>evil</b> message."}));
  body.append(soy.renderAsElement(qs.core.link, {text: "This is an evil link.", target: "javascript:alert('foo')"}));
});
