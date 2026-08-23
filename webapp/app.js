(async function () {
  const el = (id) => document.getElementById(id);
  const tree = el('tree');
  const search = el('search');
  const stats = el('stats');
  const body = el('body');
  const sidebarToggle = el('sidebar-toggle');
  const sidebarScrim = el('sidebar-scrim');

  const emptyState = el('empty-state');
  const templateView = el('template-view');

  let data = null;
  let flatTemplates = []; // {id, name, sectionTitle, subTitle, template, itemEl}
  let groups = []; // {sectionEl, subHeaderEl, subBodyEl, itemEls}
  let activeId = null;
  let activeFiles = [];
  let activeFileIndex = 0;

  async function load() {
    const res = await fetch('data.json', { cache: 'no-store' });
    data = await res.json();
    stats.textContent = `${data.stats.implemented}/${data.stats.total} templates`;
    renderTree();
    renderLeaderboard(data.leaderboard);
    handleHashChange();
  }

  function renderLeaderboard(lb) {
    if (!lb) return;
    const listEl = el('leaderboard-list');
    listEl.innerHTML = '';
    if (!lb.top.length) {
      listEl.innerHTML = '<li class="lb-empty">No contributions yet — be the first!</li>';
    } else {
      lb.top.forEach((entry, i) => {
        const li = document.createElement('li');
        li.className = 'lb-row';
        li.innerHTML = `
          <span class="lb-rank">#${i + 1}</span>
          <span class="lb-name">${escapeHtml(entry.name)}</span>
          <span class="lb-count">${entry.count} ${entry.count === 1 ? 'template' : 'templates'}</span>
        `;
        listEl.appendChild(li);
      });
    }

    const leadEl = el('leaderboard-lead');
    leadEl.innerHTML = `
      <span class="lb-icon">👑</span>
      <span class="lb-lead-name">${escapeHtml(lb.lead.name)}</span>
      <span class="lb-lead-count">${lb.lead.count} ${lb.lead.count === 1 ? 'template' : 'templates'}</span>
      <span class="lb-lead-note">lead developer — doesn't count 😉</span>
    `;
  }

  function renderTree() {
    tree.innerHTML = '';
    flatTemplates = [];
    groups = [];

    data.sections.forEach((section) => {
      const sTitle = document.createElement('div');
      sTitle.className = 'section-title';
      sTitle.textContent = section.title;
      tree.appendChild(sTitle);

      section.subsections.forEach((sub) => {
        const subHeader = document.createElement('button');
        subHeader.type = 'button';
        subHeader.className = 'sub-title';
        subHeader.innerHTML = `<span class="chevron">▾</span><span>${escapeHtml(sub.title)}</span>`;
        tree.appendChild(subHeader);

        const subBody = document.createElement('div');
        subBody.className = 'sub-body';
        tree.appendChild(subBody);

        subHeader.addEventListener('click', () => {
          const collapsed = subHeader.classList.toggle('collapsed');
          subBody.classList.toggle('collapsed', collapsed);
        });

        const itemEls = [];
        sub.templates.forEach((t) => {
          const btn = document.createElement('button');
          btn.className = 'tpl-item' + (t.image ? ' has-image' : '');
          btn.dataset.id = t.id;
          btn.innerHTML = `
            <span class="dot"></span>
            <span class="label">${escapeHtml(t.name || t.id)}</span>
            <span class="id">${escapeHtml(t.id)}</span>
          `;
          btn.addEventListener('click', () => {
            window.location.hash = t.id;
            closeSidebarOnMobile();
          });
          subBody.appendChild(btn);
          itemEls.push(btn);

          flatTemplates.push({
            id: t.id,
            name: t.name,
            sectionTitle: section.title,
            subTitle: sub.title,
            template: t,
            itemEl: btn,
          });
        });

        groups.push({ sectionEl: sTitle, subHeaderEl: subHeader, subBodyEl: subBody, itemEls });
      });
    });
  }

  function escapeHtml(s) {
    return String(s || '').replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));
  }

  function findTemplate(id) {
    return flatTemplates.find((f) => f.id.toLowerCase() === String(id).toLowerCase());
  }

  function handleHashChange() {
    const id = decodeURIComponent(window.location.hash.replace(/^#/, ''));
    if (!id) {
      showEmpty();
      return;
    }
    const found = findTemplate(id);
    if (!found) {
      showEmpty();
      return;
    }
    showTemplate(found);
  }

  function showEmpty() {
    activeId = null;
    emptyState.hidden = false;
    templateView.hidden = true;
    flatTemplates.forEach((f) => f.itemEl.classList.remove('active'));
  }

  function showTemplate(entry) {
    activeId = entry.id;
    emptyState.hidden = true;
    templateView.hidden = false;

    flatTemplates.forEach((f) => f.itemEl.classList.toggle('active', f.id === entry.id));
    entry.itemEl.scrollIntoView({ block: 'nearest' });

    const t = entry.template;
    el('tpl-name').textContent = t.name || t.id;
    el('tpl-id').textContent = t.id;

    const badges = el('tpl-badges');
    badges.innerHTML = `
      <span class="badge ${t.v30 ? 'yes' : ''}">v3.0 ${t.v30 ? '✓' : '—'}</span>
      <span class="badge ${t.v28 ? 'yes' : ''}">v2.8 ${t.v28 ? '✓' : '—'}</span>
    `;

    const meta = el('tpl-meta');
    const metaItems = [];
    if (t.feed) metaItems.push(`<span class="meta-item"><b>Feed:</b> ${escapeHtml(t.feed)}</span>`);
    if (t.contributor) metaItems.push(`<span class="meta-item"><b>Contributor:</b> ${escapeHtml(t.contributor)}</span>`);
    metaItems.push(`<span class="meta-item"><b>Category:</b> ${escapeHtml(entry.sectionTitle)} / ${escapeHtml(entry.subTitle)}</span>`);
    meta.innerHTML = metaItems.join('');

    el('tpl-description').textContent = t.description || t.notes || '';

    const imgWrap = el('tpl-image-wrap');
    const img = el('tpl-image');
    if (t.image) {
      imgWrap.hidden = false;
      img.src = t.image;
      img.alt = `${t.name || t.id} geometry preview`;
    } else {
      imgWrap.hidden = true;
    }

    activeFiles = t.files || [];
    activeFileIndex = 0;
    renderCodeTabs();
    renderActiveFile();

    window.scrollTo(0, 0);
    el('content').scrollTo(0, 0);
  }

  function renderCodeTabs() {
    const tabs = el('code-tabs');
    tabs.innerHTML = '';
    if (activeFiles.length <= 1) return;
    activeFiles.forEach((f, i) => {
      const tab = document.createElement('button');
      tab.className = 'code-tab' + (i === activeFileIndex ? ' active' : '');
      tab.textContent = f.label;
      tab.addEventListener('click', () => {
        activeFileIndex = i;
        renderCodeTabs();
        renderActiveFile();
      });
      tabs.appendChild(tab);
    });
  }

  function renderActiveFile() {
    const file = activeFiles[activeFileIndex];
    const codeBlock = el('code-block');
    const filenameEl = el('code-filename');
    if (!file) {
      codeBlock.textContent = '# No source file available for this template yet.';
      filenameEl.textContent = '';
      return;
    }
    filenameEl.textContent = file.filename;
    codeBlock.textContent = file.code;
    codeBlock.removeAttribute('data-highlighted');
    if (window.hljs) {
      window.hljs.highlightElement(codeBlock);
    }
  }

  // ---- Copy to clipboard ----
  el('copy-btn').addEventListener('click', async () => {
    const file = activeFiles[activeFileIndex];
    if (!file) return;
    try {
      await navigator.clipboard.writeText(file.code);
    } catch (e) {
      const ta = document.createElement('textarea');
      ta.value = file.code;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
    const btn = el('copy-btn');
    const label = el('copy-label');
    const prevLabel = label.textContent;
    btn.classList.add('copied');
    label.textContent = 'Copied!';
    setTimeout(() => {
      btn.classList.remove('copied');
      label.textContent = prevLabel;
    }, 1400);
  });

  // ---- Lightbox ----
  const lightbox = el('lightbox');
  const lightboxImg = el('lightbox-img');
  el('tpl-image').addEventListener('click', () => {
    lightboxImg.src = el('tpl-image').src;
    lightbox.hidden = false;
  });
  lightbox.addEventListener('click', () => { lightbox.hidden = true; });

  // ---- Search / filter ----
  search.addEventListener('input', () => {
    const q = search.value.trim().toLowerCase();

    flatTemplates.forEach((f) => {
      const hay = `${f.id} ${f.name} ${f.sectionTitle} ${f.subTitle}`.toLowerCase();
      f.itemEl.style.display = !q || hay.includes(q) ? '' : 'none';
    });

    const sectionVisible = new Map();
    groups.forEach((g) => {
      const anyVisible = g.itemEls.some((elm) => elm.style.display !== 'none');
      const show = !q || anyVisible;
      g.subHeaderEl.style.display = show ? '' : 'none';
      if (!show) {
        g.subBodyEl.style.display = 'none';
      } else if (q) {
        g.subBodyEl.style.display = 'block'; // force-expand matches while searching
      } else {
        g.subBodyEl.style.display = ''; // restore manual collapsed/expanded state
      }
      sectionVisible.set(g.sectionEl, (sectionVisible.get(g.sectionEl) || false) || show);
    });
    sectionVisible.forEach((visible, sectionEl) => {
      sectionEl.style.display = visible ? '' : 'none';
    });
  });

  // ---- Brand / home link ----
  el('brand').addEventListener('click', (e) => {
    e.preventDefault();
    window.location.hash = '';
    handleHashChange();
    closeSidebarOnMobile();
  });

  // ---- Mobile sidebar ----
  sidebarToggle.addEventListener('click', () => {
    body.classList.toggle('sidebar-open');
  });
  sidebarScrim.addEventListener('click', closeSidebarOnMobile);
  function closeSidebarOnMobile() {
    body.classList.remove('sidebar-open');
  }

  window.addEventListener('hashchange', handleHashChange);

  load().catch((err) => {
    tree.innerHTML = `<div class="no-results">Failed to load data.json: ${escapeHtml(err.message)}</div>`;
  });
})();
