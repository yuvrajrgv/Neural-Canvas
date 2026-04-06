# API Endpoint Mapping - Frontend to Backend

## ✅ Fixed API Endpoints

The frontend has been updated to match your actual backend API structure.

### Authentication Endpoints

| Frontend Call | Backend Endpoint | Method | Description |
|--------------|------------------|--------|-------------|
| `handleSignIn()` | `/auth/login/form` | POST | Login with username/password (OAuth2 form) |
| `handleSignUp()` | `/auth/signup` | POST | Register new user account |

### Image Processing Endpoints

| Frontend Call | Backend Endpoint | Method | Description |
|--------------|------------------|--------|-------------|
| `uploadImage(file, style)` | `/images/upload` | POST | Upload image with style parameter |
| `processTransformation(jobId, style)` | `/images/{job_id}/process?style={style}` | POST | Start processing uploaded image |
| `getJobDetails(jobId)` | `/images/{job_id}` | GET | Get job details and status |
| `getAllJobs()` | `/images/` | GET | List all user's jobs |
| `deleteJob(jobId)` | `/images/{job_id}` | DELETE | Delete a job |
| `downloadResult(jobId)` | `/images/download/{job_id}` | GET | Download processed image |

### Image File Serving

| Type | Backend Endpoint | Description |
|------|------------------|-------------|
| Original | `/images/file/{job_id}/original` | Get original uploaded image |
| Processed | `/images/file/{job_id}/processed` | Get processed/transformed image |
| Comparison | `/images/file/{job_id}/comparison` | Get side-by-side comparison |

### Cartoon Processing (if available)

| Frontend Call | Backend Endpoint | Method | Description |
|--------------|------------------|--------|-------------|
| `classifyCartoonImage(file)` | `/cartoon/classify` | POST | Classify celebrity in cartoon |
| `generateCartoonImage(file)` | `/cartoon/generate` | POST | Generate cartoon using GAN |

## Backend Response Structures

### Upload Response
```json
{
  "job_id": 123,
  "message": "Image uploaded successfully",
  "original_url": "/images/file/123/original"
}
```

### Job Details Response
```json
{
  "id": 123,
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

### Jobs List Response
```json
{
  "jobs": [
    {
      "id": 123,
      "original_filename": "photo.jpg",
      "style": "cartoon",
      "status": "completed",
      "created_at": "2026-01-10T00:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

## Status Values

- `pending` - Job created, waiting to process
- `processing` - Currently being processed
- `completed` - Successfully completed
- `failed` - Processing failed

## Style Values

Available transformation styles:
- `cartoon` - Classic cartoon effect
- `pencil_sketch` - Grayscale pencil sketch
- `color_pencil` - Colored pencil artistic style
- `edge_preserve` - Edge-preserving smooth effect
- `watercolor` - Soft watercolor painting effect

## Authentication Flow

1. User signs up: `POST /auth/signup`
   - Returns access_token and refresh_token
   
2. User signs in: `POST /auth/login/form`
   - Returns access_token and refresh_token
   
3. All subsequent requests include:
   ```
   Authorization: Bearer {access_token}
   ```

4. If 401 Unauthorized:
   - Frontend clears tokens
   - Redirects to login page

## Image Processing Flow

1. **Upload**: `POST /images/upload` with file and style
   - Returns job_id
   
2. **Process**: `POST /images/{job_id}/process`
   - Starts background processing
   - Job status changes to "processing"
   
3. **Poll Status**: `GET /images/{job_id}` every 1 second
   - Check status field
   - When status === "completed", show result
   
4. **Display Result**: Use `/images/file/{job_id}/processed`
   - Show in img tag
   
5. **Download**: `GET /images/download/{job_id}`
   - Downloads file with proper filename

## Changes Made to Frontend

### ✅ Fixed Files

1. **js/auth.js**
   - Changed `/api/v1/auth/login` → `/auth/login/form`
   - Changed `/api/v1/auth/register` → `/auth/signup`

2. **js/api.js**
   - Completely rewrote to match backend structure
   - Changed all `/api/v1/images/*` → `/images/*`
   - Updated upload to include style parameter
   - Fixed job polling to use correct endpoints

3. **js/main.js**
   - Updated image URLs to use `/images/file/{id}/processed`
   - Fixed job property names (job_id → id, filename → original_filename)
   - Updated gallery display logic

## Testing Checklist

- [x] Sign up works
- [x] Sign in works
- [x] Upload image works
- [x] Transform image works
- [x] View result works
- [x] Download works
- [x] Gallery loads
- [x] Delete job works

## Backend Must Be Running

Make sure your backend is running on `http://localhost:8000`:

```bash
cd backend
uvicorn app.main:app --reload
```

Then access frontend:
- Landing: `file:///path/to/frontend/index.html`
- Or use local server: `python -m http.server 8080`

---

**All API endpoints are now correctly mapped to your backend!** 🎉
