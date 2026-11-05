// Points the download links at the newest release's files on GitHub.
// Copied identically into pdf/ and cad/; keep the two copies the same.
//
// Each link with data-repo="owner/name" and data-asset="<regular expression>" gets the
// browser_download_url of the first file matching that expression in the newest published
// (not draft, not pre-release) release that has one. The link's href in the HTML is the
// GitHub releases page, so the button still works if JavaScript is off or GitHub's API
// can't be reached (it allows 60 requests an hour per visitor IP without a token).
// An element with data-version-for="owner/name" shows that release's version. See reveal()
// for downloads that only some releases have.
(function () {
  var links = document.querySelectorAll("a[data-repo][data-asset]");
  var byRepo = {};
  Array.prototype.forEach.call(links, function (a) {
    var repo = a.getAttribute("data-repo");
    (byRepo[repo] = byRepo[repo] || []).push(a);
  });

  Object.keys(byRepo).forEach(function (repo) {
    fetch("https://api.github.com/repos/" + repo + "/releases?per_page=20", {
      headers: { Accept: "application/vnd.github+json" }
    })
      .then(function (r) {
        if (!r.ok) throw new Error("GitHub API " + r.status);
        return r.json();
      })
      .then(function (releases) {
        var published = releases.filter(function (rel) {
          return !rel.draft && !rel.prerelease;
        });
        byRepo[repo].forEach(function (a) {
          var pattern = new RegExp(a.getAttribute("data-asset"), "i");
          for (var i = 0; i < published.length; i++) {
            var assets = published[i].assets || [];
            for (var j = 0; j < assets.length; j++) {
              if (pattern.test(assets[j].name)) {
                a.href = assets[j].browser_download_url;
                a.setAttribute("data-file", assets[j].name);
                reveal(a);
                if (a.hasAttribute("data-primary")) showVersion(repo, published[i]);
                return;
              }
            }
          }
        });
      })
      .catch(function () {
        // Leave the links on the releases page.
      });
  });

  // A link inside a hidden <span data-reveal="key"> (a download that not every release has,
  // like macOS) is shown once its file is found, and anything marked
  // data-hide-on-reveal="key" (such as "No macOS version yet") is hidden.
  function reveal(a) {
    var box = a.closest("[data-reveal]");
    if (!box) return;
    box.hidden = false;
    var key = box.getAttribute("data-reveal");
    var gone = document.querySelectorAll('[data-hide-on-reveal="' + key + '"]');
    Array.prototype.forEach.call(gone, function (el) { el.hidden = true; });
  }

  function showVersion(repo, rel) {
    var targets = document.querySelectorAll('[data-version-for="' + repo + '"]');
    var version = String(rel.tag_name || "").replace(/^v/i, "");
    var date = rel.published_at ? new Date(rel.published_at) : null;
    var text = "Version " + version;
    if (date && !isNaN(date)) {
      text += ", released " + date.toLocaleDateString("en-US", {
        year: "numeric", month: "long", day: "numeric"
      });
    }
    Array.prototype.forEach.call(targets, function (el) {
      el.textContent = text;
    });
  }
})();
