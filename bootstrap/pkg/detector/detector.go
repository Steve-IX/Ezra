package detector

import (
	"fmt"
	"os"
	"runtime"
	"strings"
)

// SystemInfo represents detected system information
type SystemInfo struct {
	OS           string `json:"os"`
	Version      string `json:"version"`
	Architecture string `json:"architecture"`
	Platform     string `json:"platform"`
	Capabilities []string `json:"capabilities"`
}

// Detector detects system information
type Detector struct{}

// New creates a new detector
func New() *Detector {
	return &Detector{}
}

// Detect detects system information
func (d *Detector) Detect() (*SystemInfo, error) {
	info := &SystemInfo{
		OS:           runtime.GOOS,
		Architecture: runtime.GOARCH,
		Capabilities: []string{},
	}
	
	// Detect platform
	platform, err := d.detectPlatform()
	if err != nil {
		return nil, fmt.Errorf("failed to detect platform: %w", err)
	}
	info.Platform = platform
	
	// Detect version
	version, err := d.detectVersion()
	if err != nil {
		return nil, fmt.Errorf("failed to detect version: %w", err)
	}
	info.Version = version
	
	// Detect capabilities
	capabilities, err := d.detectCapabilities()
	if err != nil {
		return nil, fmt.Errorf("failed to detect capabilities: %w", err)
	}
	info.Capabilities = capabilities
	
	return info, nil
}

// detectPlatform detects the platform type
func (d *Detector) detectPlatform() (string, error) {
	switch runtime.GOOS {
	case "linux":
		return "linux", nil
	case "windows":
		return "windows", nil
	case "darwin":
		return "macos", nil
	case "android":
		return "android", nil
	default:
		return "console", nil
	}
}

// detectVersion detects the OS version
func (d *Detector) detectVersion() (string, error) {
	switch runtime.GOOS {
	case "linux":
		return d.detectLinuxVersion()
	case "windows":
		return d.detectWindowsVersion()
	case "darwin":
		return d.detectMacOSVersion()
	default:
		return "unknown", nil
	}
}

// detectLinuxVersion detects Linux version
func (d *Detector) detectLinuxVersion() (string, error) {
	// Try to read /etc/os-release
	if data, err := os.ReadFile("/etc/os-release"); err == nil {
		lines := strings.Split(string(data), "\n")
		for _, line := range lines {
			if strings.HasPrefix(line, "PRETTY_NAME=") {
				return strings.Trim(strings.TrimPrefix(line, "PRETTY_NAME="), "\""), nil
			}
		}
	}
	
	// Fallback to uname
	return "Linux", nil
}

// detectWindowsVersion detects Windows version
func (d *Detector) detectWindowsVersion() (string, error) {
	// This would use Windows API to detect version
	// For now, return a placeholder
	return "Windows", nil
}

// detectMacOSVersion detects macOS version
func (d *Detector) detectMacOSVersion() (string, error) {
	// This would use system_profiler or similar
	// For now, return a placeholder
	return "macOS", nil
}

// detectCapabilities detects system capabilities
func (d *Detector) detectCapabilities() ([]string, error) {
	capabilities := []string{
		"file_system",
		"process_management",
		"network",
	}
	
	// Platform-specific capabilities
	switch runtime.GOOS {
	case "linux":
		capabilities = append(capabilities, d.detectLinuxCapabilities()...)
	case "windows":
		capabilities = append(capabilities, d.detectWindowsCapabilities()...)
	case "darwin":
		capabilities = append(capabilities, d.detectMacOSCapabilities()...)
	}
	
	return capabilities, nil
}

// detectLinuxCapabilities detects Linux-specific capabilities
func (d *Detector) detectLinuxCapabilities() []string {
	capabilities := []string{}
	
	// Check for package managers
	if d.hasCommand("apt") {
		capabilities = append(capabilities, "apt_package_manager")
	}
	if d.hasCommand("yum") {
		capabilities = append(capabilities, "yum_package_manager")
	}
	if d.hasCommand("dnf") {
		capabilities = append(capabilities, "dnf_package_manager")
	}
	if d.hasCommand("pacman") {
		capabilities = append(capabilities, "pacman_package_manager")
	}
	
	// Check for systemd
	if d.hasFile("/etc/systemd") {
		capabilities = append(capabilities, "systemd")
	}
	
	// Check for root access
	if os.Geteuid() == 0 {
		capabilities = append(capabilities, "root_access")
	}
	
	return capabilities
}

// detectWindowsCapabilities detects Windows-specific capabilities
func (d *Detector) detectWindowsCapabilities() []string {
	capabilities := []string{
		"powershell",
		"registry_access",
	}
	
	// Check for package managers
	if d.hasCommand("choco") {
		capabilities = append(capabilities, "chocolatey_package_manager")
	}
	if d.hasCommand("winget") {
		capabilities = append(capabilities, "winget_package_manager")
	}
	
	// Check for administrator access
	if d.isAdministrator() {
		capabilities = append(capabilities, "administrator_access")
	}
	
	return capabilities
}

// detectMacOSCapabilities detects macOS-specific capabilities
func (d *Detector) detectMacOSCapabilities() []string {
	capabilities := []string{
		"homebrew",
	}
	
	// Check for Homebrew
	if d.hasCommand("brew") {
		capabilities = append(capabilities, "homebrew_package_manager")
	}
	
	return capabilities
}

// hasCommand checks if a command exists
func (d *Detector) hasCommand(cmd string) bool {
	// This would check if command exists in PATH
	// Simplified implementation
	return false
}

// hasFile checks if a file exists
func (d *Detector) hasFile(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}

// isAdministrator checks if running as administrator
func (d *Detector) isAdministrator() bool {
	// This would check for administrator privileges
	// Simplified implementation
	return false
}
