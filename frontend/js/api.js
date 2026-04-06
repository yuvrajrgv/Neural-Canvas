// API Client for Toonify AI - Updated to match backend routes

const API_BASE = 'http://localhost:8000';

// Get auth token
function getAuthToken() {
    return localStorage.getItem('access_token');
}

// Check if user is authenticated
function isAuthenticated() {
    return !!getAuthToken();
}

// Redirect to login if not authenticated
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

// Generic API request function
async function apiRequest(endpoint, options = {}) {
    const token = getAuthToken();

    const config = {
        ...options,
        headers: {
            ...options.headers,
            ...(token && { 'Authorization': `Bearer ${token}` }),
        },
    };

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, config);

        // Handle 401 Unauthorized
        if (response.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('token_type');
            window.location.href = 'index.html';
            throw new Error('Session expired. Please sign in again.');
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Request failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Upload image with style
async function uploadImage(file, style = 'cartoon') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('style', style);

    return await apiRequest('/images/upload', {
        method: 'POST',
        body: formData,
    });
}

// Process image transformation
async function processTransformation(jobId, style) {
    return await apiRequest(`/images/${jobId}/process?style=${style}`, {
        method: 'POST',
    });
}

// Get job details
async function getJobDetails(jobId) {
    return await apiRequest(`/images/${jobId}`);
}

// Get all jobs
async function getAllJobs() {
    const response = await apiRequest('/images/');
    return response.jobs || [];
}

// Delete job
async function deleteJob(jobId) {
    return await apiRequest(`/images/${jobId}`, {
        method: 'DELETE',
    });
}

// Download result - FIXED to handle proper file extension
function downloadResult(jobId, filename) {
    const token = getAuthToken();
    const url = `${API_BASE}/images/download/${jobId}`;

    fetch(url, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Download failed');
            }

            // Get filename from Content-Disposition header if available
            const contentDisposition = response.headers.get('Content-Disposition');
            let downloadFilename = filename || 'toonify-result.png';

            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (filenameMatch && filenameMatch[1]) {
                    downloadFilename = filenameMatch[1].replace(/['"]/g, '');
                }
            }

            return response.blob().then(blob => ({ blob, filename: downloadFilename }));
        })
        .then(({ blob, filename: downloadFilename }) => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = downloadFilename;
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

// Poll job status until completion
async function pollJobStatus(jobId, onProgress) {
    return new Promise((resolve, reject) => {
        const interval = setInterval(async () => {
            try {
                const job = await getJobDetails(jobId);

                // Call progress callback if provided
                if (onProgress) {
                    onProgress(job);
                }

                if (job.status === 'completed') {
                    clearInterval(interval);
                    resolve(job);
                } else if (job.status === 'failed') {
                    clearInterval(interval);
                    reject(new Error(job.error_message || 'Job failed'));
                }
            } catch (error) {
                clearInterval(interval);
                reject(error);
            }
        }, 1000); // Poll every second

        // Timeout after 5 minutes
        setTimeout(() => {
            clearInterval(interval);
            reject(new Error('Job timeout'));
        }, 300000);
    });
}

// Transform image (complete flow) - FIXED
async function transformImage(file, style, onProgress) {
    try {
        // Upload with style - backend will create job
        const uploadResult = await uploadImage(file, style);
        const jobId = uploadResult.job_id;

        console.log('Upload result:', uploadResult);
        console.log('Job ID:', jobId);

        // Start processing
        await processTransformation(jobId, style);

        // Poll for completion
        const result = await pollJobStatus(jobId, onProgress);

        console.log('Final result:', result);

        // Return the complete job details
        return result;
    } catch (error) {
        console.error('Transform error:', error);
        throw error;
    }
}

// Classify cartoon - FIXED to handle direct response
async function classifyCartoonImage(file, onProgress) {
    try {
        const formData = new FormData();
        formData.append('file', file);

        // Cartoon classify returns predictions directly (not a job)
        const result = await apiRequest('/cartoon/classify', {
            method: 'POST',
            body: formData,
        });

        console.log('Classify result:', result);

        // Result structure: { success: true, predictions: [...], message: "..." }
        return result;
    } catch (error) {
        console.error('Classify error:', error);
        throw error;
    }
}

// Generate cartoon - FIXED to handle image response
async function generateCartoonImage(file, onProgress) {
    try {
        const token = getAuthToken();
        const formData = new FormData();
        formData.append('file', file);

        // The generate endpoint returns the image directly (not JSON)
        const response = await fetch(`${API_BASE}/cartoon/generate`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Generation failed' }));
            throw new Error(error.detail || 'Generation failed');
        }

        // Get the image blob
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);

        console.log('Generate result - image URL:', imageUrl);

        // Return an object with the image URL
        return {
            success: true,
            imageUrl: imageUrl,
            message: 'Cartoon generated successfully'
        };
    } catch (error) {
        console.error('Generate error:', error);
        throw error;
    }
}

// Get user statistics
async function getUserStats() {
    try {
        const jobs = await getAllJobs();

        const stats = {
            total: jobs.length,
            completed: jobs.filter(j => j.status === 'completed').length,
            processing: jobs.filter(j => j.status === 'processing').length,
            failed: jobs.filter(j => j.status === 'failed').length,
        };

        return stats;
    } catch (error) {
        console.error('Failed to get stats:', error);
        return {
            total: 0,
            completed: 0,
            processing: 0,
            failed: 0,
        };
    }
}
