#!/bin/bash

# Fly Catcher Bot Deployment Script for Hetzner Server
# Run this on your server: bash deploy_flycatcher.sh

set -e  # Exit on error

echo "🦎 Deploying MemeLeon Fly Catcher Bot..."

# Navigate to bots directory
cd /home/botmanager/bot-platform/bots/

# Clone the repository (separate from chartbot)
if [ -d "flycatcherbot" ]; then
    echo "⚠️  flycatcherbot directory exists. Updating..."
    cd flycatcherbot
    git fetch origin
    git checkout claude/hello-world-011CUs3M5fiW3hqzhAUWD9H1
    git pull
else
    echo "📥 Cloning repository..."
    git clone https://github.com/Loriii0/Memeleon-Fly-Catcher.git flycatcherbot
    cd flycatcherbot
    git checkout claude/hello-world-011CUs3M5fiW3hqzhAUWD9H1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found!"
    echo "Please enter your bot token from @BotFather:"
    read -s BOT_TOKEN
    echo "BOT_TOKEN=$BOT_TOKEN" > .env
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Set ownership to botmanager
echo "🔐 Setting permissions..."
chown -R botmanager:botmanager /home/botmanager/bot-platform/bots/flycatcherbot

# Create systemd service
echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/flycatcher-bot.service <<'EOF'
[Unit]
Description=MemeLeon Fly Catcher Bot
After=network.target

[Service]
Type=simple
User=botmanager
WorkingDirectory=/home/botmanager/bot-platform/bots/flycatcherbot
ExecStart=/usr/bin/python3 /home/botmanager/bot-platform/bots/flycatcherbot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Enable and start the service
echo "🚀 Starting Fly Catcher Bot..."
systemctl enable flycatcher-bot
systemctl restart flycatcher-bot

# Show status
echo ""
echo "✅ Deployment Complete!"
echo ""
echo "📊 Bot Status:"
systemctl status flycatcher-bot --no-pager

echo ""
echo "📝 Useful Commands:"
echo "  View logs:    journalctl -u flycatcher-bot -f"
echo "  Restart bot:  systemctl restart flycatcher-bot"
echo "  Stop bot:     systemctl stop flycatcher-bot"
echo "  Bot status:   systemctl status flycatcher-bot"
echo ""
echo "🎮 Test your bot at: @MemeLeonFlyBot"
