/**
 * Página Gestión de Dispositivos.
 * Carga lista desde API, búsqueda, paginación y acciones.
 */
(function () {
  // if (!authRequerirSesion()) return;  // Descomentar para requerir login en producción

  const tbody = document.getElementById('dispositivosBody');
  const searchInput = document.getElementById('searchInput');
  const pageSizeSelect = document.getElementById('pageSize');
  const paginationRange = document.getElementById('paginationRange');
  const paginationNumbers = document.getElementById('paginationNumbers');
  const btnFirst = document.getElementById('btnFirst');
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');
  const btnLast = document.getElementById('btnLast');
  const btnNuevo = document.getElementById('btnNuevo');
  const btnExportar = document.getElementById('btnExportar');

  let dispositivos = [];
  let filtered = [];
  let pageSize = 15;
  let currentPage = 1;

  function formatDate(d) {
    if (!d) return '—';
    const date = new Date(d);
    return date.toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' });
  }

  function getEstadoBadge(index) {
    const estados = ['activo', 'mantenimiento', 'inactivo'];
    return estados[index % 3];
  }

  function renderRow(d, index) {
    const estado = getEstadoBadge(index);
    const estadoLabel = estado.charAt(0).toUpperCase() + estado.slice(1);
    return `
      <tr data-id="${d.id}">
        <td>${d.serial || '—'}</td>
        <td>${d.tipoDispositivo || '—'}</td>
        <td class="marca-modelo">
          <strong>${d.marca || '—'}</strong>
          <span>${d.modelo || ''}</span>
        </td>
        <td>${d.usuario || '—'}</td>
        <td><span class="badge-estado badge-estado--${estado}">${estadoLabel}</span></td>
        <td>${formatDate(d.fechaCreado)}</td>
        <td class="acciones-cell">
          <button type="button" class="btn-icon btn-icon--edit" title="Editar" data-action="edit" data-id="${d.id}">&#9998;</button>
          <button type="button" class="btn-icon btn-icon--delete" title="Eliminar" data-action="delete" data-id="${d.id}">&#128465;</button>
        </td>
      </tr>
    `;
  }

  function filterData() {
    const q = (searchInput && searchInput.value ? searchInput.value.trim().toLowerCase() : '') || '';
    if (!q) {
      filtered = [...dispositivos];
    } else {
      filtered = dispositivos.filter(function (d) {
        const serial = (d.serial || '').toLowerCase();
        const tipo = (d.tipoDispositivo || '').toLowerCase();
        const marca = (d.marca || '').toLowerCase();
        const modelo = (d.modelo || '').toLowerCase();
        const usuario = (d.usuario || '').toLowerCase();
        return serial.includes(q) || tipo.includes(q) || marca.includes(q) || modelo.includes(q) || usuario.includes(q);
      });
    }
  }

  function getPaginated() {
    const start = (currentPage - 1) * pageSize;
    return filtered.slice(start, start + pageSize);
  }

  function renderTable() {
    if (!tbody) return;

    filterData();
    const pageData = getPaginated();
    const total = filtered.length;

    if (total === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="dispositivos-empty">No hay dispositivos que coincidan con la búsqueda.</td></tr>';
    } else {
      tbody.innerHTML = pageData.map(function (d, i) {
        return renderRow(d, (currentPage - 1) * pageSize + i);
      }).join('');
    }

    updatePagination(total);
    bindRowActions();
  }

  function updatePagination(total) {
    const totalPages = Math.max(1, Math.ceil(total / pageSize));
    const start = total === 0 ? 0 : (currentPage - 1) * pageSize + 1;
    const end = Math.min(currentPage * pageSize, total);

    if (paginationRange) {
      paginationRange.textContent = total === 0 ? '0 de 0' : start + '-' + end + ' de ' + total;
    }

    if (paginationNumbers) {
      let html = '';
      for (let i = 1; i <= totalPages; i++) {
        const active = i === currentPage ? ' active' : '';
        html += '<button type="button" class="btn-pag' + active + '" data-page="' + i + '">' + i + '</button>';
      }
      paginationNumbers.innerHTML = html;
    }

    if (btnFirst) btnFirst.disabled = currentPage <= 1;
    if (btnPrev) btnPrev.disabled = currentPage <= 1;
    if (btnNext) btnNext.disabled = currentPage >= totalPages;
    if (btnLast) btnLast.disabled = currentPage >= totalPages;
  }

  function bindRowActions() {
    if (!tbody) return;
    tbody.querySelectorAll('[data-action="edit"]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const id = btn.getAttribute('data-id');
        if (id) alert('Editar dispositivo ' + id + ' (pendiente implementar modal/formulario)');
      });
    });
    tbody.querySelectorAll('[data-action="delete"]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const id = btn.getAttribute('data-id');
        if (id && confirm('¿Eliminar este dispositivo?')) {
          if (typeof apiDelete === 'function') {
            apiDelete('/api/Dispositivo/' + id).then(function () {
              loadDispositivos();
            }).catch(function (err) {
              alert('Error al eliminar: ' + (err.message || 'Error desconocido'));
            });
          } else {
            alert('API no disponible');
          }
        }
      });
    });
    paginationNumbers && paginationNumbers.querySelectorAll('.btn-pag[data-page]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        currentPage = parseInt(btn.getAttribute('data-page'), 10);
        renderTable();
      });
    });
  }

  function loadDispositivos() {
    if (typeof apiGet !== 'function' || !authObtenerToken()) {
      dispositivos = [];
      renderTable();
      return;
    }
    apiGet('/api/Dispositivo').then(function (data) {
      dispositivos = Array.isArray(data) ? data : [];
      currentPage = 1;
      renderTable();
    }).catch(function () {
      dispositivos = [];
      renderTable();
    });
  }

  function exportCSV() {
    filterData();
    if (filtered.length === 0) {
      alert('No hay datos para exportar.');
      return;
    }
    const headers = ['Serial', 'Tipo', 'Marca', 'Modelo', 'Usuario', 'Fecha Creación'];
    const rows = filtered.map(function (d) {
      return [d.serial || '', d.tipoDispositivo || '', d.marca || '', d.modelo || '', d.usuario || '', formatDate(d.fechaCreado)];
    });
    const csv = [headers.join(','), ...rows.map(function (r) { return r.map(function (c) { return '"' + String(c).replace(/"/g, '""') + '"'; }).join(','); })].join('\n');
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'dispositivos_' + new Date().toISOString().slice(0, 10) + '.csv';
    a.click();
    URL.revokeObjectURL(a.href);
  }

  if (searchInput) {
    searchInput.addEventListener('input', function () {
      currentPage = 1;
      renderTable();
    });
  }
  if (pageSizeSelect) {
    pageSizeSelect.addEventListener('change', function () {
      pageSize = parseInt(pageSizeSelect.value, 10);
      currentPage = 1;
      renderTable();
    });
  }
  if (btnFirst) btnFirst.addEventListener('click', function () { currentPage = 1; renderTable(); });
  if (btnPrev) btnPrev.addEventListener('click', function () { if (currentPage > 1) { currentPage--; renderTable(); } });
  if (btnNext) btnNext.addEventListener('click', function () { if (currentPage < Math.ceil(filtered.length / pageSize)) { currentPage++; renderTable(); } });
  if (btnLast) btnLast.addEventListener('click', function () { currentPage = Math.max(1, Math.ceil(filtered.length / pageSize)); renderTable(); });
  if (btnNuevo) btnNuevo.addEventListener('click', function () { alert('Nuevo dispositivo (pendiente implementar formulario/modal)'); });
  if (btnExportar) btnExportar.addEventListener('click', exportCSV);

  loadDispositivos();
})();
