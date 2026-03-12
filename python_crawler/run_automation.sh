#!/bin/bash
# Amazon Crawler Automation Script
# Run crawler and generate report automatically

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Default values
MODE="bestsellers"
KEYWORD=""
PAGES=2
PRODUCTS=20
HEADLESS=true
OUTPUT="output/amazon_products_$(date +%Y%m%d_%H%M%S).csv"
REPORT=true
REMOTE_HOST=""

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to display usage
usage() {
    cat << EOF
Amazon Crawler Automation Script

Usage: $0 [OPTIONS]

Options:
    -m, --mode MODE          Crawler mode: "bestsellers" or "search" (default: bestsellers)
    -k, --keyword KEYWORD    Search keyword (required for search mode)
    -p, --pages NUM          Number of pages to crawl (default: 2)
    -n, --products NUM       Products per page (default: 20)
    -o, --output FILE        Output CSV filename
    --no-headless            Show browser window (default: headless)
    --no-report              Skip report generation
    -r, --remote HOST        Run on remote server (user@host format)
    -h, --help               Show this help message

Examples:
    # Local Best Sellers crawl
    $0 --pages 2 --products 20

    # Local search crawl
    $0 --mode search --keyword "water bottle" --pages 2 --products 20

    # Remote crawl
    $0 --mode search --keyword "blender" --remote user@server.example.com

    # Custom output location
    $0 --pages 3 --output output/my_results.csv

EOF
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -k|--keyword)
            KEYWORD="$2"
            shift 2
            ;;
        -p|--pages)
            PAGES="$2"
            shift 2
            ;;
        -n|--products)
            PRODUCTS="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        --no-headless)
            HEADLESS=false
            shift
            ;;
        --no-report)
            REPORT=false
            shift
            ;;
        -r|--remote)
            REMOTE_HOST="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate mode
if [[ "$MODE" != "bestsellers" && "$MODE" != "search" ]]; then
    print_error "Invalid mode: $MODE (must be 'bestsellers' or 'search')"
    exit 1
fi

# Validate keyword for search mode
if [[ "$MODE" == "search" && -z "$KEYWORD" ]]; then
    print_error "Keyword is required for search mode"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$(dirname "$OUTPUT")"

# Build command
if [[ "$MODE" == "search" ]]; then
    CMD="uv run python main.py --search '$KEYWORD' --pages $PAGES --products $PRODUCTS --output '$OUTPUT'"
else
    CMD="uv run python main.py --pages $PAGES --products $PRODUCTS --output '$OUTPUT'"
fi

if [[ "$HEADLESS" == true ]]; then
    CMD="$CMD --headless"
fi

# Display configuration
echo ""
echo "============================================================"
echo "           Amazon Crawler Automation"
echo "============================================================"
echo "  Mode:           $MODE"
if [[ "$MODE" == "search" ]]; then
    echo "  Keyword:        $KEYWORD"
fi
echo "  Pages:          $PAGES"
echo "  Products/page:  $PRODUCTS"
echo "  Headless:       $HEADLESS"
echo "  Output:         $OUTPUT"
echo "  Report:         $REPORT"
if [[ -n "$REMOTE_HOST" ]]; then
    echo "  Remote Host:    $REMOTE_HOST"
fi
echo "============================================================"
echo ""

# Run crawler
if [[ -n "$REMOTE_HOST" ]]; then
    print_info "Running on remote server: $REMOTE_HOST"

    # Remote execution
    ssh "$REMOTE_HOST" "cd '$PROJECT_DIR' && $CMD"

    # Transfer CSV back
    print_info "Transferring results from remote server..."
    scp "$REMOTE_HOST:$PROJECT_DIR/$OUTPUT" "$OUTPUT" 2>/dev/null || true

    # Try to get the generated CSV (filename might differ on remote)
    if [[ ! -f "$OUTPUT" ]]; then
        print_warning "Could not transfer using output path, trying to find latest CSV..."
        ssh "$REMOTE_HOST" "cd '$PROJECT_DIR' && ls -t output/*.csv | head -1" | xargs -I {} scp "$REMOTE_HOST":{} "$OUTPUT"
    fi

else
    print_info "Running crawler locally..."

    # Local execution
    eval $CMD
fi

# Check if CSV was created
if [[ ! -f "$OUTPUT" ]]; then
    print_error "CSV file not created: $OUTPUT"
    exit 1
fi

# Count products in CSV
PRODUCT_COUNT=$(tail -n +2 "$OUTPUT" | wc -l)
print_success "Crawler completed! Extracted $PRODUCT_COUNT products"

# Generate report
if [[ "$REPORT" == true ]]; then
    print_info "Generating data report..."

    uv run python crawler_report.py "$OUTPUT"

    print_success "Report generated!"
fi

# Display summary
echo ""
echo "============================================================"
echo "           Automation Complete"
echo "============================================================"
echo "  CSV Data:       $OUTPUT"
if [[ "$REPORT" == true ]]; then
    REPORT_FILE="${OUTPUT%.csv}_report.md"
    echo "  Report:         $REPORT_FILE"
    JSON_FILE="${OUTPUT%.csv}_report.json"
    echo "  Statistics:     $JSON_FILE"
fi
echo "============================================================"
echo ""
