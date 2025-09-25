package verifier

import (
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"io"
	"os"
)

// Verifier handles signature verification
type Verifier struct {
	publicKey string
	log       Logger
}

// Logger interface for logging
type Logger interface {
	Info(args ...interface{})
	Infof(format string, args ...interface{})
	Error(args ...interface{})
	Errorf(format string, args ...interface{})
}

// New creates a new verifier
func New(publicKey string, log Logger) *Verifier {
	return &Verifier{
		publicKey: publicKey,
		log:       log,
	}
}

// VerifyFile verifies a file's signature
func (v *Verifier) VerifyFile(filePath, signature string) error {
	v.log.Infof("Verifying file: %s", filePath)
	
	// Read file
	file, err := os.Open(filePath)
	if err != nil {
		return fmt.Errorf("failed to open file: %w", err)
	}
	defer file.Close()
	
	// Calculate file hash
	hash := sha256.New()
	if _, err := io.Copy(hash, file); err != nil {
		return fmt.Errorf("failed to calculate hash: %w", err)
	}
	
	fileHash := hash.Sum(nil)
	
	// Verify signature
	if err := v.verifySignature(fileHash, signature); err != nil {
		return fmt.Errorf("signature verification failed: %w", err)
	}
	
	v.log.Info("File signature verified successfully")
	return nil
}

// VerifyChecksum verifies a file's checksum
func (v *Verifier) VerifyChecksum(filePath, expectedChecksum string) error {
	v.log.Infof("Verifying checksum: %s", filePath)
	
	// Read file
	file, err := os.Open(filePath)
	if err != nil {
		return fmt.Errorf("failed to open file: %w", err)
	}
	defer file.Close()
	
	// Calculate SHA256 hash
	hash := sha256.New()
	if _, err := io.Copy(hash, file); err != nil {
		return fmt.Errorf("failed to calculate hash: %w", err)
	}
	
	actualChecksum := hex.EncodeToString(hash.Sum(nil))
	
	// Compare checksums
	if actualChecksum != expectedChecksum {
		return fmt.Errorf("checksum mismatch: expected %s, got %s", expectedChecksum, actualChecksum)
	}
	
	v.log.Info("Checksum verified successfully")
	return nil
}

// verifySignature verifies an Ed25519 signature
func (v *Verifier) verifySignature(data []byte, signature string) error {
	// Decode public key
	publicKeyBytes, err := base64.StdEncoding.DecodeString(v.publicKey)
	if err != nil {
		return fmt.Errorf("failed to decode public key: %w", err)
	}
	
	// Decode signature
	signatureBytes, err := base64.StdEncoding.DecodeString(signature)
	if err != nil {
		return fmt.Errorf("failed to decode signature: %w", err)
	}
	
	// Verify signature
	if !ed25519.Verify(publicKeyBytes, data, signatureBytes) {
		return fmt.Errorf("signature verification failed")
	}
	
	return nil
}

// VerifyRelease verifies a release's signature and checksums
func (v *Verifier) VerifyRelease(releasePath string) error {
	v.log.Info("Verifying release...")
	
	// Check for signature file
	signatureFile := releasePath + ".sig"
	if _, err := os.Stat(signatureFile); err != nil {
		return fmt.Errorf("signature file not found: %w", err)
	}
	
	// Read signature
	signature, err := os.ReadFile(signatureFile)
	if err != nil {
		return fmt.Errorf("failed to read signature: %w", err)
	}
	
	// Verify file signature
	if err := v.VerifyFile(releasePath, string(signature)); err != nil {
		return fmt.Errorf("failed to verify file signature: %w", err)
	}
	
	// Check for checksum file
	checksumFile := releasePath + ".sha256"
	if _, err := os.Stat(checksumFile); err == nil {
		// Read checksum
		checksumData, err := os.ReadFile(checksumFile)
		if err != nil {
			return fmt.Errorf("failed to read checksum: %w", err)
		}
		
		// Parse checksum (format: "hash filename")
		checksum := string(checksumData)
		if len(checksum) > 64 {
			checksum = checksum[:64]
		}
		
		// Verify checksum
		if err := v.VerifyChecksum(releasePath, checksum); err != nil {
			return fmt.Errorf("failed to verify checksum: %w", err)
		}
	}
	
	v.log.Info("Release verification completed successfully")
	return nil
}
