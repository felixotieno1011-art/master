/* aws.js — client-side table enhancer, matches real AWS console behavior.
 *
 * Runs on DOMContentLoaded. For every .aws-table it:
 *   1. Adds a filter input above the table (filters rows by any cell text)
 *   2. Adds "N of M" row count under the table
 *   3. Makes <th> headers clickable to sort (asc → desc → off)
 *   4. Adds a checkbox column + bulk-actions dropdown IF the table has
 *      data-bulk-actions="<json>".
 *
 * No backend dependency. Pure DOM.
 */

(function () {
  "use strict";

  function enhanceTable(table) {
    // Skip if already enhanced (e.g. re-render of injected content)
    if (table.dataset.enhanced === "1") return;
    table.dataset.enhanced = "1";

    const tbody = table.querySelector("tbody");
    if (!tbody) return;

    const allRows = Array.from(tbody.querySelectorAll("tr"));

    // ---- 1. Filter input above table ----
    const filterWrap = document.createElement("div");
    filterWrap.className = "aws-table-filter";
    const filterInput = document.createElement("input");
    filterInput.type = "search";
    filterInput.placeholder = "Filter by property or value";
    filterInput.className = "aws-table-filter-input";
    filterWrap.appendChild(filterInput);
    table.parentNode.insertBefore(filterWrap, table);

    // ---- 2. Row count below table ----
    const countEl = document.createElement("div");
    countEl.className = "aws-table-count";
    table.parentNode.insertBefore(countEl, table.nextSibling);
    const updateCount = (visible) => {
      countEl.textContent = `${visible} of ${allRows.length} rows shown`;
    };
    updateCount(allRows.length);

    // ---- 3. Sortable headers ----
    const headers = table.querySelectorAll("thead th");
    headers.forEach((th, colIdx) => {
      // Skip columns with no sortable data (Actions columns)
      const text = th.textContent.trim().toLowerCase();
      if (text === "actions" || text === "") return;
      th.classList.add("aws-th-sortable");
      th.style.cursor = "pointer";
      th.addEventListener("click", () => {
        const cur = th.dataset.sortDir || "";
        const next = cur === "" ? "asc" : cur === "asc" ? "desc" : "";
        headers.forEach(h => { delete h.dataset.sortDir; h.classList.remove("aws-sorted-asc", "aws-sorted-desc"); });
        if (next) {
          th.dataset.sortDir = next;
          th.classList.add("aws-sorted-" + next);
          sortByCol(tbody, colIdx, next);
        }
        // Even when sorting off, re-filter to make sure visible set is consistent
        applyFilter();
      });
    });

    function sortByCol(tb, colIdx, dir) {
      const rows = Array.from(tb.querySelectorAll("tr"));
      rows.sort((a, b) => {
        const av = a.children[colIdx] ? a.children[colIdx].textContent.trim() : "";
        const bv = b.children[colIdx] ? b.children[colIdx].textContent.trim() : "";
        // Numeric sort if both look numeric
        const an = parseFloat(av.replace(/[^\d.-]/g, ""));
        const bn = parseFloat(bv.replace(/[^\d.-]/g, ""));
        let cmp;
        if (!isNaN(an) && !isNaN(bn) && /[\d]/.test(av) && /[\d]/.test(bv)) {
          cmp = an - bn;
        } else {
          cmp = av.localeCompare(bv, undefined, { numeric: true });
        }
        return dir === "desc" ? -cmp : cmp;
      });
      rows.forEach(r => tb.appendChild(r));
    }

    // ---- 4. Filter logic ----
    function applyFilter() {
      const needle = (filterInput.value || "").toLowerCase().trim();
      let visible = 0;
      allRows.forEach(row => {
        if (!needle) {
          row.style.display = "";
          visible++;
          return;
        }
        const text = row.textContent.toLowerCase();
        const hit = text.indexOf(needle) !== -1;
        row.style.display = hit ? "" : "none";
        if (hit) visible++;
      });
      updateCount(visible);
    }
    filterInput.addEventListener("input", applyFilter);

    // ---- 5. Checkbox column + bulk actions ----
    let bulkActions = null;
    try {
      if (table.dataset.bulkActions) {
        bulkActions = JSON.parse(table.dataset.bulkActions);
      }
    } catch (e) {}

    if (bulkActions && bulkActions.length) {
      // Add a header cell for checkboxes
      const headerRow = table.querySelector("thead tr");
      if (headerRow) {
        const th = document.createElement("th");
        th.className = "aws-th-checkbox";
        th.style.width = "32px";
        const selectAllCb = document.createElement("input");
        selectAllCb.type = "checkbox";
        selectAllCb.title = "Select all";
        th.appendChild(selectAllCb);
        headerRow.insertBefore(th, headerRow.firstChild);

        selectAllCb.addEventListener("change", () => {
          tbody.querySelectorAll("tr:not([style*='display: none']) input[type=checkbox]").forEach(cb => {
            cb.checked = selectAllCb.checked;
          });
        });
      }
      // Add a checkbox cell to each row
      allRows.forEach(row => {
        const td = document.createElement("td");
        td.className = "aws-td-checkbox";
        const cb = document.createElement("input");
        cb.type = "checkbox";
        td.appendChild(cb);
        row.insertBefore(td, row.firstChild);
      });

      // Bulk actions toolbar
      const toolbar = document.createElement("div");
      toolbar.className = "aws-bulk-actions";
      toolbar.innerHTML = `
        <span class="aws-bulk-count">0 selected</span>
        <div class="aws-bulk-dropdown">
          <button type="button" class="aws-button-secondary aws-bulk-btn">
            Actions &#9662;
          </button>
          <div class="aws-bulk-menu" style="display:none;">
            ${bulkActions.map(a => `<a href="#" data-action="${a}">${a}</a>`).join("")}
          </div>
        </div>
      `;
      table.parentNode.insertBefore(toolbar, table);

      const bulkCountEl = toolbar.querySelector(".aws-bulk-count");
      const bulkBtn = toolbar.querySelector(".aws-bulk-btn");
      const bulkMenu = toolbar.querySelector(".aws-bulk-menu");

      bulkBtn.addEventListener("click", () => {
        bulkMenu.style.display = bulkMenu.style.display === "none" ? "block" : "none";
      });

      // Update count
      tbody.addEventListener("change", () => {
        const n = tbody.querySelectorAll("input[type=checkbox]:checked").length;
        bulkCountEl.textContent = `${n} selected`;
      });

      // Handle action clicks — POST the form the current page provides
      bulkMenu.addEventListener("click", (e) => {
        const action = e.target.dataset.action;
        if (!action) return;
        e.preventDefault();
        const checked = tbody.querySelectorAll("input[type=checkbox]:checked");
        if (!checked.length) {
          alert("Select at least one row first.");
          return;
        }
        if (action === "Delete" && !confirm(`Delete ${checked.length} item(s)?`)) return;
        // Dispatch a custom event so the page can handle it
        const event = new CustomEvent("aws-bulk-action", {
          detail: { action, rowIndices: Array.from(checked).map(cb => Array.from(tbody.querySelectorAll("input[type=checkbox]")).indexOf(cb)) },
        });
        document.dispatchEvent(event);
      });
    }
  }

  // Enhance all tables on page load
  function enhanceAll() {
    document.querySelectorAll(".aws-table").forEach(enhanceTable);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", enhanceAll);
  } else {
    enhanceAll();
  }
})();
