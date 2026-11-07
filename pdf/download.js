// Points the download links at the newest release's files on GitHub.
// Copied identically into pdf/ and cad/; keep the two copies the same.
//
// Each link with data-repo="owner/name" and data-asset="<regular expression>" gets the
// browser_download_url of the first file matching that expression in the newest published
// (not draft, not pre-release) release that has one. The link's href in the HTML is the
// GitHub releases page, so the button still works if JavaScript is off or GitHub's API
// can't be reached (it allows 60 requests an hour per visitor IP without a token).
// An element with data-version-for="owner/name" shows that release's version. See reveal()
// for downloads that only some releases have, and showNotes() for "What's new".
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
        if (published.length) showNotes(repo, published[0]);
        byRepo[repo].forEach(function (a) {
          var pattern = new RegExp(a.getAttribute("data-asset"), "i");
          for (var i = 0; i < published.length; i++) {
            var assets = published[i].assets || [];
            for (var j = 0; j < assets.length; j++) {
              if (pattern.test(assets[j].name) && isOwnRelease(assets[j].browser_download_url, repo)) {
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

  // Only a file in this repository's own GitHub releases is linked:
  // https://github.com/<owner>/<name>/releases/download/... Anything else the API might
  // return is ignored and the link stays on the releases page. (What people download matters
  // most on this site; this keeps a bad API answer from pointing them anywhere else.)
  function isOwnRelease(url, repo) {
    var u;
    try { u = new URL(url); } catch (e) { return false; }
    var prefix = ("/" + repo + "/releases/download/").toLowerCase();
    return u.protocol === "https:" && u.hostname === "github.com" && !u.port &&
      !u.username && !u.password && u.pathname.toLowerCase().indexOf(prefix) === 0 &&
      u.pathname.indexOf("..") === -1;
  }

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

  // "What's new": an element with data-notes-for="owner/name" gets the newest release's own
  // notes, the part of its GitHub release text between <!-- ...-notes --> and
  // <!-- /...-notes --> (the English part; KanzonasPDF adds a Spanish one after it). Only a
  // little Markdown is understood (**Heading** lines, "- " items, **bold**, *italic*, `code`),
  // and everything is put in as text, never as HTML. Each heading shows at most
  // data-notes-max items (default 6), then a link to the rest.
  function showNotes(repo, rel) {
    var box = document.querySelector('[data-notes-for="' + repo + '"]');
    if (!box) return;
    var m = /<!--\s*([a-z]+-)?notes(?:\s[^>]*)?-->([\s\S]*?)<!--\s*\/\s*([a-z]+-)?notes\s*-->/.exec(rel.body || "");
    if (!m) return;
    var max = parseInt(box.getAttribute("data-notes-max") || "6", 10);
    var sections = [], cur = null, item = null;
    m[2].split(/\r?\n/).forEach(function (line) {
      var h = /^\s*\*\*([^*]+)\*\*\s*$/.exec(line);
      if (h) { cur = { title: h[1], items: [] }; sections.push(cur); item = null; return; }
      var li = /^\s*[-*]\s+(.*)$/.exec(line);
      if (li) {
        if (!cur) { cur = { title: "", items: [] }; sections.push(cur); }
        item = li[1]; cur.items.push(item); return;
      }
      if (/^\s+\S/.test(line) && cur && cur.items.length) {
        cur.items[cur.items.length - 1] += " " + line.trim();
      }
    });
    if (!sections.length) return;
    var version = String(rel.tag_name || "").replace(/^v/i, "");
    var title = box.querySelector("[data-notes-title]");
    if (title) title.textContent = "What's new in version " + version;
    var out = box.querySelector("[data-notes-body]");
    out.textContent = "";
    sections.forEach(function (s) {
      if (!s.items.length) return;
      if (s.title) { var h3 = document.createElement("h3"); h3.textContent = s.title; out.appendChild(h3); }
      var ul = document.createElement("ul");
      s.items.slice(0, max).forEach(function (text) {
        var li = document.createElement("li"); inline(li, text); ul.appendChild(li);
      });
      out.appendChild(ul);
      if (s.items.length > max) {
        var more = document.createElement("p"); more.className = "notes-more";
        more.textContent = "...and " + (s.items.length - max) + " more.";
        out.appendChild(more);
      }
    });
    var link = box.querySelector("[data-notes-link]");
    if (link && rel.html_url && isOwnReleasePage(rel.html_url, repo)) link.href = rel.html_url;
    box.hidden = false;
  }

  // **bold**, *italic* and `code` as elements; everything else as plain text
  function inline(parent, text) {
    var re = /\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`/g, last = 0, m;
    while ((m = re.exec(text))) {
      if (m.index > last) parent.appendChild(document.createTextNode(text.slice(last, m.index)));
      var el = document.createElement(m[1] ? "strong" : m[2] ? "em" : "code");
      el.textContent = m[1] || m[2] || m[3];
      parent.appendChild(el);
      last = re.lastIndex;
    }
    if (last < text.length) parent.appendChild(document.createTextNode(text.slice(last)));
  }

  function isOwnReleasePage(url, repo) {
    var u;
    try { u = new URL(url); } catch (e) { return false; }
    return u.protocol === "https:" && u.hostname === "github.com" &&
      u.pathname.toLowerCase().indexOf(("/" + repo + "/releases/").toLowerCase()) === 0;
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
