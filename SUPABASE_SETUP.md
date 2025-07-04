# Supabase Setup Guide

This guide will help you connect your Stock Portfolio Dashboard to Supabase for free cloud database storage.

## What is Supabase?

Supabase is a free PostgreSQL database service that offers:
- 500MB database storage (free tier)
- Automatic backups
- Cloud hosting
- No expiration (unlike Replit's 30-day trial)

## Setup Instructions

### 1. Create a Supabase Account

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project" and sign up
3. Create a new project

### 2. Get Your Database URL

1. In your Supabase project dashboard, click "Settings" in the left sidebar
2. Click "Database" under Settings
3. Scroll down to "Connection String"
4. Copy the URI connection string (starts with `postgresql://`)
5. Replace `[YOUR-PASSWORD]` with your actual database password

### 3. Configure Your Portfolio App

In your Replit project:

1. Go to the "Secrets" tab (lock icon in left sidebar)
2. Add a new secret:
   - Key: `SUPABASE_URL`
   - Value: Your complete connection string from step 2

### 4. Restart Your App

1. Stop your current app (if running)
2. Start it again - it will automatically connect to Supabase
3. You'll see "✅ Connected to Supabase database!" when successful

## Benefits

Once connected to Supabase:
- Your portfolio data is stored in the cloud
- Data persists even if Replit restarts
- Automatic backups and better reliability
- 500MB storage (enough for thousands of stock entries)
- Works forever on free tier

## Troubleshooting

**"Could not connect to Supabase" message:**
- Check that your `SUPABASE_URL` secret is correctly formatted
- Verify your database password in the connection string
- Make sure there are no extra spaces in the URL

**App still using JSON files:**
- The app will automatically fall back to JSON file storage if Supabase isn't configured
- This ensures your app always works, even without Supabase

## Migration

If you already have portfolios in JSON files:
- They will be automatically migrated to Supabase when you first connect
- Your original JSON file will be backed up as `portfolios.json.backup`

## Free Tier Limits

Supabase free tier includes:
- 500MB database storage
- Up to 2 projects
- 50,000 monthly active users
- Unlimited API requests

For a personal stock portfolio, you'll likely never hit these limits!