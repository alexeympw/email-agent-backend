# Email Newsletter Backend API Documentation

## Overview
Backend service for email newsletter campaigns with background processing, SMTP integration, and progress tracking. Built with FastAPI, Celery, Redis, and PostgreSQL.

**Base URL:** `https://aiemailnewsletter-5f12f604df43.herokuapp.com`

### Key Features
- ✅ **SMTP Verification** - Test credentials before sending
- ✅ **Campaign Management** - Create, start, pause, and resume campaigns
- ✅ **Rate Limiting** - Control sending speed to respect provider limits
- ✅ **Real-time Progress** - Track campaign status and progress
- ✅ **Background Processing** - Asynchronous email sending with Celery
- ✅ **Campaign Control** - Pause/resume functionality for long-running campaigns
- ✅ **User Management** - Default admin user system (API keys coming soon)

### Database Schema
The system uses the following main entities:
- **Users**: Admin users who can create campaigns
- **ApiKeys**: API keys for authentication (future feature)
- **Campaigns**: Email campaigns with SMTP settings and content
- **Recipients**: Email recipients for each campaign
- **SentEmails**: Log of all sent emails with delivery status

## Authentication
Currently using a default admin user system. All campaigns are automatically associated with the default admin user (`a@aiemailnewsletter.com`). Future versions will include API key authentication.

## Quick Start

### 1. Verify SMTP Settings
```bash
curl -X POST "https://aiemailnewsletter-5f12f604df43.herokuapp.com/smtp/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "smtp_host": "your-smtp-host",
    "smtp_port": 465,
    "smtp_username": "your-username",
    "smtp_password": "your-password",
    "smtp_tls": false,
    "smtp_ssl": true
  }'
```

### 2. Create Campaign
```bash
curl -X POST "https://aiemailnewsletter-5f12f604df43.herokuapp.com/campaigns/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Campaign",
    "subject": "Hello World",
    "body": "This is a test email",
    "limits_count": 1,
    "limits_window_seconds": 60,
    "smtp": { /* same SMTP config */ },
    "recipients": [
      {"to_email": "test@example.com", "to_name": "Test User"}
    ]
  }'
```

### 3. Start Campaign
```bash
curl -X POST "https://aiemailnewsletter-5f12f604df43.herokuapp.com/campaigns/{campaign_id}/start"
```

### 4. Monitor Progress
```bash
curl "https://aiemailnewsletter-5f12f604df43.herokuapp.com/campaigns/{campaign_id}/status"
```

## Endpoints

### 1. Health Check
**GET** `/ping`

Check if the service is running.

**Response:**
```json
{
  "status": "ok"
}
```

### 2. SMTP Verification
**POST** `/smtp/verify`

Test SMTP credentials before creating campaigns.

**Request Body:**
```json
{
  "smtp_host": "es22.siteground.eu",
  "smtp_port": 465,
  "smtp_username": "collaborate@upvote.club",
  "smtp_password": "fK$^4y$q4Iz@",
  "smtp_tls": false,
  "smtp_ssl": true
}
```

**Parameters:**
- `smtp_host` (string, required): SMTP server hostname
- `smtp_port` (integer, required): SMTP server port (587 for STARTTLS, 465 for SSL)
- `smtp_username` (string, required): SMTP username
- `smtp_password` (string, required): SMTP password
- `smtp_tls` (boolean, optional): Use STARTTLS (default: true)
- `smtp_ssl` (boolean, optional): Use SSL connection (default: false)

**Response:**
```json
{
  "ok": true,
  "detail": null
}
```

**Error Response:**
```json
{
  "ok": false,
  "detail": "Authentication failed"
}
```

### 3. Create Campaign
**POST** `/campaigns/`

Create a new email campaign with recipients and SMTP settings. The campaign will be automatically associated with the default admin user.

**Request Body:**
```json
{
  "name": "October Newsletter",
  "from_email": "collaborate@upvote.club",
  "from_name": "Upvote Club",
  "subject": "Hello from Upvote Club",
  "body": "This is our monthly newsletter content.",
  "limits_count": 1,
  "limits_window_seconds": 3600,
  "smtp": {
    "smtp_host": "es22.siteground.eu",
    "smtp_port": 465,
    "smtp_username": "collaborate@upvote.club",
    "smtp_password": "fK$^4y$q4Iz@",
    "smtp_tls": false,
    "smtp_ssl": true
  },
  "recipients": [
    {
      "to_email": "user1@example.com",
      "to_name": "John Doe"
    },
    {
      "to_email": "user2@example.com",
      "to_name": "Jane Smith"
    }
  ]
}
```

**Parameters:**
- `name` (string, required): Campaign name
- `from_email` (string, optional): Sender email address
- `from_name` (string, optional): Sender display name
- `subject` (string, required): Email subject line
- `body` (string, required): Email body content
- `limits_count` (integer, required): Number of emails to send per time window (min: 1)
- `limits_window_seconds` (integer, required): Time window in seconds (min: 1)
- `smtp` (object, required): SMTP configuration (same as verify endpoint)
- `recipients` (array, required): List of recipients

**Response:**
```json
{
  "id": 1,
  "name": "October Newsletter"
}
```

### 4. Start Campaign
**POST** `/campaigns/{campaign_id}/start`

Start sending emails for a campaign. This triggers background processing.

**Parameters:**
- `campaign_id` (integer, path): Campaign ID from create response

**Response:**
```json
{
  "status": "started",
  "id": 1
}
```

**Error Responses:**
- `404`: Campaign not found
- `400`: Campaign already running or completed
- `400`: No recipients found

### 5. Pause Campaign
**POST** `/campaigns/{campaign_id}/pause`

Pause a running campaign. Stops sending emails but preserves progress.

**Parameters:**
- `campaign_id` (integer, path): Campaign ID

**Response:**
```json
{
  "status": "paused",
  "id": 1
}
```

**Error Responses:**
- `404`: Campaign not found
- `400`: Campaign is not running

### 6. Resume Campaign
**POST** `/campaigns/{campaign_id}/resume`

Resume a paused campaign. Continues sending emails from where it left off.

**Parameters:**
- `campaign_id` (integer, path): Campaign ID

**Response:**
```json
{
  "status": "resumed",
  "id": 1
}
```

**Error Responses:**
- `404`: Campaign not found
- `400`: Campaign is not paused

### 7. Get Campaign Status
**GET** `/campaigns/{campaign_id}/status`

Get real-time progress of a campaign.

**Parameters:**
- `campaign_id` (integer, path): Campaign ID

**Response:**
```json
{
  "id": 1,
  "status": "running",
  "total": 100,
  "sent": 45,
  "failed": 2,
  "pending": 53,
  "progress_pct": 45.0
}
```

**Status Values:**
- `draft`: Campaign created but not started
- `running`: Campaign is actively sending emails
- `paused`: Campaign is paused (can be resumed)
- `completed`: All emails sent successfully
- `failed`: Campaign failed due to critical error

**Fields:**
- `total`: Total number of recipients
- `sent`: Successfully sent emails
- `failed`: Failed email attempts
- `pending`: Emails waiting to be sent
- `progress_pct`: Completion percentage (0-100)

## Rate Limiting

The system respects the `limits_count` and `limits_window_seconds` parameters:
- If `limits_count=1` and `limits_window_seconds=3600`, sends 1 email per hour
- If `limits_count=10` and `limits_window_seconds=60`, sends 10 emails per minute

## Error Handling

### Common HTTP Status Codes
- `200`: Success
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Internal Server Error

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

## Frontend Integration Guide

### 1. Campaign Creation Flow
```javascript
// 1. Verify SMTP first
const smtpVerify = await fetch('/smtp/verify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    smtp_host: 'your-smtp-host',
    smtp_port: 465,
    smtp_username: 'your-username',
    smtp_password: 'your-password',
    smtp_tls: false,
    smtp_ssl: true
  })
});

if (!smtpVerify.ok) {
  throw new Error('SMTP verification failed');
}

// 2. Create campaign (automatically associated with default admin user)
const campaign = await fetch('/campaigns/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'My Campaign',
    from_email: 'sender@example.com',
    from_name: 'My Company',
    subject: 'Newsletter Subject',
    body: 'Email content here...',
    limits_count: 1,
    limits_window_seconds: 3600,
    smtp: { /* same SMTP config */ },
    recipients: [
      { to_email: 'user@example.com', to_name: 'User Name' }
    ]
  })
});

const campaignData = await campaign.json();
const campaignId = campaignData.id;
```

### 2. Campaign Management
```javascript
// Start campaign
await fetch(`/campaigns/${campaignId}/start`, { method: 'POST' });

// Pause campaign
await fetch(`/campaigns/${campaignId}/pause`, { method: 'POST' });

// Resume campaign
await fetch(`/campaigns/${campaignId}/resume`, { method: 'POST' });

// Poll for status updates
const pollStatus = async (campaignId) => {
  const response = await fetch(`/campaigns/${campaignId}/status`);
  const status = await response.json();
  
  console.log(`Progress: ${status.progress_pct}%`);
  console.log(`Sent: ${status.sent}/${status.total}`);
  
  if (status.status === 'completed') {
    console.log('Campaign completed!');
    return;
  }
  
  if (status.status === 'failed') {
    console.log('Campaign failed!');
    return;
  }
  
  if (status.status === 'paused') {
    console.log('Campaign is paused');
    return;
  }
  
  // Continue polling if still running
  setTimeout(() => pollStatus(campaignId), 5000);
};

pollStatus(campaignId);
```

### 3. Complete Campaign Management Example
```javascript
class CampaignManager {
  constructor(campaignId) {
    this.campaignId = campaignId;
    this.isPolling = false;
  }

  async start() {
    const response = await fetch(`/campaigns/${this.campaignId}/start`, { method: 'POST' });
    return response.json();
  }

  async pause() {
    const response = await fetch(`/campaigns/${this.campaignId}/pause`, { method: 'POST' });
    return response.json();
  }

  async resume() {
    const response = await fetch(`/campaigns/${this.campaignId}/resume`, { method: 'POST' });
    return response.json();
  }

  async getStatus() {
    const response = await fetch(`/campaigns/${this.campaignId}/status`);
    return response.json();
  }

  startPolling(callback) {
    if (this.isPolling) return;
    
    this.isPolling = true;
    const poll = async () => {
      if (!this.isPolling) return;
      
      const status = await this.getStatus();
      callback(status);
      
      if (['completed', 'failed', 'paused'].includes(status.status)) {
        this.isPolling = false;
        return;
      }
      
      setTimeout(poll, 2000);
    };
    
    poll();
  }

  stopPolling() {
    this.isPolling = false;
  }
}

// Usage
const campaign = new CampaignManager(6);
await campaign.start();
campaign.startPolling((status) => {
  console.log(`Progress: ${status.progress_pct}% (${status.sent}/${status.total})`);
});
```

### 4. Real-time Progress Updates
```javascript
// React component example
const [campaignStatus, setCampaignStatus] = useState(null);

useEffect(() => {
  if (!campaignId) return;
  
  const interval = setInterval(async () => {
    const response = await fetch(`/campaigns/${campaignId}/status`);
    const status = await response.json();
    setCampaignStatus(status);
    
    if (status.status === 'completed' || status.status === 'failed' || status.status === 'paused') {
      clearInterval(interval);
    }
  }, 2000);
  
  return () => clearInterval(interval);
}, [campaignId]);
```

## SMTP Configuration Examples

### Gmail (STARTTLS)
```json
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your-email@gmail.com",
  "smtp_password": "your-app-password",
  "smtp_tls": true,
  "smtp_ssl": false
}
```

### SiteGround (SSL)
```json
{
  "smtp_host": "es22.siteground.eu",
  "smtp_port": 465,
  "smtp_username": "your-email@yourdomain.com",
  "smtp_password": "your-password",
  "smtp_tls": false,
  "smtp_ssl": true
}
```

### Outlook (STARTTLS)
```json
{
  "smtp_host": "smtp-mail.outlook.com",
  "smtp_port": 587,
  "smtp_username": "your-email@outlook.com",
  "smtp_password": "your-password",
  "smtp_tls": true,
  "smtp_ssl": false
}
```

## Best Practices

### 1. SMTP Verification
Always verify SMTP credentials before creating campaigns to avoid failures.

### 2. Rate Limiting
- Start with conservative limits (1 email/hour) for testing
- Increase limits based on your SMTP provider's restrictions
- Monitor for bounce rates and adjust accordingly

### 3. Error Handling
- Implement proper error handling for all API calls
- Show user-friendly error messages
- Log errors for debugging

### 4. Progress Tracking
- Poll status every 2-5 seconds for active campaigns
- Stop polling when campaign completes or fails
- Show progress bars and estimated completion times

### 5. Campaign Management
- Allow users to view campaign history
- Implement campaign duplication for similar sends
- Provide campaign analytics and reporting
- Use pause/resume functionality for long-running campaigns
- Monitor campaign status and handle paused campaigns appropriately

## Troubleshooting

### Common Issues

1. **SMTP Verification Fails**
   - Check credentials and server settings
   - Verify port numbers (587 for STARTTLS, 465 for SSL)
   - Ensure app passwords are used for Gmail

2. **Campaign Stuck in "Running"**
   - Check worker logs: `heroku logs -t -p worker -a aiemailnewsletter`
   - Verify Redis connection
   - Check for SMTP errors in logs

3. **Emails Not Delivered**
   - Check spam folders
   - Verify sender reputation
   - Review SMTP provider limits

4. **Rate Limiting Issues**
   - Adjust `limits_count` and `limits_window_seconds`
   - Check SMTP provider's sending limits
   - Monitor bounce rates

5. **Database Migration Issues**
   - If deployment fails due to migration errors, check that all models are properly defined
   - The system automatically creates a default admin user (`a@aiemailnewsletter.com`) for existing campaigns
   - All campaigns are automatically associated with this default user

6. **Campaign Control Issues**
   - If a campaign appears "stuck", check if it's paused using the status endpoint
   - Use the pause endpoint to stop a running campaign immediately
   - Use the resume endpoint to continue a paused campaign
   - Long delays between emails are normal based on `limits_window_seconds` setting

### Logs Access
```bash
# Web application logs
heroku logs -t -a aiemailnewsletter

# Worker logs
heroku logs -t -p worker -a aiemailnewsletter

# Database access
heroku run -a aiemailnewsletter -- python -c "from app.db import SessionLocal; print('DB connected')"
```

## API Limits
- No rate limiting on API endpoints
- SMTP rate limiting controlled by campaign settings
- Redis and PostgreSQL limits depend on Heroku plan

## User Management

### Current Implementation
The system currently uses a simplified user management approach:

1. **Default Admin User**: All campaigns are automatically associated with a default admin user (`a@aiemailnewsletter.com`)
2. **Automatic User Creation**: If the default user doesn't exist, it's created automatically when the first campaign is created
3. **No Authentication Required**: Currently, no authentication is required for API access

### Future Authentication (Planned)
The system is prepared for future API key authentication:

- **User Management**: Admin users can be created and managed
- **API Keys**: Each user can have multiple API keys for different applications
- **Key Expiration**: API keys can have expiration dates
- **Usage Tracking**: Last used timestamps for API keys

### Database Structure
```sql
-- Users table
users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(320) UNIQUE NOT NULL,
  name VARCHAR(255),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)

-- API Keys table (for future use)
api_keys (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  key_name VARCHAR(255) NOT NULL,
  key_hash VARCHAR(255) UNIQUE NOT NULL,
  is_active BOOLEAN DEFAULT true,
  last_used_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE,
  UNIQUE(user_id, key_name)
)

-- Campaigns table (updated)
campaigns (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  name VARCHAR(255) NOT NULL,
  -- ... other fields
)
```

## Support
For technical issues, check logs and verify SMTP settings. The system is designed to be self-healing for temporary network issues.
