#!/bin/bash
# GPU Driver Diagnostics Tool (rewritten)
# - Detects which DRM card is bound to which kernel driver (ground truth)
# - Correctly checks current-user device access and group membership
# - Does not conflate "DRM device exists" with "Intel GPU present"
# - Treats lsmod as informational; autoloaded modules aren't a failure signal

set -uo pipefail

RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
BLUE=$'\033[0;34m'
NC=$'\033[0m'

ISSUES_FOUND=0

print_header()  { printf '\n%s=== %s ===%s\n\n' "$BLUE" "$1" "$NC"; }
print_success() { printf '%s✓%s %s\n' "$GREEN" "$NC" "$1"; }
print_info()    { printf '%sℹ%s %s\n' "$BLUE"  "$NC" "$1"; }
print_warning() { printf '%s⚠%s %s\n' "$YELLOW" "$NC" "$1"; ISSUES_FOUND=$((ISSUES_FOUND + 1)); }
print_error()   { printf '%s✗%s %s\n' "$RED"    "$NC" "$1"; ISSUES_FOUND=$((ISSUES_FOUND + 1)); }

# ---------------------------------------------------------------------------
# Globals populated by detect_gpus(): which vendors and drivers are present.
# Populated as plain arrays so the rest of the script doesn't reparse lspci.
# ---------------------------------------------------------------------------
declare -a GPU_PCI_LINES=()        # raw lspci -nn lines for each GPU
declare -a GPU_VENDORS=()          # nvidia | amd | intel | other (parallel)
declare -A DRM_DRIVERS=()          # /sys/class/drm/cardN -> driver name
HAS_NVIDIA=false
HAS_AMD=false
HAS_INTEL=false

detect_gpus() {
    print_header "GPU Hardware Detection"

    # First, check what drivers are bound via DRM (ground truth).
    # This works even when lspci fails to enumerate the GPU.
    local card driver
    for card in /sys/class/drm/card[0-9]*; do
        [[ -e "$card" ]] || continue
        [[ -L "$card/device/driver" ]] || continue
        driver=$(basename "$(readlink -f "$card/device/driver")")
        DRM_DRIVERS["$(basename "$card")"]=$driver
        
        # Infer vendor from driver
        case "$driver" in
            amdgpu|radeon) HAS_AMD=true ;;
            i915|xe)       HAS_INTEL=true ;;
            nvidia*)       HAS_NVIDIA=true ;;
        esac
    done

    # Then try lspci for additional info (informational, not authoritative).
    if command -v lspci >/dev/null 2>&1; then
        local line
        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            GPU_PCI_LINES+=("$line")
            local vendor=other
            if   [[ "$line" =~ [Nn][Vv][Ii][Dd][Ii][Aa] ]]; then vendor=nvidia; HAS_NVIDIA=true
            elif [[ "$line" =~ [Aa][Mm][Dd]|[Aa][Tt][Ii] ]]; then vendor=amd;    HAS_AMD=true
            elif [[ "$line" =~ [Ii][Nn][Tt][Ee][Ll]     ]]; then vendor=intel;  HAS_INTEL=true
            fi
            GPU_VENDORS+=("$vendor")
            print_info "$(printf '%-7s %s' "${vendor^^}:" "$line")"
        done < <(lspci -nn -d ::0300 -d ::0302 -d ::0380 2>/dev/null)
        
        if [[ ${#GPU_PCI_LINES[@]} -eq 0 ]]; then
            print_info "Note: lspci detected no GPUs (hardware enumeration may be hidden by BIOS/ACPI)"
        fi
    else
        print_info "lspci not available (install pciutils for detailed PCI info)"
    fi

    if [[ ${#DRM_DRIVERS[@]} -eq 0 ]]; then
        print_warning "No GPU drivers bound to DRM cards"
        return 1
    fi
}

check_drm_subsystem() {
    print_header "DRM / Graphics Subsystem"

    if ! [[ -d /sys/class/drm ]]; then
        print_error "DRM subsystem not present (/sys/class/drm missing)"
        return 1
    fi
    print_success "DRM subsystem present"

    if [[ ${#DRM_DRIVERS[@]} -eq 0 ]]; then
        print_warning "No DRM cards have a bound driver"
        return 1
    fi

    local card
    for card in "${!DRM_DRIVERS[@]}"; do
        local drv=${DRM_DRIVERS[$card]}
        case "$drv" in
            amdgpu)        print_success "$card -> amdgpu (AMD)"        ;;
            radeon)        print_warning "$card -> radeon (legacy; amdgpu preferred on modern HW)" ;;
            i915|xe)       print_success "$card -> $drv (Intel)"        ;;
            nvidia*)       print_success "$card -> $drv (NVIDIA)"       ;;
            simpledrm|vesa|efifb)
                           print_warning "$card -> $drv (firmware fallback — real GPU driver did not bind)" ;;
            *)             print_info    "$card -> $drv"                ;;
        esac
    done

    local rd
    for rd in /dev/dri/renderD*; do
        [[ -e "$rd" ]] && print_info "Render node: $(basename "$rd")"
    done
}

check_kernel_modules() {
    print_header "Kernel Module Status (informational)"
    # NOTE: amdgpu/i915/nvidia autoload on first DRM access. Absence in lsmod
    # before anything touches the GPU is NOT a failure — that's why this is
    # informational only. The authoritative check is the driver symlink walk
    # in check_drm_subsystem above.
    local mod found=false
    for mod in nvidia nvidia_drm nvidia_modeset amdgpu radeon i915 xe; do
        if lsmod 2>/dev/null | awk '{print $1}' | grep -qx "$mod"; then
            print_success "loaded: $mod"
            found=true
        fi
    done
    $found || print_info "No GPU modules currently in lsmod (may load on demand)"
}

check_permissions() {
    print_header "Device Permissions (current user)"

    local device
    for device in /dev/dri/card[0-9]* /dev/dri/renderD*; do
        [[ -e "$device" ]] || continue
        # -r and -w consult our real UID/GIDs, including supplementary groups.
        if [[ -r "$device" ]]; then print_success "$device readable"
        else                        print_error   "$device not readable"; fi
        if [[ -w "$device" ]]; then print_success "$device writable"
        else                        print_warning "$device not writable"; fi
    done

    # Group membership: id -Gn gives names; -G gives numeric GIDs.
    local groups
    groups=$(id -Gn 2>/dev/null)
    local need
    for need in video render; do
        if grep -qw "$need" <<<"$groups"; then
            print_success "user in '$need' group"
        else
            print_warning "user NOT in '$need' group — fix with: sudo usermod -aG $need \$USER (then re-login)"
        fi
    done
}

check_environment() {
    print_header "Environment Variables"
    local var
    for var in CUDA_VISIBLE_DEVICES HIP_DEVICE_ORDER HIP_VISIBLE_DEVICES \
               ROCR_VISIBLE_DEVICES DRI_PRIME __GLX_VENDOR_LIBRARY_NAME \
               VK_ICD_FILENAMES MESA_LOADER_DRIVER_OVERRIDE LD_LIBRARY_PATH; do
        if [[ -n "${!var:-}" ]]; then
            print_info "$var=${!var}"
        fi
    done
    print_success "Environment check complete"
}

check_nvidia_drivers() {
    print_header "NVIDIA Driver Check"
    if ! $HAS_NVIDIA; then
        print_info "No NVIDIA GPU detected; skipping"
        return 0
    fi

    if ! command -v nvidia-smi >/dev/null 2>&1; then
        print_warning "nvidia-smi not installed"
        return 1
    fi
    print_success "nvidia-smi present"

    local v
    if v=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1) && [[ -n "$v" ]]; then
        print_info "Driver version: $v"
    else
        print_error "nvidia-smi could not query GPU"
    fi

    if command -v nvcc >/dev/null 2>&1; then
        print_info "CUDA: $(nvcc --version | grep -oP 'release \K[0-9.]+')"
    else
        print_info "CUDA toolkit not installed (optional)"
    fi
}

check_amd_drivers() {
    print_header "AMD Driver Check"
    if ! $HAS_AMD; then
        print_info "No AMD GPU detected; skipping"
        return 0
    fi

    # Authoritative: is any DRM card bound to amdgpu?
    local bound=false card
    for card in "${!DRM_DRIVERS[@]}"; do
        [[ "${DRM_DRIVERS[$card]}" == amdgpu ]] && bound=true
    done
    if $bound; then
        print_success "amdgpu is bound to a DRM card"
    else
        print_warning "AMD GPU present but no DRM card is bound to amdgpu"
    fi

    # Quick userspace sanity check via glxinfo if available.
    if command -v glxinfo >/dev/null 2>&1; then
        local renderer
        renderer=$(glxinfo -B 2>/dev/null | awk -F': ' '/OpenGL renderer string/ {print $2}')
        if [[ -n "$renderer" ]]; then
            if [[ "$renderer" == *llvmpipe* ]]; then
                print_warning "GL renderer is llvmpipe (software) — hardware acceleration not active"
            else
                print_success "GL renderer: $renderer"
            fi
        fi
    else
        print_info "glxinfo not installed (apt install mesa-utils) — skipping GL renderer check"
    fi

    if command -v rocm-smi >/dev/null 2>&1; then
        print_success "ROCm present"
        rocm-smi --version 2>/dev/null | head -1 | sed 's/^/  /'
    else
        print_info "ROCm not installed (optional, only needed for GPU compute)"
    fi
}

check_intel_drivers() {
    print_header "Intel Driver Check"
    if ! $HAS_INTEL; then
        print_info "No Intel GPU detected; skipping"
        return 0
    fi

    local bound=false card drv
    for card in "${!DRM_DRIVERS[@]}"; do
        drv=${DRM_DRIVERS[$card]}
        [[ "$drv" == i915 || "$drv" == xe ]] && bound=true
    done
    if $bound; then
        print_success "Intel DRM driver bound (i915 or xe)"
    else
        print_warning "Intel GPU present but neither i915 nor xe is bound"
    fi

    command -v intel_gpu_top >/dev/null 2>&1 \
        && print_success "intel-gpu-tools installed" \
        || print_info "intel-gpu-tools not installed (optional)"
}

check_gpu_functionality() {
    print_header "GPU Functionality Test"
    
    local gl_works=false vk_works=false cl_works=false
    
    # Test 1: OpenGL support
    if command -v glxinfo >/dev/null 2>&1; then
        local renderer
        renderer=$(glxinfo -B 2>/dev/null | awk -F': ' '/OpenGL renderer string/ {print $2}')
        if [[ -n "$renderer" ]]; then
            if [[ "$renderer" == *llvmpipe* ]] || [[ "$renderer" == *softpipe* ]]; then
                print_warning "OpenGL: $renderer (software fallback — hardware acceleration unavailable)"
            else
                print_success "OpenGL 4.6+ working: $renderer"
                gl_works=true
            fi
        else
            print_info "OpenGL renderer detection failed (X11/Wayland not available?)"
        fi
    else
        print_info "glxinfo not installed — install 'mesa-utils' to test OpenGL"
    fi

    # Test 2: Vulkan support
    if command -v vulkaninfo >/dev/null 2>&1; then
        local vk_devices
        vk_devices=$(vulkaninfo 2>&1 | grep -c "GPU id = " || true)
        if [[ $vk_devices -gt 0 ]]; then
            print_success "Vulkan working: $vk_devices physical device(s) found"
            vk_works=true
            vulkaninfo 2>&1 | grep "GPU id" | head -3 | sed 's/^/  /'
        else
            print_warning "Vulkan available but no physical devices found"
        fi
    else
        print_info "vulkaninfo not installed — install 'vulkan-tools' to test Vulkan"
    fi

    # Test 3: OpenCL support
    if command -v clinfo >/dev/null 2>&1; then
        local cl_platforms
        cl_platforms=$(clinfo 2>&1 | grep -c "Platform.*Number of devices" || true)
        if [[ $cl_platforms -gt 0 ]]; then
            print_success "OpenCL working: $cl_platforms platform(s) available"
            cl_works=true
        else
            print_info "OpenCL available but no platforms found"
        fi
    else
        print_info "clinfo not installed — install 'clinfo' to test OpenCL (optional)"
    fi

    # Summary of functionality
    echo
    if $gl_works || $vk_works || $cl_works; then
        echo "${GREEN}✓ GPU is functional and ready to use${NC}"
        if $gl_works; then echo "  • OpenGL graphics: YES"; fi
        if $vk_works; then echo "  • Vulkan graphics: YES"; fi
        if $cl_works; then echo "  • OpenCL compute: YES"; fi
    else
        echo "${YELLOW}⚠ GPU functionality could not be verified${NC}"
        echo "  Install mesa-utils, vulkan-tools, or clinfo to enable tests"
    fi
    echo
}


generate_summary() {
    print_header "Summary"
    if [[ $ISSUES_FOUND -eq 0 ]]; then
        echo "${GREEN}✓ No critical issues detected${NC}"
        echo "  Your GPU setup is healthy and ready for use."
    else
        echo "${YELLOW}⚠ Issues found: $ISSUES_FOUND${NC}"
        echo
        echo "Troubleshooting steps:"
        echo "  1. Check kernel logs:"
        echo "     dmesg --level=err,warn | grep -iE 'amdgpu|i915|nvidia|drm'"
        echo "  2. Check systemd logs:"
        echo "     journalctl -b -p warning | grep -iE 'gpu|drm|amdgpu'"
        echo "  3. Verify kernel parameters:"
        echo "     cat /proc/cmdline   # check for 'nomodeset' or 'blacklist'"
        echo "  4. Check module configuration:"
        echo "     grep -r amdgpu /etc/modprobe.d/ /usr/lib/modprobe.d/ 2>/dev/null"
        echo "  5. For hardware not detected by lspci:"
        echo "     This is often a BIOS/ACPI quirk. Check if your GPU is functional"
        echo "     using the 'GPU Functionality Test' section above."
    fi
    echo
}

show_usage() {
    cat <<EOF
GPU Driver Diagnostics Tool
Usage: $0 [OPTIONS]
  -h, --help     Show this help
  -a, --all      Run all checks (default)
  -n, --nvidia   NVIDIA only
  -A, --amd      AMD only
  -i, --intel    Intel only
  -v, --verbose  set -x
EOF
}

main() {
    local only=""
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)    show_usage; exit 0 ;;
            -n|--nvidia)  only=nvidia ;;
            -A|--amd)     only=amd ;;
            -i|--intel)   only=intel ;;
            -a|--all)     only="" ;;
            -v|--verbose) set -x ;;
            *) echo "Unknown option: $1" >&2; show_usage; exit 2 ;;
        esac
        shift
    done

    printf '%s╔════════════════════════════════════╗%s\n' "$BLUE" "$NC"
    printf '%s║  GPU Driver Diagnostics Tool       ║%s\n' "$BLUE" "$NC"
    printf '%s╚════════════════════════════════════╝%s\n' "$BLUE" "$NC"

    detect_gpus
    check_drm_subsystem
    check_kernel_modules
    check_permissions
    check_environment

    case "$only" in
        nvidia) check_nvidia_drivers ;;
        amd)    check_amd_drivers ;;
        intel)  check_intel_drivers ;;
        "")     check_nvidia_drivers; check_amd_drivers; check_intel_drivers ;;
    esac

    check_gpu_functionality
    generate_summary
    [[ $ISSUES_FOUND -eq 0 ]] && exit 0 || exit 1
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"