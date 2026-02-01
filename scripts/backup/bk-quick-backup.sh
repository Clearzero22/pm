#!/usr/bin/env bash
#
# 名称：bk-quick-backup
# 用途：快速备份文件或目录
# 依赖：rsync, tar, gzip
# 作者：clearzero22
# 日期：2025-02-01
# 版本：1.0.0
#
# 使用示例：
#   ./bk-quick-backup.sh /path/to/source              # 备份到默认目录
#   ./bk-quick-backup.sh /path/to/source -d /backup   # 备份到指定目录
#   ./bk-quick-backup.sh --help                        # 显示帮助
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 默认配置
DEFAULT_BACKUP_DIR="$HOME/backups"
BACKUP_DIR="$DEFAULT_BACKUP_DIR"
SOURCE=""
BACKUP_NAME=""
COMPRESS=true
VERBOSE=false

# 打印带颜色的信息
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << HELP
用法: bk-quick-backup [选项] <源路径>

选项:
  -h, --help              显示此帮助信息
  -d, --dir <目录>        备份目录 (默认: ~/backups)
  -n, --name <名称>       备份名称 (默认: 自动生成)
  --no-compress           不压缩备份文件
  -v, --verbose           显示详细输出

示例:
  bk-quick-backup.sh /path/to/project                    # 备份到 ~/backups
  bk-quick-backup.sh /path/to/project -d /my/backup      # 备份到 /my/backup
  bk-quick-backup.sh /path/to/project -n project-v1      # 指定备份名称
  bk-quick-backup.sh /path/to/project --no-compress       # 不压缩
HELP
}

# 生成默认备份名称
generate_backup_name() {
    local source_name=$(basename "$SOURCE" | tr ' ' '_')
    local timestamp=$(date +%Y%m%d_%H%M%S)
    echo "${source_name}_${timestamp}"
}

# 验证源路径
validate_source() {
    if [ -z "$SOURCE" ]; then
        error "请指定源路径"
        return 1
    fi
    
    if [ ! -e "$SOURCE" ]; then
        error "源路径不存在: $SOURCE"
        return 1
    fi
    
    return 0
}

# 创建备份目录
ensure_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        info "创建备份目录: $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
    fi
}

# 备份操作
perform_backup() {
    # 验证源路径
    if ! validate_source; then
        return 1
    fi
    
    # 生成备份名称
    if [ -z "$BACKUP_NAME" ]; then
        BACKUP_NAME=$(generate_backup_name)
    fi
    
    # 确保备份目录存在
    ensure_backup_dir
    
    # 构建备份文件路径
    local backup_file
    if [ "$COMPRESS" = true ]; then
        backup_file="$BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    else
        backup_file="$BACKUP_DIR/${BACKUP_NAME}.tar"
    fi
    
    # 检查是否已存在
    if [ -e "$backup_file" ]; then
        warning "备份文件已存在: $backup_file"
        read -p "是否覆盖? [y/N] " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "操作已取消"
            return 0
        fi
    fi
    
    # 获取源路径大小
    local source_size=$(du -sh "$SOURCE" | cut -f1)
    
    echo ""
    info "开始备份..."
    info "源路径: $SOURCE ($source_size)"
    info "目标文件: $backup_file"
    echo ""
    
    # 构建tar命令
    local tar_cmd="tar"
    if [ "$COMPRESS" = true ]; then
        tar_cmd="tar -czvf"
    else
        tar_cmd="tar -cvf"
    fi
    
    if [ "$VERBOSE" = false ]; then
        tar_cmd="$tar_cmd -"
    fi
    
    # 执行备份
    local start_time=$(date +%s)
    
    if [ "$VERBOSE" = true ]; then
        tar -cf - "$SOURCE" 2>/dev/null | \
            { [ "$COMPRESS" = true ] && gzip || cat; } \
            > "$backup_file"
    else
        info "正在打包..."
        tar -cf - "$SOURCE" 2>/dev/null | \
            { [ "$COMPRESS" = true ] && gzip || cat; } \
            > "$backup_file"
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # 获取备份文件大小
    local backup_size=$(du -sh "$backup_file" | cut -f1)
    
    echo ""
    success "备份完成！"
    echo ""
    echo "统计:"
    echo "  - 源大小: $source_size"
    echo "  - 备份大小: $backup_size"
    echo "  - 耗时: ${duration}秒"
    echo "  - 文件: $backup_file"
    echo ""
    
    # 计算压缩率
    if [ "$COMPRESS" = true ]; then
        info "提示: 使用 'bk-quick-restore.sh $backup_file' 恢复"
    fi
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -n|--name)
            BACKUP_NAME="$2"
            shift 2
            ;;
        --no-compress)
            COMPRESS=false
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -*)
            error "未知选项: $1"
            show_help
            exit 1
            ;;
        *)
            SOURCE="$1"
            shift
            ;;
    esac
done

# 主逻辑
if [ -z "$SOURCE" ]; then
    show_help
    exit 1
fi

perform_backup
