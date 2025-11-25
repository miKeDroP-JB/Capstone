#!/bin/bash
# 0RB_AETHER - One-Command Deploy
# Usage: ./deploy.sh [local|docker|cloud]

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}"
cat << 'EOF'
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║    ██████╗ ██████╗ ██████╗      █████╗ ███████╗████████╗██╗  ██╗███████╗██████╗  ║
║   ██╔═══██╗██╔══██╗██╔══██╗    ██╔══██╗██╔════╝╚══██╔══╝██║  ██║██╔════╝██╔══██╗ ║
║   ██║   ██║██████╔╝██████╔╝    ███████║█████╗     ██║   ███████║█████╗  ██████╔╝ ║
║   ██║   ██║██╔══██╗██╔══██╗    ██╔══██║██╔══╝     ██║   ██╔══██║██╔══╝  ██╔══██╗ ║
║   ╚██████╔╝██║  ██║██████╔╝    ██║  ██║███████╗   ██║   ██║  ██║███████╗██║  ██║ ║
║    ╚═════╝ ╚═╝  ╚═╝╚═════╝     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ║
║                                                               ║
║              Love - Loyalty - Honor - Everybody Eats          ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

MODE=${1:-docker}

# =============================================================================
# Functions
# =============================================================================

check_deps() {
    echo -e "${YELLOW}Checking dependencies...${NC}"

    if [ "$MODE" = "docker" ]; then
        if ! command -v docker &> /dev/null; then
            echo -e "${RED}Docker not found. Install: https://docs.docker.com/get-docker/${NC}"
            exit 1
        fi
        if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
            echo -e "${RED}Docker Compose not found.${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ Docker ready${NC}"
    else
        if ! command -v python3 &> /dev/null; then
            echo -e "${RED}Python 3 not found.${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ Python $(python3 --version | cut -d' ' -f2) ready${NC}"
    fi
}

setup_env() {
    echo -e "${YELLOW}Setting up environment...${NC}"

    if [ ! -f .env ]; then
        cat > .env << 'ENVFILE'
# 0RB_AETHER Environment Configuration
# Copy this to .env and fill in your keys

# AI Provider Keys (at least one required)
CLAUDE_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=

# System Settings
ORB_ENV=production
LOG_LEVEL=INFO

# Security (generate with: openssl rand -hex 32)
SECRET_KEY=change-me-in-production

# Optional: External Services
REDIS_URL=redis://localhost:6379
ENVFILE
        echo -e "${GREEN}✓ Created .env file - add your API keys${NC}"
    else
        echo -e "${GREEN}✓ .env exists${NC}"
    fi
}

deploy_local() {
    echo -e "${YELLOW}Deploying locally...${NC}"

    # Create venv if needed
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}✓ Created virtual environment${NC}"
    fi

    # Activate and install
    source venv/bin/activate
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"

    # Run
    echo -e "${CYAN}Starting 0RB_AETHER...${NC}"
    python launcher.py
}

deploy_docker() {
    echo -e "${YELLOW}Deploying with Docker...${NC}"

    # Build
    echo "Building containers..."
    docker compose build

    # Start
    echo "Starting services..."
    docker compose up -d

    echo -e "${GREEN}✓ Services started${NC}"
    echo ""
    echo -e "Services running:"
    echo -e "  ${CYAN}Brain:${NC}     http://localhost:8080"
    echo -e "  ${CYAN}API:${NC}       http://localhost:8081"
    echo -e "  ${CYAN}Edge:${NC}      http://localhost:9000"
    echo ""
    echo -e "Commands:"
    echo -e "  ${YELLOW}docker compose logs -f${NC}     # View logs"
    echo -e "  ${YELLOW}docker compose down${NC}        # Stop all"
    echo -e "  ${YELLOW}docker compose ps${NC}          # Status"
}

deploy_cloud() {
    echo -e "${YELLOW}Cloud deployment options:${NC}"
    echo ""
    echo "1. AWS (recommended for production):"
    echo "   - Use ECS with Fargate"
    echo "   - Or EKS for Kubernetes"
    echo ""
    echo "2. Google Cloud:"
    echo "   - Cloud Run (serverless)"
    echo "   - GKE for Kubernetes"
    echo ""
    echo "3. Azure:"
    echo "   - Container Instances"
    echo "   - AKS for Kubernetes"
    echo ""
    echo "Quick deploy to any cloud with Docker image:"
    echo -e "  ${CYAN}docker build -t orb-aether .${NC}"
    echo -e "  ${CYAN}docker tag orb-aether your-registry/orb-aether${NC}"
    echo -e "  ${CYAN}docker push your-registry/orb-aether${NC}"
}

show_help() {
    echo "Usage: ./deploy.sh [MODE]"
    echo ""
    echo "Modes:"
    echo "  local     Run directly with Python (development)"
    echo "  docker    Run with Docker Compose (recommended)"
    echo "  cloud     Show cloud deployment options"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh              # Docker (default)"
    echo "  ./deploy.sh local        # Local Python"
    echo "  ./deploy.sh docker       # Docker Compose"
}

# =============================================================================
# Main
# =============================================================================

case $MODE in
    local)
        check_deps
        setup_env
        deploy_local
        ;;
    docker)
        check_deps
        setup_env
        deploy_docker
        ;;
    cloud)
        deploy_cloud
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown mode: $MODE${NC}"
        show_help
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Love - Loyalty - Honor - Everybody Eats${NC}"
