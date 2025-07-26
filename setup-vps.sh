#!/bin/bash

# ReachInbox VPS Setup Script
# Supports Ubuntu 20.04/22.04 and CentOS 8/9

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "   ReachInbox Email Management Platform Setup    "
    echo "=================================================="
    echo -e "${NC}"
}

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Detect OS
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        print_error "Cannot detect OS"
        exit 1
    fi
    
    print_status "Detected OS: $OS $VER"
}

# Update system
update_system() {
    print_status "Updating system packages..."
    
    if [[ $OS == *"Ubuntu"* ]] || [[ $OS == *"Debian"* ]]; then
        apt update && apt upgrade -y
        apt install -y curl wget git unzip software-properties-common
    elif [[ $OS == *"CentOS"* ]] || [[ $OS == *"Red Hat"* ]]; then
        yum update -y
        yum install -y curl wget git unzip
    else
        print_error "Unsupported OS: $OS"
        exit 1
    fi
}

# Install Node.js
install_nodejs() {
    print_status "Installing Node.js 18..."
    
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs
    
    # Verify installation
    node --version
    npm --version
    
    print_status "Node.js installed successfully"
}

# Install Python
install_python() {
    print_status "Installing Python 3.11..."
    
    if [[ $OS == *"Ubuntu"* ]]; then
        add-apt-repository ppa:deadsnakes/ppa -y
        apt update
        apt install -y python3.11 python3.11-pip python3.11-venv
        
        # Create symlinks
        update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
        update-alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.11 1
    else
        apt install -y python3 python3-pip python3-venv
    fi
    
    python3 --version
    pip3 --version
    
    print_status "Python installed successfully"
}

# Install Docker
install_docker() {
    print_status "Installing Docker..."
    
    # Remove old versions
    apt-get remove -y docker docker-engine docker.io containerd runc || true
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    
    # Install Docker Compose
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # Add current user to docker group
    usermod -aG docker $USER || true
    
    # Start Docker
    systemctl enable docker
    systemctl start docker
    
    docker --version
    docker-compose --version
    
    print_status "Docker installed successfully"
}

# Install PM2
install_pm2() {
    print_status "Installing PM2 process manager..."
    
    npm install -g pm2
    pm2 startup
    
    print_status "PM2 installed successfully"
}

# Install Nginx
install_nginx() {
    print_status "Installing Nginx..."
    
    apt install -y nginx
    
    # Configure firewall
    ufw allow 'Nginx Full' || true
    ufw allow ssh || true
    
    systemctl enable nginx
    systemctl start nginx
    
    print_status "Nginx installed successfully"
}

# Setup firewall
setup_firewall() {
    print_status "Configuring firewall..."
    
    # Install ufw if not present
    apt install -y ufw
    
    # Reset firewall
    ufw --force reset
    
    # Allow essential ports
    ufw allow ssh
    ufw allow 80/tcp      # HTTP
    ufw allow 443/tcp     # HTTPS
    ufw allow 4000/tcp    # Application
    ufw allow 9200/tcp    # Elasticsearch
    ufw allow 5601/tcp    # Kibana
    
    # Enable firewall
    ufw --force enable
    
    print_status "Firewall configured"
}

# Create application user
create_app_user() {
    print_status "Creating application user..."
    
    if ! id "reachinbox" &>/dev/null; then
        useradd -m -s /bin/bash reachinbox
        usermod -aG docker reachinbox
        
        # Create SSH directory
        mkdir -p /home/reachinbox/.ssh
        chown -R reachinbox:reachinbox /home/reachinbox/.ssh
        chmod 700 /home/reachinbox/.ssh
        
        print_status "User 'reachinbox' created"
    else
        print_status "User 'reachinbox' already exists"
    fi
}

# Setup application directory
setup_app_directory() {
    print_status "Setting up application directory..."
    
    mkdir -p /opt/reachinbox
    chown -R reachinbox:reachinbox /opt/reachinbox
    
    # Create necessary directories
    mkdir -p /opt/reachinbox/{logs,ssl,reply_vector_db}
    chown -R reachinbox:reachinbox /opt/reachinbox
    
    print_status "Application directory ready"
}

# Install SSL certificate (Let's Encrypt)
setup_ssl() {
    print_status "Setting up SSL certificate..."
    
    # Install certbot
    apt install -y certbot python3-certbot-nginx
    
    print_warning "To enable SSL later, run:"
    print_warning "certbot --nginx -d yourdomain.com"
}

# Main installation
main() {
    print_header
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
    
    detect_os
    update_system
    install_nodejs
    install_python
    install_docker
    install_pm2
    install_nginx
    setup_firewall
    create_app_user
    setup_app_directory
    setup_ssl
    
    print_header
    print_status "ReachInbox server setup completed!"
    echo ""
    print_status "Next steps:"
    echo "1. Switch to application user: su - reachinbox"
    echo "2. Clone your repository: git clone <your-repo-url> /opt/reachinbox/app"
    echo "3. Configure environment: cd /opt/reachinbox/app && cp .env.example .env"
    echo "4. Edit configuration: nano .env"
    echo "5. Deploy application: ./deploy.sh"
    echo ""
    print_status "Your server is ready for ReachInbox deployment!"
    
    # Restart to ensure all changes take effect
    print_warning "A reboot is recommended to ensure all changes take effect"
    print_warning "Run 'reboot' after completing the setup"
}

# Run main function
main "$@"
