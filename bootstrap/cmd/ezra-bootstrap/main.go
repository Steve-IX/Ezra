package main

import (
	"flag"
	"fmt"

	"github.com/ezra/bootstrap/internal/config"
	"github.com/ezra/bootstrap/internal/installer"
	"github.com/ezra/bootstrap/internal/logger"
	"github.com/ezra/bootstrap/pkg/detector"
)

func main() {
	var (
		configFile   = flag.String("config", "", "Configuration file path")
		offline      = flag.Bool("offline", false, "Install in offline mode")
		deviceID     = flag.String("device-id", "", "Device identifier")
		companionURL = flag.String("companion-url", "http://localhost:3000", "Companion server URL")
		verbose      = flag.Bool("verbose", false, "Enable verbose logging")
		help         = flag.Bool("help", false, "Show help")
	)
	flag.Parse()

	if *help {
		showHelp()
		return
	}

	// Set up logging
	log := logger.New(*verbose)
	log.Info("Ezra Bootstrap Installer starting...")

	// Load configuration
	cfg, err := config.Load(*configFile)
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	// Override config with command line flags
	if *deviceID != "" {
		cfg.DeviceID = *deviceID
	}
	if *companionURL != "" {
		cfg.CompanionURL = *companionURL
	}

	// Detect system
	detector := detector.New()
	systemInfo, err := detector.Detect()
	if err != nil {
		log.Fatalf("Failed to detect system: %v", err)
	}

	log.Infof("Detected system: %s %s on %s", systemInfo.OS, systemInfo.Version, systemInfo.Architecture)

	// Create installer
	inst, err := installer.New(cfg, systemInfo, log)
	if err != nil {
		log.Fatalf("Failed to create installer: %v", err)
	}

	// Choose installation method
	if *offline {
		log.Info("Installing in offline mode...")
		err = inst.InstallOffline()
	} else {
		log.Info("Installing in online mode...")
		err = inst.InstallOnline()
	}

	if err != nil {
		log.Fatalf("Installation failed: %v", err)
	}

	log.Info("Installation completed successfully!")
}

func showHelp() {
	fmt.Printf(`Ezra Bootstrap Installer

USAGE:
    ezra-bootstrap [OPTIONS]

OPTIONS:
    -config string
        Configuration file path
    -offline
        Install in offline mode (USB/SD card)
    -device-id string
        Device identifier
    -companion-url string
        Companion server URL (default: http://localhost:3000)
    -verbose
        Enable verbose logging
    -help
        Show this help message

EXAMPLES:
    # Online installation
    ezra-bootstrap -companion-url https://companion.ezra.dev

    # Offline installation
    ezra-bootstrap -offline

    # Custom device ID
    ezra-bootstrap -device-id my-device-001

For more information, visit: https://github.com/ezra/ezra
`)
}
