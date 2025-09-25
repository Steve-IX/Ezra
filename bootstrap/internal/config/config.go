package config

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

// Config represents the bootstrap configuration
type Config struct {
	DeviceID     string `json:"device_id"`
	CompanionURL string `json:"companion_url"`
	InstallPath  string `json:"install_path"`
	DataPath     string `json:"data_path"`
	CachePath    string `json:"cache_path"`
	BackupPath   string `json:"backup_path"`
	LogLevel     string `json:"log_level"`
	OfflineMode  bool   `json:"offline_mode"`
	VerifySigs   bool   `json:"verify_signatures"`
	PublicKey    string `json:"public_key"`
}

// DefaultConfig returns a default configuration
func DefaultConfig() *Config {
	homeDir, _ := os.UserHomeDir()
	
	return &Config{
		DeviceID:     "",
		CompanionURL: "http://localhost:3000",
		InstallPath:  "/usr/local/bin",
		DataPath:     filepath.Join(homeDir, ".ezra"),
		CachePath:    filepath.Join(homeDir, ".ezra", "cache"),
		BackupPath:   filepath.Join(homeDir, ".ezra", "backups"),
		LogLevel:     "info",
		OfflineMode:  false,
		VerifySigs:   true,
		PublicKey:    "",
	}
}

// Load loads configuration from file or creates default
func Load(configFile string) (*Config, error) {
	cfg := DefaultConfig()
	
	if configFile != "" {
		data, err := os.ReadFile(configFile)
		if err != nil {
			return nil, fmt.Errorf("failed to read config file: %w", err)
		}
		
		if err := json.Unmarshal(data, cfg); err != nil {
			return nil, fmt.Errorf("failed to parse config file: %w", err)
		}
	}
	
	// Generate device ID if not provided
	if cfg.DeviceID == "" {
		cfg.DeviceID = generateDeviceID()
	}
	
	return cfg, nil
}

// Save saves configuration to file
func (c *Config) Save(configFile string) error {
	data, err := json.MarshalIndent(c, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}
	
	if err := os.WriteFile(configFile, data, 0644); err != nil {
		return fmt.Errorf("failed to write config file: %w", err)
	}
	
	return nil
}

// generateDeviceID generates a unique device identifier
func generateDeviceID() string {
	hostname, _ := os.Hostname()
	return fmt.Sprintf("ezra_%s_%d", hostname, os.Getpid())
}
