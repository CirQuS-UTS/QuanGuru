// Replace the "This Page" / "Show Source" block with a single
// "Download notebook" link when the page source is a notebook (.ipynb).
// Otherwise remove the whole block.
document.addEventListener('DOMContentLoaded', function () {
    try {
        var menu = document.querySelector('.this-page-menu');
        if (!menu) return;

        // find first notebook link
        var notebookLink = null;
        var anchors = Array.from(menu.querySelectorAll('a'));
        for (var i = 0; i < anchors.length; i++) {
            var href = anchors[i].getAttribute('href') || '';
            if (href.toLowerCase().endsWith('.ipynb')) {
                notebookLink = anchors[i];
                break;
            }
        }

        // find the outer sidebar-secondary-item that contains this menu
        var sidebarItem = menu.closest('.sidebar-secondary-item');

        if (notebookLink && sidebarItem) {
            var href = notebookLink.getAttribute('href');
            // Create a clean download link element
            var container = document.createElement('div');
            container.className = 'sidebar-secondary-item';
            var a = document.createElement('a');
            a.href = href;
            a.textContent = 'Download notebook';
            a.setAttribute('rel', 'nofollow');
            a.className = 'download-notebook';
            // Encourage download behavior
            try { a.setAttribute('download', ''); } catch (e) {}
            container.appendChild(a);
            // Replace the existing sidebar item
            sidebarItem.parentNode.replaceChild(container, sidebarItem);
        } else if (sidebarItem) {
            // no notebook source: remove the whole block
            sidebarItem.remove();
        }

        // ---- Move/clone the search form into the left primary sidebar ----
        try {
            var searchForm = document.querySelector('#pst-search-dialog form.bd-search');
            var primarySidebar = document.querySelector('#pst-primary-sidebar');
            // target place: insert above the section navigation start
            var target = primarySidebar ? primarySidebar.querySelector('.sidebar-primary-items__start') : null;
            if (searchForm && target && target.parentNode) {
                var formClone = searchForm.cloneNode(true);
                // make sure the cloned form is visible and usable in sidebar
                var wrapper = document.createElement('div');
                wrapper.className = 'sidebar-search mb-3';
                wrapper.appendChild(formClone);
                target.parentNode.insertBefore(wrapper, target);
            }
        } catch (e) {
            // non-fatal
            console.error('moving search form failed', e);
        }
    } catch (e) {
        console.error('conditional_source.js error', e);
    }
});
