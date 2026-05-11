#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════
#   AUSCULTATION OF THE METAL FAMILIAR
#   A Rite of Binding and Inquiry, for the Discernment of Silicon Spirits
#   (formerly: gpu-diagnostics.sh)
# ══════════════════════════════════════════════════════════════════════════
# Logic is identical to the plain-tongue version. Only the utterances change.
# The diagnostics still tell the truth; they merely robe themselves first.

set -uo pipefail

RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
BLUE=$'\033[0;34m'
DIM=$'\033[2m'
NC=$'\033[0m'

ISSUES_FOUND=0

print_header()  { printf '\n%s❦ %s ❦%s\n%s%s%s\n' "$BLUE" "$1" "$NC" "$DIM" "────────────────────────────────────────" "$NC"; }
print_success() { printf '  %s☩%s %s\n' "$GREEN"  "$NC" "$1"; }   # the rune of binding — that which holds
print_info()    { printf '  %s☾%s %s\n' "$BLUE"   "$NC" "$1"; }   # the waning moon — that which is merely seen
print_warning() { printf '  %s☽%s %s\n' "$YELLOW" "$NC" "$1"; ISSUES_FOUND=$((ISSUES_FOUND + 1)); }  # waxing — the portent
print_error()   { printf '  %s✠%s %s\n' "$RED"    "$NC" "$1"; ISSUES_FOUND=$((ISSUES_FOUND + 1)); }  # the dread mark

declare -a GPU_PCI_LINES=()
declare -a GPU_VENDORS=()
declare -A DRM_DRIVERS=()
HAS_NVIDIA=false
HAS_AMD=false
HAS_INTEL=false

detect_gpus() {
    print_header "The Summoning at the Bus's Altar"

    if ! command -v lspci >/dev/null 2>&1; then
        print_error "the oracle lspci is absent from this house — install pciutils, that the silicon may speak"
        return 1
    fi

    local line
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        GPU_PCI_LINES+=("$line")
        local vendor=other label="a stranger"
        if   [[ "$line" =~ [Nn][Vv][Ii][Dd][Ii][Aa] ]]; then vendor=nvidia; HAS_NVIDIA=true; label="the green familiar"
        elif [[ "$line" =~ [Aa][Mm][Dd]|[Aa][Tt][Ii] ]]; then vendor=amd;    HAS_AMD=true;    label="the crimson familiar"
        elif [[ "$line" =~ [Ii][Nn][Tt][Ee][Ll]     ]]; then vendor=intel;  HAS_INTEL=true;  label="the blue familiar"
        fi
        GPU_VENDORS+=("$vendor")
        print_info "$label answers: $line"
    done < <(lspci -nn -d ::0300 -d ::0302 -d ::0380 2>/dev/null)

    # Fallback: if lspci found nothing, divine the drivers from /sys/class/drm directly
    # (some systems don't report GPUs via lspci device class filters, yet the kernel knows them)
    if [[ ${#GPU_PCI_LINES[@]} -eq 0 ]]; then
        local card driver
        for card in /sys/class/drm/card[0-9]*; do
            [[ -e "$card" ]] || continue
            [[ -L "$card/device/driver" ]] || continue
            driver=$(basename "$(readlink -f "$card/device/driver")")
            case "$driver" in
                amdgpu|radeon)  HAS_AMD=true;    print_info "the crimson familiar dwells at $(basename "$card") — bound to $driver" ;;
                nvidia*)        HAS_NVIDIA=true; print_info "the green familiar dwells at $(basename "$card") — bound to $driver" ;;
                i915|xe)        HAS_INTEL=true;  print_info "the blue familiar dwells at $(basename "$card") — bound to $driver" ;;
                *)              print_info "a lesser familiar dwells at $(basename "$card") — bound to $driver" ;;
            esac
        done
        if [[ $HAS_AMD == false && $HAS_NVIDIA == false && $HAS_INTEL == false ]]; then
            print_warning "no familiar appeared at the calling — the bus is silent"
            return 1
        fi
    fi

    local card driver
    for card in /sys/class/drm/card[0-9]*; do
        [[ -e "$card" ]] || continue
        [[ -L "$card/device/driver" ]] || continue
        driver=$(basename "$(readlink -f "$card/device/driver")")
        DRM_DRIVERS["$(basename "$card")"]=$driver
    done
}

check_drm_subsystem() {
    print_header "The Loom of the Rendering Wraiths"

    if ! [[ -d /sys/class/drm ]]; then
        print_error "the loom is missing entirely — /sys/class/drm hath been unmade"
        return 1
    fi
    print_success "the loom stands; the threads await tension"

    if [[ ${#DRM_DRIVERS[@]} -eq 0 ]]; then
        print_warning "the cards are present but no spirit is yet bound to them"
        return 1
    fi

    local card
    for card in "${!DRM_DRIVERS[@]}"; do
        local drv=${DRM_DRIVERS[$card]}
        case "$drv" in
            amdgpu)        print_success "$card is bound to amdgpu — the crimson rite is sealed"        ;;
            radeon)        print_warning "$card is bound to radeon — an older covenant; amdgpu is preferred for the new silicon" ;;
            i915|xe)       print_success "$card is bound to $drv — the blue rite is sealed"             ;;
            nvidia*)       print_success "$card is bound to $drv — the green rite is sealed"            ;;
            simpledrm|vesa|efifb)
                           print_warning "$card is bound only to $drv — a placeholder spirit, the true familiar hath not arrived" ;;
            *)             print_info    "$card is bound to $drv — a lesser-known covenant"             ;;
        esac
    done

    local rd
    for rd in /dev/dri/renderD*; do
        [[ -e "$rd" ]] && print_info "a rendering chalice waits at $(basename "$rd")"
    done
}

check_kernel_modules() {
    print_header "Tidings from the Inner Sanctum"
    # NOTE: the kernel modules will hide themselves until invoked. Their
    # absence here, before any rite has touched the GPU, is no omen of doom.
    # The true reckoning is the binding above, at the loom.
    local mod found=false
    for mod in nvidia nvidia_drm nvidia_modeset amdgpu radeon i915 xe; do
        if lsmod 2>/dev/null | awk '{print $1}' | grep -qx "$mod"; then
            print_success "the inner sanctum has admitted $mod"
            found=true
        fi
    done
    $found || print_info "the sanctum is silent — but its doors open at need; do not yet despair"
}

check_permissions() {
    print_header "The Question of Thy Bloodright"

    local device
    for device in /dev/dri/card[0-9]* /dev/dri/renderD*; do
        [[ -e "$device" ]] || continue
        if [[ -r "$device" ]]; then print_success "$device may be looked upon by thee"
        else                        print_error   "$device refuses thy gaze"; fi
        if [[ -w "$device" ]]; then print_success "$device may be marked by thy hand"
        else                        print_warning "$device will not bear thy mark"; fi
    done

    local groups
    groups=$(id -Gn 2>/dev/null)
    local need
    for need in video render; do
        if grep -qw "$need" <<<"$groups"; then
            print_success "thou art counted among the keepers of '$need'"
        else
            print_warning "thou art NOT of the '$need' lineage — seek admittance: sudo usermod -aG $need \$USER (and be reborn into thy session)"
        fi
    done
}

check_environment() {
    print_header "Whispers Set Upon the Wind"
    local var found=false
    for var in CUDA_VISIBLE_DEVICES HIP_DEVICE_ORDER HIP_VISIBLE_DEVICES \
               ROCR_VISIBLE_DEVICES DRI_PRIME __GLX_VENDOR_LIBRARY_NAME \
               VK_ICD_FILENAMES MESA_LOADER_DRIVER_OVERRIDE LD_LIBRARY_PATH; do
        if [[ -n "${!var:-}" ]]; then
            print_info "a sigil hangs on the wind — $var=${!var}"
            found=true
        fi
    done
    $found || print_info "the wind is still; no sigils have been hung"
    print_success "the listening is complete"
}

check_nvidia_drivers() {
    print_header "Inquiry into the Green Familiar"
    if ! $HAS_NVIDIA; then
        print_info "no green familiar dwells here; the inquiry is passed over"
        return 0
    fi

    if ! command -v nvidia-smi >/dev/null 2>&1; then
        print_warning "nvidia-smi, the green oracle, is not present"
        return 1
    fi
    print_success "the green oracle nvidia-smi is at hand"

    local v
    if v=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1) && [[ -n "$v" ]]; then
        print_info "the green rite is of version $v"
    else
        print_error "the green oracle would not speak"
    fi

    if command -v nvcc >/dev/null 2>&1; then
        print_info "the alchemist CUDA stands ready: $(nvcc --version | grep -oP 'release \K[0-9.]+')"
    else
        print_info "the alchemist CUDA hath not been summoned (this is no failing)"
    fi
}

check_amd_drivers() {
    print_header "Inquiry into the Crimson Familiar"
    if ! $HAS_AMD; then
        print_info "no crimson familiar dwells here; the inquiry is passed over"
        return 0
    fi

    local bound=false card
    for card in "${!DRM_DRIVERS[@]}"; do
        [[ "${DRM_DRIVERS[$card]}" == amdgpu ]] && bound=true
    done
    if $bound; then
        print_success "amdgpu is sealed to a card at the loom — the binding holds"
    else
        print_warning "the crimson familiar walks the halls, but no card hath received it"
    fi

    if command -v glxinfo >/dev/null 2>&1; then
        local renderer
        renderer=$(glxinfo -B 2>/dev/null | awk -F': ' '/OpenGL renderer string/ {print $2}')
        if [[ -n "$renderer" ]]; then
            if [[ "$renderer" == *llvmpipe* ]]; then
                print_warning "the chalice runs on llvmpipe — the CPU bears the burden in the familiar's stead"
            else
                print_success "the chalice pours through: $renderer"
            fi
        fi
    else
        print_info "glxinfo, the cup-bearer, is absent (apt install mesa-utils to summon it)"
    fi

    if command -v rocm-smi >/dev/null 2>&1; then
        print_success "ROCm, the deeper rite of compute, is present"
        rocm-smi --version 2>/dev/null | head -1 | sed 's/^/    /'
    else
        print_info "ROCm hath not been called — its absence is no wound"
    fi
}

check_intel_drivers() {
    print_header "Inquiry into the Blue Familiar"
    if ! $HAS_INTEL; then
        print_info "no blue familiar dwells here; the inquiry is passed over"
        return 0
    fi

    local bound=false card drv
    for card in "${!DRM_DRIVERS[@]}"; do
        drv=${DRM_DRIVERS[$card]}
        [[ "$drv" == i915 || "$drv" == xe ]] && bound=true
    done
    if $bound; then
        print_success "the blue rite is sealed — i915 or xe holds the binding"
    else
        print_warning "the blue familiar walks unbound — neither i915 nor xe hath claimed it"
    fi

    command -v intel_gpu_top >/dev/null 2>&1 \
        && print_success "intel-gpu-tools, the lesser oracles, are present" \
        || print_info "intel-gpu-tools hath not been summoned (this is no failing)"
}

generate_summary() {
    print_header "Verdict, Spoken Plain"
    if [[ $ISSUES_FOUND -eq 0 ]]; then
        printf '  %sthe house is in order. the familiars answer. the loom holds.%s\n' "$GREEN" "$NC"
    else
        printf '  %s%d portent(s) gathered upon thy threshold.%s\n' "$YELLOW" "$ISSUES_FOUND" "$NC"
        echo
        echo "  Further rites the supplicant may perform:"
        echo "    ☾ dmesg --level=err,warn | grep -iE 'amdgpu|i915|nvidia|drm'    — read the entrails"
        echo "    ☾ journalctl -b -p warning | grep -iE 'gpu|drm'                 — read the chronicle of this waking"
        echo "    ☾ cat /proc/cmdline                                              — read the writ above the door"
        echo "    ☾ grep -r amdgpu /etc/modprobe.d/ /usr/lib/modprobe.d/ 2>/dev/null  — read the hidden interdictions"
    fi
    echo
}

show_usage() {
    cat <<EOF
Auscultation of the Metal Familiar
  A rite for the discernment of GPU spirits and their bindings.

Usage: $0 [OPTIONS]
  -h, --help     Reveal these instructions
  -a, --all      Perform all rites (the default observance)
  -n, --nvidia   The green inquiry only
  -A, --amd      The crimson inquiry only
  -i, --intel    The blue inquiry only
  -v, --verbose  Lay bare every gesture (set -x)
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
            *) echo "An unrecognised utterance: $1" >&2; show_usage; exit 2 ;;
        esac
        shift
    done

    printf '%s╔══════════════════════════════════════════════╗%s\n' "$BLUE" "$NC"
    printf '%s║   AUSCULTATION OF THE METAL FAMILIAR         ║%s\n' "$BLUE" "$NC"
    printf '%s║   a rite of binding and inquiry              ║%s\n' "$BLUE" "$NC"
    printf '%s╚══════════════════════════════════════════════╝%s\n' "$BLUE" "$NC"
    printf '%s    let the candles be lit. let the bus be heard.%s\n' "$DIM" "$NC"

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

    generate_summary
    [[ $ISSUES_FOUND -eq 0 ]] && exit 0 || exit 1
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"
