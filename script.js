/* Frontend behavior for the Flask-backed Interpreter vs Compiler workbench. */
(() => {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    const editor = document.getElementById('sourceEditor');
    const counter = document.getElementById('charCount');
    const runForm = document.getElementById('runForm');
    const runButton = document.getElementById('runButton');

    // Update the live character count while the user edits the mini-language program.
    const updateCount = () => {
      if (editor && counter) {
        const count = editor.value.length;
        counter.textContent = `${count.toLocaleString()} character${count === 1 ? '' : 's'}`;
      }
    };

    if (editor) {
      updateCount();
      editor.addEventListener('input', updateCount);

      // Ctrl+Enter on Windows/Linux or Cmd+Enter on macOS submits the Flask form.
      editor.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
          event.preventDefault();
          if (runForm && typeof runForm.requestSubmit === 'function') {
            runForm.requestSubmit();
          } else if (runForm) {
            runForm.submit();
          }
        }
      });
    }

    // Show a running state and prevent accidental double-click submissions.
    if (runForm) {
      runForm.addEventListener('submit', (event) => {
        if (!runForm.checkValidity()) {
          event.preventDefault();
          runForm.reportValidity();
          return;
        }
        if (runButton) {
          runButton.disabled = true;
          runButton.textContent = 'Running comparison…';
          runButton.setAttribute('aria-busy', 'true');
        }
      });
    }

    // Bring newly generated results into view after the server responds.
    const results = document.getElementById('results');
    if (results) {
      results.setAttribute('tabindex', '-1');
    }
  });
})();
