package downloader

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"runtime"
	"time"

	"github.com/cheggaaa/pb/v3"
	"github.com/go-resty/resty/v2"
)

// Downloader handles downloading components
type Downloader struct {
	baseURL string
	client  *resty.Client
	log     Logger
}

// Logger interface for logging
type Logger interface {
	Info(args ...interface{})
	Infof(format string, args ...interface{})
	Error(args ...interface{})
	Errorf(format string, args ...interface{})
}

// New creates a new downloader
func New(baseURL string, log Logger) *Downloader {
	client := resty.New()
	client.SetTimeout(30 * time.Second)

	return &Downloader{
		baseURL: baseURL,
		client:  client,
		log:     log,
	}
}

// DownloadCompanion downloads the companion server
func (d *Downloader) DownloadCompanion() error {
	d.log.Info("Downloading companion server...")

	// Determine download URL based on platform
	url := d.getDownloadURL("companion")

	// Download file
	if err := d.downloadFile(url, "companion"); err != nil {
		return fmt.Errorf("failed to download companion: %w", err)
	}

	d.log.Info("Companion server downloaded successfully")
	return nil
}

// DownloadAgent downloads the agent
func (d *Downloader) DownloadAgent() error {
	d.log.Info("Downloading agent...")

	// Determine download URL based on platform
	url := d.getDownloadURL("agent")

	// Download file
	if err := d.downloadFile(url, "agent"); err != nil {
		return fmt.Errorf("failed to download agent: %w", err)
	}

	d.log.Info("Agent downloaded successfully")
	return nil
}

// DownloadExecutor downloads the executor
func (d *Downloader) DownloadExecutor() error {
	d.log.Info("Downloading executor...")

	// Determine download URL based on platform
	url := d.getDownloadURL("executor")

	// Download file
	if err := d.downloadFile(url, "executor"); err != nil {
		return fmt.Errorf("failed to download executor: %w", err)
	}

	d.log.Info("Executor downloaded successfully")
	return nil
}

// downloadFile downloads a file with progress bar
func (d *Downloader) downloadFile(url, name string) error {
	// Get file info
	resp, err := d.client.R().Head(url)
	if err != nil {
		return fmt.Errorf("failed to get file info: %w", err)
	}

	contentLength := resp.Header().Get("Content-Length")
	if contentLength == "" {
		// Fallback to simple download
		return d.simpleDownload(url, name)
	}

	// Download with progress bar
	return d.downloadWithProgress(url, name)
}

// downloadWithProgress downloads a file with progress bar
func (d *Downloader) downloadWithProgress(url, name string) error {
	// Create HTTP request
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	// Make request
	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("download failed with status: %d", resp.StatusCode)
	}

	// Create progress bar
	bar := pb.New64(resp.ContentLength)
	bar.SetTemplateString(`{{counters . }} {{bar . }} {{percent . }} {{speed . }} {{rtime . "ETA %s"}}`)
	bar.Start()

	// Create file
	file, err := os.Create(name)
	if err != nil {
		return fmt.Errorf("failed to create file: %w", err)
	}
	defer file.Close()

	// Copy with progress
	reader := bar.NewProxyReader(resp.Body)
	_, err = io.Copy(file, reader)
	if err != nil {
		return fmt.Errorf("failed to copy file: %w", err)
	}

	bar.Finish()
	return nil
}

// simpleDownload downloads a file without progress bar
func (d *Downloader) simpleDownload(url, name string) error {
	resp, err := d.client.R().Get(url)
	if err != nil {
		return fmt.Errorf("failed to download file: %w", err)
	}

	if err := os.WriteFile(name, resp.Body(), 0644); err != nil {
		return fmt.Errorf("failed to write file: %w", err)
	}

	return nil
}

// getDownloadURL constructs the download URL for a component
func (d *Downloader) getDownloadURL(component string) string {
	// Construct URL based on platform and architecture
	platform := runtime.GOOS
	arch := runtime.GOARCH

	// Map Go architecture to common names
	switch arch {
	case "amd64":
		arch = "x86_64"
	case "386":
		arch = "x86"
	case "arm64":
		arch = "aarch64"
	}

	// Construct filename
	filename := fmt.Sprintf("ezra-%s-%s-%s", component, platform, arch)

	// Add extension for Windows
	if platform == "windows" {
		filename += ".exe"
	}

	// Construct full URL
	return fmt.Sprintf("%s/releases/latest/%s", d.baseURL, filename)
}
