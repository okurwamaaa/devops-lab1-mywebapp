#!/bin/bash
echo "Starting deployment..."
docker pull ghcr.io/ТВІЙ_НІК/devops-lab1-mywebapp:latest
sudo cp mywebapp-container.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart mywebapp-container.service
echo "Deployment successful!"