// Main IDE JavaScript
$(document).ready(function() {
    // Initialize CodeMirror editor
    const editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
        mode: 'python',
        lineNumbers: true,
        theme: 'dracula',
        indentUnit: 4,
        tabSize: 4,
        lineWrapping: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        viewportMargin: Infinity,  // Allows editor to fill available space
        autoRefresh: true         // Helps with dynamic resizing
    });
    
    // Current file state
    let currentFile = null;
    let isModified = false;
    
    // Tab functionality
    $('.tab-btn').click(function() {
        const tabId = $(this).data('tab');
        $('.tab-btn').removeClass('active');
        $(this).addClass('active');
        $('.tab-content').removeClass('active');
        $(`#${tabId}-tab`).addClass('active');
    });
    
    // Toolbar button handlers
    $('#new-btn').click(newFile);
    $('#open-btn').click(openFile);
    $('#save-btn').click(saveFile);
    $('#compile-btn').click(compileCode);
    
    // Editor change handler
    editor.on('change', function() {
        isModified = true;
        updateTitle();
    });
    
    // Load initial content
    loadEditorContent();
    
    // Set up periodic updates
    setInterval(updateConsole, 1000);
    setInterval(updateInsights, 1000);
    
    // Function definitions
    function newFile() {
        if (isModified && !confirm('Discard changes?')) {
            return;
        }
        editor.setValue('');
        currentFile = null;
        isModified = false;
        updateTitle();
    }
    
    function openFile() {
        if (isModified && !confirm('Discard changes?')) {
            return;
        }
        
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.apbl,.py,.txt';
        
        input.onchange = e => {
            const file = e.target.files[0];
            const reader = new FileReader();
            
            reader.onload = function() {
                editor.setValue(reader.result);
                currentFile = file.name;
                isModified = false;
                updateTitle();
            };
            
            reader.readAsText(file);
        };
        
        input.click();
    }
    
    function saveFile() {
        if (!currentFile) {
            saveAsFile();
            return;
        }
        
        const content = editor.getValue();
        
        fetch('/file/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content: content, filename: currentFile })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'saved') {
                isModified = false;
                updateTitle();
            } else {
                alert('Save failed: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            alert('Save failed: ' + error);
        });
    }
    
    function saveAsFile() {
        const content = editor.getValue();
        const filename = prompt('Enter file name:', currentFile || 'untitled.apbl');
        
        if (!filename) return;
        
        fetch('/file/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content: content, filename: filename })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'saved') {
                currentFile = filename;
                isModified = false;
                updateTitle();
            } else {
                alert('Save failed: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            alert('Save failed: ' + error);
        });
    }
    
    function compileCode() {
        const content = editor.getValue();
        const consoleOutput = $('#console-output');
        
        // Clear console and show loading
        consoleOutput.empty();
        consoleOutput.append($('<div class="loading">▶ Starting compilation...</div>'));
        
        fetch('/compile', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ content: content })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status !== 'started') {
                consoleOutput.append($('<div class="error">❌ Failed to start</div>'));
            }
        })
        .catch(error => {
            consoleOutput.append($('<div class="error">❌ Connection error</div>'));
        });
    
        // Poll for updates every 500ms
        const pollInterval = setInterval(() => {
            updateConsole();
            updateInsights();  // Refresh insights tab too!
        }, 500);
    
        // Stop polling after 30s
        setTimeout(() => clearInterval(pollInterval), 30000);
    }
    
    function loadEditorContent() {
        fetch('/editor/content')
        .then(response => response.json())
        .then(data => {
            editor.setValue(data.content);
            currentFile = data.file;
            isModified = false;
            updateTitle();
        });
    }
    
    function updateConsole() {
        fetch('/console/output')
        .then(response => response.json())
        .then(data => {
            const consoleOutput = $('#console-output');
            
            // Only clear and rebuild if we have new content
            if (data.output && data.output.length > 0) {
                consoleOutput.empty();
                
                data.output.forEach(item => {
                    const div = $('<div>').text(item.text);
                    if (item.type === 'success') {
                        div.addClass('success');
                    } else if (item.type === 'error') {
                        div.addClass('error');
                    } else if (item.type === 'warning') {
                        div.addClass('warning');
                    }
                    consoleOutput.append(div);
                });
                
                // Auto-scroll to bottom
                consoleOutput.scrollTop(consoleOutput[0].scrollHeight);
            }
        })
        .catch(error => {
            console.error('Error fetching console output:', error);
        });
    }
    
    function updateInsights() {
        fetch('/insights/data')
        .then(response => response.json())
        .then(data => {
            const container = $('#insights-container');
            container.empty();
            
            // Add phases
            data.phases.forEach(phase => {
                const phaseDiv = $(`
                    <div class="phase">
                        <div class="phase-header">
                            <span class="phase-name">${phase.name}</span>
                            <span class="phase-status ${'status-' + phase.status} ${phase.is_error ? 'status-error' : ''}">
                                ${phase.status}
                            </span>
                        </div>
                        <div class="phase-description">${phase.description}</div>
                        ${phase.result ? `<div class="phase-result">${phase.result}</div>` : ''}
                    </div>
                `);
                container.append(phaseDiv);
            });
            
            // Add insights
            data.insights.forEach(insight => {
                const insightDiv = $(`
                    <div class="insight">
                        <div class="insight-title">${insight.title}</div>
                        ${insight.code ? `<div class="insight-code">${insight.code}</div>` : ''}
                        <div class="insight-explanation">${insight.explanation}</div>
                    </div>
                `);
                container.append(insightDiv);
            });
        });
    }
    
    function updateTitle() {
        const filename = currentFile ? currentFile : 'Untitled';
        const modified = isModified ? '*' : '';
        $('#filename').text(`${filename}${modified}`);
    }
});