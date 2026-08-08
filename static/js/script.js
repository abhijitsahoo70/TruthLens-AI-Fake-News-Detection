/* ==========================================================================
   TRUTHLENS AI — INTERACTIVE CLIENT JS SCRIPT
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  // 1. Textarea Character & Word Counter
  const newsTextarea = document.getElementById('news_text');
  const charCounter = document.getElementById('char-count');
  const wordCounter = document.getElementById('word-count');
  const clearBtn = document.getElementById('clear-text-btn');

  if (newsTextarea) {
    const updateCounts = () => {
      const text = newsTextarea.value;
      const chars = text.length;
      const words = text.trim() ? text.trim().split(/\s+/).length : 0;

      if (charCounter) charCounter.textContent = `${chars} characters`;
      if (wordCounter) wordCounter.textContent = `${words} words`;
    };

    newsTextarea.addEventListener('input', updateCounts);
    updateCounts();

    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        newsTextarea.value = '';
        updateCounts();
        newsTextarea.focus();
      });
    }
  }

  // 2. Loading Spinner Animation on Form Submit
  const predictForm = document.getElementById('predict-form');
  const loadingOverlay = document.getElementById('loading-overlay');

  if (predictForm && loadingOverlay) {
    predictForm.addEventListener('submit', (e) => {
      const textVal = newsTextarea ? newsTextarea.value.trim() : '';
      if (!textVal) {
        e.preventDefault();
        alert('Please enter or paste news content before analyzing.');
        return;
      }
      loadingOverlay.style.display = 'flex';
    });
  }

  // 3. Password Visibility Toggle
  const togglePassBtns = document.querySelectorAll('.toggle-password');
  togglePassBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const targetId = this.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (input) {
        if (input.type === 'password') {
          input.type = 'text';
          this.classList.remove('fa-eye');
          this.classList.add('fa-eye-slash');
        } else {
          input.type = 'password';
          this.classList.remove('fa-eye-slash');
          this.classList.add('fa-eye');
        }
      }
    });
  });

  // 4. Confirm Deletion Handlers
  const deleteForms = document.querySelectorAll('.delete-form');
  deleteForms.forEach(form => {
    form.addEventListener('submit', function(e) {
      if (!confirm('Are you sure you want to delete this analysis record?')) {
        e.preventDefault();
      }
    });
  });

  const clearHistoryForm = document.getElementById('clear-history-form');
  if (clearHistoryForm) {
    clearHistoryForm.addEventListener('submit', function(e) {
      if (!confirm('WARNING: This will permanently delete all your analysis records. Continue?')) {
        e.preventDefault();
      }
    });
  }

});

// Helper function to render Chart.js charts on dashboard page
function initDashboardCharts(statsData) {
  if (typeof Chart === 'undefined') return;

  // Chart 1: Prediction Distribution
  const predCtx = document.getElementById('predictionChart');
  if (predCtx && statsData.total > 0) {
    new Chart(predCtx, {
      type: 'doughnut',
      data: {
        labels: ['REAL', 'FAKE'],
        datasets: [{
          data: [statsData.real_count, statsData.fake_count],
          backgroundColor: ['#10b981', '#ef4444'],
          borderColor: '#1e293b',
          borderWidth: 3
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: '#f8fafc', font: { family: 'Outfit', size: 13 } }
          }
        }
      }
    });
  }

  // Chart 2: Credibility Distribution
  const credCtx = document.getElementById('credibilityChart');
  if (credCtx && statsData.total > 0) {
    new Chart(credCtx, {
      type: 'bar',
      data: {
        labels: ['High (80-100)', 'Moderate (60-79)', 'Low (40-59)', 'Very Low (0-39)'],
        datasets: [{
          label: 'Analyses Count',
          data: [
            statsData.high_credibility,
            statsData.moderate_credibility,
            statsData.low_credibility,
            statsData.very_low_credibility
          ],
          backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
          y: { ticks: { color: '#94a3b8', stepSize: 1 }, grid: { color: 'rgba(255,255,255,0.05)' } }
        }
      }
    });
  }
}
