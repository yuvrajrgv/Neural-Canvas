# Troubleshooting Guide - Neuralcanvas AI Frontend

## ✅ Fixed Issues

### Issue 1: Transform Image Not Showing
**Problem**: After transformation completes, the result image doesn't display.

**Root Cause**: The result object from the backend uses `id` property, not `job_id`.

**Fix Applied**:
```javascript
// Before (WRONG)
resultImg.src = `${API_BASE}/images/file/${result.job_id}/processed`;

// After (CORRECT)
const jobId = result.id;
resultImg.src = `${API_BASE}/images/file/${jobId}/processed`;
```

**Files Modified**: `js/main.js` (lines 217-221)

---

### Issue 2: Download Not in Correct Format (JPEG/PNG)
**Problem**: Downloaded files always save as `.png` regardless of original format.

**Root Cause**: The download function wasn't reading the `Content-Disposition` header from the backend response, which contains the correct filename with extension.

**Fix Applied**:
```javascript
// Extract filename from Content-Disposition header
const contentDisposition = response.headers.get('Content-Disposition');
let downloadFilename = filename || 'toonify-result.png';

if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
    if (filenameMatch && filenameMatch[1]) {
        downloadFilename = filenameMatch[1].replace(/['"]/g, '');
    }
}
```

**Backend Response Example**:
```
Content-Disposition: attachment; filename="photo_toonified.jpg"
```

**Files Modified**: `js/api.js` (downloadResult function)

---

## Backend Response Structure

### Job Details Response
```json
{
  "id": 123,                           // ← Use this for job ID
  "original_filename": "photo.jpg",
  "style": "cartoon",
  "status": "completed",
  "created_at": "2026-01-10T00:00:00",
  "processed_at": "2026-01-10T00:00:10",
  "error_message": null,
  "original_url": "/images/file/123/original",
  "processed_url": "/images/file/123/processed",
  "comparison_url": "/images/file/123/comparison",
  "download_count": 0
}
```

### Key Points:
- ✅ Job ID is in `id` property (not `job_id`)
- ✅ Filename is in `original_filename` property
- ✅ Image URLs use `/images/file/{id}/{type}` format
- ✅ Download endpoint: `/images/download/{id}`

---

## Image Display URLs

### Correct URL Format
```javascript
// Original image
`${API_BASE}/images/file/${jobId}/original`

// Processed/transformed image
`${API_BASE}/images/file/${jobId}/processed`

// Side-by-side comparison
`${API_BASE}/images/file/${jobId}/comparison`
```

### Example
```javascript
const jobId = 123;
const imageUrl = `http://localhost:8000/images/file/123/processed`;
```

---

## Download Flow

### Complete Download Process
1. **Frontend calls**: `downloadResult(jobId, filename)`
2. **Fetches from**: `GET /images/download/{jobId}`
3. **Backend returns**:
   - File as blob
   - `Content-Disposition: attachment; filename="photo_toonified.jpg"`
4. **Frontend**:
   - Extracts filename from header
   - Creates blob URL
   - Triggers download with correct filename

### Code Flow
```javascript
fetch(`${API_BASE}/images/download/${jobId}`)
  .then(response => {
    // Extract filename from header
    const header = response.headers.get('Content-Disposition');
    // Parse: filename="photo_toonified.jpg"
    return response.blob().then(blob => ({ blob, filename }));
  })
  .then(({ blob, filename }) => {
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.download = filename; // ← Correct extension preserved
    a.click();
  });
```

---

## Debugging Tips

### Check Browser Console
Open DevTools (F12) and look for:

1. **Upload Response**:
```javascript
console.log('Upload result:', uploadResult);
// Should show: { job_id: 123, message: "...", original_url: "..." }
```

2. **Transform Result**:
```javascript
console.log('Transform complete, result:', result);
// Should show: { id: 123, status: "completed", processed_url: "...", ... }
```

3. **Image URL**:
```javascript
console.log('Image URL:', resultImg.src);
// Should be: http://localhost:8000/images/file/123/processed
```

### Check Network Tab
1. Open DevTools → Network tab
2. Transform an image
3. Look for:
   - `POST /images/upload` → Returns job_id
   - `POST /images/{id}/process` → Starts processing
   - `GET /images/{id}` → Polls status (every 1s)
   - `GET /images/file/{id}/processed` → Loads result image
   - `GET /images/download/{id}` → Downloads file

### Common Issues

**Image doesn't load**:
- ✅ Check if `result.id` exists
- ✅ Verify URL: `http://localhost:8000/images/file/{id}/processed`
- ✅ Check backend logs for errors
- ✅ Ensure job status is "completed"

**Download wrong extension**:
- ✅ Check `Content-Disposition` header in Network tab
- ✅ Verify backend returns correct header
- ✅ Check browser console for filename extraction

**404 on image URL**:
- ✅ Verify backend processed the image successfully
- ✅ Check if processed file exists in backend storage
- ✅ Ensure correct job ID is being used

---

## Testing Checklist

### Transform Tab
- [x] Upload image (drag & drop or click)
- [x] Select style from dropdown
- [x] Click "Transform Image"
- [x] See loading state
- [x] Result image displays correctly
- [x] Download button works
- [x] Downloaded file has correct extension (.jpg, .png, etc.)

### Gallery Tab
- [x] Images display in grid
- [x] Correct status badges
- [x] Download works from gallery
- [x] Delete works
- [x] Correct filenames shown

---

## File Extension Mapping

The backend preserves the original file extension:

| Original File | Processed File | Download Name |
|--------------|----------------|---------------|
| photo.jpg | photo_processed.jpg | photo_toonified.jpg |
| image.png | image_processed.png | image_toonified.png |
| pic.webp | pic_processed.webp | pic_toonified.webp |

The extension is determined by the backend based on the processed file's actual format.

---

## Summary of Changes

### Files Modified
1. **js/api.js**
   - Fixed `downloadResult()` to extract filename from headers
   - Added console logging in `transformImage()`
   - Improved error handling

2. **js/main.js**
   - Fixed result image URL to use `result.id`
   - Fixed job ID storage for download
   - Fixed generate tab to use consistent ID property
   - Added debug logging

### What Now Works
✅ Transform image displays correctly  
✅ Download preserves original file extension  
✅ Proper error handling  
✅ Console logging for debugging  

---

**Both issues are now resolved!** 🎉

The transformed image will display correctly, and downloads will have the proper file extension (JPEG, PNG, WEBP, etc.) based on the original file format.
