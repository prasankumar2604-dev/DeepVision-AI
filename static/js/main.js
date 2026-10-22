/**
 * DeepVision AI — Luxury Dark Gold Client Interactive System
 * Production-ready, lightweight vanilla JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
  'use strict';

  // =========================================================================
  // 1. Mobile Navigation Toggle
  // =========================================================================
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const mobileDrawer = document.getElementById('mobileDrawer');

  if (mobileMenuBtn && mobileDrawer) {
    mobileMenuBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      mobileDrawer.classList.toggle('open');
      const icon = mobileMenuBtn.querySelector('i');
      if (icon) {
        if (mobileDrawer.classList.contains('open')) {
          icon.classList.remove('fa-bars');
          icon.classList.add('fa-xmark');
        } else {
          icon.classList.remove('fa-xmark');
          icon.classList.add('fa-bars');
        }
      }
    });

    // Close drawer when clicking outside
    document.addEventListener('click', function (e) {
      if (mobileDrawer.classList.contains('open') && !mobileDrawer.contains(e.target)) {
        mobileDrawer.classList.remove('open');
        const icon = mobileMenuBtn.querySelector('i');
        if (icon) {
          icon.classList.remove('fa-xmark');
          icon.classList.add('fa-bars');
        }
      }
    });
  }

  // =========================================================================
  // 2. Password Visibility Toggle
  // =========================================================================
  const passwordToggles = document.querySelectorAll('.toggle-password-btn');
  passwordToggles.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const input = this.closest('.password-input-wrapper').querySelector('input');
      const icon = this.querySelector('i');
      if (input) {
        if (input.type === 'password') {
          input.type = 'text';
          if (icon) {
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
          }
        } else {
          input.type = 'password';
          if (icon) {
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
          }
        }
      }
    });
  });

  // =========================================================================
  // 3. Flash Notification Auto-dismiss & Close
  // =========================================================================
  const flashAlerts = document.querySelectorAll('.flash');
  flashAlerts.forEach(function (alert) {
    // Add close button if not present
    if (!alert.querySelector('.flash-close-btn')) {
      const closeBtn = document.createElement('button');
      closeBtn.className = 'flash-close-btn';
      closeBtn.innerHTML = '&times;';
      closeBtn.setAttribute('aria-label', 'Close alert');
      closeBtn.addEventListener('click', function () {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 250);
      });
      alert.appendChild(closeBtn);
    }
  });

  // =========================================================================
  // 4. Detection Upload Studio: Drag & Drop + Live Preview + Scan Laser
  // =========================================================================
  const imageInput = document.getElementById('imageInput');
  const uploadArea = document.getElementById('uploadArea');
  const previewContainer = document.getElementById('previewContainer');
  const previewImage = document.getElementById('previewImage');
  const previewName = document.getElementById('previewName');
  const previewSize = document.getElementById('previewSize');
  const removeFileBtn = document.getElementById('removeFileBtn');
  const detectForm = document.getElementById('detectForm');
  const detectSubmitBtn = document.getElementById('detectSubmitBtn');
  const scanningBanner = document.getElementById('scanningBanner');
  const previewWrapper = document.getElementById('previewWrapper');

  function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  function handleFileSelect(file) {
    if (!file) return;

    // Validate type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type.toLowerCase())) {
      alert('Please upload a valid image file (JPG, PNG, JPEG, or WEBP).');
      if (imageInput) imageInput.value = '';
      return;
    }

    // Validate size (max 16MB)
    if (file.size > 16 * 1024 * 1024) {
      alert('Selected image exceeds the 16MB file limit. Please select a smaller image.');
      if (imageInput) imageInput.value = '';
      return;
    }

    // Update metadata
    if (previewName) previewName.textContent = file.name;
    if (previewSize) previewSize.textContent = formatBytes(file.size);

    // Show preview
    if (previewImage) {
      const reader = new FileReader();
      reader.onload = function (e) {
        previewImage.src = e.target.result;
        if (previewContainer) {
          previewContainer.classList.add('active');
        }
        if (uploadArea) {
          uploadArea.style.display = 'none';
        }
      };
      reader.readAsDataURL(file);
    }
  }

  if (imageInput) {
    imageInput.addEventListener('change', function () {
      if (this.files && this.files[0]) {
        handleFileSelect(this.files[0]);
      }
    });
  }

  if (uploadArea) {
    ['dragenter', 'dragover'].forEach(eventName => {
      uploadArea.addEventListener(eventName, function (e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.classList.add('drag-over');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      uploadArea.addEventListener(eventName, function (e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.classList.remove('drag-over');
      }, false);
    });

    uploadArea.addEventListener('drop', function (e) {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files && files.length > 0) {
        if (imageInput) {
          imageInput.files = files;
        }
        handleFileSelect(files[0]);
      }
    }, false);
  }

  // Remove file button
  if (removeFileBtn) {
    removeFileBtn.addEventListener('click', function (e) {
      e.preventDefault();
      if (imageInput) imageInput.value = '';
      if (previewImage) previewImage.src = '';
      if (previewContainer) previewContainer.classList.remove('active');
      if (uploadArea) uploadArea.style.display = 'flex';
      if (scanningBanner) scanningBanner.classList.remove('active');
    });
  }

  // Form submission with real-time laser scan animation
  if (detectForm) {
    detectForm.addEventListener('submit', function (e) {
      if (!imageInput || !imageInput.files || imageInput.files.length === 0) {
        e.preventDefault();
        alert('Please select an image first.');
        return;
      }

      // Add laser overlay to the preview wrapper
      if (previewWrapper && !previewWrapper.querySelector('.scanning-overlay')) {
        const overlay = document.createElement('div');
        overlay.className = 'scanning-overlay';
        overlay.innerHTML = '<div class="scanning-grid"></div><div class="scanning-laser"></div>';
        previewWrapper.appendChild(overlay);
      }

      // Show scanning status banner
      if (scanningBanner) {
        scanningBanner.classList.add('active');
      }

      // Update button state with spinner
      if (detectSubmitBtn) {
        detectSubmitBtn.disabled = true;
        detectSubmitBtn.innerHTML = '<span class="spinner"></span> Neural Model Inference Running...';
      }
    });
  }

  // =========================================================================
  // 5. History Real-Time Search & Filtering
  // =========================================================================
  const historySearch = document.getElementById('historySearch');
  const filterTabs = document.querySelectorAll('.filter-tab');
  const tableRows = document.querySelectorAll('.history-table tbody tr');
  const mobileCards = document.querySelectorAll('.history-mobile-card');
  const emptyFilterMsg = document.getElementById('emptyFilterMsg');

  let currentVerdictFilter = 'all';
  let currentSearchQuery = '';

  function applyHistoryFilter() {
    let visibleCount = 0;

    // Filter table rows
    tableRows.forEach(row => {
      const filename = (row.getAttribute('data-filename') || '').toLowerCase();
      const verdict = (row.getAttribute('data-verdict') || '').toLowerCase();

      const matchesSearch = filename.includes(currentSearchQuery);
      const matchesVerdict = (currentVerdictFilter === 'all') || (verdict === currentVerdictFilter);

      if (matchesSearch && matchesVerdict) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });

    // Filter mobile cards
    mobileCards.forEach(card => {
      const filename = (card.getAttribute('data-filename') || '').toLowerCase();
      const verdict = (card.getAttribute('data-verdict') || '').toLowerCase();

      const matchesSearch = filename.includes(currentSearchQuery);
      const matchesVerdict = (currentVerdictFilter === 'all') || (verdict === currentVerdictFilter);

      if (matchesSearch && matchesVerdict) {
        card.style.display = 'flex';
      } else {
        card.style.display = 'none';
      }
    });

    // Toggle empty match message
    if (emptyFilterMsg) {
      if (visibleCount === 0 && (tableRows.length > 0 || mobileCards.length > 0)) {
        emptyFilterMsg.style.display = 'block';
      } else {
        emptyFilterMsg.style.display = 'none';
      }
    }
  }

  if (historySearch) {
    historySearch.addEventListener('input', function () {
      currentSearchQuery = this.value.trim().toLowerCase();
      applyHistoryFilter();
    });
  }

  filterTabs.forEach(tab => {
    tab.addEventListener('click', function () {
      filterTabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      currentVerdictFilter = (this.getAttribute('data-filter') || 'all').toLowerCase();
      applyHistoryFilter();
    });
  });

});
