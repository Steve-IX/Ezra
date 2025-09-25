import { z } from 'zod';

// Cryptographic schemas for signing and verification
export const SignatureSchema = z.object({
  algorithm: z.literal('ed25519'),
  public_key: z.string(),
  signature: z.string(),
  timestamp: z.string(),
});

export const SignedDataSchema = z.object({
  data: z.any(),
  signature: SignatureSchema,
});

export type Signature = z.infer<typeof SignatureSchema>;
export type SignedData = z.infer<typeof SignedDataSchema>;

// Key pair schema
export const KeyPairSchema = z.object({
  public_key: z.string(),
  private_key: z.string(),
  algorithm: z.literal('ed25519'),
  created_at: z.string(),
});

export type KeyPair = z.infer<typeof KeyPairSchema>;

// Certificate schema for trusted keys
export const CertificateSchema = z.object({
  public_key: z.string(),
  issuer: z.string(),
  subject: z.string(),
  valid_from: z.string(),
  valid_until: z.string(),
  signature: SignatureSchema,
});

export type Certificate = z.infer<typeof CertificateSchema>;
