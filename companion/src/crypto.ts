import * as nacl from 'tweetnacl';
import * as util from 'tweetnacl-util';
import { Signature, SignedData, KeyPair } from '@ezra/schemas';

export class CryptoService {
  private keyPair: nacl.SignKeyPair;

  constructor(privateKey?: string) {
    if (privateKey) {
      const privateKeyBytes = util.decodeBase64(privateKey);
      this.keyPair = nacl.sign.keyPair.fromSeed(privateKeyBytes.slice(0, 32));
    } else {
      this.keyPair = nacl.sign.keyPair();
    }
  }

  getPublicKey(): string {
    return util.encodeBase64(this.keyPair.publicKey);
  }

  getPrivateKey(): string {
    return util.encodeBase64(this.keyPair.secretKey);
  }

  sign(data: unknown): Signature {
    const dataString = JSON.stringify(data);
    const dataBytes = util.decodeUTF8(dataString);
    const signature = nacl.sign.detached(dataBytes, this.keyPair.secretKey);
    
    return {
      algorithm: 'ed25519',
      public_key: this.getPublicKey(),
      signature: util.encodeBase64(signature),
      timestamp: new Date().toISOString(),
    };
  }

  verify(data: unknown, signature: Signature): boolean {
    try {
      const dataString = JSON.stringify(data);
      const dataBytes = util.decodeUTF8(dataString);
      const signatureBytes = util.decodeBase64(signature.signature);
      const publicKeyBytes = util.decodeBase64(signature.public_key);
      
      return nacl.sign.detached.verify(dataBytes, signatureBytes, publicKeyBytes);
    } catch (error) {
      return false;
    }
  }

  signData<T>(data: T): SignedData {
    return {
      data,
      signature: this.sign(data),
    };
  }

  verifySignedData<T>(signedData: SignedData): { valid: boolean; data?: T } {
    const isValid = this.verify(signedData.data, signedData.signature);
    return {
      valid: isValid,
      data: isValid ? signedData.data : undefined,
    };
  }

  generateKeyPair(): KeyPair {
    return {
      public_key: this.getPublicKey(),
      private_key: this.getPrivateKey(),
      algorithm: 'ed25519',
      created_at: new Date().toISOString(),
    };
  }
}
