/**
 * ASRS Storage Classifier Frontend
 */

// API endpoint - update for production
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:3000'
    : 'https://zatpg0rga1.execute-api.us-west-2.amazonaws.com/prod';

// DOM elements
const descriptionInput = document.getElementById('product-description');
const charCount = document.getElementById('char-count');
const classifyBtn = document.getElementById('classify-btn');
const resultSection = document.getElementById('result-section');
const errorSection = document.getElementById('error-section');
const loadingSection = document.getElementById('loading-section');

// Result elements
const classificationBadge = document.getElementById('classification-badge');
const confidenceValue = document.getElementById('confidence-value');
const reasoningText = document.getElementById('reasoning-text');
const toolsUsed = document.getElementById('tools-used');
const errorText = document.getElementById('error-text');

/**
 * Update character count display
 */
function updateCharCount() {
    const count = descriptionInput.value.length;
    charCount.textContent = count;
}

/**
 * Show a specific section and hide others
 */
function showSection(section) {
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    loadingSection.classList.add('hidden');

    if (section) {
        section.classList.remove('hidden');
    }
}

/**
 * Get CSS class for category badge
 */
function getCategoryClass(classification) {
    const classMap = {
        'POUCH': 'pouch',
        'SMALL_BIN': 'small-bin',
        'TOTE': 'tote',
        'CARTON': 'carton',
        'OVERSIZED': 'oversized'
    };
    return classMap[classification] || 'tote';
}

/**
 * Get display name for category
 */
function getCategoryDisplayName(classification) {
    const nameMap = {
        'POUCH': 'Pouch',
        'SMALL_BIN': 'Small Bin',
        'TOTE': 'Tote',
        'CARTON': 'Carton',
        'OVERSIZED': 'Oversized'
    };
    return nameMap[classification] || classification;
}

/**
 * Render tool usage information
 */
function renderToolsUsed(tools) {
    toolsUsed.innerHTML = '';

    const toolNames = {
        'lookup_known_product': 'Product Lookup',
        'extract_explicit_dimensions': 'Dimension Extraction'
    };

    for (const [toolId, tool] of Object.entries(tools)) {
        const toolItem = document.createElement('div');
        toolItem.className = 'tool-item';

        const statusClass = tool.called ? 'called' : 'not-called';
        const statusIcon = tool.called ? '✓' : '–';

        let resultText = '';
        if (tool.called && tool.result) {
            resultText = tool.result;
        } else if (!tool.called && tool.reason) {
            resultText = tool.reason;
        }

        toolItem.innerHTML = `
            <span class="tool-status ${statusClass}">${statusIcon}</span>
            <div class="tool-info">
                <div class="tool-name">${toolNames[toolId] || toolId}</div>
                ${resultText ? `<div class="tool-result">${resultText}</div>` : ''}
            </div>
        `;

        toolsUsed.appendChild(toolItem);
    }
}

/**
 * Display classification result
 */
function displayResult(data) {
    // Update classification badge
    classificationBadge.textContent = getCategoryDisplayName(data.classification);
    classificationBadge.className = `category-badge ${getCategoryClass(data.classification)}`;

    // Update confidence
    confidenceValue.textContent = `${data.confidence}%`;

    // Update reasoning
    reasoningText.textContent = data.reasoning;

    // Update tools used
    if (data.tools_used) {
        renderToolsUsed(data.tools_used);
    }

    showSection(resultSection);
}

/**
 * Display error message
 */
function displayError(message) {
    errorText.textContent = message;
    showSection(errorSection);
}

/**
 * Classify the product
 */
async function classifyProduct() {
    const description = descriptionInput.value.trim();

    // Client-side validation
    if (!description) {
        displayError('Please enter a product description');
        return;
    }

    if (description.length > 2000) {
        displayError('Description must not exceed 2000 characters');
        return;
    }

    // Show loading state
    classifyBtn.disabled = true;
    showSection(loadingSection);

    try {
        const response = await fetch(`${API_BASE_URL}/classify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ description }),
        });

        const data = await response.json();

        if (!response.ok) {
            // Handle error response
            displayError(data.message || 'An error occurred while classifying the product');
            return;
        }

        // Display successful result
        displayResult(data);

    } catch (error) {
        console.error('Classification error:', error);
        displayError('Unable to connect to the classification service. Please try again.');
    } finally {
        classifyBtn.disabled = false;
    }
}

// Event listeners
descriptionInput.addEventListener('input', updateCharCount);

classifyBtn.addEventListener('click', classifyProduct);

// Allow Enter key to submit (Ctrl+Enter or Cmd+Enter for textarea)
descriptionInput.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        classifyProduct();
    }
});

// Initialize
updateCharCount();
