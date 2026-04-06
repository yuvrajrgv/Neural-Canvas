// Main JavaScript for Toonify AI Dashboard

// Global state
let currentTab = 'transform';
let transformFile = null;
let classifyFile = null;
let generateFile = null;
let currentJobs = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    // Check authentication
    if (!requireAuth()) return;

    // Initialize tabs
    initializeTabs();

    // Initialize file uploads
    initializeFileUploads();

    // Load gallery
    loadGallery();

    // Check URL hash for tab
    const hash = window.location.hash.substring(1);
    if (hash && ['transform', 'classify', 'generate', 'gallery'].includes(hash)) {
        switchTab(hash);
    }
});

// Initialize tabs
function initializeTabs() {
    const tabs = document.querySelectorAll('.tab-button');
    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

// Switch tab
function switchTab(tabName) {
    currentTab = tabName;

    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
    });

    // Show selected tab
    const selectedTab = document.getElementById(`${tabName}-tab`);
    if (selectedTab) {
        selectedTab.classList.remove('hidden');
    }

    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    const activeBtn = document.querySelector(`[data-tab="${tabName}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }

    // Update URL hash
    window.location.hash = tabName;

    // Load gallery if switching to gallery tab
    if (tabName === 'gallery') {
        loadGallery();
    }
}

// Initialize file uploads
function initializeFileUploads() {
    // Transform upload
    setupFileUpload('transform');

    // Classify upload
    setupFileUpload('classify');

    // Generate upload
    setupFileUpload('generate');
}

// Setup file upload for a specific feature
function setupFileUpload(feature) {
    const dropZone = document.getElementById(`${feature}-drop-zone`);
    const fileInput = document.getElementById(`${feature}-file-input`);

    if (!dropZone || !fileInput) return;

    // Click to browse
    dropZone.addEventListener('click', () => fileInput.click());

    // File input change
    fileInput.addEventListener('change', function () {
        if (this.files.length > 0) {
            handleFileSelect(feature, this.files[0]);
        }
    });

    // Drag and drop
    dropZone.addEventListener('dragover', function (e) {
        e.preventDefault();
        this.classList.add('border-purple-500');
    });

    dropZone.addEventListener('dragleave', function (e) {
        e.preventDefault();
        this.classList.remove('border-purple-500');
    });

    dropZone.addEventListener('drop', function (e) {
        e.preventDefault();
        this.classList.remove('border-purple-500');

        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(feature, e.dataTransfer.files[0]);
        }
    });
}

// Handle file selection
function handleFileSelect(feature, file) {
    // Validate file
    const validation = validateFile(file);
    if (!validation.valid) {
        showToast(validation.error, 'error');
        return;
    }

    // Store file
    if (feature === 'transform') {
        transformFile = file;
    } else if (feature === 'classify') {
        classifyFile = file;
    } else if (feature === 'generate') {
        generateFile = file;
    }

    // Show preview
    const preview = document.getElementById(`${feature}-preview`);
    const previewImg = document.getElementById(`${feature}-preview-img`);
    const dropZone = document.getElementById(`${feature}-drop-zone`);
    const btn = document.getElementById(`${feature}-btn`);

    if (preview && previewImg) {
        previewImage(file, previewImg);
        preview.classList.remove('hidden');
        dropZone.classList.add('hidden');

        if (btn) {
            btn.disabled = false;
        }
    }
}

// Remove image
function removeTransformImage() {
    transformFile = null;
    document.getElementById('transform-preview').classList.add('hidden');
    document.getElementById('transform-drop-zone').classList.remove('hidden');
    document.getElementById('transform-btn').disabled = true;
    document.getElementById('transform-file-input').value = '';
}

function removeClassifyImage() {
    classifyFile = null;
    document.getElementById('classify-preview').classList.add('hidden');
    document.getElementById('classify-drop-zone').classList.remove('hidden');
    document.getElementById('classify-btn').disabled = true;
    document.getElementById('classify-file-input').value = '';
}

function removeGenerateImage() {
    generateFile = null;
    document.getElementById('generate-preview').classList.add('hidden');
    document.getElementById('generate-drop-zone').classList.remove('hidden');
    document.getElementById('generate-btn').disabled = true;
    document.getElementById('generate-file-input').value = '';
}

// Helper function to load authenticated images
async function loadAuthenticatedImage(jobId, type = 'processed') {
    const token = getAuthToken();
    const url = `${API_BASE}/images/file/${jobId}/${type}`;

    try {
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error('Failed to load image');
        }

        const blob = await response.blob();
        return URL.createObjectURL(blob);
    } catch (error) {
        console.error('Error loading image:', error);
        throw error;
    }
}

// Handle Transform
async function handleTransform() {
    if (!transformFile) {
        showToast('Please select an image first', 'error');
        return;
    }

    const style = document.getElementById('transform-style-select').value;
    const btn = document.getElementById('transform-btn');
    const resultContainer = document.getElementById('transform-result');
    const emptyState = document.getElementById('transform-empty');
    const loadingState = document.getElementById('transform-loading');
    const successState = document.getElementById('transform-success');

    try {
        // Update UI
        btn.disabled = true;
        btn.innerHTML = `${createSpinner('w-5 h-5 inline mr-2')} Processing...`;
        emptyState.classList.add('hidden');
        loadingState.classList.remove('hidden');
        successState.classList.add('hidden');

        // Transform image
        const result = await transformImage(transformFile, style, (status) => {
            console.log('Progress:', status);
        });

        console.log('Transform complete, result:', result);

        // Show result
        loadingState.classList.add('hidden');
        successState.classList.remove('hidden');

        const resultImg = document.getElementById('transform-result-img');
        // Use the job ID from the result (it's 'id' not 'job_id' in the response)
        const jobId = result.id;

        // Load image with authentication
        try {
            const imageUrl = await loadAuthenticatedImage(jobId, 'processed');
            resultImg.src = imageUrl;
        } catch (error) {
            console.error('Failed to load result image:', error);
            showToast('Failed to load result image', 'error');
        }

        // Store job ID for download
        resultImg.dataset.jobId = jobId;

        showToast('Transformation completed!', 'success');

        // Reload gallery
        loadGallery();

    } catch (error) {
        console.error('Transform error:', error);
        showToast(error.message || 'Transformation failed', 'error');

        loadingState.classList.add('hidden');
        emptyState.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '✨ Transform Image';
    }
}

// Handle Classify
async function handleClassify() {
    if (!classifyFile) {
        showToast('Please select an image first', 'error');
        return;
    }

    const btn = document.getElementById('classify-btn');
    const resultsContainer = document.getElementById('classify-results');
    const emptyState = document.getElementById('classify-empty');
    const actionsContainer = document.getElementById('classify-actions');

    try {
        // Update UI
        btn.disabled = true;
        btn.innerHTML = `${createSpinner('w-5 h-5 inline mr-2')} 🧠 AI is analyzing...`;
        emptyState.innerHTML = createSkeleton();

        // Classify image
        const result = await classifyCartoonImage(classifyFile, (status) => {
            console.log('Progress:', status);
        });

        // Show results
        emptyState.classList.add('hidden');
        actionsContainer.classList.remove('hidden');

        // Display top 5 predictions
        const predictions = result.predictions || [];
        const topPredictions = predictions.slice(0, 5);

        resultsContainer.innerHTML = topPredictions.map((pred, index) => {
            const confidence = pred.confidence * 100;
            const color = getConfidenceColor(confidence);

            return `
                <div class="glass rounded-xl p-4 border border-white/10 hover:border-purple-500/50 transition-all duration-300">
                    <div class="flex items-center gap-4">
                        <div class="w-10 h-10 rounded-full bg-gradient-to-br ${color} flex items-center justify-center font-bold text-lg">
                            ${index + 1}
                        </div>
                        <div class="flex-1">
                            <div class="font-semibold mb-1">${pred.celebrity_name}</div>
                            ${createProgressBar(confidence, 'Confidence')}
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        showToast('Classification completed!', 'success');

        // Reload gallery
        loadGallery();

    } catch (error) {
        console.error('Classify error:', error);
        showToast(error.message || 'Classification failed', 'error');

        emptyState.innerHTML = `
            <svg class="w-24 h-24 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
            <p class="text-gray-400">Results will appear here</p>
        `;
        emptyState.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🔍 Identify Celebrity';
    }
}

// Handle Generate
async function handleGenerate() {
    if (!generateFile) {
        showToast('Please select an image first', 'error');
        return;
    }

    const btn = document.getElementById('generate-btn');
    const resultContainer = document.getElementById('generate-result');
    const emptyState = document.getElementById('generate-empty');

    try {
        // Update UI
        btn.disabled = true;
        btn.innerHTML = `${createSpinner('w-5 h-5 inline mr-2')} Generating...`;
        emptyState.innerHTML = createSkeleton();

        // Generate cartoon
        const result = await generateCartoonImage(generateFile, (status) => {
            console.log('Progress:', status);
        });

        console.log('Generate result:', result);

        // Show result - use the imageUrl from the response
        emptyState.innerHTML = `
            <div class="w-full">
                <div class="mb-4">
                    <span class="text-sm font-semibold">🎨 AI-Generated Cartoon</span>
                </div>
                <img id="generate-result-img" src="${result.imageUrl}" alt="Generated" class="w-full h-auto rounded-xl shadow-2xl mb-4">
                <div class="flex gap-3">
                    <button onclick="downloadGeneratedImage()" class="flex-1 px-4 py-3 bg-gradient-to-r from-green-600 to-emerald-600 rounded-xl font-semibold hover:scale-105 transition-all duration-300">
                        📥 Download
                    </button>
                    <button onclick="copyToClipboard('${result.imageUrl}')" class="flex-1 px-4 py-3 border border-white/20 rounded-xl font-semibold hover:bg-white/10 transition-all duration-300">
                        🔗 Copy Link
                    </button>
                </div>
            </div>
        `;

        showToast('Generation completed!', 'success');

    } catch (error) {
        console.error('Generate error:', error);
        showToast(error.message || 'Generation failed', 'error');

        emptyState.innerHTML = `
            <svg class="w-24 h-24 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
            <p class="text-gray-400">Generated artwork will appear here</p>
        `;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🎨 Generate Cartoon';
    }
}

// Download transform result
function downloadTransformResult() {
    const resultImg = document.getElementById('transform-result-img');
    const jobId = resultImg.dataset.jobId;

    if (jobId) {
        downloadResult(jobId, 'toonify-transform.png');
    }
}

// Share transform result
function shareTransformResult() {
    const resultImg = document.getElementById('transform-result-img');
    const jobId = resultImg.dataset.jobId;

    if (jobId) {
        const shareUrl = `${window.location.origin}/share/${jobId}`;
        copyToClipboard(shareUrl);
    }
}

// Download generated image
function downloadGeneratedImage() {
    const resultImg = document.getElementById('generate-result-img');
    if (resultImg && resultImg.src) {
        // Fetch the blob URL and download
        fetch(resultImg.src)
            .then(res => res.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'generated-cartoon.png';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                showToast('Download started!', 'success');
            })
            .catch(error => {
                console.error('Download error:', error);
                showToast('Failed to download image', 'error');
            });
    }
}

// Clear classify results
function clearClassifyResults() {
    const resultsContainer = document.getElementById('classify-results');
    const emptyState = document.getElementById('classify-empty');
    const actionsContainer = document.getElementById('classify-actions');

    resultsContainer.innerHTML = '';
    emptyState.classList.remove('hidden');
    actionsContainer.classList.add('hidden');

    removeClassifyImage();
}

// Save classify result
function saveClassifyResult() {
    showToast('Result saved to gallery!', 'success');
}

// Load gallery
async function loadGallery() {
    const galleryGrid = document.getElementById('gallery-grid');
    const galleryEmpty = document.getElementById('gallery-empty');

    if (!galleryGrid) return;

    try {
        // Show loading
        galleryGrid.innerHTML = Array(6).fill(0).map(() => `
            <div class="glass rounded-2xl p-4">
                ${createSkeleton('48')}
            </div>
        `).join('');

        // Fetch jobs
        const jobs = await getAllJobs();
        currentJobs = jobs;

        if (jobs.length === 0) {
            galleryGrid.innerHTML = '';
            galleryEmpty.classList.remove('hidden');
            return;
        }

        galleryEmpty.classList.add('hidden');

        // Display jobs
        galleryGrid.innerHTML = jobs.map(job => {
            const statusBadge = getStatusBadge(job.status);
            const styleIcon = getStyleIcon(job.style || 'cartoon');
            const styleName = getStyleName(job.style || 'cartoon');

            return `
                <div class="group glass rounded-2xl overflow-hidden hover:border-purple-500/50 transition-all duration-300">
                    <div class="relative">
                        <img data-job-id="${job.id}" src="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 400 300%22%3E%3Crect fill=%22%23374151%22 width=%22400%22 height=%22300%22/%3E%3Ctext fill=%22%239CA3AF%22 font-family=%22sans-serif%22 font-size=%2218%22 text-anchor=%22middle%22 x=%22200%22 y=%22150%22%3ELoading...%3C/text%3E%3C/svg%3E" alt="${job.original_filename}" class="w-full h-64 object-cover gallery-image">
                        <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end justify-center p-4 gap-2">
                            <button onclick="viewJob('${job.id}')" class="px-4 py-2 bg-white/20 backdrop-blur-xl rounded-lg hover:bg-white/30 transition-colors">
                                👁️ View
                            </button>
                            ${job.status === 'completed' ? `
                                <button onclick="downloadResult('${job.id}', '${job.original_filename}')" class="px-4 py-2 bg-white/20 backdrop-blur-xl rounded-lg hover:bg-white/30 transition-colors">
                                    📥 Download
                                </button>
                            ` : ''}
                            <button onclick="deleteJobConfirm('${job.id}')" class="px-4 py-2 bg-red-500/80 backdrop-blur-xl rounded-lg hover:bg-red-600/80 transition-colors">
                                🗑️ Delete
                            </button>
                        </div>
                    </div>
                    <div class="p-4">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs text-gray-400">Job #${job.id}</span>
                            ${statusBadge}
                        </div>
                        <div class="flex items-center gap-2 mb-2">
                            <span class="text-lg">${styleIcon}</span>
                            <span class="text-sm font-medium">${styleName}</span>
                        </div>
                        <div class="text-xs text-gray-400 truncate">${job.original_filename}</div>
                        <div class="text-xs text-gray-500 mt-1">${formatDate(job.created_at)}</div>
                    </div>
                </div>
            `;
        }).join('');

        // Load authenticated images for gallery
        const galleryImages = document.querySelectorAll('.gallery-image');
        galleryImages.forEach(async (img) => {
            const jobId = img.dataset.jobId;
            if (jobId) {
                try {
                    const imageUrl = await loadAuthenticatedImage(jobId, 'processed');
                    img.src = imageUrl;
                } catch (error) {
                    console.error(`Failed to load image for job ${jobId}:`, error);
                    img.src = "data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 400 300%22%3E%3Crect fill=%22%23374151%22 width=%22400%22 height=%22300%22/%3E%3Ctext fill=%22%239CA3AF%22 font-family=%22sans-serif%22 font-size=%2224%22 text-anchor=%22middle%22 x=%22200%22 y=%22150%22%3ENo Image%3C/text%3E%3C/svg%3E";
                }
            }
        });

    } catch (error) {
        console.error('Failed to load gallery:', error);
        galleryGrid.innerHTML = `
            <div class="col-span-full text-center py-12">
                <p class="text-gray-400">Failed to load gallery</p>
                <button onclick="loadGallery()" class="mt-4 px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl hover:scale-105 transition-all duration-300">
                    Retry
                </button>
            </div>
        `;
    }
}

// View job details
function viewJob(jobId) {
    showToast('Opening job details...', 'info');
    // TODO: Implement modal with job details
}

// Delete job with confirmation
function deleteJobConfirm(jobId) {
    if (confirm('Are you sure you want to delete this job?')) {
        deleteJobById(jobId);
    }
}

// Delete job
async function deleteJobById(jobId) {
    console.log('Deleting job:', jobId);
    try {
        const result = await deleteJob(jobId);
        console.log('Delete result:', result);
        showToast('Job deleted successfully', 'success');
        loadGallery();
    } catch (error) {
        console.error('Delete error:', error);
        showToast(error.message || 'Failed to delete job', 'error');
    }
}

// Toggle user menu
function toggleUserMenu() {
    const menu = document.getElementById('user-menu');
    menu.classList.toggle('hidden');
}

// Close user menu when clicking outside
document.addEventListener('click', function (e) {
    const menu = document.getElementById('user-menu');
    const button = menu?.previousElementSibling;

    if (menu && !menu.contains(e.target) && !button?.contains(e.target)) {
        menu.classList.add('hidden');
    }
});

// Share result
function shareResult(jobId) {
    const shareUrl = `${window.location.origin}/share/${jobId}`;
    copyToClipboard(shareUrl);
}
