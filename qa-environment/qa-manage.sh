#!/bin/bash

# QA Environment Management Script

case "$1" in
    "start")
        echo "🚀 Starting QA environment..."
        docker-compose -f docker-compose.qa.yml up -d
        echo "✅ QA environment started!"
        echo "🌐 QA URL: https://qa.joborra.com"
        ;;
    "stop")
        echo "🛑 Stopping QA environment..."
        docker-compose -f docker-compose.qa.yml down
        echo "✅ QA environment stopped!"
        ;;
    "restart")
        echo "🔄 Restarting QA environment..."
        docker-compose -f docker-compose.qa.yml restart
        echo "✅ QA environment restarted!"
        ;;
    "logs")
        echo "📋 Showing QA logs..."
        docker-compose -f docker-compose.qa.yml logs -f
        ;;
    "status")
        echo "📊 QA environment status..."
        docker-compose -f docker-compose.qa.yml ps
        ;;
    "build")
        echo "🔨 Building QA environment..."
        docker-compose -f docker-compose.qa.yml build --no-cache
        echo "✅ QA environment built!"
        ;;
    "deploy")
        echo "🚀 Deploying QA environment..."
        docker-compose -f docker-compose.qa.yml down
        docker-compose -f docker-compose.qa.yml build --no-cache
        docker-compose -f docker-compose.qa.yml up -d
        echo "✅ QA deployment completed!"
        echo "🌐 QA URL: https://qa.joborra.com"
        ;;
    "clean")
        echo "🧹 Cleaning QA environment..."
        docker-compose -f docker-compose.qa.yml down -v
        docker system prune -f
        echo "✅ QA environment cleaned!"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|status|build|deploy|clean}"
        echo ""
        echo "Commands:"
        echo "  start   - Start QA environment"
        echo "  stop    - Stop QA environment"
        echo "  restart - Restart QA environment"
        echo "  logs    - Show QA logs"
        echo "  status  - Show QA status"
        echo "  build   - Build QA containers"
        echo "  deploy  - Full QA deployment"
        echo "  clean   - Clean QA environment"
        exit 1
        ;;
esac
