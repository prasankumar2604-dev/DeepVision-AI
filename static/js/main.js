/**
 * DeepVision AI — Cyber Intelligence Client Interactive System
 * Production-ready, performance-conscious vanilla JavaScript
 * Theme: Cyber Intelligence | Neon Blue + Purple + Cyan
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
      const wrapper = this.closest('.password-input-wrapper');
      if (!wrapper) return;
      const input = wrapper.querySelector('input');
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
      alert('Unsupported file format. Please upload a JPG, JPEG, PNG, or WEBP image.');
      if (imageInput) imageInput.value = '';
      return;
    }

    // Validate size (max 16MB)
    if (file.size > 16 * 1024 * 1024) {
      alert('Selected image exceeds the 16MB upload limit. Please select a smaller file.');
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

  // Form submission with indeterminate dynamic AI scanning laser
  if (detectForm) {
    detectForm.addEventListener('submit', function (e) {
      if (!imageInput || !imageInput.files || imageInput.files.length === 0) {
        e.preventDefault();
        alert('Please select an image file to analyze.');
        return;
      }

      // Add cyber laser overlay to the preview wrapper
      if (previewWrapper && !previewWrapper.querySelector('.scanning-overlay')) {
        const overlay = document.createElement('div');
        overlay.className = 'scanning-overlay';
        overlay.innerHTML = '<div class="scanning-grid"></div><div class="scanning-laser"></div>';
        previewWrapper.appendChild(overlay);
      }

      // Show indeterminate scanning status banner
      if (scanningBanner) {
        scanningBanner.classList.add('active');
      }

      // Update button state with spinner and indeterminate text
      if (detectSubmitBtn) {
        detectSubmitBtn.disabled = true;
        detectSubmitBtn.innerHTML = '<span class="spinner"></span> Analyzing image...';
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

  // =========================================================================
  // 6. Live Password Security Checklist & Strength Meter
  // =========================================================================
  const pwdInput = document.getElementById('signupPassword');
  const confirmPwdInput = document.getElementById('signupConfirmPassword');
  const rulesCard = document.getElementById('passwordRulesCard');

  if (pwdInput && rulesCard) {
    const ruleLength = document.getElementById('rule-length');
    const ruleUpper = document.getElementById('rule-upper');
    const ruleLower = document.getElementById('rule-lower');
    const ruleNumber = document.getElementById('rule-number');
    const ruleSpecial = document.getElementById('rule-special');
    const ruleMatch = document.getElementById('rule-match');
    const strengthBarFill = document.getElementById('strengthBarFill');
    const strengthLabel = document.getElementById('strengthLabel');

    function updateRule(elem, isValid) {
      if (!elem) return;
      const icon = elem.querySelector('i');
      if (isValid) {
        elem.classList.add('valid');
        elem.classList.remove('invalid');
        if (icon) {
          icon.className = 'fa-solid fa-circle-check';
        }
      } else {
        elem.classList.remove('valid');
        elem.classList.add('invalid');
        if (icon) {
          icon.className = 'fa-solid fa-circle-xmark';
        }
      }
    }

    function evaluatePassword() {
      const pwd = pwdInput.value || '';
      const confirmPwd = (confirmPwdInput ? confirmPwdInput.value : '') || '';

      const isLength = pwd.length >= 12;
      const isUpper = /[A-Z]/.test(pwd);
      const isLower = /[a-z]/.test(pwd);
      const isNumber = /[0-9]/.test(pwd);
      const isSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]/.test(pwd);
      const isMatch = (pwd.length > 0 && confirmPwd.length > 0 && pwd === confirmPwd);

      updateRule(ruleLength, isLength);
      updateRule(ruleUpper, isUpper);
      updateRule(ruleLower, isLower);
      updateRule(ruleNumber, isNumber);
      updateRule(ruleSpecial, isSpecial);
      updateRule(ruleMatch, isMatch);

      // Calculate score based on the 5 password requirements
      let score = 0;
      if (isLength) score++;
      if (isUpper) score++;
      if (isLower) score++;
      if (isNumber) score++;
      if (isSpecial) score++;

      const percent = Math.round((score / 5) * 100);
      if (strengthBarFill) {
        strengthBarFill.style.width = percent + '%';
        if (score <= 2) {
          strengthBarFill.style.backgroundColor = 'var(--status-fake)';
          if (strengthLabel) {
            strengthLabel.className = 'strength-label weak';
            strengthLabel.textContent = 'Weak';
          }
        } else if (score <= 4) {
          strengthBarFill.style.backgroundColor = 'var(--status-warning)';
          if (strengthLabel) {
            strengthLabel.className = 'strength-label fair';
            strengthLabel.textContent = 'Fair';
          }
        } else {
          strengthBarFill.style.backgroundColor = 'var(--status-real)';
          if (strengthLabel) {
            strengthLabel.className = 'strength-label strong';
            strengthLabel.textContent = isMatch ? 'Strong & Verified' : 'Strong';
          }
        }
      }
    }

    pwdInput.addEventListener('input', evaluatePassword);
    if (confirmPwdInput) {
      confirmPwdInput.addEventListener('input', evaluatePassword);
    }
  }

});
