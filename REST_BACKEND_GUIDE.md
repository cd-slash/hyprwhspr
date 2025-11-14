# REST API Transcription Backend

This guide explains how to use the new remote REST API transcription backend as an alternative to the local pywhispercpp model.

## Overview

The application now supports two transcription backends:

- **local** (default): Uses local pywhispercpp model
- **remote**: Sends audio to a REST API endpoint for transcription

## Configuration

Edit your config file at `~/.config/hyprwhspr/config.json`:

### Using Local Backend (Default)

```json
{
  "transcription_backend": "local",
  "model": "base",
  "threads": 4
}
```

### Using Remote REST API Backend

```json
{
  "transcription_backend": "remote",
  "rest_endpoint_url": "https://your-api.example.com/transcribe",
  "rest_api_key": "your-api-key-here",
  "rest_timeout": 30
}
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `transcription_backend` | string | `"local"` | Backend to use: `"local"` or `"remote"` |
| `rest_endpoint_url` | string | `null` | Full HTTPS URL of your transcription API endpoint |
| `rest_api_key` | string | `null` | Optional API key for authentication (sent as Bearer token) |
| `rest_timeout` | number | `30` | Request timeout in seconds (1-300) |
| `rest_audio_format` | string | `"wav"` | Audio format for uploads (currently only WAV supported) |

## REST API Requirements

Your REST endpoint should accept:

### Request Format

**HTTP Method:** POST

**Content-Type:** multipart/form-data

**Headers:**
- `Authorization: Bearer {api_key}` (if API key is configured)

**Form Data:**
- `file`: Audio file (WAV format, 16kHz mono, 16-bit)
- `language`: Language code (optional, if configured in hyprwhspr)

### Response Format

The API should return JSON with the transcription in one of these formats:

**Option 1:**
```json
{
  "text": "transcribed text here"
}
```

**Option 2:**
```json
{
  "transcription": "transcribed text here"
}
```

**Option 3:**
```json
{
  "result": "transcribed text here"
}
```

### Error Responses

Return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid audio format)
- `401`: Unauthorized (invalid API key)
- `429`: Rate limit exceeded
- `500`: Internal server error

## Audio Format Details

The application converts captured audio to WAV format before sending:
- **Sample Rate:** 16000 Hz (16 kHz)
- **Channels:** 1 (mono)
- **Bit Depth:** 16-bit
- **Format:** PCM WAV

## Example: Using OpenAI Whisper API

```json
{
  "transcription_backend": "remote",
  "rest_endpoint_url": "https://api.openai.com/v1/audio/transcriptions",
  "rest_api_key": "sk-your-openai-api-key",
  "rest_timeout": 30
}
```

Note: For OpenAI, you may need to adjust the endpoint parameter format. The implementation uses standard multipart file uploads.

## Example: Custom REST API

Here's a minimal Python Flask example for a custom REST endpoint:

```python
from flask import Flask, request, jsonify
import whisper

app = Flask(__name__)
model = whisper.load_model("base")

@app.route('/transcribe', methods=['POST'])
def transcribe():
    # Check authorization
    auth_header = request.headers.get('Authorization')
    if auth_header != 'Bearer your-secret-key':
        return jsonify({'error': 'Unauthorized'}), 401

    # Get the audio file
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    audio_file = request.files['file']

    # Save temporarily and transcribe
    temp_path = '/tmp/audio.wav'
    audio_file.save(temp_path)

    result = model.transcribe(temp_path)

    return jsonify({'text': result['text']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Error Handling

The remote backend includes comprehensive error handling:

- **Connection Errors:** If the API is unreachable, returns empty string
- **Timeout:** If request exceeds configured timeout, returns empty string
- **HTTP Errors:** Non-200 status codes are logged with details
- **Invalid Response:** If response format is unrecognized, returns empty string

All errors are logged to console for debugging.

## Performance Considerations

### Local Backend
- ✅ No network latency
- ✅ Works offline
- ✅ Free to use
- ❌ Requires local GPU/CPU resources
- ❌ Limited to available models

### Remote Backend
- ✅ Offloads computation to server
- ✅ Can use more powerful models
- ✅ No local resource usage
- ❌ Requires internet connection
- ❌ Network latency (typically 0.5-5 seconds)
- ❌ May have API costs

## Switching Backends

You can switch between backends by simply changing the `transcription_backend` setting in your config file. The application will automatically use the appropriate backend on the next recording.

No restart required - the backend is selected for each transcription request.

## Troubleshooting

### Remote backend not working?

1. Check your config file: `~/.config/hyprwhspr/config.json`
2. Verify `rest_endpoint_url` is correct and includes `https://` or `http://`
3. Test the endpoint manually:
   ```bash
   curl -X POST https://your-api.example.com/transcribe \
     -H "Authorization: Bearer your-api-key" \
     -F "file=@test.wav"
   ```
4. Check application logs for error messages
5. Try increasing `rest_timeout` if requests are timing out

### Testing the configuration

Run the validation script:
```bash
python3 test_backend_validation.py
```

This validates the code structure without requiring full dependency installation.

## Security Notes

- Always use HTTPS endpoints (not HTTP) for production
- Keep your API keys secure - don't commit them to git
- Consider using environment variables for sensitive data
- Validate SSL certificates are properly configured

## Implementation Details

### Files Modified

- `lib/src/config_manager.py`: Added REST configuration options
- `lib/src/whisper_manager.py`: Added REST backend implementation

### Key Methods

- `_numpy_to_wav_bytes()`: Converts numpy audio to WAV format
- `_transcribe_rest()`: Sends audio to REST API and parses response
- `transcribe_audio()`: Routes to appropriate backend
- `initialize()`: Validates REST configuration

### Dependencies

- `requests`: HTTP library (already in requirements.txt)
- `wave`: WAV file handling (Python standard library)
- `io.BytesIO`: In-memory file handling (Python standard library)

## Future Enhancements

Potential future improvements:
- Support for other audio formats (MP3, FLAC, OGG)
- Fallback to local backend on network failure
- Response caching
- Multiple REST endpoints with load balancing
- WebSocket streaming for real-time transcription
- Support for other API formats (JSON with base64)
