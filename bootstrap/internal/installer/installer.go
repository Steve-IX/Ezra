package installer

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"

	"github.com/ezra/bootstrap/internal/config"
	"github.com/ezra/bootstrap/pkg/detector"
	"github.com/ezra/bootstrap/pkg/downloader"
	"github.com/ezra/bootstrap/pkg/verifier"
)

// Installer handles the installation process
type Installer struct {
	config     *config.Config
	systemInfo *detector.SystemInfo
	log        Logger
	downloader *downloader.Downloader
	verifier   *verifier.Verifier
}

// Logger interface for logging
type Logger interface {
	Info(args ...interface{})
	Infof(format string, args ...interface{})
	Error(args ...interface{})
	Errorf(format string, args ...interface{})
}

// New creates a new installer instance
func New(cfg *config.Config, systemInfo *detector.SystemInfo, log Logger) (*Installer, error) {
	downloader := downloader.New(cfg.CompanionURL, log)
	verifier := verifier.New(cfg.PublicKey, log)

	return &Installer{
		config:     cfg,
		systemInfo: systemInfo,
		log:        log,
		downloader: downloader,
		verifier:   verifier,
	}, nil
}

// InstallOnline installs Ezra in online mode
func (i *Installer) InstallOnline() error {
	i.log.Info("Starting online installation...")

	// Download components
	if err := i.downloadComponents(); err != nil {
		return fmt.Errorf("failed to download components: %w", err)
	}

	// Install components
	if err := i.installComponents(); err != nil {
		return fmt.Errorf("failed to install components: %w", err)
	}

	// Configure system
	if err := i.configureSystem(); err != nil {
		return fmt.Errorf("failed to configure system: %w", err)
	}

	// Start services
	if err := i.startServices(); err != nil {
		return fmt.Errorf("failed to start services: %w", err)
	}

	return nil
}

// InstallOffline installs Ezra in offline mode
func (i *Installer) InstallOffline() error {
	i.log.Info("Starting offline installation...")

	// Look for offline installation media
	mediaPath, err := i.findOfflineMedia()
	if err != nil {
		return fmt.Errorf("failed to find offline media: %w", err)
	}

	// Copy components from media
	if err := i.copyComponents(mediaPath); err != nil {
		return fmt.Errorf("failed to copy components: %w", err)
	}

	// Install components
	if err := i.installComponents(); err != nil {
		return fmt.Errorf("failed to install components: %w", err)
	}

	// Configure system
	if err := i.configureSystem(); err != nil {
		return fmt.Errorf("failed to configure system: %w", err)
	}

	// Start services
	if err := i.startServices(); err != nil {
		return fmt.Errorf("failed to start services: %w", err)
	}

	return nil
}

// downloadComponents downloads all required components
func (i *Installer) downloadComponents() error {
	i.log.Info("Downloading components...")

	// Download companion server
	if err := i.downloader.DownloadCompanion(); err != nil {
		return fmt.Errorf("failed to download companion: %w", err)
	}

	// Download agent
	if err := i.downloader.DownloadAgent(); err != nil {
		return fmt.Errorf("failed to download agent: %w", err)
	}

	// Download executor
	if err := i.downloader.DownloadExecutor(); err != nil {
		return fmt.Errorf("failed to download executor: %w", err)
	}

	return nil
}

// copyComponents copies components from offline media
func (i *Installer) copyComponents(mediaPath string) error {
	i.log.Info("Copying components from offline media...")

	// Copy companion server
	if err := i.copyFile(filepath.Join(mediaPath, "companion"), i.config.DataPath); err != nil {
		return fmt.Errorf("failed to copy companion: %w", err)
	}

	// Copy agent
	if err := i.copyFile(filepath.Join(mediaPath, "agent"), i.config.DataPath); err != nil {
		return fmt.Errorf("failed to copy agent: %w", err)
	}

	// Copy executor
	if err := i.copyFile(filepath.Join(mediaPath, "executor"), i.config.DataPath); err != nil {
		return fmt.Errorf("failed to copy executor: %w", err)
	}

	return nil
}

// installComponents installs all components
func (i *Installer) installComponents() error {
	i.log.Info("Installing components...")

	// Install companion server
	if err := i.installCompanion(); err != nil {
		return fmt.Errorf("failed to install companion: %w", err)
	}

	// Install agent
	if err := i.installAgent(); err != nil {
		return fmt.Errorf("failed to install agent: %w", err)
	}

	// Install executor
	if err := i.installExecutor(); err != nil {
		return fmt.Errorf("failed to install executor: %w", err)
	}

	return nil
}

// configureSystem configures the system for Ezra
func (i *Installer) configureSystem() error {
	i.log.Info("Configuring system...")

	// Create directories
	if err := i.createDirectories(); err != nil {
		return fmt.Errorf("failed to create directories: %w", err)
	}

	// Create configuration files
	if err := i.createConfigFiles(); err != nil {
		return fmt.Errorf("failed to create config files: %w", err)
	}

	// Set up system service
	if err := i.setupSystemService(); err != nil {
		return fmt.Errorf("failed to setup system service: %w", err)
	}

	return nil
}

// startServices starts the Ezra services
func (i *Installer) startServices() error {
	i.log.Info("Starting services...")

	// Start companion server
	if err := i.startCompanion(); err != nil {
		return fmt.Errorf("failed to start companion: %w", err)
	}

	// Start agent
	if err := i.startAgent(); err != nil {
		return fmt.Errorf("failed to start agent: %w", err)
	}

	return nil
}

// Helper methods

func (i *Installer) findOfflineMedia() (string, error) {
	// Look for USB/SD card with Ezra installation
	// This is a simplified implementation
	possiblePaths := []string{
		"/media/ezra",
		"/mnt/ezra",
		"/tmp/ezra-offline",
	}

	for _, path := range possiblePaths {
		if _, err := os.Stat(path); err == nil {
			return path, nil
		}
	}

	return "", fmt.Errorf("no offline media found")
}

func (i *Installer) copyFile(src, dst string) error {
	// Create destination directory
	if err := os.MkdirAll(filepath.Dir(dst), 0755); err != nil {
		return err
	}

	// Copy file
	cmd := exec.Command("cp", "-r", src, dst)
	return cmd.Run()
}

func (i *Installer) installCompanion() error {
	i.log.Info("Installing companion server...")

	// This would install the companion server
	// Implementation depends on the platform

	return nil
}

func (i *Installer) installAgent() error {
	i.log.Info("Installing agent...")

	// This would install the agent
	// Implementation depends on the platform

	return nil
}

func (i *Installer) installExecutor() error {
	i.log.Info("Installing executor...")

	// This would install the executor
	// Implementation depends on the platform

	return nil
}

func (i *Installer) createDirectories() error {
	dirs := []string{
		i.config.DataPath,
		i.config.CachePath,
		i.config.BackupPath,
	}

	for _, dir := range dirs {
		if err := os.MkdirAll(dir, 0755); err != nil {
			return fmt.Errorf("failed to create directory %s: %w", dir, err)
		}
	}

	return nil
}

func (i *Installer) createConfigFiles() error {
	// Create agent configuration
	agentConfig := map[string]interface{}{
		"companion_url": i.config.CompanionURL,
		"device_id":     i.config.DeviceID,
		"data_dir":      i.config.DataPath,
		"cache_dir":     i.config.CachePath,
		"backup_dir":    i.config.BackupPath,
		"log_level":     i.config.LogLevel,
	}

	configPath := filepath.Join(i.config.DataPath, "agent-config.json")
	return i.writeJSONConfig(configPath, agentConfig)
}

func (i *Installer) setupSystemService() error {
	i.log.Info("Setting up system service...")

	switch runtime.GOOS {
	case "linux":
		return i.setupSystemdService()
	case "windows":
		return i.setupWindowsService()
	default:
		return fmt.Errorf("unsupported platform: %s", runtime.GOOS)
	}
}

func (i *Installer) setupSystemdService() error {
	// Create systemd service file
	serviceContent := fmt.Sprintf(`[Unit]
Description=Ezra Agent
After=network.target

[Service]
Type=simple
User=ezra
WorkingDirectory=%s
ExecStart=%s/ezra-agent start --daemon
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
`, i.config.DataPath, i.config.InstallPath)

	serviceFile := "/etc/systemd/system/ezra-agent.service"
	return os.WriteFile(serviceFile, []byte(serviceContent), 0644)
}

func (i *Installer) setupWindowsService() error {
	// Windows service setup would go here
	return fmt.Errorf("Windows service setup not implemented")
}

func (i *Installer) startCompanion() error {
	i.log.Info("Starting companion server...")

	// Start companion server
	cmd := exec.Command(filepath.Join(i.config.InstallPath, "ezra-companion"), "start")
	return cmd.Start()
}

func (i *Installer) startAgent() error {
	i.log.Info("Starting agent...")

	// Start agent
	cmd := exec.Command(filepath.Join(i.config.InstallPath, "ezra-agent"), "start", "--daemon")
	return cmd.Start()
}

func (i *Installer) writeJSONConfig(path string, config map[string]interface{}) error {
	// This would write JSON configuration
	// Implementation depends on JSON handling
	return nil
}
