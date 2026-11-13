// Screenshot viewer. Copied identically into pdf/, cad/ and svg/; keep the three copies the same.
//
// The page has <ul class="gallery"> with one <li> per screenshot:
//   <a href="shots/NAME.png" data-caption="..."><img src="shots/NAME-thumb.jpg" alt="..."></a>
// Without JavaScript each thumbnail just opens its full picture. With it, a click opens the
// <dialog class="viewer"> on that picture, and the arrows (buttons, keyboard, or a swipe on a
// phone) go through all of them; Esc, the close button or a click outside the picture closes it.
(function () {
  var gallery = document.querySelector(".gallery");
  var viewer = document.querySelector(".viewer");
  if (!gallery || !viewer || typeof viewer.showModal !== "function") return;

  var links = Array.prototype.slice.call(gallery.querySelectorAll("a[href]"));
  var img = viewer.querySelector(".viewer-img");
  var caption = viewer.querySelector(".viewer-caption");
  var counter = viewer.querySelector(".viewer-count");
  var prev = viewer.querySelector(".viewer-prev");
  var next = viewer.querySelector(".viewer-next");
  var close = viewer.querySelector(".viewer-close");
  var current = 0;
  var opener = null;

  function show(i) {
    current = (i + links.length) % links.length;
    var a = links[current];
    var thumb = a.querySelector("img");
    img.src = a.getAttribute("href");
    img.alt = thumb ? thumb.alt : "";
    caption.textContent = a.getAttribute("data-caption") || (thumb ? thumb.alt : "");
    counter.textContent = (current + 1) + " of " + links.length;
    // the neighbors, so the next arrow shows its picture at once
    [current + 1, current - 1].forEach(function (k) {
      var n = links[(k + links.length) % links.length];
      if (n) { var pre = new Image(); pre.src = n.getAttribute("href"); }
    });
  }

  links.forEach(function (a, i) {
    a.addEventListener("click", function (e) {
      if (e.ctrlKey || e.metaKey || e.shiftKey || e.button !== 0) return; // new tab/window: let it
      e.preventDefault();
      opener = a;
      show(i);
      viewer.showModal();
      next.focus();
    });
  });

  prev.addEventListener("click", function () { show(current - 1); });
  next.addEventListener("click", function () { show(current + 1); });
  close.addEventListener("click", function () { viewer.close(); });

  viewer.addEventListener("keydown", function (e) {
    if (e.key === "ArrowLeft") { e.preventDefault(); show(current - 1); }
    else if (e.key === "ArrowRight") { e.preventDefault(); show(current + 1); }
  });

  // a click on the dark area around the picture closes the viewer
  viewer.addEventListener("click", function (e) {
    if (e.target === viewer || e.target.classList.contains("viewer-stage")) viewer.close();
  });

  viewer.addEventListener("close", function () {
    img.removeAttribute("src");
    if (opener) opener.focus();
  });

  // swipe left or right on a touch screen
  var startX = null, startY = null;
  viewer.addEventListener("touchstart", function (e) {
    if (e.touches.length === 1) { startX = e.touches[0].clientX; startY = e.touches[0].clientY; }
  }, { passive: true });
  viewer.addEventListener("touchend", function (e) {
    if (startX === null) return;
    var dx = e.changedTouches[0].clientX - startX;
    var dy = e.changedTouches[0].clientY - startY;
    startX = null;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) show(current + (dx < 0 ? 1 : -1));
  });
})();
